"""SOQL and SOSL over the mock org, returning the REST API's result shapes.

Covers what agents send in practice: field lists with parent paths and child subqueries, ``FIELDS(...)``, WHERE with
AND/OR/NOT, comparison operators, LIKE, IN/NOT IN (including semi-joins), INCLUDES, null checks, date and datetime
values and date literals, GROUP BY with COUNT/COUNT_DISTINCT/SUM/AVG/MIN/MAX (aliased or ``exprN``), ORDER BY with
NULLS FIRST/LAST, LIMIT/OFFSET and USING SCOPE mine. Errors carry the API's code and its row/column caret message.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field as dc_field
from typing import Any

from . import engine
from .engine import Ctx, DateRange, QueryError
from .schema import OBJECTS, SEARCHABLE, child_relationship, find_field, find_object, parent_relationship
from .timeutil import soql_datetime


class SoqlError(Exception):
    def __init__(self, message: str, code: str = "MALFORMED_QUERY", pos: int | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.pos = pos

    def render(self, text: str) -> str:
        """The API's message: a snippet of the query, a caret, the row/column and the reason."""
        if self.pos is None:
            return str(self)
        start = max(0, self.pos - 30)
        if start:
            space = text.rfind(" ", 0, start + 1)
            start = space + 1 if space >= 0 and self.pos - space < 45 else start
        end = text.find(" ", self.pos + 30)
        snippet = text[start:end if end > 0 else len(text)]
        return f"\n{snippet}\n{' ' * (self.pos - start)}^\nERROR at Row:1:Column:{self.pos + 1}\n{self}"


_UNKNOWN_FIELD = ("No such column '{0}' on entity '{1}'. If you are attempting to use a custom field, be sure to "
                  "append the '__c' after the custom field name. Please reference your WSDL or the describe call for "
                  "the appropriate names.")
_UNKNOWN_TYPE = ("sObject type '{0}' is not supported. If you are attempting to use a custom object, be sure to "
                 "append the '__c' after the entity name. Please reference your WSDL or the describe call for the "
                 "appropriate names.")
_UNKNOWN_REL = ("Didn't understand relationship '{0}' in field path. If you are attempting to use a custom "
                "relationship, be sure to append the '__r' after the custom relationship name. Please reference your "
                "WSDL or the describe call for the appropriate names.")

# --- tokenizer ----------------------------------------------------------------------------------------------------

_TOKEN = re.compile(r"""
    (?P<ws>\s+)
  | (?P<datetime>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2}))
  | (?P<date>\d{4}-\d{2}-\d{2})
  | (?P<number>-?\d+(?:\.\d+)?)
  | (?P<string>'(?:\\.|[^'\\])*')
  | (?P<ident>[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*)
  | (?P<op><=|>=|!=|<>|=|<|>)
  | (?P<punct>[(),:])
""", re.VERBOSE)


@dataclass
class Tok:
    kind: str
    text: str
    pos: int

    @property
    def upper(self) -> str:
        return self.text.upper()


def tokenize(text: str) -> list[Tok]:
    out, pos = [], 0
    while pos < len(text):
        match = _TOKEN.match(text, pos)
        if not match:
            raise SoqlError(f"unexpected token: '{text[pos]}'", "MALFORMED_QUERY", pos)
        if match.lastgroup != "ws":
            out.append(Tok(match.lastgroup, match.group(), pos))
        pos = match.end()
    out.append(Tok("eof", "", len(text)))
    return out


def _unquote(text: str) -> str:
    body = text[1:-1]
    return re.sub(r"\\(.)", lambda m: {"n": "\n", "t": "\t", "r": "\r"}.get(m.group(1), m.group(1)), body)


# --- AST ----------------------------------------------------------------------------------------------------------

@dataclass
class Item:
    kind: str                       # field | agg | sub
    path: str = ""
    func: str | None = None
    alias: str | None = None
    sub: "Query | None" = None
    pos: int = 0


@dataclass
class Cond:
    path: str
    op: str
    value: Any
    pos: int
    func: str | None = None         # aggregate in HAVING


@dataclass
class BoolExpr:
    op: str                         # and | or | not
    parts: list


@dataclass
class Order:
    path: str
    desc: bool
    nulls_first: bool | None
    func: str | None = None


