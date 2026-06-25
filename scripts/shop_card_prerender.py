#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""업체 카드 HTML 사전 렌더 (페이지 소스·SEO용)"""

from __future__ import annotations

import json
import re
import subprocess
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CARD_JS = ROOT / "js" / "shop-card-data-outcall.js"


def esc(s: str) -> str:
    return (
        (s or "")
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def load_shop_cards() -> list[dict]:
    text = CARD_JS.read_text(encoding="utf-8")
    code = f"""
const fs = require('fs');
const vm = require('vm');
const ctx = {{ window: {{}} }};
vm.runInNewContext(fs.readFileSync({json.dumps(str(CARD_JS))}, 'utf8'), ctx);
process.stdout.write(JSON.stringify(ctx.window.outcallShopCardData));
"""
    try:
        result = subprocess.run(
            ["node", "-e", code],
            capture_output=True,
            text=True,
            check=True,
            encoding="utf-8",
        )
        return json.loads(result.stdout)
    except (subprocess.CalledProcessError, FileNotFoundError, json.JSONDecodeError):
        return _load_shop_cards_regex(text)


def _load_shop_cards_regex(text: str) -> list[dict]:
    cards = []
    for block in text.split("\n{"):
        if "type:" not in block:
            continue
        if "출장마사지" not in block and "힐링샵" not in block:
            continue
        card: dict = {}
        for key, pattern in [
            ("id", r"\bid:\s*(\d+)"),
            ("name", r"\bname:\s*'([^']+)'"),
            ("type", r"\btype:\s*'([^']+)'"),
            ("region", r"\bregion:\s*'([^']+)'"),
            ("district", r"\bdistrict:\s*'([^']*)'"),
            ("dong", r"\bdong:\s*'([^']*)'"),
            ("image", r"\bimage:\s*'([^']+)'"),
            ("alt", r"\balt:\s*'([^']*)'"),
            ("rating", r"\brating:\s*([\d.]+)"),
            ("price", r"\bprice:\s*'([^']+)'"),
            ("greeting", r"\bgreeting:\s*'([^']*)'"),
            ("file", r"\bfile:\s*'([^']*)'"),
        ]:
            m = re.search(pattern, block)
            if m:
                card[key] = m.group(1)
        if "id" in card and "name" in card:
            if "rating" in card:
                card["rating"] = float(card["rating"])
            cards.append(card)
    return cards


def normalize_area_text(value: str) -> str:
    value = (value or "").strip()
    value = re.sub(r"특별자치도|특별시|광역시", "", value)
    chars = []
    for ch in value:
        cat = unicodedata.category(ch)
        if cat[0] in ("L", "N"):
            chars.append(ch)
    value = "".join(chars)
    return re.sub(r"(시|구|군|읍|면|동|도)$", "", value)


def split_composite(value: str) -> list[str]:
    return [p.strip() for p in re.split(r"[,·/]", value or "") if p.strip()]


def region_tokens_match(shop_region: str, page_region: str) -> bool:
    page_norm = normalize_area_text(page_region)
    if not page_norm:
        return True
    pieces = split_composite(shop_region)
    if not pieces:
        return False
    for piece in pieces:
        shop_norm = normalize_area_text(piece)
        if not shop_norm:
            continue
        if (
            shop_norm == page_norm
            or shop_norm in page_norm
            or page_norm in shop_norm
        ):
            return True
    return False


def district_tokens_match(shop_district: str, page_district: str) -> bool:
    page_norm = normalize_area_text(page_district)
    if not page_norm:
        return True
    pieces = split_composite(shop_district)
    if not pieces:
        return False
    for piece in pieces:
        if "전지역" in piece:
            continue
        piece_norm = normalize_area_text(piece)
        if not piece_norm:
            continue
        if (
            piece_norm == page_norm
            or page_norm in piece_norm
            or piece_norm in page_norm
        ):
            return True
    return False


def district_serves_page(shop: dict, page_region: str, page_district: str) -> bool:
    if not page_district:
        return True
    shop_district = shop.get("district", "") or ""
    if district_tokens_match(shop_district, page_district):
        return True
    if "전지역" in shop_district and region_tokens_match(
        shop.get("region", ""), page_region
    ):
        return True
    if not shop_district.strip() and region_tokens_match(
        shop.get("region", ""), page_region
    ):
        return True
    return False


CAPITAL_REGIONS = ("서울", "경기", "인천")


def is_capital_shop(shop: dict) -> bool:
    region = shop.get("region", "") or ""
    return any(region_tokens_match(region, name) for name in CAPITAL_REGIONS)


def filter_shops(
    cards: list[dict], page_region: str, page_district: str = "", *, capital_only: bool = False
) -> list[dict]:
    if capital_only:
        filtered = [
            shop
            for shop in cards
            if (not shop.get("type") or shop.get("type") == "출장마사지")
            and is_capital_shop(shop)
        ]
        return dedupe_shops(filtered)
    filtered = [
        shop
        for shop in cards
        if (not shop.get("type") or shop.get("type") == "출장마사지")
        and region_tokens_match(shop.get("region", ""), page_region)
        and district_serves_page(shop, page_region, page_district)
    ]
    if not filtered and not page_region:
        filtered = [
            shop
            for shop in cards
            if not shop.get("type") or shop.get("type") == "출장마사지"
        ]
    return dedupe_shops(filtered)


def dedupe_shops(shops: list[dict]) -> list[dict]:
    seen: dict[str, dict] = {}
    for shop in shops:
        key = str(shop.get("id") or shop.get("name"))
        if key not in seen:
            seen[key] = shop
    return list(seen.values())


def resolve_image(src: str) -> str:
    if not src:
        return "images/placeholder-shop.jpg"
    if re.match(r"^https?://msg1000\.com/images/", src, re.I):
        src = re.sub(r"^https?://msg1000\.com/", "", src, flags=re.I)
    if src.startswith("http"):
        return src
    if src.startswith("/images/"):
        return src[1:]
    if src.startswith("images/"):
        return src
    return src.lstrip("/")


def render_stars(rating) -> str:
    r = round(float(rating or 0))
    return "★" * min(5, r) + "☆" * max(0, 5 - r)


def build_detail_url(shop: dict) -> str:
    params = f"id={shop.get('id', '')}"
    if shop.get("file"):
        params += f"&file={shop['file']}"
    return f"shop-detail.html?{params}"


def format_shop_location(shop: dict, display_label: str = "") -> str:
    shop_district = shop.get("district", "") or ""
    if display_label and (
        "전지역" in shop_district or not shop_district.strip()
    ):
        return f"{display_label} 출장 가능"

    def clean_part(value: str) -> str:
        parts = [p.strip() for p in (value or "").split("·")]
        return " · ".join(p for p in parts if p and p not in ("불가", "관리"))

    region = clean_part(shop.get("region") or "")
    district = clean_part(shop_district)
    dong = clean_part(shop.get("dong") or "")
    location = region
    if district:
        location += f" · {district}"
    if dong:
        location += f" · {dong}"
    return location


def card_image_alt(shop: dict, display_label: str = "") -> str:
    name = shop.get("name", "")
    price = shop.get("price") or "상담"
    if display_label:
        prefix = display_label
    else:
        region = shop.get("region", "전국") or "전국"
        prefix = region.split(",")[0].split("·")[0].strip()
    return f"{prefix} 출장마사지 {name} - 24시간 후불, {price}"


def parse_price_min(price_str: str) -> int:
    raw = (price_str or "").split("~")[0]
    digits = re.sub(r"[^\d]", "", raw)
    return int(digits) if digits else 999999


def render_shop_card_html(shop: dict, display_label: str = "") -> str:
    name = shop.get("name", "")
    href = esc(build_detail_url(shop))
    img = esc(resolve_image(shop.get("image", "")))
    alt = esc(card_image_alt(shop, display_label))
    rating = shop.get("rating", "-")
    stars = render_stars(rating)
    price = esc(shop.get("price") or "상담")
    price_min = parse_price_min(shop.get("price") or "")
    location = esc(format_shop_location(shop, display_label))

    greeting_html = ""
    if shop.get("greeting"):
        greeting_html = (
            f'\n      <p class="shop-card-greeting">{esc(shop["greeting"])}</p>'
        )

    tags_html = ""
    services = (shop.get("services") or [])[:3]
    if services:
        tag_items = "".join(
            f'<span class="shop-card-tag">{esc(s)}</span>' for s in services
        )
        tags_html = f'\n      <div class="shop-card-tags">{tag_items}</div>'

    return f"""    <a class="shop-card" href="{href}" aria-label="{esc(name)} 상세보기" data-price-min="{price_min}">
      <div class="shop-card-image-wrap">
        <img class="shop-card-image" src="{img}" alt="{alt}" loading="lazy" decoding="async">
        <span class="shop-card-badge">출장마사지</span>
      </div>
      <div class="shop-card-body">
        <h3 class="shop-card-name">{esc(name)}</h3>
        <div class="shop-card-meta">
          <span class="shop-card-rating">{stars} {rating}</span>
          <span class="shop-card-price">{price}</span>
        </div>
        <p class="shop-card-location">{location}</p>{greeting_html}{tags_html}
      </div>
    </a>"""


def render_shop_cards_grid(
    page_region: str,
    page_district: str = "",
    display_label: str = "",
    *,
    capital_only: bool = False,
) -> tuple[str, int]:
    cards = load_shop_cards()
    shops = filter_shops(
        cards, page_region, page_district, capital_only=capital_only
    )
    if not shops:
        label = display_label or page_district or page_region or "전국"
        return (
            f'    <div class="shop-cards-empty">현재 선택 지역({esc(label)})에 등록된 출장마사지 업체가 없습니다.</div>',
            0,
        )
    html = "\n".join(
        render_shop_card_html(shop, display_label) for shop in shops
    )
    return html, len(shops)
