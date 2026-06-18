#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""msg1000.com 이미지 URL → 로컬 images/ 경로로 교체"""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
IMAGES = ROOT / "images"

FILES = [
    ROOT / "중요한정보" / "shop-card-data-outcall.js",
    ROOT / "js" / "shop-card-data-outcall.js",
    ROOT / "js" / "shops-outcall-detail.js",
    ROOT / "중요한정보" / "shops-outcall-matched.json",
]


def local_image_names():
    return {f.name for f in IMAGES.iterdir() if f.is_file()}


def replace_in_text(text: str) -> tuple[str, int]:
    count = 0

    def sub_url(m):
        nonlocal count
        count += 1
        filename = m.group(1)
        return f"images/{filename}"

    text = re.sub(
        r"https?://msg1000\.com/images/([^'\"\\s]+)",
        sub_url,
        text,
    )
    return text, count


def replace_in_json_obj(obj, names: set) -> int:
    count = 0
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == "image" and isinstance(v, str):
                if v.startswith("https://msg1000.com/images/"):
                    fn = v.split("/")[-1]
                    obj[k] = f"images/{fn}"
                    count += 1
                elif v.startswith("http"):
                    fn = v.split("/")[-1]
                    if fn in names:
                        obj[k] = f"images/{fn}"
                        count += 1
            else:
                count += replace_in_json_obj(v, names)
    elif isinstance(obj, list):
        for item in obj:
            count += replace_in_json_obj(item, names)
    return count


def main():
    names = local_image_names()
    print(f"Local images: {len(names)}")

    for path in FILES:
        if not path.exists():
            print(f"skip (missing): {path}")
            continue

        text = path.read_text(encoding="utf-8")
        if path.suffix == ".json" or (
            path.suffix == ".js" and text.startswith("window")
        ):
            prefix = ""
            payload_text = text
            if text.startswith("window"):
                prefix, payload_text = text.split("=", 1)
                prefix = prefix.strip() + " = "
                payload_text = payload_text.strip().rstrip(";")
            data = json.loads(payload_text)
            n = replace_in_json_obj(data, names)
            if prefix:
                new_text = prefix + json.dumps(
                    data, ensure_ascii=False, indent=2
                ) + ";\n"
            else:
                new_text = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
            path.write_text(new_text, encoding="utf-8")
            print(f"{path.name}: {n} json image fields updated")
        else:
            new_text, n = replace_in_text(text)
            path.write_text(new_text, encoding="utf-8")
            print(f"{path.name}: {n} URL replacements")

    # verify card data filenames exist
    card = (ROOT / "js" / "shop-card-data-outcall.js").read_text(encoding="utf-8")
    refs = re.findall(r"image:\s*'images/([^']+)'", card)
    missing = [r for r in refs if r not in names]
    print(f"Card image refs: {len(refs)}, missing locally: {len(missing)}")
    if missing[:10]:
        print("Missing sample:", missing[:10])


if __name__ == "__main__":
    main()
