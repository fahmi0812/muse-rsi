"""Routing eval for the muse-rsi registry.

Scores each case in eval_routing.json with the same router the repo ships
(scripts/route.py): match query terms against each entry's keywords, take
the top 3, pass when one of them is in an expected domain. Cases with
"expect_no_match": true pass only when the router returns no match at all
(that covers the deliberate NO_MATCH negatives AND the policy refusals:
route.py refuses AI-detection / plagiarism-evasion requests before
scoring, so they come back as NO_MATCH too). Cases with
"expect_top1_name": pass only when the top-1 result has exactly that
name — a stricter assertion for cases that must land on one specific
skill (e.g. a new skill must beat its near-neighbours, not just its
domain).

--strict: top-1 mode. A positive case passes only when the TOP-1 result
is in an expected domain (or is the expected name for expect_top1_name
cases). This is the C1 metric (Balanced Scaling Scorecard): the plain
mode measures top-3 coverage, --strict measures whether the router's
first answer is right. Exit 0 when every case passes, 1 otherwise.

Usage: python3 eval_routing.py [--registry PATH] [--cases PATH] [--strict]
"""
import argparse, json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from route import route as route_query  # the real router code — the eval tests it

ap = argparse.ArgumentParser()
ap.add_argument('--registry', default=None)
ap.add_argument('--cases', default=None)
ap.add_argument('--strict', action='store_true',
                help='top-1 mode: a positive case passes only when the '
                     'top-1 result is in an expected domain (C1 metric)')
args = ap.parse_args()

here = pathlib.Path(__file__).resolve().parent
if args.registry:
    reg_path = pathlib.Path(args.registry)
elif (here.parent / 'skills' / 'router' / 'registry.json').exists():
    reg_path = here.parent / 'skills' / 'router' / 'registry.json'
else:
    reg_path = pathlib.Path.home() / 'workspace' / 'custom-skills' / 'muse-rsi' / 'registry.json'
cases_path = pathlib.Path(args.cases) if args.cases else here / 'eval_routing.json'

registry = json.loads(reg_path.read_text(encoding='utf-8'))
cases = json.loads(cases_path.read_text(encoding='utf-8'))['cases']


def check(case, top):
    """Return (ok, kind) for one case under the active mode."""
    if case.get('expect_no_match'):
        return top == [], 'negative'
    if case.get('expect_top1_name'):
        # Name assertion is top-1 by definition, in both modes.
        return bool(top) and top[0][1] == case['expect_top1_name'], 'top1-name'
    if args.strict:
        return bool(top) and top[0][2] in case['expected_domains'], 'positive'
    return any(d in case['expected_domains'] for _, _, d, _, _ in top), 'positive'


passed, failed = 0, []
strict_pos_total, strict_pos_pass = 0, 0
for case in cases:
    top = route_query(case['query'], registry)
    ok, kind = check(case, top)
    if kind in ('positive', 'top1-name'):
        strict_pos_total += 1
        if ok:
            strict_pos_pass += 1
    status = 'PASS' if ok else 'FAIL'
    if ok:
        passed += 1
    else:
        failed.append(case['query'])
    print(f"[{status}] {case['query']}")
    if not top:
        print("         NO_MATCH")
    for hit, name, domain, _typ, _url in top:
        print(f"         {hit} | {name} | {domain}")
print(f"\n{passed}/{len(cases)} passed" + (" (strict top-1 mode)" if args.strict else ""))
if args.strict:
    print(f"strict top-1: {strict_pos_pass}/{strict_pos_total} positive cases "
          f"correct at top-1")
if failed:
    print('Failed queries:')
    for q in failed:
        print(' -', q)
    sys.exit(1)
