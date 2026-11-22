"""Generate the muse-rsi router registry from the repo index. (v2)

Usage:
  python3 generate_registry.py [--repo PATH] [--out PATH] [--install] [--check]

- Default: regenerate <repo>/skills/router/registry.json from <repo>/skills/index.md
  and <repo>/docs/lumitome-index.md.
- --install: also install the 11 original skills into ~/workspace/custom-skills/
  (or $MUSE_RSI_CUSTOM_SKILLS) and copy the registry to
  ~/workspace/custom-skills/muse-rsi/registry.json.
- --check: regenerate to a temp string and diff against the stored registry;
  exit 1 when they differ (used by CI).

v2 changes (blueprint Fase 1):
- Index tables are parsed by HEADER NAME, not column position, so a table
  without a Licence column can no longer silently put notes into `license`.
  Bold markup (**...**) is stripped from every cell value.
- One shared token normalisation (normalize_terms — keep in sync with
  scripts/route.py): "next.js", "full-stack", "systematic review" are
  single matchable terms; 1-2 letter junk and stopwords are dropped
  (technical shorts ui/ux/qa/ci/cd/3d/ai/ml/db/id are kept).
- DOMAIN_KW gains a 'Security' key (lumitome uses domain 'Security';
  previously those 30 entries got zero domain keywords).
- Lumitome licence is 'Check Upstream', never a hardcoded 'MIT'.
  Listed licences come from the index's Licence column; missing means
  'Check Upstream'.
- No /home/hatch paths: repo and install dirs come from --repo,
  $MUSE_RSI_REPO / $MUSE_RSI_CUSTOM_SKILLS, or Path.home().

v2.1 changes (router gap fixes, 21 Nov 2026):
- normalize_terms now stems word forms (see _stem in route.py, kept
  byte-identical here) and indexes hyphen/dot components, so
  "orchestrate multiple agents" and "laporan keuangan" find their skills.
- Six generic nouns (model, doc, web, system, build, new) are stopwords:
  a lone hit from one of them used to outvote real topical terms.
- DOMAIN_KW: Security gains hardcoded/api key/credential/key/compliance;
  Full-Stack gains dashboard/dashboard ui; Design & 3D loses ui/ux (that
  domain is 3D/logo, not UI); Gap Fillers gains rank/rank better/scrape;
  Office gains email resmi/surat resmi/resmi/perusahaan/automate/
  infographic/dokumen; Finance (ID) gains laporan/keuangan; College gains
  kampus; Design & Media gains poster/image; Core RSI gains improve.
"""
import argparse, difflib, json, os, pathlib, re, sys

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
    'bikin', 'tolong', 'mohon', 'silakan',
    # 'tulis' is Indonesian "write": symmetric with English 'write'
    # above (see scripts/route.py). Keep the two STOPWORDS sets identical.
    'tulis',
}
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


def clean_cell(cell):
    """Strip bold markup and surrounding whitespace from a table cell."""
    return re.sub(r'\*\*([^*]+)\*\*', r'\1', cell or '').strip()


def find_repo(arg):
    if arg:
        return pathlib.Path(arg)
    env = os.environ.get('MUSE_RSI_REPO')
    if env:
        return pathlib.Path(env)
    here = pathlib.Path(__file__).resolve()
    if (here.parent.parent / 'skills' / 'index.md').exists():
        return here.parent.parent
    for cand in (pathlib.Path.home() / 'workspace' / 'muse-rsi',
                 pathlib.Path.home() / 'muse-rsi'):
        if (cand / 'skills' / 'index.md').exists():
            return cand
    raise SystemExit('repo not found; pass --repo')


ap = argparse.ArgumentParser()
ap.add_argument('--repo', default=None)
ap.add_argument('--out', default=None)
ap.add_argument('--install', action='store_true')
ap.add_argument('--check', action='store_true')
args = ap.parse_args()

repo = find_repo(args.repo)
custom = pathlib.Path(os.environ.get('MUSE_RSI_CUSTOM_SKILLS') or
                      (pathlib.Path.home() / 'workspace' / 'custom-skills'))
