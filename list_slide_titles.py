import json

with open("slides_ocr.json", "r", encoding="utf-8") as f:
    data = json.load(f)

sorted_items = sorted(data.items(), key=lambda x: x[1]['num'])

with open("slide_summary.txt", "w", encoding="utf-8") as out:
    for fname, item in sorted_items:
        lines = item.get("preview_lines", [])
        # find the line that starts with Q. or contains a question or topic
        q_line = ""
        for line in lines:
            if "Q." in line or "Question" in line or "?" in line:
                q_line = line
                break
        if not q_line and lines:
            q_line = lines[0]
        out.write(f"{fname:15} | {q_line}\n")

print("Written slide_summary.txt")
