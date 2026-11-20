"""Generate the muse-rsi router registry from the repo index.

Usage:
  python3 generate_registry.py [--repo PATH] [--out PATH] [--install] [--check]

- Default: regenerate <repo>/skills/router/registry.json from <repo>/skills/index.md
  and <repo>/docs/lumitome-index.md.
- --install: also install the 9 original skills into ~/workspace/custom-skills/
  and copy the registry to ~/workspace/custom-skills/muse-rsi/registry.json.
- --check: regenerate to a temp string and diff against the stored registry;
  exit 1 when they differ (used by CI).
"""
import argparse, difflib, json, pathlib, re, sys

def find_repo(arg):
    if arg:
        return pathlib.Path(arg)
    here = pathlib.Path(__file__).resolve()
    if (here.parent.parent / 'skills' / 'index.md').exists():
        return here.parent.parent
    cand = pathlib.Path('/home/hatch/workspace/muse-rsi')
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
custom = pathlib.Path('/home/hatch/workspace/custom-skills')
out_path = pathlib.Path(args.out) if args.out else repo / 'skills' / 'router' / 'registry.json'

# ---------- 1. Install the 9 original skills ----------
originals = {
    'rsi-loop': ('Daily RSI loop', 'Work and knowledge', None),
    'self-audit': ('New-skill audit checklist', 'Work and knowledge', None),
    'anti-slop-checklist': ('Anti-slop checklist', 'Work and knowledge', None),
    'health-research-literacy': ('Health research literacy', 'Health and fitness', None),
    'academic-campus': ('College and campus workflow', 'Work and knowledge', None),
    'office-corporate': ('Office and corporate workflow', 'Work and knowledge', None),
    'fullstack-delivery': ('Full-stack delivery workflow', 'Work and knowledge', None),
    'visual-check': ('Visual Check', 'Work and knowledge',
                     'Screenshot any page or HTML file at 360, 768, and 1280 pixels plus dark mode, and report console errors, failed requests, and horizontal overflow — so design work is judged by looking at it, not by reading code.'),
    'contribute': ('Contribute back to muse-rsi', 'Work and knowledge', None),
}
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
    text = pathlib.Path(path).read_text(encoding='utf-8')
    entries = []
    current_section = None
    for line in text.splitlines():
        hm = re.match(r'^##+\s+(.+?)\s*$', line)
        if hm:
            current_section = hm.group(1)
            continue
        if line.startswith('|') and 'github.com/' in line:
            if current_section and 'Not Included' in current_section: continue
            cells = [c.strip() for c in line.strip().strip('|').split('|')]
            link = None
            for cell in cells[:2]:
                link = re.search(r'\[([^\]]+)\]\((https://github\.com/[^)]+)\)', cell)
                if link: break
            if not link: continue
            li = next(i for i, c in enumerate(cells) if link.group(0) in c)
            rest = cells[li+1:]
            entries.append({
                'name': link.group(1),
                'repo': link.group(2).replace('https://github.com/', ''),
                'url': link.group(2),
                'section': current_section,
                'stars': rest[0] if len(rest) > 0 else '',
                'skill_md': rest[1] if len(rest) > 1 else '',
                'license': rest[2] if len(rest) > 2 else '',
                'notes': rest[3] if len(rest) > 3 else (rest[2] if len(rest) > 2 else ''),
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
        in_table = True; continue
    if in_table:
        if not line.startswith('|'): break
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        if len(cells) < 3 or cells[0].startswith(':') or cells[0].startswith('---'): continue
        name = cells[0].strip('`')
        if name in ('Skill',): continue
        lumi.append({'name': name, 'purpose': cells[1], 'domain': cells[2]})
print('lumitome skills parsed:', len(lumi))

# ---------- 3. Domain keywords for routing ----------
DOMAIN_KW = {
    'Core RSI': ['core', 'agent', 'skill', 'rsi', 'spec', 'workflow'],
    'Gap Fillers': ['taste', 'design', 'designed', 'generic', 'slop', 'anti-slop', 'video', 'memory', 'seo', 'browser', 'presentation', 'accessibility', 'tdd', 'indonesian', 'redesign', 'landing', 'ui', 'polish', 'unslop'],
    'DevOps & Infra': ['terraform', 'kubernetes', 'k8s', 'docker', 'deploy', 'ci', 'cd', 'aws', 'cloud', 'observability', 'sre', 'infrastructure', 'production', 'helm'],
    'College & Academic': ['thesis', 'paper', 'academic', 'citation', 'zotero', 'skripsi', 'tesis', 'journal', 'literature', 'research paper', 'dissertation', 'campus', 'study'],
    'Full-Stack Development': ['full-stack', 'fullstack', 'frontend', 'react', 'nextjs', 'next.js', 'typescript', 'api', 'testing', 'qa', 'playwright', 'cypress'],
    'Office & Corporate': ['email', 'spreadsheet', 'excel', 'powerpoint', 'ppt', 'outlook', 'meeting', 'office', 'corporate', 'trade', 'invoice', 'document'],
    'Research': ['research', 'deep research', 'paper', 'literature review', 'prisma', 'systematic review', 'arxiv'],
    'Health & Medical': ['health', 'medical', 'clinical', 'fhir', 'biomedical', 'genomics', 'healthcare', 'medicine', 'patient', 'literature', 'evidence'],
    'Video': ['video', 'animation', 'motion', 'remotion', 'gsap'],
    'Defensive Security': ['security', 'audit', 'owasp', 'secret', 'leak', 'vulnerability'],
    'Design & 3D': ['design', 'blender', '3d', 'logo', 'ui', 'ux'],
    'Trading (Research Only)': ['trading', 'quant', 'backtest', 'finance'],
    'Research, Documents & Voice': ['research', 'document', 'transcription', 'voice', 'crawl', 'markdown'],
    'Writing & Language (ID)': ['writing', 'indonesian', 'naskah', 'humanizer'],
    'Finance & Business (ID)': ['finance', 'accounting', 'akuntansi', 'pajak', 'umkm'],
    'Agent & Orchestration': ['agent', 'orchestration', 'subagent', 'mcp', 'eval'],
    'Design & Media': ['design', 'media', 'banner', 'logo', 'diagram', 'html'],
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
    if 'tier 2' in s: return 'Video'
    if 'tier 3' in s: return 'Defensive Security'
    if 'tier 4' in s: return 'Research, Documents & Voice'
    if 'tier 5' in s: return 'Design & 3D'
    if 'tier 6' in s: return 'Trading (Research Only)'
    return section or 'Other'

registry = {'version': 1, 'source_repo': 'fahmi0812/muse-rsi', 'verified': '2026-11-20',
            'counts': {}, 'skills': []}
for e in listed:
    domain = section_domain(e['section'])
    kws = set(DOMAIN_KW.get(domain, []))
    for w in re.split(r'[^a-z0-9]+', e['name'].lower()):
        if len(w) > 2: kws.add(w)
    tier = 'reference' if (e['section'] or '').startswith('Tier ') and 'Tier 1' not in (e['section'] or '') else 'core'
    registry['skills'].append({
        'name': e['name'], 'type': 'listed', 'tier': tier, 'domain': domain,
        'repo': e['repo'], 'url': e['url'], 'stars': e['stars'],
        'skill_md': e['skill_md'], 'license': e['license'],
        'notes': e['notes'], 'keywords': sorted(kws),
    })
ORIGINAL_DOMAINS = {
    'rsi-loop': 'Core RSI',
    'self-audit': 'Core RSI',
    'anti-slop-checklist': 'Gap Fillers',
    'health-research-literacy': 'Health & Medical',
    'academic-campus': 'College & Academic',
    'office-corporate': 'Office & Corporate',
    'fullstack-delivery': 'Full-Stack Development',
    'visual-check': 'Core RSI',
    'contribute': 'Core RSI',
}
for name, (title, category, _desc) in originals.items():
    od = ORIGINAL_DOMAINS[name]
    kws = set(DOMAIN_KW.get(od, [])) | set(re.split(r'[^a-z0-9]+', (title + ' ' + name).lower())) - {''}
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
        'path': f'.opencode/skills/{l["name"]}/SKILL.md', 'license': 'MIT',
        'notes': l['purpose'], 'keywords': sorted(set(re.split(r'[^a-z0-9]+', l['name'].lower())) - {''} | set(DOMAIN_KW.get(l['domain'], []))),
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
