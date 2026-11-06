import json

import pytest
from starlette.testclient import TestClient

from mock_salesforce import build_spec
from mock_salesforce.store import StateStore
from mock_salesforce.tools import load_schemas
from mockmcp.app import build_asgi_app
from mockmcp.testing import assert_deterministic, call

V = "/services/data/v62.0"
DASHBOARD, ROLLOUT, LAKESHORE, ATUL = "01ZHp0000000001IAA", "006Hp0000000001IAA", "001Hp0000000001IAA", "003Hp0000000001IAA"
EVENT, TASK, EMIL = "00UHp0000000001MAA", "00THp0000000001MAA", "005Hp0000000001IAA"


@pytest.fixture(scope="module")
def spec():
    return build_spec()


@pytest.fixture()
def web():
    store = StateStore()
    spec = build_spec(store=store)
    return spec, store, TestClient(build_asgi_app(spec), follow_redirects=False)


def _get(spec, url, conv=None, **params):
    got = call(spec, "dispatch_readonly", {"method": "GET", "url": url, **params}, conv)
    assert got.ok, got.text
    return got.json


def _soql(spec, q, conv=None):
    return _get(spec, f"{V}/query", conv, queryParams={"q": q})


def _new_task(spec, conv, subject="Send Aurora rollout proposal"):
    body = {"Subject": subject, "WhatId": ROLLOUT, "WhoId": ATUL, "ActivityDate": "2026-11-21", "Priority": "High"}
    got = call(spec, "dispatch", {"method": "POST", "url": f"{V}/sobjects/Task", "body": body}, conv)
    assert got.ok, got.text
    return got.json


# --- tool surface ----------------------------------------------------------------------------------------------

def test_tools_use_real_schemas(spec):
    real = load_schemas()
    tools = {t.name: t for t in spec.tools}
    assert set(tools) == {"describe", "discover", "dispatch", "dispatch_readonly", "display_widget"}
    for name, tool in tools.items():
        assert tool.description == real[name]["description"]
        assert tool.input_schema == real[name]["inputSchema"]


def test_discover_and_describe(spec):
    found = call(spec, "discover", {"query": "update opportunity stage"}).json
    assert found["result_type"] == "discovery" and found["results"]
    top = found["results"][0]["sor_id"]
    assert "error" not in call(spec, "describe", {"id": top}).json
    assert "No operation or SOR found" in call(spec, "describe", {"id": "nope"}).json["error"]


def test_discover_is_deterministic():
    assert_deterministic(build_spec, "discover", {"query": "opportunity pipeline", "limit": 5})


# --- REST and SOQL ---------------------------------------------------------------------------------------------

def test_success_envelope(spec):
    got = _get(spec, f"{V}/sobjects/Opportunity/{ROLLOUT}")
    assert got["status_code"] == 200 and got["url"].endswith(f"{V}/sobjects/Opportunity/{ROLLOUT}")
    assert got["body"]["Name"] == "Lakeshore Retail – Aurora 400-store rollout"
    assert got["body"]["Amount"] == 1200000.0


def test_error_envelope_body_is_json_string(spec):
    got = _get(spec, f"{V}/sobjects/Opportunity/006Hp0000000099IAA")
    assert got["error_code"] == "API_ERROR" and got["status_code"] == 404
    assert json.loads(got["body"])[0]["errorCode"] == "NOT_FOUND"


def test_soql_lab_queries(spec):
    opps = _soql(spec, "SELECT Name, StageName, Amount FROM Opportunity WHERE Account.Name = 'Lakeshore Retail'")
    assert {r["StageName"] for r in opps["body"]["records"]} == {"Proposal/Price Quote", "Closed Won"}
    contacts = _soql(spec, f"SELECT Name, Title FROM Contact WHERE AccountId = '{LAKESHORE}'")
    assert {r["Name"] for r in contacts["body"]["records"]} == {"Atul Manohar", "Jahidi Juma"}
    won = _soql(spec, "SELECT Account.Name, Amount FROM Opportunity WHERE IsWon = true")
    assert won["body"]["totalSize"] == 2


