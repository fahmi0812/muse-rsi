#!/usr/bin/env python3
"""Validate skills/router/registry.json against the generator. (v2)

Schema checks (no hardcoded counts — a valid 'Add skill' PR must pass):
- registry.json parses; version is 2; counts match the actual entries.
- Every entry has name/type/domain/url/repo; every URL is github.com.
- Names are unique.
- Every domain is a known domain (see KNOWN_DOMAINS).
- license is present, is not the notes text, and contains no Markdown bold.
- keywords are non-empty, lowercase, and contain no 1-2 letter junk
  (except the technical whitelist) and no stopwords.
- Every original skill's SKILL.md exists in the repo.
- The stored registry matches what generate_registry.py produces
  (run the generator in --check mode as the source of truth).
Exit 0 when everything passes, 1 otherwise.
"""
import json, pathlib, subprocess, sys

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent

KNOWN_DOMAINS = {
    'Core RSI', 'Gap Fillers', 'DevOps & Infra', 'College & Academic',
    'Full-Stack Development', 'Office & Corporate', 'Research',
    'Health & Medical', 'Video', 'Defensive Security', 'Security',
    'Design & 3D', 'Trading (Research Only)', 'Research, Documents & Voice',
    'Writing & Language (ID)', 'Finance & Business (ID)',
    'Agent & Orchestration', 'Design & Media', 'Other',
}
SHORT_WHITELIST = {
    'ui', 'ux', 'qa', 'ci', 'cd', '3d', 'ai', 'ml', 'db', 'id', 'go',
    'js', 'ts', 'sql', 'api', 'r', 'c',
}
STOPWORDS = {
    'a', 'an', 'the', 'and', 'or', 'of', 'to', 'in', 'on', 'for', 'with',
    'how', 'what', 'is', 'are', 'be', 'do', 'it', 'this', 'that',
}

errors = []
reg_path = REPO / 'skills' / 'router' / 'registry.json'
try:
    registry = json.loads(reg_path.read_text(encoding='utf-8'))
except Exception as e:
    print(f'FAIL: cannot parse registry.json: {e}')
    sys.exit(1)

skills = registry.get('skills', [])
if registry.get('version') != 2:
    errors.append(f"registry version is {registry.get('version')}, expected 2")
counts = registry.get('counts', {})
by_type = {}
for s in skills:
    by_type.setdefault(s.get('type', '').replace('-', '_'), []).append(s)
expected = {'listed': len(by_type.get('listed', [])),
            'original': len(by_type.get('original', [])),
            'lumitome_reference': len(by_type.get('lumitome_reference', [])),
            'total': len(skills)}
for k, v in expected.items():
    if counts.get(k) != v:
        errors.append(f'counts.{k} is {counts.get(k)}, actual {v}')

seen = set()
for s in skills:
    name = s.get('name', '')
    if not name:
        errors.append('entry without a name')
        continue
    if name in seen:
        errors.append(f'duplicate name: {name}')
    seen.add(name)
    for field in ('type', 'domain', 'url', 'repo'):
        if not s.get(field):
            errors.append(f'{name}: missing {field}')
    if s.get('url') and not s['url'].startswith('https://github.com/'):
        errors.append(f"{name}: url is not github.com: {s['url']}")
    if s.get('domain') and s['domain'] not in KNOWN_DOMAINS:
        errors.append(f"{name}: unknown domain {s['domain']!r}")
    lic = s.get('license', '')
    if not lic:
        errors.append(f'{name}: missing license')
    elif lic == s.get('notes', ''):
        errors.append(f'{name}: license == notes (positional parse bug)')
    elif '**' in lic:
        errors.append(f"{name}: license contains Markdown bold: {lic!r}")
    kws = s.get('keywords', [])
    if not kws:
        errors.append(f'{name}: no keywords')
    for k in kws:
        if k != k.lower():
            errors.append(f"{name}: keyword not lowercase: {k!r}")
        if k in STOPWORDS:
            errors.append(f"{name}: stopword keyword: {k!r}")
        if len(k) < 3 and ' ' not in k and k not in SHORT_WHITELIST:
            errors.append(f"{name}: junk short keyword: {k!r}")
    if s.get('type') == 'original':
        p = REPO / 'skills' / name / 'SKILL.md'
        if not p.exists():
            errors.append(f'{name}: original SKILL.md missing at {p}')

# The generator is the source of truth for registry content.
gen = subprocess.run([sys.executable, str(HERE / 'generate_registry.py'), '--check'],
                     capture_output=True, text=True)
if gen.returncode != 0:
    errors.append('generate_registry.py --check failed (stored registry is stale)')
    print(gen.stdout[-2000:])
    print(gen.stderr[-2000:])

if errors:
    print(f'FAIL ({len(errors)} problems):')
    for e in errors:
        print(' -', e)
    sys.exit(1)
print(f'OK: registry valid — {len(skills)} entries '
      f'({counts.get("listed")} listed, {counts.get("original")} original, '
      f'{counts.get("lumitome_reference")} lumitome-reference)')
