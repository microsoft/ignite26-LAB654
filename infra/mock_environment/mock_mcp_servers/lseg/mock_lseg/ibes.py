"""``qa_ibes_consensus``: I/B/E/S actuals, consensus estimates and the measure catalogue.

One tool, a batch of ``requests``; each has a ``dataType`` and ``options``. Any
unknown measure in the batch fails the whole call with a 404, as the live service does.
"""

from __future__ import annotations

import base64
from dataclasses import dataclass
from functools import cached_property
from typing import Any

from mockfin import CompanyView, Period, to_utc
from mockmcp import Tool, ToolOutput, UpstreamError, tidy, us_datetime
from mockmcp.tool import CallContext

from .common import Issues, LsegData, envelope

DATA_TYPES = ("qa_ibes_actuals", "qa_ibes_consensus", "qa_ibes_measures")
PERIOD_TYPES = ("Quarter", "Year")
MAX_REQUESTS = 20
MAX_PERIOD_SPAN = 12
NORM_CURRENCY = {"normCurrPermID": 500110, "normCurrDesc": "USD"}
REGION = {"regionPermID": 110173, "regionDesc": "AMER"}

# I/B/E/S measure code -> shared finance model metric. Catalogue codes without a
# mapping are valid requests that simply have no coverage for these companies.
METRIC_FOR = {
    "EPS": "eps", "REV": "revenue", "EBITDA": "ebitda", "NPROFIT": "net_income",
    "OPROFIT": "oper_income", "NDEBT": "net_debt", "EPSREP": "eps_rep", "DPS": "dps",
    "BVPS": "bvps", "ROE": "roe", "ROA": "roa", "TA": "total_assets", "SEQUITY": "equity",
}

EXAMPLE = (
    '{"requests":[{"dataType":"qa_ibes_consensus","options":{"ticker":"MSFT","measures":["Eps","Rev"],'
    '"periodType":"Year","periodIndexStart":1,"periodIndexEnd":3}}]}'
)


@dataclass(frozen=True)
class Measure:
    code: str
    measure_code: str
    description: str
    norm_scale: int
    scale_desc: str
    unit_type: str

    @property
    def id(self) -> int:
        return int(self.code)

    @property
    def per_share(self) -> bool:
        return self.scale_desc == "Per Share"

    @property
    def consensus_key(self) -> str:
        return self.measure_code.lower() + ("PerShare" if self.per_share else "Million")

    def as_catalog_row(self) -> dict:
        return {
            "code": self.code, "measureCode": self.measure_code, "measureDescription": self.description,
            "normScale": self.norm_scale, "scaleDesc": self.scale_desc, "unitType": self.unit_type,
        }


class MeasureCatalog:
    def __init__(self, rows: list[dict]) -> None:
        self.rows = sorted(
            (Measure(r["code"], r["measureCode"], r["measureDescription"], r["normScale"], r["scaleDesc"], r["unitType"]) for r in rows),
            key=lambda m: m.code,
        )
        self._by_code = {m.measure_code: m for m in self.rows}

    def find(self, name: str) -> Measure | None:
        return self._by_code.get(str(name).strip().upper())


