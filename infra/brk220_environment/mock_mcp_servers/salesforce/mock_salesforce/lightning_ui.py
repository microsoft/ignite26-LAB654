"""Building blocks for the Lightning-style viewer: object icons, field labels, value formatting and SVG charts."""

from __future__ import annotations

import html

from .schema import OBJECTS, field as schema_field
from .timeutil import display_date, display_datetime, parse_date

# Standard-icon colours (as in the search API's themeInfo) and white glyphs on a 24x24 grid.
COLORS = {"Account": "#5867E8", "Contact": "#A094ED", "Opportunity": "#FF5D2D", "Lead": "#F88962",
          "Event": "#CB65FF", "Task": "#3BA755", "User": "#1B96FF", "OpportunityHistory": "#7E8BE4",
          "Dashboard": "#EF6E64", "Home": "#FF538A", "Call": "#30C85E"}
_GLYPHS = {
    "Account": "M4 21V3h11v6h5v12zM6.5 5.5v2h2v-2zm4 0v2h2v-2zm-4 4v2h2v-2zm4 0v2h2v-2zm-4 4v2h2v-2zm4 0v2h2v-2zm6-2v2h"
               "1.5v-2zm0 4v2h1.5v-2zM9 17.5V21h3v-3.5z",
    "Contact": "M3 5h18v14H3zm6 3a2.2 2.2 0 1 0 0 4.4A2.2 2.2 0 0 0 9 8zm-3.6 8.6c0-1.9 1.6-3.1 3.6-3.1s3.6 1.2 3.6 "
               "3.1zM14 9h5v1.6h-5zm0 3.2h5v1.6h-5z",
    "Opportunity": "M3 7.5l4.6 3.8L12 4.5l4.4 6.8L21 7.5l-2 10.5H5zM5 19.3h14V21H5z",
    "Lead": "M12 3a4.2 4.2 0 1 1 0 8.4A4.2 4.2 0 0 1 12 3zM3.8 21c0-4.2 3.6-7.4 8.2-7.4s8.2 3.2 8.2 7.4z",
    "User": "M12 3a4.2 4.2 0 1 1 0 8.4A4.2 4.2 0 0 1 12 3zM3.8 21c0-4.2 3.6-7.4 8.2-7.4s8.2 3.2 8.2 7.4z",
    "Task": "M9.8 17.8 4.6 12.6l1.8-1.8 3.4 3.4 7.8-7.8 1.8 1.8z",
    "Call": "M6.6 3.5 9.5 3l1.6 4.2-2 1.6a11 11 0 0 0 5.9 5.9l1.6-2 4.2 1.6-.5 2.9c-.2.9-1 1.5-1.9 1.4C10.7 18.1 "
            "5.9 13.3 5.2 5.4c-.1-.9.5-1.7 1.4-1.9z",
    "Event": "M7 2h2v2h6V2h2v2h3.5v17h-17V4H7zM5.5 9v10h13V9zM8 11h3.5v3.5H8z",
    "OpportunityHistory": "M12 3a9 9 0 1 1 0 18 9 9 0 0 1 0-18zm-1 4v6.2l5 3 .9-1.4-4.1-2.5V7z",
    "Dashboard": "M12 4.5a9 9 0 0 0-8 13.1h16a9 9 0 0 0-8-13.1zm.9 9.6a1.7 1.7 0 1 1-1.8-.1V8.2h1.8z",
    "Home": "M12 3.2 21 11h-2.8v9h-4.6v-5.6h-3.2V20H5.8v-9H3z",
}
ICON_NAMES = {"account": "Account", "contact": "Contact", "opportunity": "Opportunity", "lead": "Lead",
              "event": "Event", "task": "Task", "user": "User", "log_a_call": "Call", "dashboard": "Dashboard",
              "home": "Home", "opportunity_stage": "OpportunityHistory"}


def e(value) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def glyph_svg(kind: str, size: int) -> str:
    path = _GLYPHS.get(kind, _GLYPHS["Account"])
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" aria-hidden="true"><path fill="#fff" '
            f'fill-rule="evenodd" d="{path}"/></svg>')


