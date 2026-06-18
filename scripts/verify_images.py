#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
names = {f.name for f in (ROOT / "images").iterdir() if f.is_file()}

for rel in ["js/shop-card-data-outcall.js", "js/shops-outcall-detail.js"]:
    text = (ROOT / rel).read_text(encoding="utf-8")
    msg = text.count("msg1000")
    refs = re.findall(r"images/([^'\"\\s]+)", text)
    missing = sorted({r for r in refs if r not in names})
    print(f"{rel}: msg1000={msg}, image refs={len(set(refs))}, missing={len(missing)}")
    for m in missing[:15]:
        print(f"  - {m}")