@dataclass
class Query:
    obj: str
    items: list[Item]
    where: Any = None
    group_by: list[str] = dc_field(default_factory=list)
    having: Any = None
    order: list[Order] = dc_field(default_factory=list)
    limit: int | None = None
    offset: int = 0
    mine: bool = False
    obj_pos: int = 0
    rel: str | None = None          # child relationship name for subqueries


@dataclass
class SemiJoin:
    query: Query


@dataclass
class Literal:
    name: str
    n: int | None


_AGGS = {"COUNT", "COUNT_DISTINCT", "SUM", "AVG", "MIN", "MAX"}
_DATE_LITERALS = {
    "TODAY", "YESTERDAY", "TOMORROW", "THIS_WEEK", "LAST_WEEK", "NEXT_WEEK", "THIS_MONTH", "LAST_MONTH", "NEXT_MONTH",
    "THIS_QUARTER", "LAST_QUARTER", "NEXT_QUARTER", "THIS_YEAR", "LAST_YEAR", "NEXT_YEAR", "LAST_90_DAYS",
    "NEXT_90_DAYS", "THIS_FISCAL_QUARTER", "THIS_FISCAL_YEAR",
}
_N_LITERALS = {"LAST_N_DAYS", "NEXT_N_DAYS", "N_DAYS_AGO", "LAST_N_WEEKS", "NEXT_N_WEEKS", "LAST_N_MONTHS",
               "NEXT_N_MONTHS"}
_CLAUSES = {"FROM", "WHERE", "GROUP", "HAVING", "ORDER", "LIMIT", "OFFSET", "USING", "WITH", "FOR"}


