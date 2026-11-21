#!/usr/bin/env python3
"""rollback_file.py — real content rollback for muse-rsi (forward-fix, not history rewrite).

The GitHub connector cannot force-push, so history can never be rewritten from
here. What CAN be rolled back is content: restore a file's last-known-good
version from the read-only mirror clone (~/workspace/muse-rsi-remote, true
remote history) or from the latest backup tarball, into the working tree.
Then run the checks and push the restore as a new commit.

Usage:
  python3 scripts/rollback_file.py <path-in-repo> [--from mirror|backup] [--list]
  python3 scripts/rollback_file.py --list   # show the mirror's last commit + latest backup
"""
import argparse
import pathlib
import shutil
import subprocess
import sys
import tarfile

REPO = pathlib.Path('/home/hatch/muse-rsi')
MIRROR = pathlib.Path('/home/hatch/workspace/muse-rsi-remote')
BACKUPS = pathlib.Path('/home/hatch/workspace/backups')


def latest_backup():
    if not BACKUPS.exists():
        return None
    tars = sorted(BACKUPS.glob('muse-rsi-*.tar.gz'))
    return tars[-1] if tars else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('path', nargs='?', default=None)
    ap.add_argument('--from', dest='source', choices=['mirror', 'backup'], default='mirror')
    ap.add_argument('--list', action='store_true')
    args = ap.parse_args()

    if args.list or not args.path:
        r = subprocess.run(['git', 'log', '--oneline', '-1'], cwd=str(MIRROR),
                           capture_output=True, text=True)
        print('mirror HEAD:', r.stdout.strip() if r.returncode == 0 else 'mirror missing')
        b = latest_backup()
        print('latest backup:', b.name if b else 'none')
        return 0

    target = REPO / args.path
    if args.source == 'mirror':
        src = MIRROR / args.path
        if not src.exists():
            sys.exit(f'not in mirror: {args.path}')
        shutil.copyfile(src, target)
        origin = f'mirror clone ({MIRROR})'
    else:
        b = latest_backup()
        if not b:
            sys.exit('no backup tarball found')
        with tarfile.open(b) as tf:
            member = next((m for m in tf.getmembers() if m.name.endswith(args.path)), None)
            if not member:
                sys.exit(f'{args.path} not in backup {b.name}')
            data = tf.extractfile(member).read()
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        origin = f'backup {b.name}'
    print(f'restored {args.path} from {origin} into the working tree')
    print('next: run ~/workspace/tools/run_all_checks.sh, then push with push-files (new commit)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
