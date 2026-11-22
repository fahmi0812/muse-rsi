# TOOLS.md — Local Notes

Short, durable notes that make external tools work reliably in this
particular setup: device nicknames, host aliases, preferred voices, and
environment-specific quirks. Skills describe how tools work in general; this
file holds only what is unique here.

## Verified quirks (muse-rsi v3.0)

- gitleaks: use the binary installed by setup in `~/workspace/tools/gitleaks/`,
  always with `--redact`. Mandatory before any public push.
- Chrome headless shell: at
  `~/workspace/tools/visual-check/chrome-headless-shell-linux64/chrome-headless-shell`
  (pinned build 159.0.8154.6). The VM's puppeteer Chrome path is gone —
  do not use it.
- `/tmp` is only 512 MB: sandboxes, builds, and large downloads go to
  `~/workspace/sandboxes/`, not `/tmp`.
- git push over HTTPS on this VM has no credentials: push to GitHub with
  the GitHub connector `push_files`, not `git push` HTTPS.
- Files under `.github/workflows/` cannot be written through the GitHub
  App API (rejected 403): the user changes them through the GitHub web UI.
- SOUL.md / IDENTITY.md / MEMORY.md / AGENTS.md cannot be written from
  the shell on this VM: setup stages them to
  `~/workspace/.muse-rsi-staging/` and exits 20; apply them with the
  file tool.
- Browser tasks expire after ~1 hour: split browser work into batches
  under 45 minutes, save progress to a file after each batch.
- Router is a program: `scripts/route.py "<task>"` in the muse-rsi repo;
  routing eval must pass every time the registry changes. Repo numbers
  (registry total, eval score) live in `state/facts.json` — read them
  there, never copy them here by hand.
