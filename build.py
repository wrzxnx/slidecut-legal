#!/usr/bin/env python3
"""Build portable, dependency-free legal pages. Python 3.10+."""
import argparse
import html
import json
import re
import shutil
from datetime import date
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "docs"
LOCALES = ["zh-Hans", "en", "zh-Hant", "ja", "ko", "th", "tr", "vi", "ru"]
URLS = {
    "restoreHelp": "https://support.apple.com/108096",
    "google": "https://policies.google.com/technologies/ads",
    "firebase": "https://firebase.google.com/support/privacy",
    "umeng": "https://www.umeng.com/page/policy",
    "github": "https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement",
    "apple": "https://www.apple.com/legal/internet-services/itunes/dev/stdeula/",
    "refund": "https://support.apple.com/118223",
}
# These phrases identify unresolved statements in the supplied draft, not legal rules.
PENDING = {
    "ru": ["необходимо уточнить перед публикацией"],
    "en": ["must be verified", "must be added", "must be confirmed", "must be specified"],
    "zh-Hans": ["需与发布版本核对", "正式发布前需补充", "须在发布前", "核对后确定"],
    "zh-Hant": ["須與發布版本核對", "正式發布前須補充", "須在發布前", "核對後確定"],
    "ja": ["確定する必要があります", "追記が必要です", "確認する必要があります", "明記する必要があります", "確認が必要です"],
    "ko": ["확정해야 합니다", "추가해야 합니다", "확인해야 합니다", "명시해야 합니다"],
    "th": ["ต้องตรวจสอบโมดูล", "ต้องเพิ่มชื่อ", "ต้องยืนยันประเทศ", "ต้องระบุการตั้งค่า", "ต้องตรวจสอบกับขั้นตอน"],
    "tr": ["doğrulanmalıdır", "eklenmelidir", "belirtilmelidir"],
    "vi": ["phải được đối chiếu", "Phải bổ sung", "Cần xác minh", "phải được nêu", "phải được xác minh"],
}


