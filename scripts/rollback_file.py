#!/usr/bin/env python3
"""rollback_file.py — real content rollback for muse-rsi (forward-fix, not history rewrite).

The GitHub connector cannot force-push, so history can never be rewritten from
here. What CAN be rolled back is content: restore a file's last-known-good
version from the read-only mirror clone (true remote history) or from the
latest backup tarball, into the working tree.
Then run the checks and push the restore as a new commit.

Usage:
  python3 scripts/rollback_file.py <path-in-repo> [--from mirror|backup] [--list]
  python3 scripts/rollback_file.py --list   # show the mirror's last commit + latest backup
  Paths default to Path.home() locations; override with --repo/--mirror/--backups.
"""
import argparse
import pathlib
import shutil
import subprocess
import sys
import tarfile

HOME = pathlib.Path.home()
DEFAULT_REPO = HOME / 'muse-rsi'
DEFAULT_MIRROR = HOME / 'workspace' / 'muse-rsi-remote'
DEFAULT_BACKUPS = HOME / 'workspace' / 'backups'


def latest_backup(backups):
    if not backups.exists():
        return None
    tars = sorted(backups.glob('muse-rsi-*.tar.gz'))
    return tars[-1] if tars else None


def _safe_target(repo, path):
    """Resolve <path-in-repo> inside the repo; refuse '..' escapes."""
    target = (repo / path).resolve()
    if target != repo.resolve() and repo.resolve() not in target.parents:
        raise SystemExit(f'refusing path outside the repo: {path}')
    return target


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('path', nargs='?', default=None)
    ap.add_argument('--from', dest='source', choices=['mirror', 'backup'], default='mirror')
    ap.add_argument('--list', action='store_true')
    ap.add_argument('--repo', default=None, help='working repo (default ~/muse-rsi)')
    ap.add_argument('--mirror', default=None, help='read-only mirror clone (default ~/workspace/muse-rsi-remote)')
    ap.add_argument('--backups', default=None, help='backup dir (default ~/workspace/backups)')
    args = ap.parse_args()

    repo = pathlib.Path(args.repo) if args.repo else DEFAULT_REPO
    mirror = pathlib.Path(args.mirror) if args.mirror else DEFAULT_MIRROR
    backups = pathlib.Path(args.backups) if args.backups else DEFAULT_BACKUPS

    if args.list or not args.path:
        if mirror.exists():
            r = subprocess.run(['git', 'log', '--oneline', '-1'], cwd=str(mirror),
                               capture_output=True, text=True)
            print('mirror HEAD:', r.stdout.strip() if r.returncode == 0 else 'mirror git log failed')
        else:
            print('mirror HEAD: mirror missing at', mirror)
        b = latest_backup(backups)
        print('latest backup:', b.name if b else 'none')
        return 0

    target = _safe_target(repo, args.path)
    if args.source == 'mirror':
        src = mirror / args.path
        if not src.exists():
            sys.exit(f'not in mirror: {args.path}')
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, target)
        origin = f'mirror clone ({mirror})'
    else:
        b = latest_backup(backups)
        if not b:
            sys.exit('no backup tarball found')
        with tarfile.open(b) as tf:
            # Exact match only (after stripping the tarball's top-level dir):
            # endswith() could restore the wrong file from a same-named path.
            member = None
            for m in tf.getmembers():
                if not m.isfile():
                    continue
                stripped = '/'.join(m.name.split('/')[1:]) if '/' in m.name else m.name
                if stripped == args.path:
                    member = m
                    break
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
