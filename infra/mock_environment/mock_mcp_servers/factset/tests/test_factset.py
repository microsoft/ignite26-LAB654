from pathlib import Path

import pytest
from starlette.testclient import TestClient

from mock_factset import build_spec
from mockmcp.app import build_asgi_app
from mockmcp.testing import assert_deterministic, call, replay

FIXTURES = sorted((Path(__file__).parent / "fixtures").glob("*.json"))
PEERS = ["LITW-US", "ADTM-US", "RLCD-US"]


@pytest.fixture(scope="module")
def spec():
    return build_spec()


@pytest.mark.parametrize("fixture", FIXTURES, ids=lambda p: p.stem)
def test_replays_recorded_trace(spec, fixture):
    assert replay(spec, fixture) == []


@pytest.mark.parametrize("args", [
    {"periodicity": "QTR", "fiscalPeriodStart": "2025-01-01", "fiscalPeriodEnd": "2026-10-16"},
    {"periodicity": "ANN", "fiscalPeriodStart": "2019-01-01", "fiscalPeriodEnd": "2023-12-31"},
    {"periodicity": "LTM"},
])
def test_fundamentals_windows(spec, args):
    out = call(spec, "FactSet_Fundamentals", {"data_type": "fundamentals", "ids": ["VANA-US", "ADVW-US"], "metrics": ["FF_SALES", "FF_GROSS_MGN"], **args})
    assert out.ok, out.text


def test_metrics_search_finds_other_concepts(spec):
    out = call(spec, "FactSet_Metrics", {"text": ["free cash flow"], "data_products": ["fundamentals"], "limit": 3})
    assert out.ok, out.text


def test_entity_reference_for_other_names(spec):
    out = call(spec, "FactSet_EntityReference", {"data_type": "entity_reference", "ids": ["WDGV-US", "COHO-US", "LMNA-US"]})
    assert out.ok, out.text


def test_unknown_metric_or_id_is_handled(spec):
    out = call(spec, "FactSet_Fundamentals", {"data_type": "fundamentals", "ids": ["ZZZZ-US"], "metrics": ["FF_SALES"]})
    assert out.text  # an explicit error or an empty result, never a crash


@pytest.mark.parametrize("args", [
    {"data_type": "fundamentals", "metrics": ["FF_SALES"]},
    {"data_type": "fundamentals", "ids": PEERS, "metrics": ["FF_SALES"], "periodicity": "WEEKLY"},
])
def test_bad_arguments_are_rejected(spec, args):
    assert not call(spec, "FactSet_Fundamentals", args).ok


def test_answers_are_deterministic():
    assert_deterministic(build_spec, "FactSet_Fundamentals", {"data_type": "fundamentals", "ids": ["WDGV-US"], "metrics": ["FF_ROIC"], "periodicity": "QTR"})


def test_healthz(spec):
    with TestClient(build_asgi_app(spec)) as client:
        body = client.get("/healthz").json()
    assert body["status"] == "ok" and body["server"] == spec.name