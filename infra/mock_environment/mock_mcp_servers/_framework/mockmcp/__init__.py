"""mockmcp: a small, domain-agnostic framework for building mock MCP servers.

A server is a ``ServerSpec`` (name, version, tools, error renderer). Each tool is a
``Tool`` subclass with a published JSON schema and a pure ``run`` method. Data lives
in JSON (``JsonStore``); anything not seeded is generated deterministically
(``Seeded``, ``AnchoredSeries``).
"""

from .app import ServerSpec, build_asgi_app, build_server, default_renderer, dumps, main
from .datastore import JsonStore
from .errors import InvalidParams, NotEntitled, ToolError, UpstreamError
from .formatting import iso_z, tidy, us_datetime
from .schema import collect_issues, validate
from .seeded import AnchoredSeries, Seeded, bounded, round_sig, split_weights, stable_hash
from .tool import READ_ONLY, CallContext, Clock, Tool, ToolOutput

__all__ = [
    "AnchoredSeries",
    "CallContext",
    "Clock",
    "InvalidParams",
    "JsonStore",
    "NotEntitled",
    "READ_ONLY",
    "Seeded",
    "ServerSpec",
    "Tool",
    "ToolError",
    "ToolOutput",
    "UpstreamError",
    "bounded",
    "build_asgi_app",
    "build_server",
    "collect_issues",
    "default_renderer",
    "dumps",
    "iso_z",
    "main",
    "round_sig",
    "split_weights",
    "stable_hash",
    "tidy",
    "us_datetime",
    "validate",
]
