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
set -e

REPO_DIR="${MUSE_RSI_DIR:-$HOME/muse-rsi}"
REPO_URL="https://github.com/fahmi0812/muse-rsi"

command -v python3 >/dev/null 2>&1 || { echo "python3 not found — install Python 3 first."; exit 1; }

if [ -d "$REPO_DIR/setup" ]; then
  echo "Using existing copy at $REPO_DIR (run 'git -C $REPO_DIR pull' first if you want the latest)."
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
    echo "Removing incomplete $REPO_DIR (it has no setup/setup.py) ..."
    rm -rf "$REPO_DIR"
  fi
  mv "$tmp_dir/muse-rsi-main" "$REPO_DIR"
  rm -rf "$tmp_dir"
  echo "Downloaded to $REPO_DIR."
fi

python3 "$REPO_DIR/setup/setup.py" --yes "$@"

echo "Verifying (all 4 checks must pass) ..."
"$HOME/workspace/tools/run_all_checks.sh" "$REPO_DIR"

echo ""
echo "Done. If the setup helped, star the repo (open $REPO_URL in the browser and click Star)"
echo "and file an install report — see skills/contribute/SKILL.md in the repo."
