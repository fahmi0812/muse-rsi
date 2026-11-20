# Operations — How This Repo Is Run

Rules learned the hard way on 20 November 2026. Follow them before any push.

## Remote is truth

- The remote history (`main` on GitHub) is the source of truth for file
  **contents**. Local git SHAs will differ from remote SHAs because pushes go
  through the GitHub API (`push_files`), which creates its own commits. That
  is normal, not a bug.
- Verify content sync with the read-only mirror clone:
  `cd ~/workspace/muse-rsi-remote && git pull` then
  `diff -rq ~/workspace/muse-rsi ~/workspace/muse-rsi-remote -x .git`.
  Empty output = in sync.

## Push procedure

1. Snapshot: `~/workspace/tools/backup.sh`.
2. Run `~/workspace/tools/run_all_checks.sh` (registry check + routing eval +
   validate + secret scan). Stop on the first failure.
3. Push with the `github push-files` subcommand and a `--paths-file`
   (NUL-delimited). Never `git push` — there are no git credentials on the VM.
4. **Workflow files are special:** the GitHub App cannot write
   `.github/workflows/` via the API (403 "Resource not accessible by
   integration"). Add or change workflow files through the GitHub website
   only — never retry the same API call.
5. Verify the push by reading the commit back from GitHub (API or website),
   not by trusting the tool receipt.

## Rollback (content, not history)

History can never be rewritten from here (no force-push). To roll back a
file's content:

```text
python3 scripts/rollback_file.py <path-in-repo> --from mirror   # last remote version
python3 scripts/rollback_file.py <path-in-repo> --from backup   # latest backup tarball
```

Then run the checks and push the restore as a new commit. The local safety
branch `rsi-run-2026-11-20-backup` is a snapshot of the pre-RSI-run state.

## Router is a program

`scripts/route.py "<task>"` routes a task against the registry — the same
scoring the eval (`scripts/eval_routing.py`, 15 queries) tests. If the eval
passes, the router works. After any registry change, run the eval.

## Usage meter

There is no token meter in this harness. What is measured is the context
window: `scripts/usage_log.py --run-id ID --context-used N
--context-remaining M --duration-min N --checks PASS|FAIL --note "..."`.
Every RSI run records one entry (read the numbers from the agent's session
status at the end of the run). `scripts/usage_log.py --report` shows the
trend. Log file: `~/workspace/tools/usage-log/usage.jsonl` (VM-local).

## Browser work

Browser tasks expire after about 1 hour and cannot auto-resume. Split long
browser work into batches under 45 minutes, save progress to a file after
each batch, and resume from the file — never from memory. Record the batch
plan in `.muse/journal.md` before starting.

## Checks (one command)

```text
~/workspace/tools/run_all_checks.sh   # 4/4 must pass before any public push
```
