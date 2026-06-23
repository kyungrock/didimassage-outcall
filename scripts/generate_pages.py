#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""시·구별 출장마사지 HTML 페이지 생성기"""

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "data" / "regions.json"
COORDS_PATH = ROOT / "data" / "area_coords.json"
OUT_DIR = ROOT
NEARBY_LINK_LIMIT = 8

import sys

sys.path.insert(0, str(ROOT / "scripts"))
from shop_card_prerender import render_shop_cards_grid  # noqa: E402
from area_content import AreaContent, course_heading, get_area_content, why_bodies  # noqa: E402
from blog import write_blog_pages  # noqa: E402
from seo_meta import (  # noqa: E402
    head_json_ld_block,
    json_ld_breadcrumb,
    json_ld_item_list,
    json_ld_local_business,
    json_ld_website,
    og_head_tags,
    write_robots,
    write_sitemap,
)


def load_coords():
    with open(COORDS_PATH, encoding="utf-8") as f:
        return json.load(f)


def build_area_index(data: dict) -> dict:
    index = {}
    for metro in data["metros"]:
        for area in metro["areas"]:
            index[area["slug"]] = {
                "slug": area["slug"],
                "short": area.get("short", area["name"]),
                "metro_id": metro["id"],
            }
    for sub in data.get("pajuSubs", []):
        index[sub["slug"]] = {
            "slug": sub["slug"],
            "short": sub["name"],
            "metro_id": "gyeonggi",
        }
    return index


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(p1) * math.cos(p2) * math.sin(dlon / 2) ** 2
    )
    return 2 * r * math.asin(math.sqrt(a))


def nearby_area_links(
    area_index: dict,
    coords: dict,
    metro: dict,
    current_slug: str,
    limit: int = NEARBY_LINK_LIMIT,
) -> str:
    current = coords.get(current_slug)
    ranked: list[tuple[float, str, dict]] = []

    if current:
        clat, clon = current
        for slug, info in area_index.items():
            if slug == current_slug or slug not in coords:
                continue
            lat, lon = coords[slug]
            dist = haversine_km(clat, clon, lat, lon)
            ranked.append((dist, slug, info))
        ranked.sort(key=lambda item: (item[0], item[1]))
    else:
        siblings = [
            area_index[a["slug"]]
            for a in metro["areas"]
            if a["slug"] != current_slug and a["slug"] in area_index
        ]
        offset = sum(ord(c) for c in current_slug) % max(len(siblings), 1)
        rotated = siblings[offset:] + siblings[:offset]
        for info in rotated:
            ranked.append((0.0, info["slug"], info))

    links = []
    for _, slug, info in ranked[:limit]:
        links.append(
            f'<li><a href="{slug}.html">{info["short"]} 출장마사지 상세보기</a></li>'
        )
    return "\n        ".join(links)


def load_data():
    with open(DATA_PATH, encoding="utf-8") as f:
        return json.load(f)


def metro_admin_label(metro: dict) -> str:
    """행정구역 정식 명칭 (예: 서울 특별시, 경기도, 인천광역시)"""
    name = metro["name"]
    t = metro.get("type", "")
    if t == "특별시":
        return f"{name} 특별시"
    if t == "광역시":
        return f"{name}광역시"
    if t == "특별자치도":
        return f"{name}특별자치도"
    if t == "도":
        return f"{name}도"
    return name


def build_duplicate_shorts(metros: list) -> set[str]:
    """전국에서 short 이름이 겹치는 구·시 (중구, 서구 등)"""
    from collections import Counter

    counts: Counter[str] = Counter()
    for metro in metros:
        for area in metro["areas"]:
            counts[area.get("short", area["name"])] += 1
    return {short for short, count in counts.items() if count > 1}


def area_title_label(metro_name: str, short: str, dup_shorts: set[str]) -> str:
    """페이지 title용: 강남 / 서울 중구 (short 중복 시 지역 접두)"""
    if short in dup_shorts:
        return f"{metro_name} {short}"
    return short


def metro_page_title(metro_name: str, site_name: str) -> str:
    return f"{metro_name} 출장마사지｜시·구 전지역 24시 - {site_name}"


def area_page_title(
    metro_name: str, short: str, dup_shorts: set[str], site_name: str
) -> str:
    label = area_title_label(metro_name, short, dup_shorts)
    return f"{label} 출장마사지｜24시 후불 - {site_name}"


def schema_telephone(phone: str) -> str:
    if phone.startswith("0"):
        return "+82-" + phone[1:]
    return phone


