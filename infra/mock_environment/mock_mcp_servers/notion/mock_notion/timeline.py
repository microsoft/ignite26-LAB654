"""Story dates that move with the calendar.

The seed's story dates are written as offsets from an *anchor*: the Monday of the
current week in US Eastern time (Saturday and Sunday roll forward to the next
Monday). During the lab week of Mon Nov 16, 2026 this gives exactly the spec's
dates; in any other week the story still reads as "this week".

Placeholders in seed strings:

- ``{{+4|iso}}`` -> ``2026-11-20`` (date property values)
- ``{{+4|md}}`` -> ``Nov 20``; ``{{+4|wmd}}`` -> ``Fri Nov 20``; ``{{+22|long}}`` -> ``Tue Dec 8, 2026``
- ``{{-28T15:20|ts}}`` -> ``2026-10-19T15:20:00.000Z`` (UTC time of day; created/edited stamps)

Timestamps are never in the future: if the latest one would be later than now
(possible early on a Monday, or at the weekend), all of them move back together.

``STORY_ANCHOR=2026-11-16`` pins the anchor; ``MOCK_NOW`` pins "now" (and so the anchor).
"""

from __future__ import annotations

import json
import os
import re
from datetime import date, datetime, timedelta, timezone

try:
    from zoneinfo import ZoneInfo

    ET = ZoneInfo("America/New_York")
except Exception:  # no tz database in the image; Eastern Standard Time covers the lab weeks
    ET = timezone(timedelta(hours=-5))

TOKEN = re.compile(r"\{\{([+-]?\d+)(?:T(\d\d):(\d\d))?\|(iso|md|wmd|long|ts)\}\}")


def now_utc() -> datetime:
    raw = os.environ.get("MOCK_NOW")
    if raw:
        return datetime.fromisoformat(raw.replace("Z", "+00:00")).astimezone(timezone.utc)
    return datetime.now(timezone.utc)


def anchor_for(now: datetime) -> date:
    pinned = os.environ.get("STORY_ANCHOR")
    if pinned:
        return date.fromisoformat(pinned)
    local = now.astimezone(ET).date()
    wd = local.weekday()
    return local - timedelta(days=wd) if wd < 5 else local + timedelta(days=7 - wd)


def _fmt(day: date, kind: str) -> str:
    if kind == "iso":
        return day.isoformat()
    if kind == "md":
        return f"{day:%b} {day.day}"
    if kind == "wmd":
        return f"{day:%a %b} {day.day}"
    return f"{day:%a %b} {day.day}, {day.year}"


def _stamp(anchor: date, m: re.Match) -> datetime:
    return datetime(anchor.year, anchor.month, anchor.day, int(m.group(2) or 0), int(m.group(3) or 0),
                    tzinfo=timezone.utc) + timedelta(days=int(m.group(1)))


def materialize(template: dict, now: datetime) -> dict:
    """Replace every placeholder for the anchor week of ``now``. Templates without placeholders pass through."""
    text = json.dumps(template, ensure_ascii=False)
    if "{{" not in text:
        return template
    anchor = anchor_for(now)
    stamps = [_stamp(anchor, m) for m in TOKEN.finditer(text) if m.group(4) == "ts"]
    shift = max(timedelta(0), max(stamps, default=now) - now + timedelta(minutes=5)) if stamps else timedelta(0)

    def sub(m: re.Match) -> str:
        if m.group(4) == "ts":
            ts = _stamp(anchor, m) - shift
            return ts.strftime("%Y-%m-%dT%H:%M:%S.000Z")
        return _fmt(anchor + timedelta(days=int(m.group(1))), m.group(4))

    return json.loads(TOKEN.sub(sub, text))
