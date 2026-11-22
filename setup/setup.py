#!/usr/bin/env python3
"""muse-rsi full setup — upgrade a Muse agent's whole system, keep its character.

What it does (new agent or long-running one):
  1. Snapshots the agent's existing SOUL.md / IDENTITY.md / USER.md / MEMORY.md /
     AGENTS.md / TOOLS.md to ~/.muse-backup/<timestamp>/ (auto-snapshot, never
     overwritten).
  2. Merges the muse-rsi operating system into SOUL.md: only the system sections
     are replaced; every character/persona section stays exactly as it is.
     IDENTITY.md is rewritten from the template on every upgrade — but the
     agent's name and character (Role) always survive; only those two lines
     are kept.
  3. Repairs MEMORY.md (clean <60-line structure + memory/scenes/) without
     deleting the user's facts. A broken single-line MEMORY.md is replaced from
     the template, keeping the user's name when it can be found.
  4. Installs the 11 original skills + the muse-rsi router (registry 248 entries)
     into ~/workspace/custom-skills/.
  5. Installs the tools: gitleaks (secret scan) + visual-check (Playwright +
     Chrome headless shell + axe) + scan-secrets.sh + run_all_checks.sh.
  6. Creates the vault dir (~/.config/muse/vault, chmod 700).
  7. Verifies: registry --check + routing eval + secret scan on the repo.

  --skills-only installs only the skills + tools: no snapshot, no system
  files touched, no vault changes.

  On Muse VMs the runtime blocks shell writes to SOUL.md / IDENTITY.md /
  MEMORY.md. When a write is blocked, setup does NOT abort: it saves the
  content to ~/workspace/.muse-rsi-staging/<file> and prints ACTION REQUIRED —
  the installing agent applies each staged file with its own file tool, then
  deletes the staging copy and runs the verification.

Usage:
  python3 setup.py [--home PATH] [--repo PATH] [--name NAME] [--user-name NAME]
                   [--dry-run] [--yes] [--no-visual-check] [--no-gitleaks]
                   [--skills-only]

Stdlib only. $0: everything it installs is free and open source. It never
writes the user's private info into the repo — it only reads the agent's own
files locally to preserve them.
"""
import argparse
import datetime
import hashlib
import json
import platform
import os
import pathlib
import re
import shutil
import subprocess
import sys
import urllib.request

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import selfheal  # noqa: E402  (fix-and-resume layer, v3.2)

HEALER = None  # set in main(); every subprocess runs with its PATH/TMPDIR repairs


def load_originals(repo_root):
    """The 11 original skills, from the single source of truth
    config/originals.json (v3.0 G1, M-13). Returns
    {name: (title, category, description_override)} — the same shape the
    old inline ORIGINALS dict had. Do not duplicate the list here."""
    data = json.loads((pathlib.Path(repo_root) / 'config' / 'originals.json')
                      .read_text(encoding='utf-8'))
    return {e['name']: (e['title'], e['category'], e['description_override'])
            for e in data['originals']}
# Marker pair that delimits the muse-rsi system block inside SOUL.md.
# Everything between the markers is owned by the template; everything
# outside them belongs to the agent and is never touched by a merge.
SYS_START = '<!-- muse-rsi:system:start -->'
SYS_END = '<!-- muse-rsi:system:end -->'
RUNTIME_FILES = ['SOUL.md', 'IDENTITY.md', 'USER.md', 'MEMORY.md', 'AGENTS.md', 'TOOLS.md',
                 'HEARTBEAT.md', 'PROACTIVE_PREFERENCES.md']

log_lines = []


def log(msg):
    print(msg)
    log_lines.append(msg)


def run(cmd, cwd=None, check=False):
    if HEALER is not None:
        return HEALER.run(cmd, cwd=cwd, check=check)
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=600, stdin=subprocess.DEVNULL)
    if check and r.returncode != 0:
        raise RuntimeError(f'command failed: {" ".join(cmd)}\n{r.stdout}\n{r.stderr}')
    return r


def http_get_json(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'muse-rsi-setup'})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode('utf-8'))


def split_sections(text):
    """Split markdown into (heading, body) pairs by ## headings. Preamble first."""
    parts = re.split(r'(?m)^(## .+)$', text)
    sections = []
    preamble = parts[0]
    for i in range(1, len(parts), 2):
        sections.append((parts[i].strip(), parts[i + 1] if i + 1 < len(parts) else ''))
    return preamble, sections


