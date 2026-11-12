from datetime import date

import pytest
from starlette.testclient import TestClient

from mock_atlassian import build_spec
from mock_atlassian.store import StateStore, build_seed
from mock_atlassian.tools import load_schemas
from mockmcp.app import build_asgi_app
from mockmcp.testing import call

CLOUD = "3f6c2a1e-8b4d-5c7e-9a2f-1d0b7e4c6a58"
CONTOSO_OPEN = ["INC-40188", "INC-40211", "INC-40302"]


@pytest.fixture(autouse=True)
def _fixed_env(monkeypatch):
    monkeypatch.setenv("MOCK_NOW", "2026-11-18T15:00:00Z")
    monkeypatch.delenv("TENANT_EMAIL_DOMAIN", raising=False)


@pytest.fixture()
def spec():
    return build_spec()


@pytest.fixture()
def web():
    store = StateStore()
    spec = build_spec(store=store)
    return spec, store, TestClient(build_asgi_app(spec), follow_redirects=False)


def _ok(spec, tool, args, conv=None):
    got = call(spec, tool, {"cloudId": CLOUD, **args}, conv)
    assert got.ok, got.text
    return got.json


def _issue(spec, key, conv=None, fields=("*all",)):
    return _ok(spec, "getJiraIssue", {"issueIdOrKey": key, "fields": list(fields)}, conv)


def _jql(spec, jql, conv=None, fields=("summary",)):
    return [i["key"] for i in _ok(spec, "searchJiraIssuesUsingJql", {"jql": jql, "fields": list(fields)}, conv)["issues"]]


# --- tool surface ----------------------------------------------------------------------------------------------

def test_tools_use_real_schemas(spec):
    real = load_schemas()
    tools = {t.name: t for t in spec.tools}
    assert len(tools) == 41 and set(tools) == set(real)
    for name, tool in tools.items():
        assert tool.description == real[name]["description"]
        assert tool.input_schema == real[name]["inputSchema"]


def test_site_and_user(spec):
    sites = call(spec, "getAccessibleAtlassianResources", {}).json
    assert {s["id"] for s in sites} == {CLOUD} and {s["name"] for s in sites} == {"northwind-ltd"}
    me = call(spec, "atlassianUserInfo", {}).json
    assert me["name"] == "Megan Bowen" and me["email"] == "megan@northwind-ltd.example"


def test_unknown_cloud_id(spec):
    got = call(spec, "getJiraIssue", {"cloudId": "nope", "issueIdOrKey": "INC-40211"})
    assert not got.ok and got.json["error"] is True and "getAccessibleAtlassianResources" in got.json["message"]


# --- relative dates and domain ---------------------------------------------------------------------------------

def test_ticket_ages_follow_the_mock_date():
    on_demo_day = {i["key"]: i["created"][:10] for i in build_seed(today=date(2026, 11, 18))["issues"]}
    assert on_demo_day["INC-40211"] == "2026-11-09"  # 9 days old
    assert on_demo_day["INC-40188"] == "2026-11-06"  # 12 days old
    assert on_demo_day["INC-40302"] == "2026-11-14"  # 4 days old
    rehearsal = build_seed(today=date(2026, 11, 10))
    assert {i["key"]: i["created"][:10] for i in rehearsal["issues"]}["INC-40211"] == "2026-11-01"
    page = next(p for p in rehearsal["confluence"]["pages"] if p["id"] == "131105")
    assert page["created"].startswith("2026-09-30")


def test_email_domain_from_env(monkeypatch):
    monkeypatch.setenv("TENANT_EMAIL_DOMAIN", "contoso-demo.onmicrosoft.com")
    users = {u["key"]: u["email"] for u in build_seed()["users"]}
    assert users["megan"] == "megan@contoso-demo.onmicrosoft.com"


# --- scenario reads --------------------------------------------------------------------------------------------

def test_three_open_contoso_incidents_two_unassigned(spec):
    jql = "project = INC AND labels = customer-contoso AND statusCategory != Done ORDER BY key"
    assert _jql(spec, jql) == CONTOSO_OPEN
    unassigned = "project = INC AND labels = customer-contoso AND statusCategory != Done AND assignee is EMPTY"
    assert _jql(spec, unassigned + " ORDER BY key") == ["INC-40211", "INC-40302"]
    f = _issue(spec, "INC-40188")["fields"]
    assert f["assignee"]["displayName"] == "Rosa Diaz" and f["priority"]["name"] == "Highest"
    priorities = {k: _issue(spec, k)["fields"]["priority"]["name"] for k in CONTOSO_OPEN}
    assert priorities == {"INC-40188": "Highest", "INC-40211": "Highest", "INC-40302": "High"}


def test_priority_order_puts_highest_first(spec):
    jql = "project = INC AND labels = customer-contoso AND statusCategory != Done ORDER BY priority DESC, created ASC"
    assert _jql(spec, jql) == ["INC-40188", "INC-40211", "INC-40302"]


