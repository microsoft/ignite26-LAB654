"""``qa_company_fundamentals``: Worldscope reported fundamentals by item code.

Recorded rows replay verbatim; any other company, item or year is computed from the
shared finance model. Items with no coverage are listed in the "No data found" note.
"""

from __future__ import annotations

from functools import cached_property

from mockfin import CompanyView, Period
from mockmcp import Tool, ToolOutput, iso_z, tidy
from mockmcp.tool import CallContext

from .common import Issues, LsegData, envelope

FREQS = ("A", "Q")
UNIT_SCALE = {"USD": 1_000_000, "SHARES": 1_000_000, "USD/SHARE": 1, "PERCENT": 1}
UNIT_DIGITS = {"USD": 0, "SHARES": 0, "USD/SHARE": 4, "PERCENT": 2}


class QaCompanyFundamentals(Tool):
    name = "qa_company_fundamentals"
    ui_resource = "ui://lseg/fundamentals"
    title = "LSEG Worldscope company fundamentals"
    description = (
        "Retrieve Worldscope company fundamentals (QA Direct) by item code. Each request: "
        "{dataType:'qa_company_fundamentals', options:{identifier (ticker, e.g. 'LITW'), type ('Ticker'), "
        "measures (comma-separated Worldscope item codes, e.g. '1001,1100,5201'), year (comma-separated fiscal "
        "years, e.g. '2023,2024,2025'), freq ('A' annual | 'Q' quarterly)}}. Common items: 1001 net sales, "
        "1051 COGS, 1100 gross income, 1250 operating income, 1551 net income, 2999 total assets, "
        "3255 total debt, 3501 common equity, 4860 operating cash flow, 5101 DPS, 5201 EPS, 8306 gross margin, "
        "18198 EBITDA."
    )
    validate_args = False
    input_schema = {
        "type": "object",
        "properties": {
            "requests": {
                "type": "array",
                "minItems": 1,
                "maxItems": 20,
                "items": {
                    "type": "object",
                    "properties": {
                        "dataType": {"type": "string", "enum": ["qa_company_fundamentals"]},
                        "options": {
                            "type": "object",
                            "properties": {
                                "identifier": {"type": "string"},
                                "type": {"type": "string", "description": "Identifier type, e.g. 'Ticker'."},
                                "measures": {"type": "string", "description": "Comma-separated Worldscope item codes."},
                                "year": {"type": "string", "description": "Comma-separated fiscal years."},
                                "freq": {"type": "string", "enum": list(FREQS)},
                            },
                            "required": ["identifier", "measures", "year"],
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
    def worldscope(self) -> dict:
        return self.data.store.view("worldscope")

    @cached_property
    def observed(self) -> dict[tuple, dict]:
        return {(r["qaCode"], r["item"], r["freq"], r["year"], r["seq"]): r for r in self.worldscope["observed"]}

    def run(self, args: dict, ctx: CallContext) -> ToolOutput:
        requests = self._validate(args)
        out = [
            {"dataType": r["dataType"], "options": _echo(r["options"]), "response": self._handle(r["options"], ctx)}
            for r in requests
        ]
        return ToolOutput(out, {"data": out})

    def _validate(self, args: dict) -> list[dict]:
        issues = Issues()
        requests = args.get("requests")
        if not isinstance(requests, list) or not requests:
            issues.add("requests must be an array of QA company fundamentals operations")
            issues.raise_if_any()
        for i, req in enumerate(requests):
            where = f"requests[{i}]"
            o = req.get("options") if isinstance(req, dict) else None
            if not isinstance(req, dict) or req.get("dataType") != "qa_company_fundamentals" or not isinstance(o, dict):
                issues.add(f"{where} must be {{dataType:'qa_company_fundamentals', options:{{...}}}}")
                continue
            if not isinstance(o.get("identifier"), str) or not o["identifier"].strip():
                issues.add(f"{where}.options.identifier is required")
            if _ints(o.get("measures")) is None:
                issues.add(f"{where}.options.measures must be a comma-separated list of numeric item codes")
            if _ints(o.get("year")) is None:
                issues.add(f"{where}.options.year must be a comma-separated list of years")
            if o.get("freq", "A") not in FREQS:
                issues.add(f"{where}.options.freq must be one of: {', '.join(FREQS)}")
        issues.raise_if_any()
        return requests

    def _handle(self, o: dict, ctx: CallContext) -> dict:
        items, years, freq = _ints(o["measures"]), _ints(o["year"]), o.get("freq", "A")
        measures_text, year_text = _text(o["measures"]), _text(o["year"])
        view = self.data.world.resolve(o["identifier"])
        if view is None:
            message = f"No QA Code found for {o.get('type', 'Ticker')} '{o['identifier']}'"
            return {"data": None, **envelope(ctx, message, "fundamentals", o, success=False)}
        qa = view.company.qa_code
        rows, missing = [], []
        for item in sorted(set(items)):
            found = [row for year in sorted(set(years)) for row in self._rows(view, item, freq, year, ctx)]
            rows.extend(found)
            if not found:
                missing.append(item)
        missing.sort(key=items.index)
        message = f"Retrieved {len(rows)} fundamental records for QA Code {qa} (Measures: {measures_text}, Freq: {freq}, Year: {year_text})"
        if missing:
            message += f"; No data found for measure(s): {', '.join(map(str, missing))}"
        data = {"qaCode": qa, "measures": measures_text, "freq": freq, "year": year_text, "fundamentals": rows}
        return {"data": data, **envelope(ctx, message, "fundamentals", o)}

    def _rows(self, view: CompanyView, item: int, freq: str, year: int, ctx: CallContext) -> list[dict]:
        spec = self.worldscope["items"].get(str(item))
        if spec is None or item in self.worldscope["unavailable_items"]:
            return []
        periods = [Period(year, None)] if freq == "A" else Period(year, None).quarters()
        out = []
        for seq, period in enumerate(periods, start=1):
            if not view.is_reported(period, ctx.clock.now):
                continue
            recorded = self.observed.get((view.company.qa_code, item, freq, year, seq))
            if recorded is not None:
                out.append(dict(recorded))
                continue
            name, units, metric = spec
            value = view.financials.value(metric, period)
            if value is None:
                continue
            announced = view.calendar.announcement(period)
            out.append({
                "qaCode": view.company.qa_code, "item": item, "freq": freq, "year": year, "seq": seq,
                "fiscalPeriodEndDate": iso_z(view.calendar.actual_end(period)),
                "epsReportDate": iso_z(announced.date()),
                "periodUpdateFlag": "3", "periodUpdateDescription": "Final", "currencyOfDocument": "USD",
                "value": tidy(value * UNIT_SCALE[units], UNIT_DIGITS[units]),
                "itemUnits": units, "itemName": name,
            })
        return out


def _ints(value) -> list[int] | None:
    parts = value if isinstance(value, list) else str(value or "").split(",")
    try:
        out = [int(str(p).strip()) for p in parts if str(p).strip()]
    except ValueError:
        return None
    return out or None


def _text(value) -> str:
    return ",".join(str(v).strip() for v in value) if isinstance(value, list) else str(value)


def _echo(options: dict) -> dict:
    """The live service echoes options with ``type`` moved to the end."""
    out = {k: v for k, v in options.items() if k != "type"}
    if "type" in options:
        out["type"] = options["type"]
    return out
