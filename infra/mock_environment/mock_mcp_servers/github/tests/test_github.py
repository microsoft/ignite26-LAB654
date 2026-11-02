import json
from pathlib import Path

import pytest
from starlette.testclient import TestClient

from mock_github import build_spec
from mock_github.tools import TOOLS, load_schemas
from mockmcp.app import build_asgi_app
from mockmcp.testing import call

REPO = {"owner": "zava-lab", "repo": "aurora-status"}
JSONL = (Path(__file__).resolve().parents[3] / "Connectors_Ignite_EMP" / "customconnectors"
         / "customconnectors_engineering.jsonl")
WRITE_WORDS = ("create", "update", "merge", "delete", "add_", "write", "submit", "request_copilot", "fork", "push")


@pytest.fixture(scope="module")
def spec():
    return build_spec()


def ok(spec, tool, args=None):
    got = call(spec, tool, args or {})
    assert got.ok, got.text
    return got.json


def err(spec, tool, args):
    got = call(spec, tool, args)
    assert not got.ok
    return got.text


# --- tool surface --------------------------------------------------------------------------------------------------

def test_exactly_the_eight_read_tools():
    names = [t["name"] for t in json.loads((Path(__file__).parents[1] / "seed_files" / "tool_schemas.json")
                                           .read_text(encoding="utf-8"))]
    assert names == ["get_me", "search_users", "search_repositories", "list_pull_requests", "search_pull_requests",
                     "pull_request_read", "list_label", "get_label"]
    assert [t.name for t in TOOLS] == names


def test_every_tool_is_read_only(spec):
    schemas = load_schemas()
    for tool in spec.tools:
        assert schemas[tool.name]["annotations"]["readOnlyHint"] is True
        assert tool.annotations.get("readOnlyHint") is True
        assert not any(w in tool.name for w in WRITE_WORDS)


# --- seed fidelity -------------------------------------------------------------------------------------------------

def test_seed_matches_connector_items(spec):
    items = [it for line in JSONL.read_text(encoding="utf-8").splitlines() if line.strip()
             for it in json.loads(line)["Items"]]
    prs = {p["number"]: p for p in ok(spec, "list_pull_requests", {**REPO, "state": "all"})}
    assert sorted(prs) == sorted(int(it["properties"]["Id"]) for it in items)
    for it in items:
        p, pr = it["properties"], prs[int(it["properties"]["Id"])]
        assert pr["title"] == p["Title"]
        assert pr["body"] == p["Description"]
        assert pr["labels"] == p["Labels"]
        assert pr["milestone"] == p["Milestone"]
        assert pr["merged"] == (p["State"] == "Merged")
        assert pr["created_at"] == p["CreatedAt"]


# --- pull requests -------------------------------------------------------------------------------------------------

def test_search_by_jira_key_finds_287(spec):
    got = ok(spec, "search_pull_requests", {"query": "AUR-142"})
    assert got["total_count"] == 1
    item = got["items"][0]
    assert item["number"] == 287 and item["state"] == "open"
    assert item["pull_request"]["html_url"].endswith("/zava-lab/aurora-status/pull/287")


def test_search_scoping_and_qualifiers(spec):
    assert ok(spec, "search_pull_requests", {"query": "is:merged", **REPO})["total_count"] == 3
    assert [i["number"] for i in ok(spec, "search_pull_requests", {"query": "author:maria-oliva"})["items"]] == [269]
    assert ok(spec, "search_pull_requests", {"query": "review:changes_requested"})["items"][0]["number"] == 287
    assert ok(spec, "search_pull_requests", {"query": "label:migration is:closed"})["items"][0]["number"] == 276
    assert ok(spec, "search_pull_requests", {"query": "AUR-142", "owner": "zava-lab",
                                             "repo": "other"})["total_count"] == 0
    assert ok(spec, "search_pull_requests", {"query": "pilot in:comments"})["items"][0]["number"] == 287


def test_search_fields_filter(spec):
    got = ok(spec, "search_pull_requests", {"query": "AUR-142", "fields": ["number", "title"]})
    assert got["items"] == [{"number": 287, "title": "Fix stale offline state after reconnect"}]


