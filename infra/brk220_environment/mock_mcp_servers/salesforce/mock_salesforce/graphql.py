"""A small GraphQL implementation of the Salesforce UI API (``/services/data/vXX.X/graphql``): ``uiapi.query`` record
connections with where/orderBy/first/after/scope, parent and child relationships, polymorphic inline fragments,
``objectInfos``, ``currentUser`` and ``aggregate``. Queries are validated against the mock's schema first, so an
unknown field fails the way a real org fails (``ValidationError`` / ``FieldUndefined``) instead of returning nulls."""

from __future__ import annotations

import base64
import re
from dataclasses import dataclass, field as dc_field
from typing import Any

from . import engine
from .engine import Ctx, QueryError
from .schema import OBJECTS, RECORD_TYPE_MASTER, find_field, find_object, parent_relationship, child_relationship
from .timeutil import iso_ms, parse_dt

# --- lexer --------------------------------------------------------------------------------------------------------

_TOKEN = re.compile(r"""
    (?P<ws>[\s,\ufeff]+|\#[^\n]*)
  | (?P<spread>\.\.\.)
  | (?P<punct>[{}()\[\]:!$=@|&])
  | (?P<block>\"\"\"(?:[^"\\]|\\.|"(?!""))*\"\"\")
  | (?P<string>"(?:[^"\\\n]|\\.)*")
  | (?P<number>-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)
  | (?P<name>[_A-Za-z][_0-9A-Za-z]*)
""", re.VERBOSE)


@dataclass
class Tok:
    kind: str
    text: str
    line: int
    col: int


class GraphQLSyntaxError(Exception):
    def __init__(self, message: str, line: int, col: int) -> None:
        super().__init__(message)
        self.line, self.col = line, col


def tokenize(source: str) -> list[Tok]:
    out: list[Tok] = []
    pos, line, line_start = 0, 1, 0
    while pos < len(source):
        m = _TOKEN.match(source, pos)
        if not m:
            raise GraphQLSyntaxError(f"Invalid syntax with offending token '{source[pos]}'", line, pos - line_start + 1)
        kind = m.lastgroup
        text = m.group()
        if kind != "ws":
            out.append(Tok(kind, text, line, pos - line_start + 1))
        newlines = text.count("\n")
        if newlines:
            line += newlines
            line_start = pos + text.rfind("\n") + 1
        pos = m.end()
    out.append(Tok("eof", "<EOF>", line, pos - line_start + 1))
    return out


# --- AST ----------------------------------------------------------------------------------------------------------

@dataclass
class Var:
    name: str


@dataclass
class Enum:
    name: str


@dataclass
class Field:
    name: str
    alias: str | None
    args: dict[str, Any]
    selections: list | None
    line: int
    col: int

    @property
    def key(self) -> str:
        return self.alias or self.name


@dataclass
class Inline:
    type_cond: str | None
    selections: list
    line: int
    col: int


@dataclass
class Spread:
    name: str
    line: int
    col: int


@dataclass
class Operation:
    kind: str
    name: str | None
    var_defaults: dict[str, Any]
    selections: list
    line: int = 1
    col: int = 1


@dataclass
class Document:
    operations: list[Operation] = dc_field(default_factory=list)
    fragments: dict[str, tuple[str, list]] = dc_field(default_factory=dict)


