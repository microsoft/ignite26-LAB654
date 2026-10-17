"""Moody's mock MCP server: entity lookup, rating history, credit opinions and beneficial owners."""

from __future__ import annotations

from mockmcp import ServerSpec

from .common import MoodysData, render_error
from .tools import FindEntity, GetCreditOpinion, GetEntityBeneficiaryOwners, GetEntityRatings

NAME = "moodys"
VERSION = "1.0.0"
INSTRUCTIONS = (
    "Mock of the Moody's MCP server for the LAB654 Ignite lab. Read-only. Call findEntity first and pass the "
    "returned entities to the other tools. NVIDIA content is recorded; other issuers are synthetic."
)


def build_spec(data: MoodysData | None = None) -> ServerSpec:
    data = data or MoodysData.default()
    tools = [FindEntity(data), GetEntityRatings(data), GetCreditOpinion(data), GetEntityBeneficiaryOwners(data)]
    return ServerSpec(NAME, VERSION, tools, instructions=INSTRUCTIONS, render_error=render_error)
