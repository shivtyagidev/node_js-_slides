import os
import json
import re
from PIL import Image
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

slides_dir = r"d:\node_js-_slides\react_slides"
output_file = r"d:\node_js-_slides\slides_ocr.json"

results = {}

# Sort slides numerically
files = [f for f in os.listdir(slides_dir) if f.startswith("slide_") and f.endswith(".jpg")]
def get_num(fname):
    m = re.search(r'slide_(\d+)', fname)
    return int(m.group(1)) if m else 0

files.sort(key=get_num)

print(f"Total slides found: {len(files)}")

for idx, fname in enumerate(files, 1):
    fpath = os.path.join(slides_dir, fname)
    try:
        img = Image.open(fpath)
        # Crop top 25% for title if needed, or get full text
        text = pytesseract.image_to_string(img)
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        title = lines[0] if lines else ""
        results[fname] = {
            "num": get_num(fname),
            "file": fname,
            "title": title,
            "preview_lines": lines[:5],
            "full_text": text.strip()
        }
        if idx % 10 == 0 or idx == len(files):
            print(f"Processed {idx}/{len(files)}: {fname} -> {title[:60]}")
    except Exception as e:
        print(f"Error on {fname}: {e}")
        results[fname] = {
            "num": get_num(fname),
            "file": fname,
            "error": str(e)
        }

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f"Saved OCR results to {output_file}")
