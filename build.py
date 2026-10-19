#!/usr/bin/env python3
"""Build the static Kaogong wiki from Markdown content.

The wiki is deliberately a small, dependency-light static site: Python-Markdown
renders the pages, one shared template supplies the navigation and search, and
FastAPI serves the generated ``wiki/site`` directory at ``/wiki``.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    import markdown
    from markdown.extensions.toc import TocExtension, slugify_unicode
    from pygments.formatters import HtmlFormatter
except ImportError as exc:  # pragma: no cover - actionable message for builders
    raise SystemExit(
        "Wiki build needs markdown and pygments. Install with "
        "`.venv/bin/pip install markdown pygments` or `pip install -e '.[docs]'`."
    ) from exc

ROOT = Path(__file__).resolve().parent
CONTENT = ROOT / "content"
ASSETS = ROOT / "assets"
DEFAULT_OUT = ROOT / "site"

CALLOUT_LABELS = {
    "note": "提示",
    "tip": "技巧",
    "warning": "注意",
    "important": "重要",
    "chemistry": "化学背景",
}

# Public brand used by the site chrome. The wiki is published on its own, so it
# uses the product name; application packages keep their existing names.
BRAND = "Kaogong"
BRAND_MARK = "考"
BRAND_FOOTER = "Kaogong 是通用 LAMMPS 工作台：示例只组合模块与数据参数，不为某个教程写死流程。"


def _prefix(base: str = "/wiki") -> str:
    """Return the mount prefix for generated links.

    ``/wiki`` (default, FastAPI mount), ``/kaogong-wiki`` (Pages project site),
    or ``""`` (custom domain served from the site root).
    """
    slug = base.strip("/")
    return f"/{slug}" if slug else ""


@dataclass
class Page:
    slug: str
    nav: str
    title: str
    description: str
    section: str
    body: str
    toc: list[dict[str, Any]]
    reading_minutes: int

    def href(self, base: str = "/wiki") -> str:
        prefix = _prefix(base)
        return f"{prefix}/" if self.slug == "index" else f"{prefix}/{self.slug}/"


def load_nav(path: Path = ROOT / "nav.json") -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("nav.json must be a list of sections")
    seen: set[str] = set()
    for section in data:
        for page in section.get("pages", []):
            slug = page.get("slug")
            if not slug or slug in seen:
                raise ValueError(f"invalid or duplicate wiki slug: {slug!r}")
            seen.add(slug)
            if not (CONTENT / f"{slug}.md").is_file():
                raise ValueError(f"nav references missing page: {slug}.md")
    return data


def convert_callouts(text: str) -> str:
    """Turn GitHub-style ``> [!NOTE]`` blocks into styled HTML callouts."""
    lines = text.splitlines()
    out: list[str] = []
    i = 0
    pattern = re.compile(r"^>\s*\[!(NOTE|TIP|WARNING|IMPORTANT|CHEMISTRY)\]\s*$", re.I)
    while i < len(lines):
        match = pattern.match(lines[i].strip())
        if not match:
            out.append(lines[i])
            i += 1
            continue
        kind = match.group(1).lower()
        i += 1
        block: list[str] = []
        while i < len(lines) and lines[i].lstrip().startswith(">"):
            block.append(re.sub(r"^\s*>\s?", "", lines[i]))
            i += 1
        inner = "\n".join(block).strip()
        label = CALLOUT_LABELS.get(kind, kind.title())
        out.extend(
            [
                f'<div class="callout {kind}" markdown="1">',
                "",
                f"**{label}**",
                "",
                inner,
                "",
                "</div>",
            ]
        )
    return "\n".join(out)


def md_renderer() -> markdown.Markdown:
    return markdown.Markdown(
        extensions=[
            "extra",
            "sane_lists",
            "codehilite",
            "md_in_html",
            TocExtension(permalink=True, toc_depth="2-3", slugify=slugify_unicode),
        ],
        extension_configs={
            "codehilite": {"css_class": "highlight", "guess_lang": False, "linenums": False}
        },
        output_format="html5",
    )


def _strip_h1(text: str) -> tuple[str, str | None]:
    match = re.match(r"^\s*#\s+(.+?)\s*$", text, flags=re.M)
    if not match:
        return text, None
    return text[: match.start()] + text[match.end() :], match.group(1).strip()


def _toc_items(tokens: list[dict[str, Any]], depth: int = 0) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for token in tokens:
        level = int(token.get("level", 1))
        if level < 2 or level > 3:
            continue
        children = _toc_items(token.get("children", []), depth + 1)
        out.append(
            {
                "id": token.get("id", ""),
                "name": re.sub(r"<[^>]+>", "", token.get("name", "")),
                "level": level,
                "children": children,
            }
        )
    return out


def _reading_minutes(text: str) -> int:
    # Chinese text has few spaces; count characters and latin words separately.
    latin = len(re.findall(r"[A-Za-z0-9_]+", text))
    chars = len(re.findall(r"[\u4e00-\u9fff]", text))
    return max(1, round((latin / 220) + (chars / 420)))


def load_pages(nav: list[dict[str, Any]]) -> list[Page]:
    pages: list[Page] = []
    for section in nav:
        for item in section["pages"]:
            slug = item["slug"]
            raw = (CONTENT / f"{slug}.md").read_text(encoding="utf-8")
            body_md, h1 = _strip_h1(raw)
            md = md_renderer()
            body = md.convert(convert_callouts(body_md))
            toc = _toc_items(getattr(md, "toc_tokens", []))
            pages.append(
                Page(
                    slug=slug,
                    nav=item.get("nav", item["title"]),
                    title=item["title"],
                    description=item.get("description", ""),
                    section=section["section"],
                    body=body,
                    toc=toc,
                    reading_minutes=_reading_minutes(body_md),
                )
            )
    return pages


def _render_toc(items: list[dict[str, Any]]) -> str:
    if not items:
        return '<p class="toc-empty">本页没有小节。</p>'
    out = ['<ul class="toc-list">']
    for item in items:
        out.append(f'<li><a href="#{html.escape(item["id"])}">{html.escape(item["name"])}</a>')
        if item.get("children"):
            out.append(_render_toc(item["children"]))
        out.append("</li>")
    out.append("</ul>")
    return "".join(out)


def _sidebar(nav: list[dict[str, Any]], active: str, prefix: str = "/wiki") -> str:
    out: list[str] = []
    for section in nav:
        out.append(f'<div class="nav-section"><div class="nav-section-title">{html.escape(section["section"])}</div>')
        for item in section["pages"]:
            slug = item["slug"]
            href = f"{prefix}/" if slug == "index" else f"{prefix}/{slug}/"
            cls = "nav-link active" if slug == active else "nav-link"
            out.append(
                f'<a class="{cls}" href="{href}"><span class="nav-dot"></span>{html.escape(item["nav"])}</a>'
            )
        out.append("</div>")
    return "".join(out)


PAGE_TEMPLATE = """<!doctype html>
<html lang="zh-CN" data-theme="dark">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <meta name="color-scheme" content="dark light" />
  <meta name="description" content="{description}" />
  <title>{title}{title_suffix}</title>
  <link rel="stylesheet" href="{prefix}/assets/wiki.css" />
  <link rel="stylesheet" href="{prefix}/assets/pygments.css" />