def icon(kind: str, size: int = 32, round_: bool = False) -> str:
    glyph = int(size * 0.68)
    radius = "50%" if round_ else "4px"
    return (f'<span class="icon" style="width:{size}px;height:{size}px;background:{COLORS.get(kind, "#747474")};'
            f'border-radius:{radius}">{glyph_svg(kind, glyph)}</span>')


def icon_file(name: str) -> str | None:
    """Standalone SVG for /img/icon/t4v35/standard/{name}.svg (the iconUrl the search API returns)."""
    kind = ICON_NAMES.get(name)
    if kind is None:
        return None
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="120" height="120" viewBox="0 0 24 24">'
            f'<rect width="24" height="24" rx="3" fill="{COLORS[kind]}"/><g transform="translate(3.6 3.6) scale(.7)">'
            f'<path fill="#fff" fill-rule="evenodd" d="{_GLYPHS[kind]}"/></g></svg>')


def record_name(obj: str, rec: dict) -> str:
    if obj in ("Task", "Event"):
        return rec.get("Subject") or "(no subject)"
    if obj == "OpportunityHistory":
        return rec.get("StageName") or ""
    return rec.get("Name") or rec.get("Id", "")


def label(obj: str, api: str) -> str:
    obj_label = OBJECTS[obj]["label"]
    special = {"OwnerId": "Assigned To" if obj in ("Task", "Event") else f"{obj_label} Owner",
               "AccountId": "Account Name", "ContactId": "Contact", "WhoId": "Name", "WhatId": "Related To",
               "ParentId": "Parent Account", "ReportsToId": "Reports To", "ManagerId": "Manager",
               "CreatedById": "Created By", "LastModifiedById": "Last Modified By", "StageName": "Stage",
               "ActivityDate": "Due Date" if obj == "Task" else "Date", "StartDateTime": "Start",
               "EndDateTime": "End", "Competitor__c": "Competitor", "Loss_Reason__c": "Loss Reason",
               "ForecastCategoryName": "Forecast Category", "IsAllDayEvent": "All-Day Event",
               "CreatedDate": "Created Date", "LastModifiedDate": "Last Modified Date"}
    if api in special:
        return special[api]
    if api == "Name" and obj in ("Opportunity", "Account"):
        return f"{obj_label} Name"
    meta = schema_field(obj, api)
    return meta[1] if meta else api


def money(value, cents: bool = True) -> str:
    if value is None:
        return ""
    return f"${value:,.2f}" if cents else f"${value:,.0f}"


def compact(value: float) -> str:
    for size, suffix in ((1e9, "B"), (1e6, "M"), (1e3, "K")):
        if abs(value) >= size:
            text = f"{value / size:.1f}".rstrip("0").rstrip(".")
            return f"${text}{suffix}"
    return f"${value:,.0f}"


def plain(obj: str, api: str, rec: dict) -> str:
    """Text form of a field value (no links)."""
    value = rec.get(api)
    if value is None or value == "":
        return ""
    meta = schema_field(obj, api)
    kind = meta[2] if meta else ""
    if kind == "CURRENCY":
        return money(value)
    if kind == "PERCENT":
        return f"{value:g}%"
    if kind == "DATE":
        day = parse_date(value)
        return display_date(day) if day else str(value)
    if kind == "DATETIME":
        return display_datetime(value)
    if kind == "INT":
        return f"{value:,}"
    if kind == "BOOLEAN":
        return "True" if value else "False"
    return str(value)


# --- SVG charts (Lightning dashboard palette) ---------------------------------------------------------------------
PALETTE = ["#52B7D8", "#E16032", "#FFB03B", "#54A77B", "#4FD2D2", "#E287B2", "#A77FE8"]
_AXIS = "#c9c9c9"
_TXT = "#444"


def _nice_max(value: float) -> float:
    if value <= 0:
        return 1.0
    step = 10 ** (len(str(int(value))) - 1)
    for mult in (1, 2, 2.5, 5, 10):
        if value <= step * mult:
            return step * mult
    return step * 10


