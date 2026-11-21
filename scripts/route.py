#!/usr/bin/env python3
"""route.py — the muse-rsi router as a program, not just a document. (v2.1)

Scores a task description against the registry with a small BM25-style
ranker over three weighted fields (keywords 3.0, domain 2.0, notes 1.0),
using ONE shared token normalisation (see normalize_terms — keep in sync
with scripts/generate_registry.py): hyphenated / dotted phrases such as
"next.js", "full-stack" and multi-word phrases such as "systematic review"
are single matchable terms, hyphenated names also contribute their
components (dispatching-parallel-agents -> dispatch, parallel, agent), and
word forms are stemmed (agents -> agent, vulnerabilities -> vulnerability,
transcription -> transcribe, tulisan -> tulis) so a query need not use the
exact dictionary form. Short junk tokens are filtered out, and six generic
nouns (model, doc, web, system, build, new) never route on their own.

Tie-break is deterministic and relevance-first: higher score, then tier
(original > core > reference > lumitome-reference), then name ascending.
Queries with no keyword-field hit return NO_MATCH instead of a junk guess.

Usage:
  python3 scripts/route.py "deploy a Next.js app to Kubernetes" [--registry PATH] [--top N]
  python3 scripts/route.py "deploy a Next.js app" --json   # machine-parseable output, nothing else on stdout
  python3 scripts/route.py --self-test   # routing checks incl. phrases + NO_MATCH, exit 1 on failure

--json output (Poka-Yoke: strict JSON, exit 0 on a match, 2 on NO_MATCH):
  {"query": str, "no_match": bool, "results": [{"name", "domain", "type", "score", "url"}]}
"""
import argparse
import json
import math
import os
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent

# Generic words that must never create a match on their own.
STOPWORDS = {
    'a', 'an', 'the', 'and', 'or', 'of', 'to', 'in', 'on', 'for', 'with',
    'how', 'what', 'why', 'when', 'where', 'which', 'who', 'is', 'are',
    'was', 'were', 'be', 'do', 'does', 'did', 'can', 'could', 'should',
    'would', 'i', 'me', 'my', 'we', 'you', 'your', 'it', 'its', 'this',
    'that', 'these', 'those', 'there', 'here', 'please', 'help', 'want',
    'need', 'make', 'get', 'use', 'using', 'used', 'write', 'writes',
    'show', 'give', 'tell', 'find', 'check',
    # Generic nouns that must never route on their own: each is so broad
    # that a single hit would outvote real topical terms (a lone 'model'
    # once routed an ML-training query to the council skill; a lone 'doc'
    # routed "how to write it in a doc" to docs-pack; 'web'/'system'/
    # 'build'/'new' did the same for web-sims, agents-system and
    # self-audit). Real routing comes from the topical words around them.
    'model', 'doc', 'web', 'system', 'build', 'new',
    # Bahasa Indonesia (query dan nama skill ID sering memakai kata ini).
    'yang', 'dan', 'di', 'ke', 'dari', 'untuk', 'dengan', 'adalah', 'saya',
    'aku', 'kamu', 'kita', 'ini', 'itu', 'pada', 'oleh', 'sebagai', 'dalam',
    'juga', 'tidak', 'bisa', 'akan', 'sudah', 'telah', 'atau', 'jika',
    'kalau', 'agar', 'supaya', 'saat', 'ketika', 'lalu', 'kemudian',
    'sangat', 'lebih', 'paling', 'semua', 'setiap', 'antara', 'tanpa',
    'setelah', 'sebelum', 'karena', 'sehingga', 'namun', 'tetapi', 'tapi',
    'pun', 'lah', 'kah', 'nya', 'ku', 'mu', 'per', 'hal', 'cara', 'buat',
    'bikin', 'tolong', 'mohon', 'silakan', 'please',
}
# Short tokens that ARE technical terms and stay as keywords.
SHORT_WHITELIST = {
    'ui', 'ux', 'qa', 'ci', 'cd', '3d', 'ai', 'ml', 'db', 'id', 'go',
    'js', 'ts', 'sql', 'api', 'r', 'c',
}

_TOKEN_RE = re.compile(r'[a-z0-9]+(?:[.\-][a-z0-9]+)*')


# Words that must never be stemmed: stripping would corrupt a real word
# (bias -> bia, series -> serie) or a word the plural guard already saves.
STEM_DENYLIST = {
    'bias', 'alias', 'chaos', 'canvas', 'atlas', 'series', 'species',
}
# Explicit conflations the rules cannot reach safely.
STEM_EXCEPTIONS = {
    'analyses': 'analysis',
}


def _has_vowel(s):
    return any(c in 'aeiou' for c in s)


