"""``FactSet_Fundamentals``: reported financials by fiscal period with audit-card links.

Rows come from the shared finance model, so any company, metric code, periodicity
and fiscal window works. Annual rows recorded in the live trace replay exactly.
"""

from __future__ import annotations

from datetime import date
from urllib.parse import quote

from mockfin import CompanyView, Period
from mockmcp import Tool, round_sig
from mockmcp.tool import CallContext

from .common import (
    REQUEST_ID_SCHEMA, FactsetData, Issues, MetricDef, check_request_id, choice, compact, id_list, parse_date,
)

MAX_IDS = 250
MAX_METRICS = 1600
PERIODICITIES = ("ANN", "QTR", "SEMI", "LTM")
EARLIEST_YEAR = 2005
AUDIT_BASE = "https://my.apps.factset.com/company-security/audit-card/v1"


class FactsetFundamentals(Tool):
    name = "FactSet_Fundamentals"
    title = "FactSet fundamentals"
    description = (
        "Reported fundamentals (income statement, balance sheet, cash flow, ratios) by fiscal period. "
        "data_type: 'fundamentals'. ids: up to 250. metrics: exact codes from FactSet_Metrics "
        "(e.g. FF_SALES, FF_GROSS_MGN). periodicity: ANN, QTR, SEMI or LTM. fiscalPeriodStart/fiscalPeriodEnd: "
        "YYYY-MM-DD bounds on fiscal period end dates; omit both for the latest period. audit: 'AUDIT_CARD'."
    )
    validate_args = False
    input_schema = {
        "type": "object",
        "properties": {
            "data_type": {"type": "string", "enum": ["fundamentals"]},
            "ids": {"type": "array", "items": {"type": "string"}, "minItems": 1, "maxItems": MAX_IDS},
            "metrics": {"type": "array", "items": {"type": "string"}, "minItems": 1, "maxItems": MAX_METRICS},
            "periodicity": {"type": "string", "enum": list(PERIODICITIES), "default": "QTR"},
            "fiscalPeriodStart": {"type": "string", "format": "date"},
            "fiscalPeriodEnd": {"type": "string", "format": "date"},
            "currency": {"type": "string", "default": "LOCAL"},
            "updateType": {"type": "string", "enum": ["RP", "RF"], "default": "RP"},
            "audit": {"type": "string", "enum": ["AUDIT_CARD"]},
            "request_id": REQUEST_ID_SCHEMA,
        },
        "required": ["data_type", "ids", "metrics"],
    }

    def __init__(self, data: FactsetData) -> None:
        self.data = data

    def run(self, args: dict, ctx: CallContext) -> dict:
        ids, metrics, periodicity, start, end, audit = self._validate(args)
        rows = []
        for identifier in ids:
            view = self.data.resolve(identifier)
            if view is None:
                continue
            periods = periods_in_window(view, periodicity, start, end, ctx.clock.now)
            for metric in metrics:
                for period in periods:
                    row = self._row(identifier, view, metric, periodicity, period, audit)
                    if row is not None:
                        rows.append(row)
        return {"data": rows}

    def _validate(self, args: dict):
        issues = Issues()
        check_request_id(issues, args)
        if args.get("data_type") != "fundamentals":
            issues.add("data_type is required and must be 'fundamentals'")
        ids = id_list(issues, args, MAX_IDS)
        codes = args.get("metrics")
        if isinstance(codes, str):
            codes = [c for c in codes.split(",")]
        metrics: list[MetricDef] = []
        if not isinstance(codes, list) or not codes:
            issues.add("metrics is required: an array of FactSet metric codes discovered with FactSet_Metrics")
        else:
            if len(codes) > MAX_METRICS:
                issues.add(f"metrics supports at most {MAX_METRICS} codes per request")
            for code in codes:
                metric = self.data.catalog.get(code)
                if metric is None:
                    issues.add(f"Unknown metric code '{code}'. Discover exact codes with FactSet_Metrics")
                elif metric.product != "fundamentals":
                    issues.add(f"'{code}' is an estimates metric; use FactSet_EstimatesConsensus or a fundamentals code")
                else:
                    metrics.append(metric)
        periodicity = choice(issues, args, "periodicity", PERIODICITIES, default="QTR")
        start = parse_date(issues, "fiscalPeriodStart", args.get("fiscalPeriodStart"))
        end = parse_date(issues, "fiscalPeriodEnd", args.get("fiscalPeriodEnd"))
        if start and end and start > end:
            issues.add("fiscalPeriodStart must be on or before fiscalPeriodEnd")
        currency = str(args.get("currency", "LOCAL")).upper()
        if currency not in ("LOCAL", "USD"):
            issues.add("currency must be LOCAL or USD for this dataset (all covered companies report in USD)")
        audit = args.get("audit")
        if audit is not None and audit != "AUDIT_CARD":
            issues.add("audit must be 'AUDIT_CARD' when provided")
        issues.raise_if_any()
        return ids, metrics, periodicity, start, end, audit == "AUDIT_CARD"

    def _row(self, identifier: str, view: CompanyView, metric: MetricDef, periodicity: str, period: Period, audit: bool):
        cal = view.calendar
        ltm = periodicity == "LTM"
        recorded = self.data.observed_fundamentals.get(
            (view.company.ticker, metric.code, periodicity, period.year, period.quarter)
        )
        value = recorded if recorded is not None else self.data.metric_value(view, metric, period, ltm=ltm)
        if value is None:
            return None
        fiscal_end = cal.period_end(period)
        report_end = cal.actual_end(period)
        length = (report_end - cal.actual_end(period.shift(-4))).days if ltm else cal.length_days(period)
        row = {
            "requestId": identifier,
            "fsymId": view.company.fsym_security_id,
            "metric": metric.code,
            "periodicity": periodicity,
            "fiscalPeriod": period.quarter,
            "fiscalYear": period.year,
            "fiscalPeriodLength": length,
            "fiscalEndDate": fiscal_end.isoformat(),
            "reportDate": report_end.isoformat(),
            "epsReportDate": cal.announcement(period).date().isoformat(),
            "updateType": "Final",
            "currency": "USD",
            "value": value if recorded is not None else round_sig(value, 15),
        }
        if audit:
            row["audit"] = {"card": audit_card(identifier, metric.code, periodicity, fiscal_end)}
        return row


