"""Move the legal scenario to a new lab date.

The legal story is pinned to a Monday "lab date" (LAB_DATE in __init__.py in
this folder). The email, chats, iManage documents and scenario docs all
mention dates relative to it, and COEP rejects seed items dated in the future.
This script rewrites every one of those dates in place so the story keeps the
same shape around a new Monday:

    python tools/scenarios/legal/redate.py --lab-date 2026-10-12

Rules:
- Dates before the contract effective date (lab date + 6) move by the same
  number of days, so weekdays are kept.
- Dates on or after the effective date keep their monthly position relative
  to it (anniversaries and quarterly payments stay on the same schedule):
  Nov 14, 2031 with effective date Nov 15, 2026 becomes the day before the
  fifth anniversary of the new effective date.
- Dates without a year are taken to be within (lab date - 2 months, lab date
  + 10 months).
- Ordinals in the Markdown docs ("the 12th") are moved only for the lab date,
  the negotiation (lab date + 3) and go-live (lab date + 6).

Afterwards run build_tenant.py to regenerate the tenant JSON.
"""

from __future__ import annotations

import argparse
import calendar
import os
import re
import shutil
import sys
import tempfile
import zipfile
from datetime import date, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent
ENV = HERE.parents[2]
REPO_SRC = ENV.parent
LEGAL_PY = HERE / "__init__.py"
MATTER = ENV / "mock_mcp_servers" / "imanage" / "seed_files" / "Cognivault-Nexus_matter"
TEXT_FILES = [
    MATTER / "matter.json",
    HERE / "content" / "radhika_email_body.html",
]
MARKDOWN_FILES = [
    REPO_SRC / "scenarios" / "legal" / "scenario.md",
    REPO_SRC / "scenarios" / "legal" / "seed_kit.md",
]
GO_LIVE_OFFSET = 6
STORY_OFFSETS = (0, 3, GO_LIVE_OFFSET)

MONTHS = {m.lower(): i for i, m in enumerate(calendar.month_name) if m}
MONTHS.update({m.lower(): i for i, m in enumerate(calendar.month_abbr) if m})
MONTHS["sept"] = 9
WEEKDAYS = {d.lower(): i for i, d in enumerate(calendar.day_name)}
WEEKDAYS.update({d.lower(): i for i, d in enumerate(calendar.day_abbr)})

DATE_RE = re.compile(
    r"(?:(?P<wd>Mon|Tue|Wed|Thu|Fri|Sat|Sun)(?P<wdrest>day|sday|nesday|rsday|urday)?(?P<wdsep>,?\s+))?"
    r"(?P<mon>Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)(?P<monrest>[a-z]*)(?P<dot>\.?)"
    r"(?P<sp>\s+)(?P<day>\d{1,2})(?!\d|st|nd|rd|th)"
    r"(?:(?P<ysep>,?\s+)(?P<year>20\d\d)(?!\d))?"
)
LAB_RE = re.compile(r"LAB_DATE = date\((\d{4}), (\d{1,2}), (\d{1,2})\)")


def add_months(d: date, n: int) -> date:
    y, m = divmod(d.month - 1 + n, 12)
    y, m = d.year + y, m + 1
    return date(y, m, min(d.day, calendar.monthrange(y, m)[1]))