class Parser:
    def __init__(self, source: str) -> None:
        self.toks = tokenize(source)
        self.i = 0

    def peek(self, offset: int = 0) -> Tok:
        return self.toks[min(self.i + offset, len(self.toks) - 1)]

    def next(self) -> Tok:
        tok = self.peek()
        self.i += 1
        return tok

    def expect(self, text: str) -> Tok:
        tok = self.next()
        if tok.text != text:
            raise GraphQLSyntaxError(f"Invalid syntax with offending token '{tok.text}'", tok.line, tok.col)
        return tok

    def name(self) -> str:
        tok = self.next()
        if tok.kind != "name":
            raise GraphQLSyntaxError(f"Invalid syntax with offending token '{tok.text}'", tok.line, tok.col)
        return tok.text

    def document(self) -> Document:
        doc = Document()
        while self.peek().kind != "eof":
            tok = self.peek()
            if tok.text == "{":
                doc.operations.append(Operation("query", None, {}, self.selection_set(), tok.line, tok.col))
            elif tok.text in ("query", "mutation", "subscription"):
                self.next()
                name = self.name() if self.peek().kind == "name" else None
                defaults = self.variable_defs() if self.peek().text == "(" else {}
                self.directives()
                doc.operations.append(Operation(tok.text, name, defaults, self.selection_set(), tok.line, tok.col))
            elif tok.text == "fragment":
                self.next()
                name = self.name()
                if self.name() != "on":
                    raise GraphQLSyntaxError("Expected 'on'", tok.line, tok.col)
                type_cond = self.name()
                self.directives()
                doc.fragments[name] = (type_cond, self.selection_set())
            else:
                raise GraphQLSyntaxError(f"Invalid syntax with offending token '{tok.text}'", tok.line, tok.col)
        return doc

    def variable_defs(self) -> dict[str, Any]:
        out: dict[str, Any] = {}
        self.expect("(")
        while self.peek().text != ")":
            self.expect("$")
            name = self.name()
            self.expect(":")
            self.type_ref()
            out[name] = self.value(const=True) if self.peek().text == "=" and self.next() else None
            self.directives()
        self.expect(")")
        return out

    def type_ref(self) -> None:
        if self.peek().text == "[":
            self.next()
            self.type_ref()
            self.expect("]")
        else:
            self.name()
        if self.peek().text == "!":
            self.next()

    def directives(self) -> None:
        while self.peek().text == "@":
            self.next()
            self.name()
            if self.peek().text == "(":
                self.arguments()

    def selection_set(self) -> list:
        self.expect("{")
        out: list = []
        while self.peek().text != "}":
            tok = self.peek()
            if tok.kind == "eof":
                raise GraphQLSyntaxError("Invalid syntax with offending token '<EOF>'", tok.line, tok.col)
            if tok.kind == "spread":
                self.next()
                if self.peek().text == "on":
                    self.next()
                    type_cond = self.name()
                    self.directives()
                    out.append(Inline(type_cond, self.selection_set(), tok.line, tok.col))
                elif self.peek().text in ("{", "@"):
                    self.directives()
                    out.append(Inline(None, self.selection_set(), tok.line, tok.col))
                else:
                    name = self.name()
                    self.directives()
                    out.append(Spread(name, tok.line, tok.col))
                continue
            first = self.name()
            alias = None
            if self.peek().text == ":":
                self.next()
                alias, first = first, self.name()
            args = self.arguments() if self.peek().text == "(" else {}
            self.directives()
            selections = self.selection_set() if self.peek().text == "{" else None
            out.append(Field(first, alias, args, selections, tok.line, tok.col))
        self.expect("}")
        return out

    def arguments(self) -> dict[str, Any]:
        self.expect("(")
        out: dict[str, Any] = {}
        while self.peek().text != ")":
            name = self.name()
            self.expect(":")
            out[name] = self.value()
        self.expect(")")
        return out

    def value(self, const: bool = False) -> Any:
        tok = self.next()
        if tok.text == "$" and not const:
            return Var(self.name())
        if tok.text == "[":
            items = []
            while self.peek().text != "]":
                items.append(self.value(const))
            self.next()
            return items
        if tok.text == "{":
            obj: dict[str, Any] = {}
            while self.peek().text != "}":
                key = self.name()
                self.expect(":")
                obj[key] = self.value(const)
            self.next()
            return obj
        if tok.kind == "string":
            return _unescape(tok.text[1:-1])
        if tok.kind == "block":
            return tok.text[3:-3]
        if tok.kind == "number":
            return float(tok.text) if any(c in tok.text for c in ".eE") else int(tok.text)
        if tok.kind == "name":
            if tok.text in ("true", "false"):
                return tok.text == "true"
            if tok.text == "null":
                return None
            return Enum(tok.text)
        raise GraphQLSyntaxError(f"Invalid syntax with offending token '{tok.text}'", tok.line, tok.col)


def _unescape(text: str) -> str:
    def repl(m: re.Match) -> str:
        ch = m.group(1)
        if ch.startswith("u"):
            return chr(int(ch[1:], 16))
        return {"n": "\n", "t": "\t", "r": "\r", "b": "\b", "f": "\f"}.get(ch, ch)

    return re.sub(r"\\(u[0-9a-fA-F]{4}|.)", repl, text)


def resolve_args(value: Any, variables: dict[str, Any]) -> Any:
    """Replace variables and enums with plain Python values."""
    if isinstance(value, Var):
        return variables.get(value.name)
    if isinstance(value, Enum):
        return value.name
    if isinstance(value, list):
        return [resolve_args(v, variables) for v in value]
    if isinstance(value, dict):
        return {k: resolve_args(v, variables) for k, v in value.items()}
    return value


# --- types used for validation ------------------------------------------------------------------------------------

_VALUE_TYPE = {"STRING": "StringValue", "PICKLIST": "PicklistValue", "MULTIPICKLIST": "MultiPicklistValue",
               "COMBOBOX": "PicklistValue", "CURRENCY": "CurrencyValue", "DATE": "DateValue",
               "DATETIME": "DateTimeValue", "BOOLEAN": "BooleanValue", "INT": "IntValue", "DOUBLE": "DoubleValue",
               "PERCENT": "PercentValue", "ID": "IDValue", "REFERENCE": "IDValue", "EMAIL": "EmailValue",
               "PHONE": "PhoneNumberValue", "URL": "UrlValue", "TEXTAREA": "TextAreaValue"}
_PICKLIST_TYPES = ("PICKLIST", "MULTIPICKLIST", "COMBOBOX")