def system_template_body(template):
    """The template's operating content: everything from the first '>'
    quote line onward. The explanatory preamble above it describes the
    template itself and must never be written into an agent's SOUL.md."""
    lines = template.split('\n')
    for i, ln in enumerate(lines):
        if ln.startswith('>'):
            return '\n'.join(lines[i:]).strip() + '\n'
    return template.strip() + '\n'


def merge_soul(existing, template, agent_name):
    """Replace ONLY the marker-delimited system block; keep everything
    else in the agent's SOUL.md byte-identical, including persona sections
    whose headings happen to contain words like 'autonomy' or 'frontstage'.

    Legacy files without markers: drop only sections whose heading EXACTLY
    matches a template heading, then append the marked block."""
    body = system_template_body(template).replace('{AGENT_NAME}', agent_name)
    block = SYS_START + '\n' + body.rstrip() + '\n' + SYS_END
    if existing is None:
        return block + '\n'
    if SYS_START in existing and SYS_END in existing:
        pre, rest = existing.split(SYS_START, 1)
        _, post = rest.split(SYS_END, 1)
        return pre + block + post
    _, t_secs = split_sections(body)
    sys_heads = {h.strip() for h, _ in t_secs}
    pre, secs = split_sections(existing)
    out = [pre.rstrip()] if pre.strip() else []
    out += [h + '\n' + b.strip() for h, b in secs if h.strip() not in sys_heads]
    out.append(block)
    return '\n\n'.join(x.rstrip() for x in out if x.strip()) + '\n'


def merge_identity(existing, template, agent_name, agent_role):
    """Rewrite IDENTITY.md from the template, keeping name + character (Role)."""
    return template.replace('{AGENT_NAME}', agent_name).replace('{AGENT_ROLE}', agent_role)


def find_name(text, key='Name'):
    """Find a `Name:` / `Role:` value in any common Markdown shape:
    bullet or plain, bold inside or outside the colon, any case, table
    row, or heading. Returns None (with no crash) when nothing matches."""
    if not text:
        return None
    # Markdown-escaped asterisks (\*\*) mean literal asterisks; unescape
    # them first so `- \*\*Role:\*\* ...` matches like `- **Role:** ...`
    # (issue #8: an IDENTITY.md written with escaped asterisks made the
    # Role fall back to the generic template line).
    text = text.replace('\\*', '*')
    patterns = [
        # - **Name**: X | - **Name:** X | Name: X | - name: x
        r'(?m)^\s*[-*]?\s*\*?\*?' + key + r'\*?\*?\s*:?\s*(.+?)\s*$',
        # | Name | X |  or  | **Name** | X |
        r'(?m)^\s*\|?\s*\*{0,2}' + key + r'\*{0,2}\s*\|\s*(.+?)\s*\|?\s*$',
        # ## Name: X
        r'(?m)^#+\s*' + key + r':\s*(.+?)\s*$',
    ]
    for pat in patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            v = m.group(1).strip().strip('*').strip().strip('"').strip("'").strip()
            if v and 'fill in' not in v.lower() and v.lower() not in ('name', key.lower()):
                return v
    return None


def strip_frontmatter(text):
    m = re.match(r'^---\n(.*?)\n---\n', text, re.S)
    desc = ''
    if m:
        dm = re.search(r'^description:\s*(.+)$', m.group(1), re.M)
        if dm:
            desc = dm.group(1).strip()
        text = text[m.end():].lstrip('\n')
    return text, desc


