"""A small, consistent financial model per company.

Seven primitive series drive everything else:

=============  ========  ==========================================================
primitive      kind      notes
=============  ========  ==========================================================
revenue        level     USD millions; grows by the company's ``rev_growth`` range
shares         level     diluted shares, millions
dps            level     dividends per share
gross_margin   ratio     %, FactSet/Worldscope basis (excludes depreciation)
oper_margin    ratio     %
net_margin     ratio     %, normalised ("street") net income / revenue
roic           ratio     %
=============  ========  ==========================================================

Derived metrics (EBITDA, EPS, net debt, invested capital, ...) are formulas over the
primitives plus the static ratios in ``companies.json -> model``. Any derived metric
can also be anchored for a given year, in which case the anchor wins.

Levels use ``AnchoredSeries`` (geometric between anchors, seeded growth beyond them).
Ratios interpolate linearly and walk beyond the anchors with a seeded, mean-reverting
step, so margins drift plausibly instead of exploding.
"""

from __future__ import annotations

from functools import lru_cache

from mockmcp import AnchoredSeries, Seeded, bounded, split_weights

from .calendars import Period
from .universe import Company

LEVELS = {"revenue": None, "shares": (-0.015, 0.01), "dps": (0.0, 0.08)}
RATIOS = {"gross_margin": 1.2, "oper_margin": 1.8, "net_margin": 1.5, "roic": 2.5}
FLOW_METRICS = {
    "revenue", "cogs", "gross_income", "dda", "oper_income", "ebitda", "net_income",
    "net_income_rep", "capex", "cfo", "fcf", "eps", "eps_rep", "dps",
}

METRICS = (
    "revenue", "cogs", "gross_income", "gross_margin", "dda", "oper_income", "oper_margin",
    "ebitda", "ebitda_margin", "net_income", "net_margin", "net_income_rep", "net_margin_rep",
    "eps", "eps_rep", "dps", "shares", "cash", "total_debt", "net_debt", "invested_capital",
    "equity", "total_assets", "roic", "roe", "roa", "capex", "cfo", "fcf", "bvps",
)


class RatioSeries:
    def __init__(self, anchors: dict[int, float], seed: Seeded, step_sd: float) -> None:
        self.anchors = dict(sorted(anchors.items()))
        self.keys = list(self.anchors)
        self.seed = seed
        self.step_sd = step_sd
        self.mean = sum(self.anchors.values()) / len(self.anchors)

    def value(self, year: int) -> float:
        if year in self.anchors:
            return self.anchors[year]
        if self.keys[0] < year < self.keys[-1]:
            lo = max(k for k in self.keys if k < year)
            hi = min(k for k in self.keys if k > year)
            t = (year - lo) / (hi - lo)
            return self.anchors[lo] + t * (self.anchors[hi] - self.anchors[lo])
        direction = 1 if year > self.keys[-1] else -1
        start = self.keys[-1] if direction > 0 else self.keys[0]
        value = self.anchors[start]
        for y in range(start + direction, year + direction, direction):
            value += 0.25 * (self.mean - value) + self.seed.gauss(0.0, self.step_sd, "step", y)
        return value


