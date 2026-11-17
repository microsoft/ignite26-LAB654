"""``discover`` and ``describe`` over the Headless-360 recipe catalogue recorded in SEVAL traces.

The real service ranks recipes with embeddings. The mock ranks the same 298 recorded cards by weighted token
overlap, and gives a small lift to recipes whose full ``describe`` result was recorded, so an agent that follows
the top hit can always open it.
"""

from __future__ import annotations

import json
import math
import re
from functools import lru_cache
from typing import Any

from .rest import SEED_DIR

_TOKEN = re.compile(r"[a-z0-9]+")
_STOP = {
    "a", "an", "and", "the", "of", "for", "to", "in", "on", "by", "with", "or", "its", "it", "is", "are", "be",
    "from", "as", "at", "that", "this", "any", "all", "use", "using", "salesforce", "record", "records", "find",
    "get", "show", "list", "including", "related", "then",
}


# The lab's questions are about CRM records; these recorded recipes answer them, so they surface for those queries.
_CRM_NOUNS = {"account", "opportunity", "contact", "task", "event", "case", "lead", "activity", "pipeline",
              "deal", "customer", "soql", "graphql", "note", "campaign", "quote", "product"}
_CRM_RECIPES = {"ui-uisdk-connect-impl-graphql-spec": 0.25, "record-discovery": 0.22,
                "activities-connect-api-sfdc.activities.connect.api-oas-67.0": 0.12}


def _tokens(text: str) -> list[str]:
    out = []
    for t in _TOKEN.findall((text or "").lower()):
        if t in _STOP or len(t) < 2:
            continue
        if len(t) > 4 and t.endswith("ies"):
            t = t[:-3] + "y"
        elif len(t) > 3 and t.endswith("s") and not t.endswith("ss"):
            t = t[:-1]
        out.append(t)
    return out


@lru_cache(maxsize=1)
def _catalog() -> dict[str, Any]:
    data = json.loads((SEED_DIR / "catalog.json").read_text(encoding="utf-8"))
    cards = data["cards"]
    docs = []
    for card in cards:
        body = " ".join([card.get("agent_description", ""), card.get("description", "")])
        name = " ".join(re.split(r"[-_.]", card["sor_id"]))
        docs.append((set(_tokens(name)), set(_tokens(body))))
    df: dict[str, int] = {}
    for name_toks, body_toks in docs:
        for t in name_toks | body_toks:
            df[t] = df.get(t, 0) + 1
    n = len(cards)
    idf = {t: math.log(1 + n / c) for t, c in df.items()}
    return {"cards": cards, "docs": docs, "idf": idf, "describe": data["describe"]}


def discover(query: str, limit: int = 10, domain: str | None = None, result_type: str | None = None) -> dict:
    cat = _catalog()
    q = list(dict.fromkeys(_tokens(query)))
    if domain:
        q += [t for t in _tokens(domain) if t not in q]
    total = sum(cat["idf"].get(t, 0.0) for t in q) or 1.0
    crm = bool(_CRM_NOUNS.intersection(q))
    scored = []
    for card, (name_toks, body_toks) in zip(cat["cards"], cat["docs"]):
        hit = sum(cat["idf"].get(t, 0.0) * (1.4 if t in name_toks else 1.0)
                  for t in q if t in name_toks or t in body_toks)
        lift = _CRM_RECIPES.get(card["sor_id"], 0.0) if crm else 0.0
        if not hit and not lift:
            continue
        score = min(0.95, 0.12 + 0.6 * hit / total)
        if card["sor_id"] in cat["describe"]:
            score = min(0.97, score * 1.15)
        score = min(0.97, score + lift)
        scored.append((round(score, 8), card))
    scored.sort(key=lambda x: (-x[0], x[1]["sor_id"]))
    filtered_out = 0
    if result_type == "sor":
        kept = [s for s in scored if s[1].get("step_count")]
        filtered_out = len(scored) - len(kept)
        scored = kept
    limit = max(1, min(50, int(limit or 10)))
    results = [{"sor_id": c["sor_id"], "score": s, **{k: v for k, v in c.items() if k != "sor_id"}}
               for s, c in scored[:limit]]
    return {"result_type": "discovery", "query": query, "results": results, "filtered_out_count": filtered_out}


def describe(item_id: str) -> dict:
    cat = _catalog()
    key = (item_id or "").strip()
    found = cat["describe"].get(key)
    if found is not None:
        return found
    for card in cat["cards"]:
        if card["sor_id"] == key:
            return {"result_type": "sor", "sor_id": key, "sor": {
                "id": key, "setup_nodes": card.get("setup_nodes", []), "complexity": card.get("complexity"),
                "description": card.get("description"), "agent_description": card.get("agent_description"),
                "steps": [], "delegates_to_sors": card.get("delegates_to_sors", []),
            }}
    return {"error": f"No operation or SOR found for id: {item_id}"}
