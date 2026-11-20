#!/usr/bin/env python3
"""route.py — the muse-rsi router as a program, not just a document.

Scores a task description against the registry (keyword overlap, same rule the
router skill describes) and prints the top matches. This is the code the
routing eval tests — if the eval passes, this router works.

Usage:
  python3 scripts/route.py "deploy a Next.js app to Kubernetes" [--registry PATH] [--top N]
  python3 scripts/route.py --self-test   # 3 quick routing checks, exit 1 on failure
"""
import argparse
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent


def load_registry(path=None):
    if path:
        return json.loads(pathlib.Path(path).read_text(encoding='utf-8'))
    for cand in (HERE.parent / 'skills' / 'router' / 'registry.json',
                 pathlib.Path('/home/hatch/workspace/custom-skills/muse-rsi/registry.json')):
        if cand.exists():
            return json.loads(cand.read_text(encoding='utf-8'))
    raise SystemExit('registry.json not found; pass --registry')


def score(query, skills):
    words = set(re.split(r'[^a-z0-9]+', query.lower())) - {''}
    out = []
    for s in skills:
        hit = len(words & set(s.get('keywords', [])))
        if hit:
            out.append((hit, s['name'], s.get('domain', ''), s.get('type', ''), s.get('url', '')))
    out.sort(key=lambda x: (x[0], x[1]), reverse=True)
    return out


def route(query, registry, top_n=3):
    return score(query, registry['skills'])[:top_n]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('query', nargs='?', default=None)
    ap.add_argument('--registry', default=None)
    ap.add_argument('--top', type=int, default=3)
    ap.add_argument('--self-test', action='store_true')
    args = ap.parse_args()

    registry = load_registry(args.registry)
    if args.self_test:
        cases = [
            ('deploy a Next.js app to Kubernetes with Terraform', 'DevOps & Infra'),
            ('write my thesis and manage citations in Zotero', 'College & Academic'),
            ('read a medical paper and check the evidence', 'Health & Medical'),
        ]
        ok = True
        for q, domain in cases:
            top = route(q, registry)
            good = any(d == domain for _, _, d, _, _ in top)
            print(('PASS' if good else 'FAIL'), '|', q, '->', top[0][1] if top else 'none')
            ok = ok and good
        print('SELF-TEST', 'OK' if ok else 'FAIL')
        return 0 if ok else 1

    if not args.query:
        ap.error('give a task description or --self-test')
    for hit, name, domain, typ, url in route(args.query, registry, args.top):
        print(f'{hit} | {name} | {domain} | {typ} | {url}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