out_path = pathlib.Path(args.out) if args.out else repo / 'skills' / 'router' / 'registry.json'

# ---------- 1. Install the 11 original skills ----------
# Single source of truth: config/originals.json (v3.0 G1, M-13). Do not
# duplicate this list here or in setup.py — both read the same file.
def load_originals(repo_root):
    data = json.loads((pathlib.Path(repo_root) / 'config' / 'originals.json')
                      .read_text(encoding='utf-8'))
    return data['originals']


originals_list = load_originals(repo)
originals = {e['name']: (e['title'], e['category'], e['description_override'])
             for e in originals_list}
ORIGINAL_DOMAINS = {e['name']: e['domain'] for e in originals_list}
if args.install:
    for name, (title, category, desc_override) in originals.items():
        src = repo / 'skills' / name / 'SKILL.md'
        text = src.read_text(encoding='utf-8')
        desc = ''
        m = re.match(r'^---\n(.*?)\n---\n', text, re.S)
        if m:
            dm = re.search(r'^description:\s*(.+)$', m.group(1), re.M)
            if dm: desc = dm.group(1).strip()
            text = text[m.end():].lstrip('\n')
        if not desc:
            q = re.search(r'^>\s*(.+)$', text, re.M)
            desc = q.group(1).strip() if q else title
        if desc_override: desc = desc_override
        dest = custom / name
        dest.mkdir(parents=True, exist_ok=True)
        (dest / 'SKILL.md').write_text(text, encoding='utf-8')
        yaml = ('name: "%s"\ntitle: "%s"\ndescription: "%s"\ncategory: "%s"\ninclude_in_prompt: false\n'
                % (name, title, desc.replace('"', "'"), category))
        (dest / 'skill.yaml').write_text(yaml, encoding='utf-8')
        print('installed original:', name, '|', desc[:70])

# ---------- 2. Build registry from the repo index ----------
def parse_index_tables(path):
    """Parse every table row with a github.com link, mapping columns by
    header name. Tables without a Licence column yield 'Check Upstream'."""
    text = pathlib.Path(path).read_text(encoding='utf-8')
    entries = []
    current_section = None
    headers = None  # list of normalised header names for the current table
    for line in text.splitlines():
        hm = re.match(r'^##+\s+(.+?)\s*$', line)
        if hm:
            current_section = hm.group(1)
            headers = None
            continue
        if not line.startswith('|'):
            continue
        cells = [clean_cell(c) for c in line.strip().strip('|').split('|')]
        if not cells:
            continue
        if cells[0].startswith('---') or all(c.startswith(':') or c.startswith('-') for c in cells if c):
            continue
        if cells[0] == '#':
            headers = [re.sub(r'\s+', ' ', re.sub(r'[^a-z ]', '', c.lower())).strip() for c in cells]
            continue
        if 'github.com/' not in line:
            continue
        if current_section and 'Not Included' in current_section:
            continue
        link = None
        for cell in cells[:2]:
            link = re.search(r'\[([^\]]+)\]\((https://github\.com/[^)]+)\)', cell)
            if link:
                break
        if not link:
            continue
        li = next(i for i, c in enumerate(cells) if link.group(0) in c)
        rest = cells[li + 1:]
        col = {}
        if headers:
            # headers[0] is '#', headers[1] is 'Skill'; the rest align
            # with the cells after the link cell.
            for h, v in zip(headers[li + 1:], rest):
                col[h] = v
        entries.append({
            'name': link.group(1),
            'repo': link.group(2).replace('https://github.com/', ''),
            'url': link.group(2),
            'section': current_section,
            'stars': col.get('stars nov', ''),
            'skill_md': col.get('skillmd', ''),
            'license': col.get('licence', '') or col.get('license', '') or 'Check Upstream',
            'notes': col.get('notes', '') or col.get('closes the gap in', ''),
            # Optional per-entry routing keywords (header "Keywords").
            # Most rows leave it empty and rely on name + domain keywords;
            # a row that needs topical terms its name does not carry (e.g.
            # modern-web-guidance: dialog, modal, dark mode) lists them
            # here. They enter the 3.0 keyword field, like name terms.
            'keywords': col.get('keywords', ''),
        })
    return entries

