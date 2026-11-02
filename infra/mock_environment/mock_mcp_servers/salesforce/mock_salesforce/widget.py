"""``display_widget``: echo a Mosaic widget definition and flatten it to the plain-text summary the real tool
returns as its text content (the host paints the widget from ``structuredContent.widgetDefinition``)."""

from __future__ import annotations

from typing import Any

RESOURCE_URI = "ui://widget/salesforce-widget-renderer"
SEP = " · "


def _scalar(value: Any) -> str | None:
    if value is None or isinstance(value, (list, dict)):
        return None
    if isinstance(value, bool):
        return "true" if value else "false"
    text = str(value).strip()
    return text or None


def _row_text(row: Any) -> str | None:
    if not isinstance(row, dict):
        return _scalar(row)
    parts = [p for p in (_scalar(v) for v in row.values() if isinstance(v, str)) if p]
    return ", ".join(parts) or None


def _flatten(node: Any, out: list[str]) -> None:
    if isinstance(node, list):
        for child in node:
            _flatten(child, out)
        return
    if not isinstance(node, dict):
        return
    definition = node.get("definition", "")
    attrs = node.get("attributes") or {}
    if definition.startswith("action/"):
        return
    if definition == "tile/text":
        _add(out, attrs.get("text"))
    elif definition in ("tile/badge", "tile/button"):
        _add(out, attrs.get("label"))
    elif definition == "tile/callout":
        _add(out, attrs.get("title"))
    elif definition in ("tile/datagrid", "tile/table"):
        _add(out, attrs.get("caption") or attrs.get("title"))
        for row in attrs.get("rows") or []:
            _add(out, _row_text(row))
    elif definition not in ("tile/mosaic", "tile/row", "tile/column", "tile/container", "tile/separator",
                            "tile/icon"):
        _add(out, attrs.get("title") or attrs.get("label") or attrs.get("caption"))
    _flatten(node.get("children"), out)


def _add(out: list[str], value: Any) -> None:
    text = _scalar(value)
    if text:
        out.append(text)


def root_of(definition: Any) -> Any:
    try:
        return definition["renderer"]["componentOverrides"]["$"]
    except (KeyError, TypeError):
        return definition


def summary(definition: Any) -> str:
    out: list[str] = []
    _flatten(root_of(definition), out)
    return SEP.join(out)
