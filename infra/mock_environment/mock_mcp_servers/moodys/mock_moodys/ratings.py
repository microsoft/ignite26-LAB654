"""Rating histories: recorded where we have them, otherwise generated to end at the seeded current rating."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta

from mockfin.universe import Company
from mockmcp import Seeded

from .common import RATING_CLASS, MoodysData

SCALE = (
    "Aaa", "Aa1", "Aa2", "Aa3", "A1", "A2", "A3", "Baa1", "Baa2", "Baa3",
    "Ba1", "Ba2", "Ba3", "B1", "B2", "B3", "Caa1", "Caa2", "Caa3", "Ca", "C",
)  # fmt: skip
ANALYSTS = ("Priya Natarajan", "Daniel Okafor", "Elena Marquez", "Hannah Cole", "Marcus Lindqvist", "Aiko Tanaka")
_seed = Seeded("moodys", "ratings")


def notch(rating: str, steps: int) -> str:
    """Move ``steps`` notches; positive is an upgrade."""
    index = min(max(SCALE.index(rating) - steps, 0), len(SCALE) - 1)
    return SCALE[index]


@dataclass(frozen=True)
class RatingEvent:
    day: date
    rating: str
    action: str


@dataclass(frozen=True)
class RatingHistory:
    rating_class: str
    current: RatingEvent
    outlook: str
    events: tuple[RatingEvent, ...]
    analyst: str

    def since(self, cutoff: date) -> list[RatingEvent]:
        return [e for e in self.events if e.day >= cutoff]

    def render(self, cutoff: date) -> str:
        c = self.current
        lines = [
            "MIS",
            "",
            f"Current Rating: {c.rating} ({self.rating_class}) - {c.day.isoformat()} {c.action} - Outlook: {self.outlook}",
            "",
            "Date\tRating\tRating Action",
            *(f"{e.day.isoformat()}\t{e.rating}\t{e.action}" for e in self.since(cutoff)),
            "",
            f"Analyst: {self.analyst}",
        ]
        return "\n".join(lines)


class RatingBook:
    """Deep module: ``history(company, today)`` hides recorded-vs-generated."""

    def __init__(self, data: MoodysData) -> None:
        self.data = data

    def history(self, company: Company, today: date) -> RatingHistory:
        recorded = self.data.recorded_rating(company)
        return self._from_record(recorded) if recorded else self._generate(company, today)

    @staticmethod
    def _from_record(rec: dict) -> RatingHistory:
        cur = rec["current"]
        return RatingHistory(
            rating_class=rec["rating_class"],
            current=RatingEvent(date.fromisoformat(cur["date"]), cur["rating"], cur["action"]),
            outlook=cur["outlook"],
            events=tuple(RatingEvent(date.fromisoformat(d), r, a) for d, r, a in rec["history"]),
            analyst=rec["analyst"],
        )

    def _generate(self, company: Company, today: date) -> RatingHistory:
        m = company.moodys
        key = m["org_id"]
        current, outlook = m["rating"], m["outlook"]
        # Positive outlooks follow a run of upgrades, negative ones a run of downgrades.
        moves = {"Positive": _seed.integer(2, 3, key, "moves"), "Negative": -_seed.integer(1, 2, key, "moves")}.get(
            outlook, _seed.choice([0, 1], key, "moves")
        )
        count = max(abs(moves) + 2, _seed.integer(5, 7, key, "count"))
        last = today - timedelta(days=_seed.integer(45, 300, key, "last"))
        days = [last]
        for i in range(count - 1):
            days.append(days[-1] - timedelta(days=_seed.integer(200, 520, key, "gap", i)))
        days.reverse()
        slots = sorted(_seed.rng(key, "slots").sample(range(1, count - 1), abs(moves)))
        rating = notch(current, -moves)
        events = [RatingEvent(days[0], rating, "Affirmation")]
        for i, day in enumerate(days[1:], start=1):
            if i in slots:
                rating = notch(rating, 1 if moves > 0 else -1)
                events.append(RatingEvent(day, rating, "Upgrade" if moves > 0 else "Downgrade"))
            else:
                events.append(RatingEvent(day, rating, "Affirmation"))
        assert events[-1].rating == current
        return RatingHistory(RATING_CLASS, events[-1], outlook, tuple(events), _seed.choice(list(ANALYSTS), key, "analyst"))
