#!/bin/bash
# Safety net for CLAUDE.md's "commit and push after every write" rule: makes
# sure a session never ends with unpushed changes sitting on disk, even if a
# commit/push step got missed mid-turn. Also gates the commit on three
# checks: a Vale style lint (blocks on real errors, e.g. an em dash), an
# append-only sanity check on the log files, and an image reference check
# (both warn, don't block, since a real compaction into a summary block or
# a photo intentionally left out of a log entry are legitimate).
set -uo pipefail

cd "$CLAUDE_PROJECT_DIR" || exit 0

# See session-start.sh for why these are derived rather than hardcoded.
PROJECT_NAME=$(head -1 "$CLAUDE_PROJECT_DIR/CLAUDE.md" 2>/dev/null | awk '{for(i=1;i<=NF;i++) $i=toupper(substr($i,1,1)) tolower(substr($i,2)); print}')
[ -n "$PROJECT_NAME" ] || PROJECT_NAME="This project"
WORKBOOK=$(basename "$(ls "$CLAUDE_PROJECT_DIR"/*.xlsx 2>/dev/null | head -1)" 2>/dev/null)
[ -n "$WORKBOOK" ] || WORKBOOK="the companion workbook"

git rev-parse --is-inside-work-tree >/dev/null 2>&1 || exit 0
git remote get-url origin >/dev/null 2>&1 || exit 0

[ -n "$(git status --porcelain)" ] || exit 0

BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null)
[ -n "$BRANCH" ] && [ "$BRANCH" != "HEAD" ] || exit 0

# --- Append-only sanity check on the log files ----------------------------
# Warns, never blocks: a real compaction of old weeks into a summary block
# (CLAUDE.md's PROCESSING AN ENTRY step 11) legitimately touches old lines.
check_append_only() {
  local append_only_files="food-log.md spending-log.md grocery-purchases.md exercise-log.md"
  local f status removed
  for f in $append_only_files; do
    [ -f "$f" ] || continue
    status=$(git status --porcelain -- "$f" 2>/dev/null | cut -c1-2)
    case "$status" in
      *M*) ;;
      *) continue ;;
    esac
    removed=$(git diff -- "$f" 2>/dev/null | grep -E '^-[^-]' || true)
    if [ -n "$removed" ]; then
      echo "$PROJECT_NAME: $f has existing line(s) removed or changed, not just appended:" >&2
      echo "$removed" | sed 's/^/  /' >&2
      echo "  If this was a deliberate compaction into a summary block, fine. If not, check before this commit goes out, it may be accidental data loss." >&2
    fi
  done
}

check_append_only

