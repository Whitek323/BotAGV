import json
import csv
import subprocess
from datetime import datetime

INTENTS_FILE = "../data/intents/intents.json"
OUT_FILE = "../logs/test_patterns.csv"
ENDPOINT = "http://127.0.0.1:7001/ai"

# โหลด intents.json
with open(INTENTS_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

# สร้าง/เขียนทับไฟล์ csv ใหม่
with open(OUT_FILE, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)

    for intent in data["intents"]:
        tag = intent["tag"]
        sentence = intent["patterns"][0]  # เอา pattern อันแรก

        for i in range(10):  # ส่ง 10 ครั้ง
            # ใช้ curl ส่ง request
            curl_cmd = [
                "curl", "-s", "-X", "POST", ENDPOINT,
                "-H", "Content-Type: application/json",
                "-d", json.dumps({"sentence": sentence}, ensure_ascii=False)
            ]
            result = subprocess.run(curl_cmd, capture_output=True, text=True, encoding="utf-8")

            # parse JSON response
            try:
                resp_json = json.loads(result.stdout)
                res_id = resp_json.get("res_id", "")
                response = resp_json.get("response", "")
            except json.JSONDecodeError:
                res_id, response = "", result.stdout.strip()
            
            writer.writerow(
                [
                    tag,
                    sentence,
                    res_id, 
                    response,
                    # datetime.now().strftime("%Y%m%d_%H%M%S")
                ]
            )

print(f"บันทึกผลการทดสอบไว้ที่ {OUT_FILE}")
