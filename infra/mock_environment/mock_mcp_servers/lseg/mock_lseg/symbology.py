"""``symbology_lookup``: map between identifier types (ticker, RIC, ISIN, CUSIP, SEDOL, PermID).

The input and output shapes were not recorded; they follow the public LSEG
symbology API (input/output pairs) in a flattened, easy-to-call form.
"""

from __future__ import annotations

from mockmcp import Tool
from mockmcp.tool import CallContext

from .common import Issues, LsegData

TYPES = ("Ticker", "RIC", "ISIN", "CUSIP", "SEDOL", "OrganizationPermID", "IBESTicker", "QACode", "Name")
DEFAULT_TO = ["RIC", "Ticker", "ISIN", "CUSIP", "SEDOL", "OrganizationPermID"]
MAX_VALUES = 50


class SymbologyLookup(Tool):
    name = "symbology_lookup"
    title = "LSEG symbology lookup"
    description = (
        "Convert instrument or company identifiers between types. values: identifier(s), comma-separated or "
        f"an array (e.g. 'NVDA' or ['US67066G1040']). from: optional input type, auto-detected if omitted. "
        f"to: output types (default {DEFAULT_TO}). Types: {', '.join(TYPES)}."
    )
    validate_args = False
    input_schema = {
        "type": "object",
        "properties": {
            "values": {"anyOf": [{"type": "string"}, {"type": "array", "items": {"type": "string"}}]},
            "from": {"type": "string", "enum": list(TYPES)},
            "to": {"type": "array", "items": {"type": "string", "enum": list(TYPES)}},
        },
        "required": ["values"],
    }

    def __init__(self, data: LsegData) -> None:
        self.data = data

    def run(self, args: dict, ctx: CallContext) -> dict:
        values, source, targets = self._validate(args)
        return {"data": [self._one(v, source, targets) for v in values]}

    def _validate(self, args: dict):
        issues = Issues()
        raw = args.get("values")
        values = raw if isinstance(raw, list) else str(raw or "").split(",")
        values = [str(v).strip() for v in values if str(v).strip()]
        if not values:
            issues.add("values is required (e.g. 'NVDA')")
        elif len(values) > MAX_VALUES:
            issues.add(f"values must contain at most {MAX_VALUES} identifiers")
        source = args.get("from")
        if source is not None and source not in TYPES:
            issues.add(f"from must be one of: {', '.join(TYPES)}")
        targets = args.get("to") or DEFAULT_TO
        if not isinstance(targets, list) or any(t not in TYPES for t in targets):
            issues.add(f"to must be an array of: {', '.join(TYPES)}")
        issues.raise_if_any()
        return values, source, targets

    def _one(self, value: str, source: str | None, targets: list[str]) -> dict:
        view = self.data.world.resolve(value)
        entry = {"input": [{"value": value, "identifierType": source or (_detect(view, value) if view else "Unknown")}]}
        if view is None:
            return {**entry, "output": [], "message": "No match found"}
        ids = _identifiers(view.company)
        return {**entry, "output": [{"value": ids[t], "identifierType": t} for t in targets]}


def _identifiers(c) -> dict:
    return {
        "Ticker": c.ticker, "RIC": c.ric, "ISIN": c.isin, "CUSIP": c.cusip, "SEDOL": c.sedol,
        "OrganizationPermID": str(c.org_permid), "IBESTicker": c.ticker, "QACode": str(c.qa_code), "Name": c.name,
    }


def _detect(view, value: str) -> str:
    upper = value.strip().upper()
    for kind, known in _identifiers(view.company).items():
        if str(known).upper() == upper:
            return kind
    return "Name"
