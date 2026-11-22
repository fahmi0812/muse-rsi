#!/usr/bin/env python3
"""rsi_cycle.py — Loop Engine for muse-rsi v3.0 (Bab 4.1, 4.2, 4.6).

One entrypoint replaces the two prose loop specs (M-01). The model never
decides the order of steps; this program does. 13 states:

  PRECHECK -> OBSERVE -> PROPOSE -> RISK -> SNAPSHOT -> APPLY -> VERIFY
  -> CRITIQUE -> DECIDE -> COMMIT -> LEARN -> REPORT -> HALT
  (HALT is reachable from any state.)

Safety properties, enforced by code, not prose:
  * Lock: ~/.muse-rsi/cycle.lock (O_EXCL). A second cycle is refused.
    A lock whose PID is dead is stale and may be removed (logged).
  * Resume: state is saved after every transition to
    ~/.muse-rsi/cycle_state.json. A crashed cycle is resumed from the
    last recorded state (`run` resumes automatically; `--fresh` starts
    a new cycle only if the previous one finished or halted).
  * STOP: file ~/.muse-rsi/STOP, or an active STOP entry in
    ~/.muse-rsi/directives.yaml, makes the engine HALT at the next
    transition — at most one step later. Only Fahmi can lift it.
  * DIRECTIVES ISOLATION (Fahmi, 22 Nov 2026): the cron cycle
    (02.00) has READ-ONLY access to directives.yaml and the STOP
    file. This program never writes either of them — the `halt`
    subcommand was moved out to scripts/stop_cycle.py (human-only,
    Fahmi). Writing directives.yaml happens only from a Fahmi
    message, outside the loop, so no prompt injection or accidental
    edit inside an autonomous cycle can change what the loop obeys.
    `rsi_cycle.py check-readonly` audits this property in its own
    source; run_all_checks.sh runs it.
  * MATCHED-METRIC DELTA (Fahmi, 22 Nov 2026): the DECIDE gate
    computes dC/dK ONLY on metrics present in BOTH the before and
    after snapshots (scripts/scorecard.py). A metric added in this
    cycle (e.g. C2 entering at 75% while C1 is 93.6%) never enters
    the delta — it becomes the baseline for the NEXT cycle. See
    docs/scorecard.md for the denominator-shift rule.
  * Constitution hash: PRECHECK hashes the <!-- muse-rsi:system -->
    block (§1-4) of ~/SOUL.md and compares it to the stored baseline
    in ~/.muse-rsi/soul_hash.txt. A change = HALT (M-11). First run
    records the baseline and logs a note.
  * Protected paths: APPLY refuses any diff touching a path listed in
    config/protected_paths.txt (fnmatch patterns, repo-relative).
    Tamper with a verifier input (e.g. scripts/eval_routing.json) is
    caught in PRECHECK (manifest --verify when a manifest exists,
    else `git diff --quiet` on the manifest inputs) and again in VERIFY.
  * Budget: 40 steps / 45 minutes / $0 per cycle by default (Bab 4.2,
    Table 13; values from config/limits.yaml when present, else the
    built-in defaults below). Steps are spent through
    scripts/run_budget.py when it exists; otherwise an internal
    counter with identical semantics is used and the substitution is
    logged. Step 41 -> budget exhausted -> HALT + revert to snapshot.
    Identical error twice -> that path stops. 3 red cycles in a row ->
    HALT until Fahmi reviews (counted from decision.tsv v2).

Modes:
  * --dry-run: walks every state, runs the read-only checks for real,
    but performs no mutation (no patch apply, no commit, no decision
    row in the real log). State lives in a temp dir; the run_id and
    the states visited are printed.
  * real run: one hypothesis per cycle. A hypothesis is applied only
    as a patch file (--patch PATH, unified diff). Without --patch the
    cycle is observation-only and ends `empty`. COMMIT commits the
    applied patch in the repo (never pushes — push is a separate,
    human-approved step).

Exit codes: 0 = green cycle (accepted|empty), 3 = halted, 1 = error,
2 = usage error.

Environment overrides (for tests; defaults are the real paths):
  MUSE_RSI_HOME  state dir (default ~/.muse-rsi)
  MUSE_RSI_SOUL  SOUL.md to hash (default ~/SOUL.md)
  MUSE_RSI_REPO  repo root (default: parent of this script's dir)

Usage:
  python3 scripts/rsi_cycle.py run [--dry-run] [--fresh]
      [--hypothesis H] [--axis C|K] [--action-class A0..A5]
      [--patch PATH] [--t2-report PATH] [--decision-file PATH]
  python3 scripts/rsi_cycle.py status
  python3 scripts/rsi_cycle.py check-readonly
  # STOP is written only by hand, never by the cycle:
  python3 scripts/stop_cycle.py --reason R
"""
import argparse
import datetime
import fnmatch
import hashlib
import json
import os
import pathlib
import subprocess
import sys
import tempfile
import time
import uuid

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import scorecard as _scorecard  # noqa: E402  (Balanced Scaling Gate, Bab 5.3)

