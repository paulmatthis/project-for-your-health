#!/bin/bash
# Opens the dashboard on demand. Nothing runs in the background before
# this and nothing is left running after: pulls and resyncs the workbook
# once, starts the local server for just this session, opens it in its
# own isolated Chrome window, and shuts the server back down the moment
# that window is closed.
#
# Deliberately not a permanent background service (no launchd job) -
# overkill for how infrequently a dashboard like this gets opened, and
# useless while the machine is asleep anyway. Scan-on-open instead.
set -e
cd "$(dirname "$0")/.."

# If Finder launched this via "Open Dashboard (Mac).command", Terminal opens a new
# window for it that otherwise just sits there after the script finishes -
# each double-click leaves another idle window behind. Remember this
# window's tty (only set when Terminal is actually the launcher) so it can
# close itself at the end, instead of piling up.
CLOSE_TERMINAL_TTY=""
if [ "$TERM_PROGRAM" = "Apple_Terminal" ]; then
  CLOSE_TERMINAL_TTY="$(tty)"
fi

git pull --rebase --quiet || echo "Warning: git pull failed, dashboard may show stale data" >&2
python3 app/recompute.py

STARTED_SERVER=0
if ! lsof -ti:8420 > /dev/null 2>&1; then
  python3 app/server.py &
  SERVER_PID=$!
  STARTED_SERVER=1
  sleep 0.5
fi

# Portable mktemp form (GNU and BSD mktemp interpret a bare -t prefix
# differently) so this works unchanged on Linux too.
PROFILE_DIR="$(mktemp -d "${TMPDIR:-/tmp}/dashboard-chrome.XXXXXXXX")"

UNAME=$(uname -s)
if [ "$UNAME" = "Darwin" ]; then
  # Any Chromium-based browser understands --app and --user-data-dir, not
  # just Chrome. Checks each app bundle's usual install location in
  # order rather than trying to launch-and-see, since `open -a` on a
  # missing app can pop a "can't find app in App Store" dialog instead
  # of just failing quietly.
  BROWSER_APP=""
  for candidate in "Google Chrome" "Brave Browser" "Microsoft Edge" "Chromium"; do
    if [ -d "/Applications/$candidate.app" ] || [ -d "$HOME/Applications/$candidate.app" ]; then
      BROWSER_APP="$candidate"
      break
    fi
  done
  if [ -z "$BROWSER_APP" ]; then
    echo "Could not find Chrome, Brave, Edge, or Chromium installed. Install one of these (or edit the candidate list in app/open_dashboard.sh if you use something else Chromium-based)." >&2
    exit 1
  fi
  open -n -a "$BROWSER_APP" --args \
    --app="http://localhost:8420/" \
    --user-data-dir="$PROFILE_DIR"
else
  # Linux: there's no `open` equivalent, so invoke a Chrome/Chromium
  # binary directly. Tries the common names in order; edit this list if
  # yours installs under something else.
  CHROME_BIN=""
  for candidate in google-chrome google-chrome-stable chromium chromium-browser brave-browser microsoft-edge microsoft-edge-stable; do
    if command -v "$candidate" >/dev/null 2>&1; then
      CHROME_BIN="$candidate"
      break
    fi
  done
  if [ -z "$CHROME_BIN" ]; then
    echo "Could not find a Chromium-based browser on PATH (tried google-chrome, google-chrome-stable, chromium, chromium-browser, brave-browser, microsoft-edge, microsoft-edge-stable). Install one of these, or edit the candidate list in app/open_dashboard.sh." >&2
    exit 1
  fi
  "$CHROME_BIN" --app="http://localhost:8420/" --user-data-dir="$PROFILE_DIR" &
fi

# Wait for this specific (isolated-profile) Chrome window to close before
# tearing anything down - other Chrome windows are untouched.
sleep 1
while pgrep -f -- "--user-data-dir=$PROFILE_DIR" > /dev/null 2>&1; do
  sleep 1
done
rm -rf "$PROFILE_DIR"

if [ "$STARTED_SERVER" = "1" ]; then
  kill "$SERVER_PID" 2>/dev/null || true
fi

# Close this window itself, last, so nothing is left over from this run -
# not the server, not the Chrome profile, not the Terminal window either.
# Backgrounded and detached so the script can exit first (an idle,
# already-exited shell closes without Terminal's "still running" prompt);
# scoped to this window's own tty so it never touches any other Terminal
# window.
if [ -n "$CLOSE_TERMINAL_TTY" ]; then
  ( sleep 1
    osascript -e "tell application \"Terminal\" to close (every window whose tty is \"$CLOSE_TERMINAL_TTY\")" >/dev/null 2>&1
  ) &
  disown
fi
