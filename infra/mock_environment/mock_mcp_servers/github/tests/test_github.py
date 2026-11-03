import json
from pathlib import Path

import pytest
from starlette.testclient import TestClient

from mock_github import build_spec
from mock_github.tools import TOOLS, load_schemas
from mockmcp.app import build_asgi_app
from mockmcp.testing import call

REPO = {"owner": "zava-lab", "repo": "aurora-status"}


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

READ = ["get_me", "search_users", "search_repositories", "list_pull_requests", "search_pull_requests",
        "pull_request_read", "list_label", "get_label"]
WRITE = ["add_issue_comment", "update_issue_comment", "issue_write", "label_write", "pull_request_review_write",
         "add_comment_to_pending_review", "add_reply_to_pull_request_comment", "update_pull_request",
         "merge_pull_request", "request_copilot_review"]


def test_eight_read_and_ten_write_tools():
    names = [t["name"] for t in json.loads((Path(__file__).parents[1] / "seed_files" / "tool_schemas.json")
                                           .read_text(encoding="utf-8"))]
    assert names == READ + WRITE
    assert [t.name for t in TOOLS] == names


def test_annotations_follow_the_real_server(spec):
    schemas = load_schemas()
    for tool in spec.tools:
        assert tool.annotations.get("readOnlyHint") is (tool.name in READ)
        assert schemas[tool.name]["annotations"]["readOnlyHint"] is (tool.name in READ)
    assert next(t for t in spec.tools if t.name == "label_write").annotations["destructiveHint"] is True


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


# --- writes (kept per conversation) --------------------------------------------------------------------------------

PR = {**REPO, "pullNumber": 287}


@pytest.fixture()
def fresh():
    return build_spec()


def wok(spec, tool, args, conv="conv-a"):
    got = call(spec, tool, args, conversation_id=conv)
    assert got.ok, got.text
    try:
        return got.json
    except ValueError:
        return got.text


def werr(spec, tool, args, conv="conv-a"):
    got = call(spec, tool, args, conversation_id=conv)
    assert not got.ok, got.text
    return got.text


def read(spec, args, conv="conv-a"):
    got = call(spec, "pull_request_read", {**PR, **args}, conversation_id=conv)
    assert got.ok, got.text
    return got.json


def test_comment_is_kept_per_conversation(fresh):
    out = wok(fresh, "add_issue_comment", {**REPO, "issue_number": 287, "body": "Pilot date confirmed."})
    assert set(out) == {"id", "url"} and "/v/" in out["url"] and out["url"].endswith(f"#issuecomment-{out['id']}")
    assert isinstance(out["id"], str)
    assert [c["body"] for c in read(fresh, {"method": "get_comments"})] == ["Pilot date confirmed."]
    assert read(fresh, {"method": "get_comments"}, "conv-b") == []
    assert read(fresh, {"method": "get_comments"}, None) == []
    assert ok(fresh, "search_pull_requests", {"query": "commenter:emil-vanggaard"})["total_count"] == 0
    got = call(fresh, "search_pull_requests", {"query": "commenter:emil-vanggaard"}, conversation_id="conv-a")
    assert got.json["total_count"] == 1


def test_comment_reaction_and_update(fresh):
    out = wok(fresh, "add_issue_comment", {**REPO, "issue_number": 287, "body": "Looks good", "reaction": "rocket"})
    assert set(out) == {"comment", "reaction"}
    cid = int(out["comment"]["id"])
    wok(fresh, "add_issue_comment", {**REPO, "issue_number": 287, "comment_id": cid, "reaction": "+1"})
    wok(fresh, "update_issue_comment", {**REPO, "comment_id": cid, "body": "Looks good now"})
    got = read(fresh, {"method": "get_comments"})[0]
    assert got["body"] == "Looks good now" and got["reactions"]["+1"] == 1
    assert "404" in werr(fresh, "update_issue_comment", {**REPO, "comment_id": 1, "body": "x"})
    assert "404" in werr(fresh, "update_issue_comment", {**REPO, "comment_id": cid, "body": "x"}, conv="conv-b")


def test_issue_write_create_is_disabled_and_update_edits_pr(fresh):
    assert "Issues are disabled" in werr(fresh, "issue_write", {"method": "create", **REPO, "title": "x"})
    out = wok(fresh, "issue_write", {"method": "update", **REPO, "issue_number": 287, "labels": ["bug"]})
    assert out["url"].endswith("/pull/287")
    labels = read(fresh, {"method": "get"})["labels"]
    assert json.dumps(labels).count('"bug"') == 1 and len(labels) == 1
    assert len(ok(fresh, "pull_request_read", {"method": "get", **PR})["labels"]) > 1


