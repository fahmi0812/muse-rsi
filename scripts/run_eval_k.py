#!/usr/bin/env python3
"""run_eval_k.py — pass^k runner for the routing eval.

Runs scripts/eval_routing.py k times (default k=5) and reports, per case,
whether it passed in ALL k runs (pass^k), plus the overall pass^k rate
(cases passing every run / total cases). Exits 0 only when every case
passes every run, 1 otherwise.

Honest note: scripts/route.py is deterministic — the same query always
scores the same way — so pass^k == pass^1 today and the k runs are
identical by construction. This harness exists so that a future
stochastic router (sampling, council votes, model calls) can be measured
with the exact same command and the exact same bar. No randomness is
faked here: the runs are real subprocess runs of the real eval.

Usage:
  python3 scripts/run_eval_k.py [--k N] [--registry PATH] [--cases PATH]
"""
import argparse
import pathlib
import re
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent

ap = argparse.ArgumentParser()
ap.add_argument('--k', type=int, default=5, help='number of eval runs (default 5)')
ap.add_argument('--registry', default=None)
ap.add_argument('--cases', default=None)
args = ap.parse_args()
if args.k < 1:
    ap.error('--k must be >= 1')

reg = args.registry or str(HERE.parent / 'skills' / 'router' / 'registry.json')
cases = args.cases or str(HERE / 'eval_routing.json')

case_re = re.compile(r'^\[(PASS|FAIL)\] (.*)$')
total_re = re.compile(r'^(\d+)/(\d+) passed$')

per_case = {}   # query -> [bool, ...] one entry per run
totals = []     # (passed, total) per run
for run in range(1, args.k + 1):
    proc = subprocess.run(
        [sys.executable, str(HERE / 'eval_routing.py'),
         '--registry', reg, '--cases', cases],
        capture_output=True, text=True, encoding='utf-8')
    run_cases = {}
    total = None
    for line in proc.stdout.splitlines():
        m = case_re.match(line)
        if m:
            run_cases[m.group(2)] = m.group(1) == 'PASS'
        t = total_re.match(line)
        if t:
            total = (int(t.group(1)), int(t.group(2)))
    if total is None or len(run_cases) != total[1]:
        print(f'run {run}: could not parse eval output (exit {proc.returncode})')
        print(proc.stdout[-2000:])
        print(proc.stderr[-2000:], file=sys.stderr)
        sys.exit(2)
    totals.append(total)
    for q, ok in run_cases.items():
        per_case.setdefault(q, []).append(ok)
    print(f'run {run}/{args.k}: {total[0]}/{total[1]} passed')

n_cases = len(per_case)
n_pass_k = sum(1 for runs in per_case.values() if all(runs))
print(f'\npass^{args.k}: {n_pass_k}/{n_cases} cases passed every run '
      f'({100.0 * n_pass_k / n_cases:.1f}%)')
flaky_or_failed = {q: runs for q, runs in per_case.items() if not all(runs)}
if flaky_or_failed:
    print(f'cases failing at least one run ({len(flaky_or_failed)}):')
    for q, runs in sorted(flaky_or_failed.items()):
        print(f'  {"".join("P" if r else "F" for r in runs)}  {q}')
    sys.exit(1)
print(f'ALL {n_cases} CASES PASSED ALL {args.k} RUNS')
