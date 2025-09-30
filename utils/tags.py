import json
import csv

INTENTS_FILE = "../data/intents/intents.json"
OUT_FILE = "../logs/tags.csv"

# โหลด intents.json
with open(INTENTS_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

# สร้าง/เขียนทับไฟล์ csv ใหม่
with open(OUT_FILE, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["tag"])  # header

    for intent in data["intents"]:
        tag = intent.get("tag", "")
        if tag:  # กัน tag ว่าง
            writer.writerow([tag])

print(f"บันทึก tag ทั้งหมดไว้ที่ {OUT_FILE}")
