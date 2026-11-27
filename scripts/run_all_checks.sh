#!/bin/bash
# run_all_checks.sh — All muse-rsi checks in one command (v3.0 G1).
# Stops at the first HARD failure (set -e). Run after any registry, skill,
# or repo change, and before any public push.
# Hard steps (must all pass): generator --check, routing eval top-3,
# validate registry, canary, manifest --verify, gen_facts --check,
# drift_check, scorecard tests, cycle read-only audit, secret scan.
# Informational step (reported, never fails the suite): routing eval
# --strict top-1 — a metric (baseline 114/114, 24 Nov 2026), not a
# pass/fail gate; the DECIDE gate uses its matched-metric delta instead.
# Usage: run_all_checks.sh [path-to-repo-clone]  (default ~/muse-rsi)
# Installed by setup.py to ~/workspace/tools/run_all_checks.sh.
set -e

REPO="${1:-}"
if [ -z "$REPO" ]; then
  if [ -d "$HOME/muse-rsi" ]; then REPO="$HOME/muse-rsi";
  elif [ -d "$HOME/workspace/muse-rsi" ]; then REPO="$HOME/workspace/muse-rsi";
  else REPO="$HOME/muse-rsi"; fi
fi
TOOLS="$HOME/workspace/tools"

echo "== 1/10 registry generator --check =="
python3 "$REPO/scripts/generate_registry.py" --check --repo "$REPO"

echo "== 2/10 routing eval (top-3) =="
python3 "$REPO/scripts/eval_routing.py" --registry "$REPO/skills/router/registry.json"

echo "== 3/10 routing eval --strict top-1 (informational metric) =="
python3 "$REPO/scripts/eval_routing.py" --registry "$REPO/skills/router/registry.json" --strict || echo "NOTE: --strict is a metric, not a hard gate (baseline 114/114). See docs/scorecard.md."

echo "== 4/10 validate registry =="
python3 "$REPO/scripts/validate_registry.py"

echo "== 5/10 canary =="
python3 "$REPO/scripts/test_canary.py" --registry "$REPO/skills/router/registry.json"

echo "== 6/10 eval manifest --verify =="
python3 "$REPO/scripts/eval_manifest.py" --verify

echo "== 7/10 gen_facts --check =="
python3 "$REPO/scripts/gen_facts.py" --check --repo "$REPO"

echo "== 8/10 drift_check =="
python3 "$REPO/scripts/drift_check.py" --repo "$REPO"

echo "== 9/10 unit tests + cycle read-only audit + verifier self-test =="
python3 "$REPO/tests/test_scorecard.py"
python3 "$REPO/tests/test_gen_facts.py"
python3 "$REPO/tests/test_autonomy_gate.py"
python3 "$REPO/tests/test_trust.py"
python3 "$REPO/tests/test_setup_find_name.py"
python3 "$REPO/tests/test_budget_lifecycle.py"
python3 "$REPO/scripts/rsi_cycle.py" check-readonly
# v3.1: every guard must still reject known-bad input (anti-weakening).
python3 "$REPO/scripts/verifier_selftest.py" --repo "$REPO"

echo "== 10/10 secret scan =="
if [ -x "$REPO/tools/scan-secrets.sh" ]; then
  "$REPO/tools/scan-secrets.sh" "$REPO"
elif [ -x "$TOOLS/scan-secrets.sh" ]; then
  "$TOOLS/scan-secrets.sh" "$REPO"
else
  echo "ERROR: scan-secrets.sh not found (looked in $REPO/tools/ and $TOOLS/). Install gitleaks via setup.py first."
  exit 2
fi

echo "ALL CHECKS PASSED"
