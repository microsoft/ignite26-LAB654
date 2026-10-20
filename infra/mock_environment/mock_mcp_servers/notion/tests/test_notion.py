"""Tests for the Notion mock: read formats, per-conversation writes, isolation and expiry."""

import json

import pytest
from mockmcp.app import build_asgi_app
from mockmcp.testing import assert_deterministic, call
from starlette.testclient import TestClient as StarletteClient

from mock_notion import build_spec
from mock_notion.store import SEED_PATH, StateStore

SEED = json.loads(SEED_PATH.read_text(encoding="utf-8"))
TRACKER = SEED["databases"][0]
COLL = "collection://" + TRACKER["data_source_id"]
DECISIONS = next(d for d in SEED["databases"] if "Decision" in d["title"])


@pytest.fixture
def spec():
    return build_spec()


def rows(spec, conv=None, **data):
    data.setdefault("data_source_url", COLL)
    return call(spec, "notion-query-data-sources", {"data": data}, conv).json["results"]


def print_row(spec, conv=None):
    return next(r for r in rows(spec, conv) if r["Task"].startswith("Print brochures"))


def test_search_ranks_tracker_first(spec):
    results = call(spec, "notion-search", {"query": "Verdantis Aurora Launch Tracker"}).json["results"]
    assert results[0]["title"] == "Verdantis Aurora Launch Tracker"
    assert results[0]["type"] == "database"


def test_database_fetch_shows_schema_and_views(spec):
    text = call(spec, "notion-fetch", {"id": TRACKER["id"]}).json["text"]
    assert "CREATE TABLE" in text and COLL in text
    assert '"Not Started", "In Progress", "At Risk", "Complete"' in text or "At Risk" in text
    assert "<views>" in text


def test_plan_page_fetch(spec):
    plan = next(r for r in call(spec, "notion-search", {"query": "Aurora launch plan"}).json["results"]
                if r["title"] == "Aurora Launch Plan")
    text = call(spec, "notion-fetch", {"id": plan["url"]}).json["text"]
    assert "# Aurora Launch Plan" in text and "launch-playbook" in text


def test_query_sorted_by_due(spec):
    result = rows(spec, sort=[{"property": "Due", "direction": "ascending"}])
    assert result[0]["Task"].startswith("Print brochures")
    assert result[0]["date:Due:start"] == "2026-10-16"


def test_write_visible_only_in_same_conversation(spec):
    page_id = print_row(spec)["url"].rsplit("/", 1)[1]
    update = call(spec, "notion-update-page", {"page_id": page_id, "command": "update_properties",
                                               "properties": {"Status": "At Risk", "date:Due:start": "2026-10-23"}}, "conv-a")
    assert update.ok
    assert print_row(spec, "conv-a")["Status"] == "At Risk"
    assert print_row(spec, "conv-a")["date:Due:start"] == "2026-10-23"
    for other in ("conv-b", None):
        assert print_row(spec, other)["Status"] == "In Progress"
        assert print_row(spec, other)["date:Due:start"] == "2026-10-16"


def test_write_without_conversation_is_discarded(spec):
    page_id = print_row(spec)["url"].rsplit("/", 1)[1]
    assert call(spec, "notion-update-page", {"page_id": page_id, "command": "update_properties",
                                             "properties": {"Status": "Complete"}}).ok
    assert print_row(spec)["Status"] == "In Progress"


def test_invalid_select_value_errors(spec):
    page_id = print_row(spec)["url"].rsplit("/", 1)[1]
    result = call(spec, "notion-update-page", {"page_id": page_id, "command": "update_properties",
                                               "properties": {"Status": "Blocked"}}, "conv-a")
    assert not result.ok
    assert "APIResponseError" in result.text and "Invalid select value" in result.text
    assert print_row(spec, "conv-a")["Status"] == "In Progress"


def test_create_pages_adds_row_in_conversation(spec):
    result = call(spec, "notion-create-pages", {
        "parent": {"data_source_id": TRACKER["data_source_id"]},
        "pages": [{"properties": {"Task": "Confirm split delivery", "Status": "Not Started", "date:Due:start": "2026-10-20"}}],
    }, "conv-c")
    assert result.ok, result.text
    assert any(r["Task"] == "Confirm split delivery" for r in rows(spec, "conv-c"))
    assert not any(r["Task"] == "Confirm split delivery" for r in rows(spec, "conv-d"))


def test_update_data_source_adds_select_option(spec):
    coll = "collection://" + TRACKER["data_source_id"]
    result = call(spec, "notion-update-data-source", {
        "data_source_id": TRACKER["data_source_id"],
        "statements": "ALTER COLUMN \"Status\" SET SELECT('Not Started':gray, 'In Progress':blue, 'At Risk':red, 'Complete':green, 'Blocked':orange)",
    }, "conv-e")
    assert result.ok, result.text
    page_id = print_row(spec)["url"].rsplit("/", 1)[1]
    assert call(spec, "notion-update-page", {"page_id": page_id, "command": "update_properties",
                                             "properties": {"Status": "Blocked"}}, "conv-e").ok
    assert print_row(spec, "conv-e")["Status"] == "Blocked"
    assert "Blocked" not in call(spec, "notion-fetch", {"id": coll}, "conv-f").text


