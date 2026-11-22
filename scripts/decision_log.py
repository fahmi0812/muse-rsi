#!/usr/bin/env python3
"""decision_log.py — decision.tsv v2 for the muse-rsi Loop Engine (v3.0 G1).

One row per RSI cycle (not per ad-hoc decision). Schema v2 (Bab 4.8):

  run_id, started_at, ended_at, state_reached, axis_target, hypothesis,
  action_class, critique_tier, checker_cmd, commit_before, commit_after,
  C_before, C_after, K_before, K_after, eval_manifest_sha256,
  heldout_score, critic_verdicts, outcome, budget_steps, budget_minutes,
  budget_usd, note

  outcome: accepted | reverted | escalated | empty | halted
  A green cycle = outcome accepted or empty + T1 green + no HALT.
  The "3 consecutive green cycles" gate is computed from this file.

Files are per-agent runtime data, NOT repo content — never commit them:
  ~/.muse-rsi/decision.tsv   — one row per cycle (v2 header)
  ~/.muse-rsi/usage.tsv      — per-run usage (unchanged from v1)

Back-compat: `report` reads both v1 files (old 8-column header) and v2
files. New rows are always written with the v2 header. A v1 file is never
rewritten in place — `migrate` writes a new v2 file next to it instead
(old columns map to the closest v2 fields, the rest stay empty).

Usage:
  python3 scripts/decision_log.py cycle --run-id R --started-at ISO
      [--ended-at ISO] [--state-reached VERIFY] [--axis-target C|K]
      [--hypothesis H] [--action-class A0..A5] [--critique-tier T0..T4]
      [--checker-cmd CMD] [--commit-before SHA] [--commit-after SHA]
      [--C-before X] [--C-after X] [--K-before X] [--K-after X]
      [--eval-manifest-sha256 HEX] [--heldout-score S]
      [--critic-verdicts V] [--outcome accepted|reverted|escalated|empty|halted]
      [--budget-steps N] [--budget-minutes N] [--budget-usd 0] [--note N]
      [--file PATH]
  python3 scripts/decision_log.py report [--file PATH] [--n N]
  python3 scripts/decision_log.py green-streak [--file PATH]
  python3 scripts/decision_log.py migrate --file PATH [--out PATH]
  python3 scripts/decision_log.py usage --task T ...   (v1, unchanged)
  python3 scripts/decision_log.py log --task T ...     (v1, deprecated;
      kept so old callers do not break; writes to a legacy file only)
"""
import argparse
import datetime
import pathlib
import sys

DEFAULT_DIR = pathlib.Path.home() / '.muse-rsi'

# v2 schema — one row per cycle.
COLUMNS_V2 = [
    'run_id', 'started_at', 'ended_at', 'state_reached', 'axis_target',
    'hypothesis', 'action_class', 'critique_tier', 'checker_cmd',
    'commit_before', 'commit_after', 'C_before', 'C_after', 'K_before',
    'K_after', 'eval_manifest_sha256', 'heldout_score', 'critic_verdicts',
    'outcome', 'budget_steps', 'budget_minutes', 'budget_usd', 'note',
]
OUTCOMES_V2 = {'accepted', 'reverted', 'escalated', 'empty', 'halted'}
ACTION_CLASSES = {'A0', 'A1', 'A2', 'A3', 'A4', 'A5', ''}
CRITIQUE_TIERS = {'T0', 'T1', 'T2', 'T3', 'T4', ''}
AXES = {'C', 'K', ''}

# v1 schema — kept for reading old files only.
COLUMNS_V1 = [
    'timestamp', 'task', 'decision', 'options_considered', 'evidence',
    'outcome', 'confidence', 'reversible',
]
USAGE_COLUMNS = ['timestamp', 'task', 'router_top3', 'result', 'notes']
OUTCOMES_V1 = {'pending', 'succeeded', 'failed', 'rolled-back'}


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


def _read_rows(path):
    """Read a decision.tsv (v1 or v2) -> (columns, [row-dict, ...])."""
    if not path.exists():
        return None, []
    lines = [l for l in path.read_text(encoding='utf-8').splitlines() if l.strip()]
    if not lines:
        return None, []
    columns = lines[0].split('\t')
    rows = []
    for line in lines[1:]:
        cells = line.split('\t')
        cells += [''] * (len(columns) - len(cells))
        rows.append(dict(zip(columns, cells)))
    return columns, rows


def _is_v2(columns):
    return columns is not None and columns[:2] == ['run_id', 'started_at']


