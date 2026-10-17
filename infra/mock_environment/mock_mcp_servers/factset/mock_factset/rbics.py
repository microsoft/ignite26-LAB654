"""``FactSet_RBICS``: revenue-based industry classification (focus) and revenue by business segment."""

from __future__ import annotations

from datetime import date

from mockfin import CompanyView, Period
from mockmcp import Seeded, Tool, stable_hash, tidy
from mockmcp.tool import CallContext

from .common import REQUEST_ID_SCHEMA, FactsetData, Issues, check_request_id, choice, id_list, parse_date

MAX_IDS = 2500
LEVELS = (1, 2, 3, 4, 5, 6)
DATA_TYPES = ("entity_focus", "entity_revenue")
EARLIEST_YEAR = 2010


def rbics_id(path: list[str]) -> str:
    """Deterministic nested ids: each level appends two digits derived from its name."""
    return "".join(str(stable_hash(name) % 90 + 10) for name in path)


class FactsetRbics(Tool):
    name = "FactSet_RBICS"
    title = "FactSet RBICS"
    description = (
        "Revenue Business Industry Classification. data_type 'entity_focus': each company's primary industry at "
        "levels 1-6 (levels array, includeNames, optional date). data_type 'entity_revenue': revenue split by "
        "RBICS segment for each fiscal year (startDate/endDate YYYY-MM-DD, level 1-6, default 6); omit dates for "
        f"the latest year. ids: up to {MAX_IDS}."
    )
    validate_args = False
    input_schema = {
        "type": "object",
        "properties": {
            "data_type": {"type": "string", "enum": list(DATA_TYPES)},
            "ids": {"type": "array", "items": {"type": "string"}, "minItems": 1, "maxItems": MAX_IDS},
            "date": {"type": "string", "format": "date"},
            "levels": {"type": "array", "items": {"type": "integer", "minimum": 1, "maximum": 6}},
            "includeNames": {"type": "boolean", "default": True},
            "startDate": {"type": "string", "format": "date"},
            "endDate": {"type": "string", "format": "date"},
            "level": {"type": "integer", "minimum": 1, "maximum": 6, "default": 6},
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
        ids = id_list(issues, args, MAX_IDS)
        if data_type == "entity_revenue":
            return self._revenue(issues, ids, args, ctx)
        return self._focus(issues, ids, args, ctx)

    def _segments(self, view: CompanyView) -> dict | None:
        return self.data.store.view("rbics")["companies"].get(view.company.ticker)

    def _focus(self, issues: Issues, ids: list[str], args: dict, ctx: CallContext) -> dict:
        levels = args.get("levels") or list(LEVELS)
        if not isinstance(levels, list) or any(isinstance(l, bool) or l not in LEVELS for l in levels):
            issues.add("levels must be an array of integers between 1 and 6")
        names = args.get("includeNames", True)
        if not isinstance(names, bool):
            issues.add("includeNames must be a boolean")
        as_of = parse_date(issues, "date", args.get("date"))
        if as_of and as_of > ctx.clock.today:
            issues.add("date cannot be in the future")
        issues.raise_if_any()
        rows = []
        for identifier in ids:
            view = self.data.resolve(identifier)
            seg = self._segments(view) if view else None
            if seg is None:
                continue
            path = _focus_path(seg)
            row = {"requestId": identifier, "fsymId": view.company.fsym_entity_id}
            for level in sorted(set(levels)):
                row[f"l{level}Id"] = rbics_id(path[:level])
                if names:
                    row[f"l{level}Name"] = path[level - 1]
            seed = Seeded("factset-rbics", view.company.ticker)
            row["effectiveStartDate"] = date(seed.integer(2016, 2022, "start"), seed.integer(1, 12, "month"), 1).isoformat()
            row["effectiveEndDate"] = None
            rows.append(row)
        return {"data": rows}

    def _revenue(self, issues: Issues, ids: list[str], args: dict, ctx: CallContext) -> dict:
        start = parse_date(issues, "startDate", args.get("startDate"))
        end = parse_date(issues, "endDate", args.get("endDate"))
        if start and end and start > end:
            issues.add("startDate must be on or before endDate")
        level = args.get("level", 6)
        if isinstance(level, bool) or level not in LEVELS:
            issues.add("level must be an integer between 1 and 6")
        issues.raise_if_any()
        rows = []
        for identifier in ids:
            view = self.data.resolve(identifier)
            seg = self._segments(view) if view else None
            if seg is None:
                continue
            for period in _years(view, start, end, ctx.clock.now):
                rows.extend(self._revenue_rows(identifier, view, seg, period, level))
        return {"data": rows}

    def _revenue_rows(self, identifier: str, view: CompanyView, seg: dict, period: Period, level: int) -> list[dict]:
        revenue = view.financials.value("revenue", period)
        if revenue is None:
            return []
        seed = Seeded("factset-rbics-revenue", view.company.ticker, period.year)
        drifted = {s["path"]: s["share"] * (1 + seed.gauss(0.0, 0.06, s["path"])) for s in seg["segments"]}
        total = sum(drifted.values())
        grouped: dict[tuple, float] = {}
        for path, share in drifted.items():
            key = tuple(path.split(" > ")[:level])
            grouped[key] = grouped.get(key, 0.0) + share / total
        end = view.calendar.period_end(period).isoformat()
        return [
            {"requestId": identifier, "fsymId": view.company.fsym_entity_id, "periodEndDate": end, "level": level,
             "rbicsId": rbics_id(list(key)), "rbicsName": key[-1], "revenuePercent": tidy(share * 100, 2),
             "revenue": tidy(revenue * share, 2), "currency": "USD"}
            for key, share in sorted(grouped.items(), key=lambda kv: -kv[1])
        ]


def _focus_path(seg: dict) -> list[str]:
    focus = seg.get("focus") or []
    for s in seg["segments"]:
        parts = s["path"].split(" > ")
        if parts[-len(focus):] == focus:
            return parts
    return seg["segments"][0]["path"].split(" > ")


def _years(view: CompanyView, start: date | None, end: date | None, now) -> list[Period]:
    latest = view.latest(now, quarterly=False)
    if start is None and end is None:
        return [latest]
    cal, out = view.calendar, []
    for year in range(max(EARLIEST_YEAR, (start or end).year - 1), latest.year + 1):
        p = Period(year)
        if (start is None or cal.period_end(p) >= start) and (end is None or cal.period_end(p) <= end):
            out.append(p)
    if start is None and out:
        return out[-1:]  # Only an end date: the last fiscal year on or before it.
    return out