def test_state_expires_after_idle_ttl():
    now = [0.0]
    store = StateStore.from_file(ttl_seconds=60, monotonic=lambda: now[0])
    spec = build_spec(store)
    page_id = print_row(spec)["url"].rsplit("/", 1)[1]
    call(spec, "notion-update-page", {"page_id": page_id, "command": "update_properties",
                                      "properties": {"Status": "At Risk"}}, "conv-x")
    assert len(store) == 1 and print_row(spec, "conv-x")["Status"] == "At Risk"
    now[0] = 61
    assert print_row(spec, "conv-x")["Status"] == "In Progress"
    assert len(store) == 0


def test_lru_cap():
    store = StateStore.from_file(max_entries=2)
    spec = build_spec(store)
    page_id = print_row(spec)["url"].rsplit("/", 1)[1]
    for conv in ("a", "b", "c"):
        call(spec, "notion-update-page", {"page_id": page_id, "command": "update_properties",
                                          "properties": {"Status": "Complete"}}, conv)
    assert len(store) == 2
    assert print_row(spec, "a")["Status"] == "In Progress"
    assert print_row(spec, "c")["Status"] == "Complete"


def test_decision_log_has_press_move(spec):
    result = rows(spec, data_source_url="collection://" + DECISIONS["data_source_id"])
    assert any("Oct 24" in r["Decision"] and r["Status"] == "Approved" for r in result)


def test_unknown_id_is_not_found(spec):
    result = call(spec, "notion-fetch", {"id": "00000000000000000000000000000000"})
    assert not result.ok and "object_not_found" in result.text


def test_deterministic():
    assert_deterministic(build_spec, "notion-search", {"query": "launch tracker"})
    assert_deterministic(build_spec, "notion-fetch", {"id": TRACKER["id"]})


def test_healthz():
    client = StarletteClient(build_asgi_app(build_spec()))
    assert client.get("/healthz").status_code == 200


# --- page viewer --------------------------------------------------------------------------------------------------

BASE = "https://mock.example"


@pytest.fixture
def web():
    store = StateStore.from_file(secret=b"test")
    spec = build_spec(store, public_base_url=BASE)
    return spec, store, StarletteClient(build_asgi_app(spec))


def local(url):
    assert url.startswith(BASE)
    return url[len(BASE):]


def test_links_stay_app_notion_without_base_url(spec):
    assert print_row(spec, "conv-a")["url"].startswith("https://app.notion.com/p/")


def test_links_point_at_viewer_with_view_token(web):
    spec, store, _ = web
    assert print_row(spec)["url"].startswith(f"{BASE}/p/")
    assert print_row(spec, "conv-a")["url"].startswith(f"{BASE}/v/{store.view_token('conv-a')}/p/")
    text = call(spec, "notion-fetch", {"id": TRACKER["id"]}, "conv-a").json["text"]
    assert "app.notion.com" not in text


def test_viewer_urls_round_trip_into_tools(web):
    spec, _, _ = web
    url = print_row(spec, "conv-a")["url"]
    assert call(spec, "notion-fetch", {"id": url}, "conv-a").ok
    assert call(spec, "notion-update-page", {"page_id": url, "command": "update_properties",
                                             "properties": {"Status": "At Risk"}}, "conv-a").ok


def test_database_and_row_pages_render(web):
    spec, _, client = web
    db = client.get(f"/p/{TRACKER['id'].replace('-', '')}")
    assert db.status_code == 200
    assert "Verdantis Aurora Launch Tracker" in db.text and "Print brochures" in db.text
    assert "MOCK NOTION" in db.text and "original workspace" in db.text
    row = client.get(local(print_row(spec)["url"]))
    assert row.status_code == 200 and "In Progress" in row.text and "October 16, 2026" in row.text


def test_viewer_shows_conversation_changes_only_with_its_token(web):
    spec, _, client = web
    url = print_row(spec, "conv-a")["url"]
    call(spec, "notion-update-page", {"page_id": url, "command": "update_properties",
                                      "properties": {"Status": "At Risk"}}, "conv-a")
    scoped = client.get(local(url))
    assert "At Risk" in scoped.text and "this conversation" in scoped.text
    plain = client.get(local(print_row(spec)["url"]))
    assert "At Risk" not in plain.text.split('<div class="props">')[1].split("</div></div></div>")[0]
    other = client.get(local(print_row(spec, "conv-b")["url"]))
    assert "No saved changes" in other.text


def test_created_page_opens_in_viewer(web):
    spec, _, client = web
    created = call(spec, "notion-create-pages", {"pages": [{"properties": {"title": "Retro <notes>"},
                                                            "content": "## Wins\n- [x] **Shipped** <script>x</script>"}]},
                   "conv-a").json
    url = created["pages"][0]["url"]
    page = client.get(local(url))
    assert page.status_code == 200
    assert "Retro &lt;notes&gt;" in page.text and "&lt;script&gt;" in page.text and "<script>" not in page.text
    assert client.get(local(url.replace(url.split("/v/")[1].split("/")[0], "0" * 20))).status_code == 404


def test_viewer_not_found_and_bad_token(web):
    _, _, client = web
    assert client.get("/p/deadbeef").status_code == 404
    assert client.get("/v/not-a-token/p/x").status_code == 404
    assert client.get("/", follow_redirects=False).headers["location"].startswith("/p/")
