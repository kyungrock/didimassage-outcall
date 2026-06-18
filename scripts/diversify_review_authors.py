#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""리뷰 작성자 이름을 전부 서로 다르게 교체"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "중요한정보" / "shop-card-data-outcall.js"
OUT = ROOT / "js" / "shop-card-data-outcall.js"

# 61개 — 모두 다른 닉네임 (지역·직업·취향·일상 등 다양하게)
AUTHORS = [
    "제주여행객님",
    "호텔투숙러님",
    "늦은퇴근러님",
    "주말힐링님",
    "피곤한월요일님",
    "새벽귀가님",
    "오피스텔거주님",
    "강남출장러님",
    "분당직장인님",
    "인천출장족님",
    "마포힐링님",
    "송파거주민님",
    "여의도직장인님",
    "홍대파티족님",
    "건대족님",
    "수원출장님",
    "일산거주님",
    "평택출장러님",
    "부천직장인님",
    "안양힐링님",
    "광명거주님",
    "동탄출장님",
    "의정부러버님",
    "김포신혼님",
    "하남미사님",
    "용인직장인님",
    "성남판교님",
    "송도출장님",
    "부평거주님",
    "연수구민님",
    "해운대여행님",
    "서면직장인님",
    "부산출장족님",
    "대구수성님",
    "달서구민님",
    "대전둔산님",
    "유성연구원님",
    "광주상무님",
    "제주도민님",
    "서귀포여행님",
    "울산공단님",
    "원주출장님",
    "강릉여행객님",
    "청주직장인님",
    "충북출장러님",
    "전주출장님",
    "포항출장족님",
    "경주관광님",
    "창원거주님",
    "릴랙스킹님",
    "몸보신러님",
    "스트레스제로님",
    "마사지덕후님",
    "코스탐험가님",
    "후기남기는사람님",
    "단골예정님",
    "출장마니아님",
    "힐링필수님",
    "야근족님",
    "비즈니스출장님",
    "출근전힐링님",
]


def main():
    text = SRC.read_text(encoding="utf-8")
    matches = list(re.finditer(r"author:\s*'([^']*)'", text))
    if len(matches) > len(AUTHORS):
        raise SystemExit(
            f"작성자 풀 부족: 리뷰 {len(matches)}개, 이름 {len(AUTHORS)}개"
        )

    idx = 0

    def repl(m: re.Match) -> str:
        nonlocal idx
        name = AUTHORS[idx]
        idx += 1
        return f"{m.group(1)}author: '{name}'"

    new_text = re.sub(r"(\s*)author:\s*'[^']*'", repl, text)

    SRC.write_text(new_text, encoding="utf-8")
    OUT.write_text(new_text, encoding="utf-8")

    used = re.findall(r"author:\s*'([^']*)'", new_text)
    unique = len(set(used))
    print(f"updated {len(used)} review authors ({unique} unique)")
    if unique != len(used):
        dupes = [a for a in used if used.count(a) > 1]
        print("WARNING duplicates:", sorted(set(dupes)))


if __name__ == "__main__":
    main()
