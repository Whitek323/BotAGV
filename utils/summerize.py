import json
import csv
from collections import Counter

INTENTS_FILE = "../data/intents/intents.json"
TEST_FILE = "../logs/test_patterns.csv"
OUT_FILE_SUMMARY = "../logs/eval_result.json"
OUT_FILE_PATTERN = "../logs/response_pattern.json"

# โหลด intents.json
with open(INTENTS_FILE, "r", encoding="utf-8") as f:
    intents = json.load(f)

# สร้าง mapping tag -> valid res_id
tag_to_responses = {intent["tag"]: [resp["res_id"] for resp in intent["responses"]]
                    for intent in intents["intents"]}

# อ่าน test_patterns.csv
results = []
with open(TEST_FILE, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        results.append({
            "tag": row["tag"],
            "res_id": str(row["res_id"]),
            "response": row["response"]
        })

total_test = len(results)
total_tag = len(set(r["tag"] for r in results))

# ตรวจสอบถูกผิดทั้งหมด
correct = sum(1 for r in results if r["res_id"] in tag_to_responses.get(r["tag"], []))
accuracy = correct / total_test if total_test > 0 else 0.0

# บันทึกไฟล์ eval_result.json
eval_result = {
    "total_test": total_test,
    "total_tag": total_tag,
    "accuracy": accuracy
}
with open(OUT_FILE_SUMMARY, "w", encoding="utf-8") as f:
    json.dump(eval_result, f, ensure_ascii=False, indent=4)

# นับ frequency + accuracy ต่อ tag และ respon_id
response_pattern = {}
for tag in sorted(set(r["tag"] for r in results)):
    counter = Counter(r["res_id"] for r in results if r["tag"] == tag)
    total_tag_test = sum(counter.values())
    correct_tag = sum(freq for rid, freq in counter.items() if rid in tag_to_responses.get(tag, []))

    details = []
    for rid, freq in counter.items():
        # accuracy ของแต่ละ respon_id = สัดส่วน freq/total_tag_test
        details.append({
            "respon_id": rid,
            "frequency": freq,
            "accuracy": round(freq / total_tag_test, 4)
        })

    tag_accuracy = correct_tag / total_tag_test if total_tag_test > 0 else 0.0
    response_pattern[tag] = {
        "accuracy": round(tag_accuracy, 4),
        "details": details
    }

# บันทึกไฟล์ response_pattern.json
with open(OUT_FILE_PATTERN, "w", encoding="utf-8") as f:
    json.dump(response_pattern, f, ensure_ascii=False, indent=4)

print(f"✅ eval_result.json บันทึกเรียบร้อย: {OUT_FILE_SUMMARY}")
print(f"✅ response_pattern.json บันทึกเรียบร้อย: {OUT_FILE_PATTERN}")