def _grid(x0: int, x1: int, y0: int, y1: int, top: float, ticks: int = 4) -> str:
    out = []
    for i in range(ticks + 1):
        y = y1 - (y1 - y0) * i / ticks
        out.append(f'<line x1="{x0}" x2="{x1}" y1="{y:.1f}" y2="{y:.1f}" stroke="{"#e5e5e5" if i else _AXIS}"/>'
                   f'<text x="{x0 - 6}" y="{y + 4:.1f}" text-anchor="end" font-size="11" fill="{_TXT}">'
                   f'{e(compact(top * i / ticks))}</text>')
    return "".join(out)


def column_chart(categories: list[str], series: list[tuple[str, list[float]]], width: int = 560,
                 height: int = 260, x_title: str = "", y_title: str = "Sum of Amount", stacked: bool = False) -> str:
    x0, x1, y0, y1 = 64, width - 12, 14, height - 52
    totals = [sum(s[1][i] for s in series) for i in range(len(categories))] if stacked else \
        [max((s[1][i] for s in series), default=0) for i in range(len(categories))]
    top = _nice_max(max(totals, default=0))
    band = (x1 - x0) / max(len(categories), 1)
    groups = 1 if stacked else len(series)
    bar = min(56, band * 0.6 / groups)
    parts = [f'<svg class="chart" viewBox="0 0 {width} {height}" width="100%" role="img">', _grid(x0, x1, y0, y1, top)]
    for i, cat in enumerate(categories):
        cx = x0 + band * (i + 0.5)
        base = y1
        for j, (name, data) in enumerate(series):
            value = data[i]
            h = (y1 - y0) * value / top
            x = cx - bar * groups / 2 + (0 if stacked else j * bar)
            y = base - h
            if value:
                parts.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar:.1f}" height="{h:.1f}" '
                             f'fill="{PALETTE[j % len(PALETTE)]}"><title>{e(name)}: {e(money(value, False))}</title>'
                             f'</rect>')
                if not stacked:
                    parts.append(f'<text x="{x + bar / 2:.1f}" y="{y - 4:.1f}" text-anchor="middle" font-size="11" '
                                 f'fill="{_TXT}">{e(compact(value))}</text>')
            if stacked:
                base = y
        parts.append(f'<text x="{cx:.1f}" y="{y1 + 16}" text-anchor="middle" font-size="11" fill="{_TXT}">'
                     f'{e(cat)}</text>')
    if x_title:
        parts.append(f'<text x="{(x0 + x1) / 2:.1f}" y="{height - 8}" text-anchor="middle" font-size="12" '
                     f'fill="{_TXT}">{e(x_title)}</text>')
    parts.append(f'<text transform="translate(14 {(y0 + y1) / 2:.1f}) rotate(-90)" text-anchor="middle" '
                 f'font-size="12" fill="{_TXT}">{e(y_title)}</text></svg>')
    return "".join(parts)


def legend(names: list[str]) -> str:
    return '<div class="legend">' + "".join(
        f'<span><i style="background:{PALETTE[i % len(PALETTE)]}"></i>{e(n)}</span>' for i, n in enumerate(names)) + \
        "</div>"


def donut(slices: list[tuple[str, float]], center_label: str, size: int = 220) -> str:
    import math
    total = sum(v for _, v in slices) or 1
    r, cx, cy, stroke = 70, size / 2, size / 2, 34
    circ = 2 * math.pi * r
    parts = [f'<svg class="chart" viewBox="0 0 {size} {size}" width="{size}" height="{size}" role="img">']
    offset = 0.0
    for i, (name, value) in enumerate(slices):
        length = circ * value / total
        parts.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{PALETTE[i % len(PALETTE)]}" '
                     f'stroke-width="{stroke}" stroke-dasharray="{length:.2f} {circ - length:.2f}" '
                     f'stroke-dashoffset="{-offset:.2f}" transform="rotate(-90 {cx} {cy})"><title>{e(name)}: '
                     f'{e(money(value, False))}</title></circle>')
        offset += length
    parts.append(f'<text x="{cx}" y="{cy - 2}" text-anchor="middle" font-size="22" fill="#181818">'
                 f'{e(compact(total))}</text><text x="{cx}" y="{cy + 16}" text-anchor="middle" font-size="11" '
                 f'fill="{_TXT}">{e(center_label)}</text></svg>')
    return "".join(parts)


