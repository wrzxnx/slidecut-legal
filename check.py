#!/usr/bin/env python3
"""Validate generated pages, locale coverage and local navigation."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import json
import re

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "docs"


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids = set()
        self.refs = []
        self.lang = None
        self.h1 = 0
        self.duplicates = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "html":
            self.lang = attrs.get("lang")
        if tag == "h1":
            self.h1 += 1
        if "id" in attrs:
            if attrs["id"] in self.ids:
                self.duplicates.append(attrs["id"])
            self.ids.add(attrs["id"])
        for attr in ("href", "src"):
            if attr in attrs:
                self.refs.append(attrs[attr])
        if tag == "script":
            assert not attrs.get("src", "").startswith(("https:", "http:", "//")), "Unexpected remote script"


def main():
    pages = {}
    failures = []
    for path in OUT.rglob("*.html"):
        source = path.read_text(encoding="utf-8")
        page = Page()
        page.feed(source)
        pages[path.resolve()] = page
        if page.h1 != 1 or not page.lang or page.duplicates:
            failures.append(f"Structure: {path.relative_to(OUT)}")
        if re.search(r"\{(?:app|developer|email)\}", source):
            failures.append(f"Unexpanded token: {path}")
        if "wrzxnx@gmail.com" not in source or "wangrui" not in source:
            failures.append(f"Missing developer contact: {path}")
    expected_pages = (len(list((ROOT / 'content').glob('*.json'))) + 1) * 4
    assert len(pages) == expected_pages, f"Expected {expected_pages} HTML pages, got {len(pages)}"
    for path, page in pages.items():
        for ref in page.refs:
            url = urlsplit(ref)
            if url.scheme or url.netloc:
                continue
            target = (path.parent / unquote(url.path)).resolve() if url.path else path
            if not target.is_relative_to(OUT.resolve()):
                failures.append(f"Navigation escapes site: {path}: {ref}")
            elif not target.exists():
                failures.append(f"Broken local link: {path}: {ref}")
            elif url.fragment and target in pages and unquote(url.fragment) not in pages[target].ids:
                failures.append(f"Broken section link: {path}: {ref}")
    for source in (ROOT / "content").glob("*.json"):
        loc = json.loads(source.read_text(encoding="utf-8"))
        for kind in ("privacy", "terms", "support"):
            target = (OUT / source.stem / f"{kind}.html").resolve()
            assert pages[target].lang == source.stem
            assert loc[kind] in target.read_text(encoding="utf-8")
    if failures:
        raise SystemExit("\n".join(failures))
    print(f"PASS: {len(pages)} pages; 9 locales; all local links, section anchors, language tags and contact details")


if __name__ == "__main__":
    main()
