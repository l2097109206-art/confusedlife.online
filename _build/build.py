#!/usr/bin/env python3
"""ConfusedLife.online — static site generator.

Reads article bodies from _build/content/*.html, wraps them in the shared
layout, and writes plain static HTML to the site root. The generated files are
what get committed and deployed — this script is a maintenance convenience,
not a runtime dependency.

Usage:  python _build/build.py
"""

import datetime
import html
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "_build" / "content"
SITE = "https://confusedlife.online"
BRAND_NAME = "ConfusedLife.online"
AUTHOR = "ConfusedLife Editorial Team"
PUBLISHED = "2026-08-31"

# Asset cache-buster. _headers sets /assets/* to `immutable` (1-year cache), so any
# change to CSS/JS must bump this version or browsers will serve a stale file forever.
# Bump on EVERY edit to assets/css/* or assets/js/*.
ASSET_VER = "2"

# Shared, traceable references used across the guides. Every entry links to a
# real, verifiable source — this is the E-E-A-T "sources" signal rendered on
# each article page (YMYL optimisation item 3).
REFERENCES = [
    {
        "title": "The Path to Purpose: How Young People Find Their Calling",
        "author": "William Damon (2008)",
        "note": "Developmental research on how a sense of purpose forms in adolescence and early adulthood — the basis of our purpose sections.",
        "url": "https://www.goodreads.com/book/show/6372615-the-path-to-purpose",
    },
    {
        "title": "The Paradox of Choice: Why More Is Less",
        "author": "Barry Schwartz (2004)",
        "note": "How abundant options increase anxiety and reduce satisfaction — the basis of our 'too many options' and decision sections.",
        "url": "https://www.goodreads.com/book/show/71211.The_Paradox_of_Choice",
    },
    {
        "title": "Development and validation of the 'quarter-life crisis' concept",
        "author": "Oliver Robinson (2012), International Journal of Behavioral Development",
        "note": "The four-stage model of the quarter-life crisis we reference in the quarter-life guide.",
        "url": "https://doi.org/10.1177/0165025412468060",
    },
    {
        "title": "Mastering the game: How high- and low-trajectories of interest shape engagement",
        "author": "Paul A. O'Keefe, Erik J. Horberg & Judith M. Harackiewicz (2015)",
        "note": "Research on how sustained interest develops — relevant to the values and purpose sections.",
        "url": "https://doi.org/10.1177/0956797614535813",
    },
]

# --------------------------------------------------------------------------
# Layout
# --------------------------------------------------------------------------

NAV_ITEMS = [
    ("/", "Home", "home"),
    ("/guides/feeling-lost-in-life/", "Main Guide", "guide"),
    ("/tools/clarity-quiz/", "Clarity Quiz", "quiz"),
    ("/quotes/confused-about-life/", "Quotes", "quotes"),
    ("/wall/", "The Clarity Wall", "wall"),
    ("/topics/", "All Topics", "topics"),
]


def nav(active):
    out = []
    for href, label, key in NAV_ITEMS:
        current = ' aria-current="page"' if key == active else ""
        out.append(f'<li><a href="{href}"{current}>{label}</a></li>')
    return "\n        ".join(out)


def header(active, extra_head=""):
    return f"""<a class="skip-link" href="#main">Skip to content</a>
<div class="progress-track" aria-hidden="true"><div class="progress-bar"></div></div>

<header class="site-header">
  <div class="wrap header-inner">
    <a class="brand" href="/">
      <span class="brand-dot" aria-hidden="true"></span>
      Confused<span class="brand-tld">Life.online</span>
    </a>
    <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="primary-nav" aria-label="Open menu">
      <span class="nav-toggle-bar"></span><span class="nav-toggle-bar"></span><span class="nav-toggle-bar"></span>
    </button>
    <nav class="primary-nav" id="primary-nav" aria-label="Primary">
      <ul>
        {nav(active)}
      </ul>
    </nav>
  </div>
</header>
{extra_head}"""


def footer():
    return """<footer class="site-footer">
  <div class="wrap">
    <div class="disclaimer-notice" role="note" aria-label="Disclaimer">
      <p><strong>Not professional advice.</strong> ConfusedLife.online is for self-reflection and personal growth only. It does not provide medical, psychological, or clinical advice. If you are in crisis, contact local emergency services or a crisis line such as <a href="https://findahelpline.com" rel="noopener nofollow" target="_blank">findahelpline.com</a> (international) or 988 (US). <a href="/disclaimer/">Read the full disclaimer</a>.</p>
    </div>
    <div class="footer-grid">
      <div class="footer-about">
        <a class="brand" href="/" style="margin-bottom:.75rem">
          <span class="brand-dot" aria-hidden="true"></span>
          Confused<span class="brand-tld">Life.online</span>
        </a>
        <p>Practical clarity for when life stops making sense. An independent editorial project.</p>
        <div class="crisis-strip">
          <strong>In crisis?</strong> US: call or text <strong>988</strong>. UK: <strong>116&nbsp;123</strong>.
          International: <a href="https://findahelpline.com" rel="noopener nofollow" target="_blank">findahelpline.com</a>.
        </div>
      </div>

      <div class="footer-col">
        <h3>Start here</h3>
        <ul>
          <li><a href="/guides/feeling-lost-in-life/">Main guide</a></li>
          <li><a href="/tools/clarity-quiz/">Clarity Quiz</a></li>
          <li><a href="/quotes/confused-about-life/">Quotes</a></li>
          <li><a href="/topics/">All topics</a></li>
        </ul>
      </div>

      <div class="footer-col">
        <h3>Guides</h3>
        <ul>
          <li><a href="/guides/why-am-i-so-confused-about-life/">Why am I so confused?</a></li>
          <li><a href="/wall/">The Clarity Wall</a></li>
          <li><a href="/guides/signs-you-are-feeling-lost/">15 signs you're lost</a></li>
          <li><a href="/guides/how-to-find-your-purpose/">Finding your purpose</a></li>
          <li><a href="/guides/quarter-life-crisis/">Quarter-life crisis</a></li>
        </ul>
      </div>

      <div class="footer-col">
        <h3>About</h3>
        <ul>
          <li><a href="/about/">Who we are</a></li>
          <li><a href="/editorial-policy/">Editorial policy</a></li>
          <li><a href="/disclaimer/">Disclaimer</a></li>
          <li><a href="/privacy-policy/">Privacy policy</a></li>
          <li><a href="/contact/">Contact</a></li>
        </ul>
      </div>
    </div>

    <div class="footer-bottom">
      <p>&copy; <span id="year">2026</span> ConfusedLife.online. General information, not professional advice.</p>
      <p><a href="/terms/">Terms</a> &middot; <a href="/privacy-policy/">Privacy</a> &middot; <a href="/disclaimer/">Disclaimer</a></p>
    </div>
  </div>
</footer>"""


