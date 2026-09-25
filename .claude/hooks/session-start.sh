#!/bin/bash
# Keeps a session (local or cloud) from ever starting against a stale
# copy of this project's log files. See CLAUDE.md's sync rule.
set -uo pipefail

cd "$CLAUDE_PROJECT_DIR" || exit 0

# PROJECT_NAME and WORKBOOK are derived, not hardcoded, so these hooks work
# unmodified under whatever name onboarding gives the project (see CLAUDE.md's
# FIRST RUN / ONBOARDING naming step). CLAUDE.md's own title line is the
# single source of truth for the display name; the workbook is whichever
# .xlsx file exists at the project root (there's only ever one).
PROJECT_NAME=$(head -1 "$CLAUDE_PROJECT_DIR/CLAUDE.md" 2>/dev/null | awk '{for(i=1;i<=NF;i++) $i=toupper(substr($i,1,1)) tolower(substr($i,2)); print}')
[ -n "$PROJECT_NAME" ] || PROJECT_NAME="This project"
WORKBOOK=$(basename "$(ls "$CLAUDE_PROJECT_DIR"/*.xlsx 2>/dev/null | head -1)" 2>/dev/null)
[ -n "$WORKBOOK" ] || WORKBOOK="the companion workbook"

# --- Primary device check (for the companion workbook; see CLAUDE.md's
# PRIMARY DEVICE section) -------------------------------------------------
# Computed here, deterministically, instead of asking Claude to self-assess
# it every session. Runs unconditionally, before any of the git-sync logic
# below, so it always prints regardless of git state.
check_primary_device() {
  local profile="$CLAUDE_PROJECT_DIR/profile-and-targets.md"
  [ -f "$profile" ] || return 0

  local sig_line
  sig_line=$(grep -m1 '^PRIMARY_DEVICE_SIGNATURE:' "$profile" 2>/dev/null)
  if [ -z "$sig_line" ]; then
    echo "$PROJECT_NAME: no PRIMARY_DEVICE_SIGNATURE recorded in profile-and-targets.md. Not primary-device-eligible until it's added (see CLAUDE.md's PRIMARY DEVICE section). Do not touch $WORKBOOK this session." >&2
    return 0
  fi

  local sig_value sig_platform sig_path
  sig_value=${sig_line#PRIMARY_DEVICE_SIGNATURE:}
  sig_value=${sig_value# }
  sig_platform=${sig_value%%|*}
  sig_path=${sig_value#*|}

  local current_platform current_path
  current_platform=$(uname -s | tr '[:upper:]' '[:lower:]')
  current_path="$CLAUDE_PROJECT_DIR"

  if [ "$sig_platform" = "$current_platform" ] && [ "$sig_path" = "$current_path" ]; then
    echo "$PROJECT_NAME: PRIMARY DEVICE (platform=$current_platform, path=$current_path matches recorded signature). Run the catch-up pass from CLAUDE.md's PRIMARY DEVICE section before processing new entries, then keep $WORKBOOK updated this session." >&2
  else
    echo "$PROJECT_NAME: NOT PRIMARY DEVICE (recorded signature: $sig_platform|$sig_path; this session: $current_platform|$current_path). Do not open, edit, or write to $WORKBOOK this session. Log to the .md files only." >&2
  fi
}

check_primary_device

# --- Repo privacy check ----------------------------------------------------
# This project archives food photos, spending data, and possibly bank
# statement images (see CLAUDE.md's opening line). Checks the actual
# GitHub visibility instead of trusting that whoever set up the remote
# remembered to flip it private. Fails open (skips with a note) if gh
# isn't installed or isn't authenticated, rather than blocking a session
# over a tooling gap.
check_repo_privacy() {
  command -v gh >/dev/null 2>&1 || {
    echo "$PROJECT_NAME: gh CLI not found, skipping the repo-privacy check. Confirm manually that the GitHub repo is private." >&2
    return 0
  }
  gh auth status >/dev/null 2>&1 || {
    echo "$PROJECT_NAME: gh isn't authenticated, skipping the repo-privacy check. Confirm manually that the GitHub repo is private." >&2
    return 0
  }

  local is_private
  is_private=$(gh repo view --json isPrivate --jq '.isPrivate' 2>/dev/null)
  if [ -z "$is_private" ]; then
    echo "$PROJECT_NAME: couldn't read the repo's visibility from GitHub, skipping the repo-privacy check." >&2
    return 0
  fi
  if [ "$is_private" != "true" ]; then
    echo "$PROJECT_NAME: WARNING, the GitHub repo for this project is NOT private. It can end up holding food photos, spending data, and bank statement images. Make it private now: gh repo edit --visibility private" >&2
  fi
}

check_repo_privacy

# --- Feature/archive consistency check --------------------------------------
# CLAUDE.md's FEATURES list and each feature's actual file location (project
# root vs archive/) are two separate sources of truth. A feature turned off
# in conversation without moving its file, or a file moved without updating
# the list, desyncs them silently. Warns, doesn't block. Fixing a mismatch
# is a one-line git mv or a one-word edit to FEATURES, not something worth
# gating a session on.
check_feature_archive_consistency() {
  local claude_md="$CLAUDE_PROJECT_DIR/CLAUDE.md"
  [ -f "$claude_md" ] || return 0

  # "Feature name as it appears in FEATURES:its file" pairs.
  local features=(
    "Spending log:spending-log.md"
    "Grocery purchases:grocery-purchases.md"
    "Exercise log:exercise-log.md"
  )

  local entry name file state root_exists archive_exists
  for entry in "${features[@]}"; do
    name="${entry%%:*}"
    file="${entry#*:}"

    state=$(grep -m1 "^- $name:" "$claude_md" 2>/dev/null | sed -E "s/^- $name:[[:space:]]*//" | tr -d '\r')
    if [ -z "$state" ]; then
      echo "$PROJECT_NAME: CLAUDE.md's FEATURES list has no entry for '$name'. Can't check it against $file." >&2
      continue
    fi

    root_exists=0
    [ -f "$CLAUDE_PROJECT_DIR/$file" ] && root_exists=1
    archive_exists=0
    [ -f "$CLAUDE_PROJECT_DIR/archive/$file" ] && archive_exists=1

    if [ "$root_exists" -eq 1 ] && [ "$archive_exists" -eq 1 ]; then
      echo "$PROJECT_NAME: $file exists both at the project root and in archive/. Only one copy should exist, resolve which is current." >&2
    fi

    case "$state" in
      on)
        if [ "$root_exists" -eq 0 ] && [ "$archive_exists" -eq 1 ]; then
          echo "$PROJECT_NAME: FEATURES lists '$name' as on, but $file is sitting in archive/, not the project root. They've drifted, move it back (git mv) or update FEATURES." >&2
        elif [ "$root_exists" -eq 0 ] && [ "$archive_exists" -eq 0 ]; then
          echo "$PROJECT_NAME: FEATURES lists '$name' as on, but $file doesn't exist at the root or in archive/." >&2
        fi
        ;;
      off)
        if [ "$archive_exists" -eq 0 ] && [ "$root_exists" -eq 1 ]; then
          echo "$PROJECT_NAME: FEATURES lists '$name' as off, but $file is still sitting at the project root, not archive/. They've drifted, move it (git mv) or update FEATURES." >&2
        elif [ "$archive_exists" -eq 0 ] && [ "$root_exists" -eq 0 ]; then
          echo "$PROJECT_NAME: FEATURES lists '$name' as off, but $file doesn't exist at the root or in archive/." >&2
        fi
        ;;
      *)
        echo "$PROJECT_NAME: FEATURES entry for '$name' is neither 'on' nor 'off' (found '$state')." >&2
        ;;
    esac
  done
}

