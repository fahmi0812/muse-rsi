"""Validate the muse-rsi registry and repo structure. Stdlib only (CI-safe).

Checks:
- skills/router/registry.json parses and counts match the actual entries.
- Core listed skills == 64, reference listed == 32, originals == 9, Lumitome == 156.
- Every entry has name/type/domain/url/repo, and every URL is github.com.
- Every original skill's SKILL.md exists in the repo.
Exit 0 when everything passes, 1 otherwise.
Usage: python3 scripts/validate_registry.py
"""
import json, pathlib, sys

root = pathlib.Path(__file__).resolve().parent.parent
reg_path = root / 'skills' / 'router' / 'registry.json'
registry = json.loads(reg_path.read_text(encoding='utf-8'))
errors = []

counts = registry.get('counts', {})
skills = registry.get('skills', [])
by_type = {}
for s in skills:
    # entry type uses a hyphen ('lumitome-reference'); counts key uses underscore
    by_type.setdefault(s.get('type', '').replace('-', '_'), []).append(s)
core = [s for s in by_type.get('listed', []) if s.get('tier') == 'core']
ref = [s for s in by_type.get('listed', []) if s.get('tier') == 'reference']

expected = {'listed': len(by_type.get('listed', [])), 'original': len(by_type.get('original', [])),
            'lumitome_reference': len(by_type.get('lumitome_reference', [])), 'total': len(skills)}
for k, v in expected.items():
    if counts.get(k) != v:
        errors.append(f'counts.{k} is {counts.get(k)}, actual {v}')
if len(core) != 64:
    errors.append(f'core listed skills: {len(core)}, expected 64')
if len(ref) != 32:
    errors.append(f'reference listed skills: {len(ref)}, expected 32')
if len(by_type.get('original', [])) != 9:
    errors.append(f"original skills: {len(by_type.get('original', []))}, expected 9")
if len(by_type.get('lumitome_reference', [])) != 156:
    errors.append(f"lumitome_reference: {len(by_type.get('lumitome_reference', []))}, expected 156")

for s in skills:
    for field in ('name', 'type', 'domain', 'url', 'repo'):
        if not s.get(field):
            errors.append(f"entry {s.get('name', '?')} missing field: {field}")
    if s.get('url', '').startswith('https://github.com/') is False:
        errors.append(f"entry {s.get('name')} url is not github.com: {s.get('url')}")
    if s.get('type') == 'original':
        path = root / s.get('path', '')
        if not path.exists():
            errors.append(f"original skill file missing: {s.get('path')}")

if errors:
    print(f'VALIDATE FAIL ({len(errors)} problems):')
    for e in errors:
        print(' -', e)
    sys.exit(1)
print(f"VALIDATE OK: {len(skills)} entries "
      f"({len(core)} core + {len(ref)} reference + {len(by_type.get('original', []))} original "
      f"+ {len(by_type.get('lumitome_reference', []))} lumitome)")
