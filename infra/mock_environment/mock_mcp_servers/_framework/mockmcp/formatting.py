"""Small helpers for emitting numbers and dates the way upstream JSON APIs do."""

from __future__ import annotations

from datetime import date, datetime


def tidy(value: float | int | None, digits: int = 4) -> float | int | None:
    """Round, and drop the ``.0`` on whole numbers (``81615.0`` -> ``81615``)."""
    if value is None:
        return None
    rounded = round(float(value), digits)
    if rounded == 0:
        return 0
    return int(rounded) if rounded.is_integer() else rounded


def us_datetime(moment: date | datetime) -> str:
    """``MM/DD/YYYY HH:MM:SS`` (dates render as midnight)."""
    if not isinstance(moment, datetime):
        moment = datetime(moment.year, moment.month, moment.day)
    return moment.strftime("%m/%d/%Y %H:%M:%S")


def iso_z(moment: date | datetime, millis: bool = False) -> str:
    """``YYYY-MM-DDTHH:MM:SSZ`` (optionally with ``.000``); dates render as midnight."""
    if not isinstance(moment, datetime):
        moment = datetime(moment.year, moment.month, moment.day)
    text = moment.strftime("%Y-%m-%dT%H:%M:%S")
    return f"{text}.{moment.microsecond // 1000:03d}Z" if millis else f"{text}Z"
