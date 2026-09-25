ONBOARDING NOT COMPLETE

This file starts every fresh clone with this placeholder line. Claude reads
this at the start of a session and, if it's still here, walks through the
FIRST RUN / ONBOARDING flow in CLAUDE.md before logging anything. Once
onboarding finishes, this whole file gets replaced with real stats, goal,
history, preferences, patterns to flag, the calculated targets, and the
PRIMARY_DEVICE_SIGNATURE line (see CLAUDE.md's PRIMARY DEVICE section).

A PreToolUse hook (.claude/hooks/pretooluse-guard.sh) also blocks direct
writes to the log files and the workbook while this placeholder is still
here, so onboarding can't get skipped by accident.
