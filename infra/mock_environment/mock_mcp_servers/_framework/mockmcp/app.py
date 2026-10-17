"""Turns a ``ServerSpec`` into a runnable MCP server.

Transports:
* ``http`` (default): streamable HTTP at ``/mcp`` plus ``/healthz``. Stateless, so it
  scales horizontally on Azure Container Apps without sticky sessions.
* ``stdio``: for local MCP clients (VS Code, Copilot CLI, MCP Inspector).

``dispatch()`` is transport-free, which keeps tests fast and lets every transport
share exactly one code path.
"""

from __future__ import annotations

import argparse
import asyncio
import contextlib
import json
import logging
import os
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Iterable, Protocol

from mcp import types
from mcp.server.lowlevel import Server

from .errors import InvalidParams, NotEntitled, ToolError, UpstreamError
from .schema import validate
from .tool import CallContext, Clock, Tool, ToolOutput

log = logging.getLogger("mockmcp")


class ErrorRenderer(Protocol):
    def __call__(self, error: ToolError, tool: str) -> str: ...


def default_renderer(error: ToolError, tool: str) -> str:
    if isinstance(error, InvalidParams):
        return "Invalid arguments:\n" + "\n".join(f"- {issue}" for issue in error.issues)
    if isinstance(error, UpstreamError):
        return f"Upstream error ({error.status}): {error.message}"
    if isinstance(error, NotEntitled):
        return f"Not entitled: {error.message}"
    return error.message


def dumps(value: Any) -> str:
    """Compact JSON, the way the real servers emit tool text."""
    return value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, separators=(",", ":"))


@dataclass
class ServerSpec:
    name: str
    version: str
    tools: list[Tool]
    instructions: str | None = None
    render_error: ErrorRenderer = default_renderer
    clock_factory: Callable[[], Clock] = Clock.from_env
    _by_name: dict[str, Tool] = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self._by_name = {}
        for tool in self.tools:
            if tool.name in self._by_name:
                raise ValueError(f"Duplicate tool name: {tool.name}")
            self._by_name[tool.name] = tool

    def tool(self, name: str) -> Tool | None:
        return self._by_name.get(name)

    def list_tools(self) -> list[types.Tool]:
        return [
            types.Tool(
                name=t.name,
                title=t.title,
                description=t.description,
                inputSchema=t.input_schema,
                annotations=types.ToolAnnotations(**t.annotations),
            )
            for t in self.tools
        ]

    def dispatch(self, name: str, arguments: dict | None) -> types.CallToolResult:
        """Run one tool call and return the exact MCP result. Never raises."""
        started = time.perf_counter()
        args = arguments or {}
        tool = self.tool(name)
        if tool is None:
            result = _error(f"Unknown tool: {name}")
        else:
            ctx = CallContext(tool=name, clock=self.clock_factory())
            try:
                if tool.validate_args:
                    validate(args, tool.input_schema)
                result = _success(tool.run(args, ctx))
            except ToolError as exc:
                result = _error(self.render_error(exc, name))
            except Exception:  # A bug in a mock must still answer like a server would.
                log.exception("Unhandled error in %s", name)
                result = _error(self.render_error(UpstreamError("Internal server error", 500), name))
        log.info(
            "tool=%s ok=%s ms=%.1f args=%s",
            name,
            not result.isError,
            (time.perf_counter() - started) * 1000,
            dumps(args)[:500],
        )
        return result


def _success(value: Any) -> types.CallToolResult:
    output = value if isinstance(value, ToolOutput) else ToolOutput(value)
    return types.CallToolResult(
        content=[types.TextContent(type="text", text=dumps(output.payload))],
        structuredContent=output.structured,
        isError=False,
    )


def _error(text: str) -> types.CallToolResult:
    return types.CallToolResult(content=[types.TextContent(type="text", text=text)], isError=True)


def build_server(spec: ServerSpec) -> Server:
    server: Server = Server(spec.name, version=spec.version, instructions=spec.instructions)

    @server.list_tools()
    async def _list_tools() -> list[types.Tool]:
        return spec.list_tools()

    # Validation happens in dispatch() so error text matches the upstream server.
    @server.call_tool(validate_input=False)
    async def _call_tool(name: str, arguments: dict) -> types.CallToolResult:
        return spec.dispatch(name, arguments)

    return server


def build_asgi_app(spec: ServerSpec, path: str = "/mcp"):
    from starlette.applications import Starlette
    from starlette.responses import JSONResponse
    from starlette.routing import Route

    from mcp.server.streamable_http_manager import StreamableHTTPSessionManager

    manager = StreamableHTTPSessionManager(app=build_server(spec), json_response=False, stateless=True)

    class _McpEndpoint:
        async def __call__(self, scope, receive, send) -> None:
            await manager.handle_request(scope, receive, send)

    async def healthz(_request):
        return JSONResponse({"status": "ok", "server": spec.name, "version": spec.version, "tools": len(spec.tools)})

    @contextlib.asynccontextmanager
    async def lifespan(_app):
        async with manager.run():
            yield

    return Starlette(
        routes=[Route(path, endpoint=_McpEndpoint(), methods=["GET", "POST", "DELETE"]), Route("/healthz", healthz)],
        lifespan=lifespan,
    )


async def _run_stdio(spec: ServerSpec) -> None:
    from mcp.server.stdio import stdio_server

    server = build_server(spec)
    async with stdio_server() as (read, write):
        await server.run(read, write, server.create_initialization_options())


def main(spec_factory: Callable[[], ServerSpec], argv: Iterable[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Run a mock MCP server.")
    parser.add_argument("--transport", choices=["http", "stdio"], default=os.environ.get("MCP_TRANSPORT", "http"))
    parser.add_argument("--host", default=os.environ.get("HOST", "0.0.0.0"))
    parser.add_argument("--port", type=int, default=int(os.environ.get("PORT", "8000")))
    parser.add_argument("--log-level", default=os.environ.get("LOG_LEVEL", "INFO"))
    opts = parser.parse_args(list(argv) if argv is not None else None)

    # stdout carries the protocol on stdio, so logs always go to stderr.
    logging.basicConfig(level=opts.log_level.upper(), format="%(asctime)s %(levelname)s %(name)s %(message)s")
    spec = spec_factory()
    if opts.transport == "stdio":
        asyncio.run(_run_stdio(spec))
        return

    import uvicorn

    uvicorn.run(build_asgi_app(spec), host=opts.host, port=opts.port, log_level=opts.log_level.lower())
