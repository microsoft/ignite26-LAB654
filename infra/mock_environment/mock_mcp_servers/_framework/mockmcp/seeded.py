"""Deterministic synthetic data.

Mock servers fall back to generated values when a request goes beyond the seeded data
(another quarter, another peer, a longer history). Generated values must be:

* deterministic: the same inputs give the same output on any machine, in any process,
  in any call order. Seeds come from SHA-256 of the inputs, never from ``hash()``
  (salted per process) or from global random state.
* anchored: generated points continue smoothly from real seed values instead of
  replacing them.

``Seeded`` is the only source of randomness mock servers should use.
"""

from __future__ import annotations

import hashlib
import json
import math
import random
from dataclasses import dataclass
from typing import Any, Iterable


def stable_hash(*parts: Any) -> int:
    """A 64-bit hash of ``parts`` that's stable across processes and platforms."""
    canonical = json.dumps(parts, sort_keys=True, default=str, separators=(",", ":"))
    return int.from_bytes(hashlib.sha256(canonical.encode("utf-8")).digest()[:8], "big")


class Seeded:
    """A namespaced, deterministic random source.

    ``Seeded("lseg", "NVDA").uniform(0.9, 1.1, "rev", 2024)`` always returns the same
    number. Each call draws from its own RNG keyed by namespace + key, so adding or
    reordering calls elsewhere never changes existing values.
    """

    def __init__(self, *namespace: Any) -> None:
        self.namespace = namespace

    def child(self, *namespace: Any) -> "Seeded":
        return Seeded(*self.namespace, *namespace)

    def rng(self, *key: Any) -> random.Random:
        return random.Random(stable_hash(*self.namespace, *key))

    def uniform(self, low: float, high: float, *key: Any) -> float:
        return self.rng(*key).uniform(low, high)

    def gauss(self, mu: float, sigma: float, *key: Any) -> float:
        return self.rng(*key).gauss(mu, sigma)

    def integer(self, low: int, high: int, *key: Any) -> int:
        return self.rng(*key).randint(low, high)

    def choice(self, options: list[Any], *key: Any) -> Any:
        return self.rng(*key).choice(options)

    def token(self, length: int, *key: Any, alphabet: str = "0123456789ABCDEFGHJKLMNPQRSTUVWXYZ") -> str:
        rng = self.rng(*key)
        return "".join(rng.choice(alphabet) for _ in range(length))


@dataclass(frozen=True)
class AnchoredSeries:
    """A positive series over integer steps (years, quarters) built from known anchors.

    * At an anchor, returns the anchor value exactly.
    * Between two anchors, interpolates geometrically, with a little seeded noise that
      vanishes at both ends.
    * Beyond the anchors, walks step by step from the nearest anchor, applying a
      seeded growth factor drawn from ``growth`` for each step. Going backwards
      divides by the factor, so history shrinks for growing companies.

    Each step's factor depends only on (seed, step), so ``value(k)`` never changes when
    other points are requested.
    """

    anchors: tuple[tuple[int, float], ...]
    growth: tuple[float, float]
    seed: Seeded
    noise: float = 0.02

    @classmethod
    def build(cls, anchors: dict[int, float], growth: tuple[float, float], seed: Seeded, noise: float = 0.02) -> "AnchoredSeries":
        clean = tuple(sorted((int(k), float(v)) for k, v in anchors.items() if v is not None))
        if not clean:
            raise ValueError("AnchoredSeries needs at least one anchor")
        return cls(clean, growth, seed, noise)

    def _factor(self, step: int) -> float:
        return 1.0 + self.seed.uniform(self.growth[0], self.growth[1], "growth", step)

    def value(self, step: int) -> float:
        keys = [k for k, _ in self.anchors]
        lookup = dict(self.anchors)
        if step in lookup:
            return lookup[step]
        if step > keys[-1]:
            value = lookup[keys[-1]]
            for s in range(keys[-1] + 1, step + 1):
                value *= self._factor(s)
            return value
        if step < keys[0]:
            value = lookup[keys[0]]
            for s in range(keys[0], step, -1):
                value /= self._factor(s)
            return value
        lo = max(k for k in keys if k < step)
        hi = min(k for k in keys if k > step)
        t = (step - lo) / (hi - lo)
        v_lo, v_hi = lookup[lo], lookup[hi]
        if v_lo > 0 and v_hi > 0:
            base = math.exp(math.log(v_lo) + t * (math.log(v_hi) - math.log(v_lo)))
        else:
            base = v_lo + t * (v_hi - v_lo)
        wobble = 1.0 + self.seed.gauss(0.0, self.noise, "between", step) * math.sin(math.pi * t)
        return base * wobble


def bounded(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def split_weights(count: int, seed: Seeded, *key: Any, trend: float = 0.0, jitter: float = 0.03) -> list[float]:
    """Positive weights summing to 1, e.g. to split a year into quarters.

    ``trend`` tilts later weights up (growth companies earn more in Q4 than Q1).
    """
    raw = [(1.0 + trend) ** i * (1.0 + seed.gauss(0.0, jitter, *key, i)) for i in range(count)]
    raw = [max(r, 0.05) for r in raw]
    total = sum(raw)
    return [r / total for r in raw]


def round_sig(value: float | None, digits: int = 6) -> float | None:
    """Round to significant digits so generated numbers look like vendor data."""
    if value is None or value == 0 or not math.isfinite(value):
        return value
    return round(value, max(0, digits - 1 - int(math.floor(math.log10(abs(value))))))


def pairwise(items: Iterable[Any]) -> Iterable[tuple[Any, Any]]:
    items = list(items)
    return zip(items, items[1:])
