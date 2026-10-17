"""One entry point for servers: ``World.default()``.

Servers ask the world for companies, periods, financials, consensus and prices; they
never touch the generators directly. Results are cached per company, and every value
is a pure function of (company, metric, period, now), so all three servers agree.
"""

from __future__ import annotations

from datetime import datetime
from functools import cached_property, lru_cache

from .calendars import Period
from .estimates import Consensus, EstimatesModel
from .financials import FinancialModel
from .prices import PriceModel
from .universe import Company, Universe


class CompanyView:
    def __init__(self, company: Company) -> None:
        self.company = company

    @cached_property
    def financials(self) -> FinancialModel:
        return FinancialModel(self.company)

    @cached_property
    def estimates(self) -> EstimatesModel:
        return EstimatesModel(self.company, self.financials)

    @cached_property
    def prices(self) -> PriceModel:
        return PriceModel(self.company)

    @property
    def calendar(self):
        return self.company.calendar

    def latest(self, now: datetime, quarterly: bool) -> Period:
        return self.calendar.latest_reported(now, quarterly)

    def relative(self, index: int, now: datetime, quarterly: bool) -> Period:
        """IBES-style relative period: 0 = latest reported, 1 = FY1 / next quarter, -1 = prior."""
        return self.latest(now, quarterly).shift(index)

    def is_reported(self, period: Period, now: datetime) -> bool:
        return self.calendar.is_reported(period, now)

    def actual(self, metric: str, period: Period, now: datetime) -> float | None:
        if not self.is_reported(period, now):
            return None
        return self.financials.value(metric, period)

    def consensus(self, metric: str, period: Period, now: datetime, vendor: str = "lseg") -> Consensus | None:
        latest = self.latest(now, not period.is_annual)
        return self.estimates.consensus(metric, period, latest, vendor)

    def market_cap(self, now: datetime) -> float | None:
        """USD millions, latest close x latest diluted shares."""
        bar = self.prices.latest(now)
        if not bar:
            return None
        latest = self.latest(now, quarterly=True)
        shares = self.financials.value("shares", latest) or self.financials.annual("shares", latest.year)
        return bar.close * shares


class World:
    def __init__(self, universe: Universe) -> None:
        self.universe = universe
        self._views: dict[str, CompanyView] = {}

    @classmethod
    def default(cls) -> "World":
        return _default_world()

    def resolve(self, identifier) -> CompanyView | None:
        company = self.universe.resolve(identifier)
        if company is None:
            return None
        view = self._views.get(company.ticker)
        if view is None:
            view = self._views[company.ticker] = CompanyView(company)
        return view

    def search(self, text: str) -> list[CompanyView]:
        return [self.resolve(c.ticker) for c in self.universe.search_names(text)]

    def all(self) -> list[CompanyView]:
        return [self.resolve(c.ticker) for c in self.universe.companies]


@lru_cache(maxsize=1)
def _default_world() -> World:
    return World(Universe.load())