class Parser:
    def __init__(self, text: str) -> None:
        self.text = text
        self.toks = tokenize(text)
        self.i = 0

    @property
    def tok(self) -> Tok:
        return self.toks[self.i]

    def take(self) -> Tok:
        tok = self.toks[self.i]
        self.i += 1
        return tok

    def is_kw(self, *words: str) -> bool:
        return self.tok.kind == "ident" and self.tok.upper in words

    def expect_kw(self, word: str) -> Tok:
        if not self.is_kw(word):
            self.fail(f"expecting '{word}'" if self.tok.kind != "eof" else f"unexpected token: <EOF>")
        return self.take()

    def expect(self, text: str) -> Tok:
        if self.tok.text != text:
            self.fail(f"unexpected token: '{self.tok.text or '<EOF>'}'")
        return self.take()

    def fail(self, message: str, code: str = "MALFORMED_QUERY", tok: Tok | None = None) -> None:
        raise SoqlError(message, code, (tok or self.tok).pos)

    # SELECT … FROM … ---------------------------------------------------------------------------------------------

    def query(self, nested: bool = False) -> Query:
        self.expect_kw("SELECT")
        items = self.select_list()
        self.expect_kw("FROM")
        obj_tok = self.take()
        if obj_tok.kind != "ident":
            self.fail(f"unexpected token: '{obj_tok.text}'", tok=obj_tok)
        q = Query(obj=obj_tok.text, items=items, obj_pos=obj_tok.pos)
        if self.is_kw("USING"):
            self.take()
            self.expect_kw("SCOPE")
            q.mine = self.take().upper == "MINE"
        if self.is_kw("WHERE"):
            self.take()
            q.where = self.expr()
        if self.is_kw("WITH"):
            self.take()
            self.take()
        if self.is_kw("GROUP"):
            self.take()
            self.expect_kw("BY")
            q.group_by.append(self.take().text)
            while self.tok.text == ",":
                self.take()
                q.group_by.append(self.take().text)
        if self.is_kw("HAVING"):
            self.take()
            q.having = self.expr()
        if self.is_kw("ORDER"):
            self.take()
            self.expect_kw("BY")
            q.order.append(self.order_item())
            while self.tok.text == ",":
                self.take()
                q.order.append(self.order_item())
        if self.is_kw("LIMIT"):
            self.take()
            q.limit = int(self.number())
        if self.is_kw("OFFSET"):
            self.take()
            q.offset = int(self.number())
        if self.is_kw("FOR"):
            self.take()
            self.take()
        if not nested and self.tok.kind != "eof":
            self.fail(f"unexpected token: '{self.tok.text}'")
        return q

    def number(self) -> float:
        tok = self.take()
        if tok.kind != "number":
            self.fail(f"unexpected token: '{tok.text}'", tok=tok)
        return float(tok.text)

    def select_list(self) -> list[Item]:
        items = [self.select_item()]
        while self.tok.text == ",":
            self.take()
            items.append(self.select_item())
        return items

    def select_item(self) -> Item:
        tok = self.tok
        if tok.text == "(":
            self.take()
            sub = self.query(nested=True)
            self.expect(")")
            return Item("sub", path=sub.obj, sub=sub, pos=tok.pos)
        if tok.kind != "ident":
            self.fail(f"unexpected token: '{tok.text or '<EOF>'}'")
        self.take()
        if self.tok.text == "(" and (tok.upper in _AGGS or tok.upper in ("FIELDS", "FORMAT", "TOLABEL",
                                                                           "CONVERTCURRENCY")):
            self.take()
            inner = "" if self.tok.text == ")" else self.take().text
            self.expect(")")
            alias = None
            if self.tok.kind == "ident" and self.tok.upper not in _CLAUSES:
                alias = self.take().text
            if tok.upper == "FIELDS":
                return Item("fields", path=inner.upper(), pos=tok.pos)
            if tok.upper in ("FORMAT", "TOLABEL", "CONVERTCURRENCY"):
                return Item("field", path=inner, alias=alias, pos=tok.pos)
            return Item("agg", path=inner, func=tok.upper, alias=alias, pos=tok.pos)
        alias = None
        if self.tok.kind == "ident" and self.tok.upper not in _CLAUSES:
            alias = self.take().text
        return Item("field", path=tok.text, alias=alias, pos=tok.pos)

    def order_item(self) -> Order:
        tok = self.take()
        func = None
        path = tok.text
        if self.tok.text == "(" and tok.upper in _AGGS:
            self.take()
            path = "" if self.tok.text == ")" else self.take().text
            self.expect(")")
            func = tok.upper
        desc, nulls = False, None
        if self.is_kw("ASC", "DESC"):
            desc = self.take().upper == "DESC"
        if self.is_kw("NULLS"):
            self.take()
            nulls = self.take().upper == "FIRST"
        return Order(path, desc, nulls, func)

    # WHERE ---------------------------------------------------------------------------------------------------------

    def expr(self) -> Any:
        left = self.term()
        parts = [left]
        while self.is_kw("OR"):
            self.take()
            parts.append(self.term())
        return parts[0] if len(parts) == 1 else BoolExpr("or", parts)

    def term(self) -> Any:
        parts = [self.factor()]
        while self.is_kw("AND"):
            self.take()
            parts.append(self.factor())
        return parts[0] if len(parts) == 1 else BoolExpr("and", parts)

    def factor(self) -> Any:
        if self.is_kw("NOT"):
            self.take()
            return BoolExpr("not", [self.factor()])
        if self.tok.text == "(":
            self.take()
            inner = self.expr()
            self.expect(")")
            return inner
        return self.condition()

    def condition(self) -> Cond:
        tok = self.take()
        if tok.kind != "ident":
            self.fail(f"unexpected token: '{tok.text or '<EOF>'}'", tok=tok)
        func = None
        path = tok.text
        if self.tok.text == "(" and tok.upper in _AGGS:
            self.take()
            path = "" if self.tok.text == ")" else self.take().text
            self.expect(")")
            func = tok.upper
        op_tok = self.tok
        if op_tok.kind == "op":
            self.take()
            op = {"=": "eq", "!=": "ne", "<>": "ne", "<": "lt", "<=": "lte", ">": "gt", ">=": "gte"}[op_tok.text]
            return Cond(path, op, self.value(), tok.pos, func)
        if self.is_kw("LIKE"):
            self.take()
            return Cond(path, "like", self.value(), tok.pos, func)
        if self.is_kw("IN", "INCLUDES", "EXCLUDES"):
            op = {"IN": "in", "INCLUDES": "includes", "EXCLUDES": "excludes"}[self.take().upper]
            return Cond(path, op, self.list_value(), tok.pos, func)
        if self.is_kw("NOT"):
            self.take()
            self.expect_kw("IN")
            return Cond(path, "nin", self.list_value(), tok.pos, func)
        self.fail(f"unexpected token: '{op_tok.text or '<EOF>'}'", tok=op_tok)
        raise AssertionError

    def list_value(self) -> Any:
        self.expect("(")
        if self.is_kw("SELECT"):
            sub = self.query(nested=True)
            self.expect(")")
            return SemiJoin(sub)
        values = [self.value()]
        while self.tok.text == ",":
            self.take()
            values.append(self.value())
        self.expect(")")
        return values

    def value(self) -> Any:
        tok = self.take()
        if tok.kind == "string":
            return _unquote(tok.text)
        if tok.kind == "number":
            return float(tok.text)
        if tok.kind in ("date", "datetime"):
            return (tok.kind, tok.text)
        if tok.kind == "ident":
            word = tok.upper
            if word == "NULL":
                return None
            if word in ("TRUE", "FALSE"):
                return word == "TRUE"
            if word in _DATE_LITERALS:
                return Literal(word, None)
            if word in _N_LITERALS:
                self.expect(":")
                return Literal(word, int(self.number()))
            self.fail(f"line 1:{tok.pos} no viable alternative at character ' '", tok=tok)
        self.fail(f"unexpected token: '{tok.text or '<EOF>'}'", tok=tok)
        raise AssertionError


