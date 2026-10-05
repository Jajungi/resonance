# -*- coding: utf-8 -*-
"""계획안_보고서.md → 인쇄용 HTML."""
from pathlib import Path
import re
import html

BASE = Path(__file__).resolve().parent
md_path = BASE / "계획안_보고서.md"
out_path = BASE / "계획안_보고서.html"


def inline(s: str) -> str:
    s = html.escape(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<em>\1</em>", s)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', s)
    return s


def main() -> None:
    lines = md_path.read_text(encoding="utf-8").splitlines()
    body: list[str] = []
    in_table = False
    table_rows: list[str] = []
    in_ul = False
    in_bq = False

    def flush_ul() -> None:
        nonlocal in_ul
        if in_ul:
            body.append("</ul>")
            in_ul = False

    def flush_bq() -> None:
        nonlocal in_bq
        if in_bq:
            body.append("</blockquote>")
            in_bq = False

    def flush_table() -> None:
        nonlocal in_table, table_rows
        if not in_table:
            return
        body.append("<table>")
        row_i = 0
        for row in table_rows:
            cells = [c.strip() for c in row.strip("|").split("|")]
            if cells and all(re.match(r"^:?-+:?$", c.replace(" ", "")) for c in cells if c):
                continue
            tag = "th" if row_i == 0 else "td"
            body.append(
                "<tr>"
                + "".join(f"<{tag}>{inline(c)}</{tag}>" for c in cells)
                + "</tr>"
            )
            row_i += 1
        body.append("</table>")
        in_table = False
        table_rows = []

    for line in lines:
        if line.startswith("|") and "|" in line[1:]:
            flush_ul()
            flush_bq()
            if not in_table:
                in_table = True
                table_rows = []
            table_rows.append(line)
            continue
        flush_table()

        if line.startswith("> "):
            flush_ul()
            if not in_bq:
                body.append("<blockquote>")
                in_bq = True
            body.append("<p>" + inline(line[2:]) + "</p>")
            continue
        flush_bq()

        if re.match(r"^---+\s*$", line):
            flush_ul()
            body.append("<hr />")
            continue
        if line.startswith("# "):
            flush_ul()
            body.append(f"<h1>{inline(line[2:])}</h1>")
            continue
        if line.startswith("## "):
            flush_ul()
            body.append(f"<h2>{inline(line[3:])}</h2>")
            continue
        if line.startswith("### "):
            flush_ul()
            body.append(f"<h3>{inline(line[4:])}</h3>")
            continue
        if line.startswith("- "):
            if not in_ul:
                body.append("<ul>")
                in_ul = True
            body.append(f"<li>{inline(line[2:])}</li>")
            continue
        if line.strip() == "":
            flush_ul()
            continue
        flush_ul()
        body.append(f"<p>{inline(line)}</p>")

    flush_ul()
    flush_bq()
    flush_table()

    css = """
:root { --ink:#111; --line:#ccc; --accent:#0f766e; }
* { box-sizing:border-box; }
body { margin:0 auto; max-width:794px; padding:48px 56px 72px;
  font-family:"Malgun Gothic","Noto Sans KR",sans-serif; color:var(--ink);
  line-height:1.75; background:#fff; font-size:11pt; }
h1 { font-size:1.6rem; border-bottom:2px solid var(--ink); padding-bottom:.4rem; margin-top:0; }
h2 { font-size:1.25rem; color:var(--accent); margin-top:2rem;
  border-bottom:1px solid var(--line); padding-bottom:.25rem; }
h3 { font-size:1.05rem; margin-top:1.4rem; }
p { margin:.55rem 0; }
ul { margin:.4rem 0 .8rem; padding-left:1.3em; }
li { margin:.25rem 0; }
table { width:100%; border-collapse:collapse; margin:0.8rem 0 1.2rem; font-size:10.5pt; }
th, td { border:1px solid var(--line); padding:8px 10px; vertical-align:top; text-align:left; }
th { background:#f3f4f6; }
blockquote { margin:1rem 0; padding:.6rem 1rem; border-left:4px solid var(--accent); background:#f7faf9; }
code { font-size:.9em; background:#f3f4f6; padding:1px 4px; }
hr { border:none; border-top:1px solid var(--line); margin:1.8rem 0; }
a { color:var(--accent); }
.footer { margin-top:2.5rem; color:#666; font-size:9.5pt; }
@media print { body { padding:18mm; max-width:none; } }
"""

    doc = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>계획안 보고서 — 공명 스테이션</title>
<style>{css}</style>
</head>
<body>
{''.join(body)}
<p class="footer">브라우저에서 Ctrl+P → PDF</p>
</body>
</html>
"""
    out_path.write_text(doc, encoding="utf-8")
    print("wrote", out_path)


if __name__ == "__main__":
    main()
