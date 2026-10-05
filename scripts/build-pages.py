# -*- coding: utf-8 -*-
"""Build static site for GitHub Pages → _site/"""
from __future__ import annotations
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INTRO = ROOT / "04_발표" / "공명_소개"
STATION = ROOT / "04_발표" / "공명스테이션_예시.html"
OUT = ROOT / "_site"

def main() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    # intro pages
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
    # station at ASCII path
    if not STATION.is_file():
        raise SystemExit(f"missing station: {STATION}")
    shutil.copy2(STATION, OUT / "station.html")
    # GitHub Pages: skip Jekyll
    (OUT / ".nojekyll").write_text("", encoding="utf-8")
    # sanity
    need = ["index.html", "styles.css", "site.js", "station.html", "about.html"]
    missing = [n for n in need if not (OUT / n).is_file()]
    if missing:
        raise SystemExit(f"build missing: {missing}")
    print(f"Built {OUT} ({sum(1 for _ in OUT.rglob('*'))} paths)")

if __name__ == "__main__":
    main()