# --- execution ----------------------------------------------------------------------------------------------------

_POLYMORPHIC = {"Who", "What"}
_ACTIVITIES = {"Task", "Event", "ActivityHistory", "OpenActivity"}


def _resolve_object(name: str, pos: int) -> str:
    obj = find_object(name)
    if obj is None:
        raise SoqlError(_UNKNOWN_TYPE.format(name), "INVALID_TYPE", pos)
    return obj


def _check_path(obj: str, path: str, pos: int) -> tuple[str, str]:
    """Validate a dotted path; returns (final object, final field API name)."""
    parts = path.split(".")
    if len(parts) > 1 and find_object(parts[0]) == obj:
        parts = parts[1:]
    current = obj
    for rel in parts[:-1]:
        hit = parent_relationship(current, rel, case_insensitive=True)
        if not hit:
            raise SoqlError(_UNKNOWN_REL.format(rel), "INVALID_FIELD", pos)
        current = hit[2][0]
    meta = find_field(current, parts[-1])
    if meta is None:
        raise SoqlError(_UNKNOWN_FIELD.format(parts[-1], current), "INVALID_FIELD", pos)
    return current, meta[0]


def _strip_obj(obj: str, path: str) -> str:
    parts = path.split(".")
    return ".".join(parts[1:]) if len(parts) > 1 and find_object(parts[0]) == obj else path


def _coerce_value(ctx: Ctx, obj: str, cond: Cond, raw: Any) -> Any:
    dtype = engine.field_type(obj, cond.path) if not cond.func else None
    name = cond.path.split(".")[-1]
    if isinstance(raw, Literal):
        if dtype not in ("DATE", "DATETIME"):
            raise SoqlError(f"value of filter criterion for field '{name}' must be of type "
                            f"{(dtype or 'string').lower()} and should be enclosed in quotes", "INVALID_FIELD",
                            cond.pos)
        start, end = engine.literal_range(ctx, raw.name, raw.n)
        return DateRange(start, end)
    if isinstance(raw, tuple):
        kind, text = raw
        if dtype == "DATETIME" and kind == "date":
            raise SoqlError(f"value of filter criterion for field '{name}' must be of type dateTime and should "
                            "not be enclosed in quotes", "INVALID_FIELD", cond.pos)
        if dtype == "DATE" and kind == "datetime":
            raise SoqlError(f"value of filter criterion for field '{name}' must be of type date and should not "
                            "be enclosed in quotes", "INVALID_FIELD", cond.pos)
        return text
    if isinstance(raw, str) and dtype in ("DATE", "DATETIME", "BOOLEAN", "INT", "DOUBLE", "CURRENCY", "PERCENT"):
        kind = {"DATETIME": "dateTime", "INT": "double", "CURRENCY": "double", "PERCENT": "double"}.get(
            dtype, dtype.lower())
        raise SoqlError(f"value of filter criterion for field '{name}' must be of type {kind} and should not be "
                        "enclosed in quotes", "INVALID_FIELD", cond.pos)
    return raw


def _validate_where(ctx: Ctx, obj: str, node: Any) -> None:
    if node is None:
        return
    if isinstance(node, BoolExpr):
        for part in node.parts:
            _validate_where(ctx, obj, part)
        return
    if node.func:
        return
    _check_path(obj, node.path, node.pos)
    node.path = _strip_obj(obj, node.path)
    values = node.value if isinstance(node.value, list) else [node.value]
    if isinstance(node.value, SemiJoin):
        sub = node.value.query
        sub.obj = _resolve_object(sub.obj, sub.obj_pos)
        if len(sub.items) != 1 or sub.items[0].kind != "field":
            raise SoqlError("The selected field in a semi join subquery must be a single Id or reference field",
                            "MALFORMED_QUERY", node.pos)
        _check_path(sub.obj, sub.items[0].path, sub.items[0].pos)
        _validate_where(ctx, sub.obj, sub.where)
        return
    node.value = [_coerce_value(ctx, obj, node, v) for v in values] if isinstance(node.value, list) \
        else _coerce_value(ctx, obj, node, node.value)


