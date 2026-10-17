"""Pieces every Moody's tool shares: data access, entity ids, entity references and errors."""

from __future__ import annotations

import base64
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from mockfin import World
from mockfin.universe import Company
from mockmcp import InvalidParams, JsonStore, NotEntitled, ToolError, UpstreamError, dumps

SEED_DIR = Path(__file__).resolve().parent.parent / "seed_files"
SOURCE = "Moody's Ratings"
COUNTRY = "UNITED STATES"
SECTOR = "Corporates, Semiconductors"
RATING_CLASS = "Senior Unsecured - Dom Curr"

ENTITY_REF_SCHEMA = {
    "type": "object",
    "properties": {
        "entityId": {"type": "string", "description": "entityId returned by findEntity."},
        "orgName": {"type": "string", "description": "Organisation name returned by findEntity."},
        "isUnrated": {"type": "boolean", "description": "isUnrated flag returned by findEntity."},
    },
    "required": ["entityId"],
}
ENTITIES_SCHEMA = {
    "type": "array",
    "minItems": 1,
    "maxItems": 10,
    "items": ENTITY_REF_SCHEMA,
    "description": "Entities exactly as returned by findEntity (pass entityId, orgName and isUnrated).",
}


def entity_id(company: Company) -> str:
    m = company.moodys
    raw = f"orgId:{m['org_id']}#orbisId:{m['orbis_id']}#bvdId:{m['bvd_id']}#dealId:null#trancheId:null"
    return base64.b64encode(raw.encode()).decode()


def decode_entity_id(value: str) -> dict[str, str] | None:
    """``orgId:..#orbisId:..`` -> ``{"orgId": ...}``; None when it isn't a Moody's entity id."""
    try:
        padded = value + "=" * (-len(value) % 4)
        text = base64.b64decode(padded, validate=True).decode()
    except (ValueError, UnicodeDecodeError):
        return None
    parts = dict(p.split(":", 1) for p in text.split("#") if ":" in p)
    return parts if "orgId" in parts else None


def url_slug(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "-", name).strip("-")


@dataclass
class MoodysData:
    """Read-only handle on the shared finance world plus Moody's-specific seed overlays."""

    world: World
    store: JsonStore

    @classmethod
    def default(cls) -> "MoodysData":
        return cls(World.default(), JsonStore(SEED_DIR))

    @property
    def rated(self) -> list[Company]:
        return [v.company for v in self.world.all() if v.company.moodys]

    def by_org(self, org_id: Any) -> Company | None:
        return next((c for c in self.rated if str(c.moodys["org_id"]) == str(org_id)), None)

    def recorded_rating(self, company: Company) -> dict | None:
        return self.store.view("ratings")["ratings"].get(str(company.moodys["org_id"]))

    def recorded_opinion(self, company: Company) -> dict | None:
        return self.store.view("opinions")["opinions"].get(str(company.moodys["org_id"]))

    def find(self, text: str) -> list[Company]:
        """Exact identifier/name match first, then name-word overlap; only Moody's-rated companies."""
        hits = self.world.universe.search_names(text)
        return [c for c in hits if c.moodys]

    def resolve_refs(self, refs: list[dict]) -> list[tuple[Company, str]]:
        """Entity references -> companies. Unknown ids fail the whole call, like the live API's 404."""
        resolved, unknown = [], []
        for ref in refs:
            parts = decode_entity_id(ref["entityId"])
            company = self.by_org(parts["orgId"]) if parts else None
            if company is None and ref.get("orgName"):
                found = self.find(ref["orgName"])
                company = found[0] if found else None
            if company is None:
                unknown.append(ref["entityId"])
            else:
                resolved.append((company, ref["entityId"] if parts else entity_id(company)))
        if unknown:
            raise UpstreamError(
                "Entity not found: " + ", ".join(unknown) + ". Call findEntity first and pass its entityId.", 404
            )
        return resolved


def render_error(error: ToolError, tool: str) -> str:
    if isinstance(error, InvalidParams):
        body = {"error": {"status": 400, "message": "Invalid request", "details": error.issues}}
    elif isinstance(error, UpstreamError):
        body = {"error": {"status": error.status, "message": error.message}}
    elif isinstance(error, NotEntitled):
        body = {"error": {"status": 403, "message": error.message}}
    else:
        body = {"error": {"status": 500, "message": error.message}}
    return dumps(body)
