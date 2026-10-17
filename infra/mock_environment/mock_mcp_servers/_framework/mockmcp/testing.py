"""Test helpers shared by every mock server's test suite."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from mcp import types

from .app import ServerSpec


class ToolCall:
    """The outcome of one ``ServerSpec.dispatch`` call, with convenient accessors."""

    def __init__(self, result: types.CallToolResult) -> None:
        self.result = result

    @property
    def ok(self) -> bool:
        return not self.result.isError

    @property
    def text(self) -> str:
        return "".join(c.text for c in self.result.content if isinstance(c, types.TextContent))

    @property
    def json(self) -> Any:
        return json.loads(self.text)

    @property
    def structured(self) -> Any:
        return self.result.structuredContent


def call(spec: ServerSpec, tool: str, args: dict | None = None) -> ToolCall:
    return ToolCall(spec.dispatch(tool, args or {}))


def assert_deterministic(spec_factory, tool: str, args: dict) -> ToolCall:
    """Two independently built servers must give byte-identical answers."""
    first = call(spec_factory(), tool, args)
    second = call(spec_factory(), tool, args)
    assert first.text == second.text, f"{tool} is not deterministic for {args}"
    return first


# --- Trace replay -----------------------------------------------------------------------------

VOLATILE_KEYS = frozenset({"timestamp", "qaQueryTime", "retrievedAt"})
ERROR_PREFIXES = (r"Error: ", r"mcp__\w+ failed: ", r"MCP server '[\w-]+': ")


def load_fixture(path) -> tuple[str, dict, str, bool]:
    """``NNN_<tool>_<ok|err>.json`` -> (tool, arguments, recorded text, recorded ok)."""
    path = Path(path)
    raw = json.loads(path.read_text(encoding="utf-8"))
    stem = path.stem
    tool = stem.split("_", 1)[1].rsplit("_", 1)[0]
    args = raw["input"] if isinstance(raw["input"], dict) else json.loads(raw["input"])
    return tool, args, raw["result"], stem.endswith("_ok")


def _strip_prefixes(text: str) -> str:
    for prefix in ERROR_PREFIXES:
        text = re.sub("^" + prefix, "", text)
    return text


def diff(actual: Any, expected: Any, path: str = "$", ignore: frozenset = VOLATILE_KEYS) -> list[str]:
    """Structural differences (key order included), skipping ``ignore`` keys anywhere."""
    if isinstance(expected, dict) and isinstance(actual, dict):
        a_keys = [k for k in actual if k not in ignore]
        e_keys = [k for k in expected if k not in ignore]
        if a_keys != e_keys:
            return [f"{path}: keys {a_keys} != {e_keys}"]
        return [d for k in e_keys for d in diff(actual[k], expected[k], f"{path}.{k}", ignore)]
    if isinstance(expected, list) and isinstance(actual, list):
        if len(actual) != len(expected):
            return [f"{path}: length {len(actual)} != {len(expected)}"]
        return [d for i, (a, e) in enumerate(zip(actual, expected)) for d in diff(a, e, f"{path}[{i}]", ignore)]
    if actual != expected or type(actual) is not type(expected):
        return [f"{path}: {actual!r} != {expected!r}"]
    return []


def _unwrap_error(recorded: str) -> str:
    """Some hosts record failures as ``{"message": "<prefix><text>", "code": "failure"}``."""
    try:
        wrapped = json.loads(recorded)
    except ValueError:
        wrapped = None
    if isinstance(wrapped, dict) and set(wrapped) == {"message", "code"}:
        recorded = wrapped["message"]
    return _strip_prefixes(recorded)


def _compare_text(actual: str, expected: str, ignore: frozenset) -> list[str]:
    try:
        return diff(json.loads(actual), json.loads(expected), ignore=ignore)
    except ValueError:
        return [] if actual == expected else [f"text differs:\n{actual[:400]}\n!=\n{expected[:400]}"]


def replay(spec: ServerSpec, fixture, ignore: frozenset = VOLATILE_KEYS) -> list[str]:
    """Re-run one recorded call and return its differences (empty means an exact replay).

    Successful recordings may carry structured content after the text, separated by a blank
    lines (``<text>\n\n{...}``); both parts are compared.
    """
    tool, args, recorded, recorded_ok = load_fixture(fixture)
    got = call(spec, tool, args)
    if got.ok != recorded_ok:
        return [f"ok={got.ok} but recording ok={recorded_ok}: {got.text[:300]}"]
    if not recorded_ok:
        return _compare_text(got.text, _unwrap_error(recorded), ignore)
    text, *rest = re.split(r"\n{2,}(?=\{)", recorded, maxsplit=1)
    problems = _compare_text(got.text, text, ignore)
    if rest:
        if got.structured is None:
            problems.append("structuredContent missing")
        else:
            problems += ["structured " + d for d in diff(got.structured, json.loads(rest[0]), ignore=ignore)]
    return problems