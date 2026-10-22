"""Tests for the mock Verdantis Hub site."""

import sys
from pathlib import Path

import pytest
from starlette.testclient import TestClient

from mock_hub import build_app
from mock_hub.app import load_pages

HUB_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HUB_DIR))


@pytest.fixture(scope="module")
def client():
    return TestClient(build_app())


def test_pages_match_tenant_generator():
    import export_pages

    assert load_pages() == export_pages.build(), "run: python verdantis_hub/export_pages.py"


def test_every_page_renders_with_badge(client):
    for p in load_pages():
        r = client.get(p["path"])
        assert r.status_code == 200 and p["title"].replace("&", "&amp;") in r.text and "MOCK INTRANET" in r.text


def test_playbook_rules(client):
    text = client.get("/retail/launch-playbook").text
    assert "3 days" in text and "Sam Patel" in text and "Launch Decision Log" in text


def test_links_are_site_relative(client):
    for p in load_pages():
        assert "hub.verdantis.com" not in p["html"] and "azurecontainerapps" not in p["html"]
    assert 'href="/retail/launch-playbook-2025"' in client.get("/retail/launch-playbook").text


def test_home_sections_and_404(client):
    home = client.get("/").text
    assert "Retail Partner Launch Playbook" in home and "2025, archived" not in home
    assert client.get("/retail").status_code == 200 and "launch-playbook-2025" in client.get("/retail").text
    assert client.get("/procurement/approved-vendors").status_code == 200
    assert client.get("/nope").status_code == 404


def test_sitemap_and_robots(client):
    assert client.get("/sitemap.xml").text.count("<url>") == 7
    assert "Sitemap:" in client.get("/robots.txt").text
    assert client.get("/healthz").json() == {"status": "ok", "pages": 7}
