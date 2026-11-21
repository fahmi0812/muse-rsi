#!/usr/bin/env python3
"""run_budget.py — tiny step budget for one RSI task (RunBudget, Fase 4).

A task gets a step budget up front; the loop checks the budget before
each step and stops when it is exhausted instead of drifting. State lives
in one JSON file under ~/.muse-rsi/ (per-agent runtime data, not repo
content) so a crashed run can resume against the same budget.

Usage:
  python3 scripts/run_budget.py start --task T --budget N [--file PATH]
  python3 scripts/run_budget.py spend --steps N [--file PATH]
  python3 scripts/run_budget.py check [--file PATH]   # exit 1 when exhausted
"""
import argparse
import datetime
import json
import pathlib
import sys

DEFAULT_FILE = pathlib.Path.home() / '.muse-rsi' / 'budget.json'


def _load(path):
    if not path.exists():
        print(f'error: no budget file at {path}; run `start` first', file=sys.stderr)
        return None
    return json.loads(path.read_text(encoding='utf-8'))


def _save(path, state):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2), encoding='utf-8')


def _remaining(state):
    return state['budget'] - state['spent']


def cmd_start(args):
    path = pathlib.Path(args.file) if args.file else DEFAULT_FILE
    if path.exists():
        old = _load(path)
        if old and old.get('status') == 'active' and _remaining(old) > 0:
            print(f"warning: replacing active budget for '{old['task']}' "
                  f"({_remaining(old)} steps left)", file=sys.stderr)
    state = {
        'task': args.task,
        'budget': args.budget,
        'spent': 0,
        'started_at': datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds'),
        'status': 'active',
    }
    _save(path, state)
    print(f"budget started: '{args.task}' — {args.budget} steps")
    return 0


def cmd_spend(args):
    path = pathlib.Path(args.file) if args.file else DEFAULT_FILE
    state = _load(path)
    if state is None:
        return 2
    state['spent'] += args.steps
    if _remaining(state) <= 0:
        state['status'] = 'exhausted'
    _save(path, state)
    print(f"spent {args.steps} step(s); remaining: {_remaining(state)} of {state['budget']}")
    return 0


def cmd_check(args):
    path = pathlib.Path(args.file) if args.file else DEFAULT_FILE
    state = _load(path)
    if state is None:
        return 2
    left = _remaining(state)
    print(f"budget: '{state['task']}' — spent {state['spent']} of {state['budget']}, "
          f"remaining {left} ({state['status']})")
    if left <= 0:
        print('BUDGET EXHAUSTED — stop, snapshot, log the decision, escalate to the user.',
              file=sys.stderr)
        return 1
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    sub = ap.add_subparsers(dest='command', required=True)

    p_start = sub.add_parser('start', help='start a step budget for a task')
    p_start.add_argument('--task', required=True)
    p_start.add_argument('--budget', type=int, required=True)
    p_start.add_argument('--file', default=None)
    p_start.set_defaults(func=cmd_start)

    p_spend = sub.add_parser('spend', help='record steps spent')
    p_spend.add_argument('--steps', type=int, required=True)
    p_spend.add_argument('--file', default=None)
    p_spend.set_defaults(func=cmd_spend)

    p_check = sub.add_parser('check', help='print remaining budget; exit 1 when exhausted')
    p_check.add_argument('--file', default=None)
    p_check.set_defaults(func=cmd_check)

    args = ap.parse_args()
    return args.func(args)


if __name__ == '__main__':
    sys.exit(main())
