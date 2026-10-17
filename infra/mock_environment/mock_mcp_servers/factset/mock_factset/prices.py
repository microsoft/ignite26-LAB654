"""``FactSet_GlobalPrices``: end-of-day prices (any range, frequency, currency, adjustment) and current market value."""

from __future__ import annotations

from datetime import date

from mockfin import CompanyView
from mockfin.calendars import is_trading_day, last_completed_session, previous_trading_day
from mockfin.prices import HISTORY_START
from mockmcp import Tool, tidy
from mockmcp.tool import CallContext

from .common import REQUEST_ID_SCHEMA, FactsetData, Issues, check_request_id, choice, id_list, parse_date

MAX_IDS_RANGE = 50
MAX_IDS_SINGLE = 500
DATA_TYPES = ("prices", "market_value")
FREQUENCIES = {"D": None, "W": "W", "AM": "M", "AQ": "Q", "AY": "Y"}
ADJUSTMENTS = ("SPLIT", "SPINOFF", "DIVADJ", "UNSPLIT")
QUARTERLY_DIVIDEND_DRAG = 0.0025
# Fixed USD conversion table: deterministic, so the same request always prices the same way.
FX_PER_USD = {"USD": 1.0, "LOCAL": 1.0, "EUR": 0.92, "GBP": 0.79, "JPY": 149.5, "CHF": 0.88,
              "CAD": 1.37, "INR": 83.9, "CNY": 7.2, "AUD": 1.52}


