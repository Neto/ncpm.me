#!/usr/bin/env python3
"""Build the site from src/.

src/template.html  -> index.html          (Spin and Grabb sales page)
src/company.html   -> company/index.html  (Spinoff Software home)
src/privacy.html   -> privacy/index.html  (Privacy Policy)

Embeds the app icons, adds the shared head and footer, and fills in the contact address.
"""
import base64
import pathlib
import re

CONTACT = "CONTACT_PENDING@example.com"  # support address shown on the site

root = pathlib.Path(__file__).resolve().parent
src = root / "src"


def data_uri(name):
    return "data:image/png;base64," + base64.b64encode((src / name).read_bytes()).decode()


ICONS = {"{{SPIN}}": data_uri("spin.png"), "{{Grabb}}": data_uri("grabb.png")}

HEAD = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="description" content="{description}">
<meta property="og:title" content="{og_title}">
<meta property="og:description" content="{description}">
<link rel="icon" type="image/png" href="/favicon.png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
"""

FOOTER_ROW = (
    '<div class="row"><span>© 2026 Mentor Neto. All rights reserved.</span>'
    '<nav aria-label="Site"><a href="/">Spin and Grabb</a><a href="/company/">Spinoff Software</a>'
    '<a href="/privacy/">Privacy Policy</a></nav></div>'
)

FOOTER = f"""<footer>
  <div class="wrap">
    {FOOTER_ROW}
  </div>
</footer>
"""

# Styles for the company and privacy pages, on top of the shared base taken from the sales page.
PAGE_CSS = """
/* company page */
.apps{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,300px),1fr));gap:20px}
.app-tile{background:var(--tile);border-radius:28px;padding:40px 28px;display:flex;flex-direction:column;align-items:center;text-align:center;gap:6px;color:var(--ink)}
.app-tile:hover{text-decoration:none}
.app-tile img{width:112px;height:auto;margin-bottom:12px;filter:drop-shadow(0 14px 22px rgba(0,0,0,.2));transition:transform .35s cubic-bezier(.2,.8,.2,1)}
.app-tile:hover img{transform:translateY(-5px) scale(1.03)}
.app-tile .name{font-size:28px;font-weight:600;letter-spacing:-.03em}
.app-tile .tag{color:var(--ink-2)}
.app-tile .more{color:var(--link);margin-top:10px}
.sec{font-size:clamp(28px,4vw,40px);margin:80px 0 24px}
.values{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,240px),1fr));gap:20px}
.values div{background:var(--tile);border-radius:24px;padding:28px}
.values h3{font-size:21px;margin-bottom:8px}
.values p{color:var(--ink-2)}
.contact{padding-bottom:64px}
.contact p{font-size:19px}

/* privacy page */
.doc{max-width:760px;padding-block:48px 64px}
.doc .crumb{font-size:14px;margin-bottom:28px}
.doc h1{font-size:clamp(40px,6vw,56px);line-height:1.05}
.doc .meta{color:var(--ink-2);font-size:14px;margin:10px 0 28px}
.doc .lead{font-size:21px;line-height:1.4;padding:20px 24px;background:var(--tile);border-radius:18px}
.doc h2{font-size:24px;margin:40px 0 10px}
.doc p+p{margin-top:12px}
.doc ul{margin:0;padding-left:1.2em;display:flex;flex-direction:column;gap:10px}
"""


def fill(html):
    for key, value in ICONS.items():
        html = html.replace(key, value)
    html = html.replace("{{CONTACT}}", CONTACT).replace("{{FOOTER_ROW}}", FOOTER_ROW)
    leftover = re.findall(r"\{\{[A-Za-z_]+\}\}", html)
    assert not leftover, f"unreplaced placeholders: {leftover}"
    return html


def write(rel, html):
    out = root / rel
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html)
    print(f"{rel}: {out.stat().st_size} bytes")


template = (src / "template.html").read_text()

# Sales page: the template carries its own styles and footer.
body = template.replace('<meta charset="utf-8">\n', "", 1)
write("index.html", HEAD.format(
    description="Spin cleans up your Desktop in style. Grabb gets videos from anywhere. "
                "Small Mac apps for simple tasks, 5 dollars each with lifetime upgrades.",
    og_title="Spin and Grabb") + fill(body) + "\n")

# Shared base: colour tokens, type, links, layout and hero, plus the footer rules.
style = template[template.index("<style>") + len("<style>"):template.index("</style>")]
base = style[style.index(":root{"):style.index("/* app sections */")]
footer_css = style[style.index("footer{"):style.index("@media (prefers-reduced-motion")]
css = "<style>\n" + base + footer_css + PAGE_CSS + "</style>\n"

pages = {
    "company/index.html": ("company.html",
                           "Spinoff Software makes small Mac apps for simple tasks: Spin and Grabb.",
                           "Spinoff Software"),
    "privacy/index.html": ("privacy.html",
                           "How Spinoff Software handles your data in Spin, Grabb and on this website.",
                           "Privacy Policy · Spinoff Software"),
}
for rel, (name, description, og_title) in pages.items():
    page = (src / name).read_text()
    write(rel, HEAD.format(description=description, og_title=og_title) + css + fill(page) + FOOTER)