def _dedup(w):
    """Drop one of a doubled consonant after stripping -ing/-ed
    (running -> run, stopping -> stop); keep ll/ss/zz (falling -> fall)."""
    if len(w) >= 2 and w[-1] == w[-2] and w[-1] in 'bcdfgmnprt':
        return w[:-1]
    return w


def _stem(tok):
    """Conservative rule-based stemmer, applied identically to query terms
    and registry keywords so matching stays symmetric.

    Phase 1 (inflection): -ies -> -y, -sses/-es/-s plurals, -ment
    (deployment -> deploy, but document stays document), Indonesian
    -kan/-an (tulisan -> tulis, laporan -> lapor).
    Phase 2 (derivation): -iption -> -ibe (transcription -> transcribe),
    -ation -> -ate (animation -> animate; documentation -> document when
    the stem ends in -ment), -tion/-sion -> strip -ion (action -> act),
    -ing/-ed (dispatching -> dispatch, animated -> animat).
    Phase 3: final -e (orchestrate -> orchestrat, code -> cod).
    A rule only fires when the remaining stem is long enough and still
    contains a vowel; -ing/-ed never strip after -eed (speed, agreed).
    """
    if tok in STEM_DENYLIST or tok in STEM_EXCEPTIONS:
        return STEM_EXCEPTIONS.get(tok, tok)
    if len(tok) < 4:
        return tok
    if '.' in tok or '-' in tok:
        return tok  # hyphenated/dotted phrases stem per component, not whole
    w = tok
    # Phase 1 — inflection.
    if w.endswith('ies') and len(w[:-3]) >= 3:
        w = w[:-3] + 'y'
    elif w.endswith('yses'):
        w = w[:-4] + 'ysis'
    elif w.endswith('sses'):
        w = w[:-2]
    elif w.endswith('es') and len(w[:-2]) >= 3 and w[:-2].endswith(('ss', 'x', 'z', 'ch', 'sh')):
        w = w[:-2]
    elif w.endswith('s') and not w.endswith(('ss', 'us', 'is')) and len(w[:-1]) >= 3:
        w = w[:-1]
    if w.endswith('ment') and len(w[:-4]) >= 5 and w[:-4][-1] not in 'aeiou':
        w = w[:-4]
    elif w.endswith('kan') and len(w[:-3]) >= 3:
        w = w[:-3]
    elif w.endswith('an') and len(w[:-2]) >= 4:
        w = w[:-2]
    # Phase 2 — derivation (one branch; the result never re-enters a branch).
    if w.endswith('iption') and len(w[:-6]) >= 3:
        w = w[:-6] + 'ibe'
    elif w.endswith('ation') and len(w[:-5]) >= 3:
        stem = w[:-5]
        w = stem if stem.endswith('ment') else stem + 'ate'
    elif (w.endswith('tion') or w.endswith('sion')) and len(w[:-3]) >= 3:
        w = w[:-3]
    elif w.endswith('ing') and len(w[:-3]) >= 3 and _has_vowel(w[:-3]):
        w = _dedup(w[:-3])
    elif w.endswith('ed') and not w.endswith('eed') and len(w[:-2]) >= 3 and _has_vowel(w[:-2]):
        w = _dedup(w[:-2])
    # Phase 3 — final -e (verb stems converge).
    if len(w) > 3 and w.endswith('e') and w[-2] not in 'aeiou':
        w = w[:-1]
    return w


def normalize_terms(text):
    """Terms for matching: stemmed single tokens (hyphens/dots kept),
    squashed variants (next.js -> nextjs), hyphen/dot components
    (dispatching-parallel-agents -> dispatch, parallel, agent), and word
    bigrams over the stemmed stream ("systematic reviews" -> the bigram
    "systematic review").

    Keep in sync with scripts/generate_registry.py::normalize_terms.
    """
    raw = _TOKEN_RE.findall((text or '').lower())
    terms = set()
    for tok in raw:
        if len(tok) < 3 and tok not in SHORT_WHITELIST:
            continue
        if tok in STOPWORDS:
            continue
        stem = _stem(tok)
        if stem in STOPWORDS:
            continue  # e.g. systems -> system, docs -> doc, models -> model
        terms.add(stem)
        squashed = stem.replace('.', '').replace('-', '')
        if squashed != stem and len(squashed) >= 2:
            terms.add(squashed)
        if '.' in stem or '-' in stem:
            for part in re.split('[.-]', stem):
                if len(part) < 3 and part not in SHORT_WHITELIST:
                    continue
                if part in STOPWORDS:
                    continue
                part_stem = _stem(part)
                if part_stem in STOPWORDS:
                    continue
                terms.add(part_stem)
    # bigrams over the raw token stream (stopwords break bigrams, so
    # "review of systems" does not fake-match "systematic review"),
    # built from the stemmed forms so "systematic reviews" matches.
    # A bigram is dropped when either stemmed part is a stopword.
    for a, b in zip(raw, raw[1:]):
        if a in STOPWORDS or b in STOPWORDS:
            continue
        sa, sb = _stem(a), _stem(b)
        if sa in STOPWORDS or sb in STOPWORDS:
            continue
        terms.add(sa + ' ' + sb)
    return terms


