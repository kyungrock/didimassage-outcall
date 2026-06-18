#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, re, pathlib

root = pathlib.Path(__file__).resolve().parent.parent / "중요한정보"
text = (root / "shops-outcall-matched.json").read_text(encoding="utf-8")
if text.startswith("window"):
    text = text.split("=", 1)[1].strip().rstrip(";")
data = json.loads(text)
print("outcall matched shops:", len(data["shops"]))
card_text = (root / "shop-card-data-outcall.js").read_text(encoding="utf-8")
card_names = re.findall(r"name: '([^']+)'", card_text)
shop_names = {s["name"] for s in data["shops"]}
matched = [n for n in set(card_names) if n in shop_names]
print("name matched:", len(matched), "/", len(set(card_names)))
print("unmatched:", [n for n in set(card_names) if n not in shop_names])
