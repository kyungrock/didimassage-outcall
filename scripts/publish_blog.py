#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""블로그 글 추가 후 HTML·sitemap 재생성"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from blog import merge_draft, write_blog_pages  # noqa: E402
from generate_pages import OUT_DIR, load_data  # noqa: E402
from seo_meta import write_robots, write_sitemap  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="블로그 글 게시 및 페이지 재생성")
    parser.add_argument(
        "--add",
        metavar="FILE",
        help="새 글 JSON 파일 병합 (단일 글 또는 {posts:[...]})",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="등록된 글 목록 출력",
    )
    args = parser.parse_args()

    if args.add:
        result = merge_draft(Path(args.add))
        print(
            f"병합 완료: 추가 {result['added']}건, 수정 {result['updated']}건, "
            f"총 {result['total']}건"
        )

    if args.list:
        from blog import load_all_posts_raw

        for p in load_all_posts_raw():
            status = "공개" if p.get("published", True) else "비공개"
            print(f"  [{status}] {p.get('date', '')}  {p.get('id')}  {p.get('title')}")
        return

    data = load_data()
    site = data["site"]
    n = write_blog_pages(OUT_DIR, site)
    write_sitemap(OUT_DIR, site["domain"], data["metros"], data.get("pajuSubs", []))
    write_robots(OUT_DIR, site["domain"])
    print(f"블로그 페이지 {n}개 생성 (blog.html + 글 {n - 1}개)")
    print("sitemap.xml, robots.txt 갱신 완료")
    print("\nGitHub에 올리려면:")
    print('  git add data/blog-posts.json blog.html blog/ css/blog.css')
    print('  git commit -m "블로그 글 업데이트"')
    print("  git push origin master")


if __name__ == "__main__":
    main()
