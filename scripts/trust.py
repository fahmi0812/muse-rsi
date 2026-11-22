#!/usr/bin/env python3
"""trust.py — Trust Ladder A0–A5, v3.1 maximum autonomy (Bab 4.5, docs/autonomy.md).

Permission is per action class (config/trust.yaml). Since v3.1 the
default is autonomy: A0–A3 run and merge without asking, A4 merges after
the veto window, and only A5 (the hard core) needs Fahmi. Nothing has to
be earned first; trust is LOST by incidents and restored by time.

The evidence ledger lives in ~/.muse-rsi/trust_ledger.json (per-agent
runtime data, never committed, never edited by the loop itself):

  {"A2": {"accepted_prs": 0, "reverts": 0, "vetoes": 0, "corrections": 0,
          "canary_trips": 0, "demoted_until": null, "demoted_mode": null,
          "first_accepted_at": "..."}, ...}

Demotion is automatic and immediate: an event listed in the class's
`demote_on` switches it to its `demoted_mode` for `demote_for_days`
(default 7). For A2/A3 that mode is `veto_window`, so even a demoted class
does not start asking for permission; its merges are only delayed.

Modes and `check` exit codes:
  automatic, auto_merge -> 0  allowed now
  veto_window           -> 4  allowed after the veto window
  fahmi_merge, fahmi_only, anything else -> 1  needs Fahmi
  usage error           -> 2

Usage:
  python3 scripts/trust.py status [--config PATH] [--ledger PATH]
  python3 scripts/trust.py check <action_class> [--config PATH] [--ledger PATH]
  python3 scripts/trust.py record --class A2 --event accepted_pr|revert_after_merge|
      veto|fahmi_correction|canary_tripped|snapshot_restore_failed [--ledger PATH]
"""
import argparse
import datetime
import json
import os
import pathlib
import sys

try:
    import yaml
except ImportError:  # pragma: no cover - PyYAML is on the VM.
    yaml = None

CLASSES = ['A0', 'A1', 'A2', 'A3', 'A4', 'A5']
ALLOWED_NOW = {'automatic', 'auto_merge'}
ALLOWED_AFTER_WINDOW = {'veto_window'}
EXIT_ALLOWED, EXIT_NEEDS_FAHMI, EXIT_USAGE, EXIT_AFTER_WINDOW = 0, 1, 2, 4
DEMOTE_EVENTS = {'revert_after_merge': 'reverts', 'veto': 'vetoes',
                 'fahmi_correction': 'corrections', 'canary_tripped': 'canary_trips',
                 'snapshot_restore_failed': 'snapshot_failures'}
EVENTS = ['accepted_pr'] + list(DEMOTE_EVENTS)


def _default_config_path():
    return pathlib.Path(__file__).resolve().parent.parent / 'config' / 'trust.yaml'


def _default_ledger_path():
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


def _now():
    return datetime.datetime.now(datetime.timezone.utc)


def _parse(raw):
    if not raw:
        return None
    try:
        dt = datetime.datetime.fromisoformat(raw)
    except ValueError:
        return None
    return dt if dt.tzinfo else dt.replace(tzinfo=datetime.timezone.utc)


def effective_mode(cfg, ledger, cls):
    """Current mode for a class, honouring an active demotion."""
    entry = ledger.get(cls, {})
    until = _parse(entry.get('demoted_until'))
    if until and _now() < until:
        spec = cfg.get('classes', {}).get(cls, {})
        mode = entry.get('demoted_mode') or spec.get('demoted_mode', 'fahmi_merge')
        return mode, f'demoted until {until.date()}'
    return cfg.get('current', {}).get(cls, 'unknown'), ''


def check_exit(mode):
    if mode in ALLOWED_NOW:
        return EXIT_ALLOWED
    if mode in ALLOWED_AFTER_WINDOW:
        return EXIT_AFTER_WINDOW
    return EXIT_NEEDS_FAHMI