check_feature_archive_consistency

# --- Git sync -------------------------------------------------------------

git rev-parse --is-inside-work-tree >/dev/null 2>&1 || exit 0

BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null)
[ -n "$BRANCH" ] && [ "$BRANCH" != "HEAD" ] || exit 0

git remote get-url origin >/dev/null 2>&1 || exit 0

# This project has one branch: main. A cloud session's own launch
# wrapper sometimes assigns a different working branch (e.g.
# claude/some-task-name) - that's a harness detail, not a project
# decision, and CLAUDE.md's commit/push rule means main. Force onto
# main here, deterministically, instead of relying on Claude to notice
# and override a competing instruction mid-session (it has missed this
# before). Only forces when the tree is clean; a dirty non-main
# checkout is left alone and flagged instead of touched.
if [ "$BRANCH" != "main" ]; then
  if [ -n "$(git status --porcelain)" ]; then
    echo "$PROJECT_NAME: session started on branch '$BRANCH' instead of main, and the working tree isn't clean, so it wasn't switched automatically. Commit or stash, then switch to main yourself before logging anything - this project never uses side branches." >&2
    exit 0
  fi
  if git fetch origin main 2>&1 && git checkout -B main --track origin/main >/dev/null 2>&1; then
    echo "$PROJECT_NAME: session started on branch '$BRANCH' (from the session's own launch settings, not this project). Switched to main automatically - this project always commits and pushes to main, never a side branch." >&2
    BRANCH=main
  else
    echo "$PROJECT_NAME: session started on branch '$BRANCH' and could not switch to main automatically (fetch/checkout failed). Switch to main manually before committing anything - this project never uses side branches." >&2
    exit 0
  fi
fi

if [ -n "$(git status --porcelain)" ]; then
  echo "$PROJECT_NAME: working tree has uncommitted changes, skipping auto-pull. Commit/push before logging new entries." >&2
  exit 0
fi

if ! git fetch origin "$BRANCH" 2>&1; then
  echo "$PROJECT_NAME: git fetch failed (offline?). Working from local copy, which may be stale." >&2
  exit 0
fi

if git merge --ff-only "origin/$BRANCH" >/dev/null 2>&1; then
  exit 0
fi

# Diverged: this device and the other one each have commits the other
# hasn't seen (e.g. both logged an entry before either synced). Try a real
# merge, safe because git only auto-merges non-overlapping changes; if the
# two sides actually edited the same content (most likely: both touched the
# binary tracker workbook, which can't be diffed line by line) it fails and
# we back out rather than guess which entry is right.
if git merge --no-edit "origin/$BRANCH" >/dev/null 2>&1; then
  echo "$PROJECT_NAME: auto-merged changes from the other device." >&2
  exit 0
fi

git merge --abort >/dev/null 2>&1
echo "$PROJECT_NAME: local and remote have conflicting edits (most likely both devices touched $WORKBOOK, which can't auto-merge) and could not be combined automatically. Resolve manually before logging anything new. Do not guess which side is right." >&2
