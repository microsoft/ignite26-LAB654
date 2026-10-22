"""Server-rendered pages, so a crawler (or a lab attendee's browser) sees the full text without JavaScript."""

from __future__ import annotations

import json
from datetime import date
from html import escape
from pathlib import Path

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse, PlainTextResponse, Response
from starlette.routing import Route

PAGES_PATH = Path(__file__).resolve().parent.parent / "seed_files" / "pages.json"

SECTIONS = {
    "retail": "Retail",
    "procurement": "Procurement",
    "comms": "Communications",
    "customer-service": "Customer Service",
    "products": "Products",
    "finance": "Finance",
}

CSS = """
*{box-sizing:border-box}
body{margin:0;font:15px/1.6 "Segoe UI",system-ui,-apple-system,sans-serif;color:#1f2a24;background:#f4f6f3}
a{color:#13734b}a:hover{color:#0b5134}
.suite{background:#0f3d2a;color:#fff;height:44px;display:flex;align-items:center;padding:0 20px;gap:14px}
.suite .logo{width:26px;height:26px;border-radius:6px;background:linear-gradient(135deg,#4cc38a,#13734b);display:grid;place-items:center;font-weight:700}
.suite .name{font-weight:600;letter-spacing:.2px}.suite .name span{opacity:.7;font-weight:400}
.suite input{margin-left:auto;width:280px;max-width:40vw;border:0;border-radius:4px;padding:6px 10px;background:#ffffff26;color:#fff}
.suite input::placeholder{color:#ffffffb3}
.hero{background:#fff;border-bottom:1px solid #dde3dc;padding:18px 32px}
.hero h2{margin:0;font-size:22px;font-weight:600}
.hero nav.tabs a{margin-right:22px;font-size:14px;color:#3d4a43;text-decoration:none}
.hero nav.tabs a.on{color:#13734b;border-bottom:2px solid #13734b;padding-bottom:4px}
.wrap{display:grid;grid-template-columns:220px 1fr;gap:28px;max-width:1180px;margin:24px auto;padding:0 24px}
aside h3{font-size:12px;text-transform:uppercase;letter-spacing:.6px;color:#6b776f;margin:0 0 8px}
aside a{display:block;padding:6px 10px;border-radius:4px;text-decoration:none;color:#2a362f;font-size:14px}
aside a:hover,aside a.on{background:#e3eee7;color:#0b5134}
article{background:#fff;border:1px solid #dde3dc;border-radius:8px;padding:28px 40px 36px;min-width:0}
article nav ol{list-style:none;padding:0;margin:0 0 6px;display:flex;flex-wrap:wrap;font-size:13px;color:#6b776f}
article nav li+li:before{content:"\\203A";margin:0 8px;color:#9aa59e}
article h1{font-size:30px;line-height:1.25;margin:8px 0 4px;font-weight:600}
article h1+p em{color:#6b776f;font-style:normal;font-size:13px}
article h2{font-size:20px;margin:28px 0 8px;font-weight:600}
article h3{font-size:16px;margin:20px 0 6px}
article table{border-collapse:collapse;width:100%;margin:12px 0;font-size:14px}
article th,article td{border:1px solid #dde3dc;padding:8px 10px;text-align:left;vertical-align:top}
article th{background:#f0f4f1}
article blockquote{margin:16px 0;padding:12px 16px;border-left:4px solid #d4a017;background:#fdf6e3}
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:14px;margin-top:16px}
.card{display:block;border:1px solid #dde3dc;border-radius:8px;padding:14px 16px;text-decoration:none;color:inherit;background:#fbfcfb}
.card:hover{border-color:#13734b}.card b{display:block;color:#13734b;margin-bottom:4px}.card small{color:#6b776f}
footer{max-width:1180px;margin:0 auto 40px;padding:0 24px;font-size:12px;color:#7a857e}
.mock{position:fixed;right:16px;bottom:16px;background:#7a2e0e;color:#fff;font-size:12px;font-weight:600;padding:6px 12px;border-radius:999px;box-shadow:0 2px 8px #0003;z-index:9}
@media(max-width:760px){.wrap{grid-template-columns:1fr}aside{display:none}article{padding:20px}}
"""


def load_pages(path: Path = PAGES_PATH) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))