def head(title, desc, canonical, og_type="website", schema="", published=None, modified=None, extra=""):
    published = published or PUBLISHED
    modified = modified or PUBLISHED
    art_meta = ""
    if og_type == "article":
        art_meta = (f'\n<meta property="article:published_time" content="{published}">'
                    f'\n<meta property="article:modified_time" content="{modified}">')

    return f"""<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">

<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">

<link rel="canonical" href="{SITE}{canonical}">

<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="{BRAND_NAME}">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:url" content="{SITE}{canonical}">
<meta property="og:image" content="{SITE}/assets/img/og-default.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Confused about life? — ConfusedLife.online">
<meta property="og:locale" content="en_US">{art_meta}

<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{html.escape(title)}">
<meta name="twitter:description" content="{html.escape(desc)}">
<meta name="twitter:image" content="{SITE}/assets/img/og-default.png">
<meta name="twitter:image:alt" content="Confused about life? — ConfusedLife.online">

<meta name="theme-color" content="#0E6B5C">
<link rel="icon" href="/assets/img/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/assets/img/favicon.png" sizes="32x32" type="image/png">
<link rel="apple-touch-icon" href="/assets/img/apple-touch-icon.png">
<link rel="stylesheet" href="/assets/css/main.css">
{extra}
{_schema_block(schema)}"""


def _schema_block(schema):
    if not schema:
        return ""
    return f'<script type="application/ld+json">\n{schema}\n</script>'


def org_graph():
    return """{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "Organization",
      "@id": "https://confusedlife.online/#organization",
      "name": "ConfusedLife.online",
      "url": "https://confusedlife.online/",
      "description": "An independent editorial project publishing plain-English guides on feeling lost, stuck or confused about life.",
      "email": "hello@confusedlife.online",
      "publishingPrinciples": "https://confusedlife.online/editorial-policy/",
      "knowsAbout": ["life transitions", "purpose and meaning", "decision making", "quarter-life crisis", "self-reflection"]
    },
    {
      "@type": "WebSite",
      "@id": "https://confusedlife.online/#website",
      "url": "https://confusedlife.online/",
      "name": "ConfusedLife.online",
      "description": "Practical clarity for when life stops making sense.",
      "publisher": { "@id": "https://confusedlife.online/#organization" },
      "inLanguage": "en-US"
    }
  ]
}"""


def article_graph(title, desc, canonical, crumbs, faq=None):
    items = []
    for i, c in enumerate(crumbs, start=1):
        name = _js(c["name"])
        if c.get("url"):
            items.append(f'{{ "@type": "ListItem", "position": {i}, "name": "{name}", "item": "{c["url"]}" }}')
        else:
            items.append(f'{{ "@type": "ListItem", "position": {i}, "name": "{name}" }}')
    crumb_json = ",\n        ".join(items)

    nodes = [
        "    {\n"
        '      "@type": "Article",\n'
        f'      "@id": "{SITE}{canonical}#article",\n'
        f'      "headline": "{_js(title)}",\n'
        f'      "description": "{_js(desc)}",\n'
        f'      "datePublished": "{PUBLISHED}",\n'
        f'      "dateModified": "{PUBLISHED}",\n'
        '      "inLanguage": "en-US",\n'
        '      "isPartOf": { "@id": "https://confusedlife.online/#website" },\n'
        '      "publisher": { "@id": "https://confusedlife.online/#organization" },\n'
        f'      "author": {{ "@type": "Organization", "name": "{AUTHOR}", "url": "https://confusedlife.online/about/" }},\n'
        '      "reviewedBy": { "@type": "Organization", "name": "ConfusedLife Editorial Team", "url": "https://confusedlife.online/editorial-policy/" },\n'
        '      "mainEntityOfPage": { "@type": "WebPage", "@id": "' + SITE + canonical + '" }\n'
        "    }",
        "    {\n"
        '      "@type": "BreadcrumbList",\n'
        '      "itemListElement": [\n        ' + crumb_json + "\n      ]\n"
        "    }",
    ]

    if faq:
        ents = ",\n".join(
            '        {\n'
            f'          "@type": "Question",\n'
            f'          "name": "{_js(q)}",\n'
            '          "acceptedAnswer": { "@type": "Answer", "text": "' + _js(a) + '" }\n'
            '        }'
            for q, a in faq
        )
        nodes.append(
            "    {\n"
            '      "@type": "FAQPage",\n'
            f'      "@id": "{SITE}{canonical}#faq",\n'
            '      "mainEntity": [\n' + ents + "\n      ]\n"
            "    }"
        )

    graph = ",\n".join(nodes)
    return '{\n  "@context": "https://schema.org",\n  "@graph": [\n' + graph + "\n  ]\n}"


_FAQ_RE = re.compile(
    r'<summary>(.*?)</summary>\s*<div class="faq-answer">(.*?)</div>',
    re.S | re.I,
)


def extract_faq(body_html):
    """Pull Q/A pairs out of a .faq block so they can become FAQPage schema."""
    out = []
    for q_html, a_html in _FAQ_RE.findall(body_html):
        q = _text(q_html)
        a = _text(a_html)
        if q and a:
            out.append((q, a))
    return out


def _text(fragment):
    """Strip tags and collapse whitespace in an HTML fragment."""
    fragment = re.sub(r"<[^>]+>", " ", fragment)
    fragment = html.unescape(fragment)
    return re.sub(r"\s+", " ", fragment).strip()


def _js(s):
    """Escape a string for embedding inside a JSON double-quoted literal."""
    return (s.replace("\\", "\\\\").replace('"', '\\"')
             .replace("\n", " ").replace("\t", " "))


def faq_schema(qas):
    ents = []
    for q, a in qas:
        ents.append(
            '        {\n'
            f'          "@type": "Question",\n'
            f'          "name": "{_js(q)}",\n'
            '          "acceptedAnswer": { "@type": "Answer", '
            f'"text": "{_js(a)}" }}\n'
            '        }'
        )
    joined = ",\n".join(ents)
    return ('{\n  "@context": "https://schema.org",\n'
            '  "@type": "FAQPage",\n'
            '  "mainEntity": [\n' + joined + '\n  ]\n}')


# --------------------------------------------------------------------------
# TOC generation
# --------------------------------------------------------------------------

def build_toc(body_html):
    """Pull <h2 id="..."> headings out of an article body to build the TOC."""
    pattern = re.compile(r'<h2\s+id="([^"]+)"[^>]*>(.*?)</h2>', re.S | re.I)
    matches = pattern.findall(body_html)
    if len(matches) < 3:
        return ""
    lis = []
    for anchor, text in matches:
        clean = re.sub(r"<[^>]+>", "", text).strip()
        lis.append(f'<li><a href="#{anchor}">{html.escape(clean)}</a></li>')
    return ('<aside class="toc" aria-label="Table of contents">\n'
            '        <p class="toc-title">On this page</p>\n'
            '        <ol>\n          ' + "\n          ".join(lis) + "\n        </ol>\n      </aside>")


