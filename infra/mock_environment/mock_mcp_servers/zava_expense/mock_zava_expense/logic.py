"""Expense logic: policy checks, receipt matching, report changes, card feed and budget."""

from __future__ import annotations

import re
from datetime import date, datetime, timedelta

from mockmcp import ToolError


CATEGORIES = [
    "Airfare", "Lodging", "Meals", "Client entertainment", "Ground transport",
    "Conference & training", "Software & subscriptions", "Mobile & internet", "Office supplies",
]
EDITABLE = ("Draft", "Returned", "Rejected")
OPEN = ("Draft", "Pending approval", "Rejected", "Returned")
BUDGET_LINE = {
    "Airfare": "Airfare", "Lodging": "Lodging", "Meals": "Meals & entertainment",
    "Client entertainment": "Meals & entertainment", "Ground transport": "Ground transport",
    "Conference & training": "Conference & training",
}


def money(n: float) -> str:
    return f"${n:,.2f}"


def round2(n: float) -> float:
    return round(n + 1e-9, 2)


def quarter_of(day: date) -> tuple[str, date, date]:
    q = (day.month - 1) // 3
    start = date(day.year, q * 3 + 1, 1)
    end = date(day.year + 1, 1, 1) - timedelta(days=1) if q == 3 else date(day.year, q * 3 + 4, 1) - timedelta(days=1)
    return f"Q{q + 1} {day.year}", start, end


# --- Lookups ------------------------------------------------------------------------------------------

def find_report(data: dict, report_id: str) -> dict:
    rid = report_id.strip().lower()
    report = next((r for r in data["reports"] if r["report_id"].lower() == rid), None)
    if report is None:
        raise ToolError(f"No expense report {report_id}. Use list_expense_reports to see report IDs.")
    return report


def summarize(r: dict) -> dict:
    return {k: r[k] for k in ("report_id", "title", "status", "status_reason", "total", "client", "submitted_on",
                              "decided_on", "reimbursed_on", "approver")} | {"item_count": len(r["items"])}


def _key(x: dict) -> str:
    return f"{x['date']}|{x['merchant']}|{x['amount']}"


def duplicate_charges(data: dict) -> set[str]:
    seen, dups = set(), set()
    for t in data["transactions"]:
        if _key(t) in seen:
            dups.add(t["transaction_id"])
        seen.add(_key(t))
    return dups


# --- Policy -------------------------------------------------------------------------------------------

def cap_for(policy: dict, city: str) -> float:
    return policy["hotel_nightly_caps_usd"].get(city, policy["default_hotel_nightly_cap_usd"])


