"""selfheal.py — fix the environment and resume, instead of stopping to ask (setup v3.2).

Fahmi, 22 Nov 2026: when an install/update step fails, do not stop and do
not ask. Adjust the environment so the step can run, continue from the
step that failed (never from the start), never skip a step silently, and
report what was fixed afterwards.

Two pieces, stdlib only:

  Healer      knows how to repair the usual causes of a failed step:
              a missing folder, a missing tool (curl/tar/unzip fall back to
              Python; Node/npm is installed user-level from nodejs.org with
              a SHA-256 check), a missing Python module (pip --user, then
              ensurepip), a non-writable path (chmod u+rwX on files the user
              owns), a full /tmp (TMPDIR -> ~/workspace/tmp), and flaky
              networks (retries with backoff). Every repair is logged as
              "[fix] ..." so nothing happens silently.

  StepRunner  runs named steps, retries a failed step after the Healer had
              a go at the error, records each result in
              ~/.muse-rsi/install_state.json, and with --resume skips the
              steps that already succeeded for the same repo version.

Hard limits — the Healer never does these, whatever fails:
  * touch the vault contents (~/.config/muse/vault) beyond chmod 700
  * skip or weaken the secret scan, the checks, or any hard-core file
    (config/protected_paths.txt) to make a step pass
  * delete user data (it moves aside or backs up instead)
  * use sudo with a password prompt (only `sudo -n`, never interactive)
  * spend money or use a paid API
"""
import hashlib
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tarfile
import time
import urllib.request
import zipfile

NODE_MAJOR = '24'
FAULT_ENV = 'MUSE_RSI_FAULT_INJECT'  # test hook: comma-separated step names that must fail


