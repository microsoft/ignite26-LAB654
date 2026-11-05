"""``important_company_news``: significant headlines for companies over a date window.

Recorded LITW headlines replay inside their window. Everything else is built from
the shared finance model so it stays consistent with the other tools: earnings
releases (on the modelled announcement dates) and large daily price moves.
"""

from __future__ import annotations

from datetime import date, datetime, time, timedelta
from functools import cached_property

from mockfin import CompanyView, to_utc
from mockfin.calendars import last_completed_session
from mockmcp import Seeded, Tool, iso_z
from mockmcp.tool import CallContext

from .common import Issues, LsegData, parse_date

DEFAULT_DAYS = 30
MAX_DAYS = 400
DEFAULT_LIMIT = 10  # the live service returned 10 headlines for a 30-day window
MAX_LIMIT = 50
BIG_MOVE = 0.03
URL = "https://api.refinitiv.com/data/news/v1/stories/urn:newsml:reuters.com:{day}:n{code}:1"


class ImportantCompanyNews(Tool):
    name = "important_company_news"
    title = "LSEG important company news"
    description = (
        "Significant Reuters headlines for one or more companies. companyRics: RIC or comma-separated RICs "
        "(e.g. 'LITW.O'). start/end: YYYY-MM-DD window (default: the last 30 days). headlineOnly: true to omit "
        f"story text. limit: max headlines (default {DEFAULT_LIMIT}). Headlines are returned newest first."
    )
    validate_args = False
    input_schema = {
        "type": "object",
        "properties": {
            "companyRics": {"type": "string"},
            "start": {"type": "string", "format": "date"},
            "end": {"type": "string", "format": "date"},
            "headlineOnly": {"type": "boolean", "default": True},
            "limit": {"type": "integer", "minimum": 1, "maximum": MAX_LIMIT, "default": DEFAULT_LIMIT},
        },
        "required": ["companyRics"],
    }

    def __init__(self, data: LsegData) -> None:
        self.data = data

    @cached_property
    def recorded(self) -> dict[str, list[dict]]:
        return self.data.store.view("news")["headlines"]

    def run(self, args: dict, ctx: CallContext) -> dict:
        rics, start, end, headline_only, limit = self._validate(args, ctx)
        headlines: list[dict] = []
        for ric in rics:
            view = self.data.world.resolve(ric)
            if view is not None:
                headlines.extend(self._for(view, start, end, headline_only, ctx))
        headlines.sort(key=lambda h: h["firstCreated"], reverse=True)
        return {"headlines": headlines[:limit], "retrievedAt": ctx.clock.iso()}

    def _validate(self, args: dict, ctx: CallContext):
        issues = Issues()
        raw = args.get("companyRics")
        if isinstance(raw, list):
            raw = ",".join(map(str, raw))
        rics = [r.strip() for r in raw.split(",") if r.strip()] if isinstance(raw, str) else []
        if not rics:
            issues.add("companyRics is required (e.g. 'LITW.O')")
        end = parse_date(issues, "end", args.get("end")) or ctx.clock.today
        start = parse_date(issues, "start", args.get("start")) or end - timedelta(days=DEFAULT_DAYS)
        if start > end:
            issues.add("start must be on or before end")
        elif (end - start).days > MAX_DAYS:
            issues.add(f"date range must be at most {MAX_DAYS} days")
        headline_only = args.get("headlineOnly", True)
        if not isinstance(headline_only, bool):
            issues.add("headlineOnly must be a boolean")
        limit = args.get("limit", DEFAULT_LIMIT)
        if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= MAX_LIMIT:
            issues.add(f"limit must be an integer between 1 and {MAX_LIMIT}")
        issues.raise_if_any()
        return rics, start, end, headline_only, limit

    def _for(self, view: CompanyView, start: date, end: date, headline_only: bool, ctx: CallContext) -> list[dict]:
        ticker = view.company.ticker
        recorded = self.recorded.get(ticker, [])
        covered = {h["firstCreated"][:10] for h in recorded}
        window_start = min(covered) if covered else None
        out = [dict(h) for h in recorded if start.isoformat() <= h["firstCreated"][:10] <= end.isoformat()]
        for moment, text, story in self._generated(view, start, end, ctx):
            if window_start and moment.date().isoformat() >= window_start:
                continue  # the recorded headlines are authoritative for their window
            out.append(_headline(ticker, moment, text, "" if headline_only else story))
        return out

    def _generated(self, view: CompanyView, start: date, end: date, ctx: CallContext):
        company, now = view.company, ctx.clock.now
        name = company.short_name
        # Earnings releases.
        latest = view.latest(now, quarterly=True)
        for i in range(0, 8):
            period = latest.shift(-i)
            announced = to_utc(view.calendar.announcement(period)).replace(tzinfo=None)
            if not start <= announced.date() <= end:
                continue
            revenue = view.financials.value("revenue", period)
            prior = view.financials.value("revenue", period.shift(-4))
            eps = view.financials.value("eps", period)
            if revenue is None:
                continue
            growth = f", up {100 * (revenue / prior - 1):.0f}% year on year" if prior and revenue > prior else ""
            label = f"Q{period.quarter} FY{period.year}"
            text = f"BRIEF-{name} Reports {label} Revenue Of ${revenue / 1000:.2f} Bln"
            story = (
                f"{company.name} reported {label} revenue of ${revenue / 1000:.2f} billion{growth}"
                + (f", and diluted EPS of ${eps:.2f}." if eps is not None else ".")
            )
            yield announced + timedelta(minutes=2), text, story
        # Large daily moves.
        last = min(end, last_completed_session(now))
        bars = view.prices.daily(start - timedelta(days=7), last, now)
        for prev, bar in zip(bars, bars[1:]):
            if bar.date < start or not prev.close:
                continue
            change = bar.close / prev.close - 1
            if abs(change) < BIG_MOVE:
                continue
            verb = "rise" if change > 0 else "fall"
            text = f"{name} shares {verb} {abs(change) * 100:.1f}%"
            story = f"{company.name} shares closed at ${bar.close:.2f}, {verb}ing {abs(change) * 100:.1f}% on the day."
            minute = Seeded("lseg", "news", company.ticker).integer(5, 55, bar.date.isoformat())
            yield datetime.combine(bar.date, time(20, minute)), text, story


def _headline(ticker: str, moment: datetime, text: str, story: str) -> dict:
    code = Seeded("lseg", "news-id", ticker).token(8, moment.isoformat(), text)
    stamp = iso_z(moment)
    return {
        "source": "RTRS", "language": "en", "headlineText": text, "story": story,
        "firstCreated": stamp, "versionCreated": stamp, "urgency": 3,
        "ldpStoryUrl": URL.format(day=moment.strftime("%Y%m%d"), code=code),
    }
