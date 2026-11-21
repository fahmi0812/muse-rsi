# MEMORY.md — Hot Core & Scene Index

<!-- HARD LIMIT: <60 lines. Read this file always; open MAX 1 scene file per task. NEVER store passwords/tokens/.env contents here. -->

## Core Facts

- **User:** (fill in the user's name).
- **Mode:** Full-Autonomous Orchestrator (0% confirmation for local work) + Friendly, simple frontstage.
- **Vault:** `~/.config/muse/vault/` (chmod 700, gitignored) + persistent browser auth profiles.
- **Privacy:** Never mention the user's private details (such as their location) in public docs, published repos, or replies. Keep timezone only for scheduling.

## Scene Index (read only 1 file that matches the task)

| Scene / Need | File Path | When to Read |
|---|---|---|
| Work environment, OS, server, stack | `memory/scenes/env-stack.md` | Coding, Linux, deploy, network tasks |
| Active projects & repo rules | `memory/scenes/projects.md` | When touching the user's projects |
| Accounts, login status & vault map | `memory/scenes/auth-map.md` | When web/Gmail/API access is needed (map only, no secrets) |
| Skill registry & installed tools | `memory/scenes/skills.md` | When delegating tools or running the 24h audit |
| Bottleneck queue & daily fixes | `memory/scenes/bottlenecks.md` | During the 24h cron or when blocked |
| Changelog & daily notes | `memory/scenes/changelog.md`, daily log `memory/YYYY-MM-DD.md` | Weekly audit or resuming a task |

## Pre-Authorized Fast Lanes

- All local workspace actions, git branch/commit/push to the user's repos, background workers, and audit/install of GitHub skills that pass the Security Gate = **auto-execute**.
- Crucial actions (deploy, migration, big refactor, publish) = approval gate: snapshot + test + secret scan first, then the runtime approval card — never auto-executed.

## System State

- **Repo:** `muse-rsi` — 96 listed (64 core + 32 reference) + 11 originals + 139 Lumitome reference = **246 registry entries**.
- **Router:** skill `muse-rsi` installed (`include_in_prompt: true`); registry at `skills/router/registry.json`.
- **Visual check:** `visual-check` installed (Playwright + Chrome headless shell in `~/workspace/tools/visual-check/`).
- **RSI loop:** NOT active until the agent creates the daily job `rsi-daily-self-improvement` (every 24h) — the setup cannot schedule it; see the setup's NEXT STEP message.
- **Secret scan:** gitleaks in `~/workspace/tools/gitleaks/`; mandatory before any public push (see skill `self-audit`).
- **Registry generator:** `scripts/generate_registry.py` in the muse-rsi repo; registry: `skills/router/registry.json`.

## Memory Hygiene

- Only long-term facts live here. New details go straight into `memory/scenes/` or the daily log `memory/YYYY-MM-DD.md`.
- Remove a bottleneck entry as soon as it is resolved.
