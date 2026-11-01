"""Builds seed_files/expense_seed.json (Emil Vanggaard's Zava Expense data) from seed_files/expense_world.json.

Run from infra/mock_environment/mock_mcp_servers:  python zava_expense/scripts/build_seed.py

Deterministic: the same world file always gives the same seed. Dates follow the lab calendar:
- The Seattle trip is Mon Oct 26 - Thu Oct 29, 2026, with the airfare charged Oct 19, matching the tenant's receipt emails.
- Past trips start on fixed Tuesdays; item offsets are days from the trip start (negative = booked in advance).
- Local card spend fills the ``local_spend_days`` before the lab week (Mon Nov 16), and every finished month
  gets a "local expenses" report; the latest (October) is still pending.
- Local spend that falls on a travel day is moved to the nearest free weekday in the same month, so monthly
  report totals and quarter totals don't change.

The tests in ../tests pin the numbers the lab guide quotes (ER-1051 $953.09, TX-10111, Q4 $4,309.55 of $6,800).
"""

from __future__ import annotations

import json
import random
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WORLD_PATH = ROOT / "seed_files" / "expense_world.json"
SEED_PATH = ROOT / "seed_files" / "expense_seed.json"


def round2(n: float) -> float:
    return round(n + 1e-9, 2)


def quarter_of(day: date) -> tuple[str, date, date]:
    q = (day.month - 1) // 3
    start = date(day.year, q * 3 + 1, 1)
    end = date(day.year + 1, 1, 1) - timedelta(days=1) if q == 3 else date(day.year, q * 3 + 4, 1) - timedelta(days=1)
    return f"Q{q + 1} {day.year}", start, end


