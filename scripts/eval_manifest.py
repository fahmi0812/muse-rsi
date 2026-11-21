#!/usr/bin/env python3
"""eval_manifest.py — frozen SHA-256 manifest for the routing eval.

Records exactly which code and data produced an eval result, so a later
"the eval passed" claim can be checked instead of trusted:

  eval/manifest.json:
    inputs:   sha256 of skills/router/registry.json, scripts/route.py,
              scripts/eval_routing.py, scripts/eval_routing.json
    result:   cases, passed, registry_version, router_version
    generated_at: UTC timestamp of the manifest (informational only)

Default mode runs the eval first (it must pass — a frozen manifest is
only written for a green eval), then writes eval/manifest.json.

--verify re-hashes the four inputs and compares them plus the recorded
result against the stored manifest; exits 0 on match, 1 on any mismatch.
generated_at is deliberately ignored by --verify: re-running the manifest
on unchanged inputs must reproduce identical input hashes, while the
timestamp is expected to differ between runs.

Usage:
  python3 scripts/eval_manifest.py [--registry PATH] [--cases PATH]
  python3 scripts/eval_manifest.py --verify [--manifest PATH]
"""
import argparse
import datetime
import hashlib
import json
import pathlib
import re
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent

INPUT_FILES = [
    'skills/router/registry.json',
    'scripts/route.py',
    'scripts/eval_routing.py',
    'scripts/eval_routing.json',
]


def sha256_file(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def router_version():
    text = (ROOT / 'scripts' / 'route.py').read_text(encoding='utf-8')
    m = re.search(r'route\.py.*\(v([0-9.]+)\)', text)
    return m.group(1) if m else None


def run_eval(registry, cases):
    proc = subprocess.run(
        [sys.executable, str(HERE / 'eval_routing.py'),
         '--registry', str(registry), '--cases', str(cases)],
        capture_output=True, text=True, encoding='utf-8')
    m = re.search(r'^(\d+)/(\d+) passed$', proc.stdout, re.M)
    if proc.returncode != 0 or not m:
        print(proc.stdout[-2000:])
        print(proc.stderr[-2000:], file=sys.stderr)
        print('eval did not pass — refusing to write a manifest for a red eval')
        return None
    return int(m.group(1)), int(m.group(2))


def build_manifest(registry, cases):
    result = run_eval(registry, cases)
    if result is None:
        return None
    passed, total = result
    reg_data = json.loads(pathlib.Path(registry).read_text(encoding='utf-8'))
    return {
        'inputs': {rel: sha256_file(ROOT / rel) for rel in INPUT_FILES},
        'result': {
            'cases': total,
            'passed': passed,
            'registry_version': reg_data.get('version'),
            'router_version': router_version(),
        },
        'generated_at': datetime.datetime.now(datetime.timezone.utc)
                        .isoformat(timespec='seconds').replace('+00:00', 'Z'),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--registry', default=None)
    ap.add_argument('--cases', default=None)
    ap.add_argument('--manifest', default=None)
    ap.add_argument('--verify', action='store_true')
    args = ap.parse_args()

    manifest_path = pathlib.Path(args.manifest) if args.manifest \
        else ROOT / 'eval' / 'manifest.json'

    if args.verify:
        if not manifest_path.exists():
            print(f'no manifest at {manifest_path} — run without --verify first')
            return 1
        stored = json.loads(manifest_path.read_text(encoding='utf-8'))
        fresh_inputs = {rel: sha256_file(ROOT / rel) for rel in INPUT_FILES}
        problems = []
        for rel, digest in fresh_inputs.items():
            if stored.get('inputs', {}).get(rel) != digest:
                problems.append(f'{rel}: hash changed')
        result = run_eval(args.registry or ROOT / 'skills' / 'router' / 'registry.json',
                          args.cases or HERE / 'eval_routing.json')
        if result is None:
            problems.append('eval does not pass now')
        else:
            passed, total = result
            if stored.get('result', {}).get('passed') != passed \
                    or stored.get('result', {}).get('cases') != total:
                problems.append(
                    f"recorded result {stored.get('result')} != current {passed}/{total}")
        if problems:
            print('MANIFEST MISMATCH:')
            for p in problems:
                print(f'  - {p}')
            return 1
        print(f'MANIFEST OK: {manifest_path} matches current inputs and eval '
              f'({stored["result"]["passed"]}/{stored["result"]["cases"]} passed)')
        return 0

    manifest = build_manifest(
        args.registry or ROOT / 'skills' / 'router' / 'registry.json',
        args.cases or HERE / 'eval_routing.json')
    if manifest is None:
        return 1
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    print(f'wrote {manifest_path}: {manifest["result"]["passed"]}/'
          f'{manifest["result"]["cases"]} passed, '
          f'registry v{manifest["result"]["registry_version"]}, '
          f'router v{manifest["result"]["router_version"]}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