def strip_h1(body_html):
    """Content files may start with a leading <h1>; the layout renders its own."""
    return re.sub(r"^\s*<h1[^>]*>.*?</h1>\s*", "", body_html, count=1, flags=re.S | re.I)


# --------------------------------------------------------------------------
# Page renderers
# --------------------------------------------------------------------------

def references_section(refs):
    """Render a 'Sources & further reading' block (YMYL E-E-A-T item 3)."""
    if not refs:
        return ""
    items = []
    for r in refs:
        items.append(
            f'        <li>\n'
            f'          <span class="ref-title">{html.escape(r["title"])}</span>\n'
            f'          <span class="ref-author">{html.escape(r["author"])}</span>\n'
            f'          <span class="ref-note">{html.escape(r["note"])}</span>\n'
            f'          <a class="ref-link" href="{r["url"]}" rel="noopener nofollow" target="_blank">View source ↗</a>\n'
            f'        </li>'
        )
    joined = "\n".join(items)
    return (
        '      <section class="references" aria-label="Sources and further reading">\n'
        '        <h2 class="references-title">Sources &amp; further reading</h2>\n'
        '        <p class="references-intro">Every guide on ConfusedLife.online is written against published research. These are the sources this article draws on. We link to them so you can check our reading.</p>\n'
        '        <ul class="references-list">\n' + joined + "\n        </ul>\n"
        '      </section>'
    )


def author_box():
    """Render the author / editorial-review identity block (YMYL E-E-A-T item 2)."""
    return (
        '      <aside class="author-box" aria-label="About the author and review">\n'
        '        <div class="author-box-head">\n'
        '          <span class="avatar avatar-lg" aria-hidden="true">CL</span>\n'
        '          <div>\n'
        f'            <p class="author-name">{AUTHOR}</p>\n'
        '            <p class="author-role">Editorial team &middot; reviewed for accuracy against cited sources</p>\n'
        '          </div>\n'
        '        </div>\n'
        '        <p class="author-note">ConfusedLife.online is an independent editorial project. We are not licensed mental health professionals, and nothing here is medical advice, diagnosis or treatment. Content is researched and reviewed by our editorial team before publication; where the evidence is thin we say so.</p>\n'
        '        <p class="author-links"><a href="/about/">Who we are</a> &middot; <a href="/editorial-policy/">Editorial policy</a> &middot; <a href="/disclaimer/">Full disclaimer</a></p>\n'
        '      </aside>'
    )


def render_article(meta, body_html, nav_key="guide"):
    """meta: slug, title, desc, eyebrow, lede, read_time, crumbs, active"""
    canonical = meta["slug"]
    body = strip_h1(body_html)
    toc = build_toc(body)
    crumbs = meta.get("crumbs", [{"name": "Home", "url": f"{SITE}/"},
                                 {"name": "Guides", "url": f"{SITE}/topics/"},
                                 {"name": meta["title"]}])

    crumb_html = []
    for i, c in enumerate(crumbs):
        if i:
            crumb_html.append('<li class="sep" aria-hidden="true">/</li>')
        if c.get("url") and i < len(crumbs) - 1:
            crumb_html.append(f'<li><a href="{c["url"].replace(SITE, "")}">{html.escape(c["name"])}</a></li>')
        else:
            crumb_html.append(f'<li aria-current="page">{html.escape(c["name"])}</li>')

    lede = meta.get("lede", "")
    lede_html = f'\n        <p class="article-lede">{lede}</p>' if lede else ""

    main = f"""
  <nav class="breadcrumbs wrap" aria-label="Breadcrumb">
    <ol>
      {"".join(crumb_html)}
    </ol>
  </nav>

  <article>
    <header class="article-header">
      <div class="wrap measure">
        <p class="eyebrow">{meta.get("eyebrow", "Guide")}</p>
        <h1>{html.escape(meta["title"])}</h1>{lede_html}
        <div class="byline">
          <span class="byline-author"><span class="avatar" aria-hidden="true">CL</span> {AUTHOR}</span>
          <span>Updated {meta.get("date_long", "31 August 2026")}</span>
          <span>&middot;</span>
          <span>{meta.get("read_time", "12 min read")}</span>
        </div>
        <p class="review-badge"><span class="review-dot" aria-hidden="true"></span> Accuracy reviewed by the editorial team against cited sources. Not medical advice.</p>
      </div>
    </header>

    <div class="wrap article-layout">
      {toc}
      <div class="article-body dropcap">
{body}
      </div>
    </div>

    <div class="wrap measure">
      {references_section(REFERENCES)}
      {author_box()}
    </div>
  </article>
"""

    faq = extract_faq(body)
    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
{head(meta["title"], meta["desc"], canonical, og_type="article", schema=article_graph(meta["title"], meta["desc"], canonical, crumbs, faq))}
</head>
<body>

{header(nav_key)}

<main id="main">
{main}
</main>

{footer()}

<script src="/assets/js/main.js" defer></script>
</body>
</html>
"""
    return page


def render_simple(meta, body_html, nav_key="topics", extra_head=""):
    """For static pages (about, privacy, etc.) — full-width, no TOC."""
    canonical = meta["slug"]
    crumbs = meta.get("crumbs")
    crumb_html = ""
    if crumbs:
        parts = []
        for i, c in enumerate(crumbs):
            if i:
                parts.append('<li class="sep" aria-hidden="true">/</li>')
            if c.get("url") and i < len(crumbs) - 1:
                parts.append(f'<li><a href="{c["url"].replace(SITE, "")}">{html.escape(c["name"])}</a></li>')
            else:
                parts.append(f'<li aria-current="page">{html.escape(c["name"])}</li>')
        crumb_html = (f'\n  <nav class="breadcrumbs wrap" aria-label="Breadcrumb">\n'
                      f'    <ol>{"".join(parts)}</ol>\n  </nav>\n')

    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
{head(meta["title"], meta["desc"], canonical, og_type="website", schema=org_graph(), extra=extra_head)}
</head>
<body>

{header(nav_key)}
{crumb_html}
<main id="main">
  <div class="wrap measure" style="padding-top:clamp(2.5rem,7vw,4rem);padding-bottom:clamp(3rem,7vw,5rem)">
{body_html}
  </div>
</main>

{footer()}

<script src="/assets/js/main.js" defer></script>
</body>
</html>
"""
    return page


