#!/bin/bash
# scan-secrets.sh — Secret Fail-Closed gate. MUST run before any public push.
# Usage:
#   scan-secrets.sh <dir>            # scan working tree files
#   scan-secrets.sh --history <repo> # scan git history too
# Exit 0 = clean, 1 = leaks found (HALT the push), 2 = usage error.
set -u
GITLEAKS="$HOME/workspace/tools/gitleaks/gitleaks"
[ -x "$GITLEAKS" ] || { echo "gitleaks not found at $GITLEAKS"; exit 2; }
if [ "${1:-}" = "--history" ]; then
  [ -n "${2:-}" ] || { echo "Usage: $0 --history <repo>"; exit 2; }
  "$GITLEAKS" git --no-banner "$2"
  code=$?
else
  [ -n "${1:-}" ] || { echo "Usage: $0 <dir> | $0 --history <repo>"; exit 2; }
  "$GITLEAKS" dir --no-banner "$1"
  code=$?
fi
if [ "$code" -eq 0 ]; then echo "SECRET SCAN CLEAN: $*"
else echo "SECRET SCAN FAILED (exit $code): leaks found — HALT, do not push."; fi
exit "$code"
