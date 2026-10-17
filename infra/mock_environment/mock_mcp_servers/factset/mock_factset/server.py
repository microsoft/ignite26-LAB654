"""FactSet mock MCP server: metrics, entity reference, fundamentals, estimates, prices and RBICS."""

from __future__ import annotations

from mockmcp import ServerSpec

from .common import FactsetData, render_error
from .entity import FactsetEntityReference
from .estimates import FactsetEstimatesConsensus
from .fundamentals import FactsetFundamentals
from .metrics import FactsetMetrics
from .prices import FactsetGlobalPrices
from .rbics import FactsetRbics
from .screener import FactsetCompanyScreener

NAME = "factset"
VERSION = "1.0.0"
INSTRUCTIONS = (
    "Mock of the FactSet MCP server for the LAB654 Ignite lab. Read-only. Discover metric codes with "
    "FactSet_Metrics before requesting fundamentals or estimates. Data is a deterministic synthetic model "
    "anchored to recorded values; it is not real market data."
)


def build_spec(data: FactsetData | None = None) -> ServerSpec:
    data = data or FactsetData.default()
    tools = [
        FactsetMetrics(data),
        FactsetEntityReference(data),
        FactsetRbics(data),
        FactsetFundamentals(data),
        FactsetEstimatesConsensus(data),
        FactsetGlobalPrices(data),
        FactsetCompanyScreener(),
    ]
    return ServerSpec(NAME, VERSION, tools, instructions=INSTRUCTIONS, render_error=render_error)