def write(rel_path, content):
    path = ROOT / rel_path.lstrip("/")
    path.parent.mkdir(parents=True, exist_ok=True)
    # Append the cache-busting version to every /assets/ reference so edited
    # CSS/JS is actually re-fetched by browsers (see ASSET_VER above).
    if rel_path.endswith(".html"):
        import re
        content = re.sub(
            r'(?P<attr>href|src)="(/assets/[^"?]+)"',
            lambda m: f'{m.group("attr")}="{m.group(2)}?v={ASSET_VER}"',
            content,
        )
    path.write_text(content, encoding="utf-8")
    return path


# --------------------------------------------------------------------------
# Pages
# --------------------------------------------------------------------------

def build_articles():
    ARTICLES = [
        {
            "file": "why-am-i-so-confused-about-life.html",
            "slug": "/guides/why-am-i-so-confused-about-life/",
            "title": "Why Am I So Confused About Life? 12 Honest Reasons",
            "desc": "Twelve reasons you feel confused about life, ordered by how often each is the real cause — including the two that disguise themselves as laziness.",
            "eyebrow": "Causes",
            "lede": "Confusion about life rarely has one cause. Here are the twelve that show up most often, roughly in the order they turn out to be the real one.",
            "read_time": "14 min read",
        },
        {
            "file": "signs-you-are-feeling-lost.html",
            "slug": "/guides/signs-you-are-feeling-lost/",
            "title": "15 Signs You're Feeling Lost in Life",
            "desc": "Going through the motions is the obvious sign. But feeling lost also shows up as overworking, as endless research, and as being oddly fine with everything.",
            "eyebrow": "Self-check",
            "lede": "Some of these look like sadness. Others look like productivity. A few look, from the outside, like having it all together.",
            "read_time": "11 min read",
        },
        {
            "file": "i-dont-know-what-to-do-with-my-life.html",
            "slug": "/guides/i-dont-know-what-to-do-with-my-life/",
            "title": "\"I Don't Know What to Do With My Life\" — What to Do",
            "desc": "The problem usually isn't a lack of options. It's too many, and no way to rank them. A practical method for narrowing them down in an afternoon.",
            "eyebrow": "Career & direction",
            "lede": "Most people saying this aren't short of options. They're drowning in them and have no way to rank them.",
            "read_time": "15 min read",
        },
        {
            "file": "how-to-find-your-purpose.html",
            "slug": "/guides/how-to-find-your-purpose/",
            "title": "How to Find Your Purpose (Without Auditing Your Soul)",
            "desc": "Purpose is built, not found. A working method based on what you keep returning to — plus why \"find your passion\" sets most people up to feel worse.",
            "eyebrow": "Meaning",
            "lede": "The search for purpose has been turned into an industry, and the industry has made people less happy. Here's a more boring, more reliable version.",
            "read_time": "16 min read",
        },
        {
            "file": "quarter-life-crisis.html",
            "slug": "/guides/quarter-life-crisis/",
            "title": "Quarter-Life Crisis: What It Is and How to Move Through It",
            "desc": "Not immaturity, and not a midlife crisis arriving early. It's a specific collision of too much choice, too much comparison and too few structures.",
            "eyebrow": "Life stage",
            "lede": "The twenties and thirties have a distinctive kind of confusion. It has a cause, and it isn't that you failed to launch.",
            "read_time": "13 min read",
        },
    ]

    for meta in ARTICLES:
        body = (CONTENT / meta["file"]).read_text(encoding="utf-8")
        out = render_article(meta, body)
        write(meta["slug"] + "index.html", out)
        print(f"  wrote {meta['slug']}")


# --------------------------------------------------------------------------
# Quotes page
# --------------------------------------------------------------------------

QUOTE_SECTIONS = [
    ("On being lost", [
        ("Not until we are lost do we begin to understand ourselves.", "Henry David Thoreau"),
        ("No one can build you the bridge on which you, and only you, must cross the stream of life.", "Friedrich Nietzsche"),
        ("The only way to make sense out of change is to plunge into it, move with it, and join the dance.", "Alan Watts"),
        ("Let yourself be silently drawn by the strange pull of what you really love. It will not lead you astray.", "Rumi"),
        ("Out beyond ideas of wrongdoing and rightdoing, there is a field. I'll meet you there.", "Rumi"),
        ("Life can only be understood backwards; but it must be lived forwards.", "Søren Kierkegaard"),
        ("The mass of men lead lives of quiet desperation.", "Henry David Thoreau"),
        ("I went to the woods because I wished to live deliberately, to front only the essential facts of life.", "Henry David Thoreau"),
        ("What you seek is seeking you.", "Rumi"),
        ("Not everything that is faced can be changed, but nothing can be changed until it is faced.", "James Baldwin"),
    ]),
    ("On not knowing yet", [
        ("Be patient toward all that is unsolved in your heart and try to love the questions themselves.", "Rainer Maria Rilke"),
        ("Live the questions now. Perhaps you will then gradually, without noticing it, live along some distant day into the answer.", "Rainer Maria Rilke"),
        ("The only true wisdom is in knowing you know nothing.", "Socrates"),
        ("Wonder is the beginning of wisdom.", "Socrates"),
        ("Beware the barrenness of a busy life.", "Socrates"),
        ("Man is not worried by real problems so much as by his imagined anxieties about real problems.", "Epictetus"),
        ("The important thing is not to stop questioning. Curiosity has its own reason for existing.", "Albert Einstein"),
        ("I have no special talent. I am only passionately curious.", "Albert Einstein"),
        ("One must still have chaos in oneself to be able to give birth to a dancing star.", "Friedrich Nietzsche"),
        ("A person who never made a mistake never tried anything new.", "Albert Einstein"),
    ]),
    ("On purpose and meaning", [
        ("He who has a why to live can bear almost any how.", "Friedrich Nietzsche"),
        ("Those who have a 'why' to live can bear with almost any 'how'.", "Viktor Frankl"),
        ("When we are no longer able to change a situation, we are challenged to change ourselves.", "Viktor Frankl"),
        ("Between stimulus and response there is a space. In that space is our power to choose our response.", "Viktor Frankl"),
        ("Tell me, what is it you plan to do with your one wild and precious life?", "Mary Oliver"),
        ("How we spend our days is, of course, how we spend our lives.", "Annie Dillard"),
        ("The two most important days in your life are the day you are born and the day you find out why.", "Attributed to Mark Twain"),
        ("Happiness is not something ready made. It comes from your own actions.", "Dalai Lama"),
        ("The purpose of our lives is to be happy.", "Dalai Lama"),
        ("To live is the rarest thing in the world. Most people exist, that is all.", "Oscar Wilde"),
    ]),
    ("On starting before you're ready", [
        ("You do not have to see the whole staircase. Just take the first step.", "Martin Luther King Jr."),
        ("The journey of a thousand miles begins with one step.", "Lao Tzu"),
        ("The best time to plant a tree was twenty years ago. The second best time is now.", "Chinese proverb"),
        ("It does not matter how slowly you go as long as you do not stop.", "Confucius"),
        ("The most difficult thing is the decision to act. The rest is merely tenacity.", "Amelia Earhart"),
        ("Twenty years from now you will be more disappointed by the things that you didn't do than by the ones you did do.", "Attributed to Mark Twain"),
        ("Life is like riding a bicycle. To keep your balance, you must keep moving.", "Albert Einstein"),
        ("In the middle of difficulty lies opportunity.", "Albert Einstein"),
        ("It's not whether you get knocked down, it's whether you get up.", "Vince Lombardi"),
        ("Fall seven times, stand up eight.", "Japanese proverb"),
    ]),
    ("On who you are underneath it", [
        ("The curious paradox is that when I accept myself just as I am, then I can change.", "Carl Rogers"),
        ("The privilege of a lifetime is to become who you truly are.", "Carl Jung"),
        ("Your vision will become clear only when you can look into your own heart.", "Carl Jung"),
        ("Who looks outside, dreams; who looks inside, awakes.", "Carl Jung"),
        ("I am not what happened to me, I am what I choose to become.", "Carl Jung"),
        ("Be yourself; everyone else is already taken.", "Oscar Wilde"),
        ("I can't go back to yesterday, because I was a different person then.", "Lewis Carroll"),
        ("When I let go of what I am, I become what I might be.", "Lao Tzu"),
        ("The soul becomes dyed with the colour of its thoughts.", "Marcus Aurelius"),
        ("Yesterday I was clever, so I wanted to change the world. Today I am wise, so I am changing myself.", "Rumi"),
    ]),
    ("Short lines for a bad day", [
        ("This too shall pass.", "Traditional"),
        ("The wound is the place where the Light enters you.", "Rumi"),
        ("We are all in the gutter, but some of us are looking at the stars.", "Oscar Wilde"),
        ("Do one thing every day that scares you.", "Attributed to Eleanor Roosevelt"),
        ("No one can make you feel inferior without your consent.", "Eleanor Roosevelt"),
        ("It is during our darkest moments that we must focus to see the light.", "Attributed to Aristotle Onassis"),
        ("Courage is the price that life exacts for granting peace.", "Amelia Earhart"),
        ("Our greatest glory is not in never falling, but in rising every time we fall.", "Attributed to Confucius"),
        ("If you think you are too small to make a difference, try sleeping with a mosquito.", "Attributed to the Dalai Lama"),
        ("Inhale the future, exhale the past.", "Traditional"),
    ]),
]