def test_label_write_lifecycle(fresh):
    wok(fresh, "label_write", {"method": "create", **REPO, "name": "pilot", "color": "0e8a16"})
    got = call(fresh, "get_label", {**REPO, "name": "pilot"}, conversation_id="conv-a")
    assert got.ok and got.json["color"] == "0e8a16"
    assert not call(fresh, "get_label", {**REPO, "name": "pilot"}).ok
    wok(fresh, "label_write", {"method": "update", **REPO, "name": "pilot", "new_name": "pilot-ready"})
    wok(fresh, "label_write", {"method": "delete", **REPO, "name": "pilot-ready"})
    assert not call(fresh, "get_label", {**REPO, "name": "pilot-ready"}, conversation_id="conv-a").ok


def test_pending_review_flow_and_thread_resolution(fresh):
    wok(fresh, "pull_request_review_write", {"method": "create", **PR})
    wok(fresh, "add_comment_to_pending_review", {**PR, "path": "src/reconnect.ts", "body": "Guard the retry here.",
                                                 "subjectType": "LINE", "line": 42, "side": "RIGHT"})
    assert read(fresh, {"method": "get_reviews"})[-1]["state"] == "PENDING"
    assert all(r["state"] != "PENDING" for r in read(fresh, {"method": "get_reviews"}, None))
    wok(fresh, "pull_request_review_write", {"method": "submit_pending", **PR, "event": "COMMENT", "body": "Notes"})
    threads = read(fresh, {"method": "get_review_comments"})
    assert "Guard the retry here." in json.dumps(threads)
    items = threads["review_threads"] if isinstance(threads, dict) and "review_threads" in threads else threads
    thread_id = items[0]["id"]
    wok(fresh, "pull_request_review_write", {"method": "resolve_thread", **PR, "threadId": thread_id})
    assert '"is_resolved": true' in json.dumps(read(fresh, {"method": "get_review_comments"}))


def test_merge_is_blocked_by_branch_protection(fresh):
    assert "approving review is required" in werr(fresh, "merge_pull_request", PR)
    assert read(fresh, {"method": "get"})["merged"] is False


def test_update_pull_request_and_reviewers(fresh):
    wok(fresh, "update_pull_request", {**PR, "title": "Fix stale offline state (pilot)", "reviewers": ["kerry-allen"]})
    pr = read(fresh, {"method": "get"})
    assert pr["title"] == "Fix stale offline state (pilot)"
    assert "kerry-allen" in json.dumps(pr["requested_reviewers"])
    assert read(fresh, {"method": "get"}, None)["title"] == "Fix stale offline state after reconnect"
    assert "422" in werr(fresh, "update_pull_request", {**PR, "reviewers": ["nobody-here"]})


def test_request_copilot_review(fresh):
    wok(fresh, "request_copilot_review", PR)
    assert "copilot" in json.dumps(read(fresh, {"method": "get"})["requested_reviewers"]).lower()


def test_write_without_a_conversation_does_not_change_the_seed(fresh):
    call(fresh, "add_issue_comment", {**REPO, "issue_number": 287, "body": "orphan"})
    assert read(fresh, {"method": "get_comments"}, None) == []


def test_viewer_shows_only_the_conversation_copy(fresh):
    out = wok(fresh, "add_issue_comment", {**REPO, "issue_number": 287, "body": "Viewer check comment"})
    url = out["url"].split("#")[0]
    path = url[url.index("/v/"):]
    token = path.split("/")[2]
    web = TestClient(build_asgi_app(fresh), follow_redirects=False)
    r = web.get(path)
    assert r.status_code == 200 and "Viewer check comment" in r.text
    assert "This conversation&#x27;s changes" in r.text
    assert f'href="/v/{token}/zava-lab/aurora-status/pulls' in r.text and 'src="/avatars/' in r.text
    assert "Viewer check comment" not in web.get("/zava-lab/aurora-status/pull/287").text
    stale = web.get("/v/0123456789abcdef0123/zava-lab/aurora-status/pull/287")
    assert stale.status_code == 200 and "No saved changes" in stale.text
    assert web.get("/v/not-a-token/zava-lab").status_code == 404
    assert web.get(f"/v/{token}/zava-lab/aurora-status/issues/287").headers["location"] == \
        f"/v/{token}/zava-lab/aurora-status/pull/287"