def load_registry(path=None):
    if path:
        return json.loads(pathlib.Path(path).read_text(encoding='utf-8'))
    cands = [HERE.parent / 'skills' / 'router' / 'registry.json']
    env = os.environ.get('MUSE_RSI_REGISTRY')
    if env:
        cands.append(pathlib.Path(env))
    cands.append(pathlib.Path.home() / 'workspace' / 'custom-skills' / 'muse-rsi' / 'registry.json')
    for cand in cands:
        if cand.exists():
            return json.loads(cand.read_text(encoding='utf-8'))
    raise SystemExit('registry.json not found; pass --registry')


def idf_map(skills):
    """Inverse document frequency per term over the registry's keyword sets."""
    n = max(len(skills), 1)
    df = {}
    for s in skills:
        for t in set(s.get('keywords', [])):
            df[t] = df.get(t, 0) + 1
    return {t: math.log((n - d + 0.5) / (d + 0.5) + 1.0) for t, d in df.items()}


def tier_rank(skill):
    if skill.get('type') == 'original':
        return 0
    if skill.get('type') == 'lumitome-reference':
        return 3
    return 1 if skill.get('tier') == 'core' else 2


def score(query, skills):
    """Return [(score, name, domain, type, url), ...] sorted best-first.

    Empty list means NO_MATCH: no query term hit any keyword field.
    """
    qterms = normalize_terms(query)
    if not qterms:
        return []
    idf = idf_map(skills)
    out = []
    for s in skills:
        kw = set(s.get('keywords', []))
        kw_hits = qterms & kw
        if not kw_hits:
            continue  # a domain/notes-only hit is not a match
        total = 0.0
        for t in kw_hits:
            total += 3.0 * idf.get(t, 1.0)
        for t in qterms & normalize_terms(s.get('domain', '')):
            total += 2.0 * idf.get(t, 1.0)
        for t in qterms & normalize_terms(s.get('notes', '')):
            total += 1.0 * idf.get(t, 1.0)
        if total < 1.0:
            continue
        out.append((round(total, 2), s['name'], s.get('domain', ''),
                    s.get('type', ''), s.get('url', '')))
    by_name = {s['name']: s for s in skills}
    out.sort(key=lambda x: (-x[0], tier_rank(by_name.get(x[1], {})), x[1]))
    return out


def route(query, registry, top_n=3):
    return score(query, registry['skills'])[:top_n]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('query', nargs='?', default=None)
    ap.add_argument('--registry', default=None)
    ap.add_argument('--top', type=int, default=3)
    ap.add_argument('--json', action='store_true',
                    help='emit strict machine-parseable JSON, nothing else on stdout')
    ap.add_argument('--self-test', action='store_true')
    args = ap.parse_args()

    if args.json and args.self_test:
        ap.error('--json and --self-test are mutually exclusive')

    registry = load_registry(args.registry)
    if args.self_test:
        cases = [
            ('deploy a Next.js app to Kubernetes with Terraform', 'DevOps & Infra'),
            ('write my thesis and manage citations in Zotero', 'College & Academic'),
            ('read a medical paper and check the evidence', 'Health & Medical'),
            ('systematic review with prisma for my paper', 'Research'),
            ('anti-slop design taste for my landing page', 'Gap Fillers'),
        ]
        ok = True
        for q, domain in cases:
            top = route(q, registry)
            good = any(d == domain for _, _, d, _, _ in top)
            print(('PASS' if good else 'FAIL'), '|', q, '->', top[0][1] if top else 'none')
            ok = ok and good
        neg = route('what is the weather in Jakarta tomorrow', registry)
        good_neg = neg == []
        print(('PASS' if good_neg else 'FAIL'), '| negative query ->',
              'NO_MATCH' if good_neg else neg[0][1])
        ok = ok and good_neg
        print('SELF-TEST', 'OK' if ok else 'FAIL')
        return 0 if ok else 1

    if not args.query:
        ap.error('give a task description or --self-test')
    top = route(args.query, registry, args.top)
    if args.json:
        payload = {
            'query': args.query,
            'no_match': not top,
            'results': [
                {'name': name, 'domain': domain, 'type': typ, 'score': sc, 'url': url}
                for sc, name, domain, typ, url in top
            ],
        }
        print(json.dumps(payload, ensure_ascii=False))
        return 2 if not top else 0
    if not top:
        print('NO_MATCH: no skill covers this task')
        return 2
    for sc, name, domain, typ, url in top:
        print(f'{sc} | {name} | {domain} | {typ} | {url}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