COPY_SVG = '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="9" y="9" width="12" height="12" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>'
SHARE_SVG = '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.6" y1="13.5" x2="15.4" y2="17.5"/><line x1="15.4" y1="6.5" x2="8.6" y2="10.5"/></svg>'


def quote_card(text, author):
    return f"""        <figure class="quote-card">
          <blockquote class="quote-text">{html.escape(text)}</blockquote>
          <figcaption class="quote-foot">
            <cite class="quote-author">{html.escape(author)}</cite>
            <span class="quote-actions">
              <button class="icon-btn" data-action="copy" title="Copy quote">{COPY_SVG}</button>
              <button class="icon-btn" data-action="share" title="Share quote">{SHARE_SVG}</button>
            </span>
          </figcaption>
        </figure>"""


def quotes_schema(total):
    items = []
    pos = 0
    for _, quotes in QUOTE_SECTIONS:
        for text, author in quotes:
            pos += 1
            items.append(
                '        {\n'
                '          "@type": "Quotation",\n'
                f'          "position": {pos},\n'
                f'          "text": "{_js(text)}",\n'
                f'          "author": {{ "@type": "Person", "name": "{_js(author)}" }}\n'
                '        }'
            )
    joined = ",\n".join(items)
    return ('{\n  "@context": "https://schema.org",\n'
            '  "@type": "CollectionPage",\n'
            f'  "name": "{total} Quotes About Feeling Confused About Life",\n'
            f'  "description": "A collection of {total} quotes on feeling lost, stuck and confused about life.",\n'
            '  "url": "https://confusedlife.online/quotes/confused-about-life/",\n'
            '  "isPartOf": { "@id": "https://confusedlife.online/#website" },\n'
            '  "publisher": { "@id": "https://confusedlife.online/#organization" },\n'
            f'  "mainEntity": {{\n    "@type": "ItemList",\n'
            f'    "numberOfItems": {total},\n'
            '    "itemListElement": [\n' + joined + "\n    ]\n  }\n}")


def topics_schema():
    entries = [
        ("/guides/feeling-lost-in-life/", "Feeling Lost in Life: A Practical Guide"),
        ("/guides/why-am-i-so-confused-about-life/", "Why Am I So Confused About Life?"),
        ("/guides/signs-you-are-feeling-lost/", "15 Signs You're Feeling Lost"),
        ("/guides/i-dont-know-what-to-do-with-my-life/", "\"I Don't Know What to Do With My Life\""),
        ("/guides/how-to-find-your-purpose/", "How to Find Your Purpose"),
        ("/guides/quarter-life-crisis/", "Quarter-Life Crisis"),
        ("/tools/clarity-quiz/", "The Clarity Quiz"),
        ("/quotes/confused-about-life/", "60 Quotes About Being Confused"),
    ]
    items = []
    for i, (path, name) in enumerate(entries, start=1):
        items.append(
            '        {\n'
            f'          "@type": "ListItem",\n'
            f'          "position": {i},\n'
            f'          "name": "{_js(name)}",\n'
            f'          "url": "{SITE}{path}"\n'
            '        }'
        )
    joined = ",\n".join(items)
    return ('{\n  "@context": "https://schema.org",\n'
            '  "@type": "CollectionPage",\n'
            '  "name": "All Guides and Tools",\n'
            '  "description": "Every guide, tool and collection on ConfusedLife.online.",\n'
            '  "url": "https://confusedlife.online/topics/",\n'
            '  "isPartOf": { "@id": "https://confusedlife.online/#website" },\n'
            '  "publisher": { "@id": "https://confusedlife.online/#organization" },\n'
            '  "mainEntity": {\n    "@type": "ItemList",\n'
            f'    "numberOfItems": {len(entries)},\n'
            '    "itemListElement": [\n' + joined + "\n    ]\n  }\n}")


def build_quotes():
    total = sum(len(qs) for _, qs in QUOTE_SECTIONS)
    sections = []
    for heading, quotes in QUOTE_SECTIONS:
        cards = "\n".join(quote_card(t, a) for t, a in quotes)
        sections.append(f"""    <section class="section" id="{heading.lower().replace(' ', '-').replace('&', 'and')}">
      <div class="wrap">
        <h2 class="section-head" style="margin-bottom:2rem">{heading}</h2>
        <div class="grid grid-2">
{cards}
        </div>
      </div>
    </section>""")

    body = "\n\n".join(sections)

    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
{head(f"{total} Quotes About Feeling Confused About Life",
      f"{total} quotes on feeling lost, stuck and confused about life — grouped by what you need to hear: being lost, not knowing yet, purpose, starting, and bad days.",
      "/quotes/confused-about-life/", schema=quotes_schema(total))}
