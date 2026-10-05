# -*- coding: utf-8 -*-
"""Build static site for GitHub Pages → _site/ and local 공명_소개/docs/"""
from __future__ import annotations

import html
import re
import shutil
from pathlib import Path
from urllib.parse import quote, unquote, urlparse

ROOT = Path(__file__).resolve().parents[1]
INTRO = ROOT / "04_발표" / "공명_소개"
STATION = ROOT / "04_발표" / "공명스테이션_예시.html"
DOCS_SRC = ROOT / "04_발표"
OUT = ROOT / "_site"

GH_BASE = "https://github.com/Jajungi/resonance"
GH_TREE = f"{GH_BASE}/tree/main/04_%EB%B0%9C%ED%91%9C"
GH_BLOB = f"{GH_BASE}/blob/main/04_%EB%B0%9C%ED%91%9C"


def gh_path(rel: str, *, blob: bool) -> str:
    encoded = "/".join(quote(part, safe="") for part in rel.split("/") if part)
    return f"{GH_BLOB if blob else GH_TREE}/{encoded}"

DOC_PAGES = [
    ("공명_소설_독자_1권_합본.md", "dokja-1.html", "독자판 1권 합본"),
    ("공명_소설_독자_2권_합본.md", "dokja-2.html", "독자판 2권 합본"),
]


def rewrite_href(href: str) -> str:
    """Map repo-relative markdown links to live site or GitHub."""
    raw = href.strip()
    if not raw or raw.startswith(("#", "http://", "https://", "mailto:")):
        return raw

    parsed = urlparse(raw)
    path = unquote(parsed.path).replace("\\", "/")
    frag = ("#" + parsed.fragment) if parsed.fragment else ""

    # strip leading ./ ../ noise for matching
    norm = path
    while norm.startswith("../") or norm.startswith("./"):
        if norm.startswith("../"):
            norm = norm[3:]
        else:
            norm = norm[2:]
    norm = norm.lstrip("/")

    # 독자판 장별
    m = re.search(r"공명_소설_분석_독자판/(?:2권/)?([^/#]+\.md)$", norm)
    if m:
        name = m.group(1)[:-3] + ".html"
        if "/2권/" in norm or norm.startswith("2권/"):
            return f"dokja/2권/{name}{frag}"
        return f"dokja/{name}{frag}"
    if re.search(r"공명_소설_분석_독자판/2권/?$", norm):
        return f"dokja/2권/{frag}" if frag else "dokja/2권/"
    if re.search(r"공명_소설_분석_독자판/?$", norm):
        return f"dokja/{frag}" if frag else "dokja/"

    # 합본 · 목차
    if "공명_소설_독자_1권_합본" in norm:
        return f"dokja-1.html{frag}"
    if "공명_소설_독자_2권_합본" in norm:
        return f"dokja-2.html{frag}"
    if re.search(r"공명_소설_독자_1권\.md$", norm):
        return f"dokja-1-toc.html{frag}"
    if re.search(r"공명_소설_독자_2권\.md$", norm):
        return f"dokja-2-toc.html{frag}"

    # 연구자판·분권 원고 → GitHub (사이트에 올리지 않음)
    if "공명_소설_분석" in norm and "공명_소설_분석_독자판" not in norm:
        idx = norm.find("공명_소설_분석")
        rel = norm[idx:]
        return gh_path(rel, blob=rel.endswith(".md")) + frag
    if re.search(r"공명_소설(?:/|$)", norm) and "공명_소설_분석" not in norm:
        idx = norm.find("공명_소설")
        rel = norm[idx:]
        return gh_path(rel, blob=rel.endswith(".md")) + frag

    # already site-relative html under docs
    if path.endswith(".html") or path.endswith("/"):
        return path + frag

    # leftover .md that we don't publish as raw files
    if norm.endswith(".md"):
        return gh_path(norm.split("/")[-1], blob=True) + frag

    return raw


def md_inline(text: str) -> str:
    text = html.escape(text)

    def link_sub(m: re.Match[str]) -> str:
        label, href = m.group(1), m.group(2)
        href2 = rewrite_href(href)
        return f'<a href="{html.escape(href2, quote=True)}">{label}</a>'

    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", link_sub, text)
    return text