_SCALARS: dict[str, set[str]] = {
    "FieldValue": {"value", "displayValue", "label", "format", "__typename"},
    "PageInfo": {"hasNextPage", "hasPreviousPage", "startCursor", "endCursor", "__typename"},
    "ObjectInfo": {"ApiName", "label", "labelPlural", "keyPrefix", "createable", "updateable", "deletable",
                   "queryable", "searchable", "custom", "nameFields", "defaultRecordTypeId", "__typename"},
    "Field": {"ApiName", "label", "dataType", "relationshipName", "required", "createable", "updateable",
              "filterable", "sortable", "nillable", "custom", "calculated", "length", "precision", "scale",
              "inlineHelpText", "compound", "__typename"},
    "ChildRelationship": {"childObjectApiName", "relationshipName", "fieldName", "__typename"},
    "ReferenceToInfo": {"ApiName", "nameFields", "__typename"},
    "PicklistValues": {"recordTypeID", "__typename"},
    "PicklistValue": {"value", "label", "validFor", "__typename"},
    "RecordTypeInfo": {"recordTypeId", "name", "master", "available", "defaultRecordTypeMapping", "__typename"},
    "AggValue": {"value", "displayValue", "format", "__typename"},
}
_NESTED: dict[str, dict[str, str]] = {
    "ObjectInfo": {"fields": "Field", "childRelationships": "ChildRelationship", "recordTypeInfos": "RecordTypeInfo"},
    "Field": {"referenceToInfos": "ReferenceToInfo"},
    "PicklistField": {"picklistValuesByRecordTypeIDs": "PicklistValues", "referenceToInfos": "ReferenceToInfo"},
    "PicklistValues": {"picklistValues": "PicklistValue", "defaultValue": "PicklistValue"},
}
_CONN_ARGS = {"where", "first", "after", "orderBy", "scope", "upperBound", "last", "before"}
_AGG_OPS = ("count", "countDistinct", "sum", "avg", "min", "max", "grouping")


class GqlError(Exception):
    def __init__(self, kind: str, message: str, line: int, col: int, path: list[str], error_type: str =
                 "ValidationError") -> None:
        super().__init__(message)
        self.kind, self.line, self.col, self.path, self.error_type = kind, line, col, path, error_type

    def to_json(self) -> dict:
        if self.error_type == "ValidationError":
            message = f"Validation error ({self.kind}@[{'/'.join(self.path)}]) : {self.args[0]}"
            return {"extensions": {"ErrorType": "ValidationError"}, "locations": [{"column": self.col, "line": self.line}],
                    "message": _escape(message), "paths": []}
        return {"extensions": {"ErrorType": self.error_type}, "locations": [{"column": self.col, "line": self.line}],
                "message": _escape(str(self.args[0])), "paths": self.path}


@dataclass(frozen=True)
class T:
    """A schema type: kind plus the object(s) it ranges over."""
    kind: str
    objs: tuple[str, ...] = ()
    dtype: str | None = None

    @property
    def name(self) -> str:
        obj = "".join(self.objs[:1])
        return {"Query": "Query", "UIAPI": "UIAPI", "RecordQuery": "RecordQuery", "RecordQueryAggregate":
                "RecordQueryAggregate", "Conn": f"{obj}Connection", "Edge": f"{obj}Edge", "Record": obj,
                "FieldValue": _VALUE_TYPE.get(self.dtype or "", "StringValue"), "AggConn":
                f"{obj}AggregateConnection", "AggEdge": f"{obj}AggregateEdge", "AggNode": f"{obj}Aggregate",
                "AggResult": f"{obj}_AggregateResult", "AggField": "AggregateField"}.get(self.kind, self.kind)


