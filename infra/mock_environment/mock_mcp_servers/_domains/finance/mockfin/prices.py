"""Deterministic daily and monthly price bars.

Closes pass exactly through ``companies.json -> price.anchors`` (log-space Brownian
bridge between anchors, seeded random walk before the first and after the last).
Exact recorded bars in ``data/price_bars.json`` override generated ones, so replayed
dates match the recorded trace to the cent.

Bars exist only for completed NYSE sessions up to "now".
"""

from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass
from datetime import date, datetime, timedelta
from functools import lru_cache

from mockmcp import Seeded

from .calendars import last_completed_session, month_end, trading_days
from .universe import DATA_DIR, Company

HISTORY_START = date(2015, 1, 2)


@dataclass(frozen=True)
class Bar:
    date: date
    open: float
    high: float
    low: float
    close: float
    volume: int
    vwap: float
    bid: float
    ask: float
    turnover: float
    num_moves: int
    blk_count: int
    blk_volume: int
    vwap_vol: int = 0
    acvol_dec: float = 0.0

    def as_dict(self) -> dict:
        out = asdict(self)
        out["date"] = self.date.isoformat()
        return out


@dataclass(frozen=True)
class MonthBar:
    date: date  # month end (vendor "endPeriod" label)
    open: float
    high: float
    low: float
    close: float
    volume: int
    vwap: float
    bid: float
    ask: float
    turnover: float
    num_moves: int
    blk_count: int
    blk_volume: int
    vwap_vol: int
    acvol_dec: float
    vwap_open: float
    vwap_high: float
    vwap_low: float
    bid_open: float
    bid_high: float
    bid_low: float
    ask_open: float
    ask_high: float
    ask_low: float


@lru_cache(maxsize=1)
def _overrides() -> dict:
    path = DATA_DIR / "price_bars.json"
    if not path.exists():
        return {}
    with open(path, encoding="utf-8") as handle:
        return json.load(handle).get("daily", {})