class QaIbesConsensus(Tool):
    name = "qa_ibes_consensus"
    title = "LSEG I/B/E/S estimates and actuals"
    description = (
        "Query LSEG I/B/E/S (QA Direct) data in a batch. Each request has a dataType and options:\n"
        "- qa_ibes_consensus: consensus (mean) estimates. options: ticker, tickerType ('Ticker'), measures "
        "(e.g. ['Eps','Rev','Ebitda','Nprofit','Oprofit','Ndebt','Epsrep','Dps']), periodType ('Quarter'|'Year'), "
        "periodIndexStart, periodIndexEnd (0 = most recently reported period, 1 = next period/FY1, 2 = FY2 ...).\n"
        "- qa_ibes_actuals: reported actuals. options: ticker, tickerType, measures, periodType, pIndex "
        "(0 = latest reported, -1 = the one before, ...).\n"
        "- qa_ibes_measures: the measure catalogue. options: limit (default 100), cursor, search (plain text).\n"
        f"Example: {EXAMPLE}"
    )
    validate_args = False
    input_schema = {
        "type": "object",
        "properties": {
            "requests": {
                "type": "array",
                "minItems": 1,
                "maxItems": MAX_REQUESTS,
                "description": "QA IBES operations to run.",
                "items": {
                    "type": "object",
                    "properties": {
                        "dataType": {"type": "string", "enum": list(DATA_TYPES)},
                        "options": {
                            "type": "object",
                            "properties": {
                                "ticker": {"type": "string", "description": "I/B/E/S ticker, e.g. NVDA."},
                                "tickerType": {"type": "string", "description": "Identifier type. Default 'Ticker'."},
                                "measures": {"type": "array", "items": {"type": "string"}},
                                "periodType": {"type": "string", "enum": list(PERIOD_TYPES)},
                                "periodIndexStart": {"type": "integer"},
                                "periodIndexEnd": {"type": "integer"},
                                "pIndex": {"type": "integer", "maximum": 0},
                                "limit": {"type": "integer", "minimum": 1, "maximum": 1000},
                                "cursor": {"type": "string"},
                                "search": {"type": "string"},
                            },
                        },
                    },
                    "required": ["dataType", "options"],
                },
            }
        },
        "required": ["requests"],
    }

    def __init__(self, data: LsegData) -> None:
        self.data = data

    @cached_property
    def catalog(self) -> MeasureCatalog:
        return MeasureCatalog(self.data.store.view("ibes_measures")["measures"])

    def run(self, args: dict, ctx: CallContext) -> ToolOutput:
        requests = self._validate(args)
        out = [
            {"dataType": r["dataType"], "options": r["options"], "response": self._handle(r["dataType"], r["options"], ctx)}
            for r in requests
        ]
        return ToolOutput(out, {"data": out})

    # -- validation ---------------------------------------------------------------

    def _validate(self, args: dict) -> list[dict]:
        requests = args.get("requests")
        issues = Issues()
        if not isinstance(requests, list) or not requests:
            issues.add(f"requests must be an array of QA IBES operations. Valid request example: {EXAMPLE}")
            issues.raise_if_any()
        if len(requests) > MAX_REQUESTS:
            issues.add(f"requests must contain at most {MAX_REQUESTS} operations")
        for i, req in enumerate(requests):
            where = f"requests[{i}]"
            if not isinstance(req, dict):
                issues.add(f"{where} must be an object with dataType and options")
                continue
            data_type, options = req.get("dataType"), req.get("options", {})
            if data_type not in DATA_TYPES:
                issues.add(f"{where}.dataType must be one of: {', '.join(DATA_TYPES)}")
                continue
            if not isinstance(options, dict):
                issues.add(f"{where}.options must be an object")
                continue
            req.setdefault("options", options)
            if data_type == "qa_ibes_measures":
                self._check_measures_options(issues, where, options)
            else:
                self._check_company_options(issues, where, data_type, options)
        issues.raise_if_any()
        for req in requests:
            for name in req["options"].get("measures", []) if req["dataType"] != "qa_ibes_measures" else []:
                if self.catalog.find(name) is None:
                    raise UpstreamError(f"Unknown measure {name}", 404)
        return requests

    @staticmethod
    def _check_company_options(issues: Issues, where: str, data_type: str, o: dict) -> None:
        if not isinstance(o.get("ticker"), str) or not o["ticker"].strip():
            issues.add(f"{where}.options.ticker is required")
        measures = o.get("measures")
        if not isinstance(measures, list) or not measures or not all(isinstance(m, str) and m for m in measures):
            issues.add(f"{where}.options.measures must be a non-empty array of measure names (e.g. [\"Eps\",\"Rev\"])")
        if o.get("periodType", "Year") not in PERIOD_TYPES:
            issues.add(f"{where}.options.periodType must be one of: {', '.join(PERIOD_TYPES)}")
        if data_type == "qa_ibes_actuals":
            p = o.get("pIndex", 0)
            if isinstance(p, bool) or not isinstance(p, int) or p > 0:
                issues.add(f"{where}.options.pIndex must be an integer less than or equal to 0")
            return
        start, end = o.get("periodIndexStart", 1), o.get("periodIndexEnd", o.get("periodIndexStart", 1))
        for name, value in (("periodIndexStart", start), ("periodIndexEnd", end)):
            if isinstance(value, bool) or not isinstance(value, int):
                issues.add(f"{where}.options.{name} must be an integer")
                return
        if end < start:
            issues.add(f"{where}.options.periodIndexEnd must be greater than or equal to periodIndexStart")
        elif end - start + 1 > MAX_PERIOD_SPAN:
            issues.add(f"{where}.options period range must span at most {MAX_PERIOD_SPAN} periods")

    @staticmethod
    def _check_measures_options(issues: Issues, where: str, o: dict) -> None:
        limit = o.get("limit", 100)
        if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= 1000:
            issues.add(f"{where}.options.limit must be an integer between 1 and 1000")
        if "search" in o and not isinstance(o["search"], str):
            issues.add(f"{where}.options.search must be a string")
        if "cursor" in o and _decode_cursor(o["cursor"]) is None:
            issues.add(f"{where}.options.cursor is not a valid cursor")

    # -- handlers -----------------------------------------------------------------

    def _handle(self, data_type: str, o: dict, ctx: CallContext) -> dict:
        if data_type == "qa_ibes_measures":
            return self._measures(o, ctx)
        measures = [self.catalog.find(m) for m in o["measures"]]
        view = self.data.world.resolve(o["ticker"])
        if data_type == "qa_ibes_actuals":
            return self._actuals(view, o, measures, ctx)
        return self._consensus(view, o, measures, ctx)

    def _actuals(self, view: CompanyView | None, o: dict, measures: list[Measure], ctx: CallContext) -> dict:
        quarterly = o.get("periodType", "Year") == "Quarter"
        p_index = o.get("pIndex", 0)
        ids = ", ".join(str(m.id) for m in measures)
        label = "Quarter" if quarterly else "Annual"
        rows: list[dict] = []
        ticker = o["ticker"].strip().upper()
        if view is not None:
            ticker = view.company.ticker
            period = view.relative(p_index, ctx.clock.now, quarterly)
            scope = "Quarter" if quarterly else "Year"
            for m in measures:
                if self.data.has_gap(ticker, "actuals", scope, m.measure_code):
                    continue
                value = _actual(view, m, period, ctx)
                if value is not None:
                    rows.append(self._actual_row(view, m, period, value))
            rows.sort(key=lambda r: r["measureCode"])
        message = f"Retrieved {len(rows)} actuals for ticker '{ticker}' (Measures: {ids}, Period Type: {label}, pIndex: {p_index})"
        data = {
            "ticker": ticker, "period": str(p_index), "type": label,
            "measures": ",".join(m.measure_code for m in measures), "actuals": rows,
        }
        return {"data": data, **envelope(ctx, message, "actuals", o)}

    def _actual_row(self, view: CompanyView, m: Measure, period: Period, value: float) -> dict:
        announced = view.calendar.announcement(period)
        local, utc = us_datetime(announced), us_datetime(to_utc(announced))
        return {
            "date": us_datetime(view.calendar.period_end(period)),
            "ibesticker": view.company.ticker,
            "estpermid": view.company.ibes_estpermid,
            "measureid": m.id,
            "measureCode": m.measure_code,
            "measureDesc": m.description,
            "pertype": 4 if period.is_annual else 3,
            "periodDesc": "Year" if period.is_annual else "Quarter",
            **NORM_CURRENCY,
            **REGION,
            "effectiveDate": local,
            "effectiveDateUTC": utc,
            "announceDate": local,
            "announceDateUTC": utc,
            "unitType": m.unit_type,
            "normActValue": value,
            "scale": m.scale_desc,
            "fiscalIndex": 0 if period.is_annual else period.quarter,
        }

    def _consensus(self, view: CompanyView | None, o: dict, measures: list[Measure], ctx: CallContext) -> dict:
        quarterly = o.get("periodType", "Year") == "Quarter"
        start = o.get("periodIndexStart", 1)
        end = o.get("periodIndexEnd", start)
        estimates: list[dict] = []
        ticker = o["ticker"].strip().upper()
        if view is not None:
            ticker = view.company.ticker
            for index in range(start, end + 1):
                period = view.relative(index, ctx.clock.now, quarterly)
                values = {}
                for m in measures:
                    if self.data.has_gap(ticker, "consensus", period.key, m.measure_code):
                        continue
                    metric = METRIC_FOR.get(m.measure_code)
                    consensus = view.consensus(metric, period, ctx.clock.now) if metric else None
                    if consensus is not None:
                        values[m.consensus_key] = {"value": tidy(consensus.mean, 5), "unitType": m.unit_type, **NORM_CURRENCY}
                if values:
                    estimates.append({
                        "date": view.calendar.period_end(period).isoformat(),
                        "estPermID": view.company.ibes_estpermid,
                        "periodIndex": index,
                        "fiscalIndex": 0 if period.is_annual else period.quarter,
                        "measures": values,
                    })
        codes = ", ".join(m.measure_code for m in measures)
        label = "Quarter" if quarterly else "Annual"
        message = (
            f"Retrieved {len(estimates)} fiscal period consensus estimates for ticker '{ticker}' "
            f"(Measures: {codes}, Period Type: {label}, periodIndex between {start} and {end})"
        )
        data = {
            "ticker": ticker, "periodIndexStart": start, "periodIndexEnd": end,
            "periodType": o.get("periodType", "Year"), "estimates": estimates,
        }
        return {"data": data, **envelope(ctx, message, "consensus", o)}

    def _measures(self, o: dict, ctx: CallContext) -> dict:
        search = o.get("search")
        if search is not None and any(ch in search for ch in "*?%"):
            raise UpstreamError("Wildcard search is not supported", 404)
        rows = self.catalog.rows
        if search:
            needle = search.strip().lower()
            rows = [m for m in rows if needle in m.measure_code.lower() or needle in m.description.lower()]
        limit = o.get("limit", 100)
        offset = _decode_cursor(o["cursor"]) if "cursor" in o else 0
        page = rows[offset: offset + limit]
        more = offset + limit < len(rows)
        message = f"Retrieved {len(page)} IBES measures matching the supplied criteria from Redis."
        return {
            "limit": limit,
            "nextCursor": base64.b64encode(str(offset + limit).encode()).decode() if more else None,
            "data": [m.as_catalog_row() for m in page],
            "rowCount": len(page),
            **envelope(ctx, message, "measures", o),
        }


def _actual(view: CompanyView, m: Measure, period: Period, ctx: CallContext) -> float | int | None:
    metric = METRIC_FOR.get(m.measure_code)
    value = view.actual(metric, period, ctx.clock.now) if metric else None
    return tidy(value, 4 if m.per_share else 3)


def _decode_cursor(cursor: Any) -> int | None:
    try:
        value = int(base64.b64decode(str(cursor), validate=True).decode())
    except Exception:
        return None
    return value if value >= 0 else None
