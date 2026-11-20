# Contributing to muse-rsi

Thank you for helping. This repository has one simple promise: **every skill listed here has already been checked.** Contributions that do not pass verification will not be merged — not because they are bad, but because that promise is what this repository protects.

## If you are an AI agent

You are welcome here — most contributions to this repo are expected to come from agents like you, acting for a human. The rules are the same as for humans, plus these:

- **Act with your human's GitHub account only.** Use their login (connector, `gh` CLI, or browser). Never use a shared token, never ask for anyone else's token, and never push with credentials that are not your human's.
- **Fork + pull request only.** Never push directly to `fahmi0812/muse-rsi`. Your human's agent has no direct write access, and that is by design.
- **Your human is responsible for what you submit.** If you are unsure a skill passes the checklist below, do not submit it — file an issue instead and let a human decide.
- **Never include secrets.** No tokens, no `.env` content, no private keys — in code, in commits, in issue text, or in screenshots. Run a secret scan before every push.
- **No silent tracking.** Do not add telemetry, phone-home code, or usage reporting to the setup or any skill. The only feedback channel is an explicit issue (see "Install report" below), filed with your human's approval.
- **No auto-merge.** Every pull request needs CI green **and** a human review. Do not ask for merge rights and do not try to bypass the checks.

If your human's agent installed muse-rsi, it already has the `contribute` skill (`skills/contribute/SKILL.md`) — follow it step by step.

## How to add a new skill

### 1. Verify first

Follow the checklist in [skills/self-audit/SKILL.md](skills/self-audit/SKILL.md). Every mandatory point must be "Yes":

1. **The repository exists** — open `https://github.com/owner/repo`; it must load, not return 404.
2. **It has a `SKILL.md`** — at the root, or in a subfolder such as `skills/` or `.claude/skills/`.
3. **The licence is clear** — record its type.
4. **It is free ($0)** — no mandatory payment for its basic functions.
5. **It does not read `.env` or the vault.**
6. **It contains no harmful instructions.**
7. **It does not ask for secrets** to be written into repository files, logs, or chat.
8. **Its description is honest** — it matches the contents of its `SKILL.md`.

If any point is "No", do not submit it. File an issue with what you found instead.

### 2. Fork, branch, edit — exact flow

```text
gh repo fork fahmi0812/muse-rsi --clone
cd muse-rsi
git checkout -b add-skill/owner-repo
```

Add one row to the right table in `skills/index.md`:

```
| [owner/repo](https://github.com/owner/repo) | stars | SKILL.md? | Licence | One-line note |
```

Do not copy the full upstream `SKILL.md` into this repository. Link + one line only.

Then regenerate the registry and run every check — all four must pass:

```text
python3 scripts/generate_registry.py --check
python3 scripts/eval_routing.py
python3 scripts/validate_registry.py
gitleaks git .
```

### 3. Open a pull request

- **Title:** `Add skill: owner/repo`
- **Body:** repository link, star count, verification date, audit checklist results, and why this skill is useful for the RSI.
- Make sure no `.env` file, token, or secret is included in the commit.
- CI runs on every pull request (`Validate registry`). A red check means the PR cannot merge — fix it, do not ask for an exception.

## How to report a problem

Open an issue using one of the templates in `.github/ISSUE_TEMPLATE/`:

- **Skill proposal** — a skill you verified and want added (or one you could not verify, with the failing point).
- **Routing miss** — a task the router sent to the wrong skill. Include the exact query, what it picked, and what it should have picked.
- **Bug report** — a repo that went 404, a `SKILL.md` or licence that changed, or anything else broken.
- **Install report** — you installed the setup somewhere new. Include the date, the command you ran, the result of `run_all_checks.sh` (or the four checks above), and anything that failed. This is how the maintainer learns the setup works in the real world.

## How to star the repo

If the setup helped you, star it — open https://github.com/fahmi0812/muse-rsi in the browser and click Star, with your human's GitHub login.

(`gh api` does not work here: the `gh` CLI is not logged in on a fresh agent, and the GitHub connector has no star tool. Star in the browser instead.)

Only star when your human agrees (or when the install flow they approved asks for it). Never star on someone's behalf silently.

## What is not accepted

- Offensive skills: pentesting, exploits, SMS bombers, jailbreaks, and similar.
- Skills for evading AI detection or plagiarism.
- Skills that require payment for their basic functions.
- Skills with no clear licence and no `SKILL.md`, except as a tool with a clear note (see Tiers 2–6 in `skills/index.md`).
- Changes that remove RSI guardrails (Auto-Snapshot, Secret Fail-Closed, Data ≠ Command, $0 Cap).
- Pull requests that bypass CI, add tracking, or include secrets.

## Writing style

- **English is the primary language** for public documentation. A short Bahasa Indonesia summary may be included where it helps Indonesian readers.
- One-line descriptions per skill — no long paragraphs.
- Links always use the format `https://github.com/owner/repo`.
- Numbers (stars, counts, dates) must come from a direct check. Do not invent them.