def audit_card(identifier: str, code: str, periodicity: str, fiscal_end: date) -> dict:
    day = compact(fiscal_end)
    formula = f"{code}({periodicity},{day},{day},,RP,USD)"
    encoded = quote(formula, safe="()")
    link = (
        f"{AUDIT_BASE}/{quote(identifier, safe='-')}?formula={encoded}"
        "&expandLevel=1&enableSourceLinks=true&navigationTarget=blank"
    )
    return {"link": link, "formula": formula, "identifier": identifier}


def periods_in_window(view: CompanyView, periodicity: str, start: date | None, end: date | None, now) -> list[Period]:
    """Reported fiscal periods whose fiscal end date falls in [start, end]; latest only when unbounded."""
    if periodicity == "SEMI":
        return []  # US filers report quarterly; FactSet has no semi-annual periods for them.
    quarterly = periodicity in ("QTR", "LTM")
    latest = view.latest(now, quarterly=quarterly)
    if start is None and end is None:
        return [latest]
    cal = view.calendar
    if start is None:  # Only an end bound: the last reported period on or before it.
        probe = latest
        while cal.period_end(probe) > end and probe.year >= EARLIEST_YEAR:
            probe = probe.shift(-1)
        return [probe] if probe.year >= EARLIEST_YEAR else []
    first = cal.period_for_year_month(start.year, start.month).shift(-1)
    first = Period(max(first.year, EARLIEST_YEAR), 1 if quarterly else None)
    out, probe = [], first
    while probe <= latest:
        if cal.period_end(probe) >= start and (end is None or cal.period_end(probe) <= end):
            out.append(probe)
        probe = probe.shift(1)
    return out
