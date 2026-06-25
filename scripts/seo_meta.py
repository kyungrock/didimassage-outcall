#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""JSON-LD, Open Graph, sitemap, robots 생성"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from xml.sax.saxutils import escape as xml_escape

from shop_card_prerender import build_detail_url, dedupe_shops, filter_shops, load_shop_cards


def esc_attr(s: str) -> str:
    return (
        (s or "")
        .replace("&", "&amp;")
        .replace('"', "&quot;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def schema_telephone(phone: str) -> str:
    if phone.startswith("0"):
        return "+82-" + phone[1:]
    return phone


def abs_url(domain: str, path: str) -> str:
    path = path.lstrip("/")
    return f"{domain.rstrip('/')}/{path}"


def og_head_tags(
    site: dict,
    title: str,
    description: str,
    url: str,
    *,
    image: str | None = None,
    og_type: str = "website",
) -> str:
    img = image or site.get("heroImage", "/img/hero-brand.svg")
    if img.startswith("/"):
        img = site["domain"] + img
    name = esc_attr(site["name"])
    return f"""  <meta property="og:type" content="{og_type}">
  <meta property="og:site_name" content="{name}">
  <meta property="og:locale" content="ko_KR">
  <meta property="og:title" content="{esc_attr(title)}">
  <meta property="og:description" content="{esc_attr(description)}">
  <meta property="og:url" content="{esc_attr(url)}">
  <meta property="og:image" content="{esc_attr(img)}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{esc_attr(title)}">
  <meta name="twitter:description" content="{esc_attr(description)}">
  <meta name="twitter:image" content="{esc_attr(img)}">"""


def json_ld_website(site: dict) -> str:
    data = {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": site["name"],
        "url": site["domain"] + "/",
        "description": "전국 시·구별 출장마사지 업체 비교·지역 안내 플랫폼",
        "inLanguage": "ko-KR",
        "publisher": {
            "@type": "Organization",
            "name": site["name"],
            "url": site["domain"] + "/",
            "telephone": schema_telephone(site["phone"]),
        },
    }
    return json.dumps(data, ensure_ascii=False, indent=2)


def json_ld_local_business(
    site: dict,
    *,
    page_url: str,
    region_label: str = "전국",
    description: str = "",
    address: dict | None = None,
) -> str:
    addr = address or {
        "addressCountry": "KR",
        "addressRegion": region_label,
    }
    addr = {"@type": "PostalAddress", **addr}
    data = {
        "@context": "https://schema.org",
        "@type": "LocalBusiness",
        "name": site["name"],
        "url": page_url,
        "telephone": schema_telephone(site["phone"]),
        "image": site["domain"] + site.get("heroImage", "/img/hero-brand.svg"),
        "priceRange": "₩₩",
        "areaServed": region_label,
        "address": addr,
        "openingHours": "Mo-Su 00:00-23:59",
        "paymentAccepted": "Cash, Credit Card, Bank Transfer",
    }
    if description:
        data["description"] = description
    return json.dumps(data, ensure_ascii=False, indent=2)


def json_ld_item_list(
    site: dict,
    page_region: str = "",
    page_district: str = "",
    list_name: str = "",
    limit: int = 30,
) -> str:
    cards = load_shop_cards()
    shops = dedupe_shops(filter_shops(cards, page_region, page_district))
    elements = []
    for i, shop in enumerate(shops[:limit], start=1):
        detail = abs_url(site["domain"], build_detail_url(shop))
        item = {
            "@type": "ListItem",
            "position": i,
            "name": shop.get("name", ""),
            "url": detail,
        }
        if shop.get("image"):
            img = shop["image"]
            if img.startswith("images/"):
                img = "/" + img
            item["image"] = site["domain"] + img
        elements.append(item)
    if not elements:
        return ""
    if not list_name:
        parts = [p for p in (page_region, page_district) if p]
        list_name = (" ".join(parts) if parts else "전국") + " 출장마사지 업체"
    data = {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": list_name,
        "numberOfItems": len(elements),
        "itemListElement": elements,
    }
    return json.dumps(data, ensure_ascii=False, indent=2)


def json_ld_breadcrumb(crumbs: list[dict]) -> str:
    elements = []
    for i, crumb in enumerate(crumbs, start=1):
        item: dict = {
            "@type": "ListItem",
            "position": i,
            "name": crumb["name"],
        }
        if crumb.get("url"):
            item["item"] = crumb["url"]
        elements.append(item)
    data = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": elements,
    }
    return json.dumps(data, ensure_ascii=False, indent=2)


def head_json_ld_block(site: dict, *payloads: str) -> str:
    scripts = []
    for payload in payloads:
        if payload:
            scripts.append(
                f'  <script type="application/ld+json">\n{payload}\n  </script>'
            )
    return "\n".join(scripts)


def collect_sitemap_urls(metros: list, paju_subs: list) -> list[tuple[str, str, str]]:
    """(path, changefreq, priority)"""
    urls: list[tuple[str, str, str]] = [("index.html", "daily", "1.0")]
    for metro in metros:
        urls.append((f"{metro['id']}.html", "weekly", "0.9"))
        for area in metro["areas"]:
            urls.append((f"{area['slug']}.html", "weekly", "0.8"))
    for sub in paju_subs:
        urls.append((f"{sub['slug']}.html", "weekly", "0.8"))
    urls.append(("shop-detail.html", "monthly", "0.5"))
    cards = load_shop_cards()
    for shop in dedupe_shops(cards):
        if shop.get("id"):
            urls.append((build_detail_url(shop), "weekly", "0.7"))
    return urls


def write_sitemap(out_dir: Path, domain: str, metros: list, paju_subs: list) -> None:
    today = date.today().isoformat()
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    urls = list(collect_sitemap_urls(metros, paju_subs))
    try:
        from blog import blog_sitemap_urls

        urls.extend(blog_sitemap_urls())
    except ImportError:
        pass
    for path, changefreq, priority in urls:
        loc = abs_url(domain, path)
        lines.append("  <url>")
        lines.append(f"    <loc>{xml_escape(loc)}</loc>")
        lines.append(f"    <lastmod>{today}</lastmod>")
        lines.append(f"    <changefreq>{changefreq}</changefreq>")
        lines.append(f"    <priority>{priority}</priority>")
        lines.append("  </url>")
    lines.append("</urlset>")
    (out_dir / "sitemap.xml").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_robots(out_dir: Path, domain: str) -> None:
    content = f"""User-agent: *
Allow: /

Sitemap: {abs_url(domain, "sitemap.xml")}
"""
    (out_dir / "robots.txt").write_text(content, encoding="utf-8")
