import json
import csv
import subprocess
from datetime import datetime

TEST_FILE = "./test_patterns.csv"   # ไฟล์ CSV ที่เก็บ pattern
OUT_FILE = "../logs/test_results.csv"
ENDPOINT = "http://127.0.0.1:7001/ai"

# อ่าน test_patterns.csv
with open(TEST_FILE, "r", encoding="utf-8") as f:
    reader = csv.reader(f)
    header = next(reader)  # ข้ามหัวตาราง (tag,sentence)

    rows = list(reader)

# สร้าง/เขียนทับไฟล์ผลลัพธ์ใหม่
with open(OUT_FILE, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["tag", "sentence", "res_id", "response"])  # เพิ่ม header

    for tag, sentence in rows:
        for i in range(1):  
            curl_cmd = [
                "curl", "-s", "-X", "POST", ENDPOINT,
                "-H", "Content-Type: application/json",
                "-d", json.dumps({"sentence": sentence}, ensure_ascii=False)
            ]
            result = subprocess.run(curl_cmd, capture_output=True, text=True, encoding="utf-8")

            try:
                resp_json = json.loads(result.stdout)
                res_id = resp_json.get("res_id", "")
                response = resp_json.get("response", "")
            except json.JSONDecodeError:
                res_id, response = "", result.stdout.strip()

            writer.writerow([tag, sentence, res_id, response])

print(f"บันทึกผลการทดสอบไว้ที่ {OUT_FILE}")
