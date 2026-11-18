"""A JQL subset: enough for the queries an assistant writes against one Software project.

Fields: project, key/issuekey/id, sprint (id or name, plus openSprints(), closedSprints(), futureSprints()),
assignee, reporter (account ID, name, email, currentUser()), status, statusCategory, priority, labels,
type/issuetype, parent, resolution, created, updated, text, summary, description, comment.
Operators: = != ~ !~ > >= < <= IN, NOT IN, IS [NOT] EMPTY|NULL, AND, OR, NOT, parentheses and ORDER BY.

Like real Jira through the Atlassian MCP server, a query that can't be parsed or names an unknown field returns no
issues rather than an error.
"""

from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone
from typing import Any, Callable

from .store import Site


class JqlError(Exception):
    pass


TOKEN = re.compile(r"""
    \s*(?:
      (?P<str>"(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*')
    | (?P<op>!=|!~|>=|<=|=|~|>|<)
    | (?P<punct>[(),])
    | (?P<word>[^\s(),=!~<>"']+)
    )""", re.VERBOSE)

KEYWORDS = {"and", "or", "not", "in", "is", "empty", "null", "order", "by", "asc", "desc"}


def tokenize(text: str) -> list[tuple[str, str]]:
    tokens: list[tuple[str, str]] = []
    pos = 0
    text = text.strip()
    while pos < len(text):
        m = TOKEN.match(text, pos)
        if not m or m.end() == pos:
            raise JqlError(f"unexpected character at {pos}")
        pos = m.end()
        if m.group("str") is not None:
            raw = m.group("str")[1:-1]
            tokens.append(("str", re.sub(r"\\(.)", r"\1", raw)))
        elif m.group("op"):
            tokens.append(("op", m.group("op")))
        elif m.group("punct"):
            tokens.append(("punct", m.group("punct")))
        else:
            word = m.group("word")
            tokens.append(("kw", word.lower()) if word.lower() in KEYWORDS else ("word", word))
    return tokens


class Parser:
    def __init__(self, text: str) -> None:
        self.tokens = tokenize(text)
        self.i = 0

    def peek(self, offset: int = 0) -> tuple[str, str] | None:
        j = self.i + offset
        return self.tokens[j] if j < len(self.tokens) else None

    def take(self) -> tuple[str, str]:
        tok = self.peek()
        if tok is None:
            raise JqlError("unexpected end of query")
        self.i += 1
        return tok

    def accept(self, kind: str, value: str | None = None) -> bool:
        tok = self.peek()
        if tok and tok[0] == kind and (value is None or tok[1] == value):
            self.i += 1
            return True
        return False

    def parse(self) -> tuple[Any, list[tuple[str, bool]]]:
        expr = None
        if self.peek() and self.peek() != ("kw", "order"):
            expr = self.or_expr()
        order: list[tuple[str, bool]] = []
        if self.accept("kw", "order"):
            if not self.accept("kw", "by"):
                raise JqlError("expected BY")
            while True:
                kind, field = self.take()
                if kind not in ("word", "str"):
                    raise JqlError("expected an ORDER BY field")
                descending = False
                if self.accept("kw", "desc"):
                    descending = True
                else:
                    self.accept("kw", "asc")
                order.append((field.lower(), descending))
                if not self.accept("punct", ","):
                    break
        if self.peek() is not None:
            raise JqlError(f"unexpected token {self.peek()[1]!r}")
        return expr, order

    def or_expr(self) -> Any:
        node = self.and_expr()
        while self.accept("kw", "or"):
            node = ("or", node, self.and_expr())
        return node

    def and_expr(self) -> Any:
        node = self.not_expr()
        while self.accept("kw", "and"):
            node = ("and", node, self.not_expr())
        return node

    def not_expr(self) -> Any:
        if self.accept("kw", "not"):
            return ("not", self.not_expr())
        if self.accept("punct", "("):
            node = self.or_expr()
            if not self.accept("punct", ")"):
                raise JqlError("expected )")
            return node
        return self.clause()

    def clause(self) -> Any:
        kind, field = self.take()
        if kind not in ("word", "str"):
            raise JqlError("expected a field")
        tok = self.take()
        if tok == ("kw", "is"):
            negate = self.accept("kw", "not")
            if not (self.accept("kw", "empty") or self.accept("kw", "null")):
                raise JqlError("expected EMPTY")
            return ("clause", field.lower(), "is not" if negate else "is", None)
        if tok == ("kw", "not"):
            if not self.accept("kw", "in"):
                raise JqlError("expected IN")
            return ("clause", field.lower(), "not in", self.value_list())
        if tok == ("kw", "in"):
            return ("clause", field.lower(), "in", self.value_list())
        if tok[0] != "op":
            raise JqlError("expected an operator")
        return ("clause", field.lower(), tok[1], self.value())

    def value_list(self) -> list:
        if self.peek() and self.peek()[0] == "word" and self.peek(1) == ("punct", "("):
            return [self.value()]  # e.g. sprint in openSprints()
        if not self.accept("punct", "("):
            raise JqlError("expected (")
        values = [self.value()]
        while self.accept("punct", ","):
            values.append(self.value())
        if not self.accept("punct", ")"):
            raise JqlError("expected )")
        return values

    def value(self) -> Any:
        kind, text = self.take()
        if kind == "kw" and text in ("empty", "null"):
            return None
        if kind == "word" and self.accept("punct", "("):
            args = []
            if not self.accept("punct", ")"):
                args.append(self.take()[1])
                while self.accept("punct", ","):
                    args.append(self.take()[1])
                if not self.accept("punct", ")"):
                    raise JqlError("expected )")
            return ("fn", text.lower(), args)
        if kind in ("word", "str"):
            return text
        raise JqlError(f"unexpected {text!r}")