def check_report(data: dict, report: dict, today: date) -> dict:
    policy = data["policy"]
    findings: list[dict] = []
    justified = bool((report.get("justification") or "").strip())
    over = "exception-justified" if justified else "blocking"

    def add(code, rule, severity, message, item=None):
        findings.append({"code": code, "rule_id": rule, "severity": severity, **({"item_id": item} if item else {}),
                         "message": message})

    if not (report.get("business_purpose") or "").strip():
        add("BUSINESS_PURPOSE_MISSING", "TE-09", "blocking", "Add a business purpose (and the client, if the trip was client-related).")

    meals: dict[str, float] = {}
    for it in report["items"]:
        if it["amount"] >= policy["receipt_required_at_or_above_usd"] and not it["receipt"]["attached"]:
            add("MISSING_RECEIPT", "TE-06", "blocking",
                f"{it['merchant']} {money(it['amount'])} on {it['date']} needs an itemized receipt.", it["item_id"])
        if it["category"] == "Lodging":
            cap = cap_for(policy, it["city"])
            for night in it.get("lodging_nights", []):
                if night["rate"] > cap:
                    tail = (" Justification provided; your manager approves the exception." if justified
                            else " Add a justification or remove the excess before submitting.")
                    add("HOTEL_OVER_CAP", "TE-01", over,
                        f"{it['merchant']}: the night of {night['date']} was {money(night['rate'])}, "
                        f"{money(night['rate'] - cap)} over the {it['city']} cap of ${cap:g}.{tail}", it["item_id"])
        if it["category"] == "Client entertainment":
            people = it.get("attendees")
            limit = policy["client_entertainment_per_person_usd"]
            if not people:
                add("ATTENDEES_MISSING", "TE-04", "warning",
                    f"{it['merchant']}: list the number of attendees for client entertainment.", it["item_id"])
            elif it["amount"] / people > limit:
                add("ENTERTAINMENT_OVER_LIMIT", "TE-04", over,
                    f"{it['merchant']}: {money(it['amount'] / people)} per person is over the ${limit} limit.", it["item_id"])
        if it["category"] == "Meals":
            meals[it["date"]] = meals.get(it["date"], 0) + it["amount"]
    for day, total in meals.items():
        if total > policy["meals_per_day_usd"]:
            add("MEALS_OVER_DAILY", "TE-03", "warning",
                f"Meals on {day} total {money(total)}, over the ${policy['meals_per_day_usd']} daily limit.")

    seen: set[str] = set()
    for it in report["items"]:
        if _key(it) in seen:
            add("DUPLICATE_ITEM", "TE-12", "blocking",
                f"{it['merchant']} {money(it['amount'])} on {it['date']} appears twice on this report. Remove one.", it["item_id"])
        seen.add(_key(it))

    # The same charge still unreported on the card feed: a double charge to get reversed, not to claim.
    for it in report["items"]:
        for t in data["transactions"]:
            if t["transaction_id"] != it.get("transaction_id") and t["report_id"] is None and _key(t) == _key(it):
                add("DUPLICATE_CARD_CHARGE", "TE-12", "warning",
                    f"Your card was charged twice for {t['merchant']} {money(t['amount'])} on {t['date']} "
                    f"({t['transaction_id']} is the duplicate). Don't claim it twice; ask "
                    f"{data['finance_contact']['name']} in Finance Operations to have it reversed.", it["item_id"])

    if report["items"] and report["status"] == "Draft":
        last = max(date.fromisoformat(i["date"]) for i in report["items"])
        if (today - last).days > policy["submission_deadline_days"]:
            add("LATE_SUBMISSION", "TE-10", "warning", "This trip ended more than 30 days ago; submit as soon as possible.")

    blocking = [f for f in findings if f["severity"] == "blocking"]
    return {
        "report_id": report["report_id"],
        "can_submit": not blocking and bool(report["items"]),
        "blocking_issues": len(blocking),
        "warnings": sum(f["severity"] == "warning" for f in findings),
        "justified_exceptions": sum(f["severity"] == "exception-justified" for f in findings),
        "findings": findings,
    }


def policy_view(policy: dict, topic: str | None, city: str | None) -> dict:
    rules = policy["rules"] if not topic or topic == "all" else [r for r in policy["rules"] if r["topic"] == topic]
    out = {"policy": policy["name"], "version": policy["version"]}
    if city:
        out["hotel_nightly_cap_for_city"] = {"city": city, "cap_usd": cap_for(policy, city)}
    out["limits"] = {k: policy[k] for k in ("hotel_nightly_caps_usd", "default_hotel_nightly_cap_usd",
                                            "meals_per_day_usd", "client_entertainment_per_person_usd",
                                            "receipt_required_at_or_above_usd")}
    out["rules"] = rules
    return out


# --- Receipt matching and report changes --------------------------------------------------------------

_WORD = re.compile(r"[a-z0-9]{3,}")


def _tokens(text: str) -> set[str]:
    return set(_WORD.findall(text.lower()))


def _match(data: dict, inp: dict, claimed: set[str]) -> dict | None:
    pool = [t for t in data["transactions"] if t["report_id"] is None and t["transaction_id"] not in claimed]
    if inp.get("transaction_id"):
        tid = inp["transaction_id"].lower()
        return next((t for t in pool if t["transaction_id"].lower() == tid), None)
    if inp.get("amount") is None:
        return None
    candidates = [t for t in pool if abs(t["amount"] - inp["amount"]) < 0.011 and
                  (not inp.get("date") or abs((date.fromisoformat(t["date"]) - date.fromisoformat(inp["date"][:10])).days) <= 3)]
    if len(candidates) <= 1 or not inp.get("merchant"):
        return candidates[0] if candidates else None
    want = _tokens(inp["merchant"])
    return max(candidates, key=lambda t: len(_tokens(t["merchant"]) & want))


