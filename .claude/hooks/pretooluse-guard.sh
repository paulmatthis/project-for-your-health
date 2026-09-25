#!/bin/bash
# Blocks writes to the tracking files until onboarding has actually run.
# See CLAUDE.md's FIRST RUN / ONBOARDING section. Without this, a
# confused or fast-moving session could log an entry before
# profile-and-targets.md has real targets in it, instead of just relying
# on Claude noticing the placeholder text on its own.
set -uo pipefail

cd "$CLAUDE_PROJECT_DIR" || exit 0

# See session-start.sh for why this is derived rather than hardcoded.
PROJECT_NAME=$(head -1 "$CLAUDE_PROJECT_DIR/CLAUDE.md" 2>/dev/null | awk '{for(i=1;i<=NF;i++) $i=toupper(substr($i,1,1)) tolower(substr($i,2)); print}')
[ -n "$PROJECT_NAME" ] || PROJECT_NAME="This project"

INPUT=$(cat)
TOOL_NAME=$(printf '%s' "$INPUT" | jq -r '.tool_name // empty' 2>/dev/null)
FILE_PATH=$(printf '%s' "$INPUT" | jq -r '.tool_input.file_path // empty' 2>/dev/null)

# Only Edit/Write/MultiEdit carry a file_path this hook can check. A write
# via Bash (e.g. a redirect) isn't caught here, this is a guard against an
# accidental early edit, not an airtight enforcement mechanism.
case "$TOOL_NAME" in
  Edit|Write|MultiEdit) ;;
  *) exit 0 ;;
esac

[ -n "$FILE_PATH" ] || exit 0

BASENAME=$(basename -- "$FILE_PATH")

case "$BASENAME" in
  food-log.md|spending-log.md|grocery-purchases.md|exercise-log.md|*.xlsx) ;;
  *) exit 0 ;;
esac

PROFILE="$CLAUDE_PROJECT_DIR/profile-and-targets.md"
if [ -f "$PROFILE" ] && grep -q "^ONBOARDING NOT COMPLETE" "$PROFILE" 2>/dev/null; then
  echo "$PROJECT_NAME: onboarding hasn't run yet, profile-and-targets.md still starts with the ONBOARDING NOT COMPLETE placeholder. Run the FIRST RUN / ONBOARDING flow in CLAUDE.md before writing to $BASENAME." >&2
  exit 2
fi

exit 0