def _shell(title: str, main: str, active: str, pages: list[dict], description: str = "") -> str:
    side = "".join(
        f'<a href="/{key}"{" class=on" if active == key else ""}>{label}</a>'
        for key, label in SECTIONS.items() if any(p["path"].startswith(f"/{key}/") for p in pages))
    meta = f'<meta name="description" content="{escape(description)}">' if description else ""
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>{escape(title)} - Verdantis Hub</title>{meta}
<style>{CSS}</style></head><body>
<div class="suite"><div class="logo">V</div><div class="name">Verdantis Hub <span>&middot; Intranet</span></div>
<input type="search" placeholder="Search Verdantis Hub" aria-label="Search (not available in the mock)" disabled></div>
<div class="hero"><h2>Verdantis Hub</h2><nav class="tabs"><a href="/"{" class=on" if active == "" else ""}>Home</a>
<a href="/retail">Retail</a><a href="/procurement">Procurement</a><a href="/comms">Communications</a></nav></div>
<div class="wrap"><aside><h3>Sections</h3>{side}</aside><article>{main}</article></div>
<footer>Verdantis, Inc. internal site &middot; Stamford, CT</footer>
<div class="mock" title="Sample data for the Microsoft Ignite LAB654 lab. Not a real company intranet.">MOCK INTRANET &middot; LAB654</div>
</body></html>"""


def _cards(items: list[dict]) -> str:
    cards = "".join(
        f'<a class="card" href="{escape(p["path"])}"><b>{escape(p["title"])}</b>'
        f'{escape(p["description"][:150].rsplit(" ", 1)[0])}&hellip;<br>'
        f'<small>Updated {_long(p["updated"])}</small></a>' for p in items)
    return f'<div class="cards">{cards}</div>'


def _long(iso: str) -> str:
    d = date.fromisoformat(iso)
    return f"{d:%B} {d.day}, {d.year}"


def build_app(pages: list[dict] | None = None) -> Starlette:
    pages = pages if pages is not None else load_pages()
    by_path = {p["path"]: p for p in pages}

    def home(request: Request) -> Response:
        current = [p for p in pages if "archived" not in p["title"].lower()]
        main = ("<h1>Welcome to Verdantis Hub</h1><p>Policies, playbooks and guidance for everyone at Verdantis.</p>"
                "<h2>Featured</h2>" + _cards(current))
        return HTMLResponse(_shell("Home", main, "", pages))

    def page(request: Request) -> Response:
        path = "/" + request.path_params["path"].strip("/")
        found = by_path.get(path)
        section = path.strip("/").split("/")[0]
        if found:
            return HTMLResponse(_shell(found["title"], found["html"], section, pages, found["description"]))
        under = [p for p in pages if p["path"].startswith(path + "/")]
        if not under:
            return HTMLResponse(_shell("Page not found", "<h1>Page not found</h1><p>This page doesn't exist on "
                                       'Verdantis Hub. <a href="/">Go to the home page</a>.</p>', "", pages),
                                status_code=404)
        label = SECTIONS.get(section, section.replace("-", " ").title())
        crumbs = '<nav aria-label="Breadcrumb"><ol><li><a href="/">Home</a></li>'
        crumbs += f"<li>{escape(label if path == '/' + section else path.rsplit('/', 1)[1].replace('-', ' ').title())}</li></ol></nav>"
        return HTMLResponse(_shell(label, f"{crumbs}<h1>{escape(label)}</h1>" + _cards(under), section, pages))

    def sitemap(request: Request) -> Response:
        base = str(request.base_url).rstrip("/")
        urls = "".join(f"<url><loc>{base}{escape(p['path'])}</loc><lastmod>{p['updated']}</lastmod></url>"
                       for p in pages)
        return Response('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/'
                        f'sitemap/0.9">{urls}</urlset>', media_type="application/xml")

    def robots(request: Request) -> Response:
        return PlainTextResponse(f"User-agent: *\nAllow: /\nSitemap: {str(request.base_url).rstrip('/')}/sitemap.xml\n")

    def healthz(request: Request) -> Response:
        return JSONResponse({"status": "ok", "pages": len(pages)})

    return Starlette(routes=[
        Route("/", home), Route("/healthz", healthz), Route("/sitemap.xml", sitemap), Route("/robots.txt", robots),
        Route("/{path:path}", page),
    ])