def test_no_tenant_domain_as_website(spec):
    acct = _get(spec, f"{V}/sobjects/Account/{LAKESHORE}")["body"]
    assert acct["Website"] == "lakeshore-retail.com"
    assert "onmicrosoft.com" not in acct["Website"]


def test_readonly_rejects_writes(spec):
    got = call(spec, "dispatch_readonly", {"method": "POST", "url": f"{V}/sobjects/Task", "body": {"Subject": "x"}})
    assert not got.ok and got.json[0]["errorCode"] == "INVALID_INPUT"


def test_write_validation(spec):
    bad = call(spec, "dispatch", {"method": "POST", "url": f"{V}/sobjects/Task", "body": {"Nope__c": 1}}, "c1").json
    assert json.loads(bad["body"])[0]["errorCode"] == "INVALID_FIELD"
    ref = call(spec, "dispatch", {"method": "POST", "url": f"{V}/sobjects/Task",
                                  "body": {"Subject": "x", "WhatId": "006Hp0000000099IAA"}}, "c1").json
    assert json.loads(ref["body"])[0]["errorCode"] == "INVALID_CROSS_REFERENCE_KEY"


def test_writes_are_scoped_per_conversation(spec):
    created = _new_task(spec, "conv-a")
    assert created["status_code"] == 201 and created["body"]["success"]
    tid = created["body"]["id"]
    assert _get(spec, f"{V}/sobjects/Task/{tid}", "conv-a")["status_code"] == 200
    assert _get(spec, f"{V}/sobjects/Task/{tid}", "conv-b")["status_code"] == 404
    assert _get(spec, f"{V}/sobjects/Task/{tid}")["status_code"] == 404


def test_patch_stage_records_history(spec):
    conv = "conv-stage"
    got = call(spec, "dispatch", {"method": "PATCH", "url": f"{V}/sobjects/Opportunity/{ROLLOUT}",
                                  "body": {"StageName": "Negotiation/Review"}}, conv).json
    assert got["status_code"] == 204
    hist = _soql(spec, f"SELECT StageName FROM OpportunityHistory WHERE OpportunityId = '{ROLLOUT}'", conv)
    assert "Negotiation/Review" in {r["StageName"] for r in hist["body"]["records"]}
    seed = _get(spec, f"{V}/sobjects/Opportunity/{ROLLOUT}")["body"]
    assert seed["StageName"] == "Proposal/Price Quote"


# --- widget ----------------------------------------------------------------------------------------------------

def test_display_widget_dynamic(spec):
    definition = {"type": "table", "columns": ["Name"], "rows": [{"Name": "Lakeshore Retail"}]}
    got = call(spec, "display_widget", {"resourceType": "dynamic", "widgetDefinition": definition})
    assert got.ok and got.structured == {"widgetDefinition": definition}


def test_display_widget_named_type_unsupported(spec):
    got = call(spec, "display_widget", {"resourceType": "salesforce_widget", "widget_resource_uri": "x"})
    assert not got.ok


def test_display_widget_accepts_json_string(spec):
    definition = {"type": "table", "columns": ["Name"], "rows": [{"Name": "Lakeshore Retail"}]}
    got = call(spec, "display_widget", {"resourceType": "dynamic", "widgetDefinition": json.dumps(definition)})
    assert got.ok and got.structured == {"widgetDefinition": definition}


def test_display_widget_malformed_string_asks_for_retry(spec):
    got = call(spec, "display_widget", {"resourceType": "dynamic", "widgetDefinition": '{"renderer":{}}},"x":1}'})
    assert not got.ok
    assert "not valid JSON" in got.text and "call display_widget again" in got.text


