"""``historical_pricing_summaries``: interday bars (daily, weekly, monthly, quarterly, yearly).

Daily bars come from the shared price model; longer intervals aggregate them over
calendar buckets. Recorded monthly rows replay verbatim. Rows are newest first.
"""

from __future__ import annotations

import re
from datetime import date, timedelta
from functools import cached_property

from mockfin import Bar, MonthBar
from mockfin.calendars import add_months, last_completed_session
from mockmcp import Tool, ToolOutput
from mockmcp.tool import CallContext

from .common import Issues, LsegData, parse_date, positive_int

INTERVALS = {"P1D": "D", "P1W": "W", "P1M": "M", "P3M": "Q", "P1Y": "Y"}
ALIASES = {"DAILY": "P1D", "WEEKLY": "P1W", "MONTHLY": "P1M", "QUARTERLY": "P3M", "YEARLY": "P1Y", "ANNUAL": "P1Y"}
MAX_COUNT = 10_000
DEFAULT_COUNT = 20
TENOR = re.compile(r"^(\d+)([DWMY])$", re.IGNORECASE)
UNKNOWN_UNIVERSE = {"code": "TS.Interday.UserRequestError.70005", "message": "The universe does not exist."}

# Header name -> bar attribute. Aggregated-interval extremes fall back to the plain
# field on a daily bar (the live service does this for the "blending" entry).
FIELD = {
    "DATE": "date", "TRDPRC_1": "close", "HIGH_1": "high", "LOW_1": "low", "ACVOL_UNS": "volume",
    "OPEN_PRC": "open", "BID": "bid", "ASK": "ask", "TRNOVR_UNS": "turnover", "VWAP": "vwap",
    "BLKCOUNT": "blk_count", "BLKVOLUM": "blk_volume", "NUM_MOVES": "num_moves", "VWAP_VOL": "vwap_vol",
    "ACVOL_DEC": "acvol_dec", "VWAP_OPEN": "vwap_open", "VWAP_HIGH": "vwap_high", "VWAP_LOW": "vwap_low",
    "OPEN_BID": "bid_open", "BID_HIGH_1": "bid_high", "BID_LOW_1": "bid_low",
    "OPEN_ASK": "ask_open", "ASK_HIGH_1": "ask_high", "ASK_LOW_1": "ask_low",
}
FALLBACK = {"vwap_open": "vwap", "vwap_high": "vwap", "vwap_low": "vwap", "bid_open": "bid", "bid_high": "bid",
            "bid_low": "bid", "ask_open": "ask", "ask_high": "ask", "ask_low": "ask"}
CONSTANT = {"TRD_STATUS": 1, "SALTIM": 72000, "NAVALUE": None}