# --- Image reference check --------------------------------------------------
# Warns, never blocks. Two directions: a doc references an images/ path
# that doesn't exist on disk (archiving step got missed or the path is
# wrong), or a file sits in images/ that nothing ever mentions (an
# archived photo that never made it into an entry, or a design asset like
# the mascot, referenced from README.md rather than a log). Scans this
# fixed list every run, not just changed files, so it catches pre-existing
# rot too, not only what this session touched.
check_image_references() {
  local log_files="food-log.md spending-log.md grocery-purchases.md profile-and-targets.md exercise-log.md README.md"
  local existing_files
  existing_files=$(for f in $log_files; do [ -f "$f" ] && echo "$f"; done)
  [ -n "$existing_files" ] || return 0

  local referenced missing orphaned ref base found
  referenced=$(grep -ohE 'images/[A-Za-z0-9._-]*[A-Za-z0-9_-]' $existing_files 2>/dev/null | sort -u)

  missing=""
  while IFS= read -r ref; do
    [ -n "$ref" ] || continue
    [ -f "$ref" ] || missing="$missing$ref"$'\n'
  done <<< "$referenced"

  if [ -n "$missing" ]; then
    echo "$PROJECT_NAME: log file(s) reference image path(s) that don't exist on disk:" >&2
    printf '%s' "$missing" | sed 's/^/  /' >&2
  fi

  if [ -d images ]; then
    orphaned=""
    for f in images/*; do
      [ -f "$f" ] || continue
      base=$(basename "$f")
      found=$(printf '%s\n' "$referenced" | grep -F "images/$base" || true)
      [ -n "$found" ] || orphaned="$orphaned$f"$'\n'
    done
    if [ -n "$orphaned" ]; then
      echo "$PROJECT_NAME: image(s) in images/ that no log file references (may just be intentionally unlogged):" >&2
      printf '%s' "$orphaned" | sed 's/^/  /' >&2
    fi
  fi
}

check_image_references

# --- Entry format lint -------------------------------------------------
# Warns, never blocks. Scans each log file's table every run, not just
# rows changed this session, same approach as the image reference check
# above, so it also catches a pre-existing malformed row, not only a new
# one. Checks that each date-led row has the column count that file's
# table header defines, and, for food-log.md specifically, that the
# Confidence column mentions exact, estimated, or looked up per CLAUDE.md
# step 3/8 (the note itself can be freeform, e.g. "[estimated, ~6% ABV
# assumed]", this just checks one of those three words shows up).
check_entry_format() {
  local files=(
    "food-log.md:8"
    "spending-log.md:5"
    "grocery-purchases.md:6"
    "exercise-log.md:5"
  )

  local entry file expected row col_count
  for entry in "${files[@]}"; do
    file="${entry%%:*}"
    expected="${entry#*:}"
    [ -f "$file" ] || continue

    while IFS= read -r row; do
      [ -n "$row" ] || continue
      col_count=$(printf '%s' "$row" | awk -F'|' '{print NF-2}')
      if [ "$col_count" -ne "$expected" ]; then
        echo "$PROJECT_NAME: $file has a row with $col_count columns, expected $expected:" >&2
        echo "  $row" >&2
      fi
      if [ "$file" = "food-log.md" ] && ! printf '%s' "$row" | grep -qiE 'exact|estimated|looked up'; then
        echo "$PROJECT_NAME: $file has a row with no confidence tag (exact/estimated/looked up):" >&2
        echo "  $row" >&2
      fi
    done < <(grep -E '^\| [0-9]{4}-[0-9]{2}-[0-9]{2} \|' "$file" 2>/dev/null)
  done
}

check_entry_format

# --- Vale style gate --------------------------------------------------------
# Blocks the commit (by not making it) on a real Vale error, e.g. the
# Local.NoEmDash rule. Fails open (skips the check, doesn't block) if
# Vale isn't installed or its config can't be found, rather than silently
# stalling every commit over an environment issue.
if command -v vale >/dev/null 2>&1; then
  MD_FILES=()
  while IFS= read -r f; do
    [ -n "$f" ] && MD_FILES+=("$f")
  done < <(git status --porcelain | cut -c4- | grep '\.md$')

  if [ "${#MD_FILES[@]}" -gt 0 ]; then
    VALE_OUT=$(vale "${MD_FILES[@]}" 2>&1)
    VALE_EXIT=$?
    if [ "$VALE_EXIT" -eq 1 ]; then
      echo "$PROJECT_NAME: Vale found a style error (likely an em dash) in a changed file. Not auto-committing until it's fixed:" >&2
      echo "$VALE_OUT" >&2
      exit 0
    elif [ "$VALE_EXIT" -ge 2 ]; then
      echo "$PROJECT_NAME: Vale couldn't run (config or install issue), skipping the style check for this commit." >&2
    fi
  fi
fi

FILES=$(git status --porcelain | cut -c4- | paste -sd ', ' -)

git add -A
git commit -m "Auto-sync: $FILES" >/dev/null 2>&1 || exit 0

# Last-resort safety net: this project has one branch, main. session-start.sh
# already forces a clean checkout onto main, but if a turn somehow still
# ended up committing on a side branch (started dirty, or a mid-session
# checkout), move that commit onto main here rather than push it to the
# side branch. Uses cherry-pick, not merge, so it works even if the side
# branch never tracked origin/main.
if [ "$BRANCH" != "main" ]; then
  COMMIT_SHA=$(git rev-parse HEAD)
  if git fetch origin main 2>&1 && git checkout main 2>/dev/null || git checkout -B main --track origin/main 2>/dev/null; then
    if git merge --ff-only origin/main >/dev/null 2>&1 && git cherry-pick "$COMMIT_SHA" >/dev/null 2>&1; then
      echo "$PROJECT_NAME: this turn's commit landed on branch '$BRANCH' instead of main - moved it onto main before pushing. This project never uses side branches." >&2
      BRANCH=main
    else
      git cherry-pick --abort >/dev/null 2>&1
      echo "$PROJECT_NAME: this turn's commit landed on branch '$BRANCH' instead of main, and it could not be moved onto main automatically (conflict). It is committed on '$BRANCH' and NOT yet on main - needs manual attention, do not guess which side is right." >&2
      exit 0
    fi
  else
    echo "$PROJECT_NAME: this turn's commit landed on branch '$BRANCH' instead of main, and main could not be checked out to fix it (offline?). It is committed locally on '$BRANCH' only - needs manual attention." >&2
    exit 0
  fi
fi

# Retry a few times in case the other device pushed in the same window
# (a plain push race, not a real conflict): fetch, auto-merge, try again.
ATTEMPT=0
while [ "$ATTEMPT" -lt 3 ]; do
  if git push origin "$BRANCH" 2>&1; then
    exit 0
  fi

  ATTEMPT=$((ATTEMPT + 1))
  git fetch origin "$BRANCH" 2>&1 || break

  if git merge --no-edit "origin/$BRANCH" >/dev/null 2>&1; then
    continue
  fi

  git merge --abort >/dev/null 2>&1
  echo "$PROJECT_NAME: push was rejected and the other device's changes couldn't be auto-merged (most likely both touched $WORKBOOK). Your entry is committed locally but NOT pushed yet. Resolve the conflict manually before the next session, do not guess which side is right." >&2
  exit 0
done

echo "$PROJECT_NAME: committed locally but still couldn't push after retrying (offline, or repeated push races). Will need manual attention before the remote is caught up." >&2