def test_list_defaults_to_open(spec):
    got = ok(spec, "list_pull_requests", REPO)
    assert [p["number"] for p in got] == [287]
    assert set(got[0]) >= {"number", "title", "body", "state", "draft", "merged", "html_url", "user", "labels"}
    assert "head" not in got[0] and "additions" not in got[0]


def test_list_unknown_repo_is_404(spec):
    text = err(spec, "list_pull_requests", {"owner": "zava-lab", "repo": "nope"})
    assert "404 Not Found" in text


def test_pull_request_read_get_and_reviews(spec):
    pr = ok(spec, "pull_request_read", {"method": "get", **REPO, "pullNumber": 287})
    assert pr["title"] == "Fix stale offline state after reconnect" and pr["merged"] is False
    reviews = ok(spec, "pull_request_read", {"method": "get_reviews", **REPO, "pullNumber": 287})
    assert len(reviews) == 1
    assert reviews[0]["state"] == "CHANGES_REQUESTED" and reviews[0]["user"]["login"] == "tama-surya"
    assert "November 20" in reviews[0]["body"]
    merged = ok(spec, "pull_request_read", {"method": "get", **REPO, "pullNumber": 281})
    assert merged["merged_at"] == "2026-10-16T19:20:00Z"


def test_pull_request_read_unseeded_and_missing(spec):
    assert "not available in this mock" in err(spec, "pull_request_read",
                                               {"method": "get_diff", **REPO, "pullNumber": 287})
    assert "404 Not Found" in err(spec, "pull_request_read", {"method": "get", **REPO, "pullNumber": 9})
    assert ok(spec, "pull_request_read", {"method": "get_comments", **REPO, "pullNumber": 287}) == []


def test_missing_required_param(spec):
    assert err(spec, "list_pull_requests", {"owner": "zava-lab"}) == "missing required parameter: repo"


# --- context tools -------------------------------------------------------------------------------------------------

def test_get_me(spec):
    me = ok(spec, "get_me")
    assert me["login"] == "emil-vanggaard" and me["details"]["name"] == "Emil Vanggaard"


def test_search_users_and_repos(spec):
    assert [u["login"] for u in ok(spec, "search_users", {"query": "tama"})["items"]] == ["tama-surya"]
    repos = ok(spec, "search_repositories", {"query": "aurora org:zava-lab"})
    assert repos["items"][0]["full_name"] == "zava-lab/aurora-status"
    assert repos["items"][0]["open_issues_count"] == 1


def test_labels(spec):
    got = ok(spec, "list_label", REPO)
    assert got["totalCount"] == 5 and got["labels"][0]["name"] == "aurora-status"
    assert ok(spec, "get_label", {**REPO, "name": "bug"})["color"] == "d73a4a"
    assert err(spec, "get_label", {**REPO, "name": "nope"}) == "label 'nope' not found in zava-lab/aurora-status"


# --- viewer --------------------------------------------------------------------------------------------------------

def test_viewer_pages(spec):
    web = TestClient(build_asgi_app(spec), follow_redirects=False)
    assert web.get("/").status_code == 302
    for path, text in [("/zava-lab", "aurora-status"), ("/zava-lab/aurora-status", "Recent pull requests"),
                       ("/zava-lab/aurora-status/pulls", "Fix stale offline state"),
                       ("/zava-lab/aurora-status/pulls?q=is%3Apr+is%3Aclosed", "Add retry backoff"),
                       ("/zava-lab/aurora-status/pull/287", "requested changes"),
                       ("/zava-lab/aurora-status/labels", "5 labels"), ("/tama-surya", "Tama Surya")]:
        r = web.get(path)
        assert r.status_code == 200, path
        assert text in r.text, path
        assert "MOCK GITHUB" in r.text
    assert web.get("/avatars/triin-lepp.svg").headers["content-type"].startswith("image/svg")
    assert web.get("/zava-lab/aurora-status/pull/9").status_code == 404
    assert web.get("/healthz").status_code == 200