def test_display_widget_still_validates_schema(spec):
    assert not call(spec, "display_widget", {"resourceType": "bogus", "widgetDefinition": {}}).ok
    assert not call(spec, "display_widget", {"resourceType": "dynamic", "widgetDefinition": 5}).ok


# --- Lightning viewer ------------------------------------------------------------------------------------------

@pytest.mark.parametrize("path", [
    "/lightning/page/home",
    f"/lightning/r/Opportunity/{ROLLOUT}/view",
    f"/lightning/r/Opportunity/{ROLLOUT}/view?tab=activity",
    f"/lightning/r/Account/{LAKESHORE}/view",
    f"/lightning/r/Contact/{ATUL}/view",
    f"/lightning/r/Event/{EVENT}/view",
    f"/lightning/r/Task/{TASK}/view",
    f"/lightning/r/User/{EMIL}/view",
    "/lightning/o/Opportunity/list",
    "/lightning/o/Dashboard/home",
    f"/lightning/r/Dashboard/{DASHBOARD}/view",
    "/lightning/search?q=aurora",
])
def test_pages_render(web, path):
    _, _, client = web
    res = client.get(path)
    assert res.status_code == 200, path
    assert "Not affiliated with Salesforce" in res.text


def test_root_redirects_home(web):
    _, _, client = web
    assert client.get("/").headers["location"].endswith("/lightning/page/home")


def test_wrong_object_redirects(web):
    _, _, client = web
    res = client.get(f"/lightning/r/Account/{ROLLOUT}/view")
    assert res.status_code == 302 and "/Opportunity/" in res.headers["location"]


def test_unknown_record_and_object_404(web):
    _, _, client = web
    assert client.get("/lightning/r/Opportunity/006Hp0000000099IAA/view").status_code == 404
    assert client.get("/lightning/o/Nope/list").status_code == 404


def test_viewer_shows_conversation_writes(web):
    spec, store, client = web
    tid = _new_task(spec, "conv-view", "Mock follow-up task")["body"]["id"]
    token = store.view_token("conv-view")
    assert "Mock follow-up task" in client.get(f"/v/{token}/lightning/r/Task/{tid}/view").text
    redirect = client.get(f"/lightning/r/Task/{tid}/view")
    assert redirect.status_code == 302 and redirect.headers["location"].startswith(f"/v/{token}/")


def test_expired_and_malformed_tokens(web):
    _, _, client = web
    expired = client.get(f"/v/{'0' * 20}/lightning/page/home")
    assert expired.status_code == 200 and "expired" in expired.text.lower()
    assert client.get("/v/not-a-token/lightning/page/home").status_code == 404


def test_icon_route(web):
    _, _, client = web
    ok = client.get("/img/icon/t4v35/standard/opportunity.svg")
    assert ok.status_code == 200 and ok.headers["content-type"].startswith("image/svg+xml")
    assert client.get("/img/icon/t4v35/standard/nope.svg").status_code == 404


def test_widget_handshake_matches_mcp_apps_sdk():
    import re
    from pathlib import Path

    import mock_salesforce

    html = (Path(mock_salesforce.__file__).parent / "ui" / "widget.html").read_text(encoding="utf-8")
    # MCP Apps SDK hosts reject ui/initialize without appInfo + appCapabilities + protocolVersion.
    init = re.search(r'request\("ui/initialize",\s*\{(.*?)\}\)', html, re.S).group(1)
    assert all(k in init for k in ("appInfo:", "appCapabilities:", "protocolVersion:"))
    assert "if (!initialized) return;" in html


def test_widget_render_is_fail_safe_for_rich_cells():
    from pathlib import Path

    import mock_salesforce

    html = (Path(mock_salesforce.__file__).parent / "ui" / "widget.html").read_text(encoding="utf-8")
    # Real Salesforce datagrids send badge cells as {value, badgeVariant}; an uncaught throw empties the iframe.
    assert "v.badgeVariant" in html
    assert "if (c instanceof Node)" in html
    assert "render failed" in html
