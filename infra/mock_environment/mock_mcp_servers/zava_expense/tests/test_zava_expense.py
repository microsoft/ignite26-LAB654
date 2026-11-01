"""Tests for the Zava Expense mock: the numbers the lab guide quotes, policy checks and per-conversation writes."""

import json

import pytest
from mockmcp.app import build_asgi_app
from mockmcp.testing import assert_deterministic, call
from starlette.testclient import TestClient

from mock_zava_expense import build_spec
from mock_zava_expense.store import SEED_PATH, StateStore

WRITE_TOOLS = {"create_expense_report", "update_expense_report", "submit_expense_report"}


@pytest.fixture(autouse=True)
def lab_week(monkeypatch):
    monkeypatch.delenv("MOCK_NOW", raising=False)  # the server defaults to Mon Nov 16, 2026, 9 AM ET


@pytest.fixture
def spec():
    return build_spec()


def seattle_receipts(spec):
    seed = spec.tools[0].store.seed()
    return [{"date": e["received_on"], "merchant": e["from"].split("<")[0].strip(), "amount": e["amount"],
             "receipt_reference": e["subject"]} for e in seed["receipt_emails"] if e["amount"] is not None]


def create_seattle(spec, conv):
    return call(spec, "create_expense_report", {
        "title": "Seattle — Fabrikam, Inc. partnership review", "client": "Fabrikam, Inc.",
        "business_purpose": "Fabrikam, Inc. partnership review with the Fabrikam leadership team.",
        "items": seattle_receipts(spec)}, conv)


def test_tools_and_annotations(spec):
    tools = {t.name: t for t in spec.list_tools()}
    assert len(tools) == 9
    for name, tool in tools.items():
        assert tool.annotations.readOnlyHint is (name not in WRITE_TOOLS), name


def test_seed_matches_the_build_script():
    import importlib.util
    spec_ = importlib.util.spec_from_file_location("build_seed", SEED_PATH.parent.parent / "scripts" / "build_seed.py")
    mod = importlib.util.module_from_spec(spec_)
    spec_.loader.exec_module(mod)
    world = json.loads(mod.WORLD_PATH.read_text(encoding="utf-8"))
    assert json.loads(json.dumps(mod.build_seed(world))) == json.loads(SEED_PATH.read_text(encoding="utf-8"))


def test_people_and_dates(spec):
    seed = spec.tools[0].store.seed()
    assert seed["employee"]["name"] == "Emil Vanggaard" and seed["manager"]["name"] == "Hannes Niemi"
    assert (seed["seattle_trip"]["start"], seed["seattle_trip"]["end"]) == ("2026-10-26", "2026-10-29")
    assert seed["budget"]["period"] == "Q4 2026"
    trips = {t["date"] for t in seed["transactions"] if t["city"] not in ("Stamford", "Online")}
    local = {t["date"] for t in seed["transactions"] if t["city"] == "Stamford" and t["report_id"] != "ER-1046"}
    assert not ({d for d in trips if "2026-10-26" <= d <= "2026-10-29"} & local)


def test_step1_open_reports(spec):
    out = call(spec, "list_expense_reports", {"status": "open"}).json
    rows = {r["report_id"]: r for r in out["reports"]}
    assert set(rows) == {"ER-1044", "ER-1045", "ER-1046", "ER-1051"}
    assert rows["ER-1044"]["status"] == "Rejected" and "142.60" in rows["ER-1044"]["status_reason"]
    assert rows["ER-1046"]["status"] == "Returned" and "business purpose" in rows["ER-1046"]["status_reason"]
    assert (rows["ER-1045"]["status"], rows["ER-1045"]["total"]) == ("Pending approval", 631.5)
    assert (rows["ER-1051"]["status"], rows["ER-1051"]["total"]) == ("Pending approval", 953.09)
    assert out["approver"] == "Hannes Niemi"


def test_step2_seattle_charges_and_duplicate(spec):
    out = call(spec, "list_card_transactions", {"start_date": "2026-10-19", "end_date": "2026-10-29", "search": "Seattle"}).json
    assert out["count"] == 8
    ubers = call(spec, "list_card_transactions", {"start_date": "2026-10-26", "end_date": "2026-10-29", "search": "Uber"}).json
    flagged = [t["transaction_id"] for t in ubers["transactions"] if t.get("possible_duplicate")]
    assert ubers["count"] == 2 and flagged == ["TX-10111"]


