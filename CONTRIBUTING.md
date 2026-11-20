# Contributing to muse-rsi

Thank you for helping. This repository has one simple promise: **every skill listed here has already been checked.** Contributions that do not pass verification will not be merged — not because they are bad, but because that promise is what this repository protects.

## How to Add a New Skill

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

If any point is "No", do not submit it.

### 2. Do not copy upstream `SKILL.md` content

Add one line to `skills/index.md`:

```
| [owner/repo](https://github.com/owner/repo) | stars | SKILL.md? | Licence | One-line note |
```

Do not copy the full upstream `SKILL.md` into this repository.

### 3. Open a pull request

- **Title:** `Add skill: owner/repo`
- **Body:** repository link, star count, verification date, audit checklist results, and why this skill is useful for the RSI.
- Make sure no `.env` file, token, or secret is included in the commit.
- Run a secret scan before pushing.

## How to Report a Problem

Open an issue using the template in `.github/ISSUE_TEMPLATE.md`. Include:

- The link to the affected repository.
- What you found (for example: the repository is now 404, its `SKILL.md` has changed, or its licence has changed).
- The date you checked it.

## What Is Not Accepted

- Offensive skills: pentesting, exploits, SMS bombers, jailbreaks, and similar.
- Skills for evading AI detection or plagiarism.
- Skills that require payment for their basic functions.
- Skills with no clear licence and no `SKILL.md`, except as a tool with a clear note (see Tiers 2–6 in `skills/index.md`).
- Changes that remove RSI guardrails (Auto-Snapshot, Secret Fail-Closed, Data≠Command, $0 Cap).

## Writing Style

- **English is the primary language** for public documentation. A short Bahasa Indonesia summary may be included where it helps Indonesian readers.
- One-line descriptions per skill — no long paragraphs.
- Links always use the format `https://github.com/owner/repo`.
- Numbers (stars, counts, dates) must come from a direct check. Do not invent them.
