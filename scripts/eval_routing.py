"""Routing eval for the muse-rsi registry.

Scores each case in eval_routing.json with the same router the repo ships
(scripts/route.py): match query terms against each entry's keywords, take
the top 3, pass when one of them is in an expected domain. Cases with
"expect_no_match": true pass only when the router returns no match at all.
Exit 0 when every case passes, 1 otherwise.
Usage: python3 eval_routing.py [--registry PATH] [--cases PATH]
"""
import argparse, json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from route import route as route_query  # the real router code — the eval tests it

ap = argparse.ArgumentParser()
ap.add_argument('--registry', default=None)
ap.add_argument('--cases', default=None)
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


passed, failed = 0, []
for case in cases:
    top = route_query(case['query'], registry)
    if case.get('expect_no_match'):
        ok = top == []
    else:
        ok = any(d in case['expected_domains'] for _, _, d, _, _ in top)
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
print(f"\n{passed}/{len(cases)} passed")
if failed:
    print('Failed queries:')
    for q in failed:
        print(' -', q)
    sys.exit(1)
