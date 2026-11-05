"""Pieces every FactSet tool shares: data access, the metric catalog, id handling and errors."""

from __future__ import annotations

import ast
import json
import operator
from dataclasses import dataclass, field
from datetime import date, datetime, time, timezone
from functools import cached_property
from pathlib import Path
from typing import Any, Callable, Iterable

from mockfin import CompanyView, Period, World
from mockfin.financials import FLOW_METRICS
from mockmcp import InvalidParams, JsonStore, NotEntitled, ToolError, UpstreamError

SEED_DIR = Path(__file__).resolve().parent.parent / "seed_files"
DATA_PRODUCTS = ("fundamentals", "estimates")
REQUEST_ID_SCHEMA = {"type": "string", "description": "Optional caller correlation id."}


# --- Metric catalog -------------------------------------------------------------------------


@dataclass(frozen=True)
class MetricDef:
    """One FactSet metric code and how to compute it from the shared finance model."""

    code: str
    properties: dict
    field: str | None = None
    expr: str | None = None
    kind: str = "ratio"  # flow (summed for LTM), stock (period-end) or ratio
    aliases: tuple[str, ...] = ()

    @property
    def product(self) -> str:
        return self.properties["dataProduct"]

    @property
    def name(self) -> str:
        return self.properties["name"]


class Formula:
    """Safe arithmetic over model metric names, e.g. ``100 * gross_income / revenue``."""

    _OPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul, ast.Div: operator.truediv}

    def __init__(self, text: str) -> None:
        self.text = text
        self.tree = ast.parse(text, mode="eval").body
        self.names = sorted({n.id for n in ast.walk(self.tree) if isinstance(n, ast.Name)})

    def evaluate(self, lookup: Callable[[str], float | None]) -> float | None:
        values = {name: lookup(name) for name in self.names}
        if any(v is None for v in values.values()):
            return None
        try:
            return self._eval(self.tree, values)
        except ZeroDivisionError:
            return None

    def _eval(self, node: ast.AST, values: dict) -> float:
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return float(node.value)
        if isinstance(node, ast.Name):
            return float(values[node.id])
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
            return -self._eval(node.operand, values)
        if isinstance(node, ast.BinOp) and type(node.op) in self._OPS:
            return self._OPS[type(node.op)](self._eval(node.left, values), self._eval(node.right, values))
        raise ValueError(f"Unsupported formula element: {ast.dump(node)}")


@dataclass
class Catalog:
    metrics: dict[str, MetricDef]
    observed_queries: dict[str, list[tuple[float, str]]] = field(default_factory=dict)

    def get(self, code: str) -> MetricDef | None:
        return self.metrics.get(str(code).strip().upper())

    def of(self, product: str) -> list[MetricDef]:
        return [m for m in self.metrics.values() if m.product == product]


def _load_catalog(store: JsonStore) -> Catalog:
    observed = store.view("metrics_catalog_observed") if store.has("metrics_catalog_observed") else {}
    observed_props = observed.get("metrics", {})
    metrics: dict[str, MetricDef] = {}
    for code, raw in store.view("metrics")["metrics"].items():
        props = dict(observed_props.get(code) or raw["properties"])
        model = raw["model"]
        kind = model.get("kind", "ratio")
        metrics[code] = MetricDef(code, props, model.get("field"), model.get("expr"), kind, tuple(raw.get("aliases", ())))
    queries = {q.lower(): [(float(s), c) for s, c in hits] for q, hits in observed.get("observed_queries", {}).items()}
    return Catalog(metrics, queries)


# --- Data handle ----------------------------------------------------------------------------


