"""Move the legal scenario to new dates.

The legal story has two anchors (in __init__.py in this folder):
- LAB_DATE, the Monday of Tomás's trigger chat. The email, the group chat and
  the date the contract arrived all come before it. COEP rejects seed items
  dated in the future, so it must be before the tenant is ingested.
- NEGOTIATION_DATE, a Thursday, with go-live / contract effective date three
  days later. These are still to come in the story, so they must be after the
  last lab day.
The email, chats, iManage documents and scenario docs all mention these dates.
This script rewrites every one of them in place:

    python infra/mock_environment/tools/scenarios/legal/redate.py --lab-date 2026-10-26 --negotiation-date 2026-12-10

Rules:
- Dates before the old negotiation move by the same number of days as the lab
  date, so weekdays are kept. The negotiation moves to the new negotiation date.
- Dates on or after the effective date keep their monthly position relative
  to it (anniversaries and quarterly payments stay on the same schedule):
  Nov 14, 2031 with effective date Nov 15, 2026 becomes the day before the
  fifth anniversary of the new effective date.
- Dates without a year are taken to be within (lab date - 2 months, lab date
  + 10 months).
- Ordinals in the Markdown docs ("the 12th") are moved only for the lab date,
  the negotiation and go-live.

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
REPO_ROOT = ENV.parents[1]
LEGAL_PY = HERE / "__init__.py"
MATTER = ENV / "mock_mcp_servers" / "imanage" / "seed_files" / "Cognivault-Nexus_matter"
TEXT_FILES = [
    MATTER / "matter.json",
    HERE / "content" / "radhika_email_body.html",
]
MARKDOWN_FILES = [
    REPO_ROOT / "docs" / "scenarios" / "legal" / "scenario.md",
    REPO_ROOT / "docs" / "scenarios" / "legal" / "seed_kit.md",
    REPO_ROOT / "instructions" / "04-legal.md",
]
GO_LIVE_AFTER_NEGOTIATION = 3

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
NEG_RE = re.compile(r"NEGOTIATION_DATE = date\((\d{4}), (\d{1,2}), (\d{1,2})\)")


def add_months(d: date, n: int) -> date:
    y, m = divmod(d.month - 1 + n, 12)
    y, m = d.year + y, m + 1
    return date(y, m, min(d.day, calendar.monthrange(y, m)[1]))


class Shifter:
    def __init__(self, old_lab: date, new_lab: date, old_neg: date, new_neg: date):
        self.old_lab, self.new_lab = old_lab, new_lab
        self.old_neg, self.new_neg = old_neg, new_neg
        self.delta = new_lab - old_lab
        self.old_eff = old_neg + timedelta(GO_LIVE_AFTER_NEGOTIATION)
        self.new_eff = new_neg + timedelta(GO_LIVE_AFTER_NEGOTIATION)
        self.count = 0

    def shift(self, d: date) -> date:
        if d < self.old_neg:
            return d + self.delta
        if d < self.old_eff:
            return d + (self.new_neg - self.old_neg)
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
        for o, n in ((self.old_lab, self.new_lab), (self.old_neg, self.new_neg), (self.old_eff, self.new_eff)):
            table[o.day] = n.day

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
    ap.add_argument("--lab-date", required=True, type=date.fromisoformat, help="trigger chat date (a Monday), YYYY-MM-DD")
    ap.add_argument("--negotiation-date", required=True, type=date.fromisoformat, help="negotiation date (a Thursday), YYYY-MM-DD")
    args = ap.parse_args()
    new_lab, new_neg = args.lab_date, args.negotiation_date
    if new_lab.weekday() != 0:
        sys.exit(f"{new_lab} is a {calendar.day_name[new_lab.weekday()]}; the lab date must be a Monday.")
    if new_neg.weekday() != 3:
        sys.exit(f"{new_neg} is a {calendar.day_name[new_neg.weekday()]}; the negotiation date must be a Thursday.")
    if new_neg <= new_lab:
        sys.exit("The negotiation must come after the lab date.")

    src = LEGAL_PY.read_bytes().decode("utf-8")
    m, n = LAB_RE.search(src), NEG_RE.search(src)
    if not (m and n):
        sys.exit(f"LAB_DATE or NEGOTIATION_DATE not found in {LEGAL_PY}")
    old_lab, old_neg = date(*map(int, m.groups())), date(*map(int, n.groups()))
    if (old_lab, old_neg) == (new_lab, new_neg):
        print("Dates are already set.")
        return 0
    sh = Shifter(old_lab, new_lab, old_neg, new_neg)

    office = sorted(p for p in MATTER.rglob("*") if p.suffix in (".docx", ".xlsx"))
    for p in office:
        print(f"{rewrite_office(p, sh):4d}  {p.relative_to(ENV)}")
    for p in TEXT_FILES + MARKDOWN_FILES:
        before = sh.count
        s = sh.text(p.read_bytes().decode("utf-8"))
        if p in MARKDOWN_FILES:
            s = sh.ordinals(s)
        p.write_text(s, encoding="utf-8", newline="")
        print(f"{sh.count - before:4d}  {p.relative_to(REPO_ROOT)}")

    src = LAB_RE.sub(f"LAB_DATE = date({new_lab.year}, {new_lab.month}, {new_lab.day})", src, count=1)
    src = NEG_RE.sub(f"NEGOTIATION_DATE = date({new_neg.year}, {new_neg.month}, {new_neg.day})", src, count=1)
    LEGAL_PY.write_text(
        src,
        encoding="utf-8",
        newline="",
    )
    print(f"Lab date {old_lab} -> {new_lab}, negotiation {old_neg} -> {new_neg}; {sh.count} dates rewritten. Now run build_tenant.py.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
