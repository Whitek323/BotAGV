import json

# ชื่อไฟล์ต้นฉบับ
# ใช้ไฟล์ intents ที่อยู่ในโฟลเดอร์ output เป็นไฟล์ต้นทาง
input_file = "./intents.json"
# ชื่อไฟล์ผลลัพธ์: แปลง responses ให้เป็นลิสต์ของประโยค และบันทึกไว้ในโฟลเดอร์ input
output_file = "./intents_no_resid_no_sentent.json"

# โหลดข้อมูลจากไฟล์ JSON
with open(input_file, "r", encoding="utf-8") as f:
    data = json.load(f)

# แปลง responses: จาก object {res_id, sentence} เป็นเพียงสตริงของ sentence
for intent in data.get("intents", []):
    original_responses = intent.get("responses", [])
    normalized_responses = []
    for response in original_responses:
        if isinstance(response, dict):
            sentence = response.get("sentence")
            if sentence is not None:
                normalized_responses.append(sentence)
        elif isinstance(response, str):
            normalized_responses.append(response)
    intent["responses"] = normalized_responses

# บันทึกผลลัพธ์กลับเป็นไฟล์ JSON
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(
    "แปลง responses เป็นประโยคเรียบร้อยแล้ว และลบ res_id ทั้งหมด! ✅\n"
    f"ไฟล์ถูกบันทึกที่: {output_file}"
)