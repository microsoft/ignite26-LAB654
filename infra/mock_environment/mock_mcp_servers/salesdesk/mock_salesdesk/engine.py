"""Record access shared by GraphQL, SOQL, REST and the viewer: field paths, relationships, filters, sorting and
display formatting, with the date literals and ranges SalesDesk supports evaluated against the mock's clock in the
org's time zone (US Eastern)."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Any, Iterable

from .schema import OBJECTS, PREFIXES, child_relationship, find_field, parent_relationship
from .store import Org
from .timeutil import display_date, display_datetime, et_date, parse_date, parse_dt, to_et


class QueryError(Exception):
    """A malformed filter, unknown field or bad value; the caller turns it into the API's error shape."""

    def __init__(self, message: str, code: str = "INVALID_FIELD") -> None:
        super().__init__(message)
        self.code = code


@dataclass
class Ctx:
    org: Org
    now: datetime

    @property
    def today(self) -> date:
        return to_et(self.now).date()


# --- rows ---------------------------------------------------------------------------------------------------------

_VIEW_COPY = ("Id", "Subject", "ActivityDate", "Status", "Priority", "Description", "StartDateTime", "EndDateTime",
              "DurationInMinutes", "Location", "CompletedDateTime", "IsClosed", "WhoId", "WhatId", "AccountId",
              "OwnerId", "CreatedDate", "LastModifiedDate")


def _activity_view(rec: dict, is_task: bool) -> dict:
    row = {k: rec.get(k) for k in _VIEW_COPY}
    row["ActivityType"] = rec.get("Type")
    row["ActivitySubtype"] = "Task" if is_task else "Event"
    row["IsTask"] = is_task
    if not is_task:
        row["IsClosed"] = None
        row["Status"] = None
    return row


def rows(ctx: Ctx, obj: str) -> list[dict]:
    """All records of ``obj``; ActivityHistory and OpenActivity are computed views over Task and Event."""
    if obj in ("ActivityHistory", "OpenActivity"):
        history = obj == "ActivityHistory"
        out = [_activity_view(t, True) for t in ctx.org.records("Task") if bool(t.get("IsClosed")) == history]
        for event in ctx.org.records("Event"):
            ended = (parse_dt(event.get("EndDateTime")) or ctx.now) < ctx.now
            if ended == history:
                out.append(_activity_view(event, False))
        return out
    return list(ctx.org.records(obj))


def last_activity(ctx: Ctx, obj: str, rec: dict) -> str | None:
    """LastActivityDate: the latest closed task or past event linked to the record."""
    key = {"Account": "AccountId", "Contact": "WhoId", "Opportunity": "WhatId"}.get(obj)
    if not key:
        return rec.get("LastActivityDate")
    days = [r.get("ActivityDate") for r in rows(ctx, "ActivityHistory") if r.get(key) == rec["Id"]]
    days = [d for d in days if d]
    return max(days) if days else None


# --- field access -------------------------------------------------------------------------------------------------

def object_of(record_id: str | None) -> str | None:
    return PREFIXES.get(str(record_id or "")[:3])


def follow(ctx: Ctx, obj: str, rec: dict, rel: str) -> tuple[str, dict] | None:
    """Parent record through relationship ``rel`` (Owner, Account, Who, What…), or None."""
    hit = parent_relationship(obj, rel, case_insensitive=True)
    if not hit:
        raise QueryError(f"Didn't understand relationship '{rel}' on {obj}")
    target = ctx.org.get(rec.get(hit[0]))
    return target if target and target[0] in hit[2] else None


def value(ctx: Ctx, obj: str, rec: dict | None, name: str) -> Any:
    """Field value by API name, computing the fields that depend on other records."""
    if rec is None:
        return None
    if name == "LastActivityDate":
        return last_activity(ctx, obj, rec)
    if name == "Name" and obj == "Organization":
        return rec.get("Name")
    return rec.get(name)


def path_value(ctx: Ctx, obj: str, rec: dict, path: str) -> Any:
    """Value of a dotted path like ``Account.Owner.Name``; field names are case-insensitive."""
    parts = path.split(".")
    current_obj, current = obj, rec
    for rel in parts[:-1]:
        hit = follow(ctx, current_obj, current, rel)
        if hit is None:
            return None
        current_obj, current = hit
    meta = find_field(current_obj, parts[-1])
    if meta is None:
        raise QueryError(f"No such column '{parts[-1]}' on entity '{current_obj}'")
    return value(ctx, current_obj, current, meta[0])


