"""The company universe and identifier resolution shared by all finance mocks."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any

from .calendars import FiscalCalendar, FiscalRule

DATA_DIR = Path(__file__).parent / "data"


@dataclass(frozen=True)
class Company:
    ticker: str
    name: str
    short_name: str
    exchange: str
    ric: str
    factset_id: str
    fsym_security_id: str
    fsym_entity_id: str
    isin: str
    cusip: str
    sedol: str
    org_permid: int
    ibes_estpermid: int
    qa_code: int
    aliases: tuple[str, ...]
    synthetic: tuple[str, ...]
    fiscal: FiscalRule
    coverage: dict
    model: dict
    price: dict
    financials: dict
    rbics: dict
    moodys: dict
    calendar: FiscalCalendar = field(compare=False, repr=False)

    @classmethod
    def from_dict(cls, raw: dict) -> "Company":
        rule = FiscalRule.from_dict(raw["fiscal"])
        financials = raw.get("financials", {})
        return cls(
            ticker=raw["ticker"],
            name=raw["name"],
            short_name=raw.get("short_name", raw["name"]),
            exchange=raw["exchange"],
            ric=raw["ric"],
            factset_id=raw["factset_id"],
            fsym_security_id=raw["fsym_security_id"],
            fsym_entity_id=raw["fsym_entity_id"],
            isin=raw["isin"],
            cusip=raw["cusip"],
            sedol=raw["sedol"],
            org_permid=raw["org_permid"],
            ibes_estpermid=raw["ibes_estpermid"],
            qa_code=raw["qa_code"],
            aliases=tuple(raw.get("aliases", [])),
            synthetic=tuple(raw.get("synthetic", [])),
            fiscal=rule,
            coverage=raw.get("coverage", {}),
            model=raw.get("model", {}),
            price=raw.get("price", {}),
            financials=financials,
            rbics=raw.get("rbics", {}),
            moodys=raw.get("moodys", {}),
            calendar=FiscalCalendar(raw["ticker"], rule, financials.get("report_dates")),
        )

    def identifiers(self) -> dict[str, Any]:
        return {
            "Ticker": self.ticker,
            "RIC": self.ric,
            "FactSetId": self.factset_id,
            "FsymSecurityId": self.fsym_security_id,
            "FsymEntityId": self.fsym_entity_id,
            "ISIN": self.isin,
            "CUSIP": self.cusip,
            "SEDOL": self.sedol,
            "OrganizationPermID": self.org_permid,
        }


def _norm(text: str) -> str:
    text = re.sub(r"[^a-z0-9 ]", " ", str(text).lower())
    text = re.sub(r"\b(the|inc|incorporated|corp|corporation|co|ltd|plc|holdings)\b", " ", text)
    return re.sub(r"\s+", " ", text).strip()


class Universe:
    """Resolves tickers, RICs, FactSet/fsym ids, ISIN, CUSIP, SEDOL, PermIDs and names."""

    def __init__(self, companies: list[Company]) -> None:
        self.companies = companies
        self._index: dict[str, Company] = {}
        for company in companies:
            keys = [
                company.ticker,
                company.ric,
                company.ric.split(".")[0],
                company.factset_id,
                f"{company.ticker}-{company.exchange}",
                company.fsym_security_id,
                company.fsym_entity_id,
                company.isin,
                company.cusip,
                company.sedol,
                str(company.org_permid),
                str(company.ibes_estpermid),
                str(company.qa_code),
            ]
            for key in keys:
                self._index.setdefault(str(key).upper(), company)
            for name in (company.name, company.short_name, *company.aliases):
                self._index.setdefault("NAME:" + _norm(name), company)

    @classmethod
    def load(cls, path: Path | None = None) -> "Universe":
        return _load_universe(str(path or DATA_DIR / "companies.json"))

    def resolve(self, identifier: Any) -> Company | None:
        if identifier is None:
            return None
        raw = str(identifier).strip()
        hit = self._index.get(raw.upper())
        if hit:
            return hit
        # Exchange suffixes: LITW.OQ, LITW US, LITW-US-EQ ...
        base = re.split(r"[.\s:-]", raw.upper())[0]
        hit = self._index.get(base)
        if hit and base:
            return hit
        return self._index.get("NAME:" + _norm(raw))

    def search_names(self, text: str) -> list[Company]:
        """Fuzzy name search for free-text lookups (e.g. Moody's findEntity)."""
        exact = self.resolve(text)
        if exact:
            return [exact]
        words = set(_norm(text).split())
        if not words:
            return []
        scored = []
        for company in self.companies:
            vocab = set(_norm(" ".join((company.name, company.short_name, *company.aliases))).split())
            overlap = len(words & vocab)
            if overlap:
                scored.append((overlap, company.ticker, company))
        scored.sort(key=lambda item: (-item[0], item[1]))
        return [c for _, _, c in scored]


@lru_cache(maxsize=None)
def _load_universe(path: str) -> Universe:
    with open(path, encoding="utf-8") as handle:
        raw = json.load(handle)
    return Universe([Company.from_dict(c) for c in raw["companies"]])
