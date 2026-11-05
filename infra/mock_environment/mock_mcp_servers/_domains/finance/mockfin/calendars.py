"""Fiscal and trading calendars.

Conventions (match LSEG Worldscope, LSEG IBES and FactSet as seen in the recorded trace):

* A fiscal year is labelled by the calendar year most of it falls in. A year ending
  January-May belongs to the previous calendar year: Litware's year ending 25 Jan 2026
  is fiscal 2025.
* ``period_end`` is the vendor-normalised month-end (IBES ``date``, FactSet
  ``fiscalEndDate``). ``actual_end`` is the company's real closing date
  (Worldscope ``fiscalPeriodEndDate``, FactSet ``reportDate``), e.g. the last Sunday
  of January for Litware.
* A period counts as reported once its earnings announcement is at or before "now".
"""

from __future__ import annotations

import calendar as _cal
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from functools import lru_cache

from mockmcp import Seeded

WEEKDAYS = {"MON": 0, "TUE": 1, "WED": 2, "THU": 3, "FRI": 4, "SAT": 5, "SUN": 6}


def month_end(year: int, month: int) -> date:
    return date(year, month, _cal.monthrange(year, month)[1])


def add_months(year: int, month: int, delta: int) -> tuple[int, int]:
    index = year * 12 + (month - 1) + delta
    return index // 12, index % 12 + 1


@dataclass(frozen=True)
class FiscalRule:
    fye_month: int
    rule: str = "month_end"  # month_end | last_weekday | nearest_weekday
    weekday: str | None = None

    @classmethod
    def from_dict(cls, raw: dict) -> "FiscalRule":
        return cls(raw["fye_month"], raw.get("rule", "month_end"), raw.get("weekday"))

    def actual_close(self, year: int, month: int) -> date:
        last = month_end(year, month)
        if self.rule == "month_end" or not self.weekday:
            return last
        target = WEEKDAYS[self.weekday]
        if self.rule == "last_weekday":
            return last - timedelta(days=(last.weekday() - target) % 7)
        before = last - timedelta(days=(last.weekday() - target) % 7)
        after = before + timedelta(days=7)
        return before if (last - before) <= (after - last) else after