def _child_type(t: T, f: Field, path: list[str]) -> T | None:
    """The type of field ``f`` inside ``t``, or None for a leaf scalar; raises FieldUndefined."""
    name = f.name

    def undefined() -> GqlError:
        return GqlError("FieldUndefined", f"Field '{name}' in type '{t.name}' is undefined", f.line, f.col,
                        path + [f.key])

    if name == "__typename":
        return None
    kind = t.kind
    if kind == "Query":
        if name == "uiapi":
            return T("UIAPI")
        raise undefined()
    if kind == "UIAPI":
        if name == "query":
            return T("RecordQuery")
        if name == "aggregate":
            return T("RecordQueryAggregate")
        if name == "objectInfos":
            return T("ObjectInfo")
        if name == "currentUser":
            return T("Record", ("User",))
        raise undefined()
    if kind in ("RecordQuery", "RecordQueryAggregate"):
        obj = name if name in OBJECTS else None
        if obj is None or OBJECTS[obj].get("virtual"):
            raise undefined()
        return T("Conn" if kind == "RecordQuery" else "AggConn", (obj,))
    if kind in ("Conn", "AggConn"):
        if name == "edges":
            return T("Edge" if kind == "Conn" else "AggEdge", t.objs)
        if name == "pageInfo":
            return T("PageInfo")
        if name in ("totalCount", "pageResultCount"):
            return None
        raise undefined()
    if kind in ("Edge", "AggEdge"):
        if name == "node":
            return T("Record" if kind == "Edge" else "AggNode", t.objs)
        if name == "cursor":
            return None
        raise undefined()
    if kind == "AggNode":
        if name == "aggregate":
            return T("AggResult", t.objs)
        raise undefined()
    if kind == "AggResult":
        meta = find_field(t.objs[0], name)
        if meta is None or meta[0] != name:
            raise undefined()
        return T("AggField", t.objs, meta[2])
    if kind == "AggField":
        if name in _AGG_OPS:
            return T("AggValue")
        if name in ("value", "displayValue", "format"):
            return None
        raise undefined()
    if kind == "Record":
        # A field must exist on every possible type unless selected inside an inline fragment.
        obj = t.objs[0]
        if len(t.objs) > 1 and name not in ("Id", "ApiName", "DisplayValue", "WeakEtag"):
            raise undefined()
        if name in ("Id", "ApiName", "DisplayValue", "WeakEtag"):
            return None
        meta = find_field(obj, name)
        if meta is not None and meta[0] == name:
            return T("FieldValue", t.objs, meta[2])
        rel = parent_relationship(obj, name)
        if rel:
            return T("Record", tuple(rel[2]))
        child = child_relationship(obj, name)
        if child:
            return T("Conn", (child[0],))
        raise undefined()
    if kind == "FieldValue":
        if name in _SCALARS["FieldValue"]:
            return None
        raise undefined()
    if kind in _SCALARS or kind in _NESTED:
        nested = _NESTED.get(kind, {})
        if name in nested:
            return T(nested[name])
        if name in _SCALARS.get(kind, set()) or (kind == "PicklistField" and name in _SCALARS["Field"]):
            return None
        raise undefined()
    raise undefined()


def _needs_selection(t: T | None) -> bool:
    return t is not None


def validate(selections: list, t: T, path: list[str], fragments: dict, errors: list[GqlError]) -> None:
    for sel in selections:
        if isinstance(sel, Spread):
            if sel.name not in fragments:
                errors.append(GqlError("UndefinedFragment", f"Undefined fragment {sel.name}", sel.line, sel.col, path))
                continue
            cond, subs = fragments[sel.name]
            validate(subs, _narrow(t, cond, sel, path, errors) or t, path, fragments, errors)
            continue
        if isinstance(sel, Inline):
            narrowed = _narrow(t, sel.type_cond, sel, path, errors) if sel.type_cond else t
            if narrowed is not None:
                validate(sel.selections, narrowed, path, fragments, errors)
            continue
        try:
            child = _child_type(t, sel, path)
        except GqlError as err:
            errors.append(err)
            continue
        if child is not None and child.kind in ("Conn", "AggConn"):
            allowed = _CONN_ARGS | ({"groupBy"} if child.kind == "AggConn" else set())
            for arg in sel.args:
                if arg not in allowed:
                    errors.append(GqlError("UnknownArgument", f"Unknown field argument {arg}", sel.line, sel.col,
                                           path + [sel.key]))
            where = sel.args.get("where")
            if isinstance(where, dict):
                try:
                    engine.check_where(child.objs[0], where)
                except QueryError as err:
                    errors.append(GqlError("WrongType", f"argument 'where' with value '{_show(where)}' {err}",
                                           sel.line, sel.col, path + [sel.key]))
        if child is None and sel.selections:
            errors.append(GqlError("SubselectionNotAllowed", f"Sub selection not allowed on leaf type of field "
                                   f"{sel.name}", sel.line, sel.col, path + [sel.key]))
        elif child is not None and not sel.selections:
            errors.append(GqlError("SubselectionRequired", f"Sub selection required for type '{child.name}' of "
                                   f"field '{sel.name}'", sel.line, sel.col, path + [sel.key]))
        elif child is not None:
            validate(sel.selections, child, path + [sel.key], fragments, errors)


def _show(value: Any) -> str:
    if isinstance(value, dict):
        return "ObjectValue{" + ", ".join(f"{k}: {_show(v)}" for k, v in value.items()) + "}"
    if isinstance(value, list):
        return "[" + ", ".join(_show(v) for v in value) + "]"
    if isinstance(value, Var):
        return "$" + value.name
    if isinstance(value, Enum):
        return value.name
    return '"' + str(value) + '"' if isinstance(value, str) else str(value).lower() if isinstance(value, bool) \
        else str(value)


def _narrow(t: T, cond: str | None, sel: Any, path: list[str], errors: list[GqlError]) -> T | None:
    if cond is None:
        return t
    if t.kind == "Record":
        if cond in t.objs:
            return T("Record", (cond,))
        if cond == "Record":
            return t
        if cond in OBJECTS:
            return None  # a valid type that this field can never be; the fragment simply never applies
    elif t.kind == "Field" and cond in ("PicklistField", "Field"):
        return T(cond)
    elif cond == t.name or cond == t.kind:
        return t
    errors.append(GqlError("UnknownType", f"Unknown type {cond}", sel.line, sel.col, path))
    return None