def test_latency_tickets_match_the_escalation(spec):
    keys = _jql(spec, "project = INC AND labels = customer-contoso AND labels = latency "
                      "AND statusCategory != Done ORDER BY key")
    assert keys == ["INC-40211", "INC-40302"]
    f = _issue(spec, "INC-40211")["fields"]
    assert "EU" in f["summary"] and f["assignee"] is None and f["issuetype"]["name"] == "Incident"
    assert "Lidia Holloway" in str(f["comment"]["comments"])


def test_kumar_resolved_contoso_latency_before(spec):
    jql = "project = INC AND labels = customer-contoso AND labels = latency AND statusCategory = Done ORDER BY key"
    keys = _jql(spec, jql)
    assert keys == ["INC-39412", "INC-39750"]
    assert {_issue(spec, k)["fields"]["assignee"]["displayName"] for k in keys} == {"Arjun Kumar"}


def test_other_contoso_is_a_separate_label(spec):
    assert _jql(spec, 'text ~ "Contoso Pharmaceuticals"') == ["INC-40260"]
    assert "INC-40260" not in _jql(spec, "labels = customer-contoso")


@pytest.mark.parametrize("jql,expected", [
    ('project = INC AND assignee = "Arjun Kumar" ORDER BY key', ["INC-39412", "INC-39750"]),
    ("project = INC AND priority IN (Highest, High) AND status = 'To Do' ORDER BY key", ["INC-40211", "INC-40302"]),
    ('text ~ "bulk export"', ["INC-40302"]),
    ("project = NOPE", []),
])
def test_jql(spec, jql, expected):
    assert _jql(spec, jql) == expected


def test_missing_issue_is_rest_404(spec):
    got = call(spec, "getJiraIssue", {"cloudId": CLOUD, "issueIdOrKey": "INC-99999"})
    assert not got.ok and got.json["statusCode"] == 404


def test_compass_is_out_of_scope(spec):
    got = call(spec, "getCompassComponents", {"cloudId": CLOUD})
    assert not got.ok and "read:component:compass" in got.json["message"]


# --- Confluence ------------------------------------------------------------------------------------------------

def test_confluence_spaces_and_pages(spec):
    spaces = _ok(spec, "getConfluenceSpaces", {})["results"]
    assert {(s["id"], s["key"]) for s in spaces} == {("131072", "CS"), ("131200", "PROD")}
    pages = _ok(spec, "getPagesInConfluenceSpace", {"spaceId": "131072"})["results"]
    assert {p["id"] for p in pages} == {"131073", "131090", "131105"}


def test_sso_ask_is_open_and_roadmap_is_committable(spec):
    overview = _ok(spec, "getConfluencePage", {"pageId": "131090", "contentFormat": "markdown"})
    body = str(overview["body"])
    assert "SSO roadmap commitment" in body and "None yet" in body
    roadmap = _ok(spec, "getConfluencePage", {"pageId": "131230"})
    assert "March 31, 2027" in str(roadmap["body"])
    assert roadmap["_links"]["webui"].startswith("/spaces/PROD/pages/131230/")


def test_confluence_cql(spec):
    def ids(cql):
        return [r["content"]["id"] if "content" in r else r["id"]
                for r in _ok(spec, "searchConfluenceUsingCql", {"cql": cql})["results"]]
    assert set(ids('type = page AND label = "contoso-ltd"')) == {"131090", "131105"}
    assert ids('space = PROD AND title ~ "SSO roadmap"') == ["131230"]
    assert ids('text ~ "nothing-matches-this"') == []


def test_confluence_writes_are_per_conversation(spec):
    page = _ok(spec, "createConfluencePage", {"spaceId": "CS", "title": "Contoso renewal plan",
                                              "body": "<p>Owners for INC-40211.</p>"}, "conv-wiki")
    assert page["id"] == "131500" and page["parentId"] == "131073"
    assert not call(spec, "getConfluencePage", {"cloudId": CLOUD, "pageId": "131500"}, "conv-x").ok


def test_rovo_search_and_fetch(spec):
    hits = call(spec, "search", {"query": "Contoso SSO roadmap"}).json["results"]
    page_ari = next(h["id"] for h in hits if "131090" in h["id"] or "131230" in h["id"])
    assert call(spec, "fetch", {"id": page_ari}).json["type"] == "confluence-page"


# --- close-out writes, per conversation ------------------------------------------------------------------------

