import pytest
from starlette.testclient import TestClient

from mock_atlassian import build_spec
from mock_atlassian.store import StateStore
from mock_atlassian.tools import load_schemas
from mockmcp.app import build_asgi_app
from mockmcp.testing import call

CLOUD = "a6d131af-e79b-5495-ab06-65cad3645500"
SPRINT_KEYS = ["AUR-133", "AUR-136", "AUR-137", "AUR-139", "AUR-142", "AUR-151"]


@pytest.fixture(scope="module")
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
    assert {s["id"] for s in sites} == {CLOUD} and {s["name"] for s in sites} == {"zava-online"}
    me = call(spec, "atlassianUserInfo", {}).json
    assert me["name"] == "Emil Vanggaard" and me["email"] == "emil@zava-online.com"


def test_unknown_cloud_id(spec):
    got = call(spec, "getJiraIssue", {"cloudId": "nope", "issueIdOrKey": "AUR-142"})
    assert not got.ok and got.json["error"] is True and "getAccessibleAtlassianResources" in got.json["message"]


# --- scenario reads --------------------------------------------------------------------------------------------

def test_default_fields_match_live(spec):
    f = _ok(spec, "getJiraIssue", {"issueIdOrKey": "AUR-142"})["fields"]
    assert "summary" in f and "status" in f and "comment" not in f and "issuelinks" not in f


def test_aur_142_story(spec):
    issue = _issue(spec, "AUR-142")
    f = issue["fields"]
    assert f["summary"] == "Aurora hubs remain offline after reconnect"
    assert f["status"]["name"] == "In Progress" and f["priority"]["name"] == "High"
    assert f["assignee"]["displayName"] == "Triin Lepp"
    assert set(f["labels"]) == {"lakeshore-retail-pilot", "at-risk"}
    assert f["timeoriginalestimate"] == 8 * 3600
    comments = f["comment"]["comments"]
    assert len(comments) == 3 and "started working on the fix" in str(comments[0]["body"])
    assert comments[0]["created"].startswith("2026-10-26")
    assert f["issuelinks"] == []


def test_sprint_has_one_item_at_risk(spec):
    keys = _jql(spec, "sprint in openSprints() ORDER BY key")
    assert keys == SPRINT_KEYS
    assert _jql(spec, "sprint in openSprints() AND labels = at-risk") == ["AUR-142"]
    done = _jql(spec, "sprint = 241 AND statusCategory = Done ORDER BY key")
    assert done == ["AUR-133", "AUR-137"]


@pytest.mark.parametrize("jql,expected", [
    ('project = AUR AND assignee = "Triin Lepp" ORDER BY key', ["AUR-137", "AUR-142", "AUR-151"]),
    ("project = AUR AND status = 'In Progress' ORDER BY key", ["AUR-136", "AUR-139", "AUR-142"]),
    ("project = AUR AND priority IN (High) ORDER BY key", ["AUR-133", "AUR-139", "AUR-142"]),
    ('text ~ "dashboard filters"', ["AUR-151"]),
    ("key = AUR-142 OR key = AUR-151 ORDER BY key DESC", ["AUR-151", "AUR-142"]),
    ("project = AUR AND sprint is EMPTY", []),
    ("project = NOPE", []),
])
def test_jql(spec, jql, expected):
    assert _jql(spec, jql) == expected


def test_missing_issue_is_rest_404(spec):
    got = call(spec, "getJiraIssue", {"cloudId": CLOUD, "issueIdOrKey": "AUR-999"})
    assert not got.ok and got.json["statusCode"] == 404
    assert "Issue does not exist" in got.json["message"]


def test_compass_is_out_of_scope(spec):
    got = call(spec, "getCompassComponents", {"cloudId": CLOUD})
    assert not got.ok and "read:component:compass" in got.json["message"]


# --- Confluence ------------------------------------------------------------------------------------------------

def test_confluence_space_and_pages(spec):
    spaces = _ok(spec, "getConfluenceSpaces", {})["results"]
    assert [(s["id"], s["key"], s["name"]) for s in spaces] == [("98306", "AUR", "Aurora Engineering")]
    pages = _ok(spec, "getPagesInConfluenceSpace", {"spaceId": "98306"})["results"]
    assert {p["id"] for p in pages} == {"98411", "98433", "98457", "98472", "98480"}


