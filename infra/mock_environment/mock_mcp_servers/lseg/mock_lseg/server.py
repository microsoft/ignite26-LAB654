"""LSEG mock MCP server: I/B/E/S, Worldscope fundamentals, pricing, news and symbology."""

from __future__ import annotations

from mockmcp import ServerSpec

from .common import LsegData, render_error
from .fundamentals import QaCompanyFundamentals
from .ibes import QaIbesConsensus
from .news import ImportantCompanyNews
from .pricing import HistoricalPricingSummaries
from .symbology import SymbologyLookup

NAME = "lseg"
VERSION = "1.0.0"
INSTRUCTIONS = (
    "Mock of the LSEG financial data MCP server for the LAB654 Ignite lab. Read-only. Data is a "
    "deterministic synthetic model anchored to recorded values; it is not real market data."
)


def build_spec(data: LsegData | None = None) -> ServerSpec:
    data = data or LsegData.default()
    tools = [
        QaIbesConsensus(data),
        QaCompanyFundamentals(data),
        HistoricalPricingSummaries(data),
        ImportantCompanyNews(data),
        SymbologyLookup(data),
    ]
    return ServerSpec(NAME, VERSION, tools, instructions=INSTRUCTIONS, render_error=render_error)