def install_skills(repo, home, dry):
    custom = home / 'workspace' / 'custom-skills'
    installed = []
    for name, (title, category, desc_override) in load_originals(repo).items():
        src = repo / 'skills' / name / 'SKILL.md'
        text, desc = strip_frontmatter(src.read_text(encoding='utf-8'))
        if not desc:
            q = re.search(r'^>\s*(.+)$', text, re.M)
            desc = q.group(1).strip() if q else title
        if desc_override:
            desc = desc_override
        if dry:
            log(f'  [dry-run] install skill {name} -> {custom / name}')
            continue
        dest = custom / name
        dest.mkdir(parents=True, exist_ok=True)
        (dest / 'SKILL.md').write_text(text, encoding='utf-8')
        yaml = ('name: "%s"\ntitle: "%s"\ndescription: "%s"\ncategory: "%s"\ninclude_in_prompt: false\n'
                % (name, title, desc.replace('"', "'"), category))
        (dest / 'skill.yaml').write_text(yaml, encoding='utf-8')
        installed.append(name)
    # router: include_in_prompt true + registry copy
    router_src = repo / 'skills' / 'router'
    if dry:
        log(f'  [dry-run] install router muse-rsi -> {custom / "muse-rsi"}')
    else:
        dest = custom / 'muse-rsi'
        dest.mkdir(parents=True, exist_ok=True)
        text, _ = strip_frontmatter((router_src / 'SKILL.md').read_text(encoding='utf-8'))
        (dest / 'SKILL.md').write_text(text, encoding='utf-8')
        (dest / 'skill.yaml').write_text(
            'name: "muse-rsi"\ntitle: "muse-rsi Router"\n'
            'description: "Route any task to the right verified Muse skill from the muse-rsi index."\n'
            'category: "Work and knowledge"\ninclude_in_prompt: true\n', encoding='utf-8')
        shutil.copyfile(router_src / 'registry.json', dest / 'registry.json')
        installed.append('muse-rsi (router)')
    return installed


def _sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def _gitleaks_arch():
    system, machine = platform.system().lower(), platform.machine().lower()
    mapping = {('linux', 'x86_64'): 'linux_x64', ('linux', 'amd64'): 'linux_x64',
               ('linux', 'aarch64'): 'linux_arm64', ('linux', 'arm64'): 'linux_arm64',
               ('darwin', 'arm64'): 'darwin_arm64', ('darwin', 'x86_64'): 'darwin_x64'}
    arch = mapping.get((system, machine))
    if not arch:
        raise RuntimeError(f'unsupported platform for gitleaks: {system} {machine}')
    return arch


def install_gitleaks(home, dry):
    dest_dir = home / 'workspace' / 'tools' / 'gitleaks'
    exe = dest_dir / 'gitleaks'
    if exe.exists():
        r = run([str(exe), 'version'])
        if r.returncode == 0:
            return f'already installed ({r.stdout.strip()})'
    if dry:
        return '[dry-run] would download latest gitleaks release'
    arch = _gitleaks_arch()
    try:
        tag = http_get_json('https://api.github.com/repos/gitleaks/gitleaks/releases/latest')['tag_name']
    except Exception:  # noqa: BLE001 - GitHub API rate limit: fall back to a pinned, verified release
        tag = 'v8.30.1'
    ver = tag.lstrip('v')
    asset = f'gitleaks_{ver}_{arch}.tar.gz'
    base = f'https://github.com/gitleaks/gitleaks/releases/download/{tag}'
    HEALER.ensure_dir(dest_dir)
    tarball = dest_dir / asset
    HEALER.download(f'{base}/{asset}', tarball)
    # SHA-256 verification against the release's own checksums file.
    # A mismatch aborts the install — never extract an unverified binary.
    sums = dest_dir / f'gitleaks_{ver}_checksums.txt'
    HEALER.download(f'{base}/gitleaks_{ver}_checksums.txt', sums)
    expected = None
    for line in sums.read_text(encoding='utf-8').splitlines():
        parts = line.split()
        if len(parts) == 2 and parts[1].strip('*') == asset:
            expected = parts[0]
    if not expected:
        raise RuntimeError(f'no SHA-256 entry for {asset} in the release checksums file')
    actual = _sha256(tarball)
    if actual != expected:
        tarball.unlink(missing_ok=True)
        raise RuntimeError(f'gitleaks checksum mismatch for {asset} (expected {expected[:16]}…, got {actual[:16]}…) — refusing to install')
    HEALER.extract_tar(tarball, dest_dir, ['gitleaks'])
    tarball.unlink(missing_ok=True)
    sums.unlink(missing_ok=True)
    os.chmod(exe, 0o755)
    r = run([str(exe), 'version'], check=True)
    return f'installed {r.stdout.strip()} (release {tag}, SHA-256 verified)'