def seo_schema_block(
    site: dict,
    *,
    canonical: str,
    region_label: str,
    page_region: str = "",
    page_district: str = "",
    item_list_name: str = "",
    local_desc: str = "",
    faq_ld: str | None = None,
    area_content: AreaContent | None = None,
    breadcrumb_ld: str | None = None,
) -> str:
    address = None
    if area_content:
        address = {
            "addressCountry": "KR",
            "addressRegion": region_label,
            "addressLocality": area_content.address_locality,
            "postalCode": area_content.postal_code,
        }
    payloads = [
        json_ld_website(site),
        json_ld_local_business(
            site,
            page_url=canonical,
            region_label=region_label,
            description=local_desc,
            address=address,
        ),
        json_ld_item_list(
            site,
            page_region=page_region,
            page_district=page_district,
            list_name=item_list_name,
        ),
    ]
    if breadcrumb_ld:
        payloads.append(breadcrumb_ld)
    if faq_ld:
        payloads.append(faq_ld)
    return head_json_ld_block(site, *payloads)


def breadcrumb_schema_for_area(
    site: dict, metro: dict, area: dict, *, is_sub: bool = False, parent_area: dict | None = None
) -> str:
    domain = site["domain"].rstrip("/")
    crumbs = [{"name": "홈", "url": f"{domain}/"}]
    if is_sub and parent_area:
        crumbs.append(
            {
                "name": parent_area["name"],
                "url": f"{domain}/{parent_area['slug']}.html",
            }
        )
        crumbs.append(
            {
                "name": area["name"],
                "url": f"{domain}/{area['slug']}.html",
            }
        )
    else:
        crumbs.append(
            {
                "name": metro["name"],
                "url": f"{domain}/{metro['id']}.html",
            }
        )
        crumbs.append(
            {
                "name": area.get("short", area["name"]),
                "url": f"{domain}/{area['slug']}.html",
            }
        )
    return json_ld_breadcrumb(crumbs)