@dataclass
class FactsetData:
    """Read-only handle on the shared finance world plus FactSet-specific seed overlays."""

    world: World
    store: JsonStore

    @classmethod
    def default(cls) -> "FactsetData":
        return cls(World.default(), JsonStore(SEED_DIR))

    @cached_property
    def catalog(self) -> Catalog:
        return _load_catalog(self.store)

    @cached_property
    def formulas(self) -> dict[str, Formula]:
        return {m.code: Formula(m.expr) for m in self.catalog.metrics.values() if m.expr}

    @cached_property
    def observed_fundamentals(self) -> dict[tuple, float]:
        if not self.store.has("fundamentals_observed"):
            return {}
        rows = self.store.view("fundamentals_observed")["rows"]
        out = {}
        for row in rows:
            view = self.world.resolve(row["requestId"])
            if view:
                out[(view.company.ticker, row["metric"], row["periodicity"], row["fiscalYear"], row["fiscalPeriod"])] = row["value"]
        return out

    def resolve(self, identifier: Any) -> CompanyView | None:
        return self.world.resolve(identifier)

    # Metric values ----------------------------------------------------------------------

    def metric_value(self, view: CompanyView, metric: MetricDef, period: Period, ltm: bool = False) -> float | None:
        """Value of ``metric`` for one fiscal year / quarter, or trailing four quarters ending ``period``."""
        model = view.financials
        if not ltm:
            if metric.field:
                return model.value(metric.field, period)
            return self.formulas[metric.code].evaluate(lambda name: model.value(name, period))

        quarters = [period.shift(-i) for i in range(3, -1, -1)]

        def trailing(name: str) -> float | None:
            values = [model.value(name, q) for q in quarters]
            if any(v is None for v in values):
                return None
            if name in FLOW_METRICS:
                return sum(values)
            return values[-1]

        if metric.code in self.formulas:
            return self.formulas[metric.code].evaluate(trailing)
        if metric.kind in ("flow", "stock"):
            return trailing(metric.field)
        values = [model.value(metric.field, q) for q in quarters]
        return None if any(v is None for v in values) else sum(values) / 4


# --- Validation helpers ---------------------------------------------------------------------


class Issues:
    """Collects validation problems, then raises them together."""

    def __init__(self) -> None:
        self.items: list[str] = []

    def add(self, issue: str) -> None:
        if issue not in self.items:
            self.items.append(issue)

    def raise_if_any(self) -> None:
        if self.items:
            raise InvalidParams(self.items)


def check_request_id(issues: Issues, args: dict) -> None:
    if "request_id" in args and not isinstance(args["request_id"], str):
        issues.add("request_id must be a string")


def id_list(issues: Issues, args: dict, maximum: int, name: str = "ids") -> list[str]:
    raw = args.get(name)
    if isinstance(raw, str):
        raw = [part for part in raw.split(",")]
    if not isinstance(raw, list) or not raw:
        issues.add(f"{name} is required: a non-empty array of identifiers such as ['LITW-US']")
        return []
    ids = [str(v).strip() for v in raw if str(v).strip()]
    if len(ids) > maximum:
        issues.add(f"{name} supports at most {maximum} identifiers per request (received {len(ids)})")
    return ids


def choice(issues: Issues, args: dict, name: str, options: Iterable[str], default: str | None = None) -> str | None:
    options = tuple(options)
    value = args.get(name, default)
    if value is None:
        return None
    text = str(value).strip().upper() if all(o.isupper() for o in options) else str(value).strip()
    if text not in options:
        issues.add(f"{name} must be one of: {', '.join(options)} (received '{value}')")
        return None
    return text


def parse_date(issues: Issues, name: str, value: Any) -> date | None:
    if value in (None, ""):
        return None
    try:
        return date.fromisoformat(str(value).strip()[:10])
    except ValueError:
        issues.add(f"{name} must be a date in YYYY-MM-DD format (received '{value}')")
        return None


def as_of(day: date) -> datetime:
    """End-of-day UTC instant for point-in-time questions about ``day``."""
    return datetime.combine(day, time(23, 0), tzinfo=timezone.utc)


def compact(day: date) -> str:
    return day.strftime("%Y%m%d")


# --- Errors ---------------------------------------------------------------------------------


def render_error(error: ToolError, tool: str) -> str:
    if isinstance(error, InvalidParams):
        errors = [{"code": "BadRequest", "title": "Invalid request parameters", "detail": issue} for issue in error.issues]
    elif isinstance(error, NotEntitled):
        errors = [{"code": "Forbidden", "title": "Not entitled", "detail": error.message}]
    elif isinstance(error, UpstreamError):
        errors = [{"code": str(error.status), "title": "Upstream error", "detail": error.message}]
    else:
        errors = [{"code": "Error", "title": "Request failed", "detail": error.message}]
    return json.dumps({"errors": errors}, ensure_ascii=False)
