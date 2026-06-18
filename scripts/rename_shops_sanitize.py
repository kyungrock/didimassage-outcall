#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""성인성 업체명·이미지 파일 정리 및 js 동기화"""

from __future__ import annotations

import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "중요한정보" / "shop-card-data-outcall.js"
DST = ROOT / "js" / "shop-card-data-outcall.js"
IMG = ROOT / "images"

# (구 이름, 신 이름, 구 이미지 파일명, 신 이미지 파일명)
RENAMES: list[tuple[str, str, str, str]] = [
    ("T팬티 콜걸", "데일리 실크 홈타이", "T팬티콜걸.jpg", "데일리실크홈타이.jpg"),
    ("20대 탱글 출장", "20대 라인 힐링", "20대이쁘니탱글출장.jpg", "20대라인힐링.jpg"),
    ("도쿄핫", "도쿄 힐링 홈타이", "출장마사지_도쿄핫.jpg", "출장마사지_도쿄힐링홈타이.jpg"),
    ("원정녀", "글로벌 혼혈 힐링", "출장마사지_원정녀.jpg", "출장마사지_글로벌혼혈힐링.jpg"),
    ("비키니출장", "서머 비치 힐링", "출장마사지_비키니출장.jpg", "출장마사지_서머비치힐링.jpg"),
    ("쏘핫", "소프트 핫 스웨디시", "출장마사지_쏘핫.jpg", "출장마사지_소프트핫스웨디시.jpg"),
    (
        "24시 슴살화끈색녀",
        "24시 슬림라인 힐링",
        "출장마사지_슴살화끈색녀.jpg",
        "출장마사지_24시슬림라인힐링.jpg",
    ),
    (
        "BJ 발정난 색끼년 출장",
        "비제이 프리미엄 스웨디시",
        "출장마사지_BJ발정난색끼년출장.jpg",
        "출장마사지_비제이프리미엄스웨디시.jpg",
    ),
    (
        "란제리 구멍 출장",
        "란제리 힐링 스웨디시",
        "출장마사지_란제리구멍출장.jpg",
        "출장마사지_란제리힐링스웨디시.jpg",
    ),
    (
        "20대 우유빛홈타이",
        "20대 밀키톤 홈타이",
        "출장마사지_20대 우유빛홈타이.jpg",
        "출장마사지_20대밀키톤홈타이.jpg",
    ),
    ("촉촉홈타이", "모이스처 홈타이", "경남출장마사지_촉촉홈타이.jpg", "경남출장마사지_모이스처홈타이.jpg"),
    ("20대 여대생 한국출장", "20대 힐링 한국출장", "대구출장_여대생한국출장.jpg", "대구출장_20대힐링한국출장.jpg"),
]

# 구 이름이 본문에 남을 수 있는 추가 치환
TEXT_REPLACEMENTS: list[tuple[str, str]] = [
    ("T팬티 콜걸", "데일리 실크 홈타이"),
    ("T팬티", "데일리 실크"),
    ("20대 이쁘니 탱글 출장", "20대 라인 힐링"),
    ("20대 탱글 출장", "20대 라인 힐링"),
    ("이쁘니 탱글", "라인 힐링"),
    ("도쿄핫", "도쿄 힐링 홈타이"),
    ("도쿄 핫", "도쿄 힐링"),
    ("원정녀", "글로벌 혼혈 힐링"),
    ("비키니출장", "서머 비치 힐링"),
    ("비키니 VIP", "서머 비치 VIP"),
    ("비키니", "서머 비치"),
    ("쏘핫", "소프트 핫 스웨디시"),
    ("24시 슴살화끈색녀", "24시 슬림라인 힐링"),
    ("슴살화끈색녀", "슬림라인 힐링"),
    ("BJ 발정난 색끼년 출장", "비제이 프리미엄 스웨디시"),
    ("BJ 발정난", "비제이 프리미엄"),
    ("BJ성난", "비제이 프리미엄"),
    ("BJ 시원한", "비제이 시원한"),
    ("BJ성난", "비제이 프리미엄"),
    ("란제리구멍출장", "란제리 힐링 스웨디시"),
    ("란제리구멍", "란제리 힐링"),
    ("란제리 핫한", "란제리 힐링"),
    ("구멍언니", "힐링 언니"),
    ("구멍 전신", "프리미엄 전신"),
    ("특별한 구멍", "특별 프리미엄"),
    ("20대 우유빛홈타이", "20대 밀키톤 홈타이"),
    ("우유빛", "밀키톤"),
    ("촉촉홈타이", "모이스처 홈타이"),
    ("20대 여대생 한국출장", "20대 힐링 한국출장"),
    ("여대생", "힐링"),
    ("콜걸", "홈타이"),
    ("색끼년", "프리미엄"),
    ("발정난", "프리미엄"),
    ("화끈한 Y존", "화끈한 힐링"),
    ("Y존 스웨디시", "딥 힐링 스웨디시"),
]


EXTRA_FILES = [
    ROOT / "js" / "shops-outcall-detail.js",
]


def apply_text_replacements(text: str) -> str:
    for old_name, new_name, old_img, new_img in RENAMES:
        text = text.replace(old_name, new_name)
        text = text.replace(f"images/{old_img}", f"images/{new_img}")
    for old, new in TEXT_REPLACEMENTS:
        text = text.replace(old, new)
    return text


def main() -> None:
    text = SRC.read_text(encoding="utf-8")

    for old_name, new_name, old_img, new_img in RENAMES:
        old_path = IMG / old_img
        new_path = IMG / new_img
        if old_path.exists():
            if new_path.exists() and new_path != old_path:
                print(f"skip image (exists): {new_img}")
            else:
                shutil.move(str(old_path), str(new_path))
                print(f"image: {old_img} -> {new_img}")
        else:
            print(f"warn: missing image {old_img}")

        text = text.replace(f"name: '{old_name}'", f"name: '{new_name}'")
        text = text.replace(f"images/{old_img}", f"images/{new_img}")

    text = apply_text_replacements(text)

    # alt 필드: 지역+업체명 기본형 (페이지 렌더 시 display_label로 덮어씀)
    def alt_repl(m: re.Match) -> str:
        block = m.group(0)
        name_m = re.search(r"name:\s*'([^']+)'", block)
        region_m = re.search(r"region:\s*'([^']+)'", block)
        price_m = re.search(r"price:\s*'([^']+)'", block)
        if not name_m:
            return block
        name = name_m.group(1)
        region = (region_m.group(1) if region_m else "전국").split(",")[0].strip()
        price = price_m.group(1) if price_m else "상담"
        alt = f"{region} 출장마사지 {name} - 24시간 후불, {price}"
        if re.search(r"alt:\s*'", block):
            block = re.sub(r"alt:\s*'[^']*'", f"alt: '{alt}'", block)
        return block

    text = re.sub(r"\{\s*\n\s*id:\s*\d+.*?\n\s*\},", alt_repl, text, flags=re.S)

    SRC.write_text(text, encoding="utf-8")
    DST.write_text(text, encoding="utf-8")
    print(f"updated {SRC.name} and copied to {DST.name}")

    for extra in EXTRA_FILES:
        if not extra.exists():
            continue
        extra_text = apply_text_replacements(extra.read_text(encoding="utf-8"))
        extra.write_text(extra_text, encoding="utf-8")
        print(f"updated {extra.name}")


if __name__ == "__main__":
    main()