def test_confluence_page_bodies(spec):
    adr = _ok(spec, "getConfluencePage", {"pageId": "98457", "contentFormat": "markdown"})
    assert adr["title"].startswith("ADR-014") and adr["version"]["number"] == 3
    assert "Tama" in adr["body"]["markdown"]["value"] if "markdown" in adr["body"] else True
    commitments = _ok(spec, "getConfluencePage", {"pageId": "98433"})
    assert "November 23" in str(commitments["body"])
    assert commitments["_links"]["webui"].startswith("/spaces/AUR/pages/98433/")


def test_confluence_cql(spec):
    def titles(cql):
        return [r["content"]["id"] if "content" in r else r["id"]
                for r in _ok(spec, "searchConfluenceUsingCql", {"cql": cql})["results"]]
    assert set(titles('type = page AND label = "lakeshore-retail-pilot"')) == {"98433", "98457"}
    assert titles('space = AUR AND title ~ "ADR-014"') == ["98457"]
    assert titles('text ~ "nothing-matches-this"') == []


def test_confluence_comments(spec):
    comments = _ok(spec, "getConfluencePageFooterComments", {"pageId": "98457"})["results"]
    assert len(comments) == 1 and "ready for your decision" in str(comments[0])


def test_confluence_writes_are_per_conversation(spec):
    conv = "conv-wiki"
    page = _ok(spec, "createConfluencePage", {"spaceId": "AUR", "title": "Pilot follow-up",
                                              "body": "<p>Next steps for AUR-142.</p>"}, conv)
    assert page["id"] == "98500" and page["parentId"] == "98411"
    _ok(spec, "createConfluenceFooterComment", {"pageId": "98457", "body": "Approved option B."}, conv)
    assert len(_ok(spec, "getConfluencePageFooterComments", {"pageId": "98457"}, conv)["results"]) == 2
    assert len(_ok(spec, "getConfluencePageFooterComments", {"pageId": "98457"}, "conv-x")["results"]) == 1
    assert not call(spec, "getConfluencePage", {"cloudId": CLOUD, "pageId": "98500"}, "conv-x").ok
    dup = call(spec, "createConfluencePage", {"cloudId": CLOUD, "spaceId": "AUR", "title": "Pilot follow-up",
                                              "body": "x"}, conv)
    assert not dup.ok


def test_rovo_search_and_fetch(spec):
    hits = call(spec, "search", {"query": "ADR-014 reconnect"}).json["results"]
    assert any(h["id"].endswith(":confluence:" + h["id"].split(":confluence:")[-1]) and "98457" in h["id"]
               for h in hits)
    assert any("AUR-142" in str(h) for h in hits)
    page_ari = next(h["id"] for h in hits if "98457" in h["id"])
    fetched = call(spec, "fetch", {"id": page_ari}).json
    assert fetched["type"] == "confluence-page" and "ADR-014" in fetched["title"]


def test_invalid_arguments(spec):
    got = call(spec, "getJiraIssue", {"cloudId": CLOUD})
    assert not got.ok and "Invalid arguments for tool getJiraIssue" in got.json["message"]


# --- writes, per conversation ----------------------------------------------------------------------------------

def test_writes_are_per_conversation(spec):
    conv = "conv-writes"
    created = _ok(spec, "createJiraIssue", {"projectKey": "AUR", "issueTypeName": "Task",
                                            "summary": "Validate reconnect on the new service"}, conv)
    key = created["key"]
    assert key == "AUR-152"
    _ok(spec, "editJiraIssue", {"issueIdOrKey": "AUR-151", "fields": {"priority": {"name": "Lowest"}}}, conv)
    _ok(spec, "addCommentToJiraIssue", {"issueIdOrKey": "AUR-142", "commentBody": "Moving to the new service."}, conv)
    _ok(spec, "addWorklogToJiraIssue", {"issueIdOrKey": "AUR-142", "timeSpent": "2h"}, conv)
    transitions = _ok(spec, "getTransitionsForJiraIssue", {"issueIdOrKey": key}, conv)["transitions"]
    done = next(t["id"] for t in transitions if t["to"]["statusCategory"]["key"] == "done")
    _ok(spec, "transitionJiraIssue", {"issueIdOrKey": key, "transition": {"id": done}}, conv)

    assert _issue(spec, key, conv)["fields"]["status"]["statusCategory"]["key"] == "done"
    assert _issue(spec, "AUR-151", conv)["fields"]["priority"]["name"] == "Lowest"
    f = _issue(spec, "AUR-142", conv)["fields"]
    assert len(f["comment"]["comments"]) == 4
    assert [w["timeSpentSeconds"] for w in f["worklog"]["worklogs"]][-1] == 2 * 3600

    # Other conversations and header-less calls see the seed.
    assert call(spec, "getJiraIssue", {"cloudId": CLOUD, "issueIdOrKey": key}, "conv-other").json["statusCode"] == 404
    assert _issue(spec, "AUR-151")["fields"]["priority"]["name"] == "Low"
    assert len(_issue(spec, "AUR-142", "conv-other")["fields"]["comment"]["comments"]) == 3