def _match(ctx: Ctx, obj: str, rec: dict, node: Any) -> bool:
    if node is None:
        return True
    if isinstance(node, BoolExpr):
        if node.op == "and":
            return all(_match(ctx, obj, rec, p) for p in node.parts)
        if node.op == "or":
            return any(_match(ctx, obj, rec, p) for p in node.parts)
        return not _match(ctx, obj, rec, node.parts[0])
    actual = engine.path_value(ctx, obj, rec, node.path)
    dtype = engine.field_type(obj, node.path)
    expected = node.value
    if isinstance(expected, SemiJoin):
        sub = expected.query
        ids = [engine.path_value(ctx, sub.obj, r, sub.items[0].path) for r in _filtered(ctx, sub)]
        expected = ids
    if node.op == "excludes":
        return not engine.compare("includes", actual, expected, dtype)
    if dtype in ("ID", "REFERENCE") and actual:
        actual = actual[:15] if any(isinstance(v, str) and len(v) == 15 for v in
                                    (expected if isinstance(expected, list) else [expected])) else actual
    return engine.compare(node.op, actual, expected, dtype)


def _filtered(ctx: Ctx, q: Query, base: list[dict] | None = None) -> list[dict]:
    out = []
    for rec in base if base is not None else engine.rows(ctx, q.obj):
        if q.mine and rec.get("OwnerId") != ctx.org.current_user_id:
            continue
        if _match(ctx, q.obj, rec, q.where):
            out.append(rec)
    return out


def _attributes(obj: str, rec: dict, version: str, type_name: str | None = None) -> dict:
    return {"type": type_name or obj, "url": f"/services/data/{version}/sobjects/{obj}/{rec['Id']}"}


def _format(dtype: str | None, raw: Any) -> Any:
    if raw is None:
        return None
    if dtype == "DATETIME":
        return soql_datetime(raw)
    if dtype in ("CURRENCY", "DOUBLE", "PERCENT"):
        return float(raw)
    if dtype == "INT":
        return int(raw)
    return raw


def _expand(obj: str, items: list[Item]) -> list[Item]:
    out: list[Item] = []
    for item in items:
        if item.kind == "fields":
            out.extend(Item("field", path=f[0]) for f in OBJECTS[obj]["fields"])
        else:
            out.append(item)
    return out


def _put(ctx: Ctx, obj: str, rec: dict, path: str, target: dict, version: str) -> None:
    parts = path.split(".")
    current_obj, current = obj, rec
    node = target
    for rel in parts[:-1]:
        hit = engine.parent_relationship(current_obj, rel, case_insensitive=True)
        rel_name = hit[1]
        parent = engine.follow(ctx, current_obj, current, rel_name)
        if parent is None:
            node[rel_name] = None
            return
        polymorphic = rel_name in _POLYMORPHIC or (rel_name == "Owner" and current_obj in _ACTIVITIES)
        existing = node.get(rel_name)
        if not isinstance(existing, dict):
            existing = {"attributes": _attributes(parent[0], parent[1], version, "Name" if polymorphic else None)}
            node[rel_name] = existing
        node = existing
        current_obj, current = parent
    meta = find_field(current_obj, parts[-1])
    node[meta[0]] = _format(meta[2], engine.value(ctx, current_obj, current, meta[0]))


def _record(ctx: Ctx, q: Query, rec: dict, version: str) -> dict:
    out: dict = {"attributes": _attributes(q.obj, rec, version)}
    for item in q.items:
        if item.kind == "field":
            _put(ctx, q.obj, rec, item.path, out, version)
        elif item.kind == "sub":
            sub = item.sub
            rel_name = sub.rel
            child_obj, kids = engine.children(ctx, q.obj, rec, rel_name)
            sub_q = Query(obj=child_obj, items=sub.items, where=sub.where, order=sub.order, limit=sub.limit,
                          offset=sub.offset)
            matched = _ordered(ctx, sub_q, _filtered(ctx, sub_q, kids))
            matched = matched[sub_q.offset:]
            if sub_q.limit is not None:
                matched = matched[:sub_q.limit]
            out[rel_name] = {"totalSize": len(matched), "done": True,
                             "records": [_record(ctx, sub_q, r, version) for r in matched]} if matched else None
    return out


