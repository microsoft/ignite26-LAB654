"""SalesDesk-style record IDs: 15 case-sensitive characters plus the 3-character case-safe suffix."""

from __future__ import annotations

import hashlib

_B62 = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
_SUFFIX = "ABCDEFGHIJKLMNOPQRSTUVWXYZ012345"


def base62(number: int, width: int) -> str:
    chars = []
    for _ in range(width):
        number, rem = divmod(number, 62)
        chars.append(_B62[rem])
    return "".join(reversed(chars))


def case_safe(id15: str) -> str:
    """Append the checksum SalesDesk uses to make 15-character IDs case-insensitive."""
    suffix = ""
    for start in range(0, 15, 5):
        bits = sum(1 << i for i, ch in enumerate(id15[start:start + 5]) if "A" <= ch <= "Z")
        suffix += _SUFFIX[bits]
    return id15 + suffix


def seed_id(prefix: str, number: int) -> str:
    return case_safe(f"{prefix}Hp00000{base62(number, 5)}")


def created_id(prefix: str, conversation_id: str | None, number: int) -> str:
    """Records created in a conversation get IDs that are unique to it, so the viewer can find their owner."""
    digest = int(hashlib.sha256((conversation_id or "-").encode()).hexdigest()[:12], 16)
    return case_safe(f"{prefix}Hq{base62(digest, 5)}{base62(number, 5)}")


def normalize(record_id: str) -> str:
    """Return the 18-character form of a 15- or 18-character ID (unchanged if it isn't one)."""
    if len(record_id) == 15 and record_id.isalnum():
        return case_safe(record_id)
    return record_id
