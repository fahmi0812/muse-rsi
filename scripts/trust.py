#!/usr/bin/env python3
"""trust.py — Trust Ladder A0–A5 (Bab 4.5).

Permission is per action class. This script is the reader/enforcer of
config/trust.yaml; the Loop Engine asks it before acting. The evidence
ledger lives in ~/.muse-rsi/trust_ledger.json (per-agent runtime data,
never committed, never edited by the loop itself):

  {"A2": {"accepted_prs": 0, "reverts": 0, "corrections": 0,
          "canary_trips": 0, "demoted_until": null, ...}, ...}

Promotion (A2 -> auto-merge): 10 consecutive accepted PRs without a
revert, over >= 14 days, T1 green, T2 calibration >= 90%.
Demotion (any class): 1 revert after merge / 1 Fahmi correction /
canary tripped -> back to Fahmi-merge for 14 days (A2), or back to
approval-only (A3). Demotion is automatic and immediate; promotion is
earned and only recorded here, never self-granted by the loop.

Usage:
  python3 scripts/trust.py status [--config PATH] [--ledger PATH]
  python3 scripts/trust.py check <action_class> [--config PATH] [--ledger PATH]
      # exit 0 = allowed (prints mode), 1 = needs Fahmi / not allowed
  python3 scripts/trust.py record --class A2 --event accepted_pr|revert_after_merge|
      fahmi_correction|canary_tripped|snapshot_restore_failed [--ledger PATH]
"""
import argparse
import datetime
import json
import pathlib
import sys

try:
    import yaml
except ImportError:  # pragma: no cover - PyYAML is on the VM.
    yaml = None

CLASSES = ['A0', 'A1', 'A2', 'A3', 'A4', 'A5']
DEMOTE_EVENTS = {'revert_after_merge', 'fahmi_correction', 'canary_tripped',
                 'snapshot_restore_failed'}


def _default_config_path():
    return pathlib.Path(__file__).resolve().parent.parent / 'config' / 'trust.yaml'


def _default_ledger_path():
    import os
    home = pathlib.Path(os.environ.get('MUSE_RSI_HOME',
                                       str(pathlib.Path.home() / '.muse-rsi')))
    return home / 'trust_ledger.json'


def _load_config(path):
    if yaml is None:
        raise RuntimeError('PyYAML is required to read trust.yaml')
    return yaml.safe_load(pathlib.Path(path).read_text(encoding='utf-8')) or {}


def _load_ledger(path):
    path = pathlib.Path(path)
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding='utf-8')) or {}


def _save_ledger(path, data):
    path = pathlib.Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding='utf-8')


def _demoted_until(ledger_entry):
    raw = (ledger_entry or {}).get('demoted_until')
    if not raw:
        return None
    try:
        return datetime.datetime.fromisoformat(raw)
    except ValueError:
        return None


def effective_mode(cfg, ledger, cls):
    """Current mode for a class, honouring an active demotion."""
    entry = ledger.get(cls, {})
    until = _demoted_until(entry)
    if until and datetime.datetime.now(datetime.timezone.utc) < until.replace(
            tzinfo=datetime.timezone.utc):
        return entry.get('demoted_mode', 'pr_then_fahmi_merge'), f'demoted until {until.date()}'
    return cfg.get('current', {}).get(cls, 'unknown'), ''


def cmd_status(args):
    cfg = _load_config(args.config)
    ledger = _load_ledger(args.ledger)
    print(f"Trust Ladder (config: {args.config})")
    for cls in CLASSES:
        spec = cfg.get('classes', {}).get(cls, {})
        mode, why = effective_mode(cfg, ledger, cls)
        entry = ledger.get(cls, {})
        print(f"  {cls} {spec.get('name', '')}: mode={mode}"
              + (f' ({why})' if why else '')
              + f" | accepted_prs={entry.get('accepted_prs', 0)}"
              f" reverts={entry.get('reverts', 0)}"
              f" corrections={entry.get('corrections', 0)}"
              f" canary_trips={entry.get('canary_trips', 0)}")
    return 0


def cmd_check(args):
    cls = args.action_class.upper()
    if cls not in CLASSES:
        print(f'error: unknown action class {cls} (A0..A5)', file=sys.stderr)
        return 2
    cfg = _load_config(args.config)
    ledger = _load_ledger(args.ledger)
    mode, why = effective_mode(cfg, ledger, cls)
    if mode in ('automatic', 'auto_merge'):
        print(f'{cls}: ALLOWED ({mode})' + (f' — {why}' if why else ''))
        return 0
    print(f'{cls}: NEEDS FAHMI ({mode})' + (f' — {why}' if why else ''))
    return 1


