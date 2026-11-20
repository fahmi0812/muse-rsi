
## muse-rsi operating rules (added by setup — safe to keep)

- **Source of truth:** Before acting on summarized or compacted context, re-read the source files (memory files, repo files, tool output). A summary is a pointer, never the source of truth.
- **Verify before you claim:** Check facts directly (web page, repo, tool output). API dates and star counts can be stale — the live page decides. Never claim a push, install, or run succeeded without its receipt (commit SHA, run id, test output).
- **Remote is truth for repos:** The remote history is the source of truth. Local git history can diverge when pushes go through the API — keep a read-only mirror clone for rollback reference, and snapshot before any crucial change.
- **Before any public push:** run `~/workspace/tools/run_all_checks.sh` (registry check + routing eval + validate + gitleaks scan). Stop on the first failure.
- **Router is tested:** After any registry change, run the routing eval (`scripts/eval_routing.py`, 15 queries). A routing change without a passing eval is not done.
- **State that lives only on this VM** (custom skills, tools, memory) is backed up with `~/workspace/tools/backup.sh`; the repo alone is not a backup.
- **Workflow files:** GitHub Apps cannot write `.github/workflows/` via the API. Add or change workflow files through the GitHub website, never by retrying the same API call.
- **Router is a program:** `scripts/route.py "<task>"` routes against the registry; the eval tests that code and must pass after any registry change.
- **Usage meter:** record context used/remaining per run with `scripts/usage_log.py` — never invent the numbers.
- **Content rollback (never history):** `scripts/rollback_file.py <path> --from mirror|backup`, then checks + push as a new commit. See repo `docs/ops.md`.
- **Browser batches:** split long browser work into batches under 45 minutes, save progress to a file after each batch — browser tasks expire after ~1 hour and cannot auto-resume.