def esc(value):
    return html.escape(str(value), quote=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--release", action="store_true", help="Require completed factual review and build effective pages")
    args = parser.parse_args()
    config = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
    data = {code: json.loads((ROOT / "content" / f"{code}.json").read_text(encoding="utf-8")) for code in LOCALES}
    date.fromisoformat(config["effective_date"])
    if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", config["email"]):
        raise SystemExit("Invalid contact email")
    required = set(data["en"])
    for code, loc in data.items():
        assert set(loc) == required, f"Translation keys differ: {code}"
        assert len(loc["privacySections"]) == 9, code
        assert len(loc["termsSections"]) == 8, code
        assert len(loc["supportSections"]) == 7, code
        for key in ("privacySections", "termsSections", "supportSections"):
            for section in loc[key]:
                assert len(section) == 2 and all(isinstance(s, str) and s.strip() for s in section), code
    if args.release:
        errors = []
        if not config.get("release_approved"):
            errors.append("config.release_approved is false")
        errors.extend(f"Unverified app behavior: {k}" for k, v in config["review"].items() if v is not True)
        errors.extend(f"SDK detail required: {k}" for k, v in config["sdk_details"].items() if not v or "UNCONFIRMED" in str(v))
        for code, loc in data.items():
            body = json.dumps(loc["privacySections"], ensure_ascii=False)
            errors.extend(f"Unresolved {code} draft wording: {phrase}" for phrase in PENDING[code] if phrase in body)
        if errors:
            raise SystemExit("Release blocked. Complete the factual content first:\n- " + "\n- ".join(errors))

    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    (OUT / "assets").mkdir()
    for name in ("style.css", "entry.js", "app-icon.png"):
        shutil.copyfile(ROOT / "assets" / name, OUT / "assets" / name)
    (OUT / ".nojekyll").touch()
    if not args.release:
        (OUT / "robots.txt").write_text("User-agent: *\nDisallow: /\n", encoding="utf-8")

    def text(value, loc):
        return esc(value.format(app=loc["app"], developer=config["developer"], email=config["email"]))

    def render(code, kind="index", entry=False):
        loc = data[code]
        prefix = "" if entry else "../"
        def path(lang, page=kind):
            return f"{prefix}{lang}/{page}.html"
        title = loc["legal"] if kind == "index" else loc[kind]
        languages = "".join(f'<a href="{path(lang)}" lang="{lang}" hreflang="{lang}"'+(' aria-current="true"' if lang == code else '')+f'>{esc(data[lang]["name"])}</a>' for lang in LOCALES)
        alternates = "".join(f'<link rel="alternate" hreflang="{lang}" href="{path(lang)}">' for lang in LOCALES)
        index_url = path(code, "index")
        privacy_url, terms_url = path(code, "privacy"), path(code, "terms")
        support_url = path(code, "support")
        contact_link = f'<a href="mailto:{esc(config["email"])}">{esc(config["email"])}</a>'
        active = lambda name: ' aria-current="page"' if name == kind else ''
        header = f'''<header class="header"><a class="brand" href="{index_url}" aria-label="{esc(loc['app'])}"><img class="app-icon" src="{prefix}assets/app-icon.png" alt="" width="38" height="38"><span>{esc(loc['app'])}</span></a>
<details class="languages"><summary><span aria-hidden="true">◎</span> {esc(loc['name'])}<span class="sr-only"> · {esc(loc['language'])}</span></summary><nav aria-label="{esc(loc['language'])}">{languages}</nav></details></header>
<nav class="tabs" aria-label="{esc(loc['legal'])}"><a href="{support_url}"{active('support')}>{esc(loc['support'])}</a><a href="{privacy_url}"{active('privacy')}>{esc(loc['privacy'])}</a><a href="{terms_url}"{active('terms')}>{esc(loc['terms'])}</a></nav>'''
        draft = '' if args.release else f'<aside class="draft" role="note">{esc(loc["draft"])}</aside>'
        date_html = f'<p class="date">{esc(loc["updated"])} <time datetime="{config["effective_date"]}">{config["effective_date"]}</time></p>'
        if kind == "index":
            body = f'''<main id="main" class="home"><p class="eyebrow">SLIDECUT</p><h1>{esc(title)}</h1><p class="intro">{esc(loc['intro'])}</p>{draft}<div class="cards"><a class="card support-card" href="{support_url}"><span class="card-icon" aria-hidden="true">?</span><h2>{esc(loc['support'])}</h2><p>{esc(loc['supportIntro'])}</p></a><a class="card" href="{privacy_url}"><span class="card-icon" aria-hidden="true">◈</span><h2>{esc(loc['privacy'])}</h2></a><a class="card" href="{terms_url}"><span class="card-icon" aria-hidden="true">≡</span><h2>{esc(loc['terms'])}</h2></a></div><section class="contact"><h2>{esc(loc['contact'])}</h2><p>{esc(config['developer'])}<br>{contact_link}</p></section></main>'''
        else:
            sections = loc[kind + "Sections"]
            toc = ''.join(f'<a href="#section-{i}">{esc(s[0])}</a>' for i, s in enumerate(sections, 1))
            articles = ''.join(f'<section id="section-{i}"><h2>{esc(s[0])}</h2><p>{text(s[1], loc)}</p></section>' for i, s in enumerate(sections, 1))
            resources = ["firebase", "umeng", "google", "github"] if kind == "privacy" else (["restoreHelp", "refund"] if kind == "support" else ["apple", "refund"])
            links = ''.join(f'<li><a href="{URLS[k]}" rel="external">{esc(loc[k])}</a></li>' for k in resources)
            help_card = ''
            if kind == "support":
                mailto = f'mailto:{config["email"]}?subject={quote("Slidecut — " + loc["support"])}'
                help_card = f'<div class="support-contact"><a class="support-button" href="{esc(mailto)}">{esc(loc["supportEmail"])}</a><span>{contact_link}</span><p>{esc(loc["supportHint"])}</p></div>'
            body = f'''<main id="main"><div class="page-heading"><p class="eyebrow">SLIDECUT · {esc(loc['legal'])}</p><h1>{esc(title)}</h1>{date_html if kind != 'support' else ''}<p class="intro">{text(loc[kind+'Intro'], loc)}</p>{help_card}{draft}</div><div class="document-layout"><aside class="toc"><h2>{esc(loc['contents'])}</h2><nav aria-label="{esc(loc['contents'])}">{toc}</nav></aside><article aria-label="{esc(title)}">{articles}<section class="resources"><h2>{esc(loc['resources'])}</h2><ul>{links}</ul></section><section class="contact"><h2>{esc(loc['contact'])}</h2><p>{esc(config['developer'])}<br>{contact_link}</p></section></article></div></main>'''
        entry_script = f'<script src="{prefix}assets/entry.js" defer></script>' if entry else ''
        robots = '' if args.release else '<meta name="robots" content="noindex,nofollow">'
        page = f'''<!doctype html>
<html lang="{code}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="color-scheme" content="light dark"><meta name="referrer" content="strict-origin-when-cross-origin">{robots}<title>{esc(title)} · {esc(loc['app'])}</title><meta name="description" content="{esc(loc['supportIntro'] if kind == 'support' else loc['intro'])}">{alternates}<link rel="icon" type="image/png" href="{prefix}assets/app-icon.png"><link rel="apple-touch-icon" href="{prefix}assets/app-icon.png"><link rel="stylesheet" href="{prefix}assets/style.css">{entry_script}</head><body data-entry="{kind if entry else ''}"><div class="shell">{header}{body}<footer><span>© {esc(config['developer'])}</span><a href="{index_url}">{esc(loc['home'])}</a></footer></div></body></html>'''
        target = OUT / f"{kind}.html" if entry else OUT / code / f"{kind}.html"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(page, encoding="utf-8")

    for code in LOCALES:
        for kind in ("index", "privacy", "terms", "support"):
            render(code, kind)
    for kind in ("index", "privacy", "terms", "support"):
        render("en", kind, entry=True)
    print(f"Built 40 HTML pages for 9 languages in {OUT} ({'release' if args.release else 'review draft'})")


if __name__ == "__main__":
    main()