# --- execution ----------------------------------------------------------------------------------------------------

def _escape(text: str) -> str:
    return (text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;").replace("'", "&#39;"))


def _cursor(index: int) -> str:
    return base64.b64encode(f"v1:{index}".encode()).decode()


def _from_cursor(cursor: str | None) -> int:
    if not cursor:
        return -1
    try:
        return int(base64.b64decode(cursor).decode().split(":", 1)[1])
    except Exception:
        raise QueryError(f"Invalid cursor: {cursor}") from None


def _raw_value(ctx: Ctx, obj: str, rec: dict, meta: tuple) -> Any:
    raw = engine.value(ctx, obj, rec, meta[0])
    dtype = meta[2]
    if raw is None:
        return None
    if dtype in ("CURRENCY", "DOUBLE", "PERCENT"):
        return float(raw)
    if dtype == "INT":
        return int(raw)
    if dtype == "BOOLEAN":
        return bool(raw)
    if dtype == "DATETIME":
        moment = parse_dt(raw)
        return iso_ms(moment) if moment else raw
    return raw


class Executor:
    def __init__(self, ctx: Ctx, fragments: dict, variables: dict) -> None:
        self.ctx, self.fragments, self.variables = ctx, fragments, variables
        self.errors: list[dict] = []

    def flatten(self, selections: list, type_name: str, objs: tuple[str, ...] = ()) -> list[Field]:
        out: list[Field] = []
        for sel in selections:
            if isinstance(sel, Field):
                out.append(sel)
                continue
            if isinstance(sel, Spread):
                cond, subs = self.fragments[sel.name]
            else:
                cond, subs = sel.type_cond, sel.selections
            if cond is None or cond == type_name or cond == "Record" or cond == "Field" or (objs and cond in objs):
                out.extend(self.flatten(subs, type_name, objs))
        return out

    def args(self, f: Field) -> dict:
        return resolve_args(f.args, self.variables)

    # top level
    def run(self, selections: list) -> dict:
        out: dict[str, Any] = {}
        for f in self.flatten(selections, "Query"):
            out[f.key] = "Query" if f.name == "__typename" else self.uiapi(f.selections or [])
        return out

    def uiapi(self, selections: list) -> dict:
        out: dict[str, Any] = {}
        for f in self.flatten(selections, "UIAPI"):
            if f.name == "__typename":
                out[f.key] = "UIAPI"
            elif f.name == "query":
                out[f.key] = self.record_query(f, aggregate=False)
            elif f.name == "aggregate":
                out[f.key] = self.record_query(f, aggregate=True)
            elif f.name == "objectInfos":
                out[f.key] = self.object_infos(f)
            elif f.name == "currentUser":
                user = self.ctx.org.user(self.ctx.org.current_user_id)
                out[f.key] = self.record("User", user, f.selections or [], ["uiapi", f.key])
        return out

    def record_query(self, f: Field, aggregate: bool) -> dict:
        out: dict[str, Any] = {}
        for sub in self.flatten(f.selections or [], "RecordQuery"):
            if sub.name == "__typename":
                out[sub.key] = "RecordQuery"
                continue
            path = ["uiapi", f.key, sub.key]
            try:
                items = self.filtered(sub.name, engine.rows(self.ctx, sub.name), self.args(sub))
                if aggregate:
                    out[sub.key] = self.aggregate_connection(sub.name, items, sub, path)
                else:
                    out[sub.key] = self.connection(sub.name, items, sub, path)
            except QueryError as err:
                self.errors.append(GqlError("WrongType", str(err), sub.line, sub.col, path).to_json())
                out[sub.key] = None
        return out

    def filtered(self, obj: str, items: list[dict], args: dict) -> list[dict]:
        scope = str(args.get("scope") or "EVERYTHING").upper()
        if scope in ("MINE", "ASSIGNEDTOME"):
            me = self.ctx.org.current_user_id
            items = [r for r in items if r.get("OwnerId") == me]
        where = args.get("where")
        if where is not None and not isinstance(where, dict):
            raise QueryError("argument 'where' must be an input object")
        return [r for r in items if engine.gql_match(self.ctx, obj, r, where)]

    def order(self, obj: str, items: list[dict], order_by: Any) -> list[dict]:
        if not order_by:
            return engine.sort_rows(self.ctx, obj, items, engine.default_order(obj))
        keys: list[tuple[str, bool, bool | None]] = []

        def walk(spec: dict, prefix: str, current: str) -> None:
            for name, val in spec.items():
                if not isinstance(val, dict):
                    raise QueryError(f"orderBy on '{name}' needs {{order: ASC|DESC}}")
                if "order" in val or "nulls" in val:
                    meta = find_field(current, name)
                    if meta is None:
                        raise QueryError(f"Field '{name}' in type '{current}_OrderBy' is undefined")
                    nulls = val.get("nulls")
                    keys.append((prefix + meta[0], str(val.get("order", "ASC")).upper() == "DESC",
                                 None if nulls is None else str(nulls).upper() == "FIRST"))
                else:
                    rel = parent_relationship(current, name, case_insensitive=True)
                    if rel is None:
                        raise QueryError(f"Field '{name}' in type '{current}_OrderBy' is undefined")
                    walk(val, prefix + rel[1] + ".", rel[2][0])

        for spec in order_by if isinstance(order_by, list) else [order_by]:
            walk(spec, "", obj)
        return engine.sort_rows(self.ctx, obj, items, keys)

    def connection(self, obj: str, items: list[dict], f: Field, path: list[str]) -> dict:
        args = self.args(f)
        items = self.order(obj, items, args.get("orderBy"))
        total = len(items)
        start = _from_cursor(args.get("after")) + 1
        first = args.get("first")
        first = 10 if first is None else max(0, min(int(first), 2000))
        page = items[start:start + first]
        out: dict[str, Any] = {}
        for sub in self.flatten(f.selections or [], "Connection"):
            if sub.name == "__typename":
                out[sub.key] = f"{obj}Connection"
            elif sub.name == "totalCount":
                out[sub.key] = total
            elif sub.name == "pageResultCount":
                out[sub.key] = len(page)
            elif sub.name == "pageInfo":
                info = {"hasNextPage": start + len(page) < total, "hasPreviousPage": start > 0,
                        "startCursor": _cursor(start) if page else None,
                        "endCursor": _cursor(start + len(page) - 1) if page else None}
                out[sub.key] = self.pick(info, sub.selections or [], "PageInfo")
            elif sub.name == "edges":
                edges = []
                for offset, rec in enumerate(page):
                    edge: dict[str, Any] = {}
                    for e in self.flatten(sub.selections or [], "Edge"):
                        if e.name == "node":
                            edge[e.key] = self.record(obj, rec, e.selections or [], path + ["edges", "node"])
                        elif e.name == "cursor":
                            edge[e.key] = _cursor(start + offset)
                        else:
                            edge[e.key] = f"{obj}Edge"
                    edges.append(edge)
                out[sub.key] = edges
        return out

    def record(self, obj: str, rec: dict | None, selections: list, path: list[str]) -> dict | None:
        if rec is None:
            return None
        out: dict[str, Any] = {}
        for f in self.flatten(selections, obj, (obj,)):
            name = f.name
            if name == "__typename":
                out[f.key] = obj
            elif name == "Id":
                out[f.key] = rec["Id"]
            elif name == "ApiName":
                out[f.key] = obj
            elif name == "DisplayValue":
                out[f.key] = engine.record_name(self.ctx, obj, rec)
            elif name == "WeakEtag":
                out[f.key] = int(parse_dt(rec.get("LastModifiedDate") or "2026-01-01T00:00:00Z").timestamp() * 1000)
            elif (meta := find_field(obj, name)) is not None and meta[0] == name:
                raw = _raw_value(self.ctx, obj, rec, meta)
                fv = {"value": raw, "displayValue": engine.display_value(meta[2], raw), "label": raw
                      if meta[2] in _PICKLIST_TYPES else None, "format": None, "__typename": _VALUE_TYPE.get(meta[2])}
                out[f.key] = {s.key: fv.get(s.name) for s in self.flatten(f.selections or [], "FieldValue")}
            elif parent_relationship(obj, name):
                hit = engine.follow(self.ctx, obj, rec, name)
                out[f.key] = self.record(hit[0], hit[1], f.selections or [], path + [f.key]) if hit else None
            elif child_relationship(obj, name):
                child_obj, kids = engine.children(self.ctx, obj, rec, name)
                try:
                    kids = self.filtered(child_obj, kids, self.args(f))
                    out[f.key] = self.connection(child_obj, kids, f, path + [f.key])
                except QueryError as err:
                    self.errors.append(GqlError("WrongType", str(err), f.line, f.col, path + [f.key]).to_json())
                    out[f.key] = None
        return out

    def pick(self, data: dict, selections: list, type_name: str) -> dict:
        return {s.key: (type_name if s.name == "__typename" else data.get(s.name))
                for s in self.flatten(selections, type_name)}

    # aggregate
    def aggregate_connection(self, obj: str, items: list[dict], f: Field, path: list[str]) -> dict:
        args = self.args(f)
        group_fields: list[str] = []
        for name, spec in (args.get("groupBy") or {}).items():
            meta = find_field(obj, name)
            if meta is None:
                raise QueryError(f"Field '{name}' in type '{obj}_GroupBy' is undefined")
            if not isinstance(spec, dict) or spec.get("group", True):
                group_fields.append(meta[0])
        groups: dict[tuple, list[dict]] = {}
        for rec in items:
            key = tuple(engine.value(self.ctx, obj, rec, g) for g in group_fields)
            groups.setdefault(key, []).append(rec)
        if not group_fields:
            groups = {(): items}
        buckets = list(groups.items())
        first = args.get("first")
        page = buckets[: 10 if first is None else int(first)] if group_fields else buckets
        out: dict[str, Any] = {}
        for sub in self.flatten(f.selections or [], "AggConn"):
            if sub.name == "totalCount":
                out[sub.key] = len(buckets)
            elif sub.name == "pageResultCount":
                out[sub.key] = len(page)
            elif sub.name == "pageInfo":
                info = {"hasNextPage": len(page) < len(buckets), "hasPreviousPage": False,
                        "startCursor": _cursor(0) if page else None,
                        "endCursor": _cursor(len(page) - 1) if page else None}
                out[sub.key] = self.pick(info, sub.selections or [], "PageInfo")
            elif sub.name == "edges":
                edges = []
                for index, (key, recs) in enumerate(page):
                    edge: dict[str, Any] = {}
                    for e in self.flatten(sub.selections or [], "AggEdge"):
                        if e.name == "cursor":
                            edge[e.key] = _cursor(index)
                        elif e.name == "node":
                            edge[e.key] = self.aggregate_node(obj, dict(zip(group_fields, key)), recs, e)
                    edges.append(edge)
                out[sub.key] = edges
            elif sub.name == "__typename":
                out[sub.key] = f"{obj}AggregateConnection"
        return out

    def aggregate_node(self, obj: str, group: dict, recs: list[dict], node: Field) -> dict:
        out: dict[str, Any] = {}
        for a in self.flatten(node.selections or [], "AggNode"):
            if a.name != "aggregate":
                continue
            result: dict[str, Any] = {}
            for fld in self.flatten(a.selections or [], "AggResult"):
                meta = find_field(obj, fld.name)
                values = [v for v in (engine.value(self.ctx, obj, r, meta[0]) for r in recs) if v is not None]
                entry: dict[str, Any] = {}
                for op in self.flatten(fld.selections or [], "AggField"):
                    if op.name in ("value", "displayValue"):
                        raw = group.get(meta[0])
                        entry[op.key] = raw if op.name == "value" else engine.display_value(meta[2], raw)
                        continue
                    agg = self._agg(op.name, values, meta[2])
                    agg_type = "INT" if op.name in ("count", "countDistinct", "grouping") else meta[2]
                    data = {"value": agg, "displayValue": engine.display_value(agg_type, agg), "format": None}
                    entry[op.key] = self.pick(data, op.selections or [], "AggValue")
                result[fld.key] = entry
            out[a.key] = result
        return out

    @staticmethod
    def _agg(op: str, values: list, dtype: str | None) -> Any:
        numeric = dtype in ("CURRENCY", "DOUBLE", "PERCENT", "INT")
        if op == "count":
            return len(values)
        if op == "countDistinct":
            return len(set(values))
        if op == "grouping":
            return 0
        if not values:
            return None
        if op == "sum":
            return float(sum(float(v) for v in values)) if numeric else None
        if op == "avg":
            return float(sum(float(v) for v in values)) / len(values) if numeric else None
        if op == "min":
            return min(values)
        return max(values)

    # objectInfos
    def object_infos(self, f: Field) -> list | None:
        args = self.args(f)
        names = list(args.get("apiNames") or [])
        record_types: dict[str, list] = {}
        for item in args.get("objectInfoInputs") or []:
            names.append(item.get("apiName"))
            record_types[item.get("apiName")] = item.get("recordTypeIDs") or []
        out = []
        for name in names:
            obj = find_object(str(name or ""))
            if obj is None or OBJECTS[obj].get("virtual"):
                self.errors.append(GqlError("DataFetchingException", f"The requested resource does not exist: "
                                            f"{name}", f.line, f.col, ["uiapi", f.key], "DataFetchingException")
                                   .to_json())
                return None
            out.append(self.object_info(obj, f.selections or []))
        return out

    def object_info(self, obj: str, selections: list) -> dict:
        meta = OBJECTS[obj]
        data = {"ApiName": obj, "label": meta["label"], "labelPlural": meta["plural"], "keyPrefix": meta["prefix"],
                "createable": obj in ("Account", "Contact", "Lead", "Opportunity", "Event", "Task"),
                "updateable": obj in ("Account", "Contact", "Lead", "Opportunity", "Event", "Task"),
                "deletable": obj in ("Account", "Contact", "Lead", "Opportunity", "Event", "Task"),
                "queryable": True, "searchable": obj not in ("OpportunityHistory", "Organization"), "custom": False,
                "nameFields": meta["name"], "defaultRecordTypeId": RECORD_TYPE_MASTER}
        out: dict[str, Any] = {}
        for s in self.flatten(selections, "ObjectInfo"):
            if s.name == "__typename":
                out[s.key] = "ObjectInfo"
            elif s.name == "fields":
                out[s.key] = [self.field_info(obj, fm, s.selections or []) for fm in meta["fields"]]
            elif s.name == "childRelationships":
                out[s.key] = [self.pick({"childObjectApiName": c[0], "relationshipName": c[1], "fieldName": c[2]},
                                        s.selections or [], "ChildRelationship") for c in meta["children"]]
            elif s.name == "recordTypeInfos":
                out[s.key] = [self.pick({"recordTypeId": RECORD_TYPE_MASTER, "name": "Master", "master": True,
                                         "available": True, "defaultRecordTypeMapping": True},
                                        s.selections or [], "RecordTypeInfo")]
            else:
                out[s.key] = data.get(s.name)
        return out

    def field_info(self, obj: str, fm: tuple, selections: list) -> dict:
        api, label, dtype, extra = fm
        required = api in OBJECTS[obj].get("required", []) or api in ("Id", "Name", "CreatedDate",
                                                                      "LastModifiedDate", "IsDeleted")
        from .schema import READ_ONLY_FIELDS
        writable = api not in READ_ONLY_FIELDS or (api == "AccountId" and obj in ("Contact", "Opportunity"))
        type_name = "PicklistField" if dtype in _PICKLIST_TYPES else "ReferenceField" if dtype == "REFERENCE" \
            else "Field"
        data = {"ApiName": api, "label": label, "dataType": dtype,
                "relationshipName": extra[0] if dtype == "REFERENCE" else None, "required": required,
                "createable": writable, "updateable": writable, "filterable": dtype != "TEXTAREA",
                "sortable": dtype != "TEXTAREA", "nillable": not required, "custom": api.endswith("__c"),
                "calculated": api in ("Name",) and obj in ("Contact", "Lead", "User"), "compound": False,
                "length": 255 if dtype in ("STRING", "PICKLIST", "COMBOBOX", "URL", "EMAIL") else 0,
                "precision": 18 if dtype == "CURRENCY" else 0, "scale": 2 if dtype == "CURRENCY" else 0,
                "inlineHelpText": None}
        out: dict[str, Any] = {}
        for s in self.flatten(selections, type_name):
            if s.name == "__typename":
                out[s.key] = type_name
            elif s.name == "referenceToInfos":
                targets = extra[1] if dtype == "REFERENCE" else []
                out[s.key] = [self.pick({"ApiName": t, "nameFields": OBJECTS[t]["name"]}, s.selections or [],
                                        "ReferenceToInfo") for t in targets]
            elif s.name == "picklistValuesByRecordTypeIDs":
                values = extra or []
                entry: dict[str, Any] = {}
                for p in self.flatten(s.selections or [], "PicklistValues"):
                    if p.name == "picklistValues":
                        entry[p.key] = [self.pick({"value": v, "label": v, "validFor": []}, p.selections or [],
                                                  "PicklistValue") for v in values]
                    elif p.name == "defaultValue":
                        entry[p.key] = None
                    elif p.name == "recordTypeID":
                        entry[p.key] = RECORD_TYPE_MASTER
                out[s.key] = [entry] if dtype in _PICKLIST_TYPES else None
            else:
                out[s.key] = data.get(s.name)
        return out


# --- entry point --------------------------------------------------------------------------------------------------

def execute(ctx: Ctx, query: str, variables: dict | None = None, operation_name: str | None = None) -> dict:
    """Run a UI API GraphQL request and return the response body ``{data, errors, extensions}``."""
    try:
        doc = Parser(query or "").document()
    except GraphQLSyntaxError as err:
        message = f"Invalid Syntax : {err}"
        return {"data": None, "errors": [{"extensions": {"ErrorType": "InvalidSyntax"},
                                          "locations": [{"column": err.col, "line": err.line}],
                                          "message": _escape(message), "paths": []}], "extensions": {}}
    ops = [o for o in doc.operations if operation_name in (None, o.name)]
    if not ops:
        return {"data": None, "errors": [{"extensions": {"ErrorType": "ValidationError"}, "locations": [],
                                          "message": "Unknown operation named " + _escape(str(operation_name)),
                                          "paths": []}], "extensions": {}}
    op = ops[0]
    if op.kind != "query":
        err = GqlError("FieldUndefined", f"Schema is not configured for {op.kind}s.", op.line, op.col, [])
        return {"data": {}, "errors": [err.to_json()], "extensions": {}}
    errors: list[GqlError] = []
    validate(op.selections, T("Query"), [], doc.fragments, errors)
    if errors:
        return {"data": {}, "errors": [e.to_json() for e in errors], "extensions": {}}
    merged = {k: v for k, v in op.var_defaults.items() if v is not None}
    merged.update(variables or {})
    executor = Executor(ctx, doc.fragments, merged)
    data = executor.run(op.selections)
    return {"data": data, "errors": executor.errors, "extensions": {}}