def _ordered(ctx: Ctx, q: Query, items: list[dict]) -> list[dict]:
    if not q.order:
        return items
    return engine.sort_rows(ctx, q.obj, items, [(o.path, o.desc, o.nulls_first) for o in q.order])


def _validate(ctx: Ctx, q: Query, child_of: str | None = None) -> None:
    if child_of:
        hit = child_relationship(child_of, q.obj, case_insensitive=True)
        if hit is None:
            raise SoqlError(_UNKNOWN_REL.format(q.obj).replace("in field path", "in FROM part of query call"),
                            "INVALID_TYPE", q.obj_pos)
        q.obj, q.rel = hit[0], hit[1]
    else:
        q.obj = _resolve_object(q.obj, q.obj_pos)
        if OBJECTS[q.obj].get("virtual"):
            raise SoqlError(f"entity type {q.obj} does not support query", "INVALID_TYPE_FOR_OPERATION", q.obj_pos)
    q.items = _expand(q.obj, q.items)
    for item in q.items:
        if item.kind == "field":
            _check_path(q.obj, item.path, item.pos)
            item.path = _strip_obj(q.obj, item.path)
        elif item.kind == "agg":
            if item.path:
                _check_path(q.obj, item.path, item.pos)
                item.path = _strip_obj(q.obj, item.path)
        elif item.kind == "sub":
            if child_of:
                raise SoqlError("Nesting of child relationship queries is not supported", "MALFORMED_QUERY",
                                item.pos)
            _validate(ctx, item.sub, q.obj)
    _validate_where(ctx, q.obj, q.where)
    for path in q.group_by:
        _check_path(q.obj, path, q.obj_pos)
    q.group_by = [_strip_obj(q.obj, p) for p in q.group_by]
    for order in q.order:
        if not order.func:
            _check_path(q.obj, order.path, q.obj_pos)
            order.path = _strip_obj(q.obj, order.path)


def _aggregate(ctx: Ctx, q: Query, matched: list[dict]) -> list[dict]:
    has_agg = any(i.kind == "agg" for i in q.items)
    for item in q.items:
        if item.kind == "field" and not has_agg and not q.group_by:
            continue
        if item.kind == "field" and item.path not in q.group_by:
            raise SoqlError(f"Field must be grouped or aggregated: {item.path.split('.')[-1]}", "MALFORMED_QUERY",
                            item.pos)
    groups: dict[tuple, list[dict]] = {}
    for rec in matched:
        key = tuple(engine.path_value(ctx, q.obj, rec, p) for p in q.group_by)
        groups.setdefault(key, []).append(rec)
    if not q.group_by and not groups:
        groups[()] = []
    results = []
    for key, members in groups.items():
        row: dict = {"attributes": {"type": "AggregateResult"}}
        expr = 0
        for item in q.items:
            if item.kind == "field":
                name = item.alias or item.path.split(".")[-1]
                dtype = engine.field_type(q.obj, item.path)
                row[name] = _format(dtype, key[q.group_by.index(item.path)])
                continue
            name = item.alias or f"expr{expr}"
            if not item.alias:
                expr += 1
            row[name] = _agg_value(ctx, q.obj, item.func, item.path, members)
        if q.having is not None and not _having(ctx, q, members, q.having):
            continue
        results.append(row)
    for order in reversed(q.order):
        def sort_key(row: dict, order: Order = order) -> Any:
            if order.func:
                match = next((i for i in q.items if i.kind == "agg" and i.func == order.func and
                              i.path.lower() == order.path.lower()), None)
                name = (match.alias or f"expr{[i for i in q.items if i.kind == 'agg'].index(match)}") if match \
                    else None
                return row.get(name)
            return row.get(order.path.split(".")[-1])
        present = [r for r in results if sort_key(r) is not None]
        missing = [r for r in results if sort_key(r) is None]
        present.sort(key=sort_key, reverse=order.desc)
        nulls_first = (not order.desc) if order.nulls_first is None else order.nulls_first
        results = missing + present if nulls_first else present + missing
    return results