</head>
<body data-page="{slug}">
  <div class="reading-progress"><span></span></div>
  <header class="topbar">
    <button class="icon-btn menu-toggle" aria-label="打开导航" data-menu-toggle>
      <span></span><span></span><span></span>
    </button>
    <a class="brand" href="{prefix}/">
      <span class="brand-mark">{brand_mark}</span>
      <span class="brand-text"><strong>{brand}</strong><em>Wiki</em></span>
    </a>
    <div class="topbar-center">
      <button class="search-trigger" data-search-open>
        <svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="7"></circle><path d="m20 20-3.5-3.5"></path></svg>
        <span>搜索文档</span><kbd>/</kbd>
      </button>
    </div>
    <div class="topbar-actions">
      <button class="icon-btn theme-toggle" data-theme-toggle aria-label="切换主题">
        <svg class="moon" viewBox="0 0 24 24"><path d="M21 12.8A9 9 0 1 1 11.2 3 7 7 0 0 0 21 12.8Z"></path></svg>
        <svg class="sun" viewBox="0 0 24 24"><circle cx="12" cy="12" r="4"></circle><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"></path></svg>
      </button>
    </div>
  </header>

  <div class="sidebar-scrim" data-menu-close></div>
  <div class="layout">
    <aside class="sidebar" data-sidebar>
      <div class="sidebar-inner">
        {sidebar}
        <div class="sidebar-foot">
          <span>LAMMPS 22 Jul 2025</span>
        </div>
      </div>
    </aside>

    <main class="content">
      <div class="breadcrumb"><a href="{prefix}/">Wiki</a><span>/</span><span>{section}</span><span>/</span><strong>{nav}</strong></div>
      <article class="prose">
        <div class="page-kicker">{section} · 约 {minutes} 分钟</div>
        <h1>{h1}</h1>
        {lead}
        {body}
      </article>
      <nav class="pager" aria-label="上一页/下一页">
        {pager}
      </nav>
      <footer class="page-foot">
        <p>{brand_footer}</p>
        <p><a href="{prefix}/extending/">如何添加模块 / 示例</a></p>
      </footer>
    </main>

    <aside class="toc" data-toc>
      <div class="toc-title">本页目录</div>
      {toc}
    </aside>
  </div>

  <div class="search-overlay" data-search-overlay hidden>
    <div class="search-panel" role="dialog" aria-modal="true" aria-label="搜索文档">
      <div class="search-box">
        <svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="7"></circle><path d="m20 20-3.5-3.5"></path></svg>
        <input id="wiki-search" type="search" autocomplete="off" placeholder="搜索模块、概念、教程…" data-search-input />
        <button class="icon-btn" data-search-close aria-label="关闭搜索">×</button>
      </div>
      <div class="search-results" data-search-results>
        <p class="search-hint">输入关键词，例如 <kbd>RDF</kbd>、<kbd>EAM</kbd>、<kbd>GCMC</kbd>。</p>
      </div>
      <div class="search-foot"><kbd>↑</kbd><kbd>↓</kbd> 选择 <kbd>Enter</kbd> 打开 <kbd>Esc</kbd> 关闭</div>
    </div>
  </div>

  <script>window.__WIKI_PREFIX__ = "{prefix}";</script>
  <script src="{prefix}/assets/wiki.js"></script>
