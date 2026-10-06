# -*- coding: utf-8 -*-
"""Assemble researcher-edition combined volumes from arc files."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "04_발표"
SRC = DOCS / "공명_소설_분석"

VOL1_ORDER = [
    ("file", "1권_00_서론과_용어론.md"),
    ("dir", "1권_01_빛없는아래"),
    ("dir", "1권_02_선별의도시"),
    ("dir", "1권_03_바깥"),
    ("file", "1권_맺음.md"),
]

VOL2_ORDER = [
    ("dir", "2권_04_별들의전장"),
    ("dir", "2권_05_무대"),
    ("dir", "2권_06_종말의문장"),
    ("dir", "2권_07_여명"),
    ("file", "2권_맺음_미확정.md"),
]

HEADER1 = """# 공명 소설 분석 연구자판 1권 (합본)

원작 1~3부 제목 아크 밀착 독해.
원작: 나리아타 『엑스칼리버 뽑습니다』. 결말 방향은 본편 07부·장편설계 §7에 맞춤(별≠가치, 「나는 별」 닫힘 폐기).
장별 파일: 공명_소설_분석/. 독자판: 공명_소설_분석_독자판/.
목차만: 공명_소설_분석_1권.md. 2권 합본: 공명_소설_분석_2권_합본.md.

금지: 별=가치 · 기억=존재 · 승리=구원 · 나는 진리 · 나는 별

---

"""

HEADER2 = """# 공명 소설 분석 연구자판 2권 (합본)

원작 4~7부 제목 아크 밀착 독해.
결말 방향 확정(별≠가치, 「나는 별」 닫힘 폐기). 14·엑칼=잔여·도구.
장별: 공명_소설_분석/. 목차: 공명_소설_분석_2권.md.
1권 합본: 공명_소설_분석_1권_합본.md.
파일명 `2권_맺음_미확정.md`는 논의 시기 흔적으로 유지. 본문은 확정 후 갱신.

금지: 별=가치 · 기억=존재 · 승리=구원 · 나는 진리 · 나는 별

---

"""


def strip_body(text: str) -> str:
    return text.replace("\r\n", "\n").strip() + "\n"


def iter_parts(order: list[tuple[str, str]]) -> list[Path]:
    paths: list[Path] = []
    for kind, name in order:
        p = SRC / name
        if kind == "file":
            if not p.is_file():
                raise SystemExit(f"missing: {p}")
            paths.append(p)
        else:
            if not p.is_dir():
                raise SystemExit(f"missing dir: {p}")
            for f in sorted(p.glob("*.md")):
                if f.name.upper() == "README.MD" or f.name.startswith("_"):
                    continue
                paths.append(f)
    return paths


def assemble(order: list[tuple[str, str]], header: str) -> str:
    parts = [header]
    for path in iter_parts(order):
        parts.append(strip_body(path.read_text(encoding="utf-8")))
        parts.append("\n---\n\n")
    return "".join(parts).rstrip() + "\n"


def main() -> None:
    out1 = DOCS / "공명_소설_분석_1권_합본.md"
    out2 = DOCS / "공명_소설_분석_2권_합본.md"
    out1.write_text(assemble(VOL1_ORDER, HEADER1), encoding="utf-8")
    out2.write_text(assemble(VOL2_ORDER, HEADER2), encoding="utf-8")
    print(f"Wrote {out1.relative_to(ROOT)} ({out1.stat().st_size} bytes)")
    print(f"Wrote {out2.relative_to(ROOT)} ({out2.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