def add_items(data: dict, report: dict, inputs: list[dict]) -> tuple[list[dict], list[dict]]:
    added, skipped = [], []
    claimed = {i["transaction_id"] for i in report["items"] if i.get("transaction_id")}
    for inp in inputs:
        receipt = ({"attached": True, "source": inp.get("receipt_source", "email"), "reference": inp["receipt_reference"]}
                   if inp.get("receipt_reference") else None)
        tx = _match(data, inp, claimed)
        if inp.get("transaction_id") and tx is None:
            skipped.append({"input": inp, "reason": f"Card charge {inp['transaction_id']} was not found or is already on another report."})
            continue
        item_id = f"LI-{data['_next_item']}"
        if tx:
            claimed.add(tx["transaction_id"])
            tx["report_id"] = report["report_id"]
            item = {"item_id": item_id, "transaction_id": tx["transaction_id"], "date": tx["date"], "merchant": tx["merchant"],
                    "city": tx["city"], "category": tx["category"], "amount": tx["amount"]}
            people = inp.get("attendees") or tx.get("attendees")
            if people:
                item["attendees"] = people
            if "lodging_nights" in tx:
                item["lodging_nights"] = tx["lodging_nights"]
            if receipt:
                tx["receipt_on_file"] = True
            item["receipt"] = receipt or ({"attached": True, "source": "upload", "reference": f"receipt-{tx['transaction_id']}.pdf"}
                                          if tx["receipt_on_file"] else {"attached": False})
        elif all(inp.get(k) is not None for k in ("date", "merchant", "amount", "category")):
            item = {"item_id": item_id, "transaction_id": None, "date": inp["date"][:10], "merchant": inp["merchant"],
                    "city": inp.get("city", "Unknown"), "category": inp["category"], "amount": round2(inp["amount"]),
                    **({"attendees": inp["attendees"]} if inp.get("attendees") else {}),
                    "receipt": receipt or {"attached": False}}
        else:
            skipped.append({"input": inp, "reason": "No matching unreported card charge. To add an out-of-pocket expense, "
                                                    "provide date, merchant, amount and category."})
            continue
        if inp.get("notes"):
            item["notes"] = inp["notes"]
        elif item["transaction_id"] is None:
            item["notes"] = "Out-of-pocket expense (no matching card charge)."
        data["_next_item"] += 1
        report["items"].append(item)
        added.append(item)
    report["total"] = round2(sum(i["amount"] for i in report["items"]))
    return added, skipped


def create_report(data: dict, args: dict, today: date) -> tuple[dict, list[dict], list[dict]]:
    report = {
        "report_id": f"ER-{data['_next_report']}", "title": args["title"],
        "business_purpose": args.get("business_purpose", ""), "client": args.get("client"),
        "status": "Draft", "status_reason": None, "created_on": today.isoformat(), "submitted_on": None,
        "decided_on": None, "reimbursed_on": None, "approver": data["manager"]["name"], "justification": None,
        "note_to_approver": None, "items": [], "total": 0,
    }
    data["_next_report"] += 1
    data["reports"].append(report)
    added, skipped = add_items(data, report, args["items"])
    return report, added, skipped


def update_report(data: dict, report: dict, args: dict) -> dict:
    if report["status"] not in EDITABLE:
        raise ToolError(f"Report {report['report_id']} is {report['status']} and can't be edited.")
    removed = []
    for iid in args.get("remove_item_ids") or []:
        item = next((i for i in report["items"] if i["item_id"].lower() == iid.lower()), None)
        if item is None:
            continue
        report["items"].remove(item)
        tx = next((t for t in data["transactions"] if t["transaction_id"] == item.get("transaction_id")), None)
        if tx:
            tx["report_id"] = None
        removed.append(item["item_id"])
    attached = []
    for a in args.get("attach_receipts") or []:
        item = next((i for i in report["items"] if i["item_id"].lower() == a["item_id"].lower()), None)
        if item is None:
            continue
        item["receipt"] = {"attached": True, "source": "email", "reference": a["receipt_reference"]}
        tx = next((t for t in data["transactions"] if t["transaction_id"] == item.get("transaction_id")), None)
        if tx:
            tx["receipt_on_file"] = True
        attached.append(item["item_id"])
    for key in ("justification", "business_purpose", "title", "client"):
        if args.get(key) is not None:
            report[key] = args[key]
    added, skipped = add_items(data, report, args.get("add_items") or [])
    if report["status"] != "Draft":
        report["status"], report["status_reason"] = "Draft", None
    return {"removed": removed, "receipts_attached": attached, "added": added, "skipped": skipped}


