"""The five Salesforce Headless-360 tools. Names, descriptions and input schemas are the real ones (from SEVAL
traces, with the ``Salesforce_`` prefix the host adds removed), loaded from ``seed_files/tool_schemas.json``."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from mockmcp import CallContext, InvalidParams, Tool, ToolOutput
from mockmcp.schema import validate

from . import catalog, rest, widget
from .store import StateStore

SCHEMAS_PATH = Path(__file__).resolve().parent.parent / "seed_files" / "tool_schemas.json"
WRITE = {"readOnlyHint": False, "destructiveHint": True, "idempotentHint": False, "openWorldHint": False}


def load_schemas(path: Path = SCHEMAS_PATH) -> dict[str, dict]:
    return {t["name"]: t for t in json.loads(path.read_text(encoding="utf-8"))}


class SalesforceTool(Tool):
    def __init__(self, store: StateStore, schemas: dict[str, dict]) -> None:
        self.store = store
        spec = schemas[self.name]
        self.description = spec["description"]
        self.input_schema = spec["inputSchema"]


class DescribeTool(SalesforceTool):
    name = "describe"

    def run(self, args: dict, ctx: CallContext) -> Any:
        return catalog.describe(str(args["id"]))


class DiscoverTool(SalesforceTool):
    name = "discover"

    def run(self, args: dict, ctx: CallContext) -> Any:
        return catalog.discover(str(args["query"]), args.get("limit") or 10, args.get("domain"),
                                args.get("resultType"))


class DispatchTool(SalesforceTool):
    name = "dispatch"
    annotations = WRITE
    readonly = False

    def run(self, args: dict, ctx: CallContext) -> Any:
        return rest.dispatch(self.store, ctx.conversation_id, args["method"], args["url"],
                             query_params=args.get("queryParams"), body=args.get("body"),
                             readonly=self.readonly, now=ctx.clock.now)


class DispatchReadonlyTool(DispatchTool):
    name = "dispatch_readonly"
    annotations = Tool.annotations
    readonly = True


class DisplayWidgetTool(SalesforceTool):
    name = "display_widget"
    ui_resource = widget.RESOURCE_URI
    # Models sometimes send widgetDefinition as a JSON string; parse it before schema validation.
    validate_args = False

    def run(self, args: dict, ctx: CallContext) -> Any:
        definition = args.get("widgetDefinition")
        if isinstance(definition, str):
            try:
                args = {**args, "widgetDefinition": json.loads(definition)}
            except ValueError as exc:
                pos = getattr(exc, "pos", 0) or 0
                raise InvalidParams([f"widgetDefinition: not valid JSON ({exc}) near "
                                     f"'{definition[max(0, pos - 60):pos + 20]}'. Fix the JSON and call "
                                     "display_widget again, passing widgetDefinition as an object, not a string"])
        validate(args, self.input_schema)
        if args["resourceType"] == "salesforce_widget":
            uri = args.get("widget_resource_uri") or ""
            # The mock org registers no Lightning Types, so named widgets can't be resolved.
            raise InvalidParams([f"widget_resource_uri: no Lightning Type widget is registered for '{uri}'; "
                                 "use resourceType \"dynamic\" with a widgetDefinition"])
        definition = args.get("widgetDefinition")
        if not isinstance(definition, dict):
            raise InvalidParams(["widgetDefinition: required when resourceType is \"dynamic\""])
        return ToolOutput(widget.summary(definition), {"widgetDefinition": definition})


TOOLS = (DescribeTool, DiscoverTool, DispatchTool, DispatchReadonlyTool, DisplayWidgetTool)
