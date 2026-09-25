#!/usr/bin/env python3
"""
The single source of truth for "what date is it, for logging purposes."

Default day boundary: a new day starts at 5am America/New_York, not
midnight. Anything logged between midnight and 4:59am belongs to the
PREVIOUS day's date - so a snack at 1am on what the calendar calls the
25th still gets logged as the 24th. Adjust TIMEZONE and DAY_START_HOUR
below to your own locale and schedule if this default doesn't fit.

This exists because a session computing "today" from its own clock
(sometimes UTC, sometimes local) reliably gets the date wrong right
around midnight. Never compute today's date by hand when logging an
entry or generating a dashboard - call this instead.

Usage: python3 app/effective_date.py
Prints the effective date as YYYY-MM-DD.
"""

import datetime

try:
    from zoneinfo import ZoneInfo
except ImportError:  # pragma: no cover - Python 3.9+ always has zoneinfo
    ZoneInfo = None

TIMEZONE = "America/New_York"
DAY_START_HOUR = 5


def effective_date(now: datetime.datetime | None = None) -> datetime.date:
    if now is None:
        now = datetime.datetime.now(ZoneInfo(TIMEZONE))
    elif now.tzinfo is None:
        now = now.replace(tzinfo=ZoneInfo(TIMEZONE))
    if now.hour < DAY_START_HOUR:
        return (now - datetime.timedelta(days=1)).date()
    return now.date()


if __name__ == "__main__":
    print(effective_date().isoformat())
