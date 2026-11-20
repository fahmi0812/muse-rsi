#!/bin/bash
# run_all_checks.sh — All muse-rsi checks in one command.
# Stops at the first failure (set -e). Run after any registry, skill, or
# repo change, and before any public push.
# Order: generator matches stored registry -> routing eval -> registry
# structure validation -> secret scan.
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

echo "== 1/4 registry generator --check =="
python3 "$REPO/scripts/generate_registry.py" --check --repo "$REPO"

echo "== 2/4 routing eval =="
python3 "$REPO/scripts/eval_routing.py" --registry "$REPO/skills/router/registry.json"

echo "== 3/4 validate registry =="
python3 "$REPO/scripts/validate_registry.py"

echo "== 4/4 secret scan =="
"$TOOLS/scan-secrets.sh" "$REPO"

echo "ALL CHECKS PASSED"
