#!/bin/bash
# muse-rsi one-line installer.
# Installs the whole muse-rsi system (skills + router + tools + operating
# system) into a Muse agent, new or long-running. The agent's name and
# character are never changed.
#
# Fastest use (read this file first if you like — it is short):
#   curl -sSL https://raw.githubusercontent.com/fahmi0812/muse-rsi/main/install.sh | bash
#
# Or download it first, then run it:
#   curl -sSL -o muse-rsi-install.sh https://raw.githubusercontent.com/fahmi0812/muse-rsi/main/install.sh
#   bash muse-rsi-install.sh [--no-visual-check] [--no-gitleaks] [--skills-only]
#
# Env: MUSE_RSI_DIR (default ~/muse-rsi), MUSE_RSI_USE_ZIP=1 (skip git,
# download the repo ZIP instead).
#   MUSE_RSI_FORCE_REPLACE=1: allow replacing a non-empty MUSE_RSI_DIR that
#   is not a muse-rsi checkout (default: refuse — this script never deletes
#   user data on its own).
set -e

REPO_DIR="${MUSE_RSI_DIR:-$HOME/muse-rsi}"
REPO_URL="https://github.com/fahmi0812/muse-rsi"

# Never delete these, whatever the user sets MUSE_RSI_DIR to.
case "$REPO_DIR" in
  "/"|"$HOME"|"$HOME/workspace"|"$HOME/"|"$HOME/workspace/"|"/tmp"|"/tmp/")
    echo "MUSE_RSI_DIR must not be $REPO_DIR — pick an empty or new directory (e.g. ~/muse-rsi)."
    exit 1
    ;;
esac

command -v python3 >/dev/null 2>&1 || { echo "python3 not found — install Python 3 first."; exit 1; }

if [ -d "$REPO_DIR/setup" ]; then
  if [ -d "$REPO_DIR/.git" ]; then
    echo "Updating existing copy at $REPO_DIR ..."
    git -C "$REPO_DIR" pull --ff-only || echo "WARNING: git pull failed — continuing with the copy already at $REPO_DIR."
  else
    echo "Using existing copy at $REPO_DIR (not a git checkout — no update attempted)."
  fi
elif [ -z "$MUSE_RSI_USE_ZIP" ] && command -v git >/dev/null 2>&1; then
  echo "Cloning $REPO_URL to $REPO_DIR ..."
  git clone "$REPO_URL" "$REPO_DIR"
else
  command -v curl >/dev/null 2>&1 || { echo "Need git or curl to fetch the repo."; exit 1; }
  command -v unzip >/dev/null 2>&1 || { echo "Need git or unzip to fetch the repo."; exit 1; }
  echo "Downloading $REPO_URL as ZIP (no git found, or MUSE_RSI_USE_ZIP=1) ..."
  tmp_dir="$(mktemp -d)"
  tmp_zip="$tmp_dir/muse-rsi.zip"
  curl -sSL -o "$tmp_zip" "$REPO_URL/archive/refs/heads/main.zip"
  unzip -q -o "$tmp_zip" -d "$tmp_dir"
  if [ -e "$REPO_DIR" ]; then
    if [ -z "$(ls -A "$REPO_DIR" 2>/dev/null)" ]; then
      echo "$REPO_DIR exists but is empty — reusing it."
      rmdir "$REPO_DIR"
    elif [ -n "$MUSE_RSI_FORCE_REPLACE" ]; then
      echo "WARNING: MUSE_RSI_FORCE_REPLACE=1 — deleting non-empty $REPO_DIR (it has no setup/setup.py)."
      rm -rf "$REPO_DIR"
    else
      echo "ERROR: $REPO_DIR already exists and is not a muse-rsi checkout."
      echo "Move it aside yourself, pick another MUSE_RSI_DIR, or re-run with MUSE_RSI_FORCE_REPLACE=1."
      echo "This installer never deletes a non-empty directory on its own."
      rm -rf "$tmp_dir"
      exit 1
    fi
  fi
  mkdir -p "$(dirname "$REPO_DIR")"
  mv "$tmp_dir/muse-rsi-main" "$REPO_DIR"
  rm -rf "$tmp_dir"
  echo "Downloaded to $REPO_DIR."
fi

# setup.py exit codes: 0 = done, 20 = STAGED_OK (system files staged for
# the agent's file tool — setup is otherwise complete), anything else = fail.
set +e
python3 "$REPO_DIR/setup/setup.py" --yes "$@"
setup_code=$?
set -e
if [ "$setup_code" -ne 0 ] && [ "$setup_code" -ne 20 ]; then
  echo "setup.py failed (exit $setup_code) — verification skipped."
  exit "$setup_code"
fi
if [ "$setup_code" -eq 20 ]; then
  echo "NOTE: setup finished with files STAGED (exit 20) — apply the staged files first (see the ACTION REQUIRED lines above), then run the verification below."
fi

echo "Verifying ..."
if [ -x "$HOME/workspace/tools/gitleaks/gitleaks" ]; then
  "$HOME/workspace/tools/run_all_checks.sh" "$REPO_DIR"
else
  echo "gitleaks was skipped (--no-gitleaks), so the secret scan is skipped too. Running checks 1-3 ..."
  python3 "$REPO_DIR/scripts/generate_registry.py" --check --repo "$REPO_DIR"
  python3 "$REPO_DIR/scripts/eval_routing.py" --registry "$REPO_DIR/skills/router/registry.json"
  python3 "$REPO_DIR/scripts/validate_registry.py"
  echo "CHECKS 1-3 PASSED (secret scan skipped: gitleaks not installed)"
fi

echo ""
echo "Done. If the setup helped, star the repo (open $REPO_URL in the browser and click Star)"
echo "and file an install report — see skills/contribute/SKILL.md in the repo."