# --- evaluation ----------------------------------------------------------------------------------------------------

def _fold(value: Any) -> str:
    return str(value).strip().lower()


def parse_date(value: Any, now: datetime) -> datetime:
    if isinstance(value, tuple):
        _, name, args = value
        offset = timedelta()
        if args:
            offset = _relative(str(args[0]))
        if name == "now":
            return now + offset
        if name in ("startofday", "endofday"):
            base = now.replace(hour=0, minute=0, second=0, microsecond=0)
            base = base if name == "startofday" else base + timedelta(days=1)
            return base + offset
        if name in ("startofweek", "endofweek"):
            start = (now - timedelta(days=now.weekday() + 1 if now.weekday() != 6 else 0)).replace(
                hour=0, minute=0, second=0, microsecond=0)
            return (start if name == "startofweek" else start + timedelta(days=7)) + offset
        raise JqlError(f"unsupported function {name}()")
    text = str(value).strip()
    if re.fullmatch(r"[-+]?\d+[wdhm]", text):
        return now + _relative(text)
    for fmt in ("%Y-%m-%d %H:%M", "%Y/%m/%d %H:%M", "%Y-%m-%d", "%Y/%m/%d"):
        try:
            return datetime.strptime(text, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    raise JqlError(f"bad date {text!r}")


def _relative(text: str) -> timedelta:
    m = re.fullmatch(r"([-+]?)(\d+)([wdhm])", text.strip())
    if not m:
        raise JqlError(f"bad offset {text!r}")
    amount = int(m.group(2)) * (-1 if m.group(1) == "-" else 1)
    unit = {"w": "weeks", "d": "days", "h": "hours", "m": "minutes"}[m.group(3)]
    return timedelta(**{unit: amount})


def stamp(text: str) -> datetime:
    return datetime.strptime(text, "%Y-%m-%dT%H:%M:%S.%f%z")


class Evaluator:
    def __init__(self, site: Site, now: datetime) -> None:
        self.site = site
        self.now = now
        self.handlers: dict[str, Callable[[dict], Any]] = {
            "project": lambda i: [self.site.project["key"], self.site.project["id"], self.site.project["name"]],
            "key": lambda i: [i["key"], i["id"]],
            "issuekey": lambda i: [i["key"], i["id"]],
            "id": lambda i: [i["key"], i["id"]],
            "sprint": self.sprint_values,
            "assignee": lambda i: self.user_values(i.get("assignee")),
            "reporter": lambda i: self.user_values(i.get("reporter")),
            "status": lambda i: [i["status"], self.site.statuses[i["status"]]["id"]],
            "statuscategory": self.category_values,
            "priority": lambda i: [i["priority"], self.site.priorities[i["priority"]]["id"]] if i.get(
                "priority") else [],
            "labels": lambda i: list(i.get("labels", [])),
            "type": self.type_values,
            "issuetype": self.type_values,
            "parent": lambda i: [i["parent"], self.site.issue(i["parent"])["id"]] if self.site.issue(
                i.get("parent")) else [],
            "resolution": lambda i: [i["resolution"]] if i.get("resolution") else [],
        }

    def sprint_values(self, issue: dict) -> list:
        sprint = self.site.sprints.get(issue.get("sprint")) if issue.get("sprint") is not None else None
        return [str(sprint["id"]), sprint["name"], ("state", sprint["state"])] if sprint else []

    def category_values(self, issue: dict) -> list:
        from .render import CATEGORIES
        category = self.site.statuses[issue["status"]]["category"]
        c = CATEGORIES[category]
        return [c["name"], c["key"], str(category)]

    def type_values(self, issue: dict) -> list:
        t = self.site.types[issue["type"]]
        return [t["name"], t["id"]]

    def user_values(self, key: str | None) -> list:
        u = self.site.users.get(key or "")
        return [u["accountId"], u["displayName"], u["email"], u["key"]] if u else []

    def resolve_value(self, field: str, value: Any) -> list:
        """The literal(s) a clause value stands for, folded for comparison."""
        if isinstance(value, tuple):
            _, name, _args = value
            if name == "currentuser":
                return [_fold(self.site.current_user["accountId"])]
            if name in ("opensprints", "closedsprints", "futuresprints"):
                state = {"opensprints": "active", "closedsprints": "closed", "futuresprints": "future"}[name]
                return [("state", state)]
            if name == "membersof":
                return [_fold(u["accountId"]) for u in self.site.data["users"]]
            if name == "standardissuetypes":
                return [_fold(t["name"]) for t in self.site.data["issueTypes"] if not t["subtask"]]
            if name == "subtaskissuetypes":
                return [_fold(t["name"]) for t in self.site.data["issueTypes"] if t["subtask"]]
            raise JqlError(f"unsupported function {name}()")
        if field in ("assignee", "reporter"):
            u = self.site.user(str(value))
            return [_fold(u["accountId"])] if u else [_fold(value)]
        return [_fold(value)]

    def matches(self, node: Any, issue: dict) -> bool:
        kind = node[0]
        if kind == "and":
            return self.matches(node[1], issue) and self.matches(node[2], issue)
        if kind == "or":
            return self.matches(node[1], issue) or self.matches(node[2], issue)
        if kind == "not":
            return not self.matches(node[1], issue)
        _, field, op, value = node
        if field in ("text", "summary", "description", "comment"):
            return self.text_clause(field, op, value, issue)
        if field in ("created", "updated", "createddate", "updateddate"):
            return self.date_clause(field.replace("date", ""), op, value, issue)
        handler = self.handlers.get(field)
        if handler is None:
            raise JqlError(f"unknown field {field}")
        actual = handler(issue)
        folded = [a if isinstance(a, tuple) else _fold(a) for a in actual]
        if op == "is":
            return not actual
        if op == "is not":
            return bool(actual)
        if value is None:
            return (not actual) if op in ("=", "in") else bool(actual)
        values = value if isinstance(value, list) else [value]
        wanted = [w for v in values for w in self.resolve_value(field, v)]
        hit = any(w in folded for w in wanted)
        if op in ("=", "in"):
            return hit
        if op in ("!=", "not in"):
            return not hit
        if op in ("~", "!~"):
            found = any(isinstance(w, str) and any(isinstance(a, str) and w in a for a in folded) for w in wanted)
            return found if op == "~" else not found
        if op in (">", ">=", "<", "<=") and field in ("key", "issuekey", "id"):
            target = self.site.issue(str(values[0]))
            if target is None:
                return False
            a, b = int(issue["id"]), int(target["id"])
            return {">": a > b, ">=": a >= b, "<": a < b, "<=": a <= b}[op]
        if op in (">", ">=", "<", "<=") and field == "priority":
            target = self.site.priorities.get(str(values[0]).title())
            if target is None or not issue.get("priority"):
                return False
            # Higher priority means a lower id.
            a, b = -int(self.site.priorities[issue["priority"]]["id"]), -int(target["id"])
            return {">": a > b, ">=": a >= b, "<": a < b, "<=": a <= b}[op]
        raise JqlError(f"operator {op} not supported for {field}")

    def text_clause(self, field: str, op: str, value: Any, issue: dict) -> bool:
        if op in ("is", "is not"):
            present = bool(issue.get(field if field != "comment" else "comments"))
            return present if op == "is not" else not present
        if op not in ("~", "!~"):
            raise JqlError(f"operator {op} not supported for {field}")
        parts = {
            "summary": [issue["summary"]],
            "description": [issue.get("description") or ""],
            "comment": [c["body"] for c in issue.get("comments", [])],
        }
        haystack = " ".join(sum(parts.values(), []) if field == "text" else parts[field]).lower()
        terms = [t for t in re.findall(r"[\w-]+", str(value).lower().replace("*", "")) if t]
        found = bool(terms) and all(t in haystack for t in terms)
        return found if op == "~" else not found

    def date_clause(self, field: str, op: str, value: Any, issue: dict) -> bool:
        actual = stamp(issue[field])
        if op in ("is", "is not"):
            return op == "is not"
        target = parse_date(value, self.now)
        if op == "=":
            return actual.date() == target.date() if len(str(value)) <= 10 else actual == target
        if op == "!=":
            return actual != target
        return {">": actual > target, ">=": actual >= target, "<": actual < target, "<=": actual <= target}[op]


def sort_key(site: Site, field: str) -> Callable[[dict], Any]:
    if field in ("key", "issuekey", "id", "rank"):
        return lambda i: int(i["id"])
    if field in ("created", "updated"):
        return lambda i: i[field]
    if field == "priority":
        return lambda i: -int(site.priorities[i["priority"]]["id"]) if i.get("priority") else -99
    if field == "status":
        return lambda i: site.statuses[i["status"]]["id"]
    if field == "summary":
        return lambda i: i["summary"].lower()
    if field in ("assignee", "reporter"):
        return lambda i: (site.users[i[field]]["displayName"] if i.get(field) else "~")
    if field in ("type", "issuetype"):
        return lambda i: i["type"]
    raise JqlError(f"cannot order by {field}")


def search(site: Site, jql: str, now: datetime) -> list[dict]:
    """Issues matching ``jql`` in order. Raises JqlError for queries the mock (or Jira) can't run."""
    expr, order = Parser(jql or "").parse()
    evaluator = Evaluator(site, now)
    found = [i for i in site.data["issues"] if expr is None or evaluator.matches(expr, i)]
    if not order:
        order = [("key", True)]
    for field, descending in reversed(order):
        found.sort(key=sort_key(site, field), reverse=descending)
    return found
