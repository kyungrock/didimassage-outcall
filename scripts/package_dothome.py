#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""닷홈 FTP 업로드용 zip 패키지 생성"""

from __future__ import annotations

import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "dist" / "dothome-upload.zip"

INCLUDE_DIRS = ("css", "js", "images", "img", "data")
INCLUDE_FILES = (
    ".htaccess",
    "index.html",
    "shop-detail.html",
    "robots.txt",
    "sitemap.xml",
)


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as zf:
        for name in INCLUDE_FILES:
            path = ROOT / name
            if path.is_file():
                zf.write(path, name)

        for pattern in ("*.html",):
            for path in ROOT.glob(pattern):
                if path.name not in INCLUDE_FILES:
                    zf.write(path, path.name)

        for d in INCLUDE_DIRS:
            dir_path = ROOT / d
            if not dir_path.is_dir():
                continue
            for file in dir_path.rglob("*"):
                if file.is_file():
                    zf.write(file, file.relative_to(ROOT).as_posix())

    print(f"Created {OUT} ({OUT.stat().st_size // 1024} KB)")
    print("닷홈 FTP: public_html(또는 www)에 압축 해제 후 업로드")


if __name__ == "__main__":
    main()