def _chrome_platform():
    system, machine = platform.system().lower(), platform.machine().lower()
    if system == 'linux' and machine in ('x86_64', 'amd64'):
        return 'linux64', 'chrome-headless-shell-linux64'
    if system == 'darwin' and machine == 'arm64':
        return 'mac-arm64', 'chrome-headless-shell-mac-arm64'
    raise RuntimeError(f'unsupported platform for Chrome headless shell: {system} {machine}')


def install_visual_check(repo, home, dry):
    src_dir = repo / 'tools' / 'visual-check'
    dest_dir = home / 'workspace' / 'tools' / 'visual-check'
    if dry:
        return '[dry-run] would install Playwright + Chrome headless shell + axe'
    HEALER.ensure_dir(dest_dir)
    HEALER.ensure_node()
    for f in ('check.mjs', 'package.json', 'package-lock.json'):
        if (src_dir / f).exists():
            shutil.copyfile(src_dir / f, dest_dir / f)
    if (dest_dir / 'package-lock.json').exists():
        r = run(['npm', 'ci', '--no-audit', '--no-fund'], cwd=str(dest_dir))
        if r.returncode != 0:
            HEALER.heal(RuntimeError(r.stdout + r.stderr))
            HEALER.fix('npm ci failed -> retried with npm install from the lockfile')
            run(['npm', 'install', '--no-audit', '--no-fund'], cwd=str(dest_dir), check=True)
    else:
        run(['npm', 'install', '--save-exact', 'playwright@1.65.1', '@axe-core/playwright@4.11.0'],
            cwd=str(dest_dir), check=True)
    plat, dirname = _chrome_platform()
    chrome_dir = dest_dir / dirname
    if not (chrome_dir / 'chrome-headless-shell').exists():
        zip_path = dest_dir / 'chrome-headless-shell.zip'
        verified = False
        try:
            data = http_get_json('https://googlechromelabs.github.io/chrome-for-testing/'
                                 'last-known-good-versions-with-downloads.json')
            stable = data['channels']['Stable']
            dl = next(d for d in stable['downloads']['chrome-headless-shell']
                      if d['platform'] == plat)
            url, expected_sha = dl['url'], dl['sha256']
            try:
                HEALER.download(url, zip_path, sha256=expected_sha)
            except RuntimeError as e:
                if 'checksum mismatch' in str(e):
                    raise RuntimeError(f'Chrome headless shell checksum mismatch — refusing to install ({e})')
                raise
            verified = True
            log(f'    Chrome headless shell {stable["version"]} ({plat}), SHA-256 verified')
        except Exception as e:  # noqa: BLE001 - JSON endpoint unreachable: pinned fallback
            if isinstance(e, RuntimeError) and 'checksum mismatch' in str(e):
                raise
            url = ('https://storage.googleapis.com/chrome-for-testing-public/'
                   '159.0.8154.6/linux64/chrome-headless-shell-linux64.zip')
            HEALER.download(url, zip_path)
            HEALER.test_zip(zip_path)
            log('    WARNING: chrome-for-testing JSON unreachable — installed pinned 159.0.8154.6 '
                'with zip-integrity test only (no upstream SHA-256 available for the pinned build)')
        HEALER.extract_zip(zip_path, dest_dir)
        zip_path.unlink(missing_ok=True)
    r = run([str(chrome_dir / 'chrome-headless-shell'), '--version'], check=True)
    return f'installed (Playwright 1.65.1 + axe 4.11.0 + {r.stdout.strip()})'



