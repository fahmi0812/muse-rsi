# Critique — The 5 Biggest Gaps in muse-rsi

- **Critique date:** 20 November 2026
- **GitHub account:** [fahmi0812](https://github.com/fahmi0812)
- **Sources:** 384 starred repositories, the 40-repository verification, and 46 repositories from 7 posts on X.
- **Method:** GitHub connector, `search_repositories` + `get_file_contents` for `SKILL.md`. No code was run, nothing was cloned, and nothing was installed.

## Summary: The 5 Biggest Gaps (in Priority Order)

### 1. Anti-slop / design taste — EMPTY in the 40 repositories

Not one of the 40 verified repositories is an anti-slop or design-taste skill, even though the starred list contains 7 strong repositories in this area. Without them, RSI output (UI, video, writing) looks generically AI-made: the same layouts, colours, and copy every time. This is gap #1 because it is visible in KimiCharmi's work every day.

**Verified additions:** [Leonxlnx/taste-skill](https://github.com/Leonxlnx/taste-skill) (119,141 stars, `SKILL.md`: Yes), [Nutlope/hallmark](https://github.com/Nutlope/hallmark) (58,330 stars, `SKILL.md`: Yes), [heydamir/unslop](https://github.com/heydamir/unslop) (18,976 stars, `SKILL.md`: Yes), [miqdadbadjuber/anti-slop](https://github.com/miqdadbadjuber/anti-slop) (9,655 stars, `SKILL.md`: Yes — reserve).

### 2. Long-term memory + self-evolving skills — EMPTY in the 40 repositories

The RSI runs every 24 hours and must learn from previous runs, but the 40 repositories contain no memory layer and no self-evolution skill. Without memory, each RSI run starts from zero; without an evaluate → fix → test → save / roll back mechanism, the skills in `muse-rsi` will not truly improve — they will only grow in number.

**Verified additions:** [mem0ai/mem0](https://github.com/mem0ai/mem0) (69,274 stars, `SKILL.md` in an integration folder), [volcengine/OpenViking](https://github.com/volcengine/OpenViking) (42,518 stars, `SKILL.md`: Yes), [alchaincyf/darwin-skill](https://github.com/alchaincyf/darwin-skill) (7,005 stars, `SKILL.md` at root).

### 3. Testing / QA / accessibility — EMPTY in the 40 repositories

There is no dedicated testing skill in the 40 repositories and no accessibility (WCAG) skill at all. Even in the starred list, only Playwright exists — as a testing library, not a skill. As a result, the RSI could ship code, UI, and video without anything testing it, and without anything checking accessibility.

**Verified additions:** [plugin87/ux-ui-agent-skills](https://github.com/plugin87/ux-ui-agent-skills) (3,209 stars, `SKILL.md`: Yes — WCAG 2.2 AA–AAA), [evanklem/evanflow](https://github.com/evanklem/evanflow) (419 stars, `SKILL.md`: Yes — TDD, 16 skills; small repo, read it first), [microsoft/playwright](https://github.com/microsoft/playwright) (100,645 stars, `SKILL.md`: Yes — reserve).

### 4. Bahasa Indonesia + natural writing — ALMOST EMPTY in the 40 repositories

Of the 40 repositories, only `nothinx/naskah-id` is specific to Bahasa Indonesia. There is no Indonesian humanizer and no natural-writing skill, even though Fahmi works in Bahasa Indonesia and KimiCharmi must speak simply and naturally. Without this, Indonesian output from the RSI will sound stiff and machine-like.

**Verified additions:** [adhiprib/humanizer-indonesia](https://github.com/adhiprib/humanizer-indonesia) (346 stars, `SKILL.md` at root — the only verified Indonesian humanizer; for fluent writing, not for evading AI detection), [blader/humanizer](https://github.com/blader/humanizer) (71,509 stars, `SKILL.md`: Yes — reserve, natural writing only), [FRCHN-GSTN/MenulisCep4t](https://github.com/FRCHN-GSTN/MenulisCep4t) (93 stars, `SKILL.md`: Yes — reserve).

### 5. Browser automation + advanced video production + presentations — EMPTY / THIN in the 40 repositories

The 40 repositories include web-crawling tools (firecrawl, crawl4ai) but no browser-agent skill. Video is represented only by small skills (66–116 stars) and Remotion; there is no complete video production system and no presentation skill.

**Verified additions:** [browser-use/browser-use](https://github.com/browser-use/browser-use) (121,585 stars, `SKILL.md`: Yes), [OpenMontageInc/OpenMontage](https://github.com/OpenMontageInc/OpenMontage) (81,870 stars, `SKILL.md`: Yes), [meta/astryx](https://github.com/meta/astryx) (31,198 stars, `SKILL.md`: Yes), [genspark-ai/genoffice](https://github.com/genspark-ai/genoffice) (12,676 stars, `SKILL.md`: Yes), [presenton/presenton](https://github.com/presenton/presenton) (11,980 stars, no `SKILL.md` — an app + API, used as a tool), [AgriciDaniel/claude-seo](https://github.com/AgriciDaniel/claude-seo) (31,050 stars, `SKILL.md`: Yes — SEO/GEO).

## The 15 Main Additions in the Core List

1. [Leonxlnx/taste-skill](https://github.com/Leonxlnx/taste-skill) — 119,141 stars
2. [browser-use/browser-use](https://github.com/browser-use/browser-use) — 121,585 stars
3. [OpenMontageInc/OpenMontage](https://github.com/OpenMontageInc/OpenMontage) — 81,870 stars
4. [mem0ai/mem0](https://github.com/mem0ai/mem0) — 69,274 stars
5. [Nutlope/hallmark](https://github.com/Nutlope/hallmark) — 58,330 stars
6. [volcengine/OpenViking](https://github.com/volcengine/OpenViking) — 42,518 stars
7. [AgriciDaniel/claude-seo](https://github.com/AgriciDaniel/claude-seo) — 31,050 stars
8. [meta/astryx](https://github.com/meta/astryx) — 31,198 stars
9. [heydamir/unslop](https://github.com/heydamir/unslop) — 18,976 stars
10. [genspark-ai/genoffice](https://github.com/genspark-ai/genoffice) — 12,676 stars
11. [presenton/presenton](https://github.com/presenton/presenton) — 11,980 stars
12. [alchaincyf/darwin-skill](https://github.com/alchaincyf/darwin-skill) — 7,005 stars
13. [plugin87/ux-ui-agent-skills](https://github.com/plugin87/ux-ui-agent-skills) — 3,209 stars
14. [evanklem/evanflow](https://github.com/evanklem/evanflow) — 419 stars
15. [adhiprib/humanizer-indonesia](https://github.com/adhiprib/humanizer-indonesia) — 346 stars

A total of 41 candidate additions were checked; all were verified to exist on GitHub. There are 24 further verified reserves for a second wave — see the full critique source file used to prepare this document.

## Revised Tiers

### Tier 1 — Unchanged (6 repositories)

anthropics/skills, obra/superpowers, mattpocock/skills, addyosmani/agent-skills, google/skills, github/spec-kit (a spec toolkit, not a `SKILL.md` package).

### Tiers 2–6 — Revised

- **Tier 2, Video:** the 10 verified repositories from the 40 remain (guanmo-ai/guan stays excluded), plus OpenMontage, astryx, hyperframes, AI-Youtube-Shorts-Generator, and video-use.
- **Tier 3, Defensive security:** the 6 repositories remain; `claude-code-security-review` (last updated 11 February 2026) is flagged as needing an active companion. No offensive additions.
- **Tier 4, Research / documents / voice:** the 8 repositories remain, plus presenton (as a tool), genoffice, and the Indonesian humanizer.
- **Tier 5, Design / 3D:** the 5 repositories remain, plus the anti-slop / taste additions (gap #1).
- **Tier 6, Trading research:** the 3 repositories remain, plus day-trader-skill as a skill. Live trading remains forbidden.

## Still Not Recommended

1. [guanmo-ai/guan](https://github.com/guanmo-ai/guan) — not found (404).
2. [win4r/MuseAI-Skills](https://github.com/win4r/MuseAI-Skills) — unofficial installation snapshot.
3. [Turnitout-Humanizer](https://github.com/AhmadHassan-BTed/Turnitout-Humanizer) — no `SKILL.md`; description is "Plagiarism Remover & Similarity Evader".
4. All offensive skills (pentesting, exploits, SMS bombers, jailbreaks) — still excluded from `muse-rsi`.
5. [useapi/muse-api](https://github.com/useapi/muse-api) — still "with notes": a third-party service, not Meta's official API.

## Critique Limits

- `SKILL.md` was checked by path matching via the GitHub connector; for large packages, existence was checked in subfolders, not the full text of every `SKILL.md` word by word.
- Licences for new candidates were not detected via the search API in this check — check each repository's LICENSE file before reuse in `muse-rsi`.
- Stars and last-update dates are live data from 20 November 2026 and may have changed since.
