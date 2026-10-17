"""Credit opinions: recorded sections verbatim, every other section from rating-aware templates."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta

from mockfin import CompanyView
from mockmcp import Seeded

from .common import MoodysData
from .ratings import SCALE, RatingHistory

# Request key -> section title as the live API prints it. Order is the canonical output order.
SECTIONS = {
    "Summary": "Summary",
    "CreditStrengths": "Credit strengths",
    "CreditChallenges": "Credit challenges",
    "RatingOutlook": "Rating outlook",
    "FactorsLeadingToUpgrade": "Factors that could lead to an upgrade",
    "FactorsLeadingToDowngrade": "Factors that could lead to a downgrade",
    "Liquidity": "Liquidity analysis",
    "ESGConsiderations": "ESG considerations",
}
DEFAULT_SECTIONS = ("Summary", "CreditStrengths", "CreditChallenges", "RatingOutlook")
_seed = Seeded("moodys", "opinions")


@dataclass(frozen=True)
class Opinion:
    doc_id: str
    title: str
    day: date
    header_html: str
    sections: tuple[tuple[str, str], ...]  # (title, html) in output order

    def render(self) -> str:
        body = "\n".join(f"Section Title: {title}\n{html}" for title, html in self.sections)
        return f"{self.header_html}\n {body}" if body else self.header_html


def _ul(items: list[str]) -> str:
    return "<ul>" + "".join(f"<li>{i} </li>" for i in items) + " </ul>"


def _p(text: str) -> str:
    return f"<p>{text} </p>"


def _money(millions: float | None) -> str:
    if millions is None:
        return "n/a"
    return f"${millions / 1000:,.1f} billion" if abs(millions) >= 1000 else f"${millions:,.0f} million"


class OpinionWriter:
    """Deep module: ``opinion(view, history, keys, now)`` hides recorded-vs-templated sections."""

    def __init__(self, data: MoodysData) -> None:
        self.data = data

    def opinion(self, view: CompanyView, history: RatingHistory, keys: list[str], now: datetime) -> Opinion:
        company = view.company
        wanted = [SECTIONS[k] for k in SECTIONS if k in keys]  # dedupe, canonical order
        recorded = self.data.recorded_opinion(company)
        facts = _Facts.build(view, history, now)
        generated = {title: self._section(title, facts) for title in wanted}
        if recorded:
            stored = [(s["title"], s["html"]) for s in recorded["sections"] if s["title"] in wanted]
            have = {t for t, _ in stored}
            extra = [(t, generated[t]) for t in wanted if t not in have]
            return Opinion(
                recorded["id"],
                recorded["title"],
                date.fromisoformat(recorded["date"]),
                recorded["header_html"],
                tuple(stored + extra),
            )
        key = company.moodys["org_id"]
        day = min(history.current.day + timedelta(days=_seed.integer(4, 30, key, "lag")), now.date() - timedelta(days=1))
        action = history.current.action.lower()
        title = f"{company.name}: Updated opinion after ratings {action}"
        header = (
            f"Title: <h4>{title} </h4> <p>Credit Opinion - ({day.isoformat()}) </p>  "
            f"<h6>Our credit view of this issuer reflects {facts.headline}.</h6>"
        )
        return Opinion(
            f"PBC_{_seed.integer(1300000, 1499999, key, 'doc')}",
            title,
            day,
            header,
            tuple((t, generated[t]) for t in wanted),
        )

    def _section(self, title: str, f: "_Facts") -> str:
        n = f.short
        if title == "Summary":
            return _p(
                f"{f.name}'s {f.rating} rating reflects {f.headline}. Revenue reached {_money(f.revenue)} in fiscal "
                f"{f.fy} with EBITDA of {_money(f.ebitda)}, and the company ended the year with "
                f"{'net cash of ' + _money(-f.net_debt) if f.net_debt is not None and f.net_debt < 0 else 'net debt of ' + _money(f.net_debt)}. "
                f"{n}'s product breadth and customer relationships across data center, PC, mobile and industrial end "
                f"markets support the credit profile, while the cyclicality of semiconductor demand and heavy, "
                f"sustained R&D and capital investment needs constrain it. The {f.outlook.lower()} outlook reflects "
                f"{f.outlook_reason}."
            )
        if title == "Credit strengths":
            return _ul(f.pick("strengths", STRENGTHS, 4))
        if title == "Credit challenges":
            return _ul(f.pick("challenges", CHALLENGES, 4))
        if title == "Rating outlook":
            return _p(f"The {f.outlook.lower()} outlook reflects {f.outlook_reason}.")
        if title == "Factors that could lead to an upgrade":
            if f.rating == SCALE[0]:
                return _p("An upgrade is unlikely given the company's position at the top of the rating scale.")
            return _ul(
                [
                    f"Sustained revenue scale above {_money((f.revenue or 0) * 1.25)} with stable or rising margins",
                    f"Debt to EBITDA sustained below {f.lev_up:.1f}x",
                    f"Free cash flow to debt consistently above {f.fcf_up}%",
                    "Greater diversification across end markets and customers",
                ]
            )
        if title == "Factors that could lead to a downgrade":
            return _ul(
                [
                    f"Debt to EBITDA sustained above {f.lev_down:.1f}x",
                    f"Free cash flow to debt falling below {f.fcf_down}% for an extended period",
                    "Material market share losses or a prolonged downturn in key end markets",
                    "More aggressive financial policies, including large debt-funded acquisitions or share buybacks",
                ]
            )
        if title == "Liquidity analysis":
            return _p(
                f"We expect {n} to maintain very good liquidity, supported by cash and investments, annual free cash "
                f"flow of roughly {_money(f.fcf)} and an undrawn committed revolving credit facility. Near-term debt "
                f"maturities are modest relative to internal cash generation."
            )
        if title == "ESG considerations":
            return _p(
                f"{n}'s ESG credit impact score is neutral-to-low. Governance risks are low, reflecting conservative "
                f"financial policies and a track record of meeting guidance. Environmental and social exposures are "
                f"manageable, though supply chain concentration and export controls remain points of attention."
            )
        raise KeyError(title)


@dataclass(frozen=True)
class _Facts:
    name: str
    short: str
    key: int
    rating: str
    outlook: str
    fy: int
    revenue: float | None
    ebitda: float | None
    net_debt: float | None
    fcf: float | None

    @classmethod
    def build(cls, view: CompanyView, history: RatingHistory, now: datetime) -> "_Facts":
        c = view.company
        period = view.latest(now, quarterly=False)
        value = lambda m: view.actual(m, period, now)  # noqa: E731
        return cls(
            c.name, c.short_name, c.moodys["org_id"], history.current.rating, history.outlook, period.year,
            value("revenue"), value("ebitda"), value("net_debt"), value("fcf"),
        )  # fmt: skip

    @property
    def tier(self) -> int:
        return SCALE.index(self.rating)

    @property
    def headline(self) -> str:
        if self.tier <= 3:
            return "its leading market positions, very strong profitability and conservative balance sheet"
        if self.tier <= 6:
            return "its large scale, strong market positions and solid free cash flow, balanced by industry cyclicality"
        return "its established franchise and scale, tempered by competitive pressure and higher leverage"

    @property
    def outlook_reason(self) -> str:
        return {
            "Positive": "our expectation that revenue growth and margin expansion will continue to strengthen credit metrics over the next 12 to 18 months",
            "Negative": "the risk that weaker operating performance and elevated investment needs keep leverage above levels consistent with the current rating",
            "Developing": "uncertainty over the outcome of strategic actions that could move credit metrics materially in either direction",
        }.get(self.outlook, "our expectation that the company will maintain its market position and credit metrics over the next 12 to 18 months")  # fmt: skip

    @property
    def lev_up(self) -> float:
        return round(max(0.5, 0.4 + 0.25 * self.tier), 1)

    @property
    def lev_down(self) -> float:
        return round(self.lev_up + 1.0, 1)

    @property
    def fcf_up(self) -> int:
        return max(20, 60 - 5 * self.tier)

    @property
    def fcf_down(self) -> int:
        return max(10, self.fcf_up - 15)

    def pick(self, label: str, pool: list[str], count: int) -> list[str]:
        rng = _seed.rng(self.key, label)
        return [s.format(n=self.short) for s in rng.sample(pool, count)]


STRENGTHS = [
    "Leading market positions in core product segments with high barriers to entry",
    "Broad and diversified product portfolio serving data center, PC, mobile and industrial customers",
    "Strong free cash flow generation through the semiconductor cycle",
    "Conservative financial policies and good liquidity",
    "Long-standing customer relationships and a large installed base",
    "Significant scale in research and development that supports product leadership",
    "Exposure to structural growth in AI and accelerated computing",
]
CHALLENGES = [
    "Cyclical and volatile semiconductor demand",
    "Intense competition and rapid technology change require sustained R&D investment",
    "Customer concentration among a small number of large buyers",
    "Reliance on third-party foundries concentrated in Taiwan amid geopolitical tensions",
    "Export controls limit access to the China market",
    "Shareholder returns could absorb a large share of free cash flow",
    "Integration and execution risk from acquisitions",
]
