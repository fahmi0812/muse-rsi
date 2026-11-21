#!/usr/bin/env python3
"""usage_log.py — the honest usage meter for the muse-rsi harness.

DEPRECATED as the loop's logger: use scripts/decision_log.py instead
(`log` for decisions, `usage` for per-run usage) — same data, one tool,
called at the decision points so it cannot be skipped. This file is kept
working for existing installs (back-compat), but the rsi-loop skill no
longer calls it.

There is no token meter inside this harness, so this log records what IS
measurable: each run's date, duration, context-window usage (read from the
agent's own session status at the end of the run), what it changed, and
whether the checks passed. The RSI loop records one entry per run; the
--report command shows the trend.

Usage:
  python3 scripts/usage_log.py --run-id ID --context-used N --context-remaining M \
      --duration-min N --note "what the run did" [--checks PASS|FAIL]
  python3 scripts/usage_log.py --report
Log file: ~/workspace/tools/usage-log/usage.jsonl (VM-local, not in the repo).
"""
import argparse
import datetime
import json
from zoneinfo import ZoneInfo
import pathlib
import sys

LOG = pathlib.Path.home() / 'workspace' / 'tools' / 'usage-log' / 'usage.jsonl'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--run-id', default=None)
    ap.add_argument('--context-used', type=int, default=None)
    ap.add_argument('--context-remaining', type=int, default=None)
    ap.add_argument('--duration-min', type=float, default=None)
    ap.add_argument('--note', default='')
    ap.add_argument('--checks', choices=['PASS', 'FAIL'], default=None)
    ap.add_argument('--report', action='store_true')
    ap.add_argument('--log', default=str(LOG))
    args = ap.parse_args()
    log = pathlib.Path(args.log)

    if args.report:
        if not log.exists():
            print('no usage entries yet')
            return 0
        rows = [json.loads(l) for l in log.read_text(encoding='utf-8').splitlines() if l.strip()]
        print(f'runs logged: {len(rows)}')
        for r in rows:
            print(f"  {r['date']} | {r.get('run_id', '?')[:8]} | ctx used {r.get('context_used', '?')} / remaining {r.get('context_remaining', '?')} | {r.get('duration_min', '?')} min | checks {r.get('checks', '?')} | {r.get('note', '')[:70]}")
        used = [r['context_used'] for r in rows if isinstance(r.get('context_used'), int)]
        if used:
            print(f'context used: min {min(used)}, max {max(used)}, avg {sum(used) // len(used)} tokens')
        return 0

    if not args.run_id:
        ap.error('--run-id is required when logging (or use --report)')
    entry = {
        'date': datetime.datetime.now(ZoneInfo('Asia/Jakarta')).strftime('%Y-%m-%d %H:%M'),
        'run_id': args.run_id,
        'context_used': args.context_used,
        'context_remaining': args.context_remaining,
        'duration_min': args.duration_min,
        'checks': args.checks,
        'note': args.note,
    }
    log.parent.mkdir(parents=True, exist_ok=True)
    with log.open('a', encoding='utf-8') as f:
        f.write(json.dumps(entry, ensure_ascii=False) + '\n')
    print('logged:', entry['date'], args.run_id[:8], '| ctx used:', args.context_used)
    return 0


if __name__ == '__main__':
    sys.exit(main())
