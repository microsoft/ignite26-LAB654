"""Eastern-time helper: Emil works in Stamford, so "today" is the US Eastern date."""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

try:
    from zoneinfo import ZoneInfo

    ET = ZoneInfo("America/New_York")
except Exception:  # no tz database in the image; Eastern Standard Time covers the lab weeks
    ET = timezone(timedelta(hours=-5))


def today_et(now: datetime) -> date:
    return now.astimezone(ET).date()