def field_type(obj: str, path: str) -> str | None:
    parts = path.split(".")
    current = obj
    for rel in parts[:-1]:
        hit = parent_relationship(current, rel, case_insensitive=True)
        if not hit:
            return None
        current = hit[2][0]
    meta = find_field(current, parts[-1])
    return meta[2] if meta else None


def children(ctx: Ctx, obj: str, rec: dict, rel: str) -> tuple[str, list[dict]]:
    hit = child_relationship(obj, rel, case_insensitive=True)
    if not hit:
        raise QueryError(f"Didn't understand relationship '{rel}' on {obj}")
    child_obj, _, fk = hit
    return child_obj, [r for r in rows(ctx, child_obj) if r.get(fk) == rec["Id"]]


# --- date literals and ranges -------------------------------------------------------------------------------------

def _quarter_start(day: date) -> date:
    return date(day.year, 3 * ((day.month - 1) // 3) + 1, 1)


def _add_months(day: date, months: int) -> date:
    total = day.year * 12 + day.month - 1 + months
    return date(total // 12, total % 12 + 1, 1)


def literal_range(ctx: Ctx, literal: str, n: int | None = None) -> tuple[date, date]:
    """Inclusive (start, end) dates for a SalesDesk date literal such as TODAY, LAST_N_DAYS:7 or THIS_QUARTER."""
    today = ctx.today
    key = literal.upper()
    week = today - timedelta(days=(today.weekday() + 1) % 7)  # weeks start on Sunday in en_US
    month = today.replace(day=1)
    quarter = _quarter_start(today)
    year = date(today.year, 1, 1)
    simple = {
        "TODAY": (today, today), "YESTERDAY": (today - timedelta(1), today - timedelta(1)),
        "TOMORROW": (today + timedelta(1), today + timedelta(1)),
        "THIS_WEEK": (week, week + timedelta(6)), "LAST_WEEK": (week - timedelta(7), week - timedelta(1)),
        "NEXT_WEEK": (week + timedelta(7), week + timedelta(13)),
        "THIS_MONTH": (month, _add_months(month, 1) - timedelta(1)),
        "LAST_MONTH": (_add_months(month, -1), month - timedelta(1)),
        "NEXT_MONTH": (_add_months(month, 1), _add_months(month, 2) - timedelta(1)),
        "THIS_QUARTER": (quarter, _add_months(quarter, 3) - timedelta(1)),
        "LAST_QUARTER": (_add_months(quarter, -3), quarter - timedelta(1)),
        "NEXT_QUARTER": (_add_months(quarter, 3), _add_months(quarter, 6) - timedelta(1)),
        "THIS_YEAR": (year, date(today.year, 12, 31)), "LAST_YEAR": (date(today.year - 1, 1, 1), year - timedelta(1)),
        "NEXT_YEAR": (date(today.year + 1, 1, 1), date(today.year + 1, 12, 31)),
        "LAST_90_DAYS": (today - timedelta(90), today), "NEXT_90_DAYS": (today + timedelta(1), today + timedelta(90)),
        "THIS_FISCAL_QUARTER": (quarter, _add_months(quarter, 3) - timedelta(1)),
        "THIS_FISCAL_YEAR": (year, date(today.year, 12, 31)),
    }
    if key in simple:
        return simple[key]
    if n is None:
        raise QueryError(f"Unknown date literal {literal}", "INVALID_QUERY_FILTER_OPERATOR")
    if key == "LAST_N_DAYS":
        return today - timedelta(n), today
    if key == "NEXT_N_DAYS":
        return today + timedelta(1), today + timedelta(n)
    if key == "N_DAYS_AGO":
        return today - timedelta(n), today - timedelta(n)
    if key == "LAST_N_WEEKS":
        return week - timedelta(7 * n), week - timedelta(1)
    if key == "NEXT_N_WEEKS":
        return week + timedelta(7), week + timedelta(7 * n + 6)
    if key == "LAST_N_MONTHS":
        return _add_months(month, -n), month - timedelta(1)
    if key == "NEXT_N_MONTHS":
        return _add_months(month, 1), _add_months(month, n + 1) - timedelta(1)
    raise QueryError(f"Unknown date literal {literal}", "INVALID_QUERY_FILTER_OPERATOR")


@dataclass
class DateRange:
    start: date
    end: date
    # GraphQL n-day ranges compare against "today ± n" with gte/lte (how the skills use them), not the range edge.
    anchor: date | None = None


def is_date_type(dtype: str | None) -> bool:
    return dtype in ("DATE", "DATETIME")


def _comparable(actual: Any, dtype: str | None) -> Any:
    if actual is None:
        return None
    if dtype == "DATE":
        return parse_date(actual)
    if dtype == "DATETIME":
        return parse_dt(actual)
    if isinstance(actual, bool):
        return actual
    if isinstance(actual, (int, float)):
        return float(actual)
    return str(actual).lower()


def _coerce(expected: Any, dtype: str | None) -> Any:
    if expected is None:
        return None
    if isinstance(expected, DateRange):
        return expected
    if dtype == "DATE":
        parsed = parse_date(expected) if isinstance(expected, str) else expected
        if parsed is None:
            raise QueryError(f"Invalid date value: {expected}", "INVALID_QUERY_FILTER_OPERATOR")
        return parsed
    if dtype == "DATETIME":
        if isinstance(expected, str) and len(expected) == 10:
            day = parse_date(expected)
            return DateRange(day, day) if day else None
        parsed = parse_dt(expected) if isinstance(expected, str) else expected
        if parsed is None:
            raise QueryError(f"Invalid datetime value: {expected}", "INVALID_QUERY_FILTER_OPERATOR")
        return parsed
    if isinstance(expected, bool):
        return expected
    if isinstance(expected, (int, float)):
        return float(expected)
    if dtype in ("INT", "DOUBLE", "CURRENCY", "PERCENT") and isinstance(expected, str):
        try:
            return float(expected)
        except ValueError:
            raise QueryError(f"Invalid number: {expected}", "INVALID_QUERY_FILTER_OPERATOR") from None
    if dtype == "BOOLEAN" and isinstance(expected, str):
        return expected.lower() == "true"
    return str(expected).lower()


def like_regex(pattern: str) -> re.Pattern:
    out = []
    for ch in pattern:
        out.append(".*" if ch == "%" else "." if ch == "_" else re.escape(ch))
    return re.compile("^" + "".join(out) + "$", re.IGNORECASE | re.DOTALL)


_OPS = {"eq", "ne", "gt", "gte", "lt", "lte", "in", "nin", "like", "nlike", "includes"}


def compare(op: str, actual: Any, expected: Any, dtype: str | None) -> bool:
    """Apply one operator; dates on DATETIME fields compare by the org-local (US Eastern) day."""
    op = op.lower()
    if op not in _OPS:
        raise QueryError(f"Unknown operator '{op}'", "INVALID_QUERY_FILTER_OPERATOR")
    if op in ("in", "nin"):
        values = expected if isinstance(expected, list) else [expected]
        hit = any(compare("eq", actual, v, dtype) for v in values)
        return hit if op == "in" else not hit
    if op in ("like", "nlike"):
        if actual is None:
            return op == "nlike"
        hit = bool(like_regex(str(expected)).match(str(actual)))
        return hit if op == "like" else not hit
    if op == "includes":
        return actual is not None and any(str(v).lower() in str(actual).lower().split(";") for v in expected)
    exp = _coerce(expected, dtype)
    if isinstance(exp, DateRange):
        day = et_date(actual) if dtype == "DATETIME" else parse_date(actual)
        if day is None:
            return op == "ne"
        low = high = exp.anchor
        low = low or exp.start
        high = high or exp.end
        return {"eq": exp.start <= day <= exp.end, "ne": not exp.start <= day <= exp.end, "gt": day > high,
                "gte": day >= low, "lt": day < low, "lte": day <= high}[op]
    act = _comparable(actual, dtype)
    if op == "eq":
        return act == exp
    if op == "ne":
        return act != exp
    if act is None or exp is None:
        return False
    try:
        return {"gt": act > exp, "gte": act >= exp, "lt": act < exp, "lte": act <= exp}[op]
    except TypeError:
        return False
    except KeyError:
        raise QueryError(f"Unknown operator {op}", "INVALID_QUERY_FILTER_OPERATOR") from None


# --- GraphQL-style filters (also used by the viewer) --------------------------------------------------------------

def gql_value(ctx: Ctx, raw: Any, op: str) -> Any:
    """Unwrap ``{value}``, ``{literal}`` and ``{range}`` filter values."""
    if isinstance(raw, dict):
        if "value" in raw:
            return raw["value"]
        if "literal" in raw:
            start, end = literal_range(ctx, str(raw["literal"]))
            return DateRange(start, end)
        if "range" in raw:
            spec = raw["range"] or {}
            (kind, n), = list(spec.items())[:1] or [("last_n_days", 0)]
            n = int(n)
            start, end = literal_range(ctx, kind.upper(), n)
            anchor = ctx.today + timedelta(n) if kind.lower().startswith("next") else ctx.today - timedelta(n)
            if op in ("lte", "lt") and kind.lower().startswith("last"):
                anchor = ctx.today
            return DateRange(start, end, anchor if op != "eq" else None)
    if isinstance(raw, list):
        return [gql_value(ctx, v, op) for v in raw]
    return raw


def check_where(obj: str, where: dict) -> None:
    """Static check of a GraphQL ``where`` (unknown fields or operators), so errors don't depend on data."""
    for key, cond in where.items():
        lower = key.lower()
        if lower in ("and", "or"):
            for c in cond if isinstance(cond, list) else [cond]:
                if isinstance(c, dict):
                    check_where(obj, c)
            continue
        if lower == "not":
            if isinstance(cond, dict):
                check_where(obj, cond)
            continue
        if find_field(obj, key) is None:
            rel = parent_relationship(obj, key, case_insensitive=True)
            if rel is None:
                raise QueryError(f"contains a field not in '{obj}_Filter': '{key}'")
            if isinstance(cond, dict) and not (set(k.lower() for k in cond) <= {"eq", "ne"} and None in cond.values()):
                check_where(rel[2][0], cond)
            continue
        if isinstance(cond, dict):
            for op in cond:
                if op.lower() not in _OPS:
                    raise QueryError(f"contains a field not in '{find_field(obj, key)[2].title()}Operators': '{op}'")


def gql_match(ctx: Ctx, obj: str, rec: dict, where: dict | None) -> bool:
    if not where:
        return True
    for key, cond in where.items():
        lower = key.lower()
        if lower == "and":
            if not all(gql_match(ctx, obj, rec, c) for c in (cond if isinstance(cond, list) else [cond])):
                return False
            continue
        if lower == "or":
            if not any(gql_match(ctx, obj, rec, c) for c in (cond if isinstance(cond, list) else [cond])):
                return False
            continue
        if lower == "not":
            if gql_match(ctx, obj, rec, cond):
                return False
            continue
        meta = find_field(obj, key)
        if meta is None:
            rel = parent_relationship(obj, key, case_insensitive=True)
            if rel is None:
                raise QueryError(f"Field '{key}' in type '{obj}_Filter' is undefined")
            parent = follow(ctx, obj, rec, key)
            if isinstance(cond, dict) and set(k.lower() for k in cond) <= {"eq", "ne"} and None in cond.values():
                is_null = parent is None
                if not (("eq" in cond and is_null) or ("ne" in cond and not is_null)):
                    return False
                continue
            if parent is None or not gql_match(ctx, parent[0], parent[1], cond):
                return False
            continue
        actual = value(ctx, obj, rec, meta[0])
        if not isinstance(cond, dict):
            raise QueryError(f"Filter on '{key}' needs an operator such as eq or like")
        for op, raw in cond.items():
            if not compare(op, actual, gql_value(ctx, raw, op.lower()), meta[2]):
                return False
    return True


# --- sorting ------------------------------------------------------------------------------------------------------

def sort_rows(ctx: Ctx, obj: str, items: list[dict], keys: Iterable[tuple[str, bool, bool | None]]) -> list[dict]:
    """Stable multi-key sort. ``keys`` are (path, descending, nulls_first); nulls default to first when ascending."""
    out = list(items)
    for path, desc, nulls_first in reversed(list(keys)):
        dtype = field_type(obj, path)
        nulls_first = (not desc) if nulls_first is None else nulls_first
        present = [r for r in out if path_value(ctx, obj, r, path) is not None]
        missing = [r for r in out if path_value(ctx, obj, r, path) is None]
        present.sort(key=lambda r: _comparable(path_value(ctx, obj, r, path), dtype), reverse=desc)
        out = missing + present if nulls_first else present + missing
    return out


def default_order(obj: str) -> list[tuple[str, bool, bool | None]]:
    return [("Id", False, None)]


# --- display ------------------------------------------------------------------------------------------------------

def display_value(dtype: str | None, raw: Any) -> str | None:
    """The UI API's formatted ``displayValue``: set for currency, percent, dates and picklists, null otherwise."""
    if raw is None:
        return None
    if dtype == "CURRENCY":
        return f"${float(raw):,.2f}" if float(raw) >= 0 else f"-${-float(raw):,.2f}"
    if dtype == "PERCENT":
        number = float(raw)
        return f"{int(number)}%" if number.is_integer() else f"{number}%"
    if dtype == "DATE":
        day = parse_date(raw)
        return display_date(day) if day else None
    if dtype == "DATETIME":
        return display_datetime(raw)
    if dtype == "PICKLIST":
        return str(raw)
    return None


def record_name(ctx: Ctx, obj: str, rec: dict | None) -> str | None:
    if rec is None:
        return None
    return rec.get(OBJECTS[obj]["name"][0]) or rec.get("Name") or rec.get("Subject") or rec["Id"]