</head>
<body>

{header("quotes")}

<main id="main">
  <section class="hero">
    <div class="wrap">
      <p class="eyebrow">Quotes</p>
      <h1>{total} quotes for when life feels confusing</h1>
      <p class="hero-lede">
        Grouped by what you probably need to hear rather than who said it first.
        Tap the copy icon to save one, or the share icon to send it to someone
        who's quietly in the same position.
      </p>
    </div>
  </section>

{body}

  <section class="section section-alt">
    <div class="wrap">
      <div class="cta-panel">
        <h2>Quotes help for about an hour</h2>
        <p>They're good for company and not much good for direction. When you want the other half, the two-minute self-check will tell you which kind of confusion you're actually in.</p>
        <div class="btn-row">
          <a class="btn btn-primary" href="/tools/clarity-quiz/">Take the Clarity Quiz</a>
          <a class="btn btn-ghost" href="/guides/feeling-lost-in-life/">Read the main guide</a>
        </div>
      </div>
    </div>
  </section>
</main>

{footer()}

<script src="/assets/js/main.js" defer></script>
</body>
</html>
"""
    write("/quotes/confused-about-life/index.html", page)
    print(f"  wrote /quotes/confused-about-life/ ({total} quotes)")


# --------------------------------------------------------------------------
# Quiz page
# --------------------------------------------------------------------------

def build_quiz():
    qas = [
        ("Is the Clarity Quiz a diagnostic test?",
         "No. It's a reflective self-check designed to help you notice which areas of your life feel least anchored. It hasn't been clinically validated, it isn't a screening tool for any condition, and a low score is a snapshot of one week — not a verdict about you."),
        ("Do you store my answers?",
         "No. The entire quiz runs in your browser. Nothing is sent to a server, nothing is saved, and there's no account. If you close the tab, your answers are gone."),
        ("How long does it take?",
         "About two minutes for twelve questions. There's no email required to see your result."),
        ("My score was low. What should I do?",
         "Start with the three suggestions in your result — they're ordered by what tends to help fastest. If you scored low mostly on energy and connection and it's been that way for more than a couple of months, that's worth mentioning to a GP or therapist."),
    ]

    body = """  <section class="hero" style="padding-bottom:clamp(2rem,5vw,3rem)">
    <div class="wrap measure">
      <p class="eyebrow">Self-check tool</p>
      <h1>The Clarity Quiz</h1>
      <p class="hero-lede">
        Twelve questions about direction, values, energy and connection. You'll get a
        score, a breakdown of where the fog is thickest, and three specific things to
        try this week. Two minutes, nothing stored.
      </p>
    </div>
  </section>

  <section class="section" style="padding-top:clamp(1.5rem,4vw,2.5rem)">
    <div class="wrap measure">
      <div class="disclaimer-notice disclaimer-notice--banner" role="note" aria-label="Disclaimer">
        <p><strong>Not professional advice.</strong> The Clarity Quiz is a reflective self-check, not a diagnostic or screening tool, and gives no medical, psychological, or clinical advice. If you are in crisis, contact local emergency services or a crisis line such as <a href="https://findahelpline.com" rel="noopener nofollow" target="_blank">findahelpline.com</a> (international) or 988 (US).</p>
      </div>
      <div class="quiz-shell" data-quiz>
        <div class="quiz-head">
          <div class="quiz-meta">
            <span data-quiz-progress>Question 1 of 12</span>
            <span>~2 min</span>
          </div>
          <div class="quiz-track"><div class="quiz-fill"></div></div>
        </div>
        <div class="quiz-body">
          <h2 class="quiz-q" data-quiz-question></h2>
          <div data-quiz-body></div>
        </div>
        <div class="quiz-foot">
          <button class="btn btn-ghost" type="button" data-quiz-back>Back</button>
          <button class="btn btn-primary" type="button" data-quiz-next disabled>Next</button>
        </div>
      </div>

      <p class="text-small text-soft" style="margin-top:1.25rem">
        Runs entirely in your browser &mdash; no answers are sent anywhere or saved.
        Not a diagnostic tool. <a href="/disclaimer/">Read our disclaimer</a>.
      </p>
    </div>
  </section>

  <section class="section section-alt">
    <div class="wrap measure">
      <h2>What the quiz measures</h2>
      <p>Most "am I lost?" quizzes measure one thing. This one separates four, because they need completely different responses and applying the wrong one is how people end up stuck for years.</p>

      <div class="grid" style="gap:1rem;margin-top:1.75rem">
        <div class="card">
          <h3>Direction</h3>
          <p>Whether you have any sense of where you're heading. Low scores here respond to experiments and deadlines, not more thinking.</p>
        </div>
        <div class="card">
          <h3>Values</h3>
          <p>Whether you know what you actually want — as opposed to what you've absorbed from the people around you. Low scores respond to subtraction before addition.</p>
        </div>
        <div class="card">
          <h3>Energy</h3>
          <p>Not motivation in the abstract, but the practical question of whether you have the capacity to act on what you want. Low scores respond to reducing load, not to trying harder.</p>
        </div>
        <div class="card">
          <h3>Connection</h3>
          <p>Whether anyone really knows how you're doing. This one is easy to skip and it quietly predicts how long everything else takes.</p>
        </div>
      </div>
    </div>
  </section>

  <section class="section">
    <div class="wrap measure">
      <h2>About the quiz</h2>

      <div class="faq">
        <details>
          <summary>Is the Clarity Quiz a diagnostic test?</summary>
          <div class="faq-answer">
            <p>No. It's a reflective self-check designed to help you notice which areas of your life feel least anchored. It hasn't been clinically validated, it isn't a screening tool for any condition, and a low score is a snapshot of one week — not a verdict about you.</p>
          </div>
        </details>
        <details>
          <summary>Do you store my answers?</summary>
          <div class="faq-answer">
            <p>No. The entire quiz runs in your browser. Nothing is sent to a server, nothing is saved, and there's no account. If you close the tab, your answers are gone.</p>
          </div>
        </details>
        <details>
          <summary>How long does it take?</summary>
          <div class="faq-answer">
            <p>About two minutes for twelve questions. There's no email required to see your result.</p>
          </div>
        </details>
        <details>
          <summary>My score was low. What should I do?</summary>
          <div class="faq-answer">
            <p>Start with the three suggestions in your result — they're ordered by what tends to help fastest. If you scored low mostly on energy and connection, and it's been that way for more than a couple of months, that's worth mentioning to a GP or therapist.</p>
          </div>
        </details>
      </div>

      <p class="text-soft">Rather read first? Start with the <a href="/guides/feeling-lost-in-life/">main guide on feeling lost</a>, or find your specific situation in <a href="/guides/why-am-i-so-confused-about-life/">the twelve common causes</a>.</p>
    </div>
  </section>