class FinancialModel:
    def __init__(self, company: Company) -> None:
        self.company = company
        self.params = company.model
        fin = company.financials
        self.anchors = {m: {int(y): float(v) for y, v in series.items()} for m, series in fin.get("anchors", {}).items()}
        self.quarter_anchors = fin.get("quarterly", {})
        self.seed = Seeded("financials", company.ticker)
        growth = tuple(self.params.get("rev_growth", (0.02, 0.1)))
        self._levels = {
            name: AnchoredSeries.build(self.anchors[name], tuple(rng or growth), self.seed.child(name), noise=0.015)
            for name, rng in LEVELS.items()
            if self.anchors.get(name)
        }
        self._ratios = {
            name: RatioSeries(self.anchors[name], self.seed.child(name), sd)
            for name, sd in RATIOS.items()
            if self.anchors.get(name)
        }

    # ------------------------------------------------------------------ annual
    def annual(self, metric: str, year: int) -> float | None:
        return _annual_cached(self, metric, year)

    def _primitive(self, metric: str, year: int) -> float:
        if metric in self._levels:
            return self._levels[metric].value(year)
        if metric in self._ratios:
            return self._ratios[metric].value(year)
        raise KeyError(metric)

    def _compute(self, metric: str, year: int) -> float | None:
        anchored = self.anchors.get(metric, {}).get(year)
        if anchored is not None:
            return anchored
        if metric in LEVELS or metric in RATIOS:
            return self._primitive(metric, year)
        p, a = self.params, self.annual
        rev = a("revenue", year)
        if metric == "dda":
            return rev * p.get("dda_ratio", 0.05)
        if metric == "gross_income":
            return rev * a("gross_margin", year) / 100
        if metric == "cogs":
            return rev - a("gross_income", year) - 0.5 * a("dda", year)
        if metric == "oper_income":
            return rev * a("oper_margin", year) / 100
        if metric == "ebitda":
            return a("oper_income", year) + a("dda", year)
        if metric == "ebitda_margin":
            return 100 * a("ebitda", year) / rev
        if metric == "net_income":
            return rev * a("net_margin", year) / 100
        if metric == "eps":
            return a("net_income", year) / a("shares", year)
        if metric == "eps_rep":
            lo, hi = p.get("rep_gap", (0.0, 0.1))
            eps = a("eps", year)
            return eps * (1 - self.seed.uniform(lo, hi, "rep_gap", year)) if eps > 0 else eps * (1 + hi)
        if metric == "net_income_rep":
            return a("eps_rep", year) * a("shares", year)
        if metric == "net_margin_rep":
            return 100 * a("net_income_rep", year) / rev
        if metric == "cash":
            return rev * p.get("cash_ratio", 0.2) * self.seed.uniform(0.85, 1.15, "cash", year)
        if metric == "total_debt":
            return rev * p.get("debt_ratio", 0.3) * self.seed.uniform(0.9, 1.1, "debt", year)
        if metric == "net_debt":
            return a("total_debt", year) - a("cash", year)
        if metric == "invested_capital":
            nopat = a("oper_income", year) * (1 - p.get("tax_rate", 0.15))
            roic = a("roic", year)
            if abs(roic) >= 1 and nopat * roic > 0:
                return 100 * nopat / roic
            return rev * p.get("capital_intensity", 1.0)
        if metric == "equity":
            return max(a("invested_capital", year) - a("total_debt", year) + a("cash", year), 0.1 * rev)
        if metric == "total_assets":
            return a("equity", year) + a("total_debt", year) + 0.25 * rev
        if metric == "roe":
            return 100 * a("net_income_rep", year) / a("equity", year)
        if metric == "roa":
            return 100 * a("net_income_rep", year) / a("total_assets", year)
        if metric == "capex":
            return rev * p.get("capex_ratio", 0.05)
        if metric == "cfo":
            return rev * p.get("cfo_margin", 0.2) * self.seed.uniform(0.9, 1.1, "cfo", year)
        if metric == "fcf":
            return a("cfo", year) - a("capex", year)
        if metric == "bvps":
            return a("equity", year) / a("shares", year)
        return None

    # --------------------------------------------------------------- quarterly
    def quarterly(self, metric: str, period: Period) -> float | None:
        return _quarter_cached(self, metric, period.year, period.quarter)

    def _quarter(self, metric: str, year: int, quarter: int) -> float | None:
        key = f"{year}Q{quarter}"
        anchored = self.quarter_anchors.get(key, {}).get(metric)
        if anchored is not None:
            return float(anchored)
        annual = self.annual(metric, year)
        if annual is None:
            return None
        if metric in FLOW_METRICS:
            fixed = {q: self.quarter_anchors.get(f"{year}Q{q}", {}).get(metric) for q in range(1, 5)}
            free = [q for q in range(1, 5) if fixed[q] is None]
            remaining = annual - sum(float(v) for v in fixed.values() if v is not None)
            trend = bounded(self.params.get("rev_growth", (0.02, 0.1))[1] / 4, 0.0, 0.08)
            weights = split_weights(4, self.seed, "quarter-split", metric, year, trend=trend)
            share = sum(weights[q - 1] for q in free)
            return remaining * weights[quarter - 1] / share
        if metric in ("net_debt", "cash", "total_debt", "equity", "invested_capital", "total_assets"):
            prior = self.annual(metric, year - 1)
            return prior + (annual - prior) * quarter / 4
        if metric in RATIOS or metric.endswith("margin") or metric in ("roe", "roa", "roic"):
            return annual + self.seed.gauss(0.0, 0.03 * max(abs(annual), 1.0), "quarter-ratio", metric, year, quarter)
        return annual

    def value(self, metric: str, period: Period) -> float | None:
        return self.annual(metric, period.year) if period.is_annual else self.quarterly(metric, period)


@lru_cache(maxsize=65536)
def _annual_cached(model: FinancialModel, metric: str, year: int) -> float | None:
    return model._compute(metric, year)


@lru_cache(maxsize=65536)
def _quarter_cached(model: FinancialModel, metric: str, year: int, quarter: int) -> float | None:
    return model._quarter(metric, year, quarter)