class Healer:
    def __init__(self, home, log):
        self.home = pathlib.Path(home)
        self.log = log
        self.fixes = []
        self.env = dict(os.environ)
        self._tmp_checked = False

    # -- bookkeeping ---------------------------------------------------
    def fix(self, msg):
        self.fixes.append(msg)
        self.log(f'  [fix] {msg}')

    def run(self, cmd, cwd=None, check=False, timeout=900):
        self.check_tmp()
        try:
            r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout,
                               stdin=subprocess.DEVNULL, env=self.env)
        except FileNotFoundError as e:
            if check:
                raise RuntimeError(f'command not found: {cmd[0]} ({e})') from e
            return subprocess.CompletedProcess(cmd, 127, '', str(e))
        if check and r.returncode != 0:
            raise RuntimeError(f'command failed: {" ".join(map(str, cmd))}\n{r.stdout[-1500:]}\n{r.stderr[-1500:]}')
        return r

    def have(self, tool):
        return shutil.which(tool, path=self.env.get('PATH')) is not None

    def prepend_path(self, d):
        d = str(d)
        parts = self.env.get('PATH', '').split(os.pathsep)
        if d not in parts:
            self.env['PATH'] = d + os.pathsep + self.env.get('PATH', '')
            os.environ['PATH'] = self.env['PATH']
            self.fix(f'PATH += {d}')

    # -- environment repairs -------------------------------------------
    def check_tmp(self, need_mb=600):
        """Muse VMs have a 512 MB /tmp: big downloads go to ~/workspace/tmp."""
        if self._tmp_checked:
            return
        self._tmp_checked = True
        tmp = self.env.get('TMPDIR', '/tmp')
        try:
            free_mb = shutil.disk_usage(tmp).free // (1 << 20)
        except OSError:
            free_mb = 0
        if free_mb < need_mb:
            alt = self.home / 'workspace' / 'tmp'
            alt.mkdir(parents=True, exist_ok=True)
            self.env['TMPDIR'] = str(alt)
            os.environ['TMPDIR'] = str(alt)
            self.fix(f'{tmp} has {free_mb} MB free (< {need_mb} MB) -> TMPDIR={alt}')

    def ensure_dir(self, path):
        path = pathlib.Path(path)
        try:
            path.mkdir(parents=True, exist_ok=True)
            return path
        except PermissionError:
            parent = path
            while not parent.exists():
                parent = parent.parent
            self.make_writable(parent)
            path.mkdir(parents=True, exist_ok=True)
            self.fix(f'created {path}')
            return path

    def make_writable(self, path):
        """chmod u+rwX on a path the current user owns. Never on the vault."""
        path = pathlib.Path(path)
        vault = self.home / '.config' / 'muse' / 'vault'
        if vault == path or vault in path.parents:
            raise PermissionError(f'refusing to change permissions inside the vault: {path}')
        try:
            st = path.stat()
        except FileNotFoundError:
            return False
        if hasattr(os, 'getuid') and st.st_uid != os.getuid():
            raise PermissionError(f'{path} belongs to another user — not changing its permissions')
        mode = st.st_mode | 0o600 | (0o100 if path.is_dir() else 0)
        os.chmod(path, mode)
        self.fix(f'chmod u+rw{"x" if path.is_dir() else ""} {path}')
        return True

    def ensure_python_module(self, module, package):
        try:
            __import__(module)
            return f'{module} present'
        except ImportError:
            pass
        attempts = [[sys.executable, '-m', 'pip', 'install', '--user', '--quiet', package],
                    [sys.executable, '-m', 'pip', 'install', '--user', '--quiet',
                     '--break-system-packages', package]]
        if self.run([sys.executable, '-m', 'pip', '--version']).returncode != 0:
            r = self.run([sys.executable, '-m', 'ensurepip', '--user'])
            if r.returncode == 0:
                self.fix('pip was missing -> python3 -m ensurepip --user')
        for cmd in attempts:
            if self.run(cmd).returncode == 0:
                self.fix(f'Python module {module} missing -> pip install --user {package}')
                import site
                import importlib
                user_site = site.getusersitepackages()
                if user_site not in sys.path:
                    sys.path.append(user_site)
                importlib.invalidate_caches()
                __import__(module)
                return f'{module} installed (user site)'
        if self.have('sudo') and self.run(['sudo', '-n', 'true']).returncode == 0 and self.have('apt-get'):
            if self.run(['sudo', '-n', 'apt-get', 'install', '-y', f'python3-{package}']).returncode == 0:
                self.fix(f'{module} missing -> sudo -n apt-get install python3-{package}')
                return f'{module} installed (apt)'
        raise RuntimeError(f'Python module {module} could not be installed (pip and ensurepip failed)')

    def ensure_node(self):
        """npm for visual-check. If missing, install Node LTS user-level (no sudo), SHA-256 verified."""
        if self.have('npm') and self.have('node'):
            return 'node/npm present'
        nvm_bin = sorted((pathlib.Path.home() / '.nvm' / 'versions' / 'node').glob('v*/bin'))
        if nvm_bin:
            self.prepend_path(nvm_bin[-1])
            if self.have('npm'):
                return f'node/npm found under {nvm_bin[-1]}'
        import platform
        machine = platform.machine().lower()
        arch = {'x86_64': 'x64', 'amd64': 'x64', 'aarch64': 'arm64', 'arm64': 'arm64'}.get(machine)
        system = platform.system().lower()
        if not arch or system not in ('linux', 'darwin'):
            raise RuntimeError(f'no Node build for {system} {machine}')
        base = f'https://nodejs.org/dist/latest-v{NODE_MAJOR}.x'
        sums = self.fetch_text(f'{base}/SHASUMS256.txt')
        want = f'-{system}-{arch}.tar.gz'
        line = next((ln for ln in sums.splitlines() if ln.strip().endswith(want) and 'node-v' in ln), None)
        if not line:
            raise RuntimeError(f'no {want} entry in {base}/SHASUMS256.txt')
        sha, name = line.split()
        dest_root = self.ensure_dir(self.home / 'workspace' / 'tools' / 'node')
        tarball = dest_root / name
        self.download(f'{base}/{name}', tarball, sha256=sha)
        self.extract_tar(tarball, dest_root)
        tarball.unlink(missing_ok=True)
        bin_dir = dest_root / name[:-len('.tar.gz')] / 'bin'
        self.prepend_path(bin_dir)
        self.fix(f'node/npm missing -> installed {name[:-len(".tar.gz")]} user-level at {bin_dir.parent}')
        return f'installed {name}'

    # -- network + archives with fallbacks -----------------------------
    def fetch_text(self, url, tries=3):
        last = None
        for i in range(tries):
            try:
                req = urllib.request.Request(url, headers={'User-Agent': 'muse-rsi-setup'})
                with urllib.request.urlopen(req, timeout=60) as r:
                    return r.read().decode('utf-8')
            except Exception as e:  # noqa: BLE001
                last = e
                time.sleep(2 * (i + 1))
        raise RuntimeError(f'could not fetch {url}: {last}')

    def download(self, url, dest, sha256=None, tries=3):
        dest = pathlib.Path(dest)
        self.ensure_dir(dest.parent)
        last = None
        for i in range(tries):
            try:
                if self.have('curl'):
                    self.run(['curl', '-fsSL', '--max-time', '600', '-o', str(dest), url], check=True)
                else:
                    if i == 0:
                        self.fix('curl not found -> downloading with Python urllib')
                    req = urllib.request.Request(url, headers={'User-Agent': 'muse-rsi-setup'})
                    with urllib.request.urlopen(req, timeout=600) as r, open(dest, 'wb') as f:
                        shutil.copyfileobj(r, f)
                if sha256 and file_sha256(dest) != sha256:
                    dest.unlink(missing_ok=True)
                    raise RuntimeError(f'checksum mismatch for {url} — refusing the file')
                if i:
                    self.fix(f'download of {url.rsplit("/", 1)[-1]} succeeded on retry {i + 1}')
                return dest
            except RuntimeError as e:
                if 'checksum mismatch' in str(e):
                    raise
                last = e
            except Exception as e:  # noqa: BLE001
                last = e
            time.sleep(3 * (i + 1))
        raise RuntimeError(f'download failed after {tries} tries: {url}: {last}')

    def extract_tar(self, tarball, dest, members=None):
        if self.have('tar'):
            cmd = ['tar', '-xzf', str(tarball), '--no-same-owner'] + list(members or [])
            if self.run(cmd, cwd=str(dest)).returncode == 0:
                return
        self.fix(f'tar unavailable/failed -> extracting {pathlib.Path(tarball).name} with Python tarfile')
        with tarfile.open(tarball, 'r:*') as t:
            names = [m for m in t.getmembers() if not members or m.name in members]
            for m in names:
                target = (pathlib.Path(dest) / m.name).resolve()
                if pathlib.Path(dest).resolve() not in target.parents and target != pathlib.Path(dest).resolve():
                    raise RuntimeError(f'unsafe path in archive: {m.name}')
            t.extractall(dest, members=names)

    def test_zip(self, zip_path):
        if self.have('unzip') and self.run(['unzip', '-t', '-q', str(zip_path)]).returncode == 0:
            return
        with zipfile.ZipFile(zip_path) as z:
            bad = z.testzip()
        if bad:
            raise RuntimeError(f'zip integrity test failed at {bad}')

    def extract_zip(self, zip_path, dest):
        if self.have('unzip') and self.run(['unzip', '-q', '-o', str(zip_path)], cwd=str(dest)).returncode == 0:
            return
        self.fix(f'unzip unavailable/failed -> extracting {pathlib.Path(zip_path).name} with Python zipfile')
        with zipfile.ZipFile(zip_path) as z:
            for info in z.infolist():
                target = (pathlib.Path(dest) / info.filename).resolve()
                if pathlib.Path(dest).resolve() not in target.parents and target != pathlib.Path(dest).resolve():
                    raise RuntimeError(f'unsafe path in zip: {info.filename}')
                z.extract(info, dest)
                mode = (info.external_attr >> 16) & 0o777
                if mode:
                    os.chmod(target, mode)

    # -- generic repair from an error message --------------------------
    def heal(self, err):
        """Try to remove the cause of `err`. Returns True if something was changed."""
        text = str(err)
        low = text.lower()
        changed = False
        if 'no space left' in low or 'enospc' in low:
            self._tmp_checked = False
            before = self.env.get('TMPDIR')
            self.check_tmp(need_mb=10 ** 9)
            changed = self.env.get('TMPDIR') != before
        if 'permission denied' in low or isinstance(err, PermissionError):
            path = getattr(err, 'filename', None)
            if path:
                p = pathlib.Path(path)
                for cand in (p, p.parent):
                    try:
                        if cand.exists() and self.make_writable(cand):
                            changed = True
                            break
                    except PermissionError as e:
                        self.log(f'  [fix skipped] {e}')
        if isinstance(err, FileNotFoundError) and getattr(err, 'filename', None):
            parent = pathlib.Path(err.filename).parent
            if not parent.exists():
                self.ensure_dir(parent)
                self.fix(f'created missing folder {parent}')
                changed = True
        for tool in ('npm', 'node', 'npx'):
            if f'command not found: {tool}' in low or f"'{tool}'" in low and 'no such file' in low:
                try:
                    self.ensure_node()
                    changed = True
                except Exception as e:  # noqa: BLE001
                    self.log(f'  [fix failed] could not install Node: {e}')
        if 'npm' in low and ('eacces' in low or 'cache' in low):
            cache = self.ensure_dir(self.home / 'workspace' / '.npm-cache')
            if self.env.get('npm_config_cache') != str(cache):
                self.env['npm_config_cache'] = str(cache)
                self.fix(f'npm cache not writable -> npm_config_cache={cache}')
                changed = True
        if any(k in low for k in ('timed out', 'timeout', 'temporary failure', 'connection reset',
                                  'could not resolve', 'econnreset', 'etimedout', '502', '503', '504')):
            time.sleep(5)
            changed = True  # transient network error: a plain retry is the fix
        return changed