class Shifter:
    def __init__(self, old_lab: date, new_lab: date):
        self.old_lab, self.new_lab = old_lab, new_lab
        self.delta = new_lab - old_lab
        self.old_eff = old_lab + timedelta(GO_LIVE_OFFSET)
        self.new_eff = new_lab + timedelta(GO_LIVE_OFFSET)
        self.count = 0

    def shift(self, d: date) -> date:
        if d < self.old_eff:
            return d + self.delta
        months = (d.year - self.old_eff.year) * 12 + d.month - self.old_eff.month
        return add_months(self.new_eff, months) + timedelta(d.day - self.old_eff.day)

    def infer_year(self, month: int, day: int) -> date:
        lo = add_months(self.old_lab, -2)
        for y in (self.old_lab.year - 1, self.old_lab.year, self.old_lab.year + 1):
            try:
                d = date(y, month, day)
            except ValueError:
                continue
            if lo <= d < add_months(self.old_lab, 10):
                return d
        raise ValueError(f"can't place {month}/{day} near {self.old_lab}")

    def _date(self, m: re.Match) -> str:
        month = MONTHS.get((m["mon"] + m["monrest"]).lower())
        if month is None:  # e.g. "Mayor", "Decision"
            return m[0]
        day = int(m["day"])
        old = date(int(m["year"]), month, day) if m["year"] else self.infer_year(month, day)
        new = self.shift(old)
        if new == old:
            return m[0]
        self.count += 1
        written = m["mon"] + m["monrest"]
        full = len(written) > 3
        if written == "May":  # same in both forms; follow other month names in the same text node/line
            s = m.string
            lo = max(s.rfind("<", 0, m.start()), s.rfind(">", 0, m.start()), s.rfind("\n", 0, m.start())) + 1
            hi = min((i for i in (s.find("<", m.end()), s.find("\n", m.end())) if i >= 0), default=len(s))
            near = re.findall(r"\b(?:Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*", s[lo:hi])
            full = any(len(w) > 4 for w in near) if near else True
        name = calendar.month_name[new.month] if full else calendar.month_abbr[new.month]
        if m["monrest"] == "t" and new.month == 9:  # "Sept"
            name = "Sept"
        out = f"{name}{m['dot']}{m['sp']}{new.day}"
        if m["year"]:
            out += f"{m['ysep']}{new.year}"
        if m["wd"]:
            wd_full = bool(m["wdrest"])
            wd = calendar.day_name[new.weekday()] if wd_full else calendar.day_abbr[new.weekday()]
            out = f"{wd}{m['wdsep']}{out}"
        return out

    def text(self, s: str) -> str:
        return DATE_RE.sub(self._date, s)

    def ordinals(self, s: str) -> str:
        table = {}
        for k in STORY_OFFSETS:
            o, n = (self.old_lab + timedelta(k)).day, (self.new_lab + timedelta(k)).day
            table[o] = n

        def sub(m: re.Match) -> str:
            n = table.get(int(m[1]))
            if n is None or n == int(m[1]):
                return m[0]
            self.count += 1
            return f"{n}{'th' if 11 <= n <= 13 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"

        return re.sub(r"\b(\d{1,2})(?:st|nd|rd|th)\b", sub, s)


def office_parts(name: str) -> bool:
    return name.endswith(".xml") and (
        name.startswith("word/") or name == "xl/sharedStrings.xml" or name.startswith("xl/worksheets/")
    )


def rewrite_office(path: Path, sh: Shifter) -> int:
    before = sh.count
    fd, name = tempfile.mkstemp(suffix=path.suffix)
    os.close(fd)
    tmp = Path(name)
    with zipfile.ZipFile(path) as zin, zipfile.ZipFile(tmp, "w") as zout:
        for info in zin.infolist():
            data = zin.read(info)
            if office_parts(info.filename):
                data = sh.text(data.decode("utf-8")).encode("utf-8")
            zout.writestr(info, data)
    shutil.move(tmp, path)
    return sh.count - before


def office_text(path: Path) -> str:
    with zipfile.ZipFile(path) as z:
        return " ".join(re.sub(r"<[^>]+>", "", z.read(n).decode("utf-8")) for n in z.namelist() if office_parts(n))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--lab-date", required=True, type=date.fromisoformat, help="new lab date (a Monday), YYYY-MM-DD")
    new_lab = ap.parse_args().lab_date
    if new_lab.weekday() != 0:
        sys.exit(f"{new_lab} is a {calendar.day_name[new_lab.weekday()]}; the lab date must be a Monday.")

    src = LEGAL_PY.read_bytes().decode("utf-8")
    m = LAB_RE.search(src)
    if not m:
        sys.exit(f"LAB_DATE not found in {LEGAL_PY}")
    old_lab = date(*map(int, m.groups()))
    if old_lab == new_lab:
        print(f"Lab date is already {new_lab}.")
        return 0
    sh = Shifter(old_lab, new_lab)

    office = sorted(p for p in MATTER.rglob("*") if p.suffix in (".docx", ".xlsx"))
    for p in office:
        print(f"{rewrite_office(p, sh):4d}  {p.relative_to(ENV)}")
    for p in TEXT_FILES + MARKDOWN_FILES:
        before = sh.count
        s = sh.text(p.read_bytes().decode("utf-8"))
        if p in MARKDOWN_FILES:
            s = sh.ordinals(s)
        p.write_text(s, encoding="utf-8", newline="")
        print(f"{sh.count - before:4d}  {p.relative_to(REPO_SRC)}")

    LEGAL_PY.write_text(
        LAB_RE.sub(f"LAB_DATE = date({new_lab.year}, {new_lab.month}, {new_lab.day})", src, count=1),
        encoding="utf-8",
        newline="",
    )
    print(f"Lab date {old_lab} -> {new_lab}; {sh.count} dates rewritten. Now run build_tenant.py.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
