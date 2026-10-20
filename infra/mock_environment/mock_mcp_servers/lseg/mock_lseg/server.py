"""LSEG mock MCP server: I/B/E/S, Worldscope fundamentals, pricing, news and symbology."""

from __future__ import annotations

from pathlib import Path

from mockmcp import ServerSpec, UiResource, load_html

from .common import LsegData, render_error
from .fundamentals import QaCompanyFundamentals
from .ibes import QaIbesConsensus
from .news import ImportantCompanyNews
from .pricing import HistoricalPricingSummaries
from .symbology import SymbologyLookup

NAME = "lseg"
VERSION = "1.1.0"
INSTRUCTIONS = (
    "Mock of the LSEG financial data MCP server for the LAB654 Ignite lab. Read-only. Data is a "
    "deterministic synthetic model anchored to recorded values; it is not real market data."
)
UI_DIR = Path(__file__).parent / "ui"


def ui_resources() -> list[UiResource]:
    """MCP Apps widgets rendered by hosts for the I/B/E/S, pricing and fundamentals tools."""
    return [
        UiResource("ui://lseg/ibes", "qa-ibes-widget", load_html(UI_DIR, "ibes.html"),
                   title="LSEG I/B/E/S", description="Chart and table of I/B/E/S actuals, consensus and measures."),
        UiResource("ui://lseg/pricing", "historical-pricing-widget", load_html(UI_DIR, "pricing.html"),
                   title="LSEG historical pricing", description="Candlestick chart and table of price summaries."),
        UiResource("ui://lseg/fundamentals", "qa-fundamentals-widget", load_html(UI_DIR, "fundamentals.html"),
                   title="LSEG company fundamentals", description="Table of Worldscope fundamentals."),
    ]


def build_spec(data: LsegData | None = None) -> ServerSpec:
    data = data or LsegData.default()
    tools = [
        QaIbesConsensus(data),
        QaCompanyFundamentals(data),
        HistoricalPricingSummaries(data),
        ImportantCompanyNews(data),
        SymbologyLookup(data),
    ]
    return ServerSpec(NAME, VERSION, tools, instructions=INSTRUCTIONS, render_error=render_error,
                      resources=ui_resources())
