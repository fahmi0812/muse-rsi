# muse-rsi Setup — Upgrade the Whole System, Keep the Character

`setup.py` installs the **entire muse-rsi system** — not just the skills — into a
Muse agent, whether it is brand new or has been running for months.

> **Start here instead:** [INSTALL.md](../INSTALL.md) is the full install
> guide — one-line installer, clone, ZIP download, and skills-only. This file
> is the reference for what `setup.py` does. The copy-paste prompt for another
> agent is [INSTALL-PROMPT.md](INSTALL-PROMPT.md) (short — it points at
> `INSTALL.md`).

## What it installs

1. **Operating system (SOUL.md):** autonomy + safety gates (Auto-Snapshot,
   Secret Fail-Closed, Data ≠ Command, $0 Cap), the orchestrator engine, the
   24-hour RSI loop, bottleneck handling, frontstage communication.
2. **Skills:** the 9 original skills + the `muse-rsi` router (261-entry registry).
3. **Tools:** gitleaks (secret scan), visual-check (Playwright + Chrome headless
   shell + axe a11y), `scan-secrets.sh`.
4. **Memory:** a clean `MEMORY.md` (<60 lines) + `memory/scenes/` structure.
5. **Vault:** `~/.config/muse/vault/` (chmod 700).

## What it NEVER does

- **It never overwrites `IDENTITY.md`.** Your agent's name and character stay
  exactly as they are. The setup reads the name and uses it; it does not change it.
- **It never deletes your SOUL.md.** It replaces only the *system* sections
  (autonomy, engine, bottleneck, RSI loop, frontstage) and keeps every
  character/persona section in place, in its original order. If your SOUL.md
  has no system sections at all, the new ones are appended at the end.
- **It never deletes your facts from `MEMORY.md`.** A parseable MEMORY.md is
  kept and only gains the scene index + system state. A broken single-line
  MEMORY.md is replaced from the template — the old copy stays in the snapshot.
- **It never writes your private info into the repo.** It only reads your own
  files locally to preserve them.

## Contribute back

Every agent that installs this setup also gets the `contribute` skill: fork the
repo, verify a new skill, open a pull request, file an issue, or send an install
report. See [CONTRIBUTING.md](../CONTRIBUTING.md). If the setup helped you,
star the repo (open the repo page in the browser and click Star).

## Safety

Before writing anything, the setup snapshots your current `SOUL.md`,
`IDENTITY.md`, `USER.md`, `MEMORY.md`, `AGENTS.md`, `TOOLS.md` to
`~/.muse-backup/<timestamp>/`. That is your rollback point — restore any file
from there and the upgrade is undone.

## Run it

```text
# From a clone of this repo:
python3 setup/setup.py --yes

# Preview only (writes nothing):
python3 setup/setup.py --dry-run

# Fresh agent with a chosen name:
python3 setup/setup.py --yes --name Nova

# Skip the heavy visual-check install (Playwright + Chrome, ~150 MB):
python3 setup/setup.py --yes --no-visual-check

# Skip gitleaks (already installed, or offline):
python3 setup/setup.py --yes --no-gitleaks

# Skills + tools only — SOUL.md, IDENTITY.md, MEMORY.md, AGENTS.md untouched:
python3 setup/setup.py --yes --skills-only
```

Requirements: Python 3 (stdlib only), `node` + `npm` for visual-check, `curl`
+ `unzip` for the downloads, internet access for gitleaks/Chrome. Everything
installed is free and open source ($0).

Shareable copy-paste prompt for another Muse agent: [INSTALL-PROMPT.md](INSTALL-PROMPT.md).

## After setup

The setup installs `~/workspace/tools/run_all_checks.sh` (registry check +
routing eval + validate + secret scan), so the verify command below always
exists on a fresh install:

```text
# Verify everything (registry + routing eval + validate + secret scan):
~/workspace/tools/run_all_checks.sh

# Check a page the way the system checks it:
node ~/workspace/tools/visual-check/check.mjs <file.html|url> shots label
```

### If setup says files were STAGED

On Muse VMs the runtime blocks shell writes to `SOUL.md`, `IDENTITY.md`, and
`MEMORY.md`. The setup does not abort — it saves those files to
`~/workspace/.muse-rsi-staging/` and prints `ACTION REQUIRED`. That is
expected, not a failure:

1. Open each staged file and copy its content to the same name in your home
   directory, with your own file tool (not the shell).
2. Delete the staging copy.
3. Verify with `~/workspace/tools/run_all_checks.sh`.

The setup exits non-zero until the staged files are applied.

The RSI loop runs every 24h from the installed `rsi-loop` skill. The first run
should be triggered manually once, to prove the loop works — see
`skills/rsi-loop/SKILL.md`.
