# -*- coding: utf-8 -*-
"""Assemble reader-edition combined volumes from chapter files."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "04_발표"
SRC = DOCS / "공명_소설_분석_독자판"

VOL1 = [
    "00_들어가는_말.md",
    "01_하늘이_없는_곳에서.md",
    "02_검이_사람을_선택할_때.md",
    "03_긍지를_지키는_사람.md",
    "04_죽은_사람이_나를_움직일_때.md",
    "05_이해하지_못한_채.md",
    "06_누구의_것인지_모르는_별자리.md",
    "07_자신을_잊은_사람.md",
    "08_아무도_기억하지_않는_나라.md",
    "09_닫지_않는_끝.md",
    "부록_용어_안내.md",
]

VOL2 = [
    "00_이어가는_말.md",
    "01_잊어버린_자와_기억하는_자.md",
    "02_이야기로_구원하려는_손.md",
    "03_무대에_선다는_것.md",
    "04_높이_날아오른_자리.md",
    "05_증명하러_온_망자들.md",
    "06_전설이_사람을_고를_때.md",
    "07_종말이_선고할_때.md",
    "08_여명에서_닫지_않는_손.md",
    "09_닫지_않는_끝.md",
    "부록_용어_안내.md",
]

HEADER1 = """# 공명 소설 독자판 1권 (합본)

장면이 먼저 오고, 질문이 생기고, 그다음에야 구분이 필요해진다.
원작: 나리아타 『엑스칼리버 뽑습니다』. 결말 방향은 본편 07부·2권 독자판에 맞춤.
장별 파일: 공명_소설_분석_독자판/. 연구자판: 공명_소설_분석/.
목차만: 공명_소설_독자_1권.md. 2권: 공명_소설_독자_2권_합본.md.
용어 이름은 본문보다 부록에서 모은다.

금지: 별=가치 · 기억=존재 · 승리=구원 · 나는 진리 · 나는 별

---

"""

HEADER2 = """# 공명 소설 독자판 2권 (합본)

장면 → 질문 → 필요할 때만 구분.
원작 4~7부. 결말 방향 확정(별≠가치, 「나는 별」 닫힘 폐기).
장별: 공명_소설_분석_독자판/2권/. 목차: 공명_소설_독자_2권.md.
1권 합본: 공명_소설_독자_1권_합본.md.
용어 이름은 본문보다 부록에서 모은다.

금지: 별=가치 · 기억=존재 · 승리=구원 · 나는 진리 · 나는 별

---

"""


def strip_body(text: str) -> str:
    return text.replace("\r\n", "\n").strip() + "\n"


def assemble(files: list[str], base: Path, header: str) -> str:
    parts = [header]
    for name in files:
        path = base / name
        if not path.is_file():
            raise SystemExit(f"missing chapter: {path}")
        parts.append(strip_body(path.read_text(encoding="utf-8")))
        parts.append("\n---\n\n")
    return "".join(parts).rstrip() + "\n"


def main() -> None:
    out1 = DOCS / "공명_소설_독자_1권_합본.md"
    out2 = DOCS / "공명_소설_독자_2권_합본.md"
    out1.write_text(assemble(VOL1, SRC, HEADER1), encoding="utf-8")
    out2.write_text(assemble(VOL2, SRC / "2권", HEADER2), encoding="utf-8")
    print(f"Wrote {out1.relative_to(ROOT)}")
    print(f"Wrote {out2.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