"""

    extra_head = f'\n{_schema_block(faq_schema(qas))}'
    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
{head("Clarity Quiz: How Lost Are You, Really?",
      "A 2-minute self-check across direction, values, energy and connection. Twelve questions, a scored breakdown, three things to try this week.",
      "/tools/clarity-quiz/", extra=extra_head)}
</head>
<body>

{header("quiz")}

<main id="main">
{body}
</main>

{footer()}

<script src="/assets/js/main.js" defer></script>
<script src="/assets/js/quiz.js" defer></script>
</body>
</html>
"""
    write("/tools/clarity-quiz/index.html", page)
    print("  wrote /tools/clarity-quiz/")


# --------------------------------------------------------------------------
# Topics index
# --------------------------------------------------------------------------

def build_topics():
    body = """  <section class="hero" style="padding-bottom:clamp(2rem,5vw,3rem)">
    <div class="wrap">
      <p class="eyebrow">Everything</p>
      <h1>All guides and tools</h1>
      <p class="hero-lede">
        Every page on ConfusedLife.online, grouped by what you're actually trying to work out.
      </p>
    </div>
  </section>

  <section class="section" style="padding-top:clamp(1.5rem,4vw,2.5rem)">
    <div class="wrap">
      <h2 class="section-head">Start with the main guide</h2>
      <div class="grid grid-3">
        <article class="card">
          <span class="card-kicker">Core guide</span>
          <h3><a href="/guides/feeling-lost-in-life/">Feeling Lost in Life: A Practical Guide</a></h3>
          <p>The four kinds of confusion, why they happen, what quietly makes it worse, and a seven-day plan. Start here if you're not sure what your problem is yet.</p>
          <a class="card-link" href="/guides/feeling-lost-in-life/">Read the guide</a>
        </article>
        <article class="card">
          <span class="card-kicker">Tool</span>
          <h3><a href="/tools/clarity-quiz/">The Clarity Quiz</a></h3>
          <p>Twelve questions across direction, values, energy and connection. Two minutes, a scored breakdown, and three things to try this week.</p>
          <a class="card-link" href="/tools/clarity-quiz/">Take the quiz</a>
        </article>
        <article class="card">
          <span class="card-kicker">Collection</span>
          <h3><a href="/quotes/confused-about-life/">60 Quotes About Being Confused</a></h3>
          <p>Grouped by what you need to hear rather than who said it. Copy or share any of them.</p>
          <a class="card-link" href="/quotes/confused-about-life/">Browse quotes</a>
        </article>
      </div>
    </div>
  </section>

  <section class="section section-alt">
    <div class="wrap">
      <h2 class="section-head">Working out what's wrong</h2>
      <div class="grid grid-2">
        <article class="card">
          <h3><a href="/guides/why-am-i-so-confused-about-life/">Why Am I So Confused About Life?</a></h3>
          <p>Twelve causes, ordered by how often each turns out to be the real one — including the two that disguise themselves as laziness and the one that disguises itself as clarity.</p>
          <a class="card-link" href="/guides/why-am-i-so-confused-about-life/">Find your cause</a>
        </article>
        <article class="card">
          <h3><a href="/guides/signs-you-are-feeling-lost/">15 Signs You're Feeling Lost</a></h3>
          <p>Going through the motions is the famous one. But it also shows up as overworking, as endless research, and as being weirdly fine with everything.</p>
          <a class="card-link" href="/guides/signs-you-are-feeling-lost/">Check the signs</a>
        </article>
      </div>
    </div>
  </section>

  <section class="section">
    <div class="wrap">
      <h2 class="section-head">Direction, work and meaning</h2>
      <div class="grid grid-2">
        <article class="card">
          <h3><a href="/guides/i-dont-know-what-to-do-with-my-life/">"I Don't Know What to Do With My Life"</a></h3>
          <p>Usually not a shortage of options but a surplus with no way to rank them. A method for narrowing the field in an afternoon.</p>
          <a class="card-link" href="/guides/i-dont-know-what-to-do-with-my-life/">Get unstuck</a>
        </article>
        <article class="card">
          <h3><a href="/guides/how-to-find-your-purpose/">How to Find Your Purpose</a></h3>
          <p>Purpose is built, not found. A working method based on what you keep returning to — and why "find your passion" mostly makes people feel worse.</p>
          <a class="card-link" href="/guides/how-to-find-your-purpose/">Start building</a>
        </article>
        <article class="card">
          <h3><a href="/guides/quarter-life-crisis/">Quarter-Life Crisis</a></h3>
          <p>What's actually happening in your twenties and thirties, why it isn't immaturity, and what the period is genuinely for.</p>
          <a class="card-link" href="/guides/quarter-life-crisis/">Understand it</a>
        </article>
      </div>
    </div>
  </section>

  <section class="section section-alt">
    <div class="wrap">
      <h2 class="section-head">About this site</h2>
      <div class="grid grid-2">
        <article class="card">
          <h3><a href="/about/">Who we are</a></h3>
          <p>An independent editorial project. No course, no coaching funnel, no 5am routine waiting at the end of an article.</p>
          <a class="card-link" href="/about/">Read more</a>
        </article>
        <article class="card">
          <h3><a href="/editorial-policy/">Editorial policy</a></h3>
          <p>How we research, what we cite, where the evidence is thin, and what we refuse to publish on this topic.</p>
          <a class="card-link" href="/editorial-policy/">Read the policy</a>
        </article>
      </div>
    </div>
  </section>
"""

    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
{head("All Guides and Tools | ConfusedLife.online",
      "Every guide, tool and collection on ConfusedLife.online, grouped by what you're trying to work out — from feeling lost to career direction to purpose.",
      "/topics/", schema=topics_schema())}
</head>
<body>

{header("topics")}

<main id="main">
{body}
</main>

{footer()}

