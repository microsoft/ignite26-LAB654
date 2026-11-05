from pathlib import Path

import pytest
from starlette.testclient import TestClient

from mock_moodys import build_spec
from mockmcp.app import build_asgi_app
from mockmcp.testing import assert_deterministic, call, replay

FIXTURES = sorted((Path(__file__).parent / "fixtures").glob("*.json"))


@pytest.fixture(scope="module")
def spec():
    return build_spec()


def _ref(spec, name):
    found = call(spec, "findEntity", {"data": name})
    assert found.ok, found.text
    hit = found.json["entities"][0]
    return {"entityId": hit["entityId"], "orgName": hit.get("orgName", name)}


@pytest.mark.parametrize("fixture", FIXTURES, ids=lambda p: p.stem)
def test_replays_recorded_trace(spec, fixture):
    assert replay(spec, fixture) == []


@pytest.mark.parametrize("name", ["A. Datum", "Relecloud", "VanArsdel", "Woodgrove Technology"])
def test_other_issuers_have_ratings_and_opinions(spec, name):
    ref = _ref(spec, name)
    ratings = call(spec, "getEntityRatings", {"entities": [ref], "years": 3})
    opinion = call(spec, "getCreditOpinion", {"entities": [ref], "sections": ["Summary", "Liquidity"]})
    assert ratings.ok and opinion.ok, ratings.text + opinion.text
    assert "Section Title: Liquidity" in opinion.text


def test_unknown_name_is_reported_not_found(spec):
    out = call(spec, "findEntity", {"data": ["Litware", "Apple Inc."]})
    assert out.ok and "Apple Inc." in out.text


def test_bad_entity_id_falls_back_to_org_name(spec):
    out = call(spec, "getEntityRatings", {"entities": [{"entityId": "not-an-id", "orgName": "VanArsdel, Ltd."}]})
    assert out.ok, out.text


@pytest.mark.parametrize("tool,args", [
    ("getCreditOpinion", {"entities": [{"entityId": "x"}], "sections": ["NotASection"]}),
    ("getEntityRatings", {"entities": []}),
    ("getEntityRatings", {"entities": [{"entityId": "x"}], "years": 0}),
])
def test_bad_arguments_are_rejected(spec, tool, args):
    assert not call(spec, tool, args).ok


def test_unknown_entity_is_an_error(spec):
    assert not call(spec, "getEntityRatings", {"entities": [{"entityId": "b3JnSWQ6MQ=="}]}).ok


def test_answers_are_deterministic(spec):
    ref = _ref(spec, "Adventure Works")
    assert_deterministic(build_spec, "getCreditOpinion", {"entities": [ref]})
    assert_deterministic(build_spec, "getEntityRatings", {"entities": [ref], "years": 10})


def test_healthz(spec):
    with TestClient(build_asgi_app(spec)) as client:
        assert client.get("/healthz").json()["server"] == spec.name