def md_to_html_body(md: str) -> str:
    lines = md.replace("\r\n", "\n").split("\n")
    out: list[str] = []
    i = 0
    in_ul = False
    in_ol = False

    def close_lists() -> None:
        nonlocal in_ul, in_ol
        if in_ul:
            out.append("</ul>")
            in_ul = False
        if in_ol:
            out.append("</ol>")
            in_ol = False

    while i < len(lines):
        line = lines[i]
        if not line.strip():
            close_lists()
            i += 1
            continue
        if line.startswith("```"):
            close_lists()
            i += 1
            buf: list[str] = []
            while i < len(lines) and not lines[i].startswith("```"):
                buf.append(html.escape(lines[i]))
                i += 1
            if i < len(lines):
                i += 1
            out.append("<pre><code>" + "\n".join(buf) + "</code></pre>")
            continue
        m = re.match(r"^(#{1,3})\s+(.*)$", line)
        if m:
            close_lists()
            level = len(m.group(1))
            out.append(f"<h{level}>{md_inline(m.group(2).strip())}</h{level}>")
            i += 1
            continue
        if re.match(r"^>\s?", line):
            close_lists()
            quote: list[str] = []
            while i < len(lines) and re.match(r"^>\s?", lines[i]):
                quote.append(re.sub(r"^>\s?", "", lines[i]))
                i += 1
            body = "<br />".join(md_inline(q) for q in quote if q.strip())
            out.append(f'<blockquote class="doc-quote">{body}</blockquote>')
            continue
        if re.match(r"^[-*]\s+", line):
            if in_ol:
                out.append("</ol>")
                in_ol = False
            if not in_ul:
                out.append("<ul>")
                in_ul = True
            out.append("<li>" + md_inline(re.sub(r"^[-*]\s+", "", line)) + "</li>")
            i += 1
            continue
        if re.match(r"^\d+\.\s+", line):
            if in_ul:
                out.append("</ul>")
                in_ul = False
            if not in_ol:
                out.append("<ol>")
                in_ol = True
            out.append("<li>" + md_inline(re.sub(r"^\d+\.\s+", "", line)) + "</li>")
            i += 1
            continue
        if line.strip() == "---":
            close_lists()
            out.append("<hr />")
            i += 1
            continue
        # skip markdown tables as raw paragraphs of pipes — keep simple
        if "|" in line and re.match(r"^\s*\|", line):
            close_lists()
            rows: list[str] = []
            while i < len(lines) and "|" in lines[i]:
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if all(re.match(r"^:?-+:?$", c or "") for c in cells):
                    i += 1
                    continue
                tds = "".join(f"<td>{md_inline(c)}</td>" for c in cells)
                rows.append(f"<tr>{tds}</tr>")
                i += 1
            if rows:
                out.append('<table class="compare-table"><tbody>' + "".join(rows) + "</tbody></table>")
            continue

        close_lists()
        para = [line]
        i += 1
        while i < len(lines) and lines[i].strip() and not re.match(
            r"^(#{1,3}\s+|[-*]\s+|\d+\.\s+|```|---\s*$|>\s?|\|)", lines[i]
        ):
            para.append(lines[i])
            i += 1
        out.append("<p>" + md_inline(" ".join(p.strip() for p in para)) + "</p>")
    close_lists()
    # rewrite any leftover bare hrefs that slipped through as html in body
    def href_fix(m: re.Match[str]) -> str:
        h = rewrite_href(m.group(1))
        return f'href="{html.escape(h, quote=True)}"'

    return re.sub(r'href="([^"]+)"', href_fix, "\n".join(out))


def wrap_doc(title: str, body: str, *, depth: int = 1) -> str:
    root = "../" * depth
    # rewrite relative dokja links based on depth
    def fix_local(m: re.Match[str]) -> str:
        h = m.group(1)
        if h.startswith(("http://", "https://", "#", "mailto:")):
            return m.group(0)
        # dokja-1.html etc from nested folder need ../
        if re.match(r"^(dokja-1|dokja-2|dokja-1-toc|dokja-2-toc)\.html", h):
            return f'href="{html.escape("../" * (depth - 1) + h if depth > 1 else h, quote=True)}"'
        if h.startswith("dokja/") and depth >= 2:
            # from docs/dokja/foo.html depth=2, dokja/x → x or ../dokja/x
            rest = h[len("dokja/") :]
            if depth == 2:
                return f'href="{html.escape(rest, quote=True)}"'
            if depth == 3:
                return f'href="{html.escape("../" + rest, quote=True)}"'
        return m.group(0)

    body2 = re.sub(r'href="([^"]+)"', fix_local, body)

    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{html.escape(title)} — 공명</title>
  <link rel="preconnect" href="https://cdn.jsdelivr.net" crossorigin />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css" rel="stylesheet" />
  <link href="https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@400;500;600;700&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="{root}styles.css" />
</head>
<body class="doc-page">
  <a class="skip" href="#main">본문으로 건너뛰기</a>
  <header class="site-header">
    <div class="header-inner">
      <a class="brand" href="{root}index.html">공명</a>
      <nav class="nav-tabs" aria-label="주요 페이지">
        <a href="{root}index.html">홈</a>
        <a href="{root}about.html">종교에 대하여</a>
        <a href="{root}visit.html">오는 법</a>
        <a href="{root}explain.html">설명</a>
        <a href="{root}library.html" aria-current="page">자료</a>
      </nav>
      <a class="nav-station" data-station href="{root}station.html">스테이션</a>
    </div>
  </header>
  <div class="doc-shell">
    <main id="main" class="page doc-main">
      <p class="eyebrow"><a href="{root}library.html">자료</a> · <a href="{root}text-dokja.html">독자판</a></p>
      <h1>{html.escape(title)}</h1>
      <article class="doc-body">
{body2}
      </article>
      <nav class="page-next" aria-label="돌아가기">
        <a href="{root}text-dokja.html">← 독자판으로</a>
        <a href="{root}library.html">자료 전체</a>
      </nav>
    </main>
  </div>
  <script src="{root}site.js" defer></script>
