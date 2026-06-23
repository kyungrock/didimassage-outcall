#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""마사지 블로그(게시판) HTML 생성"""

from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
POSTS_PATH = ROOT / "data" / "blog-posts.json"

import sys

sys.path.insert(0, str(ROOT / "scripts"))
from seo_meta import (  # noqa: E402
    esc_attr,
    head_json_ld_block,
    json_ld_breadcrumb,
    json_ld_website,
    og_head_tags,
)


def esc(s: str) -> str:
    return (
        (s or "")
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def site_host(site: dict) -> str:
    return site["domain"].replace("https://", "").replace("http://", "").rstrip("/")


def load_blog_posts() -> list[dict]:
    if not POSTS_PATH.exists():
        return []
    data = json.loads(POSTS_PATH.read_text(encoding="utf-8"))
    posts = [p for p in data.get("posts", []) if p.get("published", True)]
    posts.sort(key=lambda p: p.get("date", ""), reverse=True)
    return posts


def load_all_posts_raw() -> list[dict]:
    if not POSTS_PATH.exists():
        return []
    data = json.loads(POSTS_PATH.read_text(encoding="utf-8"))
    return data.get("posts", [])


def save_posts(posts: list[dict]) -> None:
    POSTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    POSTS_PATH.write_text(
        json.dumps({"posts": posts}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def slugify(text: str) -> str:
    s = (text or "").strip().lower()
    s = re.sub(r"[^\w\s-가-힣]", "", s, flags=re.UNICODE)
    s = re.sub(r"[\s_]+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s[:60] or "post"


def format_date_kr(d: str) -> str:
    if not d or len(d) < 10:
        return d or ""
    y, m, day = d[:10].split("-")
    return f"{y}년 {int(m)}월 {int(day)}일"


def markdown_to_html(text: str) -> str:
    """간단한 마크다운 → HTML (글쓰기 페이지에서 #, ##, * 목록 사용 시)"""
    lines = (text or "").replace("\r\n", "\n").split("\n")
    parts: list[str] = []
    in_ul = False

    def close_ul() -> None:
        nonlocal in_ul
        if in_ul:
            parts.append("</ul>")
            in_ul = False

    for line in lines:
        stripped = line.strip()
        if not stripped:
            close_ul()
            continue
        if stripped.startswith("### "):
            close_ul()
            parts.append(f"<h3>{esc(stripped[4:])}</h3>")
        elif stripped.startswith("## "):
            close_ul()
            parts.append(f"<h2>{esc(stripped[3:])}</h2>")
        elif stripped.startswith("# "):
            close_ul()
            parts.append(f"<h2>{esc(stripped[2:])}</h2>")
        elif stripped.startswith("* "):
            if not in_ul:
                parts.append("<ul>")
                in_ul = True
            parts.append(f"<li>{esc(stripped[2:])}</li>")
        else:
            close_ul()
            parts.append(f"<p>{esc(stripped)}</p>")

    close_ul()
    return "\n".join(parts)


def normalize_content(content: str) -> str:
    c = (content or "").strip()
    if not c:
        return ""
    if c.startswith("<"):
        return c
    return markdown_to_html(c)


def blog_header(site: dict, *, sub: str, depth: int = 0) -> str:
    prefix = "../" * depth
    return f"""<header>
  <div class="container">
    <div class="header-inner">
      <div>
        <div class="brand"><a href="{prefix}index.html">{esc(site["name"])}</a></div>
        <div class="sub">{esc(sub)}</div>
      </div>
      <div style="display:flex;gap:10px;align-items:center;flex-wrap:wrap;">
        <button class="toggle-btn" onclick="toggleMode()" aria-label="다크/라이트 모드 전환">🌙/☀</button>
        <a href="tel:{site["phoneTel"]}" class="cta">전화문의</a>
      </div>
    </div>
    <nav class="top-nav" aria-label="페이지 바로가기">
      <a href="{prefix}index.html">홈</a>
      <a href="{prefix}blog.html">블로그</a>
      <a href="{prefix}blog-write.html">글쓰기</a>
    </nav>
  </div>
</header>"""


def blog_footer(site: dict, depth: int = 0) -> str:
    prefix = "../" * depth
    return f"""<footer>
  <div class="container">
    <div class="foot-strong">{esc(site["name"])}</div>
    <div>출장마사지 정보 · {site["phone"]} · 24시간</div>
    <div class="muted" style="margin-top:8px;">© 2026 {esc(site_host(site))}</div>
    <div style="margin-top:10px;"><a href="{prefix}blog.html" style="color:var(--accent);">블로그 목록</a></div>
  </div>
</footer>
<div class="floating-btns">
  <a href="tel:{site["phoneTel"]}" class="call-btn" aria-label="전화">전화</a>
  <a href="{site["kakao"]}" class="kakao-btn" aria-label="카카오톡"><img src="{site["kakaoIcon"]}" alt="카카오톡" loading="lazy"></a>
</div>
<script src="{prefix}js/common.js"></script>"""


def post_card_html(post: dict, depth: int = 0) -> str:
    prefix = "../" * depth
    tags = post.get("tags") or []
    tag_html = "".join(f'<span class="blog-tag">{esc(t)}</span>' for t in tags[:5])
    img = post.get("image") or "/img/model-1.png"
    if img.startswith("/"):
        img = prefix + img.lstrip("/")
    return f"""<article class="blog-card">
  <a href="{prefix}blog/{esc(post["id"])}.html" class="blog-card-link">
    <div class="blog-card-image-wrap">
      <img src="{esc(img)}" alt="{esc(post.get("title", ""))}" loading="lazy" decoding="async">
    </div>
    <div class="blog-card-body">
      <time class="blog-date" datetime="{esc(post.get("date", ""))}">{esc(format_date_kr(post.get("date", "")))}</time>
      <h2 class="blog-card-title">{esc(post.get("title", ""))}</h2>
      <p class="blog-card-summary">{esc(post.get("summary", ""))}</p>
      <div class="blog-tags">{tag_html}</div>
    </div>
  </a>
</article>"""


def render_blog_list(site: dict, posts: list[dict]) -> str:
    canonical = f"{site['domain']}/blog.html"
    page_title = f"출장마사지 블로그｜마사지 정보·이용 가이드 - {site['name']}"
    meta_desc = "출장마사지 이용 가이드, 코스 비교, 예약 팁 등 마사지 관련 정보를 블로그 형식으로 안내합니다."
    cards = "\n".join(post_card_html(p) for p in posts) or (
        '<p class="muted blog-empty">아직 등록된 글이 없습니다. <a href="blog-write.html">첫 글 작성하기</a></p>'
    )
    breadcrumb_ld = json_ld_breadcrumb(
        [
            {"name": "홈", "url": site["domain"] + "/"},
            {"name": "블로그", "url": canonical},
        ],
    )
    schema = head_json_ld_block(
        json_ld_website(site),
        breadcrumb_ld,
    )
    return f"""<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(page_title)}</title>
  <meta name="description" content="{esc(meta_desc)}">
  <meta name="robots" content="index,follow,max-image-preview:large">
  <link rel="canonical" href="{canonical}">
{og_head_tags(site, page_title, meta_desc, canonical)}
  <link rel="stylesheet" href="css/common.css">
  <link rel="stylesheet" href="css/blog.css">
{schema}
</head>
<body>
{blog_header(site, sub="출장마사지 블로그 · 마사지 정보·가이드")}
<main>
<section class="blog-hero">
  <div class="container">
    <h1>출장마사지 블로그</h1>
    <p class="muted">마사지 이용 가이드, 코스 정보, 건강·힐링 팁을 정리합니다.</p>
    <a href="blog-write.html" class="cta blog-write-btn">✏️ 글 작성하기</a>
  </div>
</section>
<section class="blog-list-section">
  <div class="container">
    <div class="blog-grid">
      {cards}
    </div>
  </div>
</section>
</main>
{blog_footer(site)}
</body>
</html>
"""


def render_blog_post(site: dict, post: dict, all_posts: list[dict]) -> str:
    canonical = f"{site['domain']}/blog/{post['id']}.html"
    title = post.get("title", "")
    page_title = f"{title} - {site['name']}"
    meta_desc = post.get("summary", "")[:160]
    tags = post.get("tags") or []
    tag_html = "".join(f'<span class="blog-tag">{esc(t)}</span>' for t in tags)
    img = post.get("image") or site.get("heroImage", "/img/model-1.png")
    og_img = img if img.startswith("http") else site["domain"] + img
    breadcrumb_ld = json_ld_breadcrumb(
        [
            {"name": "홈", "url": site["domain"] + "/"},
            {"name": "블로그", "url": site["domain"] + "/blog.html"},
            {"name": title, "url": canonical},
        ],
    )
    article_ld = json.dumps(
        {
            "@context": "https://schema.org",
            "@type": "BlogPosting",
            "headline": title,
            "description": meta_desc,
            "datePublished": post.get("date", ""),
            "author": {"@type": "Person", "name": post.get("author", site["name"])},
            "publisher": {
                "@type": "Organization",
                "name": site["name"],
                "url": site["domain"] + "/",
            },
            "image": og_img,
            "mainEntityOfPage": canonical,
        },
        ensure_ascii=False,
        indent=2,
    )
    schema = head_json_ld_block(
        breadcrumb_ld,
        article_ld,
    )
    others = [p for p in all_posts if p["id"] != post["id"]][:3]
    related = ""
    if others:
        items = "\n".join(
            f'<li><a href="{esc(p["id"])}.html">{esc(p.get("title", ""))}</a></li>'
            for p in others
        )
        related = f"""<aside class="blog-related card">
      <h3>다른 글 보기</h3>
      <ul class="blog-related-list">{items}</ul>
    </aside>"""
    hero_img = img if not img.startswith("http") else img
    if hero_img.startswith("/"):
        hero_img = ".." + hero_img
    return f"""<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(page_title)}</title>
  <meta name="description" content="{esc(meta_desc)}">
  <meta name="robots" content="index,follow,max-image-preview:large">
  <link rel="canonical" href="{canonical}">
{og_head_tags(site, page_title, meta_desc, canonical, image=og_img, og_type="article")}
  <link rel="stylesheet" href="../css/common.css">
  <link rel="stylesheet" href="../css/blog.css">
{schema}
</head>
<body>
{blog_header(site, sub="출장마사지 블로그", depth=1)}
<main>
<article class="blog-article">
  <div class="container blog-article-inner">
    <nav class="blog-breadcrumb" aria-label="breadcrumb">
      <a href="../index.html">홈</a> › <a href="../blog.html">블로그</a>
    </nav>
    <header class="blog-article-header">
      <time datetime="{esc(post.get("date", ""))}">{esc(format_date_kr(post.get("date", "")))}</time>
      <h1>{esc(title)}</h1>
      <div class="blog-tags">{tag_html}</div>
      <p class="blog-author muted">작성: {esc(post.get("author", site["name"]))}</p>
    </header>
    <img class="blog-article-image" src="{esc(hero_img)}" alt="{esc(title)}" loading="eager" decoding="async">
    <div class="blog-content card">
      {normalize_content(post.get("content", ""))}
    </div>
    {related}
    <div class="blog-cta card">
      <h3>출장마사지 상담·예약</h3>
      <p>전국 시·구별 24시간 후불 출장마사지 · 전화/카톡 즉시 상담</p>
      <div class="blog-cta-btns">
        <a href="tel:{site["phoneTel"]}" class="cta">📞 {site["phone"]}</a>
        <a href="{site["kakao"]}" class="cta-btn">카카오톡 상담</a>
      </div>
    </div>
    <p><a href="../blog.html" class="blog-back">← 블로그 목록으로</a></p>
  </div>
</article>
</main>
{blog_footer(site, depth=1)}
</body>
</html>
"""


def blog_sitemap_urls() -> list[tuple[str, str, str]]:
    posts = load_blog_posts()
    urls: list[tuple[str, str, str]] = [("blog.html", "weekly", "0.8")]
    for post in posts:
        urls.append((f"blog/{post['id']}.html", "monthly", "0.7"))
    return urls


def write_blog_pages(out_dir: Path, site: dict) -> int:
    posts = load_blog_posts()
    (out_dir / "blog.html").write_text(
        render_blog_list(site, posts), encoding="utf-8"
    )
    blog_dir = out_dir / "blog"
    blog_dir.mkdir(exist_ok=True)
    count = 1
    for post in posts:
        (blog_dir / f"{post['id']}.html").write_text(
            render_blog_post(site, post, posts), encoding="utf-8"
        )
        count += 1
    return count


def merge_draft(draft_path: Path) -> dict:
    draft = json.loads(draft_path.read_text(encoding="utf-8"))
    if "posts" in draft:
        new_posts = draft["posts"]
    elif "id" in draft:
        new_posts = [draft]
    else:
        raise ValueError("draft JSON must be a post object or {posts: [...]}")

    posts = load_all_posts_raw()
    by_id = {p["id"]: i for i, p in enumerate(posts)}
    added, updated = 0, 0
    for p in new_posts:
        if not p.get("id"):
            p["id"] = slugify(p.get("title", "post")) + "-" + date.today().strftime("%Y%m%d")
        if not p.get("date"):
            p["date"] = date.today().isoformat()
        p.setdefault("published", True)
        p.setdefault("author", "힐링 출장마사지")
        if p.get("content") and not str(p["content"]).strip().startswith("<"):
            p["content"] = normalize_content(p["content"])
        if p["id"] in by_id:
            posts[by_id[p["id"]]] = p
            updated += 1
        else:
            posts.append(p)
            added += 1
    posts.sort(key=lambda x: x.get("date", ""), reverse=True)
    save_posts(posts)
    return {"added": added, "updated": updated, "total": len(posts)}
