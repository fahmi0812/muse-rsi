#!/usr/bin/env python3
"""decision_log.py — append-only decision + usage log for the muse-rsi RSI loop.

Replaces the manual usage_log.py habit (a separate manual step that got
skipped): every decision the loop makes is logged in one place, and usage
is logged with the same tool. The rsi-loop skill calls this at its
decision points instead of usage_log.py.

Files are per-agent runtime data, NOT repo content — never commit them:
  ~/.muse-rsi/decision.tsv   — decisions (one row per decision)
  ~/.muse-rsi/usage.tsv      — per-run usage

decision.tsv columns (tab-separated, header row first):
  timestamp (UTC ISO) | task | decision | options_considered (|-separated)
  | evidence (short) | outcome (pending/succeeded/failed/rolled-back)
  | confidence (0-1 or low/med/high) | reversible (yes/no)

usage.tsv columns:
  timestamp | task | router_top3 (|-separated "name:score") | result | notes

The script only ever appends. It never rewrites history: no edit, no
delete, no dedup. Fields are sanitised (tabs/newlines become spaces) so
one decision is always exactly one row.

Usage:
  python3 scripts/decision_log.py log --task T --decision D
      [--options "a|b"] [--evidence E] [--outcome pending|succeeded|failed|rolled-back]
      [--confidence 0.8] [--reversible yes|no] [--file PATH]
  python3 scripts/decision_log.py report [--file PATH] [--n N]
  python3 scripts/decision_log.py usage --task T [--router-top3 "a:29.3|b:12.1"]
      [--result ok|fail] [--notes N] [--file PATH]
"""
import argparse
import datetime
import pathlib
import sys

DEFAULT_DIR = pathlib.Path.home() / '.muse-rsi'
DECISION_COLUMNS = [
    'timestamp', 'task', 'decision', 'options_considered', 'evidence',
    'outcome', 'confidence', 'reversible',
]
USAGE_COLUMNS = ['timestamp', 'task', 'router_top3', 'result', 'notes']
OUTCOMES = {'pending', 'succeeded', 'failed', 'rolled-back'}


def _clean(value):
    """One TSV row must stay one line: strip tabs, newlines, carriage returns."""
    return str(value or '').replace('\t', ' ').replace('\n', ' ').replace('\r', ' ').strip()


def _now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')


def _append(path, columns, row):
    path.parent.mkdir(parents=True, exist_ok=True)
    write_header = not path.exists() or path.stat().st_size == 0
    with path.open('a', encoding='utf-8') as f:
        if write_header:
            f.write('\t'.join(columns) + '\n')
        f.write('\t'.join(_clean(row.get(c, '')) for c in columns) + '\n')
    return path


def cmd_log(args):
    outcome = args.outcome
    if outcome not in OUTCOMES:
        print(f'error: --outcome must be one of {sorted(OUTCOMES)}', file=sys.stderr)
        return 2
    path = pathlib.Path(args.file) if args.file else DEFAULT_DIR / 'decision.tsv'
    _append(path, DECISION_COLUMNS, {
        'timestamp': _now(),
        'task': args.task,
        'decision': args.decision,
        'options_considered': args.options,
        'evidence': args.evidence,
        'outcome': outcome,
        'confidence': args.confidence,
        'reversible': args.reversible,
    })
    print(f'logged decision to {path}')
    return 0


def cmd_usage(args):
    path = pathlib.Path(args.file) if args.file else DEFAULT_DIR / 'usage.tsv'
    _append(path, USAGE_COLUMNS, {
        'timestamp': _now(),
        'task': args.task,
        'router_top3': args.router_top3,
        'result': args.result,
        'notes': args.notes,
    })
    print(f'logged usage to {path}')
    return 0


def cmd_report(args):
    path = pathlib.Path(args.file) if args.file else DEFAULT_DIR / 'decision.tsv'
    if not path.exists():
        print('no decisions logged yet')
        return 0
    lines = [l for l in path.read_text(encoding='utf-8').splitlines() if l.strip()]
    rows = [dict(zip(DECISION_COLUMNS, l.split('\t'))) for l in lines[1:]]
    counts = {}
    for r in rows:
        counts[r.get('outcome', '?')] = counts.get(r.get('outcome', '?'), 0) + 1
    print(f'decisions logged: {len(rows)}')
    for outcome in sorted(counts):
        print(f'  {outcome}: {counts[outcome]}')
    bad = [r for r in rows if r.get('outcome') in ('failed', 'rolled-back')]
    if bad:
        print(f'recent failures ({min(args.n, len(bad))} of {len(bad)}):')
        for r in bad[-args.n:]:
            print(f"  {r.get('timestamp', '?')} | {r.get('task', '?')} | "
                  f"{r.get('decision', '?')[:70]}")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    sub = ap.add_subparsers(dest='command', required=True)

    p_log = sub.add_parser('log', help='append one decision')
    p_log.add_argument('--task', required=True)
    p_log.add_argument('--decision', required=True)
    p_log.add_argument('--options', default='')
    p_log.add_argument('--evidence', default='')
    p_log.add_argument('--outcome', default='pending',
                       choices=sorted(OUTCOMES))
    p_log.add_argument('--confidence', default='')
    p_log.add_argument('--reversible', default='yes', choices=['yes', 'no'])
    p_log.add_argument('--file', default=None)
    p_log.set_defaults(func=cmd_log)

    p_usage = sub.add_parser('usage', help='append one usage row')
    p_usage.add_argument('--task', required=True)
    p_usage.add_argument('--router-top3', default='')
    p_usage.add_argument('--result', default='')
    p_usage.add_argument('--notes', default='')
    p_usage.add_argument('--file', default=None)
    p_usage.set_defaults(func=cmd_usage)

    p_report = sub.add_parser('report', help='summarise decisions')
    p_report.add_argument('--file', default=None)
    p_report.add_argument('--n', type=int, default=5)
    p_report.set_defaults(func=cmd_report)

    args = ap.parse_args()
    return args.func(args)


if __name__ == '__main__':
    sys.exit(main())