class HistoricalPricingSummaries(Tool):
    name = "historical_pricing_summaries"
    ui_resource = "ui://lseg/pricing"
    title = "LSEG historical pricing summaries"
    description = (
        "Interday pricing summaries (OHLC, volume, VWAP, bid/ask, turnover) for one or more instruments. "
        "universe: RIC(s), comma-separated (e.g. 'LITW.O' or 'LITW.O,ADTM.O'). interval: P1D | P1W | P1M | P3M | P1Y. "
        "Window: either tenor (e.g. '10D', '3M', '1Y') or start/end dates (YYYY-MM-DD); end defaults to the "
        "latest completed session. count: max rows per instrument, newest first. fields: optional list of "
        "field names to return (e.g. ['TRDPRC_1','ACVOL_UNS'])."
    )
    validate_args = False
    input_schema = {
        "type": "object",
        "properties": {
            "universe": {"type": "string", "description": "RIC or comma-separated RICs, e.g. LITW.O"},
            "interval": {"type": "string", "enum": list(INTERVALS), "default": "P1D"},
            "tenor": {"type": "string", "description": "Look-back window, e.g. 10D, 6M, 1Y."},
            "start": {"type": "string", "format": "date"},
            "end": {"type": "string", "format": "date"},
            "count": {"type": "integer", "minimum": 1, "maximum": MAX_COUNT},
            "fields": {"type": "array", "items": {"type": "string"}},
        },
        "required": ["universe"],
    }

    def __init__(self, data: LsegData) -> None:
        self.data = data

    @cached_property
    def seed(self) -> dict:
        return self.data.store.view("pricing")

    def run(self, args: dict, ctx: CallContext) -> ToolOutput:
        rics, interval, start, end, count, fields = self._validate(args, ctx)
        out = [self._one(ric, interval, start, end, count, fields, ctx) for ric in rics]
        return ToolOutput(out, {"data": out})

    # -- validation ---------------------------------------------------------------

    def _validate(self, args: dict, ctx: CallContext):
        issues = Issues()
        universe = args.get("universe")
        rics = [r.strip() for r in universe.split(",") if r.strip()] if isinstance(universe, str) else []
        if not rics:
            issues.add("universe is required (e.g. 'LITW.O')")
        raw_interval = str(args.get("interval", "P1D")).strip().upper()
        interval = ALIASES.get(raw_interval, raw_interval)
        if interval not in INTERVALS:
            issues.add(f"interval must be one of: {', '.join(INTERVALS)}")
        if "count" in args:
            positive_int(issues, "count", args["count"], MAX_COUNT)
        end = parse_date(issues, "end", args.get("end")) or last_completed_session(ctx.clock.now)
        start = parse_date(issues, "start", args.get("start"))
        tenor = args.get("tenor")
        if tenor is not None:
            match = TENOR.match(str(tenor).strip())
            if not match:
                issues.add("tenor must look like 10D, 2W, 6M or 1Y")
            elif start is None:
                start = _back(end, int(match.group(1)), match.group(2).upper())
        if start and start > end:
            issues.add("start must be on or before end")
        fields = args.get("fields")
        if fields is not None and (not isinstance(fields, list) or not all(isinstance(f, str) for f in fields)):
            issues.add("fields must be an array of field names")
        issues.raise_if_any()
        count = args.get("count")
        if start is None:
            count = count or DEFAULT_COUNT
            start = _back(end, count + 1, {"D": "W", "W": "W", "M": "M", "Q": "Q", "Y": "Y"}[INTERVALS[interval]])
        return rics, interval, start, end, count, [f.upper() for f in fields] if fields else None

    # -- response -----------------------------------------------------------------

    def _one(self, ric: str, interval: str, start: date, end: date, count, fields, ctx: CallContext) -> dict:
        view = self.data.world.resolve(ric)
        if view is None:
            return {"universe": {"ric": ric}, "interval": interval, "status": UNKNOWN_UNIVERSE}
        daily = interval == "P1D"
        all_headers = self.seed["headers"]["daily" if daily else "monthly"]
        headers = [h for h in all_headers if fields is None or h["name"] == "DATE" or h["name"] in fields]
        unit = INTERVALS[interval]
        bars = view.prices.daily(start, end, ctx.clock.now) if daily else view.prices.aggregate(unit, start, end, ctx.clock.now)
        rows = [self._row(headers, b) for b in reversed(bars)]
        if unit == "M":
            rows = self._replay(view.company.ric, headers, rows)
        if count:
            rows = rows[:count]
        latest = view.prices.latest(ctx.clock.now)
        return {
            "universe": {"ric": ric},
            "interval": interval,
            **self.seed["envelope"],
            "headers": headers,
            "data": rows,
            "meta": {"blendingEntry": {"headers": headers, "data": [self._row(headers, latest)] if latest else []}},
        }

    def _replay(self, ric: str, headers: list[dict], rows: list[list]) -> list[list]:
        observed = {r["DATE"]: r for r in self.seed["monthly_observed"].get(ric, [])}
        names = [h["name"] for h in headers]
        return [[observed[row[0]].get(n) for n in names] if row[0] in observed else row for row in rows]

    @staticmethod
    def _row(headers: list[dict], bar: Bar | MonthBar) -> list:
        return [_value(bar, h["name"]) for h in headers]


def _value(bar: Bar | MonthBar, name: str):
    if name in CONSTANT:
        return CONSTANT[name]
    attr = FIELD.get(name)
    if attr is None:
        return None
    if not hasattr(bar, attr):
        attr = FALLBACK.get(attr, attr)
    value = getattr(bar, attr, None)
    if attr == "date":
        return value.isoformat()
    if attr == "turnover":
        return int(round(value))
    return value


def _back(end: date, n: int, unit: str) -> date:
    if unit == "D":
        return end - timedelta(days=n)
    if unit == "W":
        return end - timedelta(weeks=n)
    months = {"M": 1, "Q": 3, "Y": 12}[unit] * n
    year, month = add_months(end.year, end.month, -months)
    return date(year, month, 1)
