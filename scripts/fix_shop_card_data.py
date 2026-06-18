#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
from pathlib import Path

path = Path(__file__).resolve().parent.parent / "중요한정보" / "shop-card-data-outcall.js"
text = path.read_text(encoding="utf-8")

text = re.sub(
    r"reviews: \[\s*\n\s*\n(\s+)author:",
    r"reviews: [\n\1{\n\1  author:",
    text,
)
text = re.sub(
    r"\n(\s+),\n(\s+)\],",
    r"\n\1},\n\2],",
    text,
)

# msg1000 → 로컬 images/
text, n = re.subn(
    r"https?://msg1000\.com/images/([^'\"\\s]+)",
    r"images/\1",
    text,
)
if n:
    print(f"replaced {n} msg1000 image URLs")

out_js = Path(__file__).resolve().parent.parent / "js" / "shop-card-data-outcall.js"
out_js.write_text(text, encoding="utf-8")
path.write_text(text, encoding="utf-8")
print("fixed and copied to", out_js)
