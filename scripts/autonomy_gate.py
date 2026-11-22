#!/usr/bin/env python3
"""autonomy_gate.py — decides how much human involvement a change needs (v3.1).

Maximum-autonomy model (Fahmi, 22 Nov 2026): the agent merges its own
changes when the verifiers pass; Fahmi reviews after the fact (digest,
sampling, `veto` label, STOP). Only a small hard core still needs him.

Every change is classified from its diff, never from what the agent says
about it:

  AUTO  merge as soon as CI is green. Skills, router, registry, docs,
        tools, setup templates, and the eval manifest (CI re-verifies it).
  VETO  merge automatically after the veto window (config/limits.yaml,
        autonomy.veto_window_hours) unless Fahmi labels the PR `veto`.
        Additive or tightening changes to the verifier and engine
        (config/veto_paths.txt), model changes, and changes bigger than
        the per-cycle diff limits.
  HARD  Fahmi merges. Anything that could loosen the safety envelope:
        the files in config/protected_paths.txt, deleting or editing an
        existing eval case, removing a canary test, deleting or editing
        a known-bad calibration sample, deleting any verifier/test file.

The rules only ever move a change toward MORE review, never less: an
unknown situation (unreadable JSON, git error) is HARD.

This file is itself in the hard core, and the CI workflows pin its
SHA-256: a changed gate classifies as HARD until Fahmi re-pins it.

Usage:
  python3 scripts/autonomy_gate.py classify --base REF [--head REF] [--repo DIR]
  python3 scripts/autonomy_gate.py classify --patch FILE [--repo DIR]
      [--json] [--github-output]
  Exit code: 0 AUTO, 10 VETO, 20 HARD, 2 usage/internal error (treat as HARD).
"""
import argparse
import fnmatch
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

EXIT = {'AUTO': 0, 'VETO': 10, 'HARD': 20}
RANK = {'AUTO': 0, 'VETO': 1, 'HARD': 2}

# Files that are AUTO even though they sit under a VETO path: pure
# bookkeeping that CI re-verifies from first principles.
AUTO_OVERRIDES = ['eval/manifest.json', 'state/facts.json']

# Paths whose deletion is always HARD (removing a check = loosening).
NO_DELETE = ['scripts/eval_routing.json', 'eval/', 'tests/', 'scripts/test_canary.py',
             'scripts/eval_*.py', 'scripts/run_eval_k.py', 'scripts/run_all_checks.sh',
             'scripts/gen_facts.py', 'scripts/drift_check.py', 'scripts/critique.py',
             'scripts/run_budget.py', 'scripts/rsi_cycle.py', 'scripts/trust.py',
             'scripts/stop_cycle.py', 'scripts/scorecard.py']

DEFAULT_LIMITS = {'max_files_changed': 10, 'max_diff_lines': 400}


def _patterns(path):
    pats = []
    p = pathlib.Path(path)
    if p.exists():
        for line in p.read_text(encoding='utf-8').splitlines():
            line = line.strip()
            if line and not line.startswith('#'):
                pats.append(line)
    return pats


def _match(f, pats):
    for pat in pats:
        if fnmatch.fnmatch(f, pat) or fnmatch.fnmatch(f, pat.rstrip('/')) \
                or (pat.endswith('/') and f.startswith(pat)):
            return pat
    return None


def _git(repo, *args):
    r = subprocess.run(['git', '-C', str(repo), *args], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)}: {(r.stderr or r.stdout).strip()[:300]}")
    return r.stdout


