import json
import csv

INTENTS_FILE = "../data/intents/intents.json"
TEST_RESULT_FILE = "../logs/test_results.csv"
OUT_FILE = "../logs/eval_result.json"

# โหลด intents.json เพื่อสร้าง mapping response -> tag
with open(INTENTS_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

# สร้าง dict {response_sentence: tag}
response_to_tag = {}
for intent in data["intents"]:
    tag = intent["tag"]
    for resp in intent.get("responses", []):
        sentence = resp.get("sentence")
        if sentence:
            response_to_tag[sentence] = tag

# ประเมินผลจาก test_results.csv
total_test = 0
total_tag = 0

with open(TEST_RESULT_FILE, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        total_test += 1
        tag = row["tag"].strip()
        response = row["response"].strip()
        
        # เช็ค response ตรงกับ tag ใน intents.json
        correct_tag = response_to_tag.get(response)
        if correct_tag == tag:
            total_tag += 1

accuracy = total_tag / total_test if total_test else 0

# สร้าง eval_result.json
eval_result = {
    "total_test": total_test,
    "total_tag": total_tag,
    "accuracy": round(accuracy, 4)  # ปัด 4 ตำแหน่ง
}

with open(OUT_FILE, "w", encoding="utf-8") as f:
    json.dump(eval_result, f, ensure_ascii=False, indent=4)

print(f"สรุปผลการทดสอบบันทึกไว้ที่ {OUT_FILE}")
print(eval_result)
