import json
from pathlib import Path

import pytest
from starlette.testclient import TestClient

from mock_imanage import build_spec
from mock_imanage.store import StateStore
from mockmcp.app import build_asgi_app
from mockmcp.testing import assert_deterministic, call

BASE = "https://imanage.example.com"
FIXTURES = sorted((Path(__file__).parent / "fixtures").glob("*.json"))
PLAYBOOK = "DEV!252567.1"
WORKSPACE, PLAYBOOKS, DRAFTS = "Dev!1870", "Dev!1872", "Dev!1874"


@pytest.fixture(scope="module")
def spec():
    return build_spec(public_base_url=BASE)


@pytest.fixture()
def web():
    store = StateStore.from_file()
    spec = build_spec(store=store, public_base_url=BASE)
    return spec, store, TestClient(build_asgi_app(spec))


def _upload(spec, conv, folder=DRAFTS, name="Redline memo", **extra):
    return call(spec, "upload_document", {"folder_id": folder, "name": name, "content": "# Memo\nText", **extra}, conv)


def _local(url: str) -> str:
    return url.replace(BASE, "")


# --- shape fidelity against the recorded live trace -------------------------------------------------------------

def _same_shape(got: dict, live: dict, where: str) -> list[str]:
    problems = [f"{where}: missing key {k!r}" for k in live if k not in got]
    for key, value in live.items():
        if key in got and type(got[key]) is not type(value):
            problems.append(f"{where}.{key}: {type(got[key]).__name__} vs live {type(value).__name__}")
    order = [k for k in got if k in live]
    if order != [k for k in live if k in got]:
        problems.append(f"{where}: key order {order} differs from live {list(live)}")
    return problems


@pytest.mark.parametrize("fixture", FIXTURES, ids=lambda p: p.stem)
def test_matches_live_trace_shape(spec, fixture):
    rec = json.loads(fixture.read_text(encoding="utf-8"))
    got = call(spec, rec["tool"], rec["args"])
    assert got.ok, got.text
    if rec["items"] or "items" in got.json:
        summary = {k: v for k, v in got.json.items() if k != "items"}
        problems = _same_shape(summary, rec["summary"], "summary")
        assert len(got.json["items"]) == len(rec["items"]), got.text[:500]
        for i, (mine, live) in enumerate(zip(got.json["items"], rec["items"])):
            problems += _same_shape(mine, live, f"items[{i}]")
    else:
        problems = _same_shape(got.json, rec["summary"], "result")
    assert problems == []


def test_profile_keys_match_live_exactly(spec):
    rec = json.loads((Path(__file__).parent / "fixtures" / "07_get_document_profile.json").read_text(encoding="utf-8"))
    got = call(spec, "get_document_profile", rec["args"])
    assert list(got.json) == list(rec["summary"])


def test_real_host_never_appears(spec):
    for tool, args in [("search", {"query": "Playbook"}), ("get_document_profile", {"documentId": PLAYBOOK}),
                       ("search_workspaces", {"searchParams": {"name": "Trey"}})]:
        assert "cloudimanage.com" not in call(spec, tool, args).text


# --- the lab flow ----------------------------------------------------------------------------------------------

def test_lab_flow_finds_and_reads_playbook(spec):
    ws = call(spec, "search_workspaces", {"searchParams": {"name": "Trey Research"}})
    assert ws.json["topMatchingId"] == WORKSPACE
    children = call(spec, "get_container_children", {"container_id": WORKSPACE, "container_type": "workspace"})
    assert [c["name"] for c in children.json["items"]] == ["Playbooks", "Drafts"]
    docs = call(spec, "get_container_children", {"container_id": PLAYBOOKS, "container_type": "folder"})
    assert PLAYBOOK in docs.text
    hit = call(spec, "search", {"query": "AI Procurement Playbook"})
    assert [h["name"] for h in hit.json["items"]] == ["Zava AI Procurement Playbook v2.1"]
    full = call(spec, "fetch", {"id": PLAYBOOK})
    assert full.ok and "hard stop" in full.json["text"].lower()
    assert full.json["metadata"]["has_more"] is False


def test_search_folders_supports_wildcards(spec):
    out = call(spec, "search_folders", {"container_id": WORKSPACE, "name": "*Draft*"})
    assert [f["id"] for f in out.json["items"]] == [DRAFTS]


def test_absent_term_returns_no_hits(spec):
    out = call(spec, "search", {"query": "Contoso playbook"})
    assert out.ok and out.json["items"] == []


def test_current_user(spec):
    assert "EMIL" in call(spec, "get_user_information", {}).text


# --- writes ----------------------------------------------------------------------------------------------------