def test_step3_and_4_report_check_and_budget(spec):
    conv = "conv-flow"
    created = create_seattle(spec, conv)
    assert created.ok, created.text
    report = created.json["report"]
    assert len(report["items"]) == 6 and not created.json["skipped"] and report["total"] == 2052.65
    assert all(i["receipt"]["attached"] for i in report["items"])
    findings = created.json["policy_check"]["findings"]
    hotel = next(f for f in findings if f["code"] == "HOTEL_OVER_CAP")
    assert hotel["severity"] == "blocking" and "2026-10-28" in json.dumps(hotel) and "139" in json.dumps(hotel)
    assert any(f["severity"] == "warning" and "Ebere Ibeabuchi" in json.dumps(f) for f in findings)

    budget = call(spec, "get_spend_vs_budget", {}).json
    assert budget["totals"]["total_spent"] == 4309.55 and budget["totals"]["budget"] == 6800
    assert budget["totals"]["percent_used"] == 63 and budget["percent_of_period_elapsed"] == 51
    used = {l["category"]: l["percent_used"] for l in budget["lines"]}
    assert (used["Meals & entertainment"], used["Ground transport"], used["Lodging"]) == (106, 111, 80)


def test_step5_justify_and_submit(spec):
    conv = "conv-submit"
    rid = create_seattle(spec, conv).json["report"]["report_id"]
    assert call(spec, "submit_expense_report", {"report_id": rid}, conv).json["submitted"] is False
    updated = call(spec, "update_expense_report", {
        "report_id": rid,
        "justification": "A city-wide convention raised the Westin rate on the last night; no hotel within the cap was available."}, conv).json
    assert updated["policy_check"]["can_submit"] and updated["policy_check"]["justified_exceptions"] == 1
    submitted = call(spec, "submit_expense_report", {"report_id": rid}, conv).json
    assert submitted["submitted"] and submitted["report"]["status"] == "Pending approval"
    assert submitted["report"]["approver"] == "Hannes Niemi"
    lodging = next(l for l in call(spec, "get_spend_vs_budget", {}, conv).json["lines"] if l["category"] == "Lodging")
    assert lodging["pending_approval"] >= 867


def test_conversations_are_isolated(spec):
    rid = create_seattle(spec, "conv-a").json["report"]["report_id"]
    assert call(spec, "get_expense_report", {"report_id": rid}, "conv-a").ok
    other = call(spec, "get_expense_report", {"report_id": rid}, "conv-b")
    assert not other.ok and "No expense report" in other.text
    assert call(spec, "list_card_transactions", {"search": "Seattle"}, "conv-b").json["count"] == 8


def test_writes_without_conversation_are_not_kept(spec):
    rid = create_seattle(spec, None).json["report"]["report_id"]
    assert not call(spec, "get_expense_report", {"report_id": rid}).ok


def test_overlays_expire():
    clock = [0.0]
    spec = build_spec(StateStore(ttl_seconds=60, monotonic=lambda: clock[0]))
    rid = create_seattle(spec, "conv-x").json["report"]["report_id"]
    clock[0] = 120
    assert not call(spec, "get_expense_report", {"report_id": rid}, "conv-x").ok


def test_policy_and_errors(spec):
    assert call(spec, "get_travel_policy", {"city": "Seattle", "topic": "lodging"}).json["hotel_nightly_cap_for_city"]["cap_usd"] == 250
    assert not call(spec, "get_expense_report", {"report_id": "ER-9999"}).ok
    assert not call(spec, "create_expense_report", {"title": "x", "items": []}).ok  # minItems 1


def test_deterministic():
    assert_deterministic(build_spec, "list_card_transactions", {"status": "all", "limit": 200})


def test_http_healthz_and_tools_list():
    client = TestClient(build_asgi_app(build_spec()))
    with client:
        assert client.get("/healthz").json()["tools"] == 9
        r = client.post("/mcp", json={"jsonrpc": "2.0", "id": 1, "method": "tools/list"},
                        headers={"Accept": "application/json, text/event-stream"})
        assert r.status_code == 200 and "submit_expense_report" in r.text