def test_assign_latency_tickets_to_kumar(spec):
    conv = "conv-close-out"
    found = _ok(spec, "lookupJiraAccountId", {"searchString": "Arjun Kumar"})["data"]["users"]["users"]
    assert [u["displayName"] for u in found] == ["Arjun Kumar"]
    for key in ("INC-40211", "INC-40302"):
        _ok(spec, "editJiraIssue", {"issueIdOrKey": key, "fields": {"assignee": {"accountId": found[0]["accountId"]}}},
            conv)
        _ok(spec, "addCommentToJiraIssue",
            {"issueIdOrKey": key, "commentBody": "Assigned to Arjun Kumar ahead of the Contoso renewal."}, conv)
    assert _issue(spec, "INC-40211", conv)["fields"]["assignee"]["displayName"] == "Arjun Kumar"
    assert _jql(spec, "labels = customer-contoso AND statusCategory != Done AND assignee is EMPTY", conv) == []
    assert _issue(spec, "INC-40211")["fields"]["assignee"] is None


def test_new_issue_continues_numbering(spec):
    created = _ok(spec, "createJiraIssue", {"projectKey": "INC", "issueTypeName": "Task",
                                            "summary": "Contoso EU capacity check"}, "conv-new")
    assert created["key"] == "INC-40303"
    assert _issue(spec, "INC-40303", "conv-new")["fields"]["priority"]["name"] == "Medium"


def test_edit_cannot_set_status(spec):
    got = call(spec, "editJiraIssue", {"cloudId": CLOUD, "issueIdOrKey": "INC-40211",
                                       "fields": {"status": {"name": "Done"}}}, "conv-status")
    assert not got.ok and "transitionJiraIssue" in got.json["message"]


def test_shared_state_crosses_conversations(monkeypatch):
    monkeypatch.setenv("MOCK_SHARED_STATE", "1")
    store = StateStore()
    spec = build_spec(store=store)
    account = "712020:9c4d2e7f-1a6b-5c38-8d0e-4f2a7b9c1d63"
    _ok(spec, "editJiraIssue", {"issueIdOrKey": "INC-40211", "fields": {"assignee": {"accountId": account}}},
        "cowork-conversation")
    assert _issue(spec, "INC-40211", "github-copilot-session")["fields"]["assignee"]["displayName"] == "Arjun Kumar"
    assert _issue(spec, "INC-40211")["fields"]["assignee"]["displayName"] == "Arjun Kumar"
    client = TestClient(build_asgi_app(spec), follow_redirects=False)
    assert "Arjun Kumar" in client.get("/browse/INC-40211").text


# --- viewer ----------------------------------------------------------------------------------------------------

def test_viewer_pages(web):
    _, _, client = web
    for path in ("/jira/software/projects/INC/boards/12", "/jira/software/projects/INC/boards/12/backlog",
                 "/jira/software/projects/INC/list?text=latency", "/browse/INC-40211"):
        res = client.get(path)
        assert res.status_code == 200, path
        assert "Not affiliated with Atlassian" in res.text and "BRK220" in res.text
    assert "INC-40211" in client.get("/jira/software/projects/INC/boards/12").text
    assert "API latency in EU region" in client.get("/browse/INC-40211").text
    assert client.get("/healthz").status_code == 200


def test_viewer_redirects_and_404s(web):
    _, _, client = web
    assert client.get("/browse/inc-40211").headers["location"] == "/browse/INC-40211"
    assert client.get(f"/ex/jira/{CLOUD}/rest/api/3/issue/40211").headers["location"] == "/browse/INC-40211"
    assert client.get("/browse/INC-99999").status_code == 404


def test_viewer_shows_conversation_changes(web):
    spec, _, client = web
    _ok(spec, "addCommentToJiraIssue", {"issueIdOrKey": "INC-40211", "commentBody": "Viewer check note"}, "cv")
    created = _ok(spec, "createJiraIssue", {"projectKey": "INC", "issueTypeName": "Task",
                                            "summary": "Viewer check"}, "cv")
    location = client.get(f"/browse/{created['key']}").headers["location"]
    assert location.startswith("/v/")
    scoped = location.rsplit("/browse/", 1)[0]
    assert "Viewer check note" in client.get(f"{scoped}/browse/INC-40211").text
    assert "Viewer check note" not in client.get("/browse/INC-40211").text


def test_wiki_viewer(web):
    _, _, client = web
    assert client.get("/wiki").headers["location"] == "/wiki/spaces/CS/pages/131073/Customer+Success"
    res = client.get("/wiki/spaces/CS/pages/131090/Contoso")
    assert res.status_code == 200 and "MOCK ATLASSIAN · CONFLUENCE" in res.text and "comment-132010" in res.text
    assert client.get("/wiki/spaces/PROD/pages/131230/x").status_code == 200
    assert client.get("/wiki/spaces/PROD").headers["location"] == "/wiki/spaces/PROD/pages/131201/Product+Roadmap"


def test_mock_branding_can_be_hidden(web, monkeypatch):
    _, _, client = web
    assert "mock-badge\"" in client.get("/browse/INC-40211").text
    monkeypatch.setenv("MOCK_BADGE", "0")
    page = client.get("/browse/INC-40211").text
    assert "mock-badge\"" not in page and "Mock environment" not in page
