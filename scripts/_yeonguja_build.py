# -*- coding: utf-8 -*-
"""Researcher-edition HTML builder helpers for build-pages.py."""
from __future__ import annotations

import html
from pathlib import Path
from typing import Callable


def build_yeonguja(
    docs: Path,
    *,
    docs_src: Path,
    chapter_title: Callable[[str], str],
    md_to_html_body: Callable[[str], tuple[str, list]],
    wrap_doc: Callable[..., str],
    build_toc_html: Callable[..., str],
) -> int:
    essays = docs_src / "공명_소설_분석"
    if not essays.is_dir():
        return 0

    dest = docs / "yeonguja"
    dest.mkdir(parents=True, exist_ok=True)
    index_items: list[str] = []
    toc1: list[tuple[str, str]] = []
    toc2: list[tuple[str, str]] = []
    n = 0

    for md_path in sorted(essays.rglob("*.md")):
        if md_path.name.upper() == "README.MD" or md_path.name.startswith("_"):
            continue
        if "_quotes" in md_path.parts:
            continue
        rel = md_path.relative_to(essays)
        html_rel = rel.with_suffix(".html").as_posix()
        title = chapter_title(md_path.stem)
        depth = 2 + len(rel.parts) - 1
        body, _headings = md_to_html_body(md_path.read_text(encoding="utf-8"))
        out_path = dest / rel.with_suffix(".html")
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(
            wrap_doc(title, body, depth=depth, section="yeonguja", toc_items=[]),
            encoding="utf-8",
        )
        n += 1
        index_items.append(
            f'<li><a href="{html.escape(html_rel, quote=True)}">{html.escape(title)}</a></li>'
        )
        link = f"yeonguja/{html_rel}"
        if rel.parts[0].startswith("2권"):
            toc2.append((link, title))
        else:
            toc1.append((link, title))

    for src_name, out_name, title in [
        ("공명_소설_분석_1권.md", "yeonguja-1-toc.html", "연구자판 1권 목차"),
        ("공명_소설_분석_2권.md", "yeonguja-2-toc.html", "연구자판 2권 목차"),
    ]:
        src = docs_src / src_name
        if src.is_file():
            body, _ = md_to_html_body(src.read_text(encoding="utf-8"))
            (docs / out_name).write_text(
                wrap_doc(title, body, depth=1, section="yeonguja", toc_items=[]),
                encoding="utf-8",
            )
        else:
            items = toc1 if "1권" in out_name else toc2
            (docs / out_name).write_text(
                build_toc_html(title, items, depth=1), encoding="utf-8"
            )

    index_body = (
        "<p>아크 밀착 독해입니다. 일반 읽기는 "
        '<a href="../dokja/">독자판</a>부터. 소설 본편은 '
        '<a href="../sosol/">소설 분권</a>에 있습니다.</p>\n'
        "<ul>\n" + "\n".join(index_items) + "\n</ul>"
    )
    (dest / "index.html").write_text(
        wrap_doc(
            "연구자판 장별 목록",
            index_body,
            depth=2,
            section="yeonguja",
            toc_items=[],
        ),
        encoding="utf-8",
    )
    return n