<script src="/assets/js/main.js" defer></script>
</body>
</html>
"""
    write("/topics/index.html", page)
    print("  wrote /topics/")


# --------------------------------------------------------------------------
# Static trust pages
# --------------------------------------------------------------------------

def build_pages():
    PAGES = [
        {
            "file": "about.html",
            "slug": "/about/",
            "title": "About ConfusedLife.online",
            "desc": "An independent editorial project publishing plain-English guides on feeling lost, stuck or confused about life. No course, no coaching funnel, nothing to buy.",
            "crumb": "About",
        },
        {
            "file": "editorial-policy.html",
            "slug": "/editorial-policy/",
            "title": "Editorial Policy",
            "desc": "How we research and write, what we cite, where the evidence runs out, and the things we refuse to publish on this topic.",
            "crumb": "Editorial policy",
        },
        {
            "file": "disclaimer.html",
            "slug": "/disclaimer/",
            "title": "Disclaimer & Mental Health Resources",
            "desc": "General information, not medical advice. Plus crisis lines and support services by country, including 988 in the US and 116 123 in the UK.",
            "crumb": "Disclaimer",
        },
        {
            "file": "privacy-policy.html",
            "slug": "/privacy-policy/",
            "title": "Privacy Policy",
            "desc": "We collect almost nothing. No analytics trackers, no advertising cookies, and quiz answers never leave your browser.",
            "crumb": "Privacy policy",
        },
        {
            "file": "terms.html",
            "slug": "/terms/",
            "title": "Terms of Use",
            "desc": "The rules for using ConfusedLife.online, in plain language.",
            "crumb": "Terms",
        },
        {
            "file": "contact.html",
            "slug": "/contact/",
            "title": "Contact",
            "desc": "Corrections, quote attributions and permissions. We can't offer personal advice, and this page explains why.",
            "crumb": "Contact",
        },
    ]

    for meta in PAGES:
        body = (CONTENT / meta["file"]).read_text(encoding="utf-8")
        meta = dict(meta)
        meta["crumbs"] = [{"name": "Home", "url": f"{SITE}/"}, {"name": meta["crumb"]}]
        out = render_simple(meta, body, nav_key="page")
        write(meta["slug"] + "index.html", out)
        print(f"  wrote {meta['slug']}")


# --------------------------------------------------------------------------
# 404
# --------------------------------------------------------------------------

def build_404():
    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
{head("Page Not Found | ConfusedLife.online",
      "That page doesn't exist. Here's where to go instead.",
      "/404.html")}
<meta name="robots" content="noindex, follow">
</head>
<body>

{header("home")}

<main id="main">
  <section class="hero">
    <div class="wrap measure">
      <p class="eyebrow">404</p>
      <h1>That page doesn't exist</h1>
      <p class="hero-lede">
        Which is, in its own small way, thematically appropriate. Here's where you probably meant to go.
      </p>
      <div class="btn-row">
        <a class="btn btn-primary" href="/guides/feeling-lost-in-life/">Read the main guide</a>
        <a class="btn btn-ghost" href="/">Back to the homepage</a>
      </div>
    </div>
  </section>

  <section class="section">
    <div class="wrap">
      <div class="grid grid-3">
        <article class="card">
          <h3><a href="/tools/clarity-quiz/">The Clarity Quiz</a></h3>
          <p>Twelve questions, two minutes, nothing stored.</p>
        </article>
        <article class="card">
          <h3><a href="/quotes/confused-about-life/">60 Quotes</a></h3>
          <p>For when you'd rather just feel less alone first.</p>
        </article>
        <article class="card">
          <h3><a href="/topics/">All topics</a></h3>
          <p>Every guide on the site, grouped by question.</p>
        </article>
      </div>
    </div>
  </section>
</main>

{footer()}

<script src="/assets/js/main.js" defer></script>
</body>
</html>
"""
    write("/404.html", page)
    print("  wrote /404.html")


# --------------------------------------------------------------------------
# Sitemap
# --------------------------------------------------------------------------

SITEMAP_URLS = [
    ("/", "1.0", "weekly"),
    ("/guides/feeling-lost-in-life/", "1.0", "monthly"),
    ("/guides/why-am-i-so-confused-about-life/", "0.9", "monthly"),
    ("/guides/signs-you-are-feeling-lost/", "0.9", "monthly"),
    ("/guides/i-dont-know-what-to-do-with-my-life/", "0.9", "monthly"),
    ("/guides/how-to-find-your-purpose/", "0.9", "monthly"),
    ("/guides/quarter-life-crisis/", "0.8", "monthly"),
    ("/tools/clarity-quiz/", "0.9", "monthly"),
    ("/wall/", "0.7", "weekly"),
    ("/quotes/confused-about-life/", "0.8", "monthly"),
    ("/topics/", "0.7", "monthly"),
    ("/about/", "0.5", "yearly"),
    ("/editorial-policy/", "0.4", "yearly"),
    ("/disclaimer/", "0.4", "yearly"),
    ("/privacy-policy/", "0.3", "yearly"),
    ("/terms/", "0.3", "yearly"),
    ("/contact/", "0.3", "yearly"),
]


def build_wall():
    body = (CONTENT / "wall.html").read_text(encoding="utf-8")
    canonical = "/wall/"
    schema = f"""{{
  "@context": "https://schema.org",
  "@graph": [
    {{
      "@type": "WebPage",
      "@id": "{SITE}/wall/#webpage",
      "url": "{SITE}/wall/",
      "name": "The Clarity Wall",
      "description": "Share what's weighing on you and get a short, non-clinical Personal Reflection Report.",
      "isPartOf": {{ "@id": "{SITE}/#website" }},
      "inLanguage": "en-US"
    }},
    {{
      "@type": "BreadcrumbList",
      "itemListElement": [
        {{ "@type": "ListItem", "position": 1, "name": "Home", "item": "{SITE}/" }},
        {{ "@type": "ListItem", "position": 2, "name": "The Clarity Wall" }}
      ]
    }}
  ]
}}"""
    extra = '<link rel="stylesheet" href="/assets/css/wall.css">'
    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
{head("The Clarity Wall — share, reflect, you're not alone", "Post what's weighing on you anonymously, read others on the wall, and get a short Personal Reflection Report. A reflective exercise, not therapy or a diagnosis.", canonical, og_type="website", schema=schema, extra=extra)}
</head>
<body>

{header("wall")}

<main id="main">
{body}
</main>

{footer()}

<script src="/assets/js/main.js" defer></script>
<script src="/assets/js/wall.js" defer></script>
</body>
</html>"""
    write(canonical + "index.html", page)
    print("  wrote /wall/")


def build_sitemap():
    today = datetime.date.today().isoformat()
    entries = []
    for path, prio, freq in SITEMAP_URLS:
        entries.append(
            f"  <url>\n"
            f"    <loc>{SITE}{path}</loc>\n"
            f"    <lastmod>{today}</lastmod>\n"
            f"    <changefreq>{freq}</changefreq>\n"
            f"    <priority>{prio}</priority>\n"
            f"  </url>"
        )
    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
           + "\n".join(entries) +
           '\n</urlset>\n')
    write("/sitemap.xml", xml)
    print(f"  wrote /sitemap.xml ({len(entries)} urls)")


# --------------------------------------------------------------------------

def main():
    print("Building ConfusedLife.online …")
    build_articles()
    build_quotes()
    build_quiz()
    build_wall()
    build_topics()
    build_pages()
    build_404()
    build_sitemap()
    print("Done.")


if __name__ == "__main__":
    main()
