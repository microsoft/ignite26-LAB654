"""The four Moody's tools. Schemas mirror the calls observed in the live trace."""

from __future__ import annotations

from datetime import date

from mockmcp import InvalidParams, Tool
from mockmcp.tool import CallContext

from .common import COUNTRY, ENTITIES_SCHEMA, SECTOR, SOURCE, MoodysData, entity_id, url_slug
from .opinions import DEFAULT_SECTIONS, SECTIONS, OpinionWriter
from .ratings import RatingBook

MAX_NAMES = 25


def _midnight(day: date) -> str:
    return f"{day.isoformat()}T00:00:00.000Z"


class FindEntity(Tool):
    name = "findEntity"
    title = "Find Moody's entity"
    description = (
        "Look up Moody's-rated entities by organisation name, ticker or identifier. Returns the entityId needed by "
        "getEntityRatings, getCreditOpinion and getEntityBeneficiaryOwners, plus the long-term rating. Names that "
        "match nothing are listed in notFound."
    )
    input_schema = {
        "type": "object",
        "properties": {
            "data": {
                "description": "One name or identifier, or a list of them (max 25).",
                "oneOf": [
                    {"type": "string", "minLength": 1},
                    {"type": "array", "items": {"type": "string", "minLength": 1}, "minItems": 1, "maxItems": MAX_NAMES},
                ],
            }
        },
        "required": ["data"],
    }

    def __init__(self, data: MoodysData) -> None:
        self.data = data

    def run(self, args: dict, ctx: CallContext) -> dict:
        names = [args["data"]] if isinstance(args["data"], str) else args["data"]
        entities, not_found, seen = [], [], set()
        for text in names:
            hits = self.data.find(text)[:3]
            if not hits:
                not_found.append(text)
            for company in hits:
                if company.ticker in seen:
                    continue
                seen.add(company.ticker)
                entities.append(
                    {
                        "entityId": entity_id(company),
                        "orgName": company.name,
                        "isUnrated": False,
                        "ticker": company.ticker,
                        "longTermRating": company.moodys["rating"],
                        "country": COUNTRY,
                        "sector": SECTOR,
                    }
                )
        return {"entities": entities, "notFound": not_found}


class GetEntityRatings(Tool):
    name = "getEntityRatings"
    title = "Get Moody's rating history"
    description = (
        "Current Moody's rating, outlook and rating action history for one or more entities from findEntity. "
        "`years` limits how far back the history goes (default 5)."
    )
    input_schema = {
        "type": "object",
        "properties": {
            "entities": ENTITIES_SCHEMA,
            "years": {"type": "integer", "minimum": 1, "maximum": 30, "default": 5},
        },
        "required": ["entities"],
    }

    def __init__(self, data: MoodysData) -> None:
        self.data = data
        self.book = RatingBook(data)

    def run(self, args: dict, ctx: CallContext) -> list[dict]:
        today = ctx.clock.today
        years = args.get("years", 5)
        try:
            cutoff = today.replace(year=today.year - years)
        except ValueError:  # 29 February
            cutoff = today.replace(year=today.year - years, day=28)
        out = []
        for company, eid in self.data.resolve_refs(args["entities"]):
            history = self.book.history(company, today)
            org = company.moodys["org_id"]
            out.append(
                {
                    "text": history.render(cutoff),
                    "id": f"RTNG_{org}",
                    "title": f"{company.name} ({org}) - Rating History({history.rating_class})",
                    "source": SOURCE,
                    "date": _midnight(today),
                    "url": f"https://www.moodys.com/credit-ratings/{url_slug(company.name)}-credit-rating-{org}/summary",
                    "entityId": eid,
                    "metadata": {"type": "Fundamental"},
                }
            )
        return out


class GetCreditOpinion(Tool):
    name = "getCreditOpinion"
    title = "Get Moody's credit opinion"
    description = (
        "The latest Moody's Credit Opinion for entities from findEntity, limited to the requested sections. "
        f"Sections: {', '.join(SECTIONS)}. Default: {', '.join(DEFAULT_SECTIONS)}."
    )
    input_schema = {
        "type": "object",
        "properties": {
            "entities": ENTITIES_SCHEMA,
            "sections": {"type": "array", "items": {"type": "string"}, "minItems": 1, "uniqueItems": True},
        },
        "required": ["entities"],
    }

    def __init__(self, data: MoodysData) -> None:
        self.data = data
        self.book = RatingBook(data)
        self.writer = OpinionWriter(data)

    def run(self, args: dict, ctx: CallContext) -> list[dict]:
        keys = args.get("sections") or list(DEFAULT_SECTIONS)
        bad = [k for k in keys if k not in SECTIONS]
        if bad:
            raise InvalidParams([f"sections: unknown section '{k}'. Allowed: {', '.join(SECTIONS)}" for k in bad])
        out = []
        for company, eid in self.data.resolve_refs(args["entities"]):
            view = self.data.world.resolve(company.ticker)
            history = self.book.history(company, ctx.clock.today)
            op = self.writer.opinion(view, history, keys, ctx.clock.now)
            out.append(
                {
                    "text": op.render(),
                    "id": op.doc_id,
                    "title": op.title,
                    "source": SOURCE,
                    "date": _midnight(op.day),
                    "url": f"https://www.moodys.com/research/doc--{op.doc_id}",
                    "entityId": eid,
                }
            )
        return out


class GetEntityBeneficiaryOwners(Tool):
    name = "getEntityBeneficiaryOwners"
    title = "Get beneficial owners"
    description = "Ultimate beneficial owners (25% threshold) for entities from findEntity."
    input_schema = {"type": "object", "properties": {"entities": ENTITIES_SCHEMA}, "required": ["entities"]}

    def __init__(self, data: MoodysData) -> None:
        self.data = data

    def run(self, args: dict, ctx: CallContext) -> list[dict]:
        out = []
        for company, eid in self.data.resolve_refs(args["entities"]):
            m = company.moodys
            out.append(
                {
                    "text": (
                        f"Beneficial Owners - {company.name} (BvD ID {m['bvd_id']})\n\n"
                        "No individual or entity holds 25% or more of shares or voting rights. The company is publicly "
                        f"listed ({company.exchange}: {company.ticker}) with widely dispersed ownership; it is its own "
                        "global ultimate owner."
                    ),
                    "id": f"UBO_{m['bvd_id']}",
                    "title": f"{company.name} - Beneficial Owners",
                    "source": "Moody's Orbis",
                    "date": _midnight(ctx.clock.today),
                    "url": f"https://www.moodys.com/credit-ratings/{url_slug(company.name)}-credit-rating-{m['org_id']}/summary",
                    "entityId": eid,
                    "metadata": {"type": "Ownership"},
                }
            )
        return out