def test_edit_cannot_set_status(spec):
    got = call(spec, "editJiraIssue", {"cloudId": CLOUD, "issueIdOrKey": "AUR-142",
                                       "fields": {"status": {"name": "Done"}}}, "conv-status")
    assert not got.ok and "transitionJiraIssue" in got.json["message"]


def test_issue_link_is_visible(spec):
    conv = "conv-link"
    _ok(spec, "createIssueLink", {"type": "Blocks", "inwardIssue": "AUR-151", "outwardIssue": "AUR-142"}, conv)
    links = _issue(spec, "AUR-142", conv)["fields"]["issuelinks"]
    assert {(link.get("outwardIssue") or link.get("inwardIssue"))["key"] for link in links} == {"AUR-151"}


# --- viewer ----------------------------------------------------------------------------------------------------

def test_viewer_pages(web):
    _, _, client = web
    for path in ("/jira/software/projects/AUR/boards/57", "/jira/software/projects/AUR/boards/57/backlog",
                 "/jira/software/projects/AUR/list?text=reconnect", "/browse/AUR-142"):
        res = client.get(path)
        assert res.status_code == 200, path
        assert "Not affiliated with Atlassian" in res.text
    assert "Aurora hubs remain offline after reconnect" in client.get("/browse/AUR-142").text
    assert client.get("/healthz").status_code == 200


def test_viewer_redirects_and_404s(web):
    _, _, client = web
    assert client.get("/browse/aur-142").headers["location"] == "/browse/AUR-142"
    assert client.get(f"/ex/jira/{CLOUD}/rest/api/3/issue/10142").headers["location"] == "/browse/AUR-142"
    assert client.get("/browse/AUR-999").status_code == 404
    assert client.get("/v/not-a-token/browse/AUR-142").status_code == 404


def test_viewer_shows_conversation_changes(web):
    spec, _, client = web
    key = _ok(spec, "createJiraIssue", {"projectKey": "AUR", "issueTypeName": "Task",
                                        "summary": "Viewer check"}, "conv-view")["key"]
    location = client.get(f"/browse/{key}").headers["location"]
    assert location.startswith("/v/") and location.endswith(f"/browse/{key}")
    assert "Viewer check" in client.get(location).text
    board = location.rsplit("/browse/", 1)[0] + "/jira/software/projects/AUR/list"
    assert key in client.get(board).text
    assert key not in client.get("/jira/software/projects/AUR/list").text


def test_wiki_viewer(web):
    spec, _, client = web
    assert client.get("/wiki").headers["location"] == "/wiki/spaces/AUR/pages/98411/Aurora+Engineering"
    res = client.get("/wiki/spaces/AUR/pages/98457/ADR-014")
    assert res.status_code == 200 and "MOCK ATLASSIAN · CONFLUENCE" in res.text and "comment-99012" in res.text
    assert client.get("/wiki/rest/api/content/98433").headers["location"].startswith("/wiki/spaces/AUR/pages/98433/")
    assert client.get("/wiki/spaces/AUR/pages/99999").status_code == 404
    page = _ok(spec, "createConfluencePage", {"spaceId": "AUR", "title": "Viewer page", "body": "<p>hi</p>"}, "cv")
    location = client.get(f"/wiki/spaces/AUR/pages/{page['id']}").headers["location"]
    assert location.startswith("/v/") and "Viewer page" in client.get(location).text