def _show(repo, ref, path):
    """File content at ref, or None if it does not exist there."""
    r = subprocess.run(['git', '-C', str(repo), 'show', f'{ref}:{path}'],
                       capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None


def _limits(repo):
    vals = dict(DEFAULT_LIMITS)
    p = pathlib.Path(repo) / 'config' / 'limits.yaml'
    if p.exists():
        try:
            import yaml
            data = yaml.safe_load(p.read_text(encoding='utf-8')) or {}
            cyc = data.get('cycle', {}) or {}
            for k in DEFAULT_LIMITS:
                if k in cyc:
                    vals[k] = int(cyc[k])
        except Exception:  # noqa: BLE001 - unreadable limits: keep the strict defaults
            pass
    return vals


def _eval_case_key(case):
    return json.dumps(case, sort_keys=True, ensure_ascii=False)


def _eval_cases_loosened(old_text, new_text):
    """True if any existing eval case was removed or changed."""
    old = json.loads(old_text).get('cases', [])
    new = json.loads(new_text).get('cases', [])
    new_keys = {_eval_case_key(c) for c in new}
    return [c.get('query', '?') for c in old if _eval_case_key(c) not in new_keys]


def _canary_tests_removed(old_text, new_text):
    names = lambda t: set(re.findall(r'^\s*def (test_\w+)', t, re.M))  # noqa: E731
    return sorted(names(old_text) - names(new_text))


def classify_tree(repo, base, head=None, work=None):
    """Classify the change base -> head (or base -> working tree `work`)."""
    repo = pathlib.Path(repo)
    cfg_root = repo  # policy files are read from the BASE side below
    hard = _patterns_at(repo, base, 'config/protected_paths.txt')
    veto = _patterns_at(repo, base, 'config/veto_paths.txt')
    if work is not None:
        status = _git(work, 'diff', '--name-status', '--no-renames', base)
        numstat = _git(work, 'diff', '--numstat', '--no-renames', base)
        read_new = lambda p: _read(pathlib.Path(work) / p)  # noqa: E731
    else:
        status = _git(repo, 'diff', '--name-status', '--no-renames', base, head)
        numstat = _git(repo, 'diff', '--numstat', '--no-renames', base, head)
        read_new = lambda p: _show(repo, head, p)  # noqa: E731
    changes = []
    for line in status.splitlines():
        parts = line.split('\t')
        if len(parts) >= 2:
            changes.append((parts[0][0], parts[-1]))
    lines = 0
    for line in numstat.splitlines():
        a, d, *_ = line.split('\t')
        lines += (int(a) if a.isdigit() else 0) + (int(d) if d.isdigit() else 0)

    verdict, reasons = 'AUTO', []

    def bump(cls, why):
        nonlocal verdict
        reasons.append(f'{cls}: {why}')
        if RANK[cls] > RANK[verdict]:
            verdict = cls

    if not changes:
        reasons.append('AUTO: no file changes')
    lim = _limits(cfg_root)
    for st, f in changes:
        pat = _match(f, hard)
        if pat:
            bump('HARD', f'{f} is in the hard core (protected_paths: {pat})')
            continue
        if st == 'D' and _match(f, NO_DELETE):
            bump('HARD', f'{f} deleted (removing a check loosens the envelope)')
            continue
        if f == 'scripts/eval_routing.json' and st != 'A':
            try:
                gone = _eval_cases_loosened(_show(repo, base, f) or '{}', read_new(f) or '{}')
            except Exception as e:  # noqa: BLE001
                bump('HARD', f'{f} unreadable as JSON ({e})')
                continue
            if gone:
                bump('HARD', f'{f}: {len(gone)} existing eval case(s) removed or edited: '
                             + '; '.join(gone[:3]))
                continue
        if f == 'scripts/test_canary.py' and st != 'A':
            removed = _canary_tests_removed(_show(repo, base, f) or '', read_new(f) or '')
            if removed:
                bump('HARD', f'{f}: canary test(s) removed: {", ".join(removed)}')
                continue
        if f.startswith('tests/bad/') and st != 'A':
            bump('HARD', f'{f}: known-bad calibration sample edited')
            continue
        if f in AUTO_OVERRIDES:
            reasons.append(f'AUTO: {f} (bookkeeping, re-verified by CI)')
            continue
        pat = _match(f, veto)
        if pat:
            bump('VETO', f'{f} is verifier/engine (veto_paths: {pat})')
            continue
        reasons.append(f'AUTO: {f}')
    if len(changes) > lim['max_files_changed']:
        bump('VETO', f"{len(changes)} files > max_files_changed {lim['max_files_changed']}")
    if lines > lim['max_diff_lines']:
        bump('VETO', f"{lines} diff lines > max_diff_lines {lim['max_diff_lines']}")
    return {'class': verdict, 'reasons': reasons, 'files': [f for _, f in changes],
            'diff_lines': lines}


def _read(p):
    try:
        return pathlib.Path(p).read_text(encoding='utf-8')
    except FileNotFoundError:
        return None


def _patterns_at(repo, ref, path):
    """Policy lists are read from the BASE ref, so a change cannot relax its own review."""
    text = _show(repo, ref, path)
    if text is None:
        return _patterns(pathlib.Path(repo) / path)
    pats = []
    for line in text.splitlines():
        line = line.strip()
        if line and not line.startswith('#'):
            pats.append(line)
    return pats


def classify_patch(repo, patch):
    """Apply a patch in a throwaway worktree at HEAD and classify the result."""
    repo = pathlib.Path(repo)
    tmp = pathlib.Path(tempfile.mkdtemp(prefix='autonomy-gate-'))
    wt = tmp / 'wt'
    try:
        _git(repo, 'worktree', 'add', '--detach', str(wt), 'HEAD')
        r = subprocess.run(['git', '-C', str(wt), 'apply', str(pathlib.Path(patch).resolve())],
                           capture_output=True, text=True)
        if r.returncode != 0:
            raise RuntimeError(f'patch does not apply: {(r.stderr or r.stdout).strip()[:300]}')
        _git(wt, 'add', '-A')
        return classify_tree(repo, 'HEAD', work=wt)
    finally:
        subprocess.run(['git', '-C', str(repo), 'worktree', 'remove', '--force', str(wt)],
                       capture_output=True, text=True)
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    sub = ap.add_subparsers(dest='command', required=True)
    p = sub.add_parser('classify')
    p.add_argument('--repo', default=str(pathlib.Path(__file__).resolve().parent.parent))
    p.add_argument('--base')
    p.add_argument('--head', default='HEAD')
    p.add_argument('--patch')
    p.add_argument('--json', action='store_true')
    p.add_argument('--github-output', action='store_true',
                   help='also write class=... to $GITHUB_OUTPUT')
    args = ap.parse_args()
    try:
        if args.patch:
            res = classify_patch(args.repo, args.patch)
        elif args.base:
            res = classify_tree(args.repo, args.base, args.head)
        else:
            print('error: give --base REF or --patch FILE', file=sys.stderr)
            return 2
    except Exception as e:  # noqa: BLE001 - any failure means "needs a human"
        res = {'class': 'HARD', 'reasons': [f'HARD: gate error ({e})'], 'files': [],
               'diff_lines': 0}
        print(json.dumps(res, indent=2) if args.json else f"class=HARD\n  {res['reasons'][0]}")
        _gh_output(args, res)
        return 2
    if args.json:
        print(json.dumps(res, indent=2, ensure_ascii=False))
    else:
        print(f"class={res['class']} files={len(res['files'])} diff_lines={res['diff_lines']}")
        for r in res['reasons']:
            print(f'  {r}')
    _gh_output(args, res)
    return EXIT[res['class']]


def _gh_output(args, res):
    out = os.environ.get('GITHUB_OUTPUT')
    if args.github_output and out:
        with open(out, 'a', encoding='utf-8') as f:
            f.write(f"class={res['class']}\n")


if __name__ == '__main__':
    sys.exit(main())