listed = parse_index_tables(repo / 'skills' / 'index.md')
print('listed skills parsed:', len(listed))

# Lumitome index
lumi = []
text = (repo / 'docs' / 'lumitome-index.md').read_text(encoding='utf-8')
in_table = False
for line in text.splitlines():
    if line.startswith('| Skill |'):
        in_table = True
        continue
    if in_table:
        if not line.startswith('|'):
            break
        cells = [clean_cell(c) for c in line.strip().strip('|').split('|')]
        if len(cells) < 3 or cells[0].startswith(':') or cells[0].startswith('---'):
            continue
        name = cells[0].strip('`')
        if name in ('Skill',):
            continue
        lumi.append({'name': name, 'purpose': cells[1], 'domain': cells[2]})
print('lumitome skills parsed:', len(lumi))

# ---------- 3. Domain keywords for routing ----------
DOMAIN_KW = {
    'Core RSI': ['core', 'agent', 'skill', 'rsi', 'spec', 'workflow', 'improve'],
    'Gap Fillers': ['taste', 'design', 'designed', 'generic', 'slop', 'anti-slop', 'video', 'memory', 'seo', 'browser', 'presentation', 'accessibility', 'tdd', 'indonesian', 'redesign', 'landing', 'ui', 'polish', 'unslop', 'rank', 'rank better', 'scrape'],
    'DevOps & Infra': ['terraform', 'kubernetes', 'k8s', 'docker', 'deploy', 'ci', 'cd', 'aws', 'cloud', 'observability', 'sre', 'infrastructure', 'production', 'helm'],
    'College & Academic': ['thesis', 'paper', 'academic', 'citation', 'zotero', 'skripsi', 'tesis', 'journal', 'literature', 'research paper', 'dissertation', 'campus', 'kampus', 'study'],
    'Full-Stack Development': ['full-stack', 'fullstack', 'frontend', 'react', 'nextjs', 'next.js', 'typescript', 'api', 'testing', 'qa', 'playwright', 'cypress', 'dashboard', 'dashboard ui'],
    'Office & Corporate': ['email', 'spreadsheet', 'excel', 'powerpoint', 'ppt', 'outlook', 'meeting', 'office', 'corporate', 'trade', 'invoice', 'document', 'dokumen', 'email resmi', 'surat resmi', 'resmi', 'perusahaan', 'automate', 'infographic'],
    'Research': ['research', 'deep research', 'paper', 'literature review', 'prisma', 'systematic review', 'arxiv'],
    'Health & Medical': ['health', 'medical', 'clinical', 'fhir', 'biomedical', 'genomics', 'healthcare', 'medicine', 'patient', 'literature', 'evidence'],
    'Video': ['video', 'animation', 'motion', 'remotion', 'gsap'],
    'Defensive Security': ['security', 'audit', 'owasp', 'secret', 'leak', 'vulnerability', 'defensive', 'review', 'hardcoded', 'api key', 'credential', 'key', 'compliance'],
    'Security': ['security', 'audit', 'owasp', 'secret', 'leak', 'vulnerability', 'defensive', 'review', 'hardcoded', 'api key', 'credential', 'key', 'compliance'],
    'Design & 3D': ['design', 'blender', '3d', 'logo'],
    'Trading (Research Only)': ['trading', 'quant', 'backtest', 'finance'],
    'Research, Documents & Voice': ['research', 'document', 'transcription', 'voice', 'crawl', 'markdown'],
    'Writing & Language (ID)': ['writing', 'indonesian', 'indonesia', 'bahasa', 'artikel', 'tulis', 'naskah', 'humanizer'],
    'Finance & Business (ID)': ['finance', 'accounting', 'akuntansi', 'pajak', 'umkm', 'laporan', 'keuangan', 'laporan keuangan'],
    'Agent & Orchestration': ['agent', 'orchestration', 'subagent', 'mcp', 'eval'],
    'Design & Media': ['design', 'media', 'banner', 'logo', 'diagram', 'html', 'poster', 'image'],
    'Other': [],
}