def submit_report(data: dict, report: dict, note: str | None, today: date) -> dict:
    if report["status"] not in EDITABLE:
        return {"submitted": False, "message": f"Report {report['report_id']} is already {report['status']}.",
                "report": summarize(report)}
    check = check_report(data, report, today)
    if not check["can_submit"]:
        return {"submitted": False,
                "message": f"Report {report['report_id']} was NOT submitted: {check['blocking_issues']} blocking issue(s) "
                           "must be fixed first. Use update_expense_report to fix them, then submit again.",
                "policy_check": check}
    report.update(status="Pending approval", status_reason=None, submitted_on=today.isoformat(), note_to_approver=note)
    msg = f"Report {report['report_id']} ({money(report['total'])}) was submitted to {report['approver']} for approval."
    if check["justified_exceptions"]:
        msg += (f" It includes {check['justified_exceptions']} policy exception(s) with your justification for "
                f"{report['approver']} to approve.")
    return {"submitted": True, "message": msg, "report": summarize(report), "policy_check": check}


# --- Card feed and budget -----------------------------------------------------------------------------

def list_transactions(data: dict, args: dict) -> dict:
    status = args.get("status", "unreported")
    search = (args.get("search") or "").lower()
    rows = [t for t in data["transactions"]
            if (not args.get("start_date") or t["date"] >= args["start_date"])
            and (not args.get("end_date") or t["date"] <= args["end_date"])
            and (status == "all" or (t["report_id"] is None) == (status == "unreported"))
            and (not args.get("category") or t["category"] == args["category"])
            and (not search or search in f"{t['merchant']} {t['city']}".lower())]
    total = len(rows)
    rows = list(reversed(rows))[: args.get("limit", 50)]
    dups = duplicate_charges(data)
    return {
        "card": f"Corporate card ending {data['employee']['card_last_four']}",
        "filter": {**{k: v for k, v in args.items() if v is not None}, "status": status},
        "count": total,
        "returned": len(rows),
        "total_amount": round2(sum(t["amount"] for t in rows)),
        "transactions": [t | ({"possible_duplicate": True} if t["transaction_id"] in dups else {}) for t in rows],
    }


def spend_vs_budget(data: dict, now: datetime) -> dict:
    b = data["budget"]
    status = {r["report_id"]: r["status"] for r in data["reports"]}
    lines = {l["category"]: {"category": l["category"], "budget": l["budget"], "approved": 0.0,
                             "pending_approval": 0.0, "not_yet_submitted": 0.0} for l in b["lines"]}

    def add(category: str, amount: float, st: str | None) -> None:
        line = lines.get(BUDGET_LINE.get(category, ""))
        if line is None:
            return
        bucket = "approved" if st == "Approved" else "pending_approval" if st == "Pending approval" else "not_yet_submitted"
        line[bucket] += amount

    in_period = lambda d: b["period_start"] <= d <= b["period_end"]  # noqa: E731
    for t in data["transactions"]:
        if in_period(t["date"]):
            add(t["category"], t["amount"], status.get(t["report_id"]) if t["report_id"] else None)
    for r in data["reports"]:
        for i in r["items"]:
            if i.get("transaction_id") is None and in_period(i["date"]):
                add(i["category"], i["amount"], r["status"])

    out = []
    for l in lines.values():
        spent = round2(l["approved"] + l["pending_approval"] + l["not_yet_submitted"])
        out.append({**l, "approved": round2(l["approved"]), "pending_approval": round2(l["pending_approval"]),
                    "not_yet_submitted": round2(l["not_yet_submitted"]), "total_spent": spent,
                    "remaining": round2(l["budget"] - spent), "percent_used": round(spent / l["budget"] * 100)})
    budget = sum(l["budget"] for l in out)
    spent = round2(sum(l["total_spent"] for l in out))
    _, q_start, q_end = quarter_of(date.fromisoformat(b["period_start"]))
    days = (q_end - q_start).days + 1
    elapsed = min(days, max(0, (now.date() - q_start).days + 1))
    return {
        "owner": b["owner"], "period": b["period"], "period_start": b["period_start"], "period_end": b["period_end"],
        "percent_of_period_elapsed": round(elapsed / days * 100),
        "note": "Travel budget only. \"Not yet submitted\" includes card charges that are not on a submitted report yet.",
        "lines": out,
        "totals": {"budget": budget, "total_spent": spent, "remaining": round2(budget - spent),
                   "percent_used": round(spent / budget * 100)},
    }