def test_upload_is_visible_only_to_its_conversation(spec):
    out = _upload(spec, "conv-up", name="Redline memo.pdf", comment="first pass")
    assert out.ok, out.text
    new_id = out.json["id"]
    assert out.json["name"] == "Redline memo" and out.json["type_description"] == "ACROBAT"
    assert out.json["create_date"] == "2026-10-26T15:00:00.000Z"
    assert call(spec, "get_document_profile", {"documentId": new_id}, "conv-up").ok
    assert not call(spec, "get_document_profile", {"documentId": new_id}, "conv-other").ok
    assert new_id not in call(spec, "get_container_children",
                              {"container_id": DRAFTS, "container_type": "folder"}, "conv-other").text


def test_docx_upload_and_fetch_back(spec):
    out = _upload(spec, "conv-docx", name="Fallback clauses", format="docx")
    assert out.json["type_description"] == "WORD 2007"
    assert "# Memo" in call(spec, "fetch", {"id": out.json["id"]}, "conv-docx").json["text"]


def test_writes_without_conversation_are_not_kept(spec):
    out = _upload(spec, None, name="Ephemeral")
    assert out.ok
    assert not call(spec, "get_document_profile", {"documentId": out.json["id"]}).ok


@pytest.mark.parametrize("folder", [PLAYBOOKS, WORKSPACE])
def test_read_only_containers_reject_uploads(spec, folder):
    out = _upload(spec, "conv-ro", folder=folder)
    assert not out.ok and "Drafts" in out.text


def test_unknown_folder_is_not_found(spec):
    assert not _upload(spec, "conv-nf", folder="Dev!9999").ok


def test_create_folder_and_duplicate(spec):
    first = call(spec, "create_folder", {"parent_id": DRAFTS, "name": "Benchmarks"}, "conv-f")
    assert first.ok and first.json["id"] == "Dev!1875"
    assert not call(spec, "create_folder", {"parent_id": DRAFTS, "name": "Benchmarks"}, "conv-f").ok
    assert call(spec, "create_folder", {"parent_id": DRAFTS, "name": "Benchmarks"}, "conv-g").ok
    assert not call(spec, "create_folder", {"parent_id": PLAYBOOKS, "name": "X"}, "conv-f").ok


# --- argument checking and determinism -------------------------------------------------------------------------

@pytest.mark.parametrize("tool,args", [
    ("get_document_profile", {"documentId": "not-an-id"}),
    ("fetch", {}),
    ("get_container_children", {"container_id": WORKSPACE, "container_type": "drawer"}),
    ("upload_document", {"folder_id": DRAFTS, "name": "x", "content": "y", "format": "txt"}),
    ("upload_document", {"folder_id": DRAFTS, "name": "x", "content": ""}),
    ("create_folder", {"parent_id": DRAFTS}),
])
def test_bad_arguments_are_rejected(spec, tool, args):
    assert not call(spec, tool, args).ok


def test_unknown_document_is_an_error(spec):
    assert not call(spec, "get_document_profile", {"documentId": "DEV!1.1"}).ok


def test_tool_list(spec):
    names = {t.name for t in spec.tools}
    assert {"search", "fetch", "upload_document", "create_folder"} <= names and len(names) == 16


@pytest.mark.parametrize("tool,args", [("search", {"query": "Exhibit"}), ("fetch", {"id": PLAYBOOK}),
                                       ("get_recent_documents", {})])
def test_deterministic(tool, args):
    assert_deterministic(lambda: build_spec(public_base_url=BASE), tool, args)


# --- viewer ----------------------------------------------------------------------------------------------------

def test_health_and_home(web):
    _, _, client = web
    assert client.get("/healthz").status_code == 200
    home = client.get("/", follow_redirects=False)
    assert home.status_code == 302 and home.headers["location"].endswith(f"/work/link/w/{WORKSPACE}")


def test_viewer_pages_render(web):
    _, _, client = web
    for path in [f"/work/link/w/{WORKSPACE}", f"/work/link/f/{PLAYBOOKS}", f"/work/link/d/{PLAYBOOK}"]:
        page = client.get(path)
        assert page.status_code == 200, path
        assert "MOCK IMANAGE" in page.text and page.headers["cache-control"] == "no-store"
    assert "Zava AI Procurement Playbook" in client.get(f"/work/link/d/{PLAYBOOK}").text


def test_links_carry_view_token_and_scope_changes(web):
    spec, store, client = web
    out = _upload(spec, "conv-a", name="Scoped memo")
    url = out.json["document_url"]
    token = store.view_token("conv-a")
    assert url.startswith(f"{BASE}/v/{token}/work/link/d/")
    assert "Scoped memo" in client.get(_local(url)).text
    assert client.get(_local(url).replace(f"/v/{token}", "")).status_code == 404
    other = client.get(_local(url).replace(token, "0" * 20))
    assert other.status_code == 404 and "No saved changes were found" in other.text
    assert "No saved changes" not in client.get(_local(url)).text


def test_viewer_rejects_bad_token_and_unknown_items(web):
    _, _, client = web
    assert client.get(f"/v/not-a-token/work/link/w/{WORKSPACE}").status_code == 404
    assert client.get("/work/link/d/DEV!1.1").status_code == 404
    assert client.get("/work/link/f/Dev!9999").status_code == 404
