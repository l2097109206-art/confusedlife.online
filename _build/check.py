#!/usr/bin/env python3
"""Post-build QA: validate JSON-LD, resolve internal links, sanity-check SEO tags."""

import html as html_mod
import json
import re
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://confusedlife.online"

# Pages that intentionally skip structured data
NO_SCHEMA_OK = {"404.html"}

HTML_FILES = sorted(
    p for p in ROOT.rglob("*.html")
    if "_build" not in p.parts and "node_modules" not in p.parts
)

problems = []
warnings = []


def check_jsonld(path, text):
    blocks = re.findall(
        r'<script type="application/ld\+json">(.*?)</script>', text, re.S)
    if not blocks:
        if Path(path).name not in NO_SCHEMA_OK:
            warnings.append(f"{path}: no JSON-LD block")
        return
    for i, block in enumerate(blocks):
        try:
            data = json.loads(block)
        except json.JSONDecodeError as e:
            problems.append(f"{path} block#{i}: INVALID JSON — {e}")
            continue

        # Collect @type values including nested @graph
        types = []

        def walk(node):
            if isinstance(node, dict):
                if "@type" in node:
                    t = node["@type"]
                    types.extend(t if isinstance(t, list) else [t])
                for v in node.values():
                    walk(v)
            elif isinstance(node, list):
                for v in node:
                    walk(v)

        walk(data)
        if not types:
            warnings.append(f"{path} block#{i}: no @type found")


def check_links(path, text):
    hrefs = re.findall(r'(?:href|src)="(/[^"#?][^"#]*)"', text)
    for href in set(hrefs):
        href = href.split("#")[0].split("?")[0]
        if not href or href.startswith("//"):
            continue
        rel = unquote(href).lstrip("/")
        target = ROOT / rel if rel else None
        if target is None:
            continue
        if target.is_dir():
            target = target / "index.html"
        if not target.exists():
            problems.append(f"{path}: broken internal link → {href}")


def check_seo(path, text):
    rel = str(path.relative_to(ROOT))
    if not re.search(r"<title>(.*?)</title>", text, re.S):
        problems.append(f"{rel}: missing <title>")
    if not re.search(r'<meta name="description"', text):
        problems.append(f"{rel}: missing meta description")
    if not re.search(r'<link rel="canonical"', text):
        problems.append(f"{rel}: missing canonical")
    if not re.search(r'<meta property="og:title"', text):
        warnings.append(f"{rel}: missing og:title")
    if not re.search(r'<html lang="en">', text):
        problems.append(f"{rel}: missing lang attribute")

    # Measure as it renders, not as it's encoded
    title = html_mod.unescape(
        (re.search(r"<title>(.*?)</title>", text, re.S) or [None, ""])[1])
    if len(title) > 62:
        warnings.append(f"{rel}: title is {len(title)} chars (aim < 62)")

    desc = re.search(r'<meta name="description" content="(.*?)"', text, re.S)
    if desc:
        d = html_mod.unescape(desc.group(1))
        if len(d) > 158:
            warnings.append(f"{rel}: description is {len(d)} chars (aim < 158)")

    # Exactly one h1
    h1s = re.findall(r"<h1[^>]*>", text)
    if len(h1s) != 1:
        problems.append(f"{rel}: found {len(h1s)} <h1> tags (expected 1)")


def check_anchors(path, text):
    """TOC/anchor links must point at an id that exists on the page."""
    ids = set(re.findall(r'\sid="([^"]+)"', text))
    for anchor in set(re.findall(r'href="#([^"]+)"', text)):
        if anchor and anchor not in ids and anchor != "main":
            problems.append(f"{path}: dangling anchor #{anchor}")


def main():
    for f in HTML_FILES:
        text = f.read_text(encoding="utf-8")
        rel = str(f.relative_to(ROOT))
        check_jsonld(rel, text)
        check_links(rel, text)
        check_seo(f, text)
        check_anchors(rel, text)

    print(f"Checked {len(HTML_FILES)} HTML files\n")

    if problems:
        print(f"PROBLEMS ({len(problems)}):")
        for p in problems:
            print(f"  ✗ {p}")
    else:
        print("✓ No problems found")

    if warnings:
        print(f"\nWARNINGS ({len(warnings)}):")
        for w in warnings:
            print(f"  ! {w}")
    else:
        print("✓ No warnings")

    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