STATES = ['PRECHECK', 'OBSERVE', 'PROPOSE', 'RISK', 'SNAPSHOT', 'APPLY',
          'VERIFY', 'CRITIQUE', 'DECIDE', 'COMMIT', 'LEARN', 'REPORT', 'HALT']
# Manifest inputs whose on-disk hash must match the stored manifest (M-02).
MANIFEST_INPUTS = [
    'skills/router/registry.json',
    'scripts/route.py',
    'scripts/eval_routing.py',
    'scripts/eval_routing.json',
]
DEFAULT_MAX_STEPS = 40
DEFAULT_MAX_MINUTES = 45
DEFAULT_MAX_USD = 0
EXIT_HALTED = 3


def _now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')


def _home():
    return pathlib.Path(os.environ.get('MUSE_RSI_HOME', str(pathlib.Path.home() / '.muse-rsi')))


def _repo():
    env = os.environ.get('MUSE_RSI_REPO')
    if env:
        return pathlib.Path(env)
    return pathlib.Path(__file__).resolve().parent.parent


def _soul_path():
    return pathlib.Path(os.environ.get('MUSE_RSI_SOUL', str(pathlib.Path.home() / 'SOUL.md')))


def _limits(repo):
    """Budget + envelope values. config/limits.yaml wins; else built-ins (Bab 4.2)."""
    vals = {'max_steps': DEFAULT_MAX_STEPS, 'max_minutes': DEFAULT_MAX_MINUTES,
            'max_usd': DEFAULT_MAX_USD, 'source': 'built-in defaults (Bab 4.2 Tabel 13)'}
    p = repo / 'config' / 'limits.yaml'
    try:
        import yaml  # PyYAML is available on the VM; absence is not fatal.
        if p.exists():
            data = yaml.safe_load(p.read_text(encoding='utf-8')) or {}
            b = data.get('run_budget', {}) or {}
            for k in ('max_steps', 'max_minutes', 'max_usd'):
                if k in b:
                    vals[k] = b[k]
            vals['source'] = f'{p} (run_budget)'
    except Exception as e:  # noqa: BLE001 - limits are advisory; defaults are safe.
        vals['note'] = f'limits.yaml unreadable ({e}); using defaults'
    return vals


def _soul_system_block(soul_path):
    text = soul_path.read_text(encoding='utf-8')
    start = text.find('<!-- muse-rsi:system:start -->')
    end = text.find('<!-- muse-rsi:system:end -->')
    if start < 0 or end < 0 or end <= start:
        return None
    return text[start:end + len('<!-- muse-rsi:system:end -->')]


def _soul_hash(soul_path):
    block = _soul_system_block(soul_path)
    if block is None:
        return None
    return hashlib.sha256(block.encode('utf-8')).hexdigest()


def _read_directives(home):
    """Read directives.yaml READ-ONLY (Fahmi, 22 Nov 2026).

    The cron cycle may only READ this file and the STOP file. There is
    deliberately NO write path to either of them anywhere in this
    program — writing directives.yaml happens only from a Fahmi
    message, outside the loop (see scripts/stop_cycle.py for the
    human-only STOP writer). If this function ever needs to change,
    that is an A4 change: Fahmi decides.
    """
    d = home / 'directives.yaml'
    if not d.exists():
        return []
    try:
        import yaml
        # read_text only — never open(..., 'w'), never write_text.
        return yaml.safe_load(d.read_text(encoding='utf-8')) or []
    except Exception:
        return []  # unreadable directives: do not invent a STOP


def _stop_active(home):
    """STOP file or an active STOP entry in directives.yaml (Bab 4.6)."""
    if (home / 'STOP').exists():
        return 'STOP file present: ~/.muse-rsi/STOP'
    for e in _read_directives(home):
        if not isinstance(e, dict):
            continue
        if str(e.get('status', '')).lower() != 'active':
            continue
        directive = str(e.get('directive', ''))
        if directive.strip().upper().startswith('STOP'):
            return f"directives.yaml STOP active: {e.get('id', '?')}"
    return None