def main():
    global HEALER
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--home', default=None)
    ap.add_argument('--repo', default=None)
    ap.add_argument('--name', default=None, help='agent name for a fresh install')
    ap.add_argument('--user-name', default=None)
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--yes', action='store_true', help='skip the confirmation prompt')
    ap.add_argument('--no-visual-check', action='store_true')
    ap.add_argument('--no-gitleaks', action='store_true')
    ap.add_argument('--skills-only', action='store_true',
                    help='install skills + tools only; do not touch SOUL.md, IDENTITY.md, USER.md, MEMORY.md, AGENTS.md, or the vault')
    ap.add_argument('--resume', action='store_true',
                    help='continue a failed install/update: steps that already succeeded for this repo version are skipped')
    args = ap.parse_args()

    home = pathlib.Path(args.home) if args.home else pathlib.Path.home()
    here = pathlib.Path(__file__).resolve()
    repo = pathlib.Path(args.repo) if args.repo else here.parent.parent
    tpl = here.parent / 'templates'
    for f in ('SOUL-system.md', 'IDENTITY.md', 'MEMORY.md', 'AGENTS-additions.md',
              'TOOLS.md', 'HEARTBEAT.md', 'PROACTIVE_PREFERENCES.md'):
        if not (tpl / f).exists():
            sys.exit(f'template missing: {tpl / f}')
    if not (repo / 'skills' / 'router' / 'registry.json').exists():
        sys.exit(f'not a muse-rsi repo (no skills/router/registry.json): {repo}')

    HEALER = selfheal.Healer(home, log)
    runner = selfheal.StepRunner(home, repo, log, HEALER, resume=args.resume, dry_run=args.dry_run)

    # --- detect existing character (read-only) ---
    def read_home(name):
        p = home / name
        return p.read_text(encoding='utf-8') if p.exists() else None

    identity = read_home('IDENTITY.md')
    soul = read_home('SOUL.md')
    user_md = read_home('USER.md')
    memory = read_home('MEMORY.md')
    agents = read_home('AGENTS.md')
    found_name = find_name(identity)
    agent_name = found_name or args.name or 'Muse'
    user_name = find_name(user_md) or args.user_name

    log(f'muse-rsi setup — home: {home}  repo: {repo}  version: {runner.version}')
    if identity:
        if found_name:
            log(f'agent detected: {agent_name!r} (from IDENTITY.md)')
        elif args.name:
            log(f'agent name: {agent_name!r} (from --name; IDENTITY.md had no readable name)')
        else:
            log(f'WARNING: no name found in IDENTITY.md — using fallback name {agent_name!r}. Pass --name to set it.')
    else:
        log('agent: fresh install, name defaults to "Muse"')
    if user_name:
        log(f'user detected: {user_name!r}')
    if args.dry_run:
        log('DRY RUN — nothing will be written.')

    if not args.yes and not args.dry_run:
        ans = input('Install/upgrade the muse-rsi system? Existing files are snapshotted first. [y/N] ')
        if ans.strip().lower() not in ('y', 'yes'):
            print('Aborted. Nothing changed.')
            return 0

    staged = []
    bottlenecks = []

    def write_home(name, text):
        if args.skills_only:
            log(f'  [skills-only] skipped writing {name}')
            return
        if args.dry_run:
            log(f'  [dry-run] would write {name} ({len(text)} bytes)')
            return
        try:
            (home / name).write_text(text, encoding='utf-8')
        except OSError as e:
            # Muse VMs block shell writes to SOUL.md / IDENTITY.md / MEMORY.md
            # (PermissionError: Operation not permitted). That is the runtime's
            # rule, not a broken environment: never chmod around it. Stage the
            # content where the agent's own file tool can reach it (issue #1).
            staging = HEALER.ensure_dir(home / 'workspace' / '.muse-rsi-staging')
            sp = staging / name
            sp.write_text(text, encoding='utf-8')
            staged.append((name, sp))
            log(f'  STAGED {name}: shell write blocked ({e}); content saved to {sp} — apply it with your own file tool, then delete the staging copy.')

    # --- 0. dependencies the loop scripts need (PyYAML) ---
    if not args.dry_run:
        runner.step('0-deps', lambda: log('[0] deps: ' + HEALER.ensure_python_module('yaml', 'pyyaml')) or 'ok')

    # --- 1. snapshot ---
    def do_snapshot():
        if args.skills_only:
            log('[1] Snapshot skipped (--skills-only: no system files touched)')
            return None
        if args.dry_run:
            return None
        stamp = datetime.datetime.now().strftime('%Y-%m-%d-%H%M%S')
        b = home / '.muse-backup' / stamp
        HEALER.ensure_dir(b.parent)
        b.mkdir(exist_ok=False)
        for name in RUNTIME_FILES:
            p = home / name
            if p.exists():
                shutil.copyfile(p, b / name)
        log(f'[1] Snapshot -> {b} ({len(list(b.iterdir()))} files)')
        return str(b)
    backup = runner.step('1-snapshot', do_snapshot)

    # --- 2. SOUL.md merge (character kept, system replaced) ---
    soul_tpl = (tpl / 'SOUL-system.md').read_text(encoding='utf-8')
    new_soul = merge_soul(soul, soul_tpl, agent_name)

    def do_soul():
        if soul is None:
            log('[2] SOUL.md: fresh install — wrote template sections')
        else:
            sys_heads = {h.strip() for h, _ in split_sections(soul_tpl)[1]}
            kept = [h for h, _ in split_sections(soul)[1] if h.strip() not in sys_heads]
            log(f'[2] SOUL.md: kept {len(kept)} character section(s) ({", ".join(h[3:][:28] for h in kept) or "none"}), replaced system block (marker-delimited)')
        write_home('SOUL.md', new_soul)
        return 'ok'
    runner.step('2-soul', do_soul)

    # --- 2b. Loop Engine baseline for SOUL §1-4 ---
    # The engine HALTs when the live §1-4 block differs from its baseline.
    # An update legitimately changes that block (the template came from the
    # repo, reviewed as hard core), so setup records the new baseline itself:
    # the live SOUL.md matches it as soon as the (possibly staged) file is applied.
    def do_soul_baseline():
        if args.skills_only or args.dry_run:
            return 'skipped'
        i, j = new_soul.find(SYS_START), new_soul.find(SYS_END)
        if i < 0 or j < 0:
            raise RuntimeError('merged SOUL.md has no system block markers')
        digest = hashlib.sha256(new_soul[i:j + len(SYS_END)].encode('utf-8')).hexdigest()
        state = HEALER.ensure_dir(home / '.muse-rsi')
        (state / 'soul_hash.txt').write_text(digest + '\n', encoding='utf-8')
        log(f'[2b] Loop Engine SOUL §1-4 baseline -> {digest[:12]}… (matches the SOUL.md written above)')
        return digest
    runner.step('2b-soul-baseline', do_soul_baseline)

    # --- 3. IDENTITY.md: rewrite from template, keep name + character (Role) ---
    def do_identity():
        identity_tpl = (tpl / 'IDENTITY.md').read_text(encoding='utf-8')
        agent_role = find_name(identity, 'Role') or 'Personal AI agent, upgraded with the muse-rsi operating system.'
        new_identity = merge_identity(identity, identity_tpl, agent_name, agent_role)
        if identity is None:
            log(f'[3] IDENTITY.md: fresh install — wrote template (name {agent_name!r})')
        else:
            log(f'[3] IDENTITY.md: rewrote from template (name {agent_name!r} + character kept)')
        write_home('IDENTITY.md', new_identity)
        return 'ok'
    runner.step('3-identity', do_identity)

    # --- 4. USER.md: keep, or minimal template ---
    def do_user():
        if user_md is None:
            name_line = user_name or 'User'
            log('[4] USER.md: fresh install — wrote minimal template')
            write_home('USER.md', f'# USER.md\n\n- **Name:** {name_line}\n- **Timezone:** (fill in, e.g. Asia/Jakarta)\n\n> Fill in what the agent should remember about you. The setup never overwrites this file.\n')
        else:
            log('[4] USER.md: kept as-is')
        return 'ok'
    runner.step('4-user', do_user)

    # --- 5. MEMORY.md: repair structure, keep facts ---
    def do_memory():
        mem_tpl = (tpl / 'MEMORY.md').read_text(encoding='utf-8')
        if memory is None:
            log('[5] MEMORY.md: fresh install — wrote template')
            write_home('MEMORY.md', mem_tpl)
        elif memory.count('\n') < 3:
            log('[5] MEMORY.md: broken single-line file — replaced from template (old copy is in the snapshot)')
            if user_name:
                mem_tpl = mem_tpl.replace('(fill in the user\'s name)', user_name)
            write_home('MEMORY.md', mem_tpl)
        else:
            log('[5] MEMORY.md: parseable — kept, ensured scene index + system state')
            new_mem = memory
            if 'memory/scenes/' not in new_mem:
                new_mem = new_mem.rstrip() + '\n\nSee `memory/scenes/` for details (env-stack, projects, auth-map, skills, bottlenecks, changelog).\n'
            if 'muse-rsi' not in new_mem:
                new_mem = new_mem.rstrip() + '\n\n## System State\n\n- **Repo numbers:** read `state/facts.json` in the muse-rsi repo (single source of truth — never hand-copy numbers into MEMORY.md).\n'
            write_home('MEMORY.md', new_mem)
        if not args.dry_run and not args.skills_only:
            HEALER.ensure_dir(home / 'memory' / 'scenes' / 'daily')
            for scene, body in {
                'env-stack.md': '# env-stack — Work environment\n\n(Fill in: OS, Node/Python versions, tools in ~/workspace/tools/.)\n',
                'projects.md': '# projects — Active projects & repo rules\n\n(Fill in: the user\'s active projects and their rules.)\n',
                'auth-map.md': '# auth-map — Accounts & vault map\n\nMap only — NEVER write passwords/tokens/.env contents here.\n',
                'skills.md': '# skills — Skill registry & installed tools\n\n- Router `muse-rsi` (248 entries). Generator: `scripts/generate_registry.py` in the muse-rsi repo; registry: `skills/router/registry.json`. Repo numbers: `state/facts.json`.\n',
                'bottlenecks.md': '# bottlenecks — Bottleneck queue\n\nDelete an entry as soon as it is resolved.\n',
                'changelog.md': '# changelog — System changes\n\n- Setup: muse-rsi system installed.\n',
            }.items():
                sp = home / 'memory' / 'scenes' / scene
                if not sp.exists():
                    sp.write_text(body, encoding='utf-8')
        return 'ok'
    runner.step('5-memory', do_memory)

    # --- 6. AGENTS.md: append additions once ---
    def do_agents():
        additions = (tpl / 'AGENTS-additions.md').read_text(encoding='utf-8')
        if agents is None:
            log('[6] AGENTS.md: fresh install — wrote operating rules')
            write_home('AGENTS.md', '# AGENTS.md\n\n' + additions.lstrip('\n'))
        elif 'muse-rsi operating rules' in agents:
            log('[6] AGENTS.md: operating rules already present — kept as-is')
        else:
            log('[6] AGENTS.md: appended operating rules (existing conventions kept)')
            write_home('AGENTS.md', agents.rstrip() + '\n' + additions)
        return 'ok'
    runner.step('6-agents', do_agents)

    # --- 6b. Control files: TOOLS.md / HEARTBEAT.md / PROACTIVE_PREFERENCES.md ---
    def do_control_files():
        if args.skills_only:
            return 'skipped (--skills-only)'
        for _name in ('TOOLS.md', 'HEARTBEAT.md', 'PROACTIVE_PREFERENCES.md'):
            if read_home(_name) is None:
                log(f'[6b] {_name}: fresh install — wrote template')
                write_home(_name, (tpl / _name).read_text(encoding='utf-8'))
            else:
                log(f'[6b] {_name}: already present — kept as-is')
        return 'ok'
    runner.step('6b-control-files', do_control_files)

    # --- 7. vault ---
    def do_vault():
        if args.skills_only:
            log('[7] Vault: skipped (--skills-only)')
            return 'skipped'
        if not args.dry_run:
            vault = home / '.config' / 'muse' / 'vault'
            vault.mkdir(parents=True, exist_ok=True)
            os.chmod(vault, 0o700)
        log('[7] Vault dir ready (chmod 700)')
        return 'ok'
    runner.step('7-vault', do_vault)

    # --- 8. skills ---
    def do_skills():
        installed = install_skills(repo, home, args.dry_run)
        log(f'[8] Skills installed: {len(installed)} ({", ".join(installed)})')
        return installed
    runner.step('8-skills', do_skills)

    # --- 9. tools ---
    if args.no_gitleaks:
        log('[9] gitleaks: NOT installed (--no-gitleaks given) — the secret scan cannot run until it is; '
            'never push publicly before it does')
    else:
        runner.step('9-gitleaks', lambda: log('[9] gitleaks: ' + install_gitleaks(home, args.dry_run)) or 'ok')
    if args.no_visual_check:
        log('[9] visual-check: NOT installed (--no-visual-check given)')
    else:
        runner.step('9-visual-check',
                    lambda: log('[9] visual-check: ' + install_visual_check(repo, home, args.dry_run)) or 'ok')

    def do_tool_scripts():
        if args.dry_run:
            return 'skipped'
        tools = HEALER.ensure_dir(home / 'workspace' / 'tools')
        for src, label in ((repo / 'tools' / 'scan-secrets.sh', 'scan-secrets.sh'),
                           (repo / 'scripts' / 'run_all_checks.sh', 'run_all_checks.sh')):
            if src.exists():
                dest = tools / src.name
                shutil.copyfile(src, dest)
                os.chmod(dest, 0o755)
                log(f'[9] {label} installed')
        return 'ok'
    runner.step('9-tool-scripts', do_tool_scripts)

    # --- 10. verify ---
    if not args.dry_run:
        def do_scan():
            scan = repo / 'tools' / 'scan-secrets.sh'
            gitleaks = home / 'workspace' / 'tools' / 'gitleaks' / 'gitleaks'
            if not gitleaks.exists():
                if args.no_gitleaks:
                    log('[10] secret scan: NOT run (gitleaks not installed by request) — reported, not skipped silently')
                    return 'not run'
                log('[10] secret scan: gitleaks missing -> installing it now')
                HEALER.fix('gitleaks missing at verify -> installed it')
                install_gitleaks(home, False)
            r = run(['bash', str(scan), str(repo)], cwd=str(repo))
            if r.returncode != 0:
                # Leaks are never "healed" — that would weaken the gate.
                bottlenecks.append('secret scan found leaks (or gitleaks failed) — do not push')
                log('[10] secret scan: LEAKS FOUND — halt any public push\n' + r.stdout + r.stderr)
                return 'leaks'
            log('[10] secret scan: CLEAN')
            return 'clean'
        runner.step('10-secret-scan', do_scan, tries=2)

        def do_registry_check():
            r = run([sys.executable, str(repo / 'scripts' / 'generate_registry.py'), '--check'], cwd=str(repo))
            if r.returncode != 0:
                raise RuntimeError('registry --check failed\n' + r.stdout + r.stderr)
            log('[10] registry --check: OK')
            return 'ok'
        runner.step('10-registry-check', do_registry_check, tries=2)

        def do_eval():
            r = run([sys.executable, str(repo / 'scripts' / 'eval_routing.py'),
                     '--registry', str(home / 'workspace' / 'custom-skills' / 'muse-rsi' / 'registry.json')],
                    cwd=str(repo))
            tail = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else ''
            if r.returncode != 0:
                raise RuntimeError('routing eval failed: ' + tail)
            log('[10] routing eval: ' + tail)
            return tail
        runner.step('10-routing-eval', do_eval, tries=2)

    for name, err in runner.failed:
        bottlenecks.append(f'step {name} failed after repair attempts: {err}')

    log('')
    if HEALER.fixes:
        log(f'Self-heal: {len(HEALER.fixes)} repair(s) made so the install could continue:')
        for f in HEALER.fixes:
            log(f'  - {f}')
    if args.dry_run:
        log('DRY RUN done — nothing was written. Re-run without --dry-run to apply.')
    elif args.skills_only:
        log('Selesai: muse-rsi skills installed (skills-only — no system files changed).')
        log(f'Pengaman: identity {agent_name!r} preserved; secret scan mandatory before public push.')
    else:
        log(f'Selesai: muse-rsi system installed. Backup (rollback point): {backup}')
        log(f'Pengaman: snapshot before any change; identity {agent_name!r} preserved; secret scan mandatory before public push.')
    if not args.dry_run:
        log('')
        log('NEXT STEP — activate the 24h RSI loop (the setup cannot schedule it; the agent must):')
        log('  Create a daily scheduled job named rsi-daily-self-improvement, every 24h,')
        log('  that runs the Loop Engine: python3 scripts/rsi_cycle.py run')
        log('  Then trigger the first run manually once, to prove the loop works.')
    if staged:
        log('')
        log('ACTION REQUIRED — the shell cannot write these files on this machine:')
        for name, sp in staged:
            log(f'  - {name}  ->  staged at {sp}')
        log('Apply each staged file to your home directory with your own file tool (not the shell),')
        log('then delete the staging copy. The setup is NOT complete until this is done.')
        log('After applying, verify with: ~/workspace/tools/run_all_checks.sh')
    if bottlenecks:
        log('Bottleneck (everything else finished; fix these, then re-run with --resume):')
        for b in bottlenecks:
            log(' - ' + b)
    if staged and not bottlenecks:
        log('Exit code 20 = STAGED_OK: setup finished, but files above are staged — apply them, then verify.')
        return 20
    return 1 if bottlenecks else 0


if __name__ == '__main__':
    sys.exit(main())