def build_seed(world: dict) -> dict:
    rnd = random.Random(world["random_seed"])
    emp = world["employee"]
    card = emp["card_last_four"]
    trip = world["seattle_trip"]
    anchor = date.fromisoformat(world["lab_week_start"])
    seattle = date.fromisoformat(trip["start"])
    seattle_end = seattle + timedelta(days=trip["days"] - 1)
    blackout = (date.fromisoformat(trip["random_draw_blackout"]["start"]),
                date.fromisoformat(trip["random_draw_blackout"]["end"]))
    window_start = anchor - timedelta(days=world["local_spend_days"])
    month_start = anchor.replace(day=1)

    transactions: list[dict] = []
    reports: list[dict] = []
    away: list[tuple[date, date]] = [(seattle, seattle_end)]
    counters = {"tx": world["first_transaction_number"] - 1, "report": world["first_report_number"] - 1, "item": 0}

    def add_tx(day: date, merchant: str, city: str, category: str, amount: float, **extra) -> dict:
        counters["tx"] += 1
        tx = {"transaction_id": f"TX-{counters['tx']}", "date": day.isoformat(), "merchant": merchant, "city": city,
              "category": category, "amount": round2(amount), "currency": world["currency"], "card_last_four": card,
              **extra, "receipt_on_file": False, "report_id": None}
        transactions.append(tx)
        return tx

    def to_item(tx: dict, receipt: bool) -> dict:
        counters["item"] += 1
        item = {"item_id": f"LI-{counters['item']}", "transaction_id": tx["transaction_id"], "date": tx["date"],
                "merchant": tx["merchant"], "city": tx["city"], "category": tx["category"], "amount": tx["amount"]}
        for key in ("attendees", "lodging_nights"):
            if key in tx:
                item[key] = tx[key]
        item["receipt"] = ({"attached": True, "source": "upload", "reference": f"receipt-{tx['transaction_id']}.pdf"}
                           if receipt else {"attached": False})
        return item

    def make_report(title: str, purpose: str, client: str | None, status: str, reason: str | None,
                    created: date, submitted: date | None, decided: date | None, items: list[dict]) -> dict:
        counters["report"] += 1
        report = {
            "report_id": f"ER-{counters['report']}", "title": title, "business_purpose": purpose, "client": client,
            "status": status, "status_reason": reason, "created_on": created.isoformat(),
            "submitted_on": submitted.isoformat() if submitted else None,
            "decided_on": decided.isoformat() if decided else None,
            "reimbursed_on": (decided + timedelta(days=5)).isoformat() if decided and status == "Approved" else None,
            "approver": world["manager"]["name"], "justification": None, "note_to_approver": None,
            "items": items, "total": round2(sum(i["amount"] for i in items)),
        }
        for item in items:
            tx = next(t for t in transactions if t["transaction_id"] == item["transaction_id"])
            tx["report_id"] = report["report_id"]
            tx["receipt_on_file"] = item["receipt"]["attached"]
        reports.append(report)
        return report

    # Past trips, oldest first so report numbers rise over time.
    for past in sorted(world["past_trips"], key=lambda t: t["start"]):
        start = date.fromisoformat(past["start"])
        items, last = [], start
        for it in past["items"]:
            day = start + timedelta(days=it["offset"])
            last = max(last, day)
            extra = {}
            if "attendees" in it:
                extra["attendees"] = it["attendees"]
            if "nights" in it:
                n = len(it["nights"])
                extra["lodging_nights"] = [{"date": (day - timedelta(days=n - k)).isoformat(), "rate": rate}
                                           for k, rate in enumerate(it["nights"])]
            tx = add_tx(day, it["merchant"], past["city"], it["category"], it["amount"], **extra)
            items.append(to_item(tx, it.get("receipt", True)))
        away.append((start, last))
        submitted = last + timedelta(days=3)
        decided = None if past["status"] == "Pending approval" else submitted + timedelta(days=3)
        make_report(past["title"], past["purpose"], past["client"], past["status"], past.get("status_reason"),
                    last + timedelta(days=1), submitted, decided, items)

    # A report sent back for a missing business purpose.
    ret = world["returned_report"]
    day = date.fromisoformat(ret["date"])
    items = [to_item(add_tx(day, it["merchant"], it["city"], it["category"], it["amount"]), True) for it in ret["items"]]
    make_report(ret["title"], "", None, ret["status"], ret["status_reason"], day + timedelta(days=1),
                day + timedelta(days=2), day + timedelta(days=4), items)

    # Local card spend and monthly subscriptions.
    local: list[dict] = []
    day = window_start
    while day < anchor:
        for rec in world["recurring"]:
            if day.day == rec["day"]:
                tx = add_tx(day, rec["merchant"], "Online", rec["category"], rec["amount"])
                tx["receipt_on_file"] = True
        if day.weekday() < 5 and not (blackout[0] <= day <= blackout[1]) and rnd.random() < world["local_spend_probability"]:
            m = world["local_merchants"][int(rnd.random() * len(world["local_merchants"]))]
            amount = m["min"] + rnd.random() * (m["max"] - m["min"])
            extra = {"attendees": 2 + int(rnd.random() * 2)} if m["category"] == "Client entertainment" else {}
            local.append(add_tx(day, m["merchant"], world["home_city"], m["category"], amount, **extra))
        day += timedelta(days=1)

    # Emil can't buy lunch in Stamford while he's travelling: move those charges to a free weekday in the same month.
    def is_away(d: date) -> bool:
        return any(a <= d <= b for a, b in away)

    for tx in local:
        d = date.fromisoformat(tx["date"])
        if not is_away(d):
            continue
        for delta in (1, -1, 2, -2, 3, -3, 4, -4, 5, -5, 6, -6, 7, -7):
            cand = d + timedelta(days=delta)
            if cand.month == d.month and cand.weekday() < 5 and not is_away(cand) and cand < anchor:
                tx["date"] = cand.isoformat()
                break
        else:
            raise RuntimeError(f"no free weekday for {tx['transaction_id']}")

    # Monthly "local expenses" reports for finished months; the most recent one is still pending.
    by_month: dict[str, list[dict]] = {}
    for tx in sorted(transactions, key=lambda t: (t["date"], t["transaction_id"])):
        if tx["report_id"] is None and tx["date"] < month_start.isoformat():
            by_month.setdefault(tx["date"][:7], []).append(tx)
    months = sorted(by_month)
    for idx, key in enumerate(months):
        first = date.fromisoformat(f"{key}-01")
        nxt = (first.replace(day=28) + timedelta(days=4)).replace(day=1)
        pending = idx == len(months) - 1
        submitted = nxt + timedelta(days=2)
        make_report(f"Local expenses and subscriptions — {first:%B %Y}",
                    "Local client meetings, travel to customer sites and monthly software subscriptions.", None,
                    "Pending approval" if pending else "Approved", None, nxt + timedelta(days=1), submitted,
                    None if pending else submitted + timedelta(days=4),
                    [to_item(tx, True) for tx in by_month[key]])

    # The Seattle trip: not on any report yet; its receipts are in Emil's inbox.
    for it in trip["items"]:
        extra = {}
        d = date.fromisoformat(it["date"]) if "date" in it else seattle + timedelta(days=it["offset"])
        if "attendees" in it:
            extra["attendees"] = it["attendees"]
        if "nights" in it:
            extra["lodging_nights"] = [{"date": (seattle + timedelta(days=k)).isoformat(), "rate": rate}
                                       for k, rate in enumerate(it["nights"])]
        add_tx(d, it["merchant"], "Seattle", it["category"], it["amount"], **extra)

    transactions.sort(key=lambda t: (t["date"], t["transaction_id"]))

    airfare = next(it["date"] for it in trip["items"] if "date" in it)
    fmt = {f"d{k}": f"{seattle + timedelta(days=k):%B} {(seattle + timedelta(days=k)).day}" for k in range(trip["days"])}
    fmt.update({"airfare": f"{date.fromisoformat(airfare):%B} {date.fromisoformat(airfare).day}", "card": card})
    emails = [{"from": e["from"], "subject": e["subject"], "received_on": e["received_on"],
               "amount": e["amount"], "body": e["body"].format(**fmt)} for e in trip["receipt_emails"]]

    label, q_start, q_end = quarter_of(anchor)
    return {
        "lab_week_start": anchor.isoformat(),
        "company": world["company"],
        "employee": emp,
        "manager": world["manager"],
        "finance_contact": world["finance_contact"],
        "clients": world["clients"],
        "policy": world["policy"],
        "budget": {"owner": emp["name"], "period": label, "period_start": q_start.isoformat(),
                   "period_end": q_end.isoformat(), "lines": world["budget"]["lines"]},
        "seattle_trip": {"start": seattle.isoformat(), "end": seattle_end.isoformat(), "client": trip["client"],
                         "purpose": trip["purpose"]},
        "receipt_emails": emails,
        "transactions": transactions,
        "reports": reports,
        "_next_report": world["new_report_number"],
        "_next_item": counters["item"] + 1,
    }


def main() -> None:
    world = json.loads(WORLD_PATH.read_text(encoding="utf-8"))
    seed = build_seed(world)
    SEED_PATH.write_text(json.dumps(seed, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {SEED_PATH.relative_to(ROOT)}: {len(seed['transactions'])} card charges, {len(seed['reports'])} reports")


if __name__ == "__main__":
    main()