def _agg_value(ctx: Ctx, obj: str, func: str, path: str, members: list[dict]) -> Any:
    if func == "COUNT":
        if not path:
            return len(members)
        return sum(1 for r in members if engine.path_value(ctx, obj, r, path) is not None)
    values = [engine.path_value(ctx, obj, r, path) for r in members]
    values = [v for v in values if v is not None]
    if func == "COUNT_DISTINCT":
        return len(set(values))
    if not values:
        return None
    dtype = engine.field_type(obj, path)
    if func == "SUM":
        return float(sum(values))
    if func == "AVG":
        return float(sum(values)) / len(values)
    return _format(dtype, (min if func == "MIN" else max)(values))


def _having(ctx: Ctx, q: Query, members: list[dict], node: Any) -> bool:
    if isinstance(node, BoolExpr):
        results = [_having(ctx, q, members, p) for p in node.parts]
        return all(results) if node.op == "and" else any(results) if node.op == "or" else not results[0]
    if node.func:
        actual = _agg_value(ctx, q.obj, node.func, node.path, members)
        return engine.compare(node.op, actual, node.value, "DOUBLE")
    actual = engine.path_value(ctx, q.obj, members[0], node.path) if members else None
    return engine.compare(node.op, actual, node.value, engine.field_type(q.obj, node.path))


def query(ctx: Ctx, text: str, version: str = "v63.0") -> dict:
    """Run a SOQL query; returns the REST body ``{totalSize, done, records}``. Raises SoqlError."""
    q = Parser(text).query()
    try:
        _validate(ctx, q)
        matched = _filtered(ctx, q)
        is_count = len(q.items) == 1 and q.items[0].kind == "agg" and q.items[0].func == "COUNT" \
            and not q.items[0].path and not q.group_by
        if is_count:
            return {"totalSize": len(matched), "done": True, "records": []}
        if any(i.kind == "agg" for i in q.items) or q.group_by:
            records = _aggregate(ctx, q, matched)
        else:
            ordered = _ordered(ctx, q, matched)[q.offset:]
            if q.limit is not None:
                ordered = ordered[:q.limit]
            records = [_record(ctx, q, r, version) for r in ordered]
            return {"totalSize": len(records), "done": True, "records": records}
        records = records[q.offset:]
        if q.limit is not None:
            records = records[:q.limit]
        return {"totalSize": len(records), "done": True, "records": records}
    except QueryError as err:
        raise SoqlError(str(err), err.code, q.obj_pos) from None


# --- SOSL ---------------------------------------------------------------------------------------------------------

_RESERVED = set("{}[]()^~:\\\"'+-")
_GROUPS = {"ALL": None, "NAME": "name", "EMAIL": "EMAIL", "PHONE": "PHONE"}


def _search_terms(text: str) -> tuple[str, int]:
    """The braced term and the position after it, rejecting unescaped reserved characters like the API does."""
    match = re.match(r"\s*FIND\s*\{", text, re.IGNORECASE)
    if not match:
        quoted = re.match(r"\s*FIND\s*'", text, re.IGNORECASE)
        if quoted:
            end = text.find("'", quoted.end())
            return text[quoted.end():end], end + 1
        raise SoqlError("unexpected token: FIND", "MALFORMED_SEARCH", 0)
    out, pos = [], match.end()
    while pos < len(text):
        ch = text[pos]
        if ch == "\\" and pos + 1 < len(text):
            out.append(text[pos + 1])
            pos += 2
            continue
        if ch == "}":
            return "".join(out), pos + 1
        if ch in _RESERVED:
            raise SoqlError(f"line 1:{pos} mismatched character '{ch}' expecting '}}'", "MALFORMED_SEARCH", pos)
        out.append(ch)
        pos += 1
    raise SoqlError("line 1:%d mismatched character '<EOF>' expecting '}'" % pos, "MALFORMED_SEARCH", pos)


