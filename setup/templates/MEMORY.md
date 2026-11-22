# MEMORY.md — Hot Core & Scene Index

<!-- HARD LIMIT: 8 KB. Read this file always; open MAX 1 scene file per task. NEVER store passwords/tokens/.env contents here. Numbers live in state/facts.json (repo) — never copy them here by hand. -->

## Core Facts

- **User:** (fill in the user's name).
- **Mode:** Full-Autonomous Orchestrator (A0–A1 without asking; A2–A5 only through their gate — see SOUL §1) + Friendly, simple frontstage.
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

- Maximum autonomy (v3.1): act, merge, report — the user reviews after the fact. Never ask for A0–A4.
- Local workspace, background workers, root files (snapshot + T2), and GitHub skills that pass the Security Gate = **auto-execute** (A0–A3).
- Repo changes = push to branch `rsi/<run_id>`; the auto-merge workflow merges when CI is green (A2), or after the 24 h veto window for verifier/engine changes (A4). Never push straight to main.
- Only the hard core waits for the user, collected in one daily digest (A5): loosening the Safety Envelope, money or paid APIs, messages to other people, production deploy, publishing outside the user's own repo, vault/API keys, permanent delete.

## System State (live, not static text)

- **Repo numbers:** read `state/facts.json` in the muse-rsi repo (registry total, eval top-3/top-1, canary, HEAD). Never hand-copy numbers into this file — `drift_check.py` flags any mismatch.
- **RSI loop status:** read the heartbeat, not this file — `HEARTBEAT.md` check `rsi-daily-cycle` (last `decision.tsv` row <26h old) tells whether the loop is alive. Setup cannot schedule the loop; the agent creates the daily job `rsi-daily-self-improvement` (see the setup's NEXT STEP message).
- **Router:** skill `muse-rsi` installed (`include_in_prompt: true`); registry at `skills/router/registry.json`; generator `scripts/generate_registry.py`.
- **Visual check:** `visual-check` installed (Playwright + Chrome headless shell in `~/workspace/tools/visual-check/`).
- **Secret scan:** gitleaks in `~/workspace/tools/gitleaks/`; mandatory before any public push (see skill `self-audit`).

## Memory Hygiene

- Only long-term facts live here. New details go straight into `memory/scenes/` or the daily log `memory/YYYY-MM-DD.md`.
- Remove a bottleneck entry as soon as it is resolved.
