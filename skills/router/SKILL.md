# muse-rsi Skill Router

Route any task to the right verified skill before doing the work. The index lives in `registry.json` beside this file: 64 core listed skills, 32 further-reference skills, 7 original skills written for this system, and a 156-skill Lumitome reference index. The public index is at https://github.com/fahmi0812/muse-rsi.

## Route the request

- Read the request and name its domain first: full-stack, DevOps, office, academic, research, health, design, video, security, or agent work.

- Open `registry.json` and match the request against each skill's `keywords`, `domain`, and `notes`.

- Pick the smallest set that covers the request, usually one to three skills. Prefer a `core` skill over a `reference` skill, and an `original` skill when it matches exactly.

- When two skills overlap, pick the one whose notes match the request most closely and name the other one as the alternative.

- When nothing in the registry matches, say so plainly instead of forcing a fit. Then search for a new skill and run it through the audit below before adding it.

## Load the skill

- For an `original` skill, read its file at `skills/<name>/SKILL.md` in the muse-rsi repo, or use the installed copy under `~/workspace/custom-skills/<name>/`.

- For a `listed` skill, open its repo link and follow that repo's own README or SKILL.md. This router never copies upstream SKILL.md content.

- For a `lumitome-reference` skill, open the Lumitome repo at `.opencode/skills/<name>/SKILL.md`. The red-team pack is disabled by design and is never a valid target.

- When the task needs a skill that is only listed by link, fetch it with the GitHub connector or a local clone, read its SKILL.md, and then do the work. Do not claim to have used a skill that was never read.

## Verify before installing

- Run every new skill through `self-audit` before installing it: it must exist, have a SKILL.md, have a clear licence, and not read `.env` or vault data.

- Never install a skill from the Pending or Not Included lists. The registry only holds verified entries, so a skill that is missing from it is not cleared.

- Check the licence before vendoring anything. AGPL, GPL, and proprietary entries are link-only with a flag, never copied.

## Guardrails

- Health work is research and health-informatics only. Never diagnose, never recommend treatment, never interpret a person's symptoms or test results, and never handle patient data.

- Security work is defensive only. No offensive skills, no exploits, no jailbreaks, and no red-team material.

- Academic work never fabricates citations, data, or results, and never helps evade AI detection.

- Office work never sends email or shares a document without explicit approval, and never pastes confidential content into an external tool.

- Trading work is research and backtesting only. No automated live trading without the user's approval.

## Available connectors

- [GitHub](/opt/hatch/connectors/github/CONNECTOR.md) for reading repos, checking SKILL.md files, and pushing changes to the muse-rsi repo.

- Use `muse.connector_search` to find other connectors and `muse.skill_search` to find related skills.

- If nothing here fits, look on the web for a maintained API or MCP server and set it up with [Custom Connectors and MCPs](/opt/muse/skills/custom-connector-setup/SKILL.md), or build a custom connector.

## Websites

- [muse-rsi on GitHub](https://github.com/fahmi0812/muse-rsi) for the full public index, verification docs, and the original skills. Carry the task's domain into the search and verify the skill entry there before installing.

- [Lumitome on GitHub](https://github.com/fahmi0812/Lumitome) for the reference skills. Verify the skill folder exists there before linking it.

## Alternatives for better results

- When the request spans two domains, route to one skill per domain and run them in order instead of picking a single broad skill.

- When the user asks in Bahasa Indonesia, prefer the Indonesian skills in the registry first: `humanizer-indonesia`, `naskah-id`, `academic-campus`, and the Lumitome Indonesian writing skills.