def _matcher(term: str):
    """SOSL term matching: words are ANDed unless joined by OR; ``*`` is a prefix wildcard; quotes make phrases."""
    clauses = [c for c in re.split(r"\s+OR\s+", term.strip(), flags=re.IGNORECASE) if c.strip()]
    parsed = []
    for clause in clauses:
        words = re.findall(r'"[^"]+"|\S+', clause)
        parsed.append([w.strip('"').lower() for w in words if w.upper() != "AND"])

    def hit(text: str) -> bool:
        tokens = re.findall(r"[a-z0-9@.]+", text.lower())
        flat = " ".join(tokens)
        for words in parsed:
            ok = True
            for word in words:
                if " " in word:
                    ok = " ".join(re.findall(r"[a-z0-9@.]+", word)) in flat
                elif word.endswith("*"):
                    ok = any(t.startswith(word[:-1]) for t in tokens)
                else:
                    ok = any(t == word or t.split("@")[0] == word or t.rstrip(".") == word for t in tokens)
                if not ok:
                    break
            if ok:
                return True
        return False
    return hit


def _search_text(obj: str, rec: dict, group: str | None) -> str:
    if group == "name":
        names = OBJECTS[obj]["name"] + (["FirstName", "LastName"] if obj in ("Contact", "Lead", "User") else [])
        return " ".join(str(rec.get(n) or "") for n in names)
    kinds = {"STRING", "TEXTAREA", "EMAIL", "PHONE", "URL", "PICKLIST", "COMBOBOX"} if group is None else {group}
    return " ".join(str(rec.get(f[0]) or "") for f in OBJECTS[obj]["fields"] if f[2] in kinds)


def search(ctx: Ctx, text: str, version: str = "v63.0") -> dict:
    """Run a SOSL search; returns ``{searchRecords: [...]}``. Raises SoqlError."""
    term, pos = _search_terms(text)
    if len(term.replace("*", "").strip()) < 2:
        raise SoqlError("search term must be longer than one character", "MALFORMED_SEARCH", 0)
    rest = text[pos:]
    group = None
    scope = re.match(r"\s*IN\s+(\w+)\s+FIELDS", rest, re.IGNORECASE)
    if scope:
        group = _GROUPS.get(scope.group(1).upper(), None)
        rest = rest[scope.end():]
    specs: list[tuple[str, str]] = []
    returning = re.match(r"\s*RETURNING\s+", rest, re.IGNORECASE)
    total_limit = None
    if returning:
        body = rest[returning.end():]
        depth, start, chunks = 0, 0, []
        for i, ch in enumerate(body):
            depth += ch == "("
            depth -= ch == ")"
            if ch == "," and depth == 0:
                chunks.append(body[start:i])
                start = i + 1
        chunks.append(body[start:])
        tail = re.search(r"\)\s*LIMIT\s+(\d+)\s*$|^\s*\w+\s+LIMIT\s+(\d+)\s*$", chunks[-1], re.IGNORECASE)
        if tail:
            total_limit = int(tail.group(1) or tail.group(2))
            chunks[-1] = chunks[-1][:tail.start() + (1 if tail.group(1) else 0)] if tail.group(1) else \
                re.sub(r"\s+LIMIT\s+\d+\s*$", "", chunks[-1], flags=re.IGNORECASE)
        for chunk in chunks:
            m = re.match(r"\s*(\w+)\s*(?:\((.*)\))?\s*$", chunk, re.DOTALL)
            if not m:
                raise SoqlError(f"unexpected token: '{chunk.strip()}'", "MALFORMED_SEARCH", pos)
            specs.append((m.group(1), m.group(2) or "Id"))
    else:
        limit = re.search(r"LIMIT\s+(\d+)", rest, re.IGNORECASE)
        total_limit = int(limit.group(1)) if limit else None
        specs = [(obj, "Id") for obj in SEARCHABLE]
    hit = _matcher(term)
    records: list[dict] = []
    for obj_name, inner in specs:
        obj = find_object(obj_name)
        if obj is None:
            raise SoqlError(_UNKNOWN_TYPE.format(obj_name), "INVALID_TYPE", text.find(obj_name))
        clause = re.search(r"\b(WHERE|ORDER\s+BY|LIMIT|OFFSET)\b", inner, re.IGNORECASE)
        fields_part, tail = (inner[:clause.start()], inner[clause.start():]) if clause else (inner, "")
        soql = f"SELECT {fields_part.strip() or 'Id'} FROM {obj} {tail}"
        q = Parser(soql).query()
        _validate(ctx, q)
        rows = [r for r in _filtered(ctx, q) if hit(_search_text(obj, r, group))]
        rows = _ordered(ctx, q, rows)[q.offset:]
        if q.limit is not None:
            rows = rows[:q.limit]
        records.extend(_record(ctx, q, r, version) for r in rows)
    if total_limit is not None:
        records = records[:total_limit]
    return {"searchRecords": records}