def section_domain(section):
    s = (section or '').lower()
    if 'devops' in s: return 'DevOps & Infra'
    if 'academic' in s or 'college' in s: return 'College & Academic'
    if 'full-stack' in s: return 'Full-Stack Development'
    if 'office' in s: return 'Office & Corporate'
    if s.startswith('research') or 'research (' in s: return 'Research'
    if 'health' in s: return 'Health & Medical'
    if 'tier 1' in s: return 'Core RSI'
    if 'gap filler' in s: return 'Gap Fillers'
    if 'agent & orchestration' in s: return 'Agent & Orchestration'
    if 'tier 2' in s: return 'Video'
    if 'tier 3' in s: return 'Defensive Security'
    if 'tier 4' in s: return 'Research, Documents & Voice'
    if 'tier 5' in s: return 'Design & 3D'
    if 'tier 6' in s: return 'Trading (Research Only)'
    return section or 'Other'

def domain_keywords(domain):
    kws = set()
    for phrase in DOMAIN_KW.get(domain, []):
        kws |= normalize_terms(phrase)
    return kws

registry = {'version': 2, 'source_repo': 'fahmi0812/muse-rsi', 'verified': '2026-11-21',
            'counts': {}, 'skills': []}
for e in listed:
    domain = section_domain(e['section'])
    kws = domain_keywords(domain) | normalize_terms(e['name']) | normalize_terms(e.get('keywords', ''))
    tier = 'reference' if (e['section'] or '').startswith('Tier ') and 'Tier 1' not in (e['section'] or '') else 'core'
    registry['skills'].append({
        'name': e['name'], 'type': 'listed', 'tier': tier, 'domain': domain,
        'repo': e['repo'], 'url': e['url'], 'stars': e['stars'],
        'skill_md': e['skill_md'], 'license': e['license'],
        'notes': e['notes'], 'keywords': sorted(kws),
    })
for name, (title, category, _desc) in originals.items():
    od = ORIGINAL_DOMAINS[name]
    kws = domain_keywords(od) | normalize_terms(title + ' ' + name)
    registry['skills'].append({
        'name': name, 'type': 'original', 'domain': od,
        'repo': 'fahmi0812/muse-rsi', 'url': 'https://github.com/fahmi0812/muse-rsi',
        'path': f'skills/{name}/SKILL.md', 'license': 'MIT',
        'notes': title, 'keywords': sorted(kws),
    })
for l in lumi:
    registry['skills'].append({
        'name': l['name'], 'type': 'lumitome-reference', 'domain': l['domain'],
        'repo': 'fahmi0812/Lumitome', 'url': 'https://github.com/fahmi0812/Lumitome',
        'path': f'.opencode/skills/{l["name"]}/SKILL.md', 'license': 'Check Upstream',
        'notes': l['purpose'], 'keywords': sorted(domain_keywords(l['domain']) | normalize_terms(l['name'])),
    })
from collections import Counter
registry['counts'] = {'listed': len(listed), 'original': len(originals), 'lumitome_reference': len(lumi),
                      'total': len(registry['skills'])}
print('registry total:', registry['counts'])
reg_json = json.dumps(registry, ensure_ascii=False, indent=1)
print('registry bytes:', len(reg_json))
if args.check:
    stored = out_path.read_text(encoding='utf-8') if out_path.exists() else ''
    if stored == reg_json:
        print('CHECK OK: stored registry matches generated registry')
    else:
        print('CHECK FAIL: stored registry differs from generated registry')
        for line in difflib.unified_diff(stored.splitlines(), reg_json.splitlines(), 'stored', 'generated', lineterm=''):
            print(line)
        sys.exit(1)
else:
    out_path.write_text(reg_json, encoding='utf-8')
    print('wrote:', out_path)
    if args.install:
        router_reg = custom / 'muse-rsi' / 'registry.json'
        router_reg.parent.mkdir(parents=True, exist_ok=True)
        router_reg.write_text(reg_json, encoding='utf-8')
        print('wrote:', router_reg)