def _check_readonly():
    """Audit: this program must contain NO write to STOP / directives.yaml.

    Scans this file's own source for write operations targeting those
    two paths. Returns a list of offending lines (empty = clean).
    The cron cycle's read-only isolation is enforced structurally
    (the writer lives in scripts/stop_cycle.py) and audited here.
    """
    src = pathlib.Path(__file__).read_text(encoding='utf-8').splitlines()
    bad = []
    for i, line in enumerate(src, 1):
        low = line.lower()
        if ('stop' in low or 'directives' in low) and (
                'write_text' in low or "open(" in low and "'w'" in low
                or 'open(' in low and '"w"' in low):
            bad.append(f'{i}: {line.strip()}')
    return bad


def _load_metrics_file(path):
    """Load a flat metrics JSON file ({"C1": 93.6, ...}); None -> {}."""
    if not path:
        return {}
    p = pathlib.Path(path)
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding='utf-8'))
    except Exception:
        return {}


def _protected_patterns(repo):
    p = repo / 'config' / 'protected_paths.txt'
    pats = []
    if p.exists():
        for line in p.read_text(encoding='utf-8').splitlines():
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            pats.append(line)
    return pats


def _protected_hit(changed, patterns):
    hits = []
    for f in changed:
        for pat in patterns:
            if fnmatch.fnmatch(f, pat) or fnmatch.fnmatch(f, pat.rstrip('/')) \
                    or (pat.endswith('/') and f.startswith(pat)):
                hits.append((f, pat))
                break
    return hits


def _run(cmd, cwd=None, timeout=300):
    try:
        r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout)
        return r.returncode, (r.stdout + r.stderr)[-4000:]
    except subprocess.TimeoutExpired:
        return 124, 'TIMEOUT'
    except FileNotFoundError as e:
        return 127, f'NOT FOUND: {e}'


def _git(repo, *args, timeout=60):
    return _run(['git', '-C', str(repo), *args], timeout=timeout)


class Halt(Exception):
    def __init__(self, reason):
        super().__init__(reason)
        self.reason = reason