</body>
</html>
"""


def chapter_title(stem: str) -> str:
    return stem.replace("_", " ")


def build_toc_html(title: str, items: list[tuple[str, str]], *, depth: int = 1) -> str:
    """items: (href, label)"""
    lis = "\n".join(
        f'<li><a href="{html.escape(h, quote=True)}">{html.escape(label)}</a></li>'
        for h, label in items
    )
    body = f"<p>사이트에서 바로 읽는 목차입니다. 연구자판(아크 밀착)은 저장소에만 있습니다.</p>\n<ul>\n{lis}\n</ul>"
    return wrap_doc(title, body, depth=depth)


def build_docs(docs: Path) -> int:
    if docs.exists():
        shutil.rmtree(docs)
    docs.mkdir(parents=True, exist_ok=True)

    for src_name, out_name, title in DOC_PAGES:
        src = DOCS_SRC / src_name
        if not src.is_file():
            raise SystemExit(f"missing doc: {src}")
        body = md_to_html_body(src.read_text(encoding="utf-8"))
        (docs / out_name).write_text(wrap_doc(title, body, depth=1), encoding="utf-8")

    essays = DOCS_SRC / "공명_소설_분석_독자판"
    essay_n = 0
    if not essays.is_dir():
        return 0

    essay_dest = docs / "dokja"
    essay_dest.mkdir(parents=True, exist_ok=True)
    toc1: list[tuple[str, str]] = []
    toc2: list[tuple[str, str]] = []
    index_items: list[str] = []

    for md_path in sorted(essays.rglob("*.md")):
        if md_path.name.upper() == "README.MD":
            continue
        rel = md_path.relative_to(essays)
        html_rel = rel.with_suffix(".html").as_posix()
        title = chapter_title(md_path.stem)
        depth = 2 + len(rel.parts) - 1
        body = md_to_html_body(md_path.read_text(encoding="utf-8"))
        out_path = essay_dest / rel.with_suffix(".html")
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(wrap_doc(title, body, depth=depth), encoding="utf-8")
        essay_n += 1
        index_items.append(
            f'<li><a href="{html.escape(html_rel, quote=True)}">{html.escape(title)}</a></li>'
        )
        link = f"dokja/{html_rel}"
        if rel.parts[0] == "2권":
            toc2.append((link, title))
        else:
            toc1.append((link, title))

    (essay_dest / "index.html").write_text(
        wrap_doc(
            "독자판 장별 목록",
            "<p>1권과 2권 장별 읽기입니다.</p>\n<ul>\n"
            + "\n".join(index_items)
            + "\n</ul>",
            depth=2,
        ),
        encoding="utf-8",
    )

    (docs / "dokja-1-toc.html").write_text(
        build_toc_html("독자판 1권 목차", toc1, depth=1), encoding="utf-8"
    )
    (docs / "dokja-2-toc.html").write_text(
        build_toc_html("독자판 2권 목차", toc2, depth=1), encoding="utf-8"
    )
    return essay_n


def main() -> None:
    essay_n = build_docs(INTRO / "docs")

    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)

    for p in INTRO.iterdir():
        if p.name.startswith(".") or p.name in {"serve.py", "실행.bat", "README.md"}:
            continue
        if p.name.startswith("_"):
            continue
        dest = OUT / p.name
        if p.is_file():
            shutil.copy2(p, dest)
        elif p.is_dir():
            shutil.copytree(p, dest)

    if not STATION.is_file():
        raise SystemExit(f"missing station: {STATION}")
    shutil.copy2(STATION, OUT / "station.html")
    (OUT / ".nojekyll").write_text("", encoding="utf-8")

    need = [
        "index.html",
        "styles.css",
        "site.js",
        "station.html",
        "about.html",
        "text-dokja.html",
        "docs/dokja-1.html",
        "docs/dokja-2.html",
        "docs/dokja/index.html",
        "docs/dokja-1-toc.html",
    ]
    missing = [n for n in need if not (OUT / n).is_file()]
    if missing:
        raise SystemExit(f"build missing: {missing}")

    # sanity: no unpublished relative .md / researcher paths left as local hrefs
    bad: list[str] = []
    for p in (OUT / "docs").rglob("*.html"):
        for m in re.finditer(r'href="([^"]+)"', p.read_text(encoding="utf-8")):
            h = m.group(1)
            if h.startswith(("http://", "https://", "#", "mailto:")):
                continue
            if ".md" in h or ("공명_소설_분석" in h and "독자판" not in h):
                bad.append(f"{p.relative_to(OUT)} → {h}")
    if bad:
        raise SystemExit("broken doc links remain:\n" + "\n".join(bad[:30]))

    print(
        f"Built {OUT} (+ {INTRO / 'docs'}) "
        f"({sum(1 for _ in OUT.rglob('*'))} paths, "
        f"{len(DOC_PAGES)} volumes, {essay_n} essays)"
    )


if __name__ == "__main__":
    main()
