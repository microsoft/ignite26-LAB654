"""Build ``seed_files/workspace.json`` (and optionally ``tool_schemas.json``) for the iManage mock.

Run from ``infra/mock_environment/mock_mcp_servers``:

    python imanage/scripts/build_seed.py
    python imanage/scripts/build_seed.py --tools <path to imanage_tools.json from an Office debug trace>

Reads the matter under ``seed_files/TreyResearch-AIPlatform_matter`` (``matter.json`` plus the files),
extracts each document's text the way the live ``fetch`` tool returns it (header line, then paragraphs and
table cells one per line, then footer lines and the page count), and writes one JSON file the server
loads at start-up. Needs python-docx and openpyxl (dev only; the server itself doesn't).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SEED = ROOT / "seed_files"
MATTER_DIR = SEED / "TreyResearch-AIPlatform_matter"

LIBRARY = "DEV"
WORKSPACE_ID = "Dev!1870"
WORKSPACE_NUMBER = 252553
FIRST_FOLDER = 1871
FIRST_DOCUMENT = 252561
PLAYBOOK_NUMBER = 252567  # the number the recorded trace fetched
OWNER = "EMIL"
CREATED = "2026-10-16T15:12:04.118Z"  # the vendor draft arrived Oct 16, 2026
EDITED = "2026-10-16T15:31:47.602Z"

# Matches the legal tenant personas (tools/scenarios/legal/__init__.py).
USERS = [
    {"id": "EMIL", "full_name": "Emil Vanggaard", "email": "emil@zava-online.com",
     "job_title": "Associate General Counsel, Technology Transactions"},
    {"id": "HEMANTI", "full_name": "Hemanti Baishya", "email": "hemanti@zava-online.com",
     "job_title": "SVP, Strategic Procurement & Vendor Management"},
    {"id": "LUC", "full_name": "Luc Lacombe", "email": "luc@zava-online.com",
     "job_title": "Chief Underwriting Officer"},
]

TOOL_PREFIX = re.compile(r"^mcp__[0-9a-f-]+__")
RENAMES = {"get_contai_3000dcfbaf": "get_container_children", "get_worksp_69b8a97f9b": "get_workspace_templates"}
FORBIDDEN = ("cloudimanage", "microsoftgc", "verdantis", "cognivault", "vti-legal", "hyi")
TYPE_DESCRIPTIONS = {"docx": "WORD 2007", "xlsx": "EXCEL 2007"}


def _runs_text(element) -> str:
    from docx.oxml.ns import qn

    return "".join(t.text or "" for t in element.iter(qn("w:t"))).strip()


def docx_text(path: Path) -> str:
    from docx import Document
    from docx.oxml.ns import qn

    doc = Document(str(path))
    section = doc.sections[0]
    lines = [p.text.strip() for p in section.header.paragraphs if p.text.strip()]
    for child in doc.element.body.iterchildren():
        if child.tag == qn("w:p"):
            text = _runs_text(child)
            if text:
                lines.append(text)
        elif child.tag == qn("w:tbl"):
            for cell in child.iter(qn("w:tc")):
                text = "\n".join(t for t in (_runs_text(p) for p in cell.iter(qn("w:p"))) if t)
                if text:
                    lines.append(text)
    # Footer page fields (PAGE / NUMPAGES) render as "1 of 1" in the live text, so drop their cached values.
    page_label = False
    for p in section.footer.paragraphs:
        text = re.sub(r"\s*\d*\s*of\s*\d*\s*$", "", p.text.strip()).strip()
        if text.endswith("Page"):
            page_label = True
            text = text[:-4].rstrip(" |\u2013\u2014-")
        if text:
            lines.append(text)
    lines.append("Page 1 of 1" if page_label else "1 of 1")
    return "\n".join(lines) + "\n"


def _cell(value) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    if hasattr(value, "strftime"):
        return value.strftime("%Y-%m-%d")
    return str(value).strip()


def xlsx_text(path: Path) -> str:
    """Assumed rendering (no xlsx was fetched in the trace): sheet name, then one line per row."""
    from openpyxl import load_workbook

    wb = load_workbook(str(path), data_only=True)
    lines: list[str] = []
    for ws in wb.worksheets:
        lines.append(ws.title)
        for row in ws.iter_rows(values_only=True):
            cells = [_cell(v) for v in row]
            while cells and not cells[-1]:
                cells.pop()
            if any(cells):
                lines.append(" | ".join(cells))
    return "\n".join(lines) + "\n"


def build_workspace() -> dict:
    matter = json.loads((MATTER_DIR / "matter.json").read_text(encoding="utf-8"))
    folders, documents = [], []
    number = FIRST_DOCUMENT
    for i, folder in enumerate(matter["folders"]):
        folder_id = f"Dev!{FIRST_FOLDER + i}"
        folders.append({"id": folder_id, "name": folder["name"], "parent_id": WORKSPACE_ID,
                        "description": folder.get("description", ""), "writable": bool(folder.get("writable")),
                        "owner": OWNER, "create_date": CREATED, "edit_date": CREATED})
        for doc in folder["documents"]:
            path = MATTER_DIR / doc["file"]
            ext = path.suffix.lstrip(".").lower()
            if doc["docType"] == "Playbook":
                doc_number = PLAYBOOK_NUMBER
            else:
                doc_number, number = number, number + 1
            documents.append({
                "number": doc_number, "version": 1, "name": path.stem, "extension": ext,
                "type_description": TYPE_DESCRIPTIONS[ext], "folder_id": folder_id, "author": OWNER,
                "comment": doc["description"], "doc_type": doc["docType"], "size": path.stat().st_size,
                "create_date": CREATED, "edit_date": CREATED, "edit_profile_date": EDITED,
                "text": docx_text(path) if ext == "docx" else xlsx_text(path),
            })
    documents.sort(key=lambda d: d["number"])
    return {
        "_source": "Built by imanage/scripts/build_seed.py from seed_files/TreyResearch-AIPlatform_matter. "
                   "Don't edit by hand.",
        "library": LIBRARY,
        "current_user": OWNER,
        "users": USERS,
        "workspace": {"id": WORKSPACE_ID, "document_number": WORKSPACE_NUMBER, "name": matter["matter"],
                      "description": f"{matter['client']} matter: {matter['matter']}", "client": matter["client"],
                      "owner": OWNER, "create_date": CREATED, "edit_date": EDITED},
        "folders": folders,
        "documents": documents,
        "next_folder": FIRST_FOLDER + len(folders),
        "next_document": max(PLAYBOOK_NUMBER, number) + 1,
    }


def clean_tools(raw_path: Path) -> list[dict]:
    tools = []
    for item in json.loads(raw_path.read_text(encoding="utf-8")):
        name = TOOL_PREFIX.sub("", item["name"])
        if name == "load_tools":
            continue
        description = item["description"]
        if "\ufffd" in description:  # the trace stored an em dash and bullets as replacement characters
            description = description.replace("find\ufffdsuch", "find\u2014such").replace("\ufffd", "\u2022")
        tools.append({"name": RENAMES.get(name, name), "description": description,
                      "inputSchema": item["inputSchema"]})
    return tools


def check(text: str, label: str) -> None:
    lowered = text.lower()
    bad = [w for w in FORBIDDEN if re.search(rf"\b{re.escape(w)}\b", lowered)]
    if bad:
        sys.exit(f"{label} still mentions {bad}; fix the source before seeding.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the iManage mock's seed files.")
    parser.add_argument("--tools", type=Path, help="imanage_tools.json from an Office debug trace")
    args = parser.parse_args()

    workspace = build_workspace()
    text = json.dumps(workspace, ensure_ascii=False, indent=1)
    check(text, "workspace.json")
    (SEED / "workspace.json").write_text(text + "\n", encoding="utf-8")
    print(f"workspace.json: {len(workspace['folders'])} folders, {len(workspace['documents'])} documents")

    if args.tools:
        tools = clean_tools(args.tools)
        text = json.dumps(tools, ensure_ascii=False, indent=1)
        check(text, "tool_schemas.json")
        (SEED / "tool_schemas.json").write_text(text + "\n", encoding="utf-8")
        print(f"tool_schemas.json: {len(tools)} tools: {', '.join(t['name'] for t in tools)}")


if __name__ == "__main__":
    main()