def esc(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def pricing_tables(pricing: dict, prefix: str, slug: str = "") -> str:
    parts = []
    for key in ("A", "B", "C"):
        course = pricing[key]
        rows = "".join(
            f"<tr><td>{r[0]}</td><td>{r[1]}</td></tr>" for r in course["rows"]
        )
        heading = (
            course_heading(prefix, key, course["name"], slug)
            if slug
            else f"{prefix} {key} 코스 — {course['name']}"
        )
        parts.append(
            f"""
      <h3>{esc(heading)}</h3>
      <div class="table-wrap">
        <table>
          <thead><tr><th>시간</th><th>가격</th></tr></thead>
          <tbody>{rows}</tbody>
        </table>
      </div>
      <div class="hr"></div>"""
        )
    return "\n".join(parts)


def local_highlight_html(region_label: str, content: AreaContent) -> str:
    paras = "\n".join(
        f'      <p class="muted">{esc(p)}</p>' for p in content.highlights
    )
    return f"""
<section id="local">
  <div class="container">
    <h2>📍 {esc(region_label)} 지역 맞춤 출장 안내</h2>
    <div class="card">
{paras}
    </div>
  </div>
</section>"""


def why_section_html(
    region_label: str,
    dong_list: str = "",
    content: AreaContent | None = None,
    slug: str = "",
) -> str:
    dong_hint = dong_list.replace("·", ", ") if dong_list else region_label
    if content:
        titles = content.why_titles
        bodies = why_bodies(region_label, dong_list, len(titles), slug)
    else:
        titles = [
            f"1) {region_label} 호텔·자택에서 편하게 이용하는 출장마사지",
            "2) 늦은 밤·당일 일정에도 상담 가능",
            "3) 방문 후 결제하는 후불제",
            "4) 피로·컨디션에 맞춘 맞춤 코스",
        ]
        bodies = [
            f"{region_label} 호텔·펜션·자택·오피스텔로 관리사가 직접 방문합니다. 샵까지 이동할 필요 없이 편한 공간에서 케어를 받을 수 있습니다.",
            f"24시간 전화·카톡 상담으로 {region_label} 기준 빠른 배정이 가능합니다. 퇴근 후, 여행 중, 갑작스러운 피로가 쌓였을 때도 부담 없이 문의하세요.",
            "관리사 도착·코스 확인 후 결제하는 후불제로 운영됩니다. 현금·계좌이체·카드 등 결제 방법은 상담 시 안내해 드립니다.",
            f"건식·아로마·힐링(스웨디시) 등 원하시는 강도와 부위에 맞춰 코스를 안내합니다. {dong_hint} 등 {region_label} 전지역에서 이용하실 수 있습니다.",
        ]
    blocks = []
    for title, body in zip(titles, bodies):
        blocks.append(
            f"""
      <h3>{esc(title)}</h3>
      <p class="muted">{esc(body)}</p>"""
        )
    return f"""
<section id="why">
  <div class="container">
    <h2>📌 {esc(region_label)} 출장마사지가 필요한 순간</h2>
    <div class="card">
{"".join(blocks)}
    </div>
  </div>
</section>"""


def faq_schema_items(
    region_label: str, dong_list: str = "", content: AreaContent | None = None
) -> list:
    dong_hint = dong_list.replace("·", ", ") if dong_list else region_label
    local_q = (
        f"{region_label} 어느 동네·숙소까지 방문하나요?"
        if content
        else f"{region_label} 어디까지 방문 가능한가요?"
    )
    return [
        (
            f"{region_label} 출장마사지 예약 후 얼마나 기다리나요?",
            f"{region_label} 기준으로 상황에 따라 보통 20~40분 안에 배정·방문 일정을 안내해 드립니다. 급한 경우 전화·카톡으로 먼저 문의해 주세요.",
        ),
        (
            "결제는 언제 하나요? 선결제가 필요한가요?",
            "관리사 방문 후 코스를 확인하신 뒤 결제하는 후불제입니다. 이용 전 선결제 없이 예약하실 수 있으며, 현금·계좌이체·카드 등 결제 방법은 상담 시 안내드립니다.",
        ),
        (
            local_q,
            (
                f"{content.highlights[0]} {content.highlights[1] if len(content.highlights) > 1 else ''} 상세 주소·건물명은 예약 시 안내드립니다."
                if content and content.highlights
                else f"호텔·펜션·자택·오피스텔 등 머무시는 공간으로 방문합니다. {dong_hint} 등 {region_label} 전지역 상담 가능하며, 상세 주소는 예약 시 안내드립니다."
            ),
        ),
        (
            "어떤 코스를 선택할 수 있나요?",
            "건식·아로마·힐링(스웨디시) 등 피로 부위와 원하시는 강도에 맞춰 상담 후 코스를 추천해 드립니다. 시간·요금은 상단 가격표 또는 상담 시 확인하세요.",
        ),
        (
            "늦은 시간·당일 예약도 가능한가요?",
            f"24시간 전화·카톡 상담을 운영합니다. {region_label} 기준 당일·야간 예약 가능 여부를 상담 시 바로 안내해 드립니다.",
        ),
    ]


def faq_html(
    region_label: str, dong_list: str = "", content: AreaContent | None = None
) -> str:
    items = faq_schema_items(region_label, dong_list, content)
    blocks = []
    for q, a in items:
        blocks.append(
            f"""
      <h3>Q. {esc(q)}</h3>
      <p class="muted">A. {esc(a)}</p>"""
        )
    return "\n".join(blocks)


def faq_json_ld(
    region_label: str, dong_list: str = "", content: AreaContent | None = None
) -> str:
    items = faq_schema_items(region_label, dong_list, content)
    entities = []
    for q, a in items:
        entities.append(
            {
                "@type": "Question",
                "name": q,
                "acceptedAnswer": {"@type": "Answer", "text": a},
            }
        )
    return json.dumps(
        {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": entities},
        ensure_ascii=False,
        indent=2,
    )


SHOP_CSS = '<link rel="stylesheet" href="css/shop-cards.css">'
REGION_CSS = '<link rel="stylesheet" href="css/region-selector.css">'
SHOP_SCRIPTS = """
<script src="js/regions-data.js"></script>
<script src="js/shop-card-data-outcall.js"></script>
<script src="js/shop-cards.js"></script>
<script src="js/region-selector.js"></script>"""


def region_selector_html(metro_id: str = "", slug: str = "") -> str:
    return f"""
<div id="regionSelectorBar" class="region-selector-bar"
  data-metro-id="{esc(metro_id)}"
  data-slug="{esc(slug)}">
  <div class="container">
    <button type="button" id="regionCompactBtn" class="region-compact-btn" aria-expanded="false" aria-controls="regionPickerPanel">
      <span class="region-compact-icon" aria-hidden="true">📍</span>
      <span id="regionCompactText" class="region-compact-text">지역 · 구 선택</span>
      <span class="region-compact-change">변경</span>
    </button>
    <div id="regionPickerPanel" class="region-picker-panel">
      <div class="region-selector-inner">
        <span class="region-selector-title">📍 지역 · 구 선택</span>
        <div class="region-select-group">
          <label for="metroSelect">지역</label>
          <select id="metroSelect" aria-label="지역 선택"></select>
        </div>
        <div class="region-select-group">
          <label for="districtSelect">구/시</label>
          <select id="districtSelect" aria-label="구 시 선택" disabled></select>
        </div>
        <button type="button" id="regionSearchBtn" class="region-search-btn">업체 보기</button>
      </div>
    </div>
  </div>
</div>"""


def site_top_open() -> str:
    return '<div class="site-top">'


def site_top_close() -> str:
    return "</div>"


def write_regions_data_js(metros: list, paju_subs: list) -> None:
    payload = {"metros": []}
    for metro in metros:
        areas = [
            {"slug": a["slug"], "name": a["name"], "short": a["short"]}
            for a in metro["areas"]
        ]
        if metro["id"] == "gyeonggi":
            for sub in paju_subs:
                areas.append(
                    {
                        "slug": sub["slug"],
                        "name": "파주 " + sub["name"],
                        "short": sub["name"],
                    }
                )
        payload["metros"].append(
            {
                "id": metro["id"],
                "name": metro["name"],
                "type": metro["type"],
                "label": metro_admin_label(metro),
                "areas": areas,
            }
        )
    out = ROOT / "js" / "regions-data.js"
    out.write_text(
        "window.regionsData = "
        + json.dumps(payload, ensure_ascii=False, indent=2)
        + ";\n",
        encoding="utf-8",
    )


def shop_section_html(
    region_label: str,
    region: str,
    district: str,
    metro_id: str,
    slug: str = "",
    cards_title: str = "",
) -> str:
    cards_html, shop_count = render_shop_cards_grid(
        region, district, display_label=region_label if district else ""
    )
    count_text = f"{shop_count}개 업체"
    title = cards_title or f"💆 {esc(region_label)} 출장마사지 업체"
    return f"""
<section id="shops" class="shop-cards-section"
  data-region="{esc(region)}"
  data-district="{esc(district)}"
  data-region-label="{esc(region_label)}"
  data-metro="{esc(metro_id)}"
  data-slug="{esc(slug if slug else "")}">
  <div class="container">
    <div class="shop-cards-head">
      <h2 id="shopCardsTitle">{title}</h2>
      <span id="shopCardsCount" class="shop-cards-count">{count_text}</span>
    </div>
    <p class="muted">카드를 클릭하면 코스·가격·리뷰 등 상세 정보를 확인할 수 있습니다.</p>
    <div id="shopCardsGrid" class="shop-cards-grid" aria-live="polite">
{cards_html}
    </div>
  </div>
</section>"""


def render_area_page(
    site: dict,
    pricing: dict,
    metro: dict,
    area: dict,
    area_index: dict,
    coords: dict,
    dup_shorts: set[str],
    *,
    is_sub: bool = False,
    parent_area: dict | None = None,
) -> str:
    slug = area["slug"]
    short = area.get("short", area["name"])
    metro_name = metro["name"]
    dong_list = "·".join(area.get("dong", [])[:6])
    region_label = f"{metro_name} {short}"
    page_title = area_page_title(metro_name, short, dup_shorts, site["name"])
    h1 = f"{region_label} 출장마사지 24시간 후불"
    canonical = f"{site['domain']}/{slug}.html"
    map_query = f"{metro_name} {area['name']}"
    price_prefix = short
    meta_desc = f"{region_label} 출장마사지 24시간 운영. {dong_list} 등 전지역 방문. 후불제, 전문 테라피스트 배정."
    area_content = get_area_content(slug, metro, area, region_label, dong_list)
    if area_content.highlights:
        meta_desc = area_content.highlights[0][:120] + (
            "…" if len(area_content.highlights[0]) > 120 else ""
        )
    og_desc = meta_desc
    item_list_name = f"{region_label} 출장마사지 업체"
    breadcrumb_ld = breadcrumb_schema_for_area(
        site, metro, area, is_sub=is_sub, parent_area=parent_area
    )

    breadcrumb = f'<div class="breadcrumb"><a href="index.html">홈</a> › {esc(metro_name)} › {esc(area["name"])}</div>'
    if is_sub and parent_area:
        breadcrumb = (
            f'<div class="breadcrumb"><a href="index.html">홈</a> › '
            f'<a href="{parent_area["slug"]}.html">{esc(parent_area["name"])}</a> › '
            f'{esc(area["name"])}</div>'
        )

    sub_links_html = ""
    if area.get("subLinks"):
        subs = "\n        ".join(
            f'<li><a href="{s["href"]}">{esc(s["label"])}</a></li>' for s in area["subLinks"]
        )
        sub_links_html = f"""
      <ul class="region-list">
        {subs}
      </ul>"""

    sibling_html = nearby_area_links(area_index, coords, metro, slug)
    back_link = f'<li><a href="{metro["id"]}.html">{esc(metro_admin_label(metro))} 전체 보기</a></li>'

    return f"""<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(page_title)}</title>
  <meta name="description" content="{esc(meta_desc)}">
  <meta name="robots" content="index,follow,max-image-preview:large">
  <meta name="theme-color" content="#111111">
  <link rel="canonical" href="{canonical}">
  <link rel="preload" as="image" href="{site["heroImage"]}" fetchpriority="high">
{og_head_tags(site, page_title, og_desc, canonical)}
  <link rel="stylesheet" href="css/common.css">
  {SHOP_CSS}
  {REGION_CSS}
{seo_schema_block(site, canonical=canonical, region_label=region_label, page_region=metro_name, page_district=short, item_list_name=item_list_name, local_desc=meta_desc, faq_ld=faq_json_ld(region_label, dong_list, area_content), area_content=area_content, breadcrumb_ld=breadcrumb_ld)}
</head>
<body>
{site_top_open()}
<header>
  <div class="container">
    <div class="header-inner">
      <div>
        <div class="brand"><a href="index.html">{site["name"]}</a></div>
        <div class="sub">{region_label} 출장마사지 · 24시간 · 후불제 · 전지역 방문</div>
      </div>
      <div style="display:flex;gap:10px;align-items:center;flex-wrap:wrap;">
        <button class="toggle-btn" onclick="toggleMode()" aria-label="다크/라이트 모드 전환">🌙/☀</button>
        <a href="tel:{site["phoneTel"]}" class="cta">전화문의</a>
      </div>
    </div>
    <nav class="top-nav" aria-label="페이지 바로가기">
      <a href="#shops">업체</a>
      <a href="#price">가격</a>
      <a href="#local">지역안내</a>
      <a href="#why">장점</a>
      <a href="#area">지역</a>
      <a href="#faq">FAQ</a>
      <a href="#map">지도</a>
      <a href="#contact">상담</a>
    </nav>
  </div>
</header>
{region_selector_html(metro["id"], slug)}
{site_top_close()}
<main>
<section class="hero" aria-label="{esc(region_label)} 출장마사지">
  <img src="{site["heroImage"]}" alt="{esc(region_label)} 출장마사지" class="hero-bg" width="1200" height="800" loading="eager" fetchpriority="high" decoding="async">
  <div class="hero-content">
    <h1>{esc(h1)}</h1>
    <p>{dong_list} 등 {esc(region_label)} 전지역 · 자택/호텔/오피스텔 · 전화/카톡 즉시 상담</p>
    <a href="tel:{site["phoneTel"]}" class="cta-btn">지금 전화 상담하기</a>
    <div class="phone-display">📞 {site["phone"]}</div>
    <div class="badges">
      <span>24시간</span><span>후불제</span><span>전지역</span><span>즉시상담</span>
    </div>
  </div>
</section>
{shop_section_html(region_label, metro_name, short, metro["id"], slug)}
<section id="price">
  <div class="container">
    {breadcrumb}
    <h2>💆 {esc(region_label)} 출장마사지 코스별 가격</h2>
    <div class="card">
      <p class="muted">정확한 금액/가능 여부는 상담 시 안내됩니다.</p>
      {pricing_tables(pricing, price_prefix, slug)}
    </div>
  </div>
</section>
{local_highlight_html(region_label, area_content)}
{why_section_html(region_label, dong_list, area_content, slug)}
<section id="area">
  <div class="container">
    <h2>📍 {esc(region_label)} 출장마사지 가능 지역</h2>
    <div class="card">
      <p><strong>{esc(area["name"])} 전지역</strong> 방문 가능합니다. ({dong_list} 등)</p>
      {sub_links_html}
      <ul class="region-list">
        {back_link}
        {sibling_html}
        <li><a href="index.html">전국 출장마사지 메인으로</a></li>
      </ul>
    </div>
  </div>
</section>
<section id="faq">
  <div class="container">
    <h2>❓ {esc(region_label)} FAQ</h2>
    <div class="card">
      {faq_html(region_label, dong_list, area_content)}
    </div>
  </div>
</section>
<section id="map">
  <div class="container">
    <h2>🗺️ {esc(region_label)} 지도</h2>
    <div class="card" style="padding:0;overflow:hidden;">
      <div class="map-wrap">
        <iframe src="https://www.google.com/maps?q={esc(map_query)}&output=embed" loading="lazy" referrerpolicy="no-referrer-when-downgrade" allowfullscreen title="{esc(region_label)} 지도"></iframe>
      </div>
    </div>
  </div>
</section>
<section id="contact">
  <div class="container">
    <h2>📞 지금 바로 상담</h2>
    <div class="card">
      <p><strong>전화:</strong> <a href="tel:{site["phoneTel"]}" style="color:var(--accent);font-weight:950;text-decoration:none;">{site["phone"]}</a></p>
      <p><strong>카카오톡:</strong> <a href="{site["kakao"]}" style="color:var(--accent);font-weight:950;text-decoration:none;">오픈채팅 바로가기</a></p>
      <p class="muted">상담 시 "지역 + 코스/시간"을 알려주시면 더 빠르게 안내 가능합니다.</p>
    </div>
  </div>
</section>
</main>
<footer>
  <div class="container">
    <div class="foot-strong">{site["name"]}</div>
    <div>{esc(region_label)} 출장마사지 · {site["phone"]} · 24시간</div>
    <div class="muted" style="margin-top:8px;">© 2026 {esc(site_host(site))}</div>
  </div>
</footer>
<div class="floating-btns">
  <a href="tel:{site["phoneTel"]}" class="call-btn" aria-label="전화">전화</a>
  <a href="{site["kakao"]}" class="kakao-btn" aria-label="카카오톡"><img src="{site["kakaoIcon"]}" alt="카카오톡" loading="lazy"></a>
</div>
<script src="js/common.js"></script>
{SHOP_SCRIPTS}
</body>
</html>
"""


def render_metro_hub(site: dict, metro: dict) -> str:
    label = metro_admin_label(metro)
    metro_name = metro["name"]
    canonical = f"{site['domain']}/{metro['id']}.html"
    page_title = metro_page_title(metro_name, site["name"])
    meta_desc = f"{metro_name} 출장마사지. {len(metro['areas'])}개 지역 전지역 방문, 24시간 후불제."
    return f"""<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(page_title)}</title>
  <meta name="description" content="{esc(meta_desc)}">
  <meta name="robots" content="index,follow,max-image-preview:large">
  <link rel="canonical" href="{canonical}">
  <link rel="preload" as="image" href="{site["heroImage"]}" fetchpriority="high">
{og_head_tags(site, page_title, meta_desc, canonical)}
  <link rel="stylesheet" href="css/common.css">
  {SHOP_CSS}
  {REGION_CSS}
{seo_schema_block(site, canonical=canonical, region_label=f"{metro_name} 출장마사지", page_region=metro["name"], item_list_name=f"{metro_name} 출장마사지 업체", local_desc=meta_desc)}
</head>
<body>
{site_top_open()}
<header>
  <div class="container">
    <div class="header-inner">
      <div>
        <div class="brand"><a href="index.html">{site["name"]}</a></div>
        <div class="sub">{esc(label)} · 시·구별 안내</div>
      </div>
      <div style="display:flex;gap:10px;align-items:center;flex-wrap:wrap;">
        <button class="toggle-btn" onclick="toggleMode()" aria-label="다크/라이트">🌙/☀</button>
        <a href="tel:{site["phoneTel"]}" class="cta">전화문의</a>
      </div>
    </div>
  </div>
</header>
{region_selector_html(metro["id"], "")}
{site_top_close()}
<main>
<section class="hero">
  <img src="{site["heroImage"]}" alt="{esc(label)}" class="hero-bg" width="1200" height="800" loading="eager" fetchpriority="high">
  <div class="hero-content">
    <h1>{esc(label)} · 시·구 전지역 24시간</h1>
    <p>{esc(label)} 전 지역 · 후불제 · 전문 테라피스트</p>
    <a href="tel:{site["phoneTel"]}" class="cta-btn">지금 전화 상담</a>
    <div class="phone-display">📞 {site["phone"]}</div>
  </div>
</section>
{shop_section_html(metro["name"], metro["name"], "", metro["id"], "", cards_title=f"💆 {esc(label)} 업체")}
</main>
<footer>
  <div class="container">
    <div class="foot-strong">{site["name"]}</div>
    <div>{esc(label)} · {site["phone"]} · 24시간</div>
    <div class="muted" style="margin-top:8px;">© 2026 {esc(site_host(site))}</div>
  </div>
</footer>
<div class="floating-btns">
  <a href="tel:{site["phoneTel"]}" class="call-btn">전화</a>
  <a href="{site["kakao"]}" class="kakao-btn"><img src="{site["kakaoIcon"]}" alt="카카오톡"></a>
</div>
<script src="js/common.js"></script>
{SHOP_SCRIPTS}
</body>
</html>
"""


def render_index(site: dict, metros: list) -> str:
    canonical = f"{site['domain']}/"
    page_title = f"전국 출장마사지｜시·구별 24시 후불 - {site['name']}"
    meta_desc = "서울·경기·인천·부산·대구·대전·광주·울산 시·구별 출장마사지. 24시간 후불제, 전지역 방문, 전화/카톡 즉시 상담."
    return f"""<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(page_title)}</title>
  <meta name="description" content="{esc(meta_desc)}">
  <meta name="robots" content="index,follow,max-image-preview:large">
  <link rel="canonical" href="{canonical}">
  <link rel="preload" as="image" href="{site["heroImage"]}" fetchpriority="high">
{og_head_tags(site, page_title, meta_desc, canonical)}
  <link rel="stylesheet" href="css/common.css">
  {SHOP_CSS}
  {REGION_CSS}
{seo_schema_block(site, canonical=canonical, region_label="전국", page_region="", item_list_name="전국 출장마사지 업체", local_desc=meta_desc)}
</head>
<body>
{site_top_open()}
<header>
  <div class="container">
    <div class="header-inner">
      <div>
        <div class="brand">{site["name"]}</div>
        <div class="sub">전국 출장마사지 · 시·구별 안내 · 24시간 · 후불제</div>
      </div>
      <div style="display:flex;gap:10px;align-items:center;flex-wrap:wrap;">
        <button class="toggle-btn" onclick="toggleMode()" aria-label="다크/라이트">🌙/☀</button>
        <a href="tel:{site["phoneTel"]}" class="cta">전화문의</a>
      </div>
    </div>
  </div>
</header>
{region_selector_html("", "")}
{site_top_close()}
<main>
<section class="hero">
  <img src="{site["heroImage"]}" alt="전국 출장마사지" class="hero-bg" width="1200" height="800" loading="eager" fetchpriority="high">
  <div class="hero-content">
    <h1>전국 출장마사지 · 시·구별 24시간 후불</h1>
    <p>서울·경기·인천·부산 등 전국 시·구 방문 · 자택/호텔/오피스텔 · 전문 테라피스트</p>
    <a href="tel:{site["phoneTel"]}" class="cta-btn">지금 전화 상담하기</a>
    <div class="phone-display">📞 {site["phone"]}</div>
    <div class="badges">
      <span>24시간</span><span>후불제</span><span>전국</span><span>즉시상담</span>
    </div>
  </div>
</section>
{shop_section_html("전국", "", "", "", "")}
<section id="blog-link">
  <div class="container">
    <h2>📝 출장마사지 블로그</h2>
    <div class="card">
      <p>마사지 이용 가이드, 코스 비교, 예약 팁 등 유용한 정보를 블로그에서 확인하세요.</p>
      <p style="margin-top:12px;"><a href="blog.html" class="cta-btn" style="display:inline-block;text-decoration:none;">블로그 보기</a>
      <a href="blog-write.html" style="margin-left:10px;color:var(--accent);font-weight:700;">글 작성</a></p>
    </div>
  </div>
</section>
<section id="contact">
  <div class="container">
    <h2>📞 지금 바로 상담</h2>
    <div class="card">
      <p><strong>전화:</strong> <a href="tel:{site["phoneTel"]}" style="color:var(--accent);font-weight:950;text-decoration:none;">{site["phone"]}</a></p>
      <p><strong>카카오톡:</strong> <a href="{site["kakao"]}" style="color:var(--accent);font-weight:950;text-decoration:none;">오픈채팅 바로가기</a></p>
    </div>
  </div>
</section>
</main>
<footer>
  <div class="container">
    <div class="foot-strong">{site["name"]}</div>
    <div>전국 출장마사지 · {site["phone"]} · 24시간</div>
    <div class="muted" style="margin-top:8px;">© 2026 {esc(site_host(site))}</div>
  </div>
</footer>
<div class="floating-btns">
  <a href="tel:{site["phoneTel"]}" class="call-btn">전화</a>
  <a href="{site["kakao"]}" class="kakao-btn"><img src="{site["kakaoIcon"]}" alt="카카오톡"></a>
</div>
<script src="js/common.js"></script>
{SHOP_SCRIPTS}
</body>
</html>
"""


def site_host(site: dict) -> str:
    domain = site.get("domain", "https://example.com")
    return domain.replace("https://", "").replace("http://", "").rstrip("/")


def render_shop_detail(site: dict) -> str:
    domain = site["domain"].rstrip("/")
    host = site_host(site)
    tel = site["phoneTel"]
    name = site["name"]
    img = domain + site["heroImage"]
    return f"""<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>출장마사지 업체 상세 | {esc(name)}</title>
  <meta name="description" content="출장마사지 업체 상세 정보, 코스별 가격, 리뷰">
  <meta name="robots" content="index,follow,max-image-preview:large">
  <link rel="canonical" href="{domain}/shop-detail.html">
{og_head_tags(site, f"출장마사지 업체 상세 | {name}", "출장마사지 업체 상세 정보, 코스별 가격, 리뷰", f"{domain}/shop-detail.html")}
  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "WebSite",
    "name": "{name}",
    "url": "{domain}/",
    "inLanguage": "ko-KR"
  }}
  </script>
  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "LocalBusiness",
    "name": "{name}",
    "url": "{domain}/shop-detail.html",
    "telephone": "{schema_telephone(site["phone"])}",
    "image": "{img}",
    "priceRange": "₩₩",
    "areaServed": "전국",
    "address": {{
      "@type": "PostalAddress",
      "addressCountry": "KR"
    }},
    "openingHours": "Mo-Su 00:00-23:59"
  }}
  </script>
  <link rel="stylesheet" href="css/common.css">
  <link rel="stylesheet" href="css/shop-cards.css">
  <link rel="stylesheet" href="css/shop-detail.css">
  <style>.hidden{{display:none!important}}</style>
</head>
<body>
<header>
  <div class="container">
    <div class="header-inner">
      <div>
        <div class="brand"><a href="index.html">{esc(name)}</a></div>
        <div class="sub">출장마사지 업체 상세</div>
      </div>
      <div style="display:flex;gap:10px;align-items:center;">
        <button class="toggle-btn" onclick="toggleMode()" aria-label="다크/라이트">🌙/☀</button>
      </div>
    </div>
  </div>
</header>

<main id="shopDetailRoot">
  <section class="shop-detail-hero">
    <img id="shopHeroImage" src="{site["heroImage"]}" alt="업체 이미지" width="1200" height="420" loading="eager">
    <span class="shop-card-badge">출장마사지</span>
  </section>

  <section>
    <div class="container">
      <div class="card">
        <div class="shop-detail-header">
          <h1 class="shop-detail-name" id="shopName">업체명</h1>
          <div class="shop-detail-district" id="shopDistrict">지역</div>
          <div class="shop-detail-rating">
            <span class="shop-detail-stars" id="shopStars">★★★★★</span>
            <span id="shopRatingText">4.9</span>
          </div>
        </div>
        <p id="shopDescription"></p>

        <div class="shop-info-grid">
          <div class="shop-info-item">
            <span class="shop-info-label">주소</span>
            <span class="shop-info-value" id="shopAddress">-</span>
            <span class="shop-info-value muted" id="shopDetailAddress"></span>
          </div>
          <div class="shop-info-item">
            <span class="shop-info-label">전화</span>
            <span class="shop-info-value" id="shopPhone">-</span>
          </div>
          <div class="shop-info-item">
            <span class="shop-info-label">운영시간</span>
            <span class="shop-info-value" id="shopHours">-</span>
          </div>
          <div class="shop-info-item">
            <span class="shop-info-label">최저가</span>
            <span class="shop-info-value" id="shopPrice">-</span>
          </div>
        </div>

        <div class="shop-detail-cta">
          <a id="shopCallBtn" class="btn-call" href="tel:{tel}">전화 상담</a>
          <a id="shopBackBtn" class="btn-back" href="index.html">← 목록으로</a>
        </div>
      </div>
    </div>
  </section>

  <section>
    <div class="container">
      <h2>코스별 가격</h2>
      <div class="card" id="shopCourses"></div>
    </div>
  </section>

  <section>
    <div class="container">
      <h2>특징</h2>
      <div class="card">
        <div class="feature-tags" id="shopFeatures"></div>
      </div>
    </div>
  </section>

  <section>
    <div class="container">
      <h2>관리사 안내</h2>
      <div class="card">
        <p class="staff-info" id="shopStaff"></p>
      </div>
    </div>
  </section>

  <section>
    <div class="container">
      <h2>리뷰</h2>
      <div class="card" id="shopReviews"></div>
    </div>
  </section>
</main>

<footer>
  <div class="container">
    <div class="foot-strong">{esc(name)}</div>
    <div class="muted" style="margin-top:8px;">© 2026 {esc(host)}</div>
  </div>
</footer>

<script src="js/shop-card-data-outcall.js"></script>
<script src="js/shops-outcall-detail.js"></script>
<script src="js/common.js"></script>
<script src="js/shop-detail.js"></script>
</body>
</html>
"""


def main():
    data = load_data()
    coords = load_coords()
    area_index = build_area_index(data)
    site = data["site"]
    pricing = data["pricing"]
    dup_shorts = build_duplicate_shorts(data["metros"])
    count = 0

    for metro in data["metros"]:
        (OUT_DIR / f"{metro['id']}.html").write_text(
            render_metro_hub(site, metro), encoding="utf-8"
        )
        count += 1

        for area in metro["areas"]:
            (OUT_DIR / f"{area['slug']}.html").write_text(
                render_area_page(
                    site, pricing, metro, area, area_index, coords, dup_shorts
                ),
                encoding="utf-8",
            )
            count += 1

    paju_parent = next(
        a
        for m in data["metros"]
        if m["id"] == "gyeonggi"
        for a in m["areas"]
        if a["slug"] == "gyeonggi-paju"
    )
    gyeonggi_metro = next(m for m in data["metros"] if m["id"] == "gyeonggi")

    for sub in data.get("pajuSubs", []):
        area = {
            "slug": sub["slug"],
            "name": sub["name"],
            "short": sub["name"],
            "dong": [sub["name"]],
        }
        (OUT_DIR / f"{sub['slug']}.html").write_text(
            render_area_page(
                site,
                pricing,
                gyeonggi_metro,
                area,
                area_index,
                coords,
                dup_shorts,
                is_sub=True,
                parent_area=paju_parent,
            ),
            encoding="utf-8",
        )
        count += 1

    (OUT_DIR / "index.html").write_text(
        render_index(site, data["metros"]), encoding="utf-8"
    )
    count += 1

    (OUT_DIR / "shop-detail.html").write_text(
        render_shop_detail(site), encoding="utf-8"
    )
    count += 1

    write_regions_data_js(data["metros"], data.get("pajuSubs", []))

    blog_count = write_blog_pages(OUT_DIR, site)
    count += blog_count

    write_sitemap(OUT_DIR, site["domain"], data["metros"], data.get("pajuSubs", []))
    write_robots(OUT_DIR, site["domain"])

    print(f"Generated {count} HTML files in {OUT_DIR}")
    print(f"Generated blog.html + {blog_count - 1} blog posts")
    print("Generated sitemap.xml, robots.txt")


if __name__ == "__main__":
    main()
