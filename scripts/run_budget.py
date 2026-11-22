#!/usr/bin/env python3
"""run_budget.py v2 — enforced step/time/cost budget for one RSI cycle (v3.0 G1, M-06).

v1 only counted steps, `spend` always exited 0, `start` silently replaced
an active budget, and nothing ever called it. v2 enforces the limits in
config/limits.yaml (Bab 4.2) across five dimensions — steps, wall-clock
minutes, cost in USD, files changed, diff lines, retries — and is meant
to be called by the Loop Engine before and after every step, not by the
model on its own initiative.

  start  — begin a budget. REFUSES to overwrite an active budget
           (exit 3); use --force only when the previous cycle is known dead.
           A finished (done/exhausted) budget may be replaced.
  spend  — record consumption: --steps, --files, --lines, --cost, --retries.
           Exit 1 (and mark the budget exhausted) the moment ANY dimension
           is over its limit — including wall-clock time since start and
           any cost above the $0 cap.
  check  — print remaining budget per dimension; exit 1 when exhausted.
  close  — mark the budget done (cycle finished inside its limits).
  show   — print the raw state JSON.

State lives in one JSON file (default ~/.muse-rsi/budget.json, per-agent
runtime data, not repo content) so a crashed run resumes against the
same budget. Exit codes: 0 ok, 1 exhausted, 2 no budget file, 3 refused
to overwrite an active budget.

Usage:
  python3 scripts/run_budget.py start --task T [--budget N] [--file PATH] [--limits PATH]
  python3 scripts/run_budget.py spend [--steps N] [--files N] [--lines N] [--cost X] [--retries N] [--file PATH]
  python3 scripts/run_budget.py check [--file PATH]
  python3 scripts/run_budget.py close [--file PATH]
  python3 scripts/run_budget.py show [--file PATH]
"""
import argparse
import datetime
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
DEFAULT_FILE = pathlib.Path.home() / '.muse-rsi' / 'budget.json'
DEFAULT_LIMITS = HERE.parent / 'config' / 'limits.yaml'

DIMENSIONS = ('steps', 'minutes', 'cost_usd', 'files_changed', 'diff_lines',
              'retries')
LIMIT_KEYS = {
    'steps': 'max_steps',
    'minutes': 'max_minutes',
    'cost_usd': 'max_cost_usd',
    'files_changed': 'max_files_changed',
    'diff_lines': 'max_diff_lines',
    'retries': 'max_retries',
}


def load_limits(path):
    """Minimal YAML reader for the flat `cycle:` block in limits.yaml.

    No PyYAML dependency: the file is six `key: value` lines under one
    section header. Every expected key must be present, or the budget
    refuses to start rather than silently running unlimited.
    """
    path = pathlib.Path(path)
    if not path.exists():
        raise SystemExit(f'error: limits file not found: {path}')
    limits = {}
    in_cycle = False
    for raw in path.read_text(encoding='utf-8').splitlines():
        line = raw.strip()
        if not line or line.startswith('#'):
            continue
        if not line.startswith((' ', '\t')) and line.endswith(':'):
            in_cycle = (line[:-1] == 'cycle')
            continue
        if in_cycle and ':' in line:
            key, _, value = line.partition(':')
            key, value = key.strip(), value.strip()
            try:
                limits[key] = float(value) if '.' in value else int(value)
            except ValueError:
                raise SystemExit(f'error: bad value in {path}: {line!r}')
    missing = [k for k in LIMIT_KEYS.values() if k not in limits]
    if missing:
        raise SystemExit(f'error: {path} is missing limits: {missing}')
    return {dim: limits[LIMIT_KEYS[dim]] for dim in DIMENSIONS}


def _load(path):
    if not path.exists():
        print(f'error: no budget file at {path}; run `start` first',
              file=sys.stderr)
        return None
    return json.loads(path.read_text(encoding='utf-8'))


def _save(path, state):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2), encoding='utf-8')


def _elapsed_minutes(state):
    started = datetime.datetime.fromisoformat(state['started_at'])
    now = datetime.datetime.now(datetime.timezone.utc)
    return (now - started).total_seconds() / 60.0


def _spent(state, dim):
    if dim == 'minutes':
        return _elapsed_minutes(state)
    return state['spent'][dim]


def _remaining(state, dim):
    return state['limits'][dim] - _spent(state, dim)


def _check_exhausted(state):
    """A dimension is exhausted when its remaining budget goes BELOW zero:
    a budget of 40 steps allows exactly 40 — the 41st spend fails (G1 exit
    gate). Cost is the same rule in practice: any spend above a $0 cap
    makes the remainder negative. Returns exhausted dimensions."""
    bad = []
    for dim in DIMENSIONS:
        if _remaining(state, dim) < 0:
            bad.append(dim)
    return bad


def _describe(state):
    parts = []
    for dim in DIMENSIONS:
        spent = _spent(state, dim)
        if dim == 'minutes':
            parts.append(f'{dim}: {spent:.1f}/{state["limits"][dim]}')
        elif dim == 'cost_usd':
            parts.append(f'{dim}: ${spent:.2f}/${state["limits"][dim]:.2f}')
        else:
            parts.append(f'{dim}: {spent}/{state["limits"][dim]}')
    return ', '.join(parts)