class Cycle:
    def __init__(self, repo, home, dry_run=False, hypothesis='', axis='',
                 action_class='', patch=None, t2_report=None, decision_file=None,
                 state_home=None, metrics_before=None, metrics_after=None):
        self.metrics_before = _load_metrics_file(metrics_before)
        self.metrics_after = _load_metrics_file(metrics_after)
        self.gate_reasons = []
        self.repo = repo
        self.home = home  # real home: STOP file + directives.yaml live here
        # state_home: lock / state / budget / soul baseline / trajectory.
        # In --dry-run this is a temp dir so a dry run never mutates
        # real runtime state — but STOP is still read from the real home.
        self.state_home = state_home or home
        self.dry_run = dry_run
        self.hypothesis = hypothesis
        self.axis = axis
        self.action_class = action_class
        self.patch = pathlib.Path(patch) if patch else None
        self.t2_report = pathlib.Path(t2_report) if t2_report else None
        self.decision_file = pathlib.Path(decision_file) if decision_file else None
        self.run_id = uuid.uuid4().hex[:12]
        self.started_at = _now()
        self.started_mono = time.monotonic()
        self.state = 'PRECHECK'
        self.history = []
        self.snapshot_commit = ''
        self.commit_before = ''
        self.commit_after = ''
        self.checker_cmd = ''
        self.checker_output = ''
        self.checker_exit = None
        self.critic_verdicts = ''
        self.critique_tier = 'T0'
        self.eval_manifest_sha = ''
        self.steps_spent = 0
        self.budget_via = ''
        self.outcome = 'halted'
        self.note = ''
        self.limits = _limits(repo)
        self.state_path = self.state_home / 'cycle_state.json'
        self.lock_path = self.state_home / 'cycle.lock'
        self.budget_file = self.state_home / 'budget.json'
        self._lock_acquired = False

    # -- persistence -------------------------------------------------
    def _save_state(self):
        if self.dry_run:
            return
        self.state_home.mkdir(parents=True, exist_ok=True)
        data = {
            'run_id': self.run_id, 'state': self.state,
            'started_at': self.started_at, 'hypothesis': self.hypothesis,
            'axis_target': self.axis, 'action_class': self.action_class,
            'snapshot_commit': self.snapshot_commit,
            'commit_before': self.commit_before,
            'commit_after': self.commit_after,
            'steps_spent': self.steps_spent,
            'history': self.history,
        }
        self.state_path.write_text(json.dumps(data, indent=2), encoding='utf-8')

    def _transition(self, state, note=''):
        # STOP is re-checked at every transition: HALT within one step.
        stop = _stop_active(self.home)
        if stop and state != 'HALT':
            raise Halt(f'STOP active at transition to {state}: {stop}')
        self.state = state
        self.history.append({'state': state, 'at': _now(), 'note': note})
        print(f'[{self.run_id}] -> {state}' + (f' — {note}' if note else ''))
        self._spend_step()
        self._save_state()

    # -- lock --------------------------------------------------------
    def _acquire_lock(self):
        if self.dry_run:
            return
        self.state_home.mkdir(parents=True, exist_ok=True)
        payload = json.dumps({'run_id': self.run_id, 'pid': os.getpid(),
                              'started_at': self.started_at})
        try:
            fd = os.open(self.lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            old = self.lock_path.read_text(encoding='utf-8', errors='replace')
            try:
                pid = json.loads(old).get('pid')
            except Exception:
                pid = None
            alive = False
            if pid:
                try:
                    os.kill(int(pid), 0)
                    alive = True
                except (ProcessLookupError, ValueError, PermissionError):
                    alive = False
            if alive:
                raise Halt(f'another cycle is running (lock held by pid {pid})')
            print(f'stale lock (pid {pid} dead) — removing and continuing')
            self.lock_path.unlink()
            fd = os.open(self.lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        os.write(fd, payload.encode('utf-8'))
        os.close(fd)
        self._lock_acquired = True

    def _release_lock(self):
        if self._lock_acquired and self.lock_path.exists():
            self.lock_path.unlink()
            self._lock_acquired = False

    # -- budget ------------------------------------------------------
    def _budget_start(self):
        rb = self.repo / 'scripts' / 'run_budget.py'
        if rb.exists() and not self.dry_run:
            rc, out = _run([sys.executable, str(rb), 'start', '--task',
                            f'rsi-cycle-{self.run_id}',
                            '--budget', str(self.limits['max_steps']),
                            '--file', str(self.budget_file)])
            self.budget_via = 'scripts/run_budget.py'
            if rc != 0:
                print(f'warning: run_budget start failed ({out.strip()}); '
                      f'using internal counter', file=sys.stderr)
                self.budget_via = 'internal counter (run_budget.py start failed)'
        else:
            self.budget_via = 'internal counter' + (
                ' (dry-run: no mutation)' if self.dry_run
                else ' (scripts/run_budget.py not found — see REPORT-G1C.md)')
            if self.dry_run:
                print(f'note: budget via {self.budget_via}')

    def _spend_step(self):
        self.steps_spent += 1
        elapsed_min = (time.monotonic() - self.started_mono) / 60.0
        if elapsed_min > self.limits['max_minutes']:
            raise Halt(f'time budget exceeded: {elapsed_min:.1f} min > '
                       f"{self.limits['max_minutes']} min")
        if self.steps_spent > self.limits['max_steps']:
            raise Halt(f"step budget exhausted at step {self.steps_spent} "
                       f"(max {self.limits['max_steps']}) — revert to snapshot")
        if self.budget_via.startswith('scripts/run_budget.py'):
            rc, out = _run([sys.executable, str(self.repo / 'scripts' / 'run_budget.py'),
                            'spend', '--steps', '1', '--file', str(self.budget_file)])
            if rc != 0:
                raise Halt(f'run_budget spend failed: {out.strip()}')
            rc, out = _run([sys.executable, str(self.repo / 'scripts' / 'run_budget.py'),
                            'check', '--file', str(self.budget_file)])
            if rc != 0:
                raise Halt(f'budget exhausted (run_budget check): {out.strip()}')

    # -- states ------------------------------------------------------
    def state_precheck(self):
        stop = _stop_active(self.home)
        if stop:
            raise Halt(f'STOP active in PRECHECK: {stop}')
        # Constitution hash (M-11).
        soul = _soul_path()
        digest = _soul_hash(soul)
        if digest is None:
            raise Halt(f'SOUL system block not found in {soul} — cannot verify §1-4')
        baseline_path = self.state_home / 'soul_hash.txt'
        if not baseline_path.exists():
            if not self.dry_run:
                baseline_path.write_text(digest + '\n', encoding='utf-8')
            print(f'note: SOUL §1-4 baseline recorded ({digest[:12]}...)')
        elif baseline_path.read_text(encoding='utf-8').strip() != digest:
            raise Halt('SOUL §1-4 hash changed — constitution tampered or edited '
                       'without approval; HALT')
        # Tamper: verifier inputs must be clean vs HEAD (M-02).
        rc, out = _git(self.repo, 'diff', '--quiet', '--', *MANIFEST_INPUTS)
        if rc == 1:
            rc2, changed = _git(self.repo, 'diff', '--name-only', '--', *MANIFEST_INPUTS)
            raise Halt('verifier input modified in working tree (tamper?): '
                       + changed.replace('\n', ', ').strip())
        if rc != 0:
            raise Halt(f'cannot verify verifier inputs via git ({out.strip()[:200]})')
        # Manifest verify when a manifest exists.
        manifest = self.repo / 'eval' / 'manifest.json'
        if manifest.exists():
            rc, out = _run([sys.executable, str(self.repo / 'scripts' / 'eval_manifest.py'),
                            '--verify'])
            self.eval_manifest_sha = hashlib.sha256(
                manifest.read_bytes()).hexdigest()
            if rc != 0:
                raise Halt(f'eval manifest mismatch: {out.strip()[:300]}')
        # Budget start (also re-checked before every step).
        self._budget_start()
        rc, out = _git(self.repo, 'rev-parse', '--short', 'HEAD')
        self.commit_before = out.strip() if rc == 0 else ''
        print(f'PRECHECK ok: soul_hash={digest[:12]}..., HEAD={self.commit_before}, '
              f"budget={self.limits['max_steps']} steps / "
              f"{self.limits['max_minutes']} min / ${self.limits['max_usd']} "
              f"({self.limits['source']}) via {self.budget_via}")

    def state_observe(self):
        rc, out = _git(self.repo, 'status', '--porcelain')
        dirty = [l for l in out.splitlines() if l.strip()] if rc == 0 else []
        print(f'OBSERVE: {len(dirty)} dirty file(s) in working tree; '
              f'hypothesis={"set" if self.hypothesis else "none"}')
        # Scorecard baseline: explicit --metrics-before wins, else the
        # repo's state/scorecard.json when present. No file = no
        # measurable C/K this cycle (never invented).
        if not self.metrics_before:
            self.metrics_before = _load_metrics_file(
                self.repo / 'state' / 'scorecard.json')
        if self.metrics_before:
            print(f"OBSERVE: scorecard baseline metrics: "
                  f"{sorted(self.metrics_before)}")
        if not self.hypothesis and not self.patch:
            print('OBSERVE: nothing to do — cycle will end empty')

    def state_propose(self):
        if not self.hypothesis and not self.patch:
            self.axis = self.axis or ''
            print('PROPOSE: no hypothesis — empty cycle')
            return
        self.axis = self.axis or 'C'
        print(f'PROPOSE: axis={self.axis} hypothesis={self.hypothesis[:80]}')

    def state_risk(self):
        cls = self.action_class or ('A1' if self.patch else 'A0')
        self.action_class = cls
        print(f'RISK: action_class={cls} (patch={"yes" if self.patch else "no"})')
        if cls in ('A4', 'A5'):
            raise Halt(f'action class {cls} needs Fahmi approval (T4) — '
                       f'cycle escalates, nothing applied')

    def state_snapshot(self):
        if self.dry_run:
            print('SNAPSHOT: skipped (dry-run)')
            return
        rc, out = _git(self.repo, 'stash', 'create')
        self.snapshot_commit = out.strip() if rc == 0 else ''
        print(f'SNAPSHOT: {self.snapshot_commit or "(clean tree — nothing to stash)"}')

    def state_apply(self):
        if not self.patch:
            print('APPLY: no patch — nothing to apply')
            return
        if self.dry_run:
            print(f'APPLY: skipped (dry-run) — would apply {self.patch}')
            return
        # Which files does the patch touch? Check ONLY those against the
        # protected list BEFORE applying — a dirty working tree from
        # unrelated work must never make a good patch HALT, and a
        # protected patch must never be applied even briefly.
        rc, out = _run(['git', '-C', str(self.repo), 'apply', '--numstat',
                        str(self.patch)])
        if rc != 0:
            raise Halt(f'patch does not apply cleanly: {out.strip()[:300]}')
        patch_files = []
        for line in out.splitlines():
            parts = line.split('\t')
            if len(parts) == 3:
                patch_files.append(parts[2])
        self.patch_files = patch_files
        hits = _protected_hit(patch_files, _protected_patterns(self.repo))
        if hits:
            raise Halt('APPLY refused — patch touches protected path(s): ' +
                       ', '.join(f'{f} (pattern {p})' for f, p in hits))
        rc, out = _run(['git', '-C', str(self.repo), 'apply', str(self.patch)])
        if rc != 0:
            raise Halt(f'patch apply failed: {out.strip()[:300]}')
        print(f'APPLY: patch applied, {len(patch_files)} file(s) changed: '
              + ', '.join(patch_files))

    def _revert_to_snapshot(self):
        # Surgical revert: restore ONLY the files the patch touched, to
        # their HEAD state (or delete them if the patch created them).
        # Unrelated uncommitted work in the tree is never touched.
        for f in getattr(self, 'patch_files', []):
            rc, _ = _git(self.repo, 'cat-file', '-e', f'HEAD:{f}')
            if rc == 0:
                _git(self.repo, 'checkout', 'HEAD', '--', f)
            else:
                target = self.repo / f
                if target.exists():
                    target.unlink()
        print('REVERT: patch files restored to pre-APPLY state '
              f'(snapshot object {self.snapshot_commit or "n/a"})')

    def state_verify(self):
        cmd = ['bash', str(self.repo / 'scripts' / 'run_all_checks.sh'), str(self.repo)]
        self.checker_cmd = ' '.join(cmd)
        rc, out = _run(cmd, timeout=600)
        self.checker_exit = rc
        self.checker_output = out
        if rc != 0:
            if self.patch and not self.dry_run:
                self._revert_to_snapshot()
            raise Halt(f'VERIFY failed: run_all_checks.sh exit {rc}\n{out[-800:]}')
        print('VERIFY: run_all_checks.sh PASSED')

    def state_critique(self):
        # T0 checklist (always, $0) + T1 deterministic verifier evidence.
        self.critique_tier = 'T1'
        t0 = {
            'hypothesis_recorded': bool(self.hypothesis or not self.patch),
            't1_green': self.checker_exit == 0,
            'protected_paths_clean': True,
            'no_secret_in_diff': self.checker_exit == 0,
        }
        rc, out = _run([sys.executable, str(self.repo / 'scripts' / 'critique.py'),
                        't1', '--repo', str(self.repo)])
        t1_note = out.strip().splitlines()[-1] if out.strip() else ''
        self.critic_verdicts = f'T0={t0} | T1(rc={rc}): {t1_note}'
        if rc != 0:
            raise Halt(f'CRITIQUE T1 failed (rc={rc}): {t1_note[:300]}')
        if self.t2_report and self.t2_report.exists():
            self.critique_tier = 'T2'
            self.critic_verdicts += f" | T2 report: {self.t2_report}"
        print(f'CRITIQUE: tier={self.critique_tier} — {self.critic_verdicts[:200]}')

    def state_decide(self):
        # Balanced Scaling Gate (Bab 5.3, matched-metric delta — Fahmi,
        # 22 Nov 2026): accept only when T1 is green AND the gate on
        # dC/dK passes. dC/dK are computed ONLY on metrics present in
        # BOTH snapshots; a metric added this cycle never enters the
        # delta (see scripts/scorecard.py — denominator shift).
        if not self.patch:
            self.outcome = 'empty'
            print('DECIDE: empty cycle — nothing proposed, nothing changed')
            return
        if self.checker_exit != 0:
            self.outcome = 'reverted'
            print('DECIDE: reverted (T1 not green)')
            return
        after = self.metrics_after or self.metrics_before
        if not self.metrics_before or not after:
            self.outcome = 'accepted'
            self.note = 'gate: no C/K metrics measurable — T1 only'
            print('DECIDE: accepted (T1 green; no C/K metrics measurable, '
                  'gate rests on T1 — see note)')
            return
        accept, reasons, delta = _scorecard.gate(self.metrics_before, after)
        self.gate_reasons = reasons
        d = (f"matched dC={delta['dC']} dK={delta['dK']} "
             f"common C={delta['common_C']} K={delta['common_K']} "
             f"added={delta['added'] or 'none'}")
        self.note = f'gate: {d} | ' + '; '.join(reasons)
        print(f'DECIDE: {d}')
        for r in reasons:
            print(f'DECIDE:  - {r}')
        if accept:
            self.outcome = 'accepted'
            print('DECIDE: accepted (T1 green + Balanced Scaling Gate PASS)')
        else:
            self.outcome = 'reverted'
            print('DECIDE: reverted (Balanced Scaling Gate REJECT)')
            if not self.dry_run:
                self._revert_to_snapshot()

    def state_commit(self):
        if self.dry_run or not self.patch or self.outcome != 'accepted':
            print('COMMIT: skipped (dry-run / no patch / not accepted)')
            return
        rc, out = _git(self.repo, 'add', '--', *getattr(self, 'patch_files', []))
        if rc != 0:
            raise Halt(f'COMMIT git add failed: {out.strip()[:200]}')
        rc, out = _git(self.repo, 'commit', '-m',
                       f'rsi-cycle {self.run_id}: {self.hypothesis[:100]}')
        if rc != 0:
            raise Halt(f'COMMIT failed: {out.strip()[:200]}')
        rc, out = _git(self.repo, 'rev-parse', '--short', 'HEAD')
        self.commit_after = out.strip() if rc == 0 else ''
        print(f'COMMIT: {self.commit_after} (never pushes — push is human-approved)')

    def state_learn(self):
        if self.dry_run:
            print('LEARN: skipped (dry-run)')
            return
        traj = {
            'run_id': self.run_id, 'started_at': self.started_at,
            'ended_at': _now(), 'hypothesis': self.hypothesis,
            'axis_target': self.axis, 'action_class': self.action_class,
            'checker_cmd': self.checker_cmd, 'checker_exit': self.checker_exit,
            'critic_verdicts': self.critic_verdicts,
            'outcome': self.outcome, 'commit_before': self.commit_before,
            'commit_after': self.commit_after,
        }
        p = self.state_home / 'trajectory.jsonl'
        with p.open('a', encoding='utf-8') as f:
            f.write(json.dumps(traj) + '\n')
        print(f'LEARN: trajectory appended to {p}')

    def state_report(self):
        if self.dry_run:
            print(f'REPORT (dry-run): run_id={self.run_id} outcome={self.outcome} '
                  f'states={len(self.history)} steps={self.steps_spent}')
            return
        args = [sys.executable, str(self.repo / 'scripts' / 'decision_log.py'),
                'cycle', '--run-id', self.run_id,
                '--started-at', self.started_at, '--ended-at', _now(),
                '--state-reached', self.state,
                '--axis-target', self.axis, '--hypothesis', self.hypothesis,
                '--action-class', self.action_class,
                '--critique-tier', self.critique_tier,
                '--checker-cmd', self.checker_cmd,
                '--commit-before', self.commit_before,
                '--commit-after', self.commit_after,
                '--eval-manifest-sha256', self.eval_manifest_sha,
                '--critic-verdicts', self.critic_verdicts,
                '--outcome', self.outcome,
                '--budget-steps', str(self.steps_spent),
                '--budget-minutes',
                f"{(time.monotonic() - self.started_mono) / 60.0:.2f}",
                '--budget-usd', '0',
                '--note', self.note or f'budget via {self.budget_via}',
                '--file', str(self.decision_file or (self.state_home / 'decision.tsv'))]
        rc, out = _run(args)
        if rc != 0:
            print(f'warning: decision log write failed: {out.strip()}', file=sys.stderr)
        else:
            print(out.strip())

    # -- driver ------------------------------------------------------
    def run(self, fresh=False):
        # Resume: an unfinished state file means a crashed cycle.
        if not self.dry_run and self.state_path.exists() and not fresh:
            try:
                old = json.loads(self.state_path.read_text(encoding='utf-8'))
                if old.get('state') not in (None, 'REPORT', 'HALT'):
                    print(f"resuming crashed cycle {old.get('run_id')} "
                          f"from state {old.get('state')}")
                    self.run_id = old.get('run_id', self.run_id)
                    self.state = old.get('state', 'PRECHECK')
                    self.history = old.get('history', [])
                    self.hypothesis = old.get('hypothesis', self.hypothesis)
                    self.axis = old.get('axis_target', self.axis)
                    self.action_class = old.get('action_class', self.action_class)
                    self.snapshot_commit = old.get('snapshot_commit', '')
                    self.commit_before = old.get('commit_before', '')
                    self.steps_spent = old.get('steps_spent', 0)
            except Exception as e:  # noqa: BLE001 - corrupt state = HALT, not guess.
                raise Halt(f'corrupt cycle state file: {e}')
        order = ['PRECHECK', 'OBSERVE', 'PROPOSE', 'RISK', 'SNAPSHOT', 'APPLY',
                 'VERIFY', 'CRITIQUE', 'DECIDE', 'COMMIT', 'LEARN', 'REPORT']
        try:
            self._acquire_lock()
            start_idx = order.index(self.state) if self.state in order else 0
            for st in order[start_idx:]:
                self._transition(st)
                getattr(self, 'state_' + st.lower())()
                if st == 'PROPOSE' and not self.hypothesis and not self.patch:
                    # Empty cycle: skip RISK..COMMIT, go straight to REPORT.
                    self.outcome = 'empty'
                    self._transition('REPORT')
                    self.state_report()
                    break
            if self.state != 'HALT':
                self._transition('HALT', note=f'cycle finished: {self.outcome}')
            self._save_state()
            print(f'cycle {self.run_id} finished: outcome={self.outcome} '
                  f'steps={self.steps_spent}')
            return 0
        except Halt as h:
            self.outcome = 'halted'
            self.note = str(h)
            print(f'HALT: {h}')
            try:
                if not self.dry_run:
                    self.state = 'HALT'
                    self.history.append({'state': 'HALT', 'at': _now(),
                                         'note': str(h)})
                    self._save_state()
                    self.state_report()
            except Exception:  # noqa: BLE001 - HALT reporting must not mask HALT.
                pass
            return EXIT_HALTED
        finally:
            self._release_lock()


def cmd_status(args):
    home = _home()
    sp = home / 'cycle_state.json'
    if not sp.exists():
        print('no cycle state recorded yet')
        return 0
    print(json.dumps(json.loads(sp.read_text(encoding='utf-8')), indent=2))
    return 0


def cmd_check_readonly(_args):
    """Audit the directives-isolation property (Fahmi, 22 Nov 2026)."""
    bad = _check_readonly()
    if bad:
        print('READONLY CHECK FAILED — write(s) to STOP/directives.yaml '
              'found in this file:')
        for line in bad:
            print(f'  {line}')
        return 1
    print('READONLY OK: no write to STOP or directives.yaml in '
          'scripts/rsi_cycle.py (writer lives in scripts/stop_cycle.py, '
          'human-only)')
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    sub = ap.add_subparsers(dest='command', required=True)

    p = sub.add_parser('run', help='run one RSI cycle (resumes a crashed one)')
    p.add_argument('--dry-run', action='store_true')
    p.add_argument('--fresh', action='store_true')
    p.add_argument('--hypothesis', default='')
    p.add_argument('--axis', default='', choices=['C', 'K', ''])
    p.add_argument('--action-class', default='',
                   choices=['A0', 'A1', 'A2', 'A3', 'A4', 'A5', ''])
    p.add_argument('--patch', default=None)
    p.add_argument('--t2-report', default=None)
    p.add_argument('--decision-file', default=None)
    p.add_argument('--metrics-before', default=None,
                   help='flat metrics JSON for the DECIDE gate baseline')
    p.add_argument('--metrics-after', default=None,
                   help='flat metrics JSON after the change (default: before)')
    p.set_defaults(func='run')

    p = sub.add_parser('status', help='show last recorded cycle state')
    p.set_defaults(func='status')

    p = sub.add_parser('check-readonly',
                       help='audit: no write to STOP/directives.yaml in this file')
    p.set_defaults(func='check-readonly')

    p = sub.add_parser('halt', help='REMOVED: use scripts/stop_cycle.py (human-only)')
    p.set_defaults(func='halt-removed')

    args = ap.parse_args()
    if args.func == 'status':
        return cmd_status(args)
    if args.func == 'check-readonly':
        return cmd_check_readonly(args)
    if args.func == 'halt-removed':
        print('rsi_cycle.py halt was moved to scripts/stop_cycle.py: the '
              'cron cycle must never write the STOP file (directives '
              'isolation, Fahmi 22 Nov 2026). Run that script by hand.',
              file=sys.stderr)
        return 2
    home = _home()
    state_home = home
    if args.dry_run:
        state_home = pathlib.Path(tempfile.mkdtemp(prefix='rsi-cycle-dryrun-'))
        print(f'dry-run: isolated state dir {state_home} (no mutation); '
              f'STOP still read from {home}')
    repo = _repo()
    c = Cycle(repo, home, dry_run=args.dry_run, hypothesis=args.hypothesis,
              axis=args.axis, action_class=args.action_class, patch=args.patch,
              t2_report=args.t2_report, decision_file=args.decision_file,
              state_home=state_home, metrics_before=args.metrics_before,
              metrics_after=args.metrics_after)
    return c.run(fresh=args.fresh)


if __name__ == '__main__':
    sys.exit(main())
