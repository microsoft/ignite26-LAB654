"""Analyst consensus generated from the financial model.

* Unreported period: the mean tracks the model's "truth" with a small seeded bias, or
  equals ``companies.json -> financials.consensus`` when anchored.
* Reported period: the mean is the pre-announcement consensus, i.e. the actual divided
  by a seeded surprise (mostly beats, as is typical for large-cap tech).
* Dispersion and analyst counts depend on the horizon (FY1 tighter than FY2), the
  measure (EPS is covered by more analysts than net debt), and the company's
  ``coverage`` block.
* Different vendors (LSEG IBES vs FactSet) differ slightly but consistently, the same
  way real vendor consensus differs because of contributor sets.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass

from mockmcp import Seeded

from .calendars import Period
from .financials import FinancialModel
from .universe import Company

COVERAGE_SHARE = {
    "eps": 1.0, "revenue": 0.96, "ebitda": 0.62, "net_income": 0.58, "oper_income": 0.5,
    "dps": 0.48, "net_debt": 0.34, "eps_rep": 0.45, "gross_margin": 0.4, "capex": 0.36,
    "cfo": 0.3, "fcf": 0.3, "roic": 0.18, "roe": 0.25,
}
DISPERSION = {"net_debt": 3.0, "dps": 1.4, "fcf": 1.8, "cfo": 1.5, "capex": 1.4, "net_income": 1.1}


@dataclass(frozen=True)
class Consensus:
    mean: float
    median: float
    high: float
    low: float
    std: float
    count: int
    up: int
    down: int

    def as_dict(self) -> dict:
        return asdict(self)


class EstimatesModel:
    def __init__(self, company: Company, financials: FinancialModel) -> None:
        self.company = company
        self.financials = financials
        self.anchors = company.financials.get("consensus", {})
        self.analysts = int(company.coverage.get("analysts", 25))
        self.dispersion = float(company.coverage.get("dispersion", 1.0))

    def horizon(self, period: Period, latest: Period) -> int:
        """0 = the latest reported period, 1 = FY1/next quarter, ..."""
        return period.ordinal() - latest.ordinal()

    def consensus(self, metric: str, period: Period, latest: Period, vendor: str = "lseg") -> Consensus | None:
        h = self.horizon(period, latest)
        if period.is_annual and h > 3 or not period.is_annual and h > 8:
            return None
        truth = self.financials.value(metric, period)
        if truth is None:
            return None
        seed = Seeded("estimates", self.company.ticker, metric, period.key)
        anchored = self.anchors.get(period.key, {}).get(metric)
        if anchored is not None:
            mean = float(anchored)
        elif h <= 0:
            surprise = seed.uniform(-0.04, 0.09, "surprise")
            mean = truth / (1 + surprise) if truth > 0 else truth - abs(truth) * surprise
        else:
            mean = truth * (1 + seed.gauss(0.0, 0.012, "bias"))
        count = self._count(metric, period, h, seed)
        cv = self._cv(metric, period, h)
        if vendor != "lseg":
            mean *= 1 + seed.gauss(0.0, 0.006, "vendor", vendor)
            count = max(1, count + seed.integer(-3, 2, "vendor-count", vendor))
        std = 0.0 if count == 1 else abs(mean) * cv * seed.uniform(0.85, 1.15, "std", vendor)
        if count == 1:
            return Consensus(mean, mean, mean, mean, 0.0, 1, 0, 0)
        median = mean + std * seed.gauss(0.0, 0.18, "median", vendor)
        high = mean + std * seed.uniform(1.8, 2.6, "high", vendor)
        low = mean - std * seed.uniform(1.8, 2.6, "low", vendor)
        up = seed.integer(0, max(1, count // 3), "up", vendor) if h >= 0 else 0
        down = seed.integer(0, max(1, count // 6), "down", vendor) if h >= 0 else 0
        return Consensus(mean, median, high, low, std, count, up, down)

    def _count(self, metric: str, period: Period, h: int, seed: Seeded) -> int:
        share = COVERAGE_SHARE.get(metric, 0.3)
        if period.is_annual:
            horizon = {0: 1.0, 1: 1.0, 2: 0.88, 3: 0.42}.get(h, 0.9)
        else:
            horizon = 0.92 if h <= 1 else max(0.25, 0.92 - 0.12 * (h - 1))
        base = self.analysts * share * horizon * seed.uniform(0.92, 1.06, "count")
        return max(1, round(base))

    def _cv(self, metric: str, period: Period, h: int) -> float:
        if period.is_annual:
            cv = {0: 0.015, 1: 0.035, 2: 0.08, 3: 0.13}.get(h, 0.02)
        else:
            cv = 0.015 if h <= 0 else 0.02 + 0.008 * (h - 1)
        return cv * self.dispersion * DISPERSION.get(metric, 1.0)
