from pathlib import Path

import pytest
from starlette.testclient import TestClient

from mock_lseg import build_spec
from mockmcp.app import build_asgi_app
from mockmcp.testing import assert_deterministic, call, replay

FIXTURES = sorted((Path(__file__).parent / "fixtures").glob("*.json"))
# The live API returned only 2 of the 13 requested monthly bars; the mock deliberately returns all 13.
KNOWN_DEVIATIONS = {"036_historical_pricing_summaries_ok"}


@pytest.fixture(scope="module")
def spec():
    return build_spec()


@pytest.mark.parametrize("fixture", FIXTURES, ids=lambda p: p.stem)
def test_replays_recorded_trace(spec, fixture):
    if fixture.stem in KNOWN_DEVIATIONS:
        pytest.xfail("documented deviation from the live API")
    assert replay(spec, fixture) == []


def _ibes(data_type, **options):
    return {"requests": [{"dataType": data_type, "options": options}]}


@pytest.mark.parametrize("ticker", ["AMD", "AVGO", "INTC", "MRVL"])
def test_peers_get_consensus_and_actuals(spec, ticker):
    out = call(spec, "qa_ibes_consensus", {"requests": [
        {"dataType": "qa_ibes_consensus", "options": {"ticker": ticker, "measures": ["Eps", "Rev"], "periodType": "Year", "periodIndexStart": 1, "periodIndexEnd": 3}},
        {"dataType": "qa_ibes_actuals", "options": {"ticker": ticker, "measures": ["Eps", "Rev"], "periodType": "Quarter", "pIndex": -3}},
    ]})
    assert out.ok, out.text
    assert out.json[0]["response"]["data"]["estimates"]


@pytest.mark.parametrize("p_index", [-2, -5, -7])
def test_older_quarters_resolve(spec, p_index):
    out = call(spec, "qa_ibes_consensus", _ibes("qa_ibes_actuals", ticker="NVDA", measures=["Eps"], periodType="Quarter", pIndex=p_index))
    assert out.ok, out.text


@pytest.mark.parametrize("args", [
    {"universe": "AMD.O", "interval": "P1D", "count": 20},
    {"universe": "NVDA.O", "interval": "P1W", "start": "2026-01-01", "end": "2026-06-30"},
    {"universe": "INTC.O", "interval": "P3M", "count": 4},
])
def test_pricing_variations(spec, args):
    out = call(spec, "historical_pricing_summaries", args)
    assert out.ok, out.text
    assert out.json[0]["data"]


def test_fundamentals_for_a_peer(spec):
    out = call(spec, "qa_company_fundamentals", _ibes("qa_company_fundamentals", identifier="QCOM", type="Ticker", measures="1001,1100", year="2024,2025", freq="A"))
    assert out.ok, out.text


def test_news_for_another_window(spec):
    out = call(spec, "important_company_news", {"companyRics": "AMD.O", "start": "2026-07-01", "end": "2026-08-15"})
    assert out.ok, out.text


@pytest.mark.parametrize("tool,args", [
    ("historical_pricing_summaries", {"universe": "NVDA.O", "interval": "P1D", "count": -1}),
    ("historical_pricing_summaries", {"interval": "P1D"}),
    ("qa_ibes_consensus", {"requests": []}),
])
def test_bad_arguments_are_rejected(spec, tool, args):
    assert not call(spec, tool, args).ok


def test_unknown_ticker_returns_empty_estimates(spec):
    out = call(spec, "qa_ibes_consensus", _ibes("qa_ibes_consensus", ticker="ZZZZ", measures=["Eps"], periodType="Year", periodIndexStart=1, periodIndexEnd=1))
    assert out.ok and out.json[0]["response"]["data"]["estimates"] == []


def test_answers_are_deterministic():
    assert_deterministic(build_spec, "historical_pricing_summaries", {"universe": "MU.O", "interval": "P1D", "count": 30})
    assert_deterministic(build_spec, "qa_ibes_consensus", _ibes("qa_ibes_actuals", ticker="TXN", measures=["Eps", "Rev"], periodType="Year", pIndex=-2))


def test_healthz(spec):
    with TestClient(build_asgi_app(spec)) as client:
        body = client.get("/healthz").json()
    assert body["status"] == "ok" and body["server"] == spec.name and body["tools"] == len(spec.tools)

WIDGETS = {
    "qa_ibes_consensus": "ui://lseg/ibes",
    "historical_pricing_summaries": "ui://lseg/pricing",
    "qa_company_fundamentals": "ui://lseg/fundamentals",
}


def test_widget_tools_declare_their_ui_resource(spec):
    meta = {t.name: (t.meta or {}) for t in spec.list_tools()}
    for tool, uri in WIDGETS.items():
        assert meta[tool]["ui"]["resourceUri"] == uri
        assert meta[tool]["ui/resourceUri"] == uri
    assert "ui" not in meta["important_company_news"] and "ui" not in meta["symbology_lookup"]


def test_widgets_are_served_as_self_contained_mcp_apps(spec):
    import asyncio
    import re

    from mcp import types
    from mockmcp import UI_MIME_TYPE
    from mockmcp.app import build_server

    listed = {str(r.uri): r for r in spec.list_resources()}
    assert set(listed) == set(WIDGETS.values())
    assert all(r.mimeType == UI_MIME_TYPE for r in listed.values())

    handler = build_server(spec).request_handlers[types.ReadResourceRequest]
    for uri in WIDGETS.values():
        req = types.ReadResourceRequest(method="resources/read", params=types.ReadResourceRequestParams(uri=uri))
        contents = asyncio.run(handler(req)).root.contents
        assert len(contents) == 1 and contents[0].mimeType == UI_MIME_TYPE
        html = contents[0].text
        assert html.startswith("<!doctype html>") and "window.Kit" in html and "ui/initialize" in html
        assert "include:" not in html
        # MCP Apps SDK hosts reject ui/initialize without appInfo + appCapabilities + protocolVersion.
        init = re.search(r'request\("ui/initialize",\s*\{(.*?)\}\)\.then', html, re.S).group(1)
        assert all(k in init for k in ("appInfo:", "appCapabilities:", "protocolVersion:")), uri
        assert "if (!initialized) return;" in html, uri
        assert not re.search(r"""(src|href)\s*=\s*["']?(https?:)?//""", html), uri


def test_fundamentals_return_structured_content(spec):
    out = call(spec, "qa_company_fundamentals", {"requests": [{"dataType": "qa_company_fundamentals", "options": {
        "identifier": "NVDA", "type": "Ticker", "measures": "1001,5201", "year": "2024,2025", "freq": "A"}}]})
    assert out.ok, out.text
    assert out.result.structuredContent["data"] == out.json


def test_cors_allows_the_m365_widget_renderer(spec):
    origin = "https://abc123.widget-renderer.usercontent.microsoft.com"
    with TestClient(build_asgi_app(spec)) as client:
        ok = client.options("/mcp", headers={"Origin": origin, "Access-Control-Request-Method": "POST",
                                             "Access-Control-Request-Headers": "content-type,mcp-session-id"})
        bad = client.options("/mcp", headers={"Origin": "https://evil.example.com", "Access-Control-Request-Method": "POST"})
    assert ok.status_code == 200 and ok.headers["access-control-allow-origin"] == origin
    assert "access-control-allow-origin" not in bad.headers
