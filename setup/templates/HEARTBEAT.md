# HEARTBEAT.md

_Recurring checks for your heartbeat worker. Add one per line, and the next tick picks them up._

- rsi-daily-cycle: last row of decision.tsv younger than 26 hours; if not, tell the user.
- muse-rsi: remote HEAD matches the numbers in state/facts.json and CI on main is green.
- drift_check: 0 number mismatches between scenes, MEMORY.md, and the repo (run scripts/drift_check.py).