def cmd_start(args):
    path = pathlib.Path(args.file) if args.file else DEFAULT_FILE
    limits_path = pathlib.Path(args.limits) if args.limits else DEFAULT_LIMITS
    limits = load_limits(limits_path)
    if args.budget is not None:
        limits['steps'] = args.budget
    if path.exists():
        old = _load(path)
        if old and old.get('status') == 'active' and not args.force:
            print(f"error: refusing to overwrite active budget for "
                  f"'{old['task']}' ({_describe(old)}). "
                  f"Close it first (`close`), or pass --force if the "
                  f"cycle is known dead.", file=sys.stderr)
            return 3
    state = {
        'version': 2,
        'task': args.task,
        'status': 'active',
        'started_at': datetime.datetime.now(datetime.timezone.utc)
                      .isoformat(timespec='seconds'),
        'ended_at': None,
        'limits': limits,
        'spent': {dim: 0 for dim in DIMENSIONS if dim != 'minutes'},
    }
    _save(path, state)
    print(f"budget started: '{args.task}' — {_describe(state)}")
    return 0


def cmd_spend(args):
    path = pathlib.Path(args.file) if args.file else DEFAULT_FILE
    state = _load(path)
    if state is None:
        return 2
    if state['status'] == 'exhausted':
        print(f"BUDGET EXHAUSTED — '{state['task']}' is already over "
              f"({_describe(state)}). Stop, snapshot, log the decision, "
              f"escalate to the user.", file=sys.stderr)
        return 1
    if state['status'] != 'active':
        print(f"error: budget for '{state['task']}' is {state['status']}, "
              f"not active; start a new one first", file=sys.stderr)
        return 2
    state['spent']['steps'] += args.steps
    state['spent']['files_changed'] += args.files
    state['spent']['diff_lines'] += args.lines
    state['spent']['cost_usd'] += args.cost
    state['spent']['retries'] += args.retries
    bad = _check_exhausted(state)
    if bad:
        state['status'] = 'exhausted'
        state['ended_at'] = datetime.datetime.now(datetime.timezone.utc) \
            .isoformat(timespec='seconds')
        _save(path, state)
        print(f"BUDGET EXHAUSTED ({', '.join(bad)}) — {_describe(state)}. "
              f"Stop, snapshot, log the decision, escalate to the user.",
              file=sys.stderr)
        return 1
    _save(path, state)
    print(f"spent: {_describe(state)}")
    return 0


def cmd_check(args):
    path = pathlib.Path(args.file) if args.file else DEFAULT_FILE
    state = _load(path)
    if state is None:
        return 2
    print(f"budget: '{state['task']}' ({state['status']}) — {_describe(state)}")
    bad = _check_exhausted(state)
    if state['status'] == 'active' and bad:
        state['status'] = 'exhausted'
        state['ended_at'] = datetime.datetime.now(datetime.timezone.utc) \
            .isoformat(timespec='seconds')
        _save(path, state)
    if bad:
        print(f"BUDGET EXHAUSTED ({', '.join(bad)}) — stop, snapshot, "
              f"log the decision, escalate to the user.", file=sys.stderr)
        return 1
    return 0


def cmd_close(args):
    path = pathlib.Path(args.file) if args.file else DEFAULT_FILE
    state = _load(path)
    if state is None:
        return 2
    if state['status'] == 'exhausted':
        print(f"budget for '{state['task']}' is already exhausted; "
              f"not marking done", file=sys.stderr)
        return 1
    state['status'] = 'done'
    state['ended_at'] = datetime.datetime.now(datetime.timezone.utc) \
        .isoformat(timespec='seconds')
    _save(path, state)
    print(f"budget closed: '{state['task']}' — {_describe(state)}")
    return 0


def cmd_show(args):
    path = pathlib.Path(args.file) if args.file else DEFAULT_FILE
    state = _load(path)
    if state is None:
        return 2
    print(json.dumps(state, indent=2))
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    sub = ap.add_subparsers(dest='command', required=True)

    p_start = sub.add_parser('start', help='start a budget for a task')
    p_start.add_argument('--task', required=True)
    p_start.add_argument('--budget', type=int, default=None,
                         help='override max_steps from limits.yaml')
    p_start.add_argument('--file', default=None)
    p_start.add_argument('--limits', default=None)
    p_start.add_argument('--force', action='store_true',
                         help='overwrite even an active budget')
    p_start.set_defaults(func=cmd_start)

    p_spend = sub.add_parser('spend', help='record consumption; exit 1 when exhausted')
    p_spend.add_argument('--steps', type=int, default=0)
    p_spend.add_argument('--files', type=int, default=0)
    p_spend.add_argument('--lines', type=int, default=0)
    p_spend.add_argument('--cost', type=float, default=0.0)
    p_spend.add_argument('--retries', type=int, default=0)
    p_spend.add_argument('--file', default=None)
    p_spend.set_defaults(func=cmd_spend)

    p_check = sub.add_parser('check', help='print remaining budget; exit 1 when exhausted')
    p_check.add_argument('--file', default=None)
    p_check.set_defaults(func=cmd_check)

    p_close = sub.add_parser('close', help='mark the budget done')
    p_close.add_argument('--file', default=None)
    p_close.set_defaults(func=cmd_close)

    p_show = sub.add_parser('show', help='print the budget state JSON')
    p_show.add_argument('--file', default=None)
    p_show.set_defaults(func=cmd_show)

    args = ap.parse_args()
    return args.func(args)


if __name__ == '__main__':
    sys.exit(main())
