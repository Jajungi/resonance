# -*- coding: utf-8 -*-
"""Build static site for GitHub Pages → _site/"""
from __future__ import annotations

import html
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INTRO = ROOT / "04_발표" / "공명_소개"
STATION = ROOT / "04_발표" / "공명스테이션_예시.html"
DOCS_SRC = ROOT / "04_발표"
OUT = ROOT / "_site"

# (source relative to 04_발표, site path under docs/, page title)
DOC_PAGES = [
    ("공명_소설_독자_1권_합본.md", "dokja-1.html", "독자판 1권 합본"),
    ("공명_소설_독자_2권_합본.md", "dokja-2.html", "독자판 2권 합본"),
    ("공명_소설_독자_1권.md", "dokja-1-toc.html", "독자판 1권 목차"),
    ("공명_소설_독자_2권.md", "dokja-2-toc.html", "독자판 2권 목차"),
]


def md_inline(text: str) -> str:
    text = html.escape(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', text)
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
        close_lists()
        para = [line]
        i += 1
        while i < len(lines) and lines[i].strip() and not re.match(
            r"^(#{1,3}\s+|[-*]\s+|\d+\.\s+|```|---\s*$)", lines[i]
        ):
            para.append(lines[i])
            i += 1
        out.append("<p>" + md_inline(" ".join(p.strip() for p in para)) + "</p>")
    close_lists()
    return "\n".join(out)


def wrap_doc(title: str, body: str, *, depth: int = 1) -> str:
    root = "../" * depth
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
  <main id="main" class="page doc-main">
    <p class="eyebrow"><a href="{root}text-dokja.html">독자판</a> · 본문</p>
    <h1>{html.escape(title)}</h1>
    <article class="doc-body">
{body}
    </article>
    <nav class="page-next" aria-label="돌아가기">
      <a href="{root}text-dokja.html">← 독자판으로</a>
    </nav>
  </main>
  <script src="{root}site.js" defer></script>
</body>
</html>
"""


def copy_tree_md(src: Path, dest: Path) -> int:
    """Copy markdown tree; return file count."""
    n = 0
    if dest.exists():
        shutil.rmtree(dest)
    for p in src.rglob("*"):
        if not p.is_file():
            continue
        if p.suffix.lower() not in {".md", ".txt"}:
            continue
        rel = p.relative_to(src)
        target = dest / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, target)
        n += 1
    return n


def build_docs(docs: Path) -> int:
    """Write readable docs into docs/ (intro local + Pages). Return essay count."""
    if docs.exists():
        shutil.rmtree(docs)
    docs.mkdir(parents=True, exist_ok=True)
    for src_name, out_name, title in DOC_PAGES:
        src = DOCS_SRC / src_name
        if not src.is_file():
            raise SystemExit(f"missing doc: {src}")
        body = md_to_html_body(src.read_text(encoding="utf-8"))
        (docs / out_name).write_text(wrap_doc(title, body, depth=1), encoding="utf-8")
        shutil.copy2(src, docs / src.name)

    essay_n = 0
    essays = DOCS_SRC / "공명_소설_분석_독자판"
    if essays.is_dir():
        essay_dest = docs / "dokja"
        essay_n = copy_tree_md(essays, essay_dest)
        index_items: list[str] = []
        for md_path in sorted(essay_dest.rglob("*.md")):
            title = md_path.stem.replace("_", " ")
            html_rel = md_path.with_suffix(".html").relative_to(essay_dest).as_posix()
            depth = 2 + len(md_path.relative_to(essay_dest).parts) - 1
            body = md_to_html_body(md_path.read_text(encoding="utf-8"))
            md_path.with_suffix(".html").write_text(
                wrap_doc(title, body, depth=depth), encoding="utf-8"
            )
            index_items.append(
                f'<li><a href="{html.escape(html_rel)}">{html.escape(title)}</a></li>'
            )
        index_body = "<ul>\n" + "\n".join(index_items) + "\n</ul>"
        (essay_dest / "index.html").write_text(
            wrap_doc("독자판 장별 목록", index_body, depth=2), encoding="utf-8"
        )
    return essay_n


def main() -> None:
    # 로컬 serve / file 열기와 Pages가 같은 docs/ 를 쓰도록 소개 폴더에 먼저 생성
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
    ]
    missing = [n for n in need if not (OUT / n).is_file()]
    if missing:
        raise SystemExit(f"build missing: {missing}")

    print(
        f"Built {OUT} (+ {INTRO / 'docs'}) "
        f"({sum(1 for _ in OUT.rglob('*'))} paths, "
        f"{len(DOC_PAGES)} doc pages, {essay_n} dokja essays)"
    )


if __name__ == "__main__":
    main()
