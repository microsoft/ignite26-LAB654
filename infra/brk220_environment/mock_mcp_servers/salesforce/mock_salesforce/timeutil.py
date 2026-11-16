"""Date and time helpers: Salesforce wire formats and US Eastern time (the org's and the user's time zone)."""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone


def _nth_sunday(year: int, month: int, n: int) -> date:
    first = date(year, month, 1)
    return first + timedelta(days=(6 - first.weekday()) % 7 + 7 * (n - 1))


def et_offset(moment: datetime) -> timedelta:
    """UTC offset of America/New_York at ``moment`` (DST: second Sunday of March to first Sunday of November)."""
    utc = moment.astimezone(timezone.utc).replace(tzinfo=None)
    start = datetime.combine(_nth_sunday(utc.year, 3, 2), datetime.min.time()) + timedelta(hours=7)
    end = datetime.combine(_nth_sunday(utc.year, 11, 1), datetime.min.time()) + timedelta(hours=6)
    return timedelta(hours=-4) if start <= utc < end else timedelta(hours=-5)


def to_et(moment: datetime) -> datetime:
    return (moment.astimezone(timezone.utc) + et_offset(moment)).replace(tzinfo=None)


def et_midnight_utc(day: date) -> datetime:
    """The UTC instant at which ``day`` starts in US Eastern time."""
    guess = datetime(day.year, day.month, day.day, 5, tzinfo=timezone.utc)
    return datetime(day.year, day.month, day.day, tzinfo=timezone.utc) - et_offset(guess)


def parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    text = value.strip().replace("Z", "+00:00")
    if len(text) >= 5 and text[-5] in "+-" and text[-3] != ":":
        text = text[:-2] + ":" + text[-2:]
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def parse_date(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(str(value)[:10])
    except ValueError:
        return None


def iso_ms(moment: datetime) -> str:
    moment = moment.astimezone(timezone.utc)
    return moment.strftime("%Y-%m-%dT%H:%M:%S.") + f"{moment.microsecond // 1000:03d}Z"


def soql_datetime(value: str) -> str:
    """REST/SOQL datetimes use +0000 instead of Z."""
    moment = parse_dt(value)
    return moment.strftime("%Y-%m-%dT%H:%M:%S.000+0000") if moment else value


def et_date(value: str | None) -> date | None:
    moment = parse_dt(value)
    return to_et(moment).date() if moment else None


def display_date(day: date) -> str:
    return f"{day.month}/{day.day}/{day.year}"


def display_datetime(value: str) -> str:
    moment = parse_dt(value)
    if not moment:
        return value
    local = to_et(moment)
    hour = local.hour % 12 or 12
    return f"{display_date(local.date())}, {hour}:{local.minute:02d} {'AM' if local.hour < 12 else 'PM'}"


def long_date(day: date) -> str:
    return f"{day.strftime('%B')} {day.day}, {day.year}"