@dataclass(frozen=True, order=True)
class Period:
    """A fiscal year (``quarter`` is None) or a fiscal quarter (1-4) of ``year``."""

    year: int
    quarter: int | None = None

    @property
    def is_annual(self) -> bool:
        return self.quarter is None

    @property
    def key(self) -> str:
        return f"FY{self.year}" if self.is_annual else f"{self.year}Q{self.quarter}"

    def ordinal(self) -> int:
        return self.year if self.is_annual else self.year * 4 + self.quarter - 1

    def shift(self, steps: int) -> "Period":
        if self.is_annual:
            return Period(self.year + steps)
        index = self.ordinal() + steps
        return Period(index // 4, index % 4 + 1)

    def quarters(self) -> list["Period"]:
        return [Period(self.year, q) for q in range(1, 5)] if self.is_annual else [self]


class FiscalCalendar:
    """Fiscal periods and reporting dates for one company."""

    def __init__(self, ticker: str, rule: FiscalRule, report_anchors: dict | None = None) -> None:
        self.ticker = ticker
        self.rule = rule
        anchors = report_anchors or {}
        self._annual = {int(k): datetime.fromisoformat(v) for k, v in anchors.get("annual", {}).items()}
        self._quarterly = {k: datetime.fromisoformat(v) for k, v in anchors.get("quarterly", {}).items()}
        self._seed = Seeded("calendar", ticker)

    def _end_month(self, period: Period) -> tuple[int, int]:
        end_year = period.year + 1 if self.rule.fye_month <= 5 else period.year
        if period.is_annual or period.quarter == 4:
            return end_year, self.rule.fye_month
        return add_months(end_year, self.rule.fye_month, -3 * (4 - period.quarter))

    def period_end(self, period: Period) -> date:
        return month_end(*self._end_month(period))

    def actual_end(self, period: Period) -> date:
        return self.rule.actual_close(*self._end_month(period))

    def actual_start(self, period: Period) -> date:
        return self.actual_end(period.shift(-1)) + timedelta(days=1)

    def length_days(self, period: Period) -> int:
        return (self.actual_end(period) - self.actual_end(period.shift(-1))).days

    def period_for_year_month(self, year: int, month: int) -> Period:
        """The fiscal year whose normalised end falls in or after (year, month)."""
        label = year - 1 if self.rule.fye_month <= 5 else year
        for candidate in (label - 1, label, label + 1):
            if self.period_end(Period(candidate)) >= month_end(year, month):
                return Period(candidate)
        return Period(label + 1)

    def announcement(self, period: Period) -> datetime:
        """Local (US/Eastern) announcement time of the earnings release."""
        if period.is_annual or period.quarter == 4:
            anchored = self._annual.get(period.year)
            if anchored:
                return anchored
            base, lo, hi, key = self.actual_end(Period(period.year)), 26, 45, f"FY{period.year}"
        else:
            anchored = self._quarterly.get(period.key)
            if anchored:
                return anchored
            base, lo, hi, key = self.actual_end(period), 22, 36, period.key
        day = base + timedelta(days=self._seed.integer(lo, hi, "report", key))
        while day.weekday() >= 4:  # results land Monday-Thursday
            day += timedelta(days=1)
        minute = self._seed.integer(5, 50, "report-minute", key)
        return datetime.combine(day, time(16, minute))

    def is_reported(self, period: Period, now: datetime) -> bool:
        return to_utc(self.announcement(period)) <= now

    def latest_reported(self, now: datetime, quarterly: bool) -> Period:
        probe = self.period_for_year_month(now.year, now.month)
        probe = Period(probe.year, 4) if quarterly else probe
        while not self.is_reported(probe, now):
            probe = probe.shift(-1)
        return probe


# --- US/Eastern without a tz database: DST runs 2nd Sunday of March to 1st Sunday of November.

def _nth_weekday(year: int, month: int, weekday: int, n: int) -> date:
    first = date(year, month, 1)
    return first + timedelta(days=(weekday - first.weekday()) % 7 + 7 * (n - 1))


def eastern_offset(moment: datetime) -> int:
    start = _nth_weekday(moment.year, 3, 6, 2)
    end = _nth_weekday(moment.year, 11, 6, 1)
    return 4 if start <= moment.date() < end else 5


def to_utc(local_eastern: datetime) -> datetime:
    return (local_eastern + timedelta(hours=eastern_offset(local_eastern))).replace(tzinfo=timezone.utc)


# --- NYSE trading calendar.

def _easter(year: int) -> date:
    a, b, c = year % 19, year // 100, year % 100
    d, e = b // 4, b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = c // 4, c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    return date(year, month, (h + l - 7 * m + 114) % 31 + 1)


def _observed(day: date) -> date:
    if day.weekday() == 5:
        return day - timedelta(days=1)
    if day.weekday() == 6:
        return day + timedelta(days=1)
    return day


@lru_cache(maxsize=None)
def nyse_holidays(year: int) -> frozenset[date]:
    days = {
        _observed(date(year, 1, 1)),
        _nth_weekday(year, 1, 0, 3),
        _nth_weekday(year, 2, 0, 3),
        _easter(year) - timedelta(days=2),
        month_end(year, 5) - timedelta(days=month_end(year, 5).weekday()),
        _observed(date(year, 7, 4)),
        _nth_weekday(year, 9, 0, 1),
        _nth_weekday(year, 11, 3, 4),
        _observed(date(year, 12, 25)),
    }
    if year >= 2022:
        days.add(_observed(date(year, 6, 19)))
    return frozenset(d for d in days if d.year == year)


def is_trading_day(day: date) -> bool:
    return day.weekday() < 5 and day not in nyse_holidays(day.year)


def trading_days(start: date, end: date) -> list[date]:
    out, day = [], start
    while day <= end:
        if is_trading_day(day):
            out.append(day)
        day += timedelta(days=1)
    return out


def previous_trading_day(day: date) -> date:
    while not is_trading_day(day):
        day -= timedelta(days=1)
    return day


def last_completed_session(now: datetime) -> date:
    """The latest trading day whose close (16:00 ET) is at or before ``now``."""
    local = now.replace(tzinfo=None) - timedelta(hours=eastern_offset(now.replace(tzinfo=None)))
    day = local.date() if local.time() >= time(16, 0) else local.date() - timedelta(days=1)
    return previous_trading_day(day)
