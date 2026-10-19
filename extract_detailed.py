import json
import re

with open("slides_ocr.json", "r", encoding="utf-8") as f:
    data = json.load(f)

sorted_items = sorted(data.items(), key=lambda x: x[1]['num'])

with open("detailed_slides.txt", "w", encoding="utf-8") as out:
    for fname, item in sorted_items:
        text = item.get("full_text", "")
        # Get first 300 characters or lines
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        out.write(f"=== {fname} ===\n")
        for l in lines[:6]:
            out.write(f"  {l}\n")
        out.write("\n")

print("Written detailed_slides.txt")