def cmd_record(args):
    cls = args.action_class.upper()
    if cls not in CLASSES:
        print(f'error: unknown action class {cls}', file=sys.stderr)
        return 2
    ledger = _load_ledger(args.ledger)
    entry = ledger.setdefault(cls, {'accepted_prs': 0, 'reverts': 0,
                                    'corrections': 0, 'canary_trips': 0,
                                    'demoted_until': None, 'demoted_mode': None,
                                    'first_accepted_at': None})
    ev = args.event
    now = datetime.datetime.now(datetime.timezone.utc)
    if ev == 'accepted_pr':
        entry['accepted_prs'] = entry.get('accepted_prs', 0) + 1
        entry.setdefault('first_accepted_at', now.isoformat(timespec='seconds'))
        # Promotion check for A2 (Bab 4.5): 10 PRs, >=14 days.
        if cls == 'A2':
            first = entry.get('first_accepted_at')
            days = 0
            if first:
                try:
                    days = (now - datetime.datetime.fromisoformat(first)
                            .replace(tzinfo=datetime.timezone.utc)).days
                except ValueError:
                    days = 0
            if entry['accepted_prs'] >= 10 and days >= 14:
                print(f'A2 promotion criteria met ({entry["accepted_prs"]} PRs, '
                      f'{days} days) — auto-merge is EARNED; record it in '
                      f'trust.yaml via a Fahmi-approved change, never here.')
    elif ev in DEMOTE_EVENTS:
        key = {'revert_after_merge': 'reverts', 'fahmi_correction': 'corrections',
               'canary_tripped': 'canary_trips',
               'snapshot_restore_failed': 'snapshot_failures'}.get(ev)
        entry[key] = entry.get(key, 0) + 1
        if cls == 'A2':
            entry['accepted_prs'] = 0  # consecutive streak resets
            entry['demoted_until'] = (now + datetime.timedelta(days=14)).isoformat(
                timespec='seconds')
            entry['demoted_mode'] = 'pr_then_fahmi_merge'
            print(f'A2 DEMOTED: {ev} -> Fahmi merge for 14 days '
                  f"(until {entry['demoted_until'][:10]})")
        elif cls == 'A3':
            entry['demoted_until'] = (now + datetime.timedelta(days=14)).isoformat(
                timespec='seconds')
            entry['demoted_mode'] = 'staging_plus_t2_then_fahmi_digest'
            print(f'A3 DEMOTED: {ev} -> back to approval for 14 days')
        else:
            print(f'{cls}: demotion event recorded ({ev}); mode unchanged '
                  f'({cls} has no auto mode to lose)')
    else:
        print(f'error: unknown event {ev}', file=sys.stderr)
        return 2
    _save_ledger(args.ledger, ledger)
    print(f'ledger updated: {args.ledger}')
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--config', default=str(_default_config_path()))
    ap.add_argument('--ledger', default=str(_default_ledger_path()))
    sub = ap.add_subparsers(dest='command', required=True)

    # --config/--ledger are also accepted AFTER the subcommand (SUPPRESS
    # so a value given before the subcommand is never overwritten).
    def _add_common(p):
        p.add_argument('--config', default=argparse.SUPPRESS)
        p.add_argument('--ledger', default=argparse.SUPPRESS)

    p = sub.add_parser('status', help='show the ladder and ledger counters')
    _add_common(p)
    p.set_defaults(func=cmd_status)

    p = sub.add_parser('check', help='is this action class allowed now?')
    p.add_argument('action_class')
    _add_common(p)
    p.set_defaults(func=cmd_check)

    p = sub.add_parser('record', help='record a promotion/demotion event')
    p.add_argument('--class', dest='action_class', required=True)
    p.add_argument('--event', required=True,
                   choices=['accepted_pr', 'revert_after_merge',
                            'fahmi_correction', 'canary_tripped',
                            'snapshot_restore_failed'])
    _add_common(p)
    p.set_defaults(func=cmd_record)

    args = ap.parse_args()
    return args.func(args)


if __name__ == '__main__':
    sys.exit(main())
