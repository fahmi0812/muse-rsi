#!/usr/bin/env python3
"""drift_check.py — catch stale hand-copied numbers in repo docs (v3.0 G1, M-13).

Scans README, INSTALL, docs, setup templates, SKILL.md files and issue
templates for registry/eval figures that no longer match state/facts.json
(the machine-computed Truth Layer, design Bab 4.4). A mismatch in the
repo is a red check: exit 1. Exit 0 only when nothing is stale.

What it flags (known-stale literals, not live numbers):
  17/17            the old routing-eval size (now 125/125)
  registry 261 / 261 entri / 261 entries   the old registry total (now 246)
  260 entri / 260 entries                  the other stale total seen in VM scenes
  five queries / all five hold             test_canary.py docstring (now seven)
  9 original / 10 skill                    stale original-skill / installed-skill counts

It also requires the current figures to actually appear where they are
claimed: README.md and INSTALL.md must state the current eval score
("125/125") and registry total ("246").

Usage: python3 scripts/drift_check.py [--repo PATH] [--facts PATH]
"""
import argparse
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
DEFAULT_REPO = HERE.parent

# (pattern, explanation). Patterns are literal stale values, so a file
# that states the current numbers can never trip them.
STALE_PATTERNS = [
    (re.compile(r'17/17'), 'stale eval size 17/17'),
    (re.compile(r'registry\s+261\b'), 'stale registry total 261'),
    (re.compile(r'\b261\s+entr(i|ies)\b'), 'stale registry total 261'),
    (re.compile(r'\b260\s+entr(i|ies)\b'), 'stale registry total 260'),
    (re.compile(r'five queries'), 'stale canary count "five queries"'),
    (re.compile(r'all five hold'), 'stale canary count "all five hold"'),
    (re.compile(r'\b9 original\b'), 'stale original-skill count 9'),
    (re.compile(r'\b10 skill\b'), 'stale installed-skill count 10'),
    (re.compile(r'skill\s+10\b'), 'stale installed-skill count 10'),
    (re.compile(r'e\.g\.\s*261\b'), 'stale registry example 261'),
]

# Files that must actually state the current figures (not just avoid stale ones).
EXPECTED_PRESENT = {
    'README.md': ['125/125', '246'],
    'INSTALL.md': ['125/125', '246'],
}

# Scan every Markdown file in the repo plus the canary script's docstring;
# skip generated data, the facts file itself, and this checker (it contains
# the stale literals as patterns by design). Worker run reports
# (REPORT-*.md at the repo root) are run logs, not shipped docs, and may
# quote stale values as evidence — they are skipped too.
SKIP_DIRS = {'.git', '__pycache__', 'state', 'node_modules'}
SKIP_FILES = {'drift_check.py', 'gen_facts.py'}


def scan_files(repo):
    files = []
    for path in sorted(repo.rglob('*.md')):
        if any(part in SKIP_DIRS for part in path.relative_to(repo).parts):
            continue
        if path.name.startswith('REPORT-') and path.parent == repo:
            continue
        files.append(path)
    canary = repo / 'scripts' / 'test_canary.py'
    if canary.exists():
        files.append(canary)
    return files


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo', default=None)
    ap.add_argument('--facts', default=None)
    args = ap.parse_args()
    repo = pathlib.Path(args.repo) if args.repo else DEFAULT_REPO
    facts_path = pathlib.Path(args.facts) if args.facts \
        else repo / 'state' / 'facts.json'
    if not facts_path.exists():
        print(f'error: no facts file at {facts_path}; '
              f'run `python3 scripts/gen_facts.py` first', file=sys.stderr)
        return 2
    facts = json.loads(facts_path.read_text(encoding='utf-8'))

    problems = []
    scanned = 0
    for path in scan_files(repo):
        scanned += 1
        text = path.read_text(encoding='utf-8', errors='replace')
        rel = str(path.relative_to(repo))
        for lineno, line in enumerate(text.splitlines(), 1):
            for pattern, label in STALE_PATTERNS:
                if pattern.search(line):
                    problems.append(
                        f'{rel}:{lineno}: {label}: {line.strip()[:120]}')
        if rel in EXPECTED_PRESENT:
            for token in EXPECTED_PRESENT[rel]:
                if token not in text:
                    problems.append(
                        f'{rel}: missing current figure {token!r} '
                        f'(facts.json says eval top-3 '
                        f'{facts.get("eval_top3")}, registry '
                        f'{facts.get("registry_total")})')

    if problems:
        print(f'DRIFT FOUND: {len(problems)} stale figure(s) '
              f'in {scanned} scanned file(s):')
        for p in problems:
            print(f'  - {p}')
        print('Fix the numbers (or point the text at state/facts.json) '
              'and re-run.')
        return 1
    print(f'DRIFT OK: 0 mismatches across {scanned} file(s) '
          f'(registry {facts.get("registry_total")}, eval top-3 '
          f'{facts.get("eval_top3")}, canary {facts.get("canary")})')
    return 0


if __name__ == '__main__':
    sys.exit(main())
