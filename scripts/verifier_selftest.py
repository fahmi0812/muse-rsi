#!/usr/bin/env python3
"""verifier_selftest.py — proves the checks still catch known-bad input (v3.1).

Maximum autonomy lets the loop change verifier and engine code (class A4,
merged after the veto window). The risk is a change that quietly makes a
check stop checking. This self-test is the counterweight: it feeds every
guard a known-bad input in a throwaway copy of the repo and fails if the
guard lets it through. CI runs it on every change, so a weakening patch
turns red and never merges. This file is in the hard core
(config/protected_paths.txt) and its SHA-256 is pinned by CI.

Probes (each must REJECT the bad input, and the clean copy must pass):
  1. drift_check   catches a stale number planted in a doc
  2. gen_facts     --check catches a tampered fact
  3. run_budget    refuses the step past the budget
  4. critique      calibrate catches >= target of tests/bad
  5. autonomy_gate classifies loosening as HARD and additions as VETO
  6. rsi_cycle     HALTs on a tampered verifier input
  7. rsi_cycle     HALTs when the STOP file exists

Usage: python3 scripts/verifier_selftest.py [--repo DIR] [--quick]
  --quick skips the two rsi_cycle probes (they run the eval twice).
Exit 0 = every probe rejected its bad input; 1 = a guard let bad input through.
"""
import argparse
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile

PY = sys.executable
RESULTS = []


def run(cmd, cwd=None, env=None, timeout=600):
    r = subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True, timeout=timeout)
    return r.returncode, (r.stdout + r.stderr)


def probe(name, ok, detail=''):
    RESULTS.append((name, ok, detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f' — {detail}' if detail else ''))


def copy_repo(repo, dest, with_git=False):
    ignore = shutil.ignore_patterns('__pycache__', 'node_modules', *([] if with_git else ['.git']))
    shutil.copytree(repo, dest, ignore=ignore, symlinks=True)
    return dest


def p_drift(repo, tmp):
    c = copy_repo(repo, tmp / 'drift')
    rc_clean, out_clean = run([PY, str(c / 'scripts/drift_check.py'), '--repo', str(c)])
    (c / 'docs' / 'zz-selftest-stale.md').write_text(
        'The registry has 261 entries and the eval is 17/17.\n', encoding='utf-8')
    rc_bad, _ = run([PY, str(c / 'scripts/drift_check.py'), '--repo', str(c)])
    probe('drift_check catches a planted stale number', rc_clean == 0 and rc_bad != 0,
          f'clean rc={rc_clean}, stale rc={rc_bad}' + ('' if rc_clean == 0 else f' | {out_clean[-200:]}'))


def p_facts(repo, tmp):
    facts = repo / 'state' / 'facts.json'
    bad = tmp / 'facts-tampered.json'
    data = json.loads(facts.read_text(encoding='utf-8'))
    data['registry_total'] = int(data.get('registry_total', 0)) + 1
    bad.write_text(json.dumps(data, indent=2), encoding='utf-8')
    rc_bad, _ = run([PY, str(repo / 'scripts/gen_facts.py'), '--check', '--repo', str(repo),
                     '--out', str(bad)])
    probe('gen_facts --check catches a tampered fact', rc_bad == 1, f'tampered rc={rc_bad}')


def p_budget(repo, tmp):
    f = tmp / 'budget.json'
    rb = str(repo / 'scripts/run_budget.py')
    rc0, out0 = run([PY, rb, 'start', '--task', 'selftest', '--budget', '3', '--file', str(f),
                     '--force'])
    codes = [run([PY, rb, 'spend', '--steps', '1', '--file', str(f)])[0] for _ in range(4)]
    probe('run_budget refuses the step past the budget',
          rc0 == 0 and codes[:3] == [0, 0, 0] and codes[3] != 0,
          f'start rc={rc0}, spend rcs={codes}' + ('' if rc0 == 0 else f' | {out0[-200:]}'))


def p_critique(repo):
    rc, out = run([PY, str(repo / 'scripts/critique.py'), 'calibrate', '--samples',
                   str(repo / 'tests'), '--repo', str(repo)])
    summary = next((ln.strip() for ln in out.splitlines() if ln.strip().startswith('calibration')),
                   f'rc={rc}')
    probe('critique calibrate catches known-bad samples', rc == 0, summary)


def p_gate(repo):
    rc, out = run([PY, str(repo / 'tests/test_autonomy_gate.py')])
    probe('autonomy_gate: loosening = HARD, additions = VETO, engine fix = AUTO, docs = AUTO', rc == 0,
          out.strip().splitlines()[-1] if out.strip() else f'rc={rc}')


def _cycle_env(tmp, name, soul_text):
    home = tmp / f'{name}-home'
    home.mkdir()
    soul = tmp / f'{name}-SOUL.md'
    soul.write_text(soul_text, encoding='utf-8')
    env = dict(os.environ, MUSE_RSI_HOME=str(home), MUSE_RSI_SOUL=str(soul))
    env.pop('MUSE_RSI_REPO', None)
    return env, home


SOUL = ('# SOUL\n<!-- muse-rsi:system:start -->\n## 1. Autonomy\nselftest\n'
        '<!-- muse-rsi:system:end -->\n')


def p_cycle_tamper(repo, tmp):
    c = copy_repo(repo, tmp / 'cycle-tamper', with_git=True)
    env, _ = _cycle_env(tmp, 'tamper', SOUL)
    ev = c / 'scripts' / 'eval_routing.json'
    ev.write_text(ev.read_text(encoding='utf-8') + ' ', encoding='utf-8')
    rc, out = run([PY, str(c / 'scripts/rsi_cycle.py'), 'run', '--dry-run'], env=env)
    probe('rsi_cycle HALTs on a tampered verifier input', rc == 3 and 'tamper' in out.lower(),
          f'rc={rc}')


def p_cycle_stop(repo, tmp):
    c = copy_repo(repo, tmp / 'cycle-stop', with_git=True)
    env, home = _cycle_env(tmp, 'stop', SOUL)
    (home / 'STOP').write_text('selftest\n', encoding='utf-8')
    rc, out = run([PY, str(c / 'scripts/rsi_cycle.py'), 'run', '--dry-run'], env=env)
    probe('rsi_cycle HALTs when STOP exists', rc == 3 and 'STOP' in out, f'rc={rc}')


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--repo', default=str(pathlib.Path(__file__).resolve().parent.parent))
    ap.add_argument('--quick', action='store_true')
    args = ap.parse_args()
    repo = pathlib.Path(args.repo).resolve()
    tmp = pathlib.Path(tempfile.mkdtemp(prefix='verifier-selftest-'))
    try:
        p_drift(repo, tmp)
        p_facts(repo, tmp)
        p_budget(repo, tmp)
        p_critique(repo)
        p_gate(repo)
        if not args.quick:
            p_cycle_tamper(repo, tmp)
            p_cycle_stop(repo, tmp)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    bad = [n for n, ok, _ in RESULTS if not ok]
    if bad:
        print(f'VERIFIER SELFTEST FAILED: {len(bad)} guard(s) let bad input through: '
              + '; '.join(bad))
        return 1
    print(f'VERIFIER SELFTEST OK: {len(RESULTS)} probe(s), every guard rejected its bad input')
    return 0


if __name__ == '__main__':
    sys.exit(main())