class FactsetGlobalPrices(Tool):
    name = "FactSet_GlobalPrices"
    title = "FactSet global prices"
    description = (
        "data_type 'prices': end-of-day open/high/low/close and volume (thousands). startDate/endDate YYYY-MM-DD "
        "(omit both for the latest session), frequency D, W, AM, AQ or AY, currency (LOCAL, USD, EUR, GBP, JPY, ...), "
        "adjust SPLIT (default), SPINOFF, DIVADJ or UNSPLIT. Up to 50 ids for a date range, 500 for one day. "
        "data_type 'market_value': current market capitalisation in USD millions; it takes no date or currency inputs."
    )
    validate_args = False
    input_schema = {
        "type": "object",
        "properties": {
            "data_type": {"type": "string", "enum": list(DATA_TYPES)},
            "ids": {"type": "array", "items": {"type": "string"}, "minItems": 1, "maxItems": MAX_IDS_SINGLE},
            "startDate": {"type": "string", "format": "date"},
            "endDate": {"type": "string", "format": "date"},
            "frequency": {"type": "string", "enum": list(FREQUENCIES), "default": "D"},
            "currency": {"type": "string", "default": "LOCAL"},
            "adjust": {"type": "string", "enum": list(ADJUSTMENTS), "default": "SPLIT"},
            "request_id": REQUEST_ID_SCHEMA,
        },
        "required": ["data_type", "ids"],
    }

    def __init__(self, data: FactsetData) -> None:
        self.data = data

    def run(self, args: dict, ctx: CallContext) -> dict:
        issues = Issues()
        check_request_id(issues, args)
        data_type = args.get("data_type")
        if data_type not in DATA_TYPES:
            issues.add(f"data_type is required: one of {', '.join(DATA_TYPES)}")
            issues.raise_if_any()
        if data_type == "market_value":
            return self._market_value(issues, args, ctx)
        return self._prices(issues, args, ctx)

    def _market_value(self, issues: Issues, args: dict, ctx: CallContext) -> dict:
        for name in ("startDate", "endDate", "frequency", "adjust"):
            if args.get(name) is not None:
                issues.add(f"{name} is not supported for market_value, which returns the current value only; "
                           "use data_type 'prices' for history")
        if str(args.get("currency") or "USD").upper() not in ("USD", "LOCAL"):
            issues.add("market_value is returned in USD only; omit currency")
        ids = id_list(issues, args, MAX_IDS_SINGLE)
        issues.raise_if_any()
        session = last_completed_session(ctx.clock.now)
        rows = []
        for identifier in ids:
            view = self.data.resolve(identifier)
            value = view.market_cap(ctx.clock.now) if view else None
            if value is None:
                continue
            rows.append({"requestId": identifier, "fsymId": view.company.fsym_security_id,
                         "date": session.isoformat(), "currency": "USD", "marketValue": tidy(value, 2)})
        return {"data": rows}

    def _prices(self, issues: Issues, args: dict, ctx: CallContext) -> dict:
        start = parse_date(issues, "startDate", args.get("startDate"))
        end = parse_date(issues, "endDate", args.get("endDate"))
        frequency = choice(issues, args, "frequency", FREQUENCIES, default="D")
        currency = str(args.get("currency") or "LOCAL").upper()
        if currency not in FX_PER_USD:
            issues.add(f"currency '{currency}' is not supported; use one of {', '.join(FX_PER_USD)}")
        adjust = choice(issues, args, "adjust", ADJUSTMENTS, default="SPLIT")
        session = last_completed_session(ctx.clock.now)
        if start and end and start > end:
            issues.add("startDate must be on or before endDate")
        for name, value in (("startDate", start), ("endDate", end)):
            if value and value > ctx.clock.today:
                issues.add(f"{name} {value.isoformat()} is in the future; the latest session is {session.isoformat()}")
            if value and value < HISTORY_START:
                issues.add(f"{name} is before the start of available history ({HISTORY_START.isoformat()})")
        single = (start is None and end is None) or start == end or (start is None and end is not None)
        ids = id_list(issues, args, MAX_IDS_SINGLE if single else MAX_IDS_RANGE)
        issues.raise_if_any()

        if single:
            day = end or start or session
            day = min(day, session)
            start = end = day if is_trading_day(day) else previous_trading_day(day)
            frequency = "D"
        end = min(end or session, session)
        rows = []
        for identifier in ids:
            view = self.data.resolve(identifier)
            if view is None:
                continue
            for bar in self._bars(view, start, end, frequency, ctx):
                rows.append(self._row(identifier, view, bar, currency, adjust, session))
        return {"data": rows}

    @staticmethod
    def _bars(view: CompanyView, start: date, end: date, frequency: str, ctx: CallContext):
        unit = FREQUENCIES[frequency]
        if unit is None:
            return view.prices.daily(start, end, ctx.clock.now)
        return view.prices.aggregate(unit, start, end, ctx.clock.now)

    def _row(self, identifier: str, view: CompanyView, bar, currency: str, adjust: str, session: date) -> dict:
        price_factor, volume_factor = self._adjustment(view.company.ticker, bar.date, adjust, session)
        fx = FX_PER_USD[currency]
        price = lambda v: tidy(v * price_factor * fx, 4)  # noqa: E731
        return {
            "requestId": identifier,
            "fsymId": view.company.fsym_security_id,
            "date": bar.date.isoformat(),
            "currency": "USD" if currency == "LOCAL" else currency,
            "price": price(bar.close),
            "priceOpen": price(bar.open),
            "priceHigh": price(bar.high),
            "priceLow": price(bar.low),
            "volume": tidy(bar.volume * volume_factor / 1000, 3),
        }

    def _adjustment(self, ticker: str, day: date, adjust: str, session: date) -> tuple[float, float]:
        if adjust == "UNSPLIT":
            ratio = 1.0
            for split in self.data.store.view("corporate_actions")["splits"].get(ticker, []):
                if day < date.fromisoformat(split["date"]):
                    ratio *= split["ratio"]
            return ratio, 1 / ratio
        if adjust == "DIVADJ":
            quarters = max(0, (session - day).days) / 91.3
            return (1 - QUARTERLY_DIVIDEND_DRAG) ** quarters, 1.0
        return 1.0, 1.0
