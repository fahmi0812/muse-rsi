#!/usr/bin/env python3
"""stop_cycle.py — HUMAN-ONLY STOP writer for muse-rsi v3.0.

Writes ~/.muse-rsi/STOP so the next cycle transition HALTs. Only
Fahmi can lift it (remove the file).

Directives isolation (Fahmi, 22 Nov 2026): this writer lives OUTSIDE
scripts/rsi_cycle.py on purpose. The cron cycle (02.00) has READ-ONLY
access to directives.yaml and the STOP file and must never write
either of them — no prompt injection or accidental edit inside an
autonomous cycle can change what the loop obeys. Never invoke this
script from a cron job, a cycle, or any automated loop. Run it by
hand, as Fahmi, when a HALT is wanted.

Usage: python3 scripts/stop_cycle.py --reason "why"
"""
import argparse
import datetime
import pathlib
import sys


def main():
    ap = argparse.ArgumentParser(description='Write the STOP file (human-only)')
    ap.add_argument('--reason', default='manual halt')
    args = ap.parse_args()
    home = pathlib.Path.home() / '.muse-rsi'
    home.mkdir(parents=True, exist_ok=True)
    now = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')
    (home / 'STOP').write_text(f'{now} {args.reason}\n', encoding='utf-8')
    print(f'STOP written to {home / "STOP"}: {args.reason}')
    print('The next cycle transition will HALT. Only Fahmi can lift it '
          '(remove the file).')
    return 0


if __name__ == '__main__':
    sys.exit(main())