class PriceModel:
    def __init__(self, company: Company) -> None:
        self.company = company
        cfg = company.price
        self.vol = float(cfg.get("vol", 0.02))
        self.base_volume = float(cfg.get("volume", 5_000_000))
        self.anchors = sorted((date.fromisoformat(d), float(p)) for d, p in cfg.get("anchors", {}).items())
        self.seed = Seeded("prices", company.ticker)
        self.overrides = {
            date.fromisoformat(d): row for d, row in _overrides().get(company.ticker, {}).items()
        }

    # ------------------------------------------------------------ closes
    @lru_cache(maxsize=4)
    def _closes(self, until: date) -> dict[date, float]:
        days = trading_days(HISTORY_START, max(until, self.anchors[-1][0] if self.anchors else until))
        if not self.anchors:
            self.anchors = [(days[0], 50.0)]
        log_close: dict[date, float] = {}
        first_day, first_px = self.anchors[0]
        # Before the first anchor: walk backwards.
        level = math.log(first_px)
        for day in reversed([d for d in days if d < first_day]):
            level -= self.seed.gauss(0.0004, self.vol, "ret", day.isoformat())
            log_close[day] = level
        # Between anchors: Brownian bridge.
        for (d0, p0), (d1, p1) in zip(self.anchors, self.anchors[1:]):
            seg = [d for d in days if d0 <= d <= d1]
            if not seg:
                continue
            walk, acc = [0.0], 0.0
            for day in seg[1:]:
                acc += self.seed.gauss(0.0, self.vol, "ret", day.isoformat())
                walk.append(acc)
            n = len(seg) - 1 or 1
            a, b = math.log(p0), math.log(p1)
            for i, day in enumerate(seg):
                t = i / n
                log_close[day] = a + t * (b - a) + walk[i] - t * walk[-1]
        # After the last anchor: walk forwards.
        last_day, last_px = self.anchors[-1]
        level = math.log(last_px)
        for day in (d for d in days if d > last_day):
            level += self.seed.gauss(0.0004, self.vol, "ret", day.isoformat())
            log_close[day] = level
        for day, px in self.anchors:
            log_close[day] = math.log(px)
        return {d: round(math.exp(v), 2) for d, v in sorted(log_close.items())}

    # -------------------------------------------------------------- bars
    def daily(self, start: date, end: date, now: datetime) -> list[Bar]:
        """Completed daily bars in [start, end], oldest first."""
        last = min(end, last_completed_session(now))
        if last < max(start, HISTORY_START):
            return []
        closes = self._closes(_horizon(now))
        days = [d for d in closes if max(start, HISTORY_START) <= d <= last]
        return [self._bar(d, closes) for d in days]

    def latest(self, now: datetime) -> Bar | None:
        last = last_completed_session(now)
        bars = self.daily(last - timedelta(days=10), last, now)
        return bars[-1] if bars else None

    def _bar(self, day: date, closes: dict[date, float]) -> Bar:
        override = self.overrides.get(day)
        if override:
            return Bar(date=day, **override)
        close = closes[day]
        prior = closes.get(_prev_key(closes, day), close)
        key = day.isoformat()
        rng = self.seed.child("bar", key)
        open_ = round(prior * math.exp(rng.gauss(0.0, self.vol * 0.35, "open")), 2)
        span = abs(rng.gauss(0.0, self.vol * 0.55, "range"))
        high = round(max(open_, close) * (1 + span * rng.uniform(0.2, 1.0, "hi")), 4)
        low = round(min(open_, close) * (1 - span * rng.uniform(0.2, 1.0, "lo")), 4)
        move = abs(math.log(close / prior)) / self.vol if prior else 0.0
        volume = int(self.base_volume * math.exp(rng.gauss(0.0, 0.22, "vol")) * (0.8 + 0.25 * move))
        vwap = round((open_ + high + low + 2 * close) / 5, 4)
        tick = 0.01
        return Bar(
            date=day, open=open_, high=high, low=low, close=close, volume=volume, vwap=vwap,
            bid=round(close - tick * rng.integer(0, 2, "bid"), 2),
            ask=round(close + tick * rng.integer(1, 3, "ask"), 2),
            turnover=float(round(volume * vwap)),
            num_moves=int(volume / rng.uniform(48, 64, "moves")),
            blk_count=rng.integer(60, 260, "blk"),
            blk_volume=int(volume * rng.uniform(0.12, 0.24, "blkvol")),
            vwap_vol=int(volume * rng.uniform(0.84, 0.92, "vwapvol")),
            acvol_dec=round(volume + rng.uniform(0.0, 1.0, "dec"), 6),
        )

    def monthly(self, start: date, end: date, now: datetime) -> list[MonthBar]:
        """Monthly bars labelled by month end; the current month is partial (to date)."""
        return self.aggregate("M", start, end, now)

    def aggregate(self, unit: str, start: date, end: date, now: datetime) -> list[MonthBar]:
        """Bars over calendar buckets: ``W`` (week ending Friday), ``M``, ``Q`` or ``Y``.

        Each bar is labelled by its bucket end; the current bucket is partial (to date).
        Buckets are included when their label falls in [start, end-bucket label].
        """
        label_of = _BUCKETS[unit]
        first = label_of(start) - _BUCKET_SPAN[unit]
        buckets: dict[date, list[Bar]] = {}
        for bar in self.daily(first, end, now):
            buckets.setdefault(label_of(bar.date), []).append(bar)
        out = []
        for label, group in sorted(buckets.items()):
            if label < start or label > label_of(end):
                continue
            volume = sum(b.volume for b in group)
            turnover = sum(b.turnover for b in group)
            vwaps = [b.vwap for b in group]
            bids = [b.bid for b in group]
            asks = [b.ask for b in group]
            out.append(MonthBar(
                date=label, open=group[0].open, high=max(b.high for b in group),
                low=min(b.low for b in group), close=group[-1].close, volume=volume,
                vwap=round(turnover / volume, 4) if volume else group[-1].vwap,
                bid=group[-1].bid, ask=group[-1].ask, turnover=turnover,
                num_moves=sum(b.num_moves for b in group), blk_count=sum(b.blk_count for b in group),
                blk_volume=sum(b.blk_volume for b in group),
                vwap_vol=sum(b.vwap_vol for b in group),
                acvol_dec=round(sum(b.acvol_dec for b in group), 6),
                vwap_open=vwaps[0], vwap_high=max(vwaps), vwap_low=min(vwaps),
                bid_open=bids[0], bid_high=max(bids), bid_low=min(bids),
                ask_open=asks[0], ask_high=max(asks), ask_low=min(asks),
            ))
        return out

    def close_on(self, day: date, now: datetime) -> Bar | None:
        """The bar for ``day`` or the last completed session before it."""
        bars = self.daily(day - timedelta(days=12), day, now)
        return bars[-1] if bars else None


_BUCKETS = {
    "W": lambda d: d + timedelta(days=(4 - d.weekday()) % 7),
    "M": lambda d: month_end(d.year, d.month),
    "Q": lambda d: month_end(d.year, ((d.month - 1) // 3) * 3 + 3),
    "Y": lambda d: date(d.year, 12, 31),
}
_BUCKET_SPAN = {"W": timedelta(days=7), "M": timedelta(days=31), "Q": timedelta(days=92), "Y": timedelta(days=366)}


def _prev_key(closes: dict[date, float], day: date) -> date:
    probe = day - timedelta(days=1)
    for _ in range(10):
        if probe in closes:
            return probe
        probe -= timedelta(days=1)
    return day


def _horizon(now: datetime) -> date:
    """Generate through year-end so the cache key changes rarely."""
    return date(now.year, 12, 31)
