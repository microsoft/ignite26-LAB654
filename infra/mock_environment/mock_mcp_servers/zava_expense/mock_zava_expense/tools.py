"""The Zava Expense tools. Reads are pure; writes go through the per-conversation store."""

from __future__ import annotations

from typing import Any

from mockmcp import READ_ONLY, CallContext, Tool

from . import logic, timeline
from .store import StateStore

WRITE = {"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False, "openWorldHint": False}

CATEGORY = {"type": "string", "enum": logic.CATEGORIES}
REPORT_ID = {"type": "string", "minLength": 1, "description": "Report ID, e.g. ER-1047."}
ITEM = {
    "type": "object",
    "properties": {
        "transaction_id": {"type": "string", "description": "ID of an unreported corporate card charge (e.g. TX-10123), from list_card_transactions."},
        "date": {"type": "string", "description": "Expense date, YYYY-MM-DD. Used to match the receipt to a card charge."},
        "merchant": {"type": "string", "description": "Merchant name as shown on the receipt."},
        "amount": {"type": "number", "description": "Total amount in USD as shown on the receipt."},
        "category": {**CATEGORY, "description": "Expense category. Required only for out-of-pocket expenses with no card charge."},
        "city": {"type": "string", "description": "City where the expense happened."},
        "attendees": {"type": "integer", "minimum": 1, "description": "Number of people at a client meal, including the employee."},
        "receipt_reference": {"type": "string", "description": "Where the receipt is, e.g. the subject line of the receipt email or a file name. Providing it attaches the receipt."},
        "receipt_source": {"type": "string", "enum": ["email", "upload"], "description": "Where the receipt came from. Defaults to email."},
        "notes": {"type": "string"},
    },
}


class ExpenseTool(Tool):
    def __init__(self, store: StateStore) -> None:
        self.store = store

    @staticmethod
    def today(ctx: CallContext):
        return timeline.today_et(ctx.clock.now)


class ListExpenseReports(ExpenseTool):
    name = "list_expense_reports"
    title = "List my expense reports"
    description = (
        "List the signed-in employee's expense reports in Zava Expense, Zava's in-house expense system, newest "
        "first. Shows status (Draft, Pending approval, Approved, Rejected, Returned), total, approver, and the reason a "
        "report was rejected or returned. Use it to answer \"what's still open\", \"what was rejected\" or \"has my "
        "report been approved\"."
    )
    input_schema = {
        "type": "object",
        "properties": {
            "status": {"type": "string", "enum": ["all", "open", "Draft", "Pending approval", "Approved", "Rejected", "Returned"],
                       "description": "Filter by status. \"open\" means Draft, Pending approval, Rejected or Returned. Defaults to all."},
            "limit": {"type": "integer", "minimum": 1, "maximum": 50, "description": "Maximum reports to return. Defaults to 20."},
        },
    }

    def run(self, args: dict, ctx: CallContext) -> Any:
        data = self.store.read(ctx.conversation_id)
        status = args.get("status", "all")
        rows = [r for r in reversed(data["reports"])
                if status == "all" or (r["status"] in logic.OPEN if status == "open" else r["status"] == status)]
        counts: dict[str, int] = {}
        for r in data["reports"]:
            counts[r["status"]] = counts.get(r["status"], 0) + 1
        return {"employee": data["employee"]["name"], "approver": data["manager"]["name"], "status_counts": counts,
                "count": min(len(rows), args.get("limit", 20)), "reports": [logic.summarize(r) for r in rows[: args.get("limit", 20)]]}


class GetExpenseReport(ExpenseTool):
    name = "get_expense_report"
    title = "Get an expense report"
    description = (
        "Get one Zava Expense report by ID (e.g. ER-1047), with every line item, receipts, status, approver and a "
        "travel-policy check. Use it to check whether a report has gone through and who needs to approve it."
    )
    input_schema = {"type": "object", "properties": {"report_id": REPORT_ID}, "required": ["report_id"]}

    def run(self, args: dict, ctx: CallContext) -> Any:
        data = self.store.read(ctx.conversation_id)
        report = logic.find_report(data, args["report_id"])
        return {"report": report, "policy_check": logic.check_report(data, report, self.today(ctx))}


class ListCardTransactions(ExpenseTool):
    name = "list_card_transactions"
    title = "List corporate card charges"
    description = (
        "List charges on the employee's Zava corporate card from Zava Expense. By default returns charges not "
        "yet on any expense report. Filter by date range to find the charges for a trip. Flags possible duplicate charges."
    )
    input_schema = {
        "type": "object",
        "properties": {
            "start_date": {"type": "string", "description": "Earliest charge date, YYYY-MM-DD."},
            "end_date": {"type": "string", "description": "Latest charge date, YYYY-MM-DD."},
            "status": {"type": "string", "enum": ["unreported", "reported", "all"], "description": "unreported (default) = not on any report yet."},
            "category": CATEGORY,
            "search": {"type": "string", "description": "Text to match in the merchant or city, e.g. \"Seattle\" or \"Uber\"."},
            "limit": {"type": "integer", "minimum": 1, "maximum": 200, "description": "Maximum charges to return, newest first. Defaults to 50."},
        },
    }

    def run(self, args: dict, ctx: CallContext) -> Any:
        return logic.list_transactions(self.store.read(ctx.conversation_id), args)


class GetTravelPolicy(ExpenseTool):
    name = "get_travel_policy"
    title = "Get Zava travel policy"
    description = (
        "Get Zava's travel and expense policy: hotel nightly caps by city, meal and client-entertainment limits, "
        "receipt rules, submission deadline and how to request an exception."
    )
    input_schema = {
        "type": "object",
        "properties": {
            "topic": {"type": "string", "enum": ["all", "lodging", "meals", "receipts", "airfare", "ground", "general"], "description": "Defaults to all."},
            "city": {"type": "string", "description": "Return the hotel nightly cap for this city."},
        },
    }

    def run(self, args: dict, ctx: CallContext) -> Any:
        return logic.policy_view(self.store.read(ctx.conversation_id)["policy"], args.get("topic"), args.get("city"))


class CheckExpenseReport(ExpenseTool):
    name = "check_expense_report"
    title = "Check a report against travel policy"
    description = (
        "Check a Zava Expense report against Zava's travel policy before submitting it. Returns blocking issues "
        "(e.g. a hotel night over the city cap, a missing receipt, a duplicate item), warnings, and whether the report "
        "can be submitted."
    )
    input_schema = {"type": "object", "properties": {"report_id": REPORT_ID}, "required": ["report_id"]}

    def run(self, args: dict, ctx: CallContext) -> Any:
        data = self.store.read(ctx.conversation_id)
        return logic.check_report(data, logic.find_report(data, args["report_id"]), self.today(ctx))


class GetSpendVsBudget(ExpenseTool):
    name = "get_spend_vs_budget"
    title = "Travel spend vs budget"
    description = (
        "Show the employee's travel spend for the current quarter against budget, by category (airfare, lodging, meals & "
        "entertainment, ground transport, training), split into approved, pending approval and not yet submitted."
    )
    input_schema = {"type": "object", "properties": {}}

    def run(self, args: dict, ctx: CallContext) -> Any:
        return logic.spend_vs_budget(self.store.read(ctx.conversation_id), ctx.clock.now)


class CreateExpenseReport(ExpenseTool):
    name = "create_expense_report"
    title = "Create an expense report"
    annotations = WRITE
    description = (
        "Create a draft expense report in Zava Expense. Add items either by card charge ID, or from receipts: pass "
        "each receipt's date, merchant and amount and the server matches it to the corporate card charge. Pass the "
        "receipt email subject as receipt_reference to attach the receipt. Returns the draft and a travel-policy check. "
        "Does not submit; use submit_expense_report for that."
    )
    input_schema = {
        "type": "object",
        "properties": {
            "title": {"type": "string", "minLength": 1, "description": "Report title, e.g. \"Seattle — Fabrikam, Inc. partnership review\"."},
            "business_purpose": {"type": "string", "description": "Why the expenses were incurred. Required before submitting."},
            "client": {"type": "string", "description": "Client the trip was for, if any."},
            "items": {"type": "array", "minItems": 1, "items": ITEM, "description": "Expenses to add."},
        },
        "required": ["title", "items"],
    }

    def run(self, args: dict, ctx: CallContext) -> Any:
        with self.store.write(ctx.conversation_id) as data:
            report, added, skipped = logic.create_report(data, args, self.today(ctx))
            check = logic.check_report(data, report, self.today(ctx))
        msg = f"Draft {report['report_id']} created with {len(added)} item(s), total {logic.money(report['total'])}."
        if skipped:
            msg += f" {len(skipped)} item(s) were not added."
        return {"message": msg, "report": report, "skipped": skipped, "policy_check": check}


class UpdateExpenseReport(ExpenseTool):
    name = "update_expense_report"
    title = "Update an expense report"
    annotations = WRITE
    description = (
        "Update a Draft, Returned or Rejected Zava Expense report: add or remove items, attach receipts, set the "
        "business purpose, or add a justification for a policy exception (e.g. a hotel night over the cap). Returns the "
        "updated report and a policy check."
    )
    input_schema = {
        "type": "object",
        "properties": {
            "report_id": REPORT_ID,
            "add_items": {"type": "array", "items": ITEM},
            "remove_item_ids": {"type": "array", "items": {"type": "string"}, "description": "Line item IDs to remove, e.g. [\"LI-212\"]."},
            "attach_receipts": {"type": "array", "items": {"type": "object", "properties": {
                "item_id": {"type": "string"}, "receipt_reference": {"type": "string"}}, "required": ["item_id", "receipt_reference"]}},
            "justification": {"type": "string", "description": "Why a policy exception is needed. Your manager sees it when approving."},
            "business_purpose": {"type": "string"},
            "title": {"type": "string"},
            "client": {"type": "string"},
        },
        "required": ["report_id"],
    }

    def run(self, args: dict, ctx: CallContext) -> Any:
        with self.store.write(ctx.conversation_id) as data:
            report = logic.find_report(data, args["report_id"])
            changes = logic.update_report(data, report, args)
            check = logic.check_report(data, report, self.today(ctx))
        return {"message": f"Report {report['report_id']} updated. Total {logic.money(report['total'])}.",
                "changes": changes, "report": report, "policy_check": check}


class SubmitExpenseReport(ExpenseTool):
    name = "submit_expense_report"
    title = "Submit an expense report"
    annotations = WRITE
    description = (
        "Submit a Zava Expense report to the employee's manager for approval. Runs the travel-policy check first and "
        "refuses to submit if there are blocking issues, explaining what to fix. Confirm with the user before calling this."
    )
    input_schema = {
        "type": "object",
        "properties": {
            "report_id": REPORT_ID,
            "note_to_approver": {"type": "string", "description": "Optional note for the approver."},
        },
        "required": ["report_id"],
    }

    def run(self, args: dict, ctx: CallContext) -> Any:
        with self.store.write(ctx.conversation_id) as data:
            report = logic.find_report(data, args["report_id"])
            return logic.submit_report(data, report, args.get("note_to_approver"), self.today(ctx))


TOOLS = (ListExpenseReports, GetExpenseReport, ListCardTransactions, GetTravelPolicy, CheckExpenseReport,
         GetSpendVsBudget, CreateExpenseReport, UpdateExpenseReport, SubmitExpenseReport)
