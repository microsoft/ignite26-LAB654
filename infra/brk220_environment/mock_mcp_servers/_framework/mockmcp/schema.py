"""JSON Schema validation with upstream-style error messages.

Schemas are plain JSON Schema (draft 2020-12) so they can be published verbatim as the
tool's ``inputSchema``. Add an ``errorMessage`` keyword (a string or a list of strings)
to any subschema to replace the generic jsonschema text with the upstream server's
wording when that subschema fails.
"""

from __future__ import annotations

from typing import Any

from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError

from .errors import InvalidParams


def _path(error: ValidationError) -> str:
    parts = [str(p) for p in error.absolute_path]
    return ".".join(parts) if parts else "(root)"


def _messages(error: ValidationError) -> list[str]:
    custom = error.schema.get("errorMessage") if isinstance(error.schema, dict) else None
    if isinstance(custom, str):
        return [custom]
    if isinstance(custom, list):
        return [str(m) for m in custom]
    return [f"{_path(error)}: {error.message}"]


def collect_issues(instance: Any, schema: dict) -> list[str]:
    """Return de-duplicated, ordered validation messages (empty when valid)."""
    validator = Draft202012Validator(schema)
    issues: list[str] = []
    for error in sorted(validator.iter_errors(instance), key=lambda e: list(map(str, e.absolute_path))):
        for message in _messages(error):
            if message not in issues:
                issues.append(message)
    return issues


def validate(instance: Any, schema: dict) -> None:
    """Raise ``InvalidParams`` when ``instance`` doesn't match ``schema``."""
    issues = collect_issues(instance, schema)
    if issues:
        raise InvalidParams(issues)