def gauge(value: float, bands: tuple[float, float] = (40, 60), width: int = 260) -> str:
    """Half-circle gauge for a 0-100 percentage with red / yellow / green bands."""
    import math
    cx, cy, r = width / 2, 120, 92

    def point(pct: float, radius: float) -> tuple[float, float]:
        angle = math.pi * (1 - pct / 100)
        return cx + radius * math.cos(angle), cy - radius * math.sin(angle)

    def arc(a: float, b: float, color: str) -> str:
        (x1, y1), (x2, y2) = point(a, r), point(b, r)
        return (f'<path d="M{x1:.1f} {y1:.1f} A{r} {r} 0 0 1 {x2:.1f} {y2:.1f}" fill="none" stroke="{color}" '
                f'stroke-width="26"/>')

    nx, ny = point(max(0, min(100, value)), r - 22)
    return (f'<svg class="chart" viewBox="0 0 {width} 150" width="100%" role="img">'
            f'{arc(0, bands[0], "#ea001e")}{arc(bands[0], bands[1], "#fe9339")}{arc(bands[1], 100, "#45c65a")}'
            f'<line x1="{cx}" y1="{cy}" x2="{nx:.1f}" y2="{ny:.1f}" stroke="#181818" stroke-width="3"/>'
            f'<circle cx="{cx}" cy="{cy}" r="6" fill="#181818"/>'
            f'<text x="{cx}" y="{cy + 26}" text-anchor="middle" font-size="22" fill="#181818">{value:.1f}%</text>'
            f'<text x="{cx - r}" y="{cy + 18}" text-anchor="middle" font-size="11" fill="{_TXT}">0%</text>'
            f'<text x="{cx + r}" y="{cy + 18}" text-anchor="middle" font-size="11" fill="{_TXT}">100%</text></svg>')


def line_chart(x_labels: list[str], lines: list[tuple[str, str, list[tuple[float, float]], bool]],
               top_value: float, width: int = 640, height: int = 230, today: float | None = None) -> str:
    """``lines`` are (name, colour, [(x 0..1, value)], dashed)."""
    x0, x1, y0, y1 = 64, width - 16, 12, height - 30
    top = _nice_max(top_value)
    parts = [f'<svg class="chart" viewBox="0 0 {width} {height}" width="100%" role="img">', _grid(x0, x1, y0, y1, top)]
    for i, lab in enumerate(x_labels):
        x = x0 + (x1 - x0) * (i + 0.5) / len(x_labels)
        parts.append(f'<text x="{x:.1f}" y="{y1 + 18}" text-anchor="middle" font-size="11" fill="{_TXT}">'
                     f'{e(lab)}</text>')
    if today is not None:
        tx = x0 + (x1 - x0) * today
        parts.append(f'<line x1="{tx:.1f}" x2="{tx:.1f}" y1="{y0}" y2="{y1}" stroke="#747474" '
                     f'stroke-dasharray="3 3"/><text x="{tx + 4:.1f}" y="{y0 + 10}" font-size="10" fill="{_TXT}">'
                     f'Today</text>')
    for name, color, points, dashed in lines:
        if not points:
            continue
        coords = " ".join(f"{x0 + (x1 - x0) * px:.1f},{y1 - (y1 - y0) * v / top:.1f}" for px, v in points)
        dash = ' stroke-dasharray="6 4"' if dashed else ""
        parts.append(f'<polyline points="{coords}" fill="none" stroke="{color}" stroke-width="2.5"{dash}>'
                     f'<title>{e(name)}</title></polyline>')
        lx, lv = points[-1]
        parts.append(f'<circle cx="{x0 + (x1 - x0) * lx:.1f}" cy="{y1 - (y1 - y0) * lv / top:.1f}" r="3.5" '
                     f'fill="{color}"/>')
    parts.append("</svg>")
    return "".join(parts)