</body>
</html>
"""


def _lead(description: str) -> str:
    return f'<p class="lead">{html.escape(description)}</p>' if description else ""


def _rewrite_body(body: str, prefix: str) -> str:
    """Point Markdown-authored absolute links at the configured mount prefix."""
    body = body.replace('href="/wiki/', f'href="{prefix}/')
    body = body.replace('src="/wiki/', f'src="{prefix}/')
    return body


def _pager(pages: list[Page], index: int, base: str = "/wiki") -> str:
    out: list[str] = []
    if index > 0:
        prev = pages[index - 1]
        out.append(
            f'<a class="pager-link prev" href="{prev.href(base)}"><span>上一页</span><strong>{html.escape(prev.nav)}</strong></a>'
        )
    else:
        out.append("<span></span>")
    if index + 1 < len(pages):
        nxt = pages[index + 1]
        out.append(
            f'<a class="pager-link next" href="{nxt.href(base)}"><span>下一页</span><strong>{html.escape(nxt.nav)}</strong></a>'
        )
    else:
        out.append("<span></span>")
    return "".join(out)


def _search_index(pages: list[Page], base: str = "/wiki") -> list[dict[str, Any]]:
    index: list[dict[str, Any]] = []
    for page in pages:
        text = re.sub(r"<[^>]+>", " ", page.body)
        text = html.unescape(re.sub(r"\s+", " ", text)).strip()
        index.append(
            {
                "title": page.title,
                "nav": page.nav,
                "section": page.section,
                "url": page.href(base),
                "description": page.description,
                "text": text[:12000],
            }
        )
    return index


def build(out_dir: Path = DEFAULT_OUT, base: str = "/wiki") -> list[Page]:
    nav = load_nav()
    pages = load_pages(nav)
    prefix = _prefix(base)
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    shutil.copytree(ASSETS, out_dir / "assets")
    pygments_css = HtmlFormatter(style="monokai").get_style_defs(".highlight")
    (out_dir / "assets" / "pygments.css").write_text(pygments_css, encoding="utf-8")

    for index, page in enumerate(pages):
        html_text = PAGE_TEMPLATE.format(
            title=html.escape(page.title),
            title_suffix="" if page.slug == "index" else f" · {BRAND} Wiki",
            description=html.escape(page.description),
            slug=page.slug,
            prefix=prefix,
            brand=BRAND,
            brand_mark=BRAND_MARK,
            brand_footer=BRAND_FOOTER,
            sidebar=_sidebar(nav, page.slug, prefix),
            section=html.escape(page.section),
            nav=html.escape(page.nav),
            minutes=page.reading_minutes,
            h1=html.escape(page.title),
            lead=_lead(page.description),
            body=_rewrite_body(page.body, prefix),
            toc=_render_toc(page.toc),
            pager=_pager(pages, index, base),
        )
        target = out_dir / "index.html" if page.slug == "index" else out_dir / page.slug / "index.html"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(html_text, encoding="utf-8")

    (out_dir / "search-index.json").write_text(
        json.dumps(_search_index(pages, base), ensure_ascii=False, indent=2), encoding="utf-8"
    )
    # A tiny, self-contained 404 page also works when previewing the folder.
    home = next(page for page in pages if page.slug == "index")
    (out_dir / "404.html").write_text(
        (out_dir / "index.html").read_text(encoding="utf-8").replace(
            f"<h1>{html.escape(home.title)}</h1>", "<h1>页面不存在</h1>"
        ),
        encoding="utf-8",
    )
    return pages


def main() -> None:
    parser = argparse.ArgumentParser(description=f"Build the {BRAND} wiki")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument(
        "--base",
        default="/wiki",
        help="Mount prefix: /wiki (app), /<repo> (Pages project), \"\" (domain root)",
    )
    args = parser.parse_args()
    pages = build(args.out, base=args.base)
    print(f"built {len(pages)} pages -> {args.out}")


if __name__ == "__main__":
    main()
