"""Routing eval for the muse-rsi registry.

Scores each case in eval_routing.json with the same keyword-overlap rule the
router skill describes: match query words against each entry's keywords,
take the top 3, pass when one of them is in an expected domain.
Exit 0 when every case passes, 1 otherwise.
Usage: python3 eval_routing.py [--registry PATH] [--cases PATH]
"""
import argparse, json, pathlib, re, sys

ap = argparse.ArgumentParser()
ap.add_argument('--registry', default=None)
ap.add_argument('--cases', default=None)
args = ap.parse_args()

here = pathlib.Path(__file__).resolve().parent
if args.registry:
    reg_path = pathlib.Path(args.registry)
elif (here.parent.parent / 'skills' / 'router' / 'registry.json').exists():
    reg_path = here.parent.parent / 'skills' / 'router' / 'registry.json'
else:
    reg_path = pathlib.Path('/home/hatch/workspace/custom-skills/muse-rsi/registry.json')
cases_path = pathlib.Path(args.cases) if args.cases else here / 'eval_routing.json'

registry = json.loads(reg_path.read_text(encoding='utf-8'))
cases = json.loads(cases_path.read_text(encoding='utf-8'))['cases']

def route(query, top_n=3):
    words = set(re.split(r'[^a-z0-9]+', query.lower())) - {''}
    scored = []
    for s in registry['skills']:
        hit = len(words & set(s.get('keywords', [])))
        if hit:
            scored.append((hit, s['name'], s['domain']))
    scored.sort(key=lambda x: (x[0], x[1]), reverse=True)
    return scored[:top_n]

passed, failed = 0, []
for case in cases:
    top = route(case['query'])
    ok = any(d in case['expected_domains'] for _, _, d in top)
    status = 'PASS' if ok else 'FAIL'
    if ok:
        passed += 1
    else:
        failed.append(case['query'])
    print(f"[{status}] {case['query']}")
    for hit, name, domain in top:
        print(f"         {hit} | {name} | {domain}")
print(f"\n{passed}/{len(cases)} passed")
if failed:
    print('Failed queries:')
    for q in failed:
        print(' -', q)
    sys.exit(1)
