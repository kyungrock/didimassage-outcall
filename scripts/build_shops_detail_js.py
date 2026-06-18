#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""shops.json에서 출장마사지 상세 데이터 추출 + 카드 데이터와 매핑"""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
IMPORTANT = ROOT / "중요한정보"
OUT_JS = ROOT / "js" / "shops-outcall-detail.js"


def load_shops_json():
    text = (IMPORTANT / "shops.json").read_text(encoding="utf-8")
    if text.startswith("window"):
        text = text.split("=", 1)[1].strip().rstrip(";")
    return json.loads(text)["shops"]


def load_card_data():
    text = (IMPORTANT / "shop-card-data-outcall.js").read_text(encoding="utf-8")
    # crude eval via regex for id, name, file
    blocks = text.split("\n{")
    cards = []
    for block in blocks:
        if "type: '출장마사지'" not in block and "type: \"출장마사지\"" not in block:
            continue
        id_m = re.search(r"\bid:\s*(\d+)", block)
        name_m = re.search(r"\bname:\s*'([^']+)'", block)
        file_m = re.search(r"\bfile:\s*'([^']+)'", block)
        if id_m and name_m:
            cards.append(
                {
                    "cardId": int(id_m.group(1)),
                    "name": name_m.group(1),
                    "file": file_m.group(1) if file_m else "",
                }
            )
    return cards


def normalize_image(url: str) -> str:
    if not url:
        return url
    if url.startswith("https://msg1000.com/images/"):
        return "images/" + url.rsplit("/", 1)[-1]
    return url


def main():
    shops = [s for s in load_shops_json() if s.get("type") == "출장마사지"]
    for shop in shops:
        if "image" in shop:
            shop["image"] = normalize_image(shop["image"])
    cards = load_card_data()

    by_name = {s["name"]: s for s in shops}
    by_file = {}
    for c in cards:
        if c["file"]:
            key = c["file"].replace(".html", "")
            by_file[key] = c

    index = []
    for card in cards:
        detail = by_name.get(card["name"])
        entry = {
            "cardId": card["cardId"],
            "file": card["file"],
            "name": card["name"],
            "detail": detail,
        }
        index.append(entry)

    payload = {
        "shops": shops,
        "index": index,
    }

    OUT_JS.parent.mkdir(parents=True, exist_ok=True)
    OUT_JS.write_text(
        "window.shopsOutcallDetail = "
        + json.dumps(payload, ensure_ascii=False, indent=2)
        + ";\n",
        encoding="utf-8",
    )

    matched = sum(1 for e in index if e["detail"])
    print(f"Outcall shops in shops.json: {len(shops)}")
    print(f"Card entries: {len(cards)}")
    print(f"Matched detail by name: {matched}/{len(cards)}")
    print(f"Written: {OUT_JS}")


if __name__ == "__main__":
    main()
