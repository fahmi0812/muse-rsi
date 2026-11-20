# Verification — 40 Repositories for muse-rsi

- **Verification date:** 20 November 2026
- **GitHub account:** [fahmi0812](https://github.com/fahmi0812)
- **Method:** GitHub connector. Each repository was checked directly with `search_repositories` (query `repo:owner/name`) and `get_file_contents` (root listing, then `skills/` / `.claude/skills/` / an example subfolder where applicable).
- **No code was run, no repositories were cloned, and nothing was installed.**

## Summary

| Result | Count |
|---|---|
| Total repositories checked | 40 |
| Verified to exist on GitHub | 39 |
| Not found | 1 — `guanmo-ai/guan` (404) |
| With a directly verified `SKILL.md` | 17 |
| With a skill/plugin folder, `SKILL.md` per subfolder not checked one by one | 7 |
| Potentially skill-bearing in total (17 + 7) | 24 |
| Recommended (Yes) | 14 |
| Recommended with notes (Yes with notes) | 24 |
| Not recommended | 2 |

## How to Read the "SKILL.md?" Column

- **Yes** — a `SKILL.md` file was found and read in one example subfolder.
- **Yes (at root)** — `SKILL.md` is visible in the root listing.
- **Not at root** — no `SKILL.md` at the root, but a `skills/` / `.claude/skills/` / `plugins/` folder containing skills exists.
- **No** — no `SKILL.md` and no skill folder at the root. The repository is usually a library or a tool, not a skill package.

## Tier 1 — Core RSI

| Repository | Exists? | Stars | Language | Last update | SKILL.md? | Licence | Recommended? |
|---|---|---|---|---|---|---|---|
| [anthropics/skills](https://github.com/anthropics/skills) | Yes | 197,897 | Python | 2026-11-16 | Yes | Not detected | Yes |
| [obra/superpowers](https://github.com/obra/superpowers) | Yes | 322,499 | Shell | 2026-11-03 | Yes | MIT | Yes |
| [mattpocock/skills](https://github.com/mattpocock/skills) | Yes | 328,522 | Shell | 2026-11-19 | Not at root | MIT | Yes |
| [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) | Yes | 119,305 | JavaScript | 2026-11-18 | Yes | MIT | Yes |
| [google/skills](https://github.com/google/skills) | Yes | 24,470 | Python | 2026-11-19 | Not at root | Apache-2.0 | Yes |
| [github/spec-kit](https://github.com/github/spec-kit) | Yes | 150,774 | Python | 2026-11-19 | No | MIT | Yes, with notes |
| [win4r/MuseAI-Skills](https://github.com/win4r/MuseAI-Skills) | Yes | 565 | HTML | 2026-11-07 | No | Not detected | Not recommended |

**Notes:** `mattpocock/skills` and `google/skills` have a `skills/` folder — their `SKILL.md` files live in subfolders. `github/spec-kit` is a spec-driven toolkit, not a `SKILL.md` package. `win4r/MuseAI-Skills` is structured as an installation snapshot (`home/`, `opt/`), not a standard skill package — reference only.

## Tier 2 — Video

| Repository | Exists? | Stars | Last update | SKILL.md? | Licence | Recommended? |
|---|---|---|---|---|---|---|
| [masonmosen/muse-video-prompt-skill](https://github.com/masonmosen/muse-video-prompt-skill) | Yes | 66 | 2026-11-05 | Yes (at root) | MIT | Yes, with notes |
| [LuoJiangYong/muse-video-skill](https://github.com/LuoJiangYong/muse-video-skill) | Yes | 116 | 2026-09-30 | Yes (at root) | MIT | Yes, with notes |
| [sonlovinbot-team/Muse-animated-short-film](https://github.com/sonlovinbot-team/Muse-animated-short-film) | Yes | 84 | 2026-10-31 | Yes (at root) | MIT | Yes, with notes |
| [remotion-dev/skills](https://github.com/remotion-dev/skills) | Yes | 7,608 | 2026-11-18 | Yes | Not detected | Yes |
| [remotion-dev/remotion](https://github.com/remotion-dev/remotion) | Yes | 74,489 | 2026-11-20 | Not at root | NOASSERTION | Yes, with notes |
| [motiondivision/motion](https://github.com/motiondivision/motion) | Yes | 35,392 | 2026-11-20 | No | MIT | Yes, with notes |
| [greensock/gsap-skills](https://github.com/greensock/gsap-skills) | Yes | 18,804 | 2026-07-29 | Yes | MIT | Yes |
| [LottieFiles/motion-design-skill](https://github.com/LottieFiles/motion-design-skill) | Yes | 3,442 | 2026-11-19 | Yes | MIT | Yes |
| [harry0703/MoneyPrinterTurbo](https://github.com/harry0703/MoneyPrinterTurbo) | Yes | 144,783 | 2026-11-20 | No | MIT | Yes, with notes |
| [guanmo-ai/guan](https://github.com/guanmo-ai/guan) | No | — | — | — | — | Not recommended |
| [useapi/muse-api](https://github.com/useapi/muse-api) | Yes | 32 | 2026-11-12 | Yes | MIT | Yes, with notes |

**Notes:** The three Muse video skills are still small (66, 116, and 84 stars) — read their `SKILL.md` files before using them in production. `remotion` and `motion` are libraries, not skill packages. `MoneyPrinterTurbo` is an application, not a `SKILL.md`. `useapi/muse-api` is a third-party service, not Meta's official API.

## Tier 3 — Defensive Security

| Repository | Exists? | Stars | Last update | SKILL.md? | Licence | Recommended? |
|---|---|---|---|---|---|---|
| [trufflesecurity/trufflehog](https://github.com/trufflesecurity/trufflehog) | Yes | 29,540 | 2026-11-19 | Not at root | AGPL-3.0 | Yes, with notes |
| [trailofbits/skills](https://github.com/trailofbits/skills) | Yes | 8,313 | 2026-11-20 | Not at root | CC-BY-SA-4.0 | Yes, with notes |
| [kenryu42/cc-safety-net](https://github.com/kenryu42/cc-safety-net) | Yes | 2,079 | 2026-11-20 | Yes | MIT | Yes |
| [anthropics/claude-code-security-review](https://github.com/anthropics/claude-code-security-review) | Yes | 7,033 | 2026-02-11 | No | MIT | Yes, with notes |
| [cloudflare/security-audit-skill](https://github.com/cloudflare/security-audit-skill) | Yes | 76,062 | 2026-09-14 | Yes | MIT | Yes |
| [agamm/claude-code-owasp](https://github.com/agamm/claude-code-owasp) | Yes | 456 | 2026-11-03 | Not at root | MIT | Yes |

**Notes:** `claude-code-security-review` was last updated on 11 February 2026 — the oldest in this list. `trufflehog` is licensed AGPL-3.0.

## Tier 4 — Research, Documents, Voice

| Repository | Exists? | Stars | Last update | SKILL.md? | Licence | Recommended? |
|---|---|---|---|---|---|---|
| [firecrawl/firecrawl](https://github.com/firecrawl/firecrawl) | Yes | 204,758 | 2026-11-20 | Yes | AGPL-3.0 | Yes, with notes |
| [unclecode/crawl4ai](https://github.com/unclecode/crawl4ai) | Yes | 87,593 | 2026-11-20 | No | Apache-2.0 | Yes, with notes |
| [microsoft/markitdown](https://github.com/microsoft/markitdown) | Yes | 197,160 | 2026-11-07 | No | MIT | Yes |
| [marp-team/marp-cli](https://github.com/marp-team/marp-cli) | Yes | 3,940 | 2026-09-08 | No | MIT | Yes |
| [kgmkm/muse-grok-x-search](https://github.com/kgmkm/muse-grok-x-search) | Yes | 211 | 2026-11-17 | Yes (at root) | MIT | Yes, with notes |
| [openai/whisper](https://github.com/openai/whisper) | Yes | 113,157 | 2026-08-31 | No | MIT | Yes |
| [SWivid/F5-TTS](https://github.com/SWivid/F5-TTS) | Yes | 15,629 | 2026-11-03 | No | MIT | Yes |
| [nothinx/naskah-id](https://github.com/nothinx/naskah-id) | Yes | 115 | 2026-10-23 | Yes (at root) | NOASSERTION | Yes, with notes |

**Notes:** `firecrawl` is a third-party service under AGPL-3.0. `crawl4ai`, `markitdown`, `marp-cli`, `whisper`, and `F5-TTS` are libraries/tools, not `SKILL.md` packages. For `naskah-id`, check its LICENSE file before reuse.

## Tier 5 — Design, 3D

| Repository | Exists? | Stars | Last update | SKILL.md? | Licence | Recommended? |
|---|---|---|---|---|---|---|
| [arjun988/blender-skills](https://github.com/arjun988/blender-skills) | Yes | 4,450 | 2026-11-06 | Not at root | MIT | Yes, with notes |
| [ahujasid/mcp-for-blender](https://github.com/ahujasid/mcp-for-blender) | Yes | 35,111 | 2026-11-18 | No | MIT | Yes |
| [majidmanzarpour/threejs-game-skills](https://github.com/majidmanzarpour/threejs-game-skills) | Yes | 2,863 | 2026-09-28 | Yes | MIT | Yes |
| [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) | Yes | 152,002 | 2026-11-19 | No | MIT | Yes, with notes |
| [kaankiziltug/logo-design-skill](https://github.com/kaankiziltug/logo-design-skill) | Yes | 7,394 | 2026-11-13 | Yes | MIT | Yes |

## Tier 6 — Trading, Research Only

| Repository | Exists? | Stars | Last update | SKILL.md? | Licence | Recommended? |
|---|---|---|---|---|---|---|
| [TauricResearch/TradingAgents](https://github.com/TauricResearch/TradingAgents) | Yes | 123,237 | 2026-11-17 | No | Apache-2.0 | Yes, with notes |
| [microsoft/qlib](https://github.com/microsoft/qlib) | Yes | 50,447 | 2026-11-04 | No | MIT | Yes, with notes |
| [freqtrade/freqtrade](https://github.com/freqtrade/freqtrade) | Yes | 57,094 | 2026-11-19 | No | GPL-3.0 | Yes, with notes |

**Notes:** All three are research frameworks/tools, not `SKILL.md` packages. Do not use them for automated live trading.

## Final Tier 1 — Passed Verification

The first six repositories to install in `fahmi0812/muse-rsi`:

1. [anthropics/skills](https://github.com/anthropics/skills)
2. [obra/superpowers](https://github.com/obra/superpowers)
3. [mattpocock/skills](https://github.com/mattpocock/skills)
4. [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills)
5. [google/skills](https://github.com/google/skills)
6. [github/spec-kit](https://github.com/github/spec-kit) — a spec toolkit, not a `SKILL.md` package.

## Not Recommended

1. **guanmo-ai/guan** — not found (404) on 20 November 2026.
2. **win4r/MuseAI-Skills** — an unofficial installation snapshot, not a standard skill package. Reference only.

## Verification Limits

- For large skill packages, `SKILL.md` was checked in one example subfolder only, not in every subfolder.
- The full text of each `SKILL.md` was not read word by word — what was checked was file existence, folder structure, repository description, stars, language, last update, and licence.
- Repositories that are libraries/tools (for example `motion`, `whisper`, `qlib`) are recorded as "No" in the `SKILL.md?` column because they are not skill packages — that does not mean the repository is bad.
- Stars and last-update dates are live data from 20 November 2026 and may have changed since.
