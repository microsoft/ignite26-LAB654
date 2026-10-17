"""``FactSet_Metrics``: discover exact metric codes from natural-language text.

Queries seen in the live trace replay their recorded scores and order. Any other
text is ranked by a deterministic similarity over metric names, aliases and
descriptions, so "operating margin" or "free cash flow" still find sensible codes.
"""

from __future__ import annotations

import re

from mockmcp import Tool, tidy
from mockmcp.tool import CallContext

from .common import DATA_PRODUCTS, REQUEST_ID_SCHEMA, Catalog, FactsetData, Issues, MetricDef, check_request_id

DEFAULT_LIMIT = 10
MIN_SCORE = 0.2
STOPWORDS = {"a", "an", "and", "the", "of", "to", "on", "per", "for", "in", "by", "ratio", "metric"}


class FactsetMetrics(Tool):
    name = "FactSet_Metrics"
    title = "FactSet metric discovery"
    description = (
        "Find exact FactSet metric codes for natural-language concepts before calling FactSet_Fundamentals or "
        "FactSet_EstimatesConsensus. text: array of short queries (no hyphens), e.g. ['gross margin']. "
        "target: 'metric'. data_products: ['fundamentals'] or ['estimates'] (codes differ between them). "
        f"limit: results per query, 1-100 (default {DEFAULT_LIMIT})."
    )
    validate_args = False
    input_schema = {
        "type": "object",
        "properties": {
            "text": {"type": "array", "items": {"type": "string"}, "minItems": 1},
            "target": {"type": "string", "enum": ["metric"], "default": "metric"},
            "data_products": {"type": "array", "items": {"type": "string", "enum": list(DATA_PRODUCTS)}},
            "limit": {"type": "integer", "minimum": 1, "maximum": 100, "default": DEFAULT_LIMIT},
            "request_id": REQUEST_ID_SCHEMA,
        },
        "required": ["text"],
    }

    def __init__(self, data: FactsetData) -> None:
        self.data = data

    def run(self, args: dict, ctx: CallContext) -> dict:
        queries, products, limit = self._validate(args)
        return {"data": [self._search(q, products, limit) for q in queries]}

    def _validate(self, args: dict):
        issues = Issues()
        check_request_id(issues, args)
        raw = args.get("text")
        queries = [raw] if isinstance(raw, str) else raw
        if not isinstance(queries, list) or not queries or not all(isinstance(q, str) and q.strip() for q in queries):
            issues.add("text is required: a non-empty array of query strings, e.g. ['gross margin']")
            queries = []
        for q in queries:
            if "-" in q:
                issues.add(f"text must not contain hyphens; rephrase '{q}' (e.g. '{q.replace('-', ' ')}')")
        if args.get("target", "metric") != "metric":
            issues.add("target must be 'metric'")
        products = args.get("data_products") or list(DATA_PRODUCTS)
        if isinstance(products, str):
            products = [products]
        if not isinstance(products, list) or any(p not in DATA_PRODUCTS for p in products):
            issues.add(f"data_products must be an array containing: {', '.join(DATA_PRODUCTS)}")
        limit = args.get("limit", DEFAULT_LIMIT)
        if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= 100:
            issues.add("limit must be an integer between 1 and 100")
        issues.raise_if_any()
        return [q.strip() for q in queries], products, limit

    def _search(self, query: str, products: list[str], limit: int) -> dict:
        ranked = rank(self.data.catalog, query, products)
        results = [{"score": score, "properties": metric.properties} for score, metric in ranked[:limit]]
        return {"query": query, "target": "metric", "results": results, "searchParameters": {"limit": limit}}


def rank(catalog: Catalog, query: str, products: list[str]) -> list[tuple[float, MetricDef]]:
    """Recorded results first (verbatim), then generated matches scored below them."""
    eligible = [m for m in catalog.metrics.values() if m.product in products]
    recorded = [(s, catalog.get(c)) for s, c in catalog.observed_queries.get(query.lower(), [])]
    recorded = [(s, m) for s, m in recorded if m and m.product in products]
    seen = {m.code for _, m in recorded}
    floor = min((s for s, _ in recorded), default=1.0)
    scored = []
    for metric in eligible:
        if metric.code in seen:
            continue
        score = similarity(query, metric)
        if score >= MIN_SCORE:
            scored.append((min(score, floor - 1e-6) if recorded else score, metric))
    scored.sort(key=lambda item: (-item[0], item[1].code))
    return recorded + [(tidy(s, 8), m) for s, m in scored]


def _tokens(text: str) -> list[str]:
    words = re.findall(r"[a-z0-9&]+", text.lower())
    return [w[:-1] if len(w) > 3 and w.endswith("s") and not w.endswith("ss") else w for w in words if w not in STOPWORDS]


def _trigrams(text: str) -> set[str]:
    padded = f"  {re.sub(r'[^a-z0-9]+', ' ', text.lower()).strip()} "
    return {padded[i : i + 3] for i in range(len(padded) - 2)}


def _phrase_score(query: str, phrase: str) -> float:
    q, p = _tokens(query), _tokens(phrase)
    if not q or not p:
        return 0.0
    if q == p:
        return 1.0
    common = len(set(q) & set(p))
    dice = 2 * common / (len(set(q)) + len(set(p)))
    tq, tp = _trigrams(query), _trigrams(phrase)
    tri = len(tq & tp) / len(tq | tp) if tq and tp else 0.0
    return 0.7 * dice + 0.3 * tri


def similarity(query: str, metric: MetricDef) -> float:
    phrases = [metric.name, metric.code.replace("FF_", "").replace("_", " "), *metric.aliases]
    best = max(_phrase_score(query, p) for p in phrases)
    if best == 1.0:
        return 1.0
    q = set(_tokens(query))
    described = len(q & set(_tokens(metric.properties.get("description", "")))) / len(q) if q else 0.0
    return min(0.98, 0.85 * best + 0.15 * described)
