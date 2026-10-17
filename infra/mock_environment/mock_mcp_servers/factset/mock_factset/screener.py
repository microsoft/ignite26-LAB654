"""``FactSet_CompanyScreener``: present in the real catalogue but not licensed for the lab tenant."""

from __future__ import annotations

from mockmcp import NotEntitled, Tool
from mockmcp.tool import CallContext


class FactsetCompanyScreener(Tool):
    name = "FactSet_CompanyScreener"
    title = "FactSet company screener"
    description = (
        "Screen the global company universe by criteria (industry, size, ratios). Requires a FactSet Screening "
        "entitlement. For a known peer set, use FactSet_Fundamentals with explicit ids instead."
    )
    validate_args = False
    input_schema = {
        "type": "object",
        "properties": {"query": {"type": "string"}, "request_id": {"type": "string"}},
    }

    def run(self, args: dict, ctx: CallContext) -> dict:
        raise NotEntitled(
            "Your FactSet subscription does not include Company Screening. Query known companies directly with "
            "FactSet_Fundamentals, FactSet_RBICS or FactSet_EntityReference."
        )
