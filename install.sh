#!/bin/bash
# muse-rsi one-line installer (install or update), self-healing since v3.2.
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
# When a step fails it does not stop to ask: it repairs the cause (retry,
# fallback tool, stash local edits, move a folder aside, ...), continues
# from the step that failed, and prints every repair as "[fix] ...".
# It never deletes user data (moves aside / backs up instead), never skips
# the secret scan silently, and never uses sudo with a password prompt.
#
# Env: MUSE_RSI_DIR (default ~/muse-rsi), MUSE_RSI_BRANCH (default main),
# MUSE_RSI_USE_ZIP=1 (skip git, download the repo ZIP instead).
set -u

REPO_DIR="${MUSE_RSI_DIR:-$HOME/muse-rsi}"
BRANCH="${MUSE_RSI_BRANCH:-main}"
REPO_URL="https://github.com/fahmi0812/muse-rsi"
STAMP="$(date +%Y%m%d-%H%M%S)"
FIXES=0
fix() { FIXES=$((FIXES + 1)); echo "  [fix] $*"; }

# Never operate on these, whatever the user sets MUSE_RSI_DIR to.
case "$REPO_DIR" in
  "/"|"$HOME"|"$HOME/workspace"|"$HOME/"|"$HOME/workspace/"|"/tmp"|"/tmp/")
    echo "MUSE_RSI_DIR must not be $REPO_DIR — pick an empty or new directory (e.g. ~/muse-rsi)."
    exit 1
    ;;
esac

# --- python3 (everything else needs it) ---------------------------------
if ! command -v python3 >/dev/null 2>&1; then
  if command -v sudo >/dev/null 2>&1 && sudo -n true 2>/dev/null; then
    if command -v apt-get >/dev/null 2>&1; then sudo -n apt-get install -y python3 && fix "python3 missing -> apt-get install python3"
    elif command -v dnf >/dev/null 2>&1; then sudo -n dnf install -y python3 && fix "python3 missing -> dnf install python3"
    fi
  fi
  command -v python3 >/dev/null 2>&1 || { echo "python3 not found and cannot be installed without a password — install Python 3, then re-run this same command (it resumes)."; exit 1; }
fi

# --- fetch helpers with fallbacks ---------------------------------------
download() {  # url dest
  for i in 1 2 3; do
    if command -v curl >/dev/null 2>&1; then
      curl -fsSL --max-time 600 -o "$2" "$1" && return 0
    else
      [ "$i" = 1 ] && fix "curl not found -> downloading with Python"
      python3 -c "import sys,urllib.request; urllib.request.urlretrieve(sys.argv[1], sys.argv[2])" "$1" "$2" && return 0
    fi
    echo "  download attempt $i failed: $1"; sleep $((i * 3))
  done
  return 1
}

fetch_zip() {  # -> repo at $REPO_DIR (an existing non-checkout dir is moved aside, never deleted)
  tmp_dir="$(mktemp -d "${TMPDIR:-/tmp}/muse-rsi-XXXX" 2>/dev/null || mktemp -d "$HOME/workspace/tmp-muse-rsi-XXXX")"
  download "$REPO_URL/archive/refs/heads/$BRANCH.zip" "$tmp_dir/repo.zip" || { echo "ERROR: could not download the repo ZIP"; return 1; }
  if command -v unzip >/dev/null 2>&1; then unzip -q -o "$tmp_dir/repo.zip" -d "$tmp_dir"
  else
    fix "unzip not found -> extracting with Python"
    python3 -c "import sys,zipfile; zipfile.ZipFile(sys.argv[1]).extractall(sys.argv[2])" "$tmp_dir/repo.zip" "$tmp_dir"
  fi
  src="$(find "$tmp_dir" -mindepth 1 -maxdepth 1 -type d -name 'muse-rsi-*' | head -1)"
  [ -n "$src" ] || { echo "ERROR: ZIP had no muse-rsi folder"; return 1; }
  if [ -e "$REPO_DIR" ] && [ -n "$(ls -A "$REPO_DIR" 2>/dev/null)" ]; then
    mv "$REPO_DIR" "$REPO_DIR.old-$STAMP" && fix "moved the old $REPO_DIR aside to $REPO_DIR.old-$STAMP (nothing deleted)"
  else
    rmdir "$REPO_DIR" 2>/dev/null || true
  fi
  mkdir -p "$(dirname "$REPO_DIR")"
  mv "$src" "$REPO_DIR"
  rm -rf "$tmp_dir"
  echo "Downloaded $BRANCH to $REPO_DIR (ZIP)."
}

