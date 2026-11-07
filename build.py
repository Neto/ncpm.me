#!/usr/bin/env python3
"""Build index.html from src/template.html. Embeds the app icons and wraps the page in a full document."""
import base64, pathlib

root = pathlib.Path(__file__).resolve().parent
src = root / "src"

def data_uri(name):
    return "data:image/png;base64," + base64.b64encode((src / name).read_bytes()).decode()

body = (src / "template.html").read_text()
body = body.replace("{{SPIN}}", data_uri("spin.png")).replace("{{Grabb}}", data_uri("grabb.png"))
assert "{{" not in body, "unreplaced placeholder in template"
body = body.replace('<meta charset="utf-8">\n', "", 1)

head = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="description" content="Spin cleans up your Desktop in style. Grabb gets videos from anywhere. Small Mac apps for simple tasks, 5 dollars each with lifetime upgrades.">
<meta property="og:title" content="Spin and Grabb">
<meta property="og:description" content="Small apps for simple tasks. Mac only.">
<link rel="icon" type="image/png" href="favicon.png">
<link rel="apple-touch-icon" href="apple-touch-icon.png">
"""
(root / "index.html").write_text(head + body + "\n")
print("index.html", (root / "index.html").stat().st_size, "bytes")