def cmd_cycle(args):
    """Append one v2 cycle row. Refuses to append to a v1-header file."""
    if args.outcome not in OUTCOMES_V2:
        print(f'error: --outcome must be one of {sorted(OUTCOMES_V2)}', file=sys.stderr)
        return 2
    if args.action_class not in ACTION_CLASSES:
        print(f'error: --action-class must be one of A0..A5', file=sys.stderr)
        return 2
    if args.critique_tier not in CRITIQUE_TIERS:
        print(f'error: --critique-tier must be one of T0..T4', file=sys.stderr)
        return 2
    if args.axis_target not in AXES:
        print(f'error: --axis-target must be C or K', file=sys.stderr)
        return 2
    path = pathlib.Path(args.file) if args.file else DEFAULT_DIR / 'decision.tsv'
    if path.exists() and path.stat().st_size > 0:
        columns, _ = _read_rows(path)
        if not _is_v2(columns):
            print(f'error: {path} has a v1 header — run `migrate` first, '
                  f'never mix schemas in one file', file=sys.stderr)
            return 2
    row = {
        'run_id': args.run_id,
        'started_at': args.started_at or _now(),
        'ended_at': args.ended_at or _now(),
        'state_reached': args.state_reached,
        'axis_target': args.axis_target,
        'hypothesis': args.hypothesis,
        'action_class': args.action_class,
        'critique_tier': args.critique_tier,
        'checker_cmd': args.checker_cmd,
        'commit_before': args.commit_before,
        'commit_after': args.commit_after,
        'C_before': args.C_before,
        'C_after': args.C_after,
        'K_before': args.K_before,
        'K_after': args.K_after,
        'eval_manifest_sha256': args.eval_manifest_sha256,
        'heldout_score': args.heldout_score,
        'critic_verdicts': args.critic_verdicts,
        'outcome': args.outcome,
        'budget_steps': args.budget_steps,
        'budget_minutes': args.budget_minutes,
        'budget_usd': args.budget_usd,
        'note': args.note,
    }
    _append(path, COLUMNS_V2, row)
    print(f'logged cycle {args.run_id} ({args.outcome}) to {path}')
    return 0


def cmd_report(args):
    path = pathlib.Path(args.file) if args.file else DEFAULT_DIR / 'decision.tsv'
    columns, rows = _read_rows(path)
    if columns is None:
        print('no decisions logged yet')
        return 0
    schema = 'v2' if _is_v2(columns) else 'v1 (legacy)'
    print(f'decision log: {path}  schema={schema}  rows={len(rows)}')
    counts = {}
    for r in rows:
        counts[r.get('outcome', '?')] = counts.get(r.get('outcome', '?'), 0) + 1
    for outcome in sorted(counts):
        print(f'  {outcome}: {counts[outcome]}')
    bad = [r for r in rows if r.get('outcome') in ('failed', 'rolled-back',
                                                   'reverted', 'halted', 'escalated')]
    if bad:
        print(f'recent problem rows ({min(args.n, len(bad))} of {len(bad)}):')
        for r in bad[-args.n:]:
            key = r.get('run_id') or r.get('timestamp', '?')
            print(f"  {key} | {r.get('outcome', '?')} | "
                  f"{(r.get('note') or r.get('decision') or '')[:70]}")
    return 0


def cmd_green_streak(args):
    """Count consecutive green cycles from the tail (accepted|empty)."""
    path = pathlib.Path(args.file) if args.file else DEFAULT_DIR / 'decision.tsv'
    columns, rows = _read_rows(path)
    if columns is None or not _is_v2(columns):
        print('green streak: 0 (no v2 decision log yet)')
        return 0
    streak = 0
    for r in reversed(rows):
        if r.get('outcome') in ('accepted', 'empty'):
            streak += 1
        else:
            break
    print(f'green streak: {streak} consecutive green cycle(s) '
          f'({"PASS" if streak >= 3 else "need 3 for the G1 gate"})')
    return 0 if streak >= 3 else 1


def cmd_migrate(args):
    """Write a v2 copy of a v1 file next to it; never rewrites the original."""
    src = pathlib.Path(args.file)
    columns, rows = _read_rows(src)
    if columns is None:
        print(f'error: no file at {src}', file=sys.stderr)
        return 2
    if _is_v2(columns):
        print(f'{src} is already v2 — nothing to migrate')
        return 0
    out = pathlib.Path(args.out) if args.out else src.with_name(src.stem + '.v2.tsv')
    if out.exists():
        print(f'error: {out} already exists — refusing to overwrite', file=sys.stderr)
        return 2
    with out.open('w', encoding='utf-8') as f:
        f.write('\t'.join(COLUMNS_V2) + '\n')
        for r in rows:
            v2 = {
                'run_id': '',
                'started_at': r.get('timestamp', ''),
                'ended_at': r.get('timestamp', ''),
                'state_reached': '',
                'axis_target': '',
                'hypothesis': r.get('task', ''),
                'action_class': '',
                'critique_tier': '',
                'checker_cmd': '',
                'commit_before': '',
                'commit_after': '',
                'C_before': '', 'C_after': '', 'K_before': '', 'K_after': '',
                'eval_manifest_sha256': '',
                'heldout_score': '',
                'critic_verdicts': '',
                'outcome': {'succeeded': 'accepted', 'failed': 'reverted',
                            'rolled-back': 'reverted',
                            'pending': 'escalated'}.get(r.get('outcome', ''), ''),
                'budget_steps': '', 'budget_minutes': '', 'budget_usd': '',
                'note': f"migrated from v1: decision={r.get('decision', '')} "
                        f"evidence={r.get('evidence', '')} "
                        f"confidence={r.get('confidence', '')}",
            }
            f.write('\t'.join(_clean(v2.get(c, '')) for c in COLUMNS_V2) + '\n')
    print(f'migrated {len(rows)} row(s): {src} -> {out} (original untouched)')
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