# --- get or update the repo ---------------------------------------------
if [ -d "$REPO_DIR/.git" ] && [ -z "${MUSE_RSI_USE_ZIP:-}" ] && command -v git >/dev/null 2>&1; then
  echo "Updating existing copy at $REPO_DIR to $BRANCH ..."
  updated=0
  for i in 1 2 3; do
    if git -C "$REPO_DIR" fetch --quiet origin "$BRANCH"; then updated=1; break; fi
    echo "  fetch attempt $i failed"; sleep $((i * 3))
  done
  if [ "$updated" = 1 ]; then
    if ! git -C "$REPO_DIR" diff --quiet || ! git -C "$REPO_DIR" diff --cached --quiet || [ -n "$(git -C "$REPO_DIR" ls-files --others --exclude-standard)" ]; then
      git -C "$REPO_DIR" stash push -u -q -m "muse-rsi-autostash-$STAMP" && fix "local edits in $REPO_DIR saved to git stash 'muse-rsi-autostash-$STAMP' (restore: git stash pop)"
    fi
    current="$(git -C "$REPO_DIR" rev-parse --abbrev-ref HEAD)"
    if [ "$current" != "$BRANCH" ]; then
      git -C "$REPO_DIR" checkout -q "$BRANCH" 2>/dev/null || git -C "$REPO_DIR" checkout -q -b "$BRANCH" FETCH_HEAD
      fix "switched $REPO_DIR from '$current' to '$BRANCH'"
    fi
    if ! git -C "$REPO_DIR" merge --ff-only -q FETCH_HEAD 2>/dev/null; then
      git -C "$REPO_DIR" branch -q "backup/pre-update-$STAMP"
      git -C "$REPO_DIR" checkout -q -B "$BRANCH" FETCH_HEAD
      fix "local $BRANCH had diverged -> kept it as branch backup/pre-update-$STAMP, $BRANCH now matches origin"
    fi
    echo "Repo at $(git -C "$REPO_DIR" rev-parse --short HEAD) ($BRANCH)."
  else
    fix "git fetch failed 3x -> fetching a fresh copy as ZIP instead of continuing with the old one"
    fetch_zip || exit 1
  fi
elif [ -d "$REPO_DIR/setup" ] && [ ! -d "$REPO_DIR/.git" ]; then
  fix "$REPO_DIR is not a git checkout -> replacing it with a fresh copy (old one moved aside)"
  fetch_zip || exit 1
elif [ -z "${MUSE_RSI_USE_ZIP:-}" ] && command -v git >/dev/null 2>&1; then
  echo "Cloning $REPO_URL ($BRANCH) to $REPO_DIR ..."
  if [ -e "$REPO_DIR" ] && [ -n "$(ls -A "$REPO_DIR" 2>/dev/null)" ]; then
    mv "$REPO_DIR" "$REPO_DIR.old-$STAMP" && fix "moved the existing non-checkout $REPO_DIR aside to $REPO_DIR.old-$STAMP"
  fi
  cloned=0
  for i in 1 2 3; do
    if git clone --quiet --branch "$BRANCH" "$REPO_URL" "$REPO_DIR"; then cloned=1; break; fi
    rm -rf "$REPO_DIR" 2>/dev/null; echo "  clone attempt $i failed"; sleep $((i * 3))
  done
  if [ "$cloned" = 0 ]; then fix "git clone failed 3x -> downloading the ZIP instead"; fetch_zip || exit 1; fi
else
  [ -z "${MUSE_RSI_USE_ZIP:-}" ] && fix "git not found -> downloading the repo ZIP"
  fetch_zip || exit 1
fi

# --- setup (resumes itself on a second pass) -----------------------------
# setup.py exit codes: 0 = done, 20 = STAGED_OK (system files staged for the
# agent's file tool), 1 = something still failed after its own repairs.
python3 "$REPO_DIR/setup/setup.py" --yes "$@"
setup_code=$?
if [ "$setup_code" -ne 0 ] && [ "$setup_code" -ne 20 ]; then
  fix "setup.py exit $setup_code -> re-running with --resume (only the failed steps run again)"
  python3 "$REPO_DIR/setup/setup.py" --yes --resume "$@"
  setup_code=$?
fi
if [ "$setup_code" -eq 20 ]; then
  echo "NOTE: files STAGED (exit 20) — apply them with the agent's file tool (see ACTION REQUIRED above)."
fi

# --- verify (repairs a missing tool once, then re-checks) -----------------
echo "Verifying ..."
checks="$HOME/workspace/tools/run_all_checks.sh"
[ -x "$checks" ] || { cp "$REPO_DIR/scripts/run_all_checks.sh" "$checks" 2>/dev/null && chmod +x "$checks" && fix "run_all_checks.sh was missing -> installed"; }
bash "$checks" "$REPO_DIR"
check_code=$?
if [ "$check_code" -ne 0 ]; then
  fix "checks failed (exit $check_code) -> setup --resume, then checks again"
  python3 "$REPO_DIR/setup/setup.py" --yes --resume "$@" >/dev/null
  bash "$checks" "$REPO_DIR"
  check_code=$?
fi

echo ""
echo "Self-heal: $FIXES installer repair(s) (setup.py lists its own under 'Self-heal')."
if [ "$check_code" -ne 0 ] || { [ "$setup_code" -ne 0 ] && [ "$setup_code" -ne 20 ]; }; then
  echo "NOT DONE: setup exit $setup_code, checks exit $check_code. Everything that could run has run."
  echo "Fix the Bottleneck lines above, then re-run this same command — it resumes from the failed step."
  exit 1
fi
echo "Done. If the setup helped, star the repo (open $REPO_URL in the browser and click Star)"
echo "and file an install report — see skills/contribute/SKILL.md in the repo."
[ "$setup_code" -eq 20 ] && exit 20
exit 0