def file_sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


class StepRunner:
    """Runs named steps with heal-and-retry, and remembers results for --resume."""

    def __init__(self, home, repo, log, healer, resume=False, dry_run=False):
        self.log = log
        self.healer = healer
        self.dry_run = dry_run
        self.path = pathlib.Path(home) / '.muse-rsi' / 'install_state.json'
        self.version = _repo_version(repo)
        self.failed = []
        self.results = {}
        self.state = {'version': self.version, 'steps': {}}
        faults = os.environ.get(FAULT_ENV, '')
        self.faults = {f.strip() for f in faults.split(',') if f.strip()}
        if not resume and self.path.exists():
            # Re-running the same command after a failure continues from the
            # failed step on its own: no flag needed, never back to the start.
            try:
                old = json.loads(self.path.read_text(encoding='utf-8'))
                if old.get('version') == self.version and any(
                        v.get('status') == 'failed' for v in old.get('steps', {}).values()):
                    resume = True
                    log('RESUME (auto): the last run of this version failed part-way — continuing from the failed step')
            except (ValueError, OSError):
                pass
        if resume and self.path.exists():
            try:
                old = json.loads(self.path.read_text(encoding='utf-8'))
                if old.get('version') == self.version:
                    self.state = old
                    done = [k for k, v in old.get('steps', {}).items() if v.get('status') == 'done']
                    log(f'RESUME: continuing install of {self.version} — {len(done)} step(s) already done')
                else:
                    log(f"RESUME: repo changed ({old.get('version')} -> {self.version}) — every step runs again")
            except (ValueError, OSError) as e:
                log(f'RESUME: unreadable install state ({e}) — every step runs again')

    def done(self, name):
        return self.state['steps'].get(name, {}).get('status') == 'done'

    def data(self, name):
        return self.state['steps'].get(name, {}).get('data')

    def step(self, name, fn, tries=3):
        if self.done(name):
            self.log(f'[{name}] already done (resume) — skipped, not repeated')
            return self.data(name)
        last = None
        for attempt in range(1, tries + 1):
            try:
                if name in self.faults:
                    raise RuntimeError(f'injected fault ({FAULT_ENV}) in step {name}')
                result = fn()
                self._record(name, 'done', data=result if _jsonable(result) else None)
                if attempt > 1:
                    self.log(f'[{name}] passed on attempt {attempt} after repair')
                self.results[name] = result
                return result
            except Exception as e:  # noqa: BLE001 - a failed step is healed, retried, then reported
                last = e
                self.log(f'[{name}] attempt {attempt}/{tries} failed: {str(e).splitlines()[0][:300]}')
                if attempt < tries and not self.healer.heal(e):
                    time.sleep(1)
        self._record(name, 'failed', error=str(last)[:2000])
        self.failed.append((name, str(last).splitlines()[0][:300] if str(last) else repr(last)))
        self.log(f'[{name}] FAILED after {tries} attempts — reported, setup continues with the next step; '
                 f're-run with --resume to retry only what failed')
        return None

    def _record(self, name, status, error=None, data=None):
        if self.dry_run:
            return
        entry = {'status': status, 'at': time.strftime('%Y-%m-%dT%H:%M:%S%z')}
        if error:
            entry['error'] = error
        if data is not None:
            entry['data'] = data
        self.state['steps'][name] = entry
        self.state['version'] = self.version
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.write_text(json.dumps(self.state, indent=2), encoding='utf-8')
        except OSError as e:
            self.log(f'  warning: could not save install state ({e}) — resume will redo this step')


def _jsonable(x):
    try:
        json.dumps(x)
        return True
    except (TypeError, ValueError):
        return False


def _repo_version(repo):
    repo = pathlib.Path(repo)
    try:
        r = subprocess.run(['git', '-C', str(repo), 'rev-parse', '--short', 'HEAD'],
                           capture_output=True, text=True, timeout=30)
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        pass
    h = hashlib.sha256()
    for rel in ('setup/setup.py', 'skills/router/registry.json', 'state/facts.json'):
        p = repo / rel
        if p.exists():
            h.update(p.read_bytes())
    return 'tree-' + h.hexdigest()[:12]