def cmd_status(args):
    cfg = _load_config(args.config)
    ledger = _load_ledger(args.ledger)
    print(f"Trust Ladder v{cfg.get('version', '?')} (config: {args.config})")
    for cls in CLASSES:
        spec = cfg.get('classes', {}).get(cls, {})
        mode, why = effective_mode(cfg, ledger, cls)
        e = ledger.get(cls, {})
        print(f"  {cls} {spec.get('name', '')}: mode={mode}"
              + (f' ({why})' if why else '')
              + f" | accepted_prs={e.get('accepted_prs', 0)}"
              f" reverts={e.get('reverts', 0)} vetoes={e.get('vetoes', 0)}"
              f" corrections={e.get('corrections', 0)}"
              f" canary_trips={e.get('canary_trips', 0)}")
    return 0


def cmd_check(args):
    cls = args.action_class.upper()
    if cls not in CLASSES:
        print(f'error: unknown action class {cls} (A0..A5)', file=sys.stderr)
        return EXIT_USAGE
    cfg = _load_config(args.config)
    mode, why = effective_mode(cfg, _load_ledger(args.ledger), cls)
    code = check_exit(mode)
    label = {EXIT_ALLOWED: 'ALLOWED', EXIT_AFTER_WINDOW: 'ALLOWED AFTER VETO WINDOW',
             EXIT_NEEDS_FAHMI: 'NEEDS FAHMI'}[code]
    print(f'{cls}: {label} ({mode})' + (f' — {why}' if why else ''))
    return code


def cmd_record(args):
    cls = args.action_class.upper()
    if cls not in CLASSES:
        print(f'error: unknown action class {cls}', file=sys.stderr)
        return EXIT_USAGE
    cfg = _load_config(args.config)
    spec = cfg.get('classes', {}).get(cls, {})
    ledger = _load_ledger(args.ledger)
    entry = ledger.setdefault(cls, {})
    for k in ('accepted_prs', 'reverts', 'vetoes', 'corrections', 'canary_trips'):
        entry.setdefault(k, 0)
    ev, now = args.event, _now()
    if ev == 'accepted_pr':
        entry['accepted_prs'] += 1
        if not entry.get('first_accepted_at'):
            entry['first_accepted_at'] = now.isoformat(timespec='seconds')
        print(f"{cls}: accepted_pr recorded ({entry['accepted_prs']} total)")
    elif ev in DEMOTE_EVENTS:
        key = DEMOTE_EVENTS[ev]
        entry[key] = entry.get(key, 0) + 1
        if ev in spec.get('demote_on', []):
            days = int(spec.get('demote_for_days', 7))
            mode = spec.get('demoted_mode', 'fahmi_merge')
            entry['accepted_prs'] = 0
            entry['demoted_until'] = (now + datetime.timedelta(days=days)).isoformat(
                timespec='seconds')
            entry['demoted_mode'] = mode
            print(f"{cls} DEMOTED: {ev} -> {mode} for {days} days "
                  f"(until {entry['demoted_until'][:10]})")
        else:
            print(f'{cls}: {ev} recorded; mode unchanged (not in demote_on)')
    else:
        print(f'error: unknown event {ev}', file=sys.stderr)
        return EXIT_USAGE
    _save_ledger(args.ledger, ledger)
    print(f'ledger updated: {args.ledger}')
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--config', default=str(_default_config_path()))
    ap.add_argument('--ledger', default=str(_default_ledger_path()))
    sub = ap.add_subparsers(dest='command', required=True)

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
    p = sub.add_parser('record', help='record an accepted PR or a demotion event')
    p.add_argument('--class', dest='action_class', required=True)
    p.add_argument('--event', required=True, choices=EVENTS)
    _add_common(p)
    p.set_defaults(func=cmd_record)
    args = ap.parse_args()
    return args.func(args)


if __name__ == '__main__':
    sys.exit(main())
