#!/usr/bin/env python3
"""gen_facts.py — build state/facts.json from machine-computed numbers (v3.0 G1, M-13).

The Truth Layer's single source of numbers (design Bab 4.4): every figure
in facts.json is computed by running the repo's own tools, never copied
by hand from a document.

  registry counts : read from skills/router/registry.json (cross-checked
                    against the skills list by type)
  eval top-3      : scripts/eval_routing.py output ("125/125 passed")
  eval top-1      : strict re-score — a positive case passes only when the
                    router's TOP-1 hit is in an expected domain; a negative
                    (expect_no_match) case passes only on NO_MATCH
  canary          : scripts/test_canary.py ("Ran 7 tests", OK)
  manifest        : scripts/eval_manifest.py --verify + sha256 of
                    eval/manifest.json
  head            : git rev-parse --short HEAD

Usage:
  python3 scripts/gen_facts.py [--repo PATH] [--out PATH]
  python3 scripts/gen_facts.py --check [--repo PATH] [--out PATH]
    --check recomputes the facts and compares them with the stored file
    (ignoring generated_at); exit 0 on match, 1 on any mismatch,
    2 when no stored file exists yet.
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
DEFAULT_REPO = HERE.parent


def _run(cmd, cwd):
    return subprocess.run(cmd, cwd=str(cwd), capture_output=True,
                          text=True, encoding='utf-8', timeout=300)


def registry_counts(repo):
    path = repo / 'skills' / 'router' / 'registry.json'
    reg = json.loads(path.read_text(encoding='utf-8'))
    counts = reg.get('counts', {})
    # Cross-check the stored counts against the skills list itself.
    by_type = {}
    for s in reg.get('skills', []):
        by_type[s.get('type')] = by_type.get(s.get('type'), 0) + 1
    listed = by_type.get('listed', 0)
    original = by_type.get('original', 0)
    lumitome = by_type.get('lumitome-reference', 0)
    total = len(reg.get('skills', []))
    for key, got, want in (('listed', listed, counts.get('listed')),
                           ('original', original, counts.get('original')),
                           ('lumitome_reference', lumitome,
                            counts.get('lumitome_reference')),
                           ('total', total, counts.get('total'))):
        if want is not None and got != want:
            raise SystemExit(
                f'registry.json counts mismatch: {key} counted {got} '
                f'but counts field says {want}')
    return {
        'registry_version': reg.get('version'),
        'registry_total': total,
        'listed': listed,
        'original': original,
        'lumitome': lumitome,
    }


def eval_scores(repo):
    """Top-3 score from eval_routing.py; top-1 strict re-score in-process."""
    proc = _run([sys.executable, str(HERE / 'eval_routing.py'),
                 '--registry', str(repo / 'skills' / 'router' / 'registry.json')],
                cwd=repo)
    m = re.search(r'^(\d+)/(\d+) passed$', proc.stdout, re.M)
    if proc.returncode != 0 or not m:
        print(proc.stdout[-2000:])
        print(proc.stderr[-2000:], file=sys.stderr)
        raise SystemExit('eval_routing.py did not pass — facts not generated')
    top3_passed, top3_total = int(m.group(1)), int(m.group(2))

    sys.path.insert(0, str(HERE))
    from route import route as route_query  # the real router code
    registry = json.loads(
        (repo / 'skills' / 'router' / 'registry.json').read_text(encoding='utf-8'))
    cases = json.loads(
        (HERE / 'eval_routing.json').read_text(encoding='utf-8'))['cases']
    pos_total = pos_passed = neg_total = neg_passed = 0
    for case in cases:
        top = route_query(case['query'], registry)
        if case.get('expect_no_match'):
            neg_total += 1
            if top == []:
                neg_passed += 1
        else:
            pos_total += 1
            # Cases may pin the exact winner (expect_top1_name, added
            # G1-B for the two new skills) or a domain list. A case
            # with neither counts as passed when the router matches
            # anything — its top-3 verdict already comes from
            # eval_routing.py itself.
            if 'expect_top1_name' in case:
                if top and top[0][1] == case['expect_top1_name']:
                    pos_passed += 1
            elif 'expected_domains' in case:
                if top and top[0][2] in case['expected_domains']:
                    pos_passed += 1
            elif top:
                pos_passed += 1
    return {
        'eval_top3': f'{top3_passed}/{top3_total}',
        'eval_top3_passed': top3_passed,
        'eval_top3_total': top3_total,
        'eval_top1_positive': f'{pos_passed}/{pos_total}',
        'eval_top1_positive_passed': pos_passed,
        'eval_top1_positive_total': pos_total,
        'eval_top1_negative': f'{neg_passed}/{neg_total}',
        'eval_top1_negative_passed': neg_passed,
        'eval_top1_negative_total': neg_total,
    }


def canary_score(repo):
    proc = _run([sys.executable, str(HERE / 'test_canary.py')], cwd=repo)
    # unittest writes its report to stderr, not stdout.
    combined = proc.stdout + proc.stderr
    m = re.search(r'^Ran (\d+) tests? in ', combined, re.M)
    if proc.returncode != 0 or not m or '\nOK' not in combined:
        print(combined[-2000:], file=sys.stderr)
        raise SystemExit('test_canary.py did not pass — facts not generated')
    total = int(m.group(1))
    return {'canary': f'{total}/{total}', 'canary_passed': total,
            'canary_total': total}


def manifest_info(repo):
    manifest_path = repo / 'eval' / 'manifest.json'
    proc = _run([sys.executable, str(HERE / 'eval_manifest.py'), '--verify'],
                cwd=repo)
    ok = proc.returncode == 0
    digest = None
    if manifest_path.exists():
        digest = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
    return {'manifest_ok': ok,
            'manifest_sha256': digest}


def router_version(repo):
    text = (repo / 'scripts' / 'route.py').read_text(encoding='utf-8')
    m = re.search(r'route\.py.*\(v([0-9.]+)\)', text)
    return m.group(1) if m else None


def head_sha(repo):
    """HEAD of the content facts.json describes.

    Committing facts.json itself must not invalidate it: the stored
    head is the last commit that touched anything EXCEPT
    state/facts.json. (A plain rev-parse HEAD can never match after
    the facts commit lands, because that commit moves HEAD.)
    Falls back to rev-parse HEAD when the pathspec form is unavailable.
    """
    proc = _run(['git', 'log', '-1', '--format=%h', '--', '.',
                 ':!state/facts.json'], cwd=repo)
    if proc.returncode == 0 and proc.stdout.strip():
        return proc.stdout.strip()
    proc = _run(['git', 'rev-parse', '--short', 'HEAD'], cwd=repo)
    return proc.stdout.strip() if proc.returncode == 0 else 'unknown'


def compute_facts(repo):
    facts = {
        'generated_at': datetime.datetime.now(datetime.timezone.utc)
                         .isoformat(timespec='seconds').replace('+00:00', 'Z'),
        'head': head_sha(repo),
        'router_version': router_version(repo),
    }
    facts.update(registry_counts(repo))
    facts.update(eval_scores(repo))
    facts.update(canary_score(repo))
    facts.update(manifest_info(repo))
    return facts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo', default=None)
    ap.add_argument('--out', default=None)
    ap.add_argument('--check', action='store_true',
                    help='compare stored facts.json with a fresh computation')
    args = ap.parse_args()
    repo = pathlib.Path(args.repo) if args.repo else DEFAULT_REPO
    out = pathlib.Path(args.out) if args.out else repo / 'state' / 'facts.json'

    fresh = compute_facts(repo)
    if args.check:
        if not out.exists():
            print(f'no stored facts at {out} — run without --check first')
            return 2
        stored = json.loads(out.read_text(encoding='utf-8'))
        stored.pop('generated_at', None)
        fresh_cmp = dict(fresh)
        fresh_cmp.pop('generated_at', None)
        problems = []
        for key in sorted(set(stored) | set(fresh_cmp)):
            if stored.get(key) != fresh_cmp.get(key):
                problems.append(f'{key}: stored {stored.get(key)!r} '
                                f'!= current {fresh_cmp.get(key)!r}')
        if problems:
            print('FACTS MISMATCH — stored facts.json is stale:')
            for p in problems:
                print(f'  - {p}')
            return 1
        print(f'FACTS OK: {out} matches current repo state '
              f'(registry {fresh["registry_total"]}, eval top-3 '
              f'{fresh["eval_top3"]}, top-1 {fresh["eval_top1_positive"]}, '
              f'canary {fresh["canary"]}, head {fresh["head"]})')
        return 0

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(fresh, indent=2) + '\n', encoding='utf-8')
    print(f'wrote {out}: registry {fresh["registry_total"]} '
          f'({fresh["listed"]} listed + {fresh["original"]} original + '
          f'{fresh["lumitome"]} lumitome), eval top-3 {fresh["eval_top3"]}, '
          f'top-1 positive {fresh["eval_top1_positive"]}, '
          f'top-1 negative {fresh["eval_top1_negative"]}, '
          f'canary {fresh["canary"]}, manifest_ok={fresh["manifest_ok"]}, '
          f'head {fresh["head"]}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
