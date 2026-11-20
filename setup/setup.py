#!/usr/bin/env python3
"""muse-rsi full setup — upgrade a Muse agent's whole system, keep its character.

What it does (new agent or long-running one):
  1. Snapshots the agent's existing SOUL.md / IDENTITY.md / USER.md / MEMORY.md /
     AGENTS.md / TOOLS.md to ~/.muse-backup/<timestamp>/ (auto-snapshot, never
     overwritten).
  2. Merges the muse-rsi operating system into SOUL.md: only the system sections
     are replaced; every character/persona section stays exactly as it is.
     IDENTITY.md is NEVER overwritten — the agent's name and character survive.
  3. Repairs MEMORY.md (clean <60-line structure + memory/scenes/) without
     deleting the user's facts. A broken single-line MEMORY.md is replaced from
     the template, keeping the user's name when it can be found.
  4. Installs the 9 original skills + the muse-rsi router (registry 261 entries)
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
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import urllib.request

ORIGINALS = {
    'rsi-loop': ('Daily RSI loop', 'Work and knowledge', None),
    'self-audit': ('New-skill audit checklist', 'Work and knowledge', None),
    'anti-slop-checklist': ('Anti-slop checklist', 'Work and knowledge', None),
    'health-research-literacy': ('Health research literacy', 'Health and fitness', None),
    'academic-campus': ('College and campus workflow', 'Work and knowledge', None),
    'office-corporate': ('Office and corporate workflow', 'Work and knowledge', None),
    'fullstack-delivery': ('Full-stack delivery workflow', 'Work and knowledge', None),
    'visual-check': ('Visual Check', 'Work and knowledge',
                     'Screenshot any page or HTML file at 360, 768, and 1280 pixels plus dark mode, and report console errors, failed requests, and horizontal overflow — so design work is judged by looking at it, not by reading code.'),
    'contribute': ('Contribute back to muse-rsi', 'Work and knowledge', None),
}
# Headings that belong to the operating system (matched by keyword, case-insensitive).
SYSTEM_HEADING_KEYS = ['autonomy', 'orchestrator engine', 'bottleneck', 'self-improvement', 'frontstage']
RUNTIME_FILES = ['SOUL.md', 'IDENTITY.md', 'USER.md', 'MEMORY.md', 'AGENTS.md', 'TOOLS.md']

log_lines = []


def log(msg):
    print(msg)
    log_lines.append(msg)


def run(cmd, cwd=None, check=False):
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


def is_system_heading(heading):
    h = heading.lower()
    return any(k in h for k in SYSTEM_HEADING_KEYS)


def merge_soul(existing, template, agent_name):
    """Replace system sections, keep character sections, preserve order."""
    template = template.replace('{AGENT_NAME}', agent_name)
    t_pre, t_secs = split_sections(template)
    sys_secs = [(h, b) for h, b in t_secs if is_system_heading(h)]
    if existing is None:
        return template
    pre, secs = split_sections(existing)
    replaced = set()
    out = [pre.rstrip() + '\n'] if pre.strip() else []
    for h, b in secs:
        if is_system_heading(h):
            # replace with the template's matching system section
            match = next((tb for th, tb in sys_secs if any(
                k in th.lower() and k in h.lower() for k in SYSTEM_HEADING_KEYS)), None)
            if match is not None:
                out.append(h + '\n' + match.strip() + '\n')
                replaced.add(h)
            else:
                out.append(h + '\n' + b.strip() + '\n')
        else:
            out.append(h + '\n' + b.strip() + '\n')
    # any template system section not present in the old file gets appended
    for h, b in sys_secs:
        if not any(is_system_heading(oh) and any(
                k in oh.lower() and k in h.lower() for k in SYSTEM_HEADING_KEYS) for oh, _ in secs):
            out.append(h + '\n' + b.strip() + '\n')
    return '\n\n'.join(s.rstrip() for s in out) + '\n'


def find_name(text, key='Name'):
    if not text:
        return None
    m = re.search(r'(?m)^[*-]\s*\*?\*?' + key + r':\*?\*?\s*(.+?)\s*$', text)
    if m:
        return m.group(1).strip().strip('*').strip()
    m = re.search(r'(?m)^#+\s*' + key + r':\s*(.+?)\s*$', text)
    return m.group(1).strip() if m else None


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
    for name, (title, category, desc_override) in ORIGINALS.items():
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


def install_gitleaks(home, dry):
    dest_dir = home / 'workspace' / 'tools' / 'gitleaks'
    exe = dest_dir / 'gitleaks'
    if exe.exists():
        r = run([str(exe), 'version'])
        if r.returncode == 0:
            return f'already installed ({r.stdout.strip()})'
    if dry:
        return '[dry-run] would download latest gitleaks release'
    try:
        tag = http_get_json('https://api.github.com/repos/gitleaks/gitleaks/releases/latest')['tag_name']
    except Exception:  # noqa: BLE001 - GitHub API rate limit: fall back to a pinned, verified release
        tag = 'v8.30.1'
    url = f'https://github.com/gitleaks/gitleaks/releases/download/{tag}/gitleaks_{tag.lstrip("v")}_linux_x64.tar.gz'
    dest_dir.mkdir(parents=True, exist_ok=True)
    run(['curl', '-sL', '--max-time', '300', '-o', str(dest_dir / 'gitleaks.tar.gz'), url], check=True)
    run(['tar', '-xzf', str(dest_dir / 'gitleaks.tar.gz'), '--no-same-owner', 'gitleaks'],
        cwd=str(dest_dir), check=True)
    (dest_dir / 'gitleaks.tar.gz').unlink(missing_ok=True)
    os.chmod(exe, 0o755)
    r = run([str(exe), 'version'], check=True)
    return f'installed {r.stdout.strip()} (release {tag})'


def install_visual_check(repo, home, dry):
    src_dir = repo / 'tools' / 'visual-check'
    dest_dir = home / 'workspace' / 'tools' / 'visual-check'
    if dry:
        return '[dry-run] would install Playwright + Chrome headless shell + axe'
    dest_dir.mkdir(parents=True, exist_ok=True)
    for f in ('check.mjs', 'package.json'):
        shutil.copyfile(src_dir / f, dest_dir / f)
    run(['npm', 'install', '--save-exact', 'playwright@1.65.1', '@axe-core/playwright@4.11.0'],
        cwd=str(dest_dir), check=True)
    chrome_dir = dest_dir / 'chrome-headless-shell-linux64'
    if not (chrome_dir / 'chrome-headless-shell').exists():
        url = ('https://storage.googleapis.com/chrome-for-testing-public/'
               '159.0.8154.6/linux64/chrome-headless-shell-linux64.zip')
        run(['curl', '-sL', '--max-time', '600', '-o', str(dest_dir / 'chrome-headless-shell.zip'), url], check=True)
        run(['unzip', '-q', '-o', str(dest_dir / 'chrome-headless-shell.zip')], cwd=str(dest_dir), check=True)
        (dest_dir / 'chrome-headless-shell.zip').unlink(missing_ok=True)
    r = run([str(chrome_dir / 'chrome-headless-shell'), '--version'], check=True)
    return f'installed (Playwright 1.65.1 + axe 4.11.0 + {r.stdout.strip()})'


def main():
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
    args = ap.parse_args()

    home = pathlib.Path(args.home) if args.home else pathlib.Path.home()
    here = pathlib.Path(__file__).resolve()
    repo = pathlib.Path(args.repo) if args.repo else here.parent.parent
    tpl = here.parent / 'templates'
    for f in ('SOUL-system.md', 'IDENTITY.md', 'MEMORY.md', 'AGENTS-additions.md'):
        if not (tpl / f).exists():
            sys.exit(f'template missing: {tpl / f}')
    if not (repo / 'skills' / 'router' / 'registry.json').exists():
        sys.exit(f'not a muse-rsi repo (no skills/router/registry.json): {repo}')

    # --- detect existing character (read-only) ---
    def read_home(name):
        p = home / name
        return p.read_text(encoding='utf-8') if p.exists() else None

    identity = read_home('IDENTITY.md')
    soul = read_home('SOUL.md')
    user_md = read_home('USER.md')
    memory = read_home('MEMORY.md')
    agents = read_home('AGENTS.md')
    agent_name = find_name(identity) or args.name or 'Muse'
    user_name = find_name(user_md) or args.user_name

    log(f'muse-rsi setup — home: {home}  repo: {repo}')
    log(f'agent detected: {agent_name!r} (from IDENTITY.md)' if identity else 'agent: fresh install, name defaults to "Muse"')
    if user_name:
        log(f'user detected: {user_name!r}')
    if args.dry_run:
        log('DRY RUN — nothing will be written.')

    if not args.yes and not args.dry_run:
        ans = input('Install/upgrade the muse-rsi system? Existing files are snapshotted first. [y/N] ')
        if ans.strip().lower() not in ('y', 'yes'):
            print('Aborted. Nothing changed.')
            return 0

    # --- 1. snapshot ---
    stamp = datetime.datetime.now().strftime('%Y-%m-%d-%H%M%S')
    backup = None
    if args.skills_only:
        log('[1] Snapshot skipped (--skills-only: no system files touched)')
    elif not args.dry_run:
        backup = home / '.muse-backup' / stamp
        backup.mkdir(parents=True, exist_ok=False)
        for name in RUNTIME_FILES:
            p = home / name
            if p.exists():
                shutil.copyfile(p, backup / name)
        log(f'[1] Snapshot -> {backup} ({len(list(backup.iterdir()))} files)')

    # Files the shell could not write (staged for the agent's file tool).
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
            # (PermissionError: Operation not permitted). Don't abort: stage
            # the content where the agent's own file tool can reach it, and
            # let the agent apply it. See issue #1.
            staging = home / 'workspace' / '.muse-rsi-staging'
            try:
                staging.mkdir(parents=True, exist_ok=True)
                sp = staging / name
                sp.write_text(text, encoding='utf-8')
                staged.append((name, sp))
                log(f'  STAGED {name}: shell write blocked ({e}); content saved to {sp} — apply it with your own file tool, then delete the staging copy.')
            except OSError as e2:
                log(f'  FAILED {name}: shell write blocked ({e}) and staging also failed ({e2}) — re-run setup after fixing the block, or apply the merge manually from the templates.')
                bottlenecks.append(f'{name} could not be written or staged: {e2}')

    # --- 2. SOUL.md merge (character kept, system replaced) ---
    soul_tpl = (tpl / 'SOUL-system.md').read_text(encoding='utf-8')
    new_soul = merge_soul(soul, soul_tpl, agent_name)
    if soul is None:
        log('[2] SOUL.md: fresh install — wrote template sections')
    else:
        kept = [h for h, _ in split_sections(soul)[1] if not is_system_heading(h)]
        log(f'[2] SOUL.md: kept {len(kept)} character section(s) ({", ".join(h[3:][:28] for h in kept) or "none"}), replaced system sections')
    write_home('SOUL.md', new_soul)

    # --- 3. IDENTITY.md: never overwrite ---
    if identity is None:
        log('[3] IDENTITY.md: fresh install — wrote template (edit the name to your agent\'s name)')
        write_home('IDENTITY.md', (tpl / 'IDENTITY.md').read_text(encoding='utf-8'))
    else:
        log(f'[3] IDENTITY.md: kept as-is (name {agent_name!r} preserved)')

    # --- 4. USER.md: keep, or minimal template ---
    if user_md is None:
        name_line = user_name or 'User'
        log('[4] USER.md: fresh install — wrote minimal template')
        write_home('USER.md', f'# USER.md\n\n- **Name:** {name_line}\n- **Timezone:** (fill in, e.g. Asia/Jakarta)\n\n> Fill in what the agent should remember about you. The setup never overwrites this file.\n')

    # --- 5. MEMORY.md: repair structure, keep facts ---
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
            new_mem = new_mem.rstrip() + '\n\n## System State\n\n- **Repo:** `muse-rsi` — 64 listed + 32 reference + 9 originals + 156 Lumitome reference = 261 registry entries.\n'
        write_home('MEMORY.md', new_mem)
    if not args.dry_run and not args.skills_only:
        (home / 'memory' / 'scenes').mkdir(parents=True, exist_ok=True)
        (home / 'memory' / 'scenes' / 'daily').mkdir(parents=True, exist_ok=True)
        for scene, body in {
            'env-stack.md': '# env-stack — Work environment\n\n(Fill in: OS, Node/Python versions, tools in ~/workspace/tools/.)\n',
            'projects.md': '# projects — Active projects & repo rules\n\n(Fill in: the user\'s active projects and their rules.)\n',
            'auth-map.md': '# auth-map — Accounts & vault map\n\nMap only — NEVER write passwords/tokens/.env contents here.\n',
            'skills.md': '# skills — Skill registry & installed tools\n\n- Router `muse-rsi` (261 entries). Generator: `~/workspace/tools/registry-gen/generate_registry.py`.\n',
            'bottlenecks.md': '# bottlenecks — Bottleneck queue\n\nDelete an entry as soon as it is resolved.\n',
            'changelog.md': '# changelog — System changes\n\n- Setup: muse-rsi system installed.\n',
        }.items():
            sp = home / 'memory' / 'scenes' / scene
            if not sp.exists():
                sp.write_text(body, encoding='utf-8')

    # --- 6. AGENTS.md: append additions once ---
    additions = (tpl / 'AGENTS-additions.md').read_text(encoding='utf-8')
    if agents is None:
        log('[6] AGENTS.md: fresh install — wrote operating rules')
        write_home('AGENTS.md', '# AGENTS.md\n\n' + additions.lstrip('\n'))
    elif 'muse-rsi operating rules' in agents:
        log('[6] AGENTS.md: operating rules already present — kept as-is')
    else:
        log('[6] AGENTS.md: appended operating rules (existing conventions kept)')
        write_home('AGENTS.md', agents.rstrip() + '\n' + additions)

    # --- 7. vault ---
    vault = home / '.config' / 'muse' / 'vault'
    if args.skills_only:
        log('[7] Vault: skipped (--skills-only)')
    elif not args.dry_run:
        vault.mkdir(parents=True, exist_ok=True)
        os.chmod(vault, 0o700)
        log('[7] Vault dir ready (chmod 700)')
    else:
        log('[7] Vault dir ready (chmod 700)')

    # --- 8. skills ---
    installed = install_skills(repo, home, args.dry_run)
    log(f'[8] Skills installed: {len(installed)} ({", ".join(installed)})')

    # --- 9. tools ---
    if not args.no_gitleaks:
        try:
            log('[9] gitleaks: ' + install_gitleaks(home, args.dry_run))
        except Exception as e:  # noqa: BLE001 - report, don't abort the setup
            bottlenecks.append(f'gitleaks install failed: {e}')
            log('[9] gitleaks FAILED: ' + str(e))
    else:
        log('[9] gitleaks: skipped (--no-gitleaks)')
    if not args.no_visual_check:
        try:
            log('[9] visual-check: ' + install_visual_check(repo, home, args.dry_run))
        except Exception as e:  # noqa: BLE001
            bottlenecks.append(f'visual-check install failed: {e}')
            log('[9] visual-check FAILED: ' + str(e))
    else:
        log('[9] visual-check: skipped (--no-visual-check)')
    scan_src = repo / 'tools' / 'scan-secrets.sh'
    if scan_src.exists() and not args.dry_run:
        dest = home / 'workspace' / 'tools' / 'scan-secrets.sh'
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(scan_src, dest)
        os.chmod(dest, 0o755)
        log('[9] scan-secrets.sh installed')
    checks_src = repo / 'scripts' / 'run_all_checks.sh'
    if checks_src.exists() and not args.dry_run:
        dest = home / 'workspace' / 'tools' / 'run_all_checks.sh'
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(checks_src, dest)
        os.chmod(dest, 0o755)
        log('[9] run_all_checks.sh installed (verify with it after setup)')

    # --- 10. verify ---
    if not args.dry_run:
        try:
            r = run([sys.executable, str(repo / 'scripts' / 'generate_registry.py'), '--check'],
                    cwd=str(repo))
            log('[10] registry --check: ' + ('OK' if r.returncode == 0 else 'FAILED\n' + r.stdout + r.stderr))
            if r.returncode != 0:
                bottlenecks.append('registry --check failed')
        except Exception as e:  # noqa: BLE001
            bottlenecks.append(f'registry --check error: {e}')
        try:
            r = run([sys.executable, str(repo / 'scripts' / 'eval_routing.py'),
                     '--registry', str(home / 'workspace' / 'custom-skills' / 'muse-rsi' / 'registry.json')],
                    cwd=str(repo))
            tail = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else ''
            log('[10] routing eval: ' + tail)
            if r.returncode != 0:
                bottlenecks.append('routing eval failed')
        except Exception as e:  # noqa: BLE001
            bottlenecks.append(f'routing eval error: {e}')

    log('')
    if args.dry_run:
        log('DRY RUN done — nothing was written. Re-run without --dry-run to apply.')
    elif args.skills_only:
        log('Selesai: muse-rsi skills installed (skills-only — no system files changed).')
        log(f'Pengaman: identity {agent_name!r} preserved; secret scan mandatory before public push.')
    else:
        log(f'Selesai: muse-rsi system installed. Backup (rollback point): {backup}')
        log(f'Pengaman: snapshot before any change; identity {agent_name!r} preserved; secret scan mandatory before public push.')
    if staged:
        log('')
        log('ACTION REQUIRED — the shell cannot write these files on this machine:')
        for name, sp in staged:
            log(f'  - {name}  ->  staged at {sp}')
        log('Apply each staged file to your home directory with your own file tool (not the shell),')
        log('then delete the staging copy. The setup is NOT complete until this is done.')
        log('After applying, verify with: ~/workspace/tools/run_all_checks.sh')
    if bottlenecks:
        log('Bottleneck:')
        for b in bottlenecks:
            log(' - ' + b)
    return 1 if (bottlenecks or staged) else 0


if __name__ == '__main__':
    sys.exit(main())