def cmd_log(args):
    """v1 `log` — deprecated. Writes to a legacy file, never to decision.tsv v2."""
    print('warning: `log` is the v1 API and is deprecated; use `cycle` for '
          'Loop Engine rows. Writing to legacy-decision.tsv instead of '
          'decision.tsv so the v2 schema is never mixed.', file=sys.stderr)
    if args.outcome not in OUTCOMES_V1:
        print(f'error: --outcome must be one of {sorted(OUTCOMES_V1)}', file=sys.stderr)
        return 2
    path = pathlib.Path(args.file) if args.file else DEFAULT_DIR / 'legacy-decision.tsv'
    _append(path, COLUMNS_V1, {
        'timestamp': _now(),
        'task': args.task,
        'decision': args.decision,
        'options_considered': args.options,
        'evidence': args.evidence,
        'outcome': args.outcome,
        'confidence': args.confidence,
        'reversible': args.reversible,
    })
    print(f'logged legacy decision to {path}')
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    sub = ap.add_subparsers(dest='command', required=True)

    p = sub.add_parser('cycle', help='append one v2 cycle row')
    p.add_argument('--run-id', required=True)
    p.add_argument('--started-at', default='')
    p.add_argument('--ended-at', default='')
    p.add_argument('--state-reached', default='')
    p.add_argument('--axis-target', default='', choices=['C', 'K', ''])
    p.add_argument('--hypothesis', default='')
    p.add_argument('--action-class', default='', choices=['A0', 'A1', 'A2', 'A3', 'A4', 'A5', ''])
    p.add_argument('--critique-tier', default='', choices=['T0', 'T1', 'T2', 'T3', 'T4', ''])
    p.add_argument('--checker-cmd', default='')
    p.add_argument('--commit-before', default='')
    p.add_argument('--commit-after', default='')
    p.add_argument('--C-before', default='')
    p.add_argument('--C-after', default='')
    p.add_argument('--K-before', default='')
    p.add_argument('--K-after', default='')
    p.add_argument('--eval-manifest-sha256', default='')
    p.add_argument('--heldout-score', default='')
    p.add_argument('--critic-verdicts', default='')
    p.add_argument('--outcome', default='empty',
                   choices=sorted(OUTCOMES_V2))
    p.add_argument('--budget-steps', default='')
    p.add_argument('--budget-minutes', default='')
    p.add_argument('--budget-usd', default='0')
    p.add_argument('--note', default='')
    p.add_argument('--file', default=None)
    p.set_defaults(func=cmd_cycle)

    p = sub.add_parser('report', help='summarise the decision log (v1 or v2)')
    p.add_argument('--file', default=None)
    p.add_argument('--n', type=int, default=5)
    p.set_defaults(func=cmd_report)

    p = sub.add_parser('green-streak', help='consecutive green cycles (exit 0 iff >=3)')
    p.add_argument('--file', default=None)
    p.set_defaults(func=cmd_green_streak)

    p = sub.add_parser('migrate', help='write a v2 copy of a v1 file')
    p.add_argument('--file', required=True)
    p.add_argument('--out', default=None)
    p.set_defaults(func=cmd_migrate)

    p = sub.add_parser('usage', help='append one usage row (v1, unchanged)')
    p.add_argument('--task', required=True)
    p.add_argument('--router-top3', default='')
    p.add_argument('--result', default='')
    p.add_argument('--notes', default='')
    p.add_argument('--file', default=None)
    p.set_defaults(func=cmd_usage)

    p = sub.add_parser('log', help='DEPRECATED v1 decision log')
    p.add_argument('--task', required=True)
    p.add_argument('--decision', required=True)
    p.add_argument('--options', default='')
    p.add_argument('--evidence', default='')
    p.add_argument('--outcome', default='pending', choices=sorted(OUTCOMES_V1))
    p.add_argument('--confidence', default='')
    p.add_argument('--reversible', default='yes', choices=['yes', 'no'])
    p.add_argument('--file', default=None)
    p.set_defaults(func=cmd_log)

    args = ap.parse_args()
    return args.func(args)


if __name__ == '__main__':
    sys.exit(main())
