"""``FactSet_EstimatesConsensus``: broker consensus by fixed or rolling fiscal period, with history snapshots."""

from __future__ import annotations

import re
from datetime import date, timedelta

from mockfin import CompanyView, Period
from mockfin.calendars import month_end, trading_days
from mockmcp import Tool, tidy
from mockmcp.tool import CallContext

from .common import REQUEST_ID_SCHEMA, FactsetData, Issues, MetricDef, as_of, check_request_id, choice, id_list, parse_date

MAX_IDS = 3000
MAX_SNAPSHOTS = 400
ESTIMATE_TYPES = ("consensus_fixed", "consensus_rolling")
PERIODICITIES = ("ANN", "QTR")
FREQUENCIES = ("D", "W", "AM", "AQ", "AY")
FISCAL_PATTERN = re.compile(r"^(?:FY)?(\d{4})(?:/(?:Q)?([1-4])F?)?$", re.IGNORECASE)


class FactsetEstimatesConsensus(Tool):
    name = "FactSet_EstimatesConsensus"
    title = "FactSet consensus estimates"
    description = (
        "Broker consensus (mean, median, high, low, standard deviation, count, revisions) for ONE estimates metric "
        "per call (codes from FactSet_Metrics with data_products ['estimates'], e.g. EPS, SALES). "
        "estimate_type 'consensus_fixed': fiscalPeriodStart/fiscalPeriodEnd as 'YYYY' (annual) or 'YYYY/QF' "
        "(quarter, e.g. '2026/3F'). estimate_type 'consensus_rolling': relativeFiscalStart/relativeFiscalEnd "
        "integers (0 = latest reported, 1 = next period) with periodicity ANN or QTR. Optional startDate/endDate "
        "(YYYY-MM-DD) return consensus history snapshots at frequency D, W, AM, AQ or AY."
    )
    validate_args = False
    input_schema = {
        "type": "object",
        "properties": {
            "estimate_type": {"type": "string", "enum": list(ESTIMATE_TYPES)},
            "ids": {"type": "array", "items": {"type": "string"}, "minItems": 1, "maxItems": MAX_IDS},
            "metrics": {"type": "array", "items": {"type": "string"}, "minItems": 1, "maxItems": 1},
            "periodicity": {"type": "string", "enum": list(PERIODICITIES), "default": "ANN"},
            "fiscalPeriodStart": {"type": "string"},
            "fiscalPeriodEnd": {"type": "string"},
            "relativeFiscalStart": {"type": "integer"},
            "relativeFiscalEnd": {"type": "integer"},
            "startDate": {"type": "string", "format": "date"},
            "endDate": {"type": "string", "format": "date"},
            "frequency": {"type": "string", "enum": list(FREQUENCIES), "default": "AM"},
            "currency": {"type": "string", "default": "LOCAL"},
            "request_id": REQUEST_ID_SCHEMA,
        },
        "required": ["estimate_type", "ids", "metrics"],
    }

    def __init__(self, data: FactsetData) -> None:
        self.data = data

    def run(self, args: dict, ctx: CallContext) -> dict:
        req = self._validate(args, ctx.clock.today)
        rows = []
        for identifier in req["ids"]:
            view = self.data.resolve(identifier)
            if view is None:
                continue
            for snapshot in req["snapshots"]:
                now = as_of(snapshot)
                for period, relative in self._periods(view, req, now):
                    row = self._row(identifier, view, req["metric"], period, relative, snapshot, now)
                    if row:
                        rows.append(row)
        return {"data": rows}

    def _validate(self, args: dict, today: date) -> dict:
        issues = Issues()
        check_request_id(issues, args)
        kind = args.get("estimate_type")
        if kind not in ESTIMATE_TYPES:
            issues.add(f"estimate_type is required: one of {', '.join(ESTIMATE_TYPES)}")
        ids = id_list(issues, args, MAX_IDS)
        metric = self._metric(issues, args.get("metrics"))
        req: dict = {"ids": ids, "metric": metric, "kind": kind}
        if kind == "consensus_fixed":
            req["fixed"] = self._fixed(issues, args)
        elif kind == "consensus_rolling":
            req["periodicity"] = choice(issues, args, "periodicity", PERIODICITIES, default="ANN")
            req["rolling"] = self._rolling(issues, args)
        req["snapshots"] = self._snapshots(issues, args, today)
        currency = str(args.get("currency", "LOCAL")).upper()
        if currency not in ("LOCAL", "USD"):
            issues.add("currency must be LOCAL or USD for this dataset")
        issues.raise_if_any()
        return req

    def _metric(self, issues: Issues, codes) -> MetricDef | None:
        if isinstance(codes, str):
            codes = [codes]
        if not isinstance(codes, list) or not codes:
            issues.add("metrics is required: exactly one estimates metric code, e.g. ['EPS']")
            return None
        if len(codes) > 1:
            issues.add("FactSet_EstimatesConsensus accepts one metric per request; call it once per metric")
            return None
        metric = self.data.catalog.get(codes[0])
        if metric is None:
            issues.add(f"Unknown metric code '{codes[0]}'. Use FactSet_Metrics with data_products ['estimates']")
        elif metric.product != "estimates":
            issues.add(f"'{codes[0]}' is a fundamentals code. Use FactSet_Metrics with data_products ['estimates'] "
                       "to find the estimates code (e.g. EPS, SALES)")
            return None
        return metric

    def _fixed(self, issues: Issues, args: dict) -> tuple[Period, Period] | None:
        start, end = args.get("fiscalPeriodStart"), args.get("fiscalPeriodEnd")
        if start is None:
            issues.add("consensus_fixed requires fiscalPeriodStart ('YYYY' or 'YYYY/QF', e.g. '2026/3F')")
            return None
        first, last = _fiscal(issues, "fiscalPeriodStart", start), _fiscal(issues, "fiscalPeriodEnd", end or start)
        if not first or not last:
            return None
        if first.is_annual != last.is_annual:
            issues.add("fiscalPeriodStart and fiscalPeriodEnd must both be annual ('YYYY') or both quarterly ('YYYY/QF')")
            return None
        if first.ordinal() > last.ordinal():
            issues.add("fiscalPeriodStart must be on or before fiscalPeriodEnd")
            return None
        if last.ordinal() - first.ordinal() > 40:
            issues.add("fiscal period range is too wide; request at most 40 periods")
            return None
        return first, last

    def _rolling(self, issues: Issues, args: dict) -> tuple[int, int] | None:
        start, end = args.get("relativeFiscalStart"), args.get("relativeFiscalEnd")
        if start is None:
            issues.add("consensus_rolling requires relativeFiscalStart (integer; 1 = next fiscal period)")
            return None
        end = start if end is None else end
        if any(isinstance(v, bool) or not isinstance(v, int) for v in (start, end)):
            issues.add("relativeFiscalStart and relativeFiscalEnd must be integers")
            return None
        if start > end:
            issues.add("relativeFiscalStart must be less than or equal to relativeFiscalEnd")
            return None
        if end - start > 20:
            issues.add("relative fiscal range is too wide; request at most 20 periods")
            return None
        return start, end

    def _snapshots(self, issues: Issues, args: dict, today: date) -> list[date]:
        start = parse_date(issues, "startDate", args.get("startDate"))
        end = parse_date(issues, "endDate", args.get("endDate"))
        frequency = choice(issues, args, "frequency", FREQUENCIES, default="AM")
        for name, value in (("startDate", start), ("endDate", end)):
            if value and value > today:
                issues.add(f"{name} {value.isoformat()} is in the future; consensus history ends {today.isoformat()}")
        if start is None and end is None:
            return [today]
        start, end = start or end, end or today
        if start > end:
            issues.add("startDate must be on or before endDate")
            return []
        if start == end:
            return [start]
        points = snapshot_dates(start, end, frequency or "AM")
        if len(points) > MAX_SNAPSHOTS:
            issues.add(f"Too many snapshots ({len(points)}); narrow the date range or use a coarser frequency")
        return points or [end]

    def _periods(self, view: CompanyView, req: dict, now) -> list[tuple[Period, int]]:
        if req["kind"] == "consensus_fixed":
            first, last = req["fixed"]
            latest = view.latest(now, quarterly=not first.is_annual)
            out, probe = [], first
            while probe <= last:
                out.append((probe, probe.ordinal() - latest.ordinal()))
                probe = probe.shift(1)
            return out
        start, end = req["rolling"]
        quarterly = req["periodicity"] == "QTR"
        return [(view.relative(i, now, quarterly), i) for i in range(start, end + 1)]

    def _row(self, identifier, view: CompanyView, metric: MetricDef, period: Period, relative: int, snapshot, now):
        consensus = view.consensus(metric.field, period, now, vendor="factset")
        if consensus is None:
            return None
        return {
            "requestId": identifier,
            "fsymId": view.company.fsym_security_id,
            "metric": metric.code,
            "periodicity": "ANN" if period.is_annual else "QTR",
            "fiscalPeriod": period.quarter,
            "fiscalYear": period.year,
            "fiscalEndDate": view.calendar.period_end(period).isoformat(),
            "relativePeriod": relative,
            "estimateDate": snapshot.isoformat(),
            "currency": "USD",
            "mean": tidy(consensus.mean, 4),
            "median": tidy(consensus.median, 4),
            "standardDeviation": tidy(consensus.std, 4),
            "high": tidy(consensus.high, 4),
            "low": tidy(consensus.low, 4),
            "estimateCount": consensus.count,
            "up": consensus.up,
            "down": consensus.down,
        }


def _fiscal(issues: Issues, name: str, value) -> Period | None:
    match = FISCAL_PATTERN.match(str(value).strip()) if isinstance(value, (str, int)) else None
    if not match:
        issues.add(f"{name} must be 'YYYY' for a fiscal year or 'YYYY/QF' for a fiscal quarter (e.g. '2026/3F'); got {value!r}")
        return None
    year, quarter = int(match.group(1)), match.group(2)
    return Period(year, int(quarter) if quarter else None)


def snapshot_dates(start: date, end: date, frequency: str) -> list[date]:
    """Snapshot dates in [start, end]: trading days, Fridays, or calendar month/quarter/year ends."""
    if frequency == "D":
        return trading_days(start, end)
    if frequency == "W":
        first = start + timedelta(days=(4 - start.weekday()) % 7)
        return [first + timedelta(weeks=i) for i in range((end - first).days // 7 + 1)] if first <= end else []
    step = {"AM": 1, "AQ": 3, "AY": 12}[frequency]
    out, year, month = [], start.year, start.month
    while True:
        day = month_end(year, month)
        if day > end:
            break
        if day >= start and month % step == 0:
            out.append(day)
        year, month = (year + 1, 1) if month == 12 else (year, month + 1)
    return out
