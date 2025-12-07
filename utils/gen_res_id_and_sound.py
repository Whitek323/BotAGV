import json
from collections import OrderedDict
import asyncio
import edge_tts
from cute_voice import CuteVoice
import os

# -----------------------------
# CONFIG
# -----------------------------
INPUT_FILE = "./formatjson/intents_input.json"
OUTPUT_JSON = "./formatjson/intents.json"
OUTPUT_AUDIO_DIR = "./output/sound/th/"
TMP_AUDIO = "./output/tmp_output.wav"

# -----------------------------
# STEP 1: สร้าง intents.json พร้อม res_id
# -----------------------------
def generate_intents_with_resid():
    # สร้างโฟลเดอร์ output ถ้ายังไม่มี
    os.makedirs(os.path.dirname(OUTPUT_JSON), exist_ok=True)

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    res_counter = 1

    for intent in data.get("intents", []):
        new_responses = []

        for response in intent.get("responses", []):
            # กรณี response เป็น string → แปลงให้เป็น dict
            if isinstance(response, str):
                response = {"sentence": response}

            # เพิ่ม res_id ถ้ายังไม่มี
            if "res_id" not in response:
                response["res_id"] = str(res_counter)
                res_counter += 1

            # จัดลำดับให้สวยงาม: res_id → sentence
            ordered_response = OrderedDict()
            ordered_response["res_id"] = response["res_id"]
            ordered_response["sentence"] = response["sentence"]

            new_responses.append(ordered_response)

        intent["responses"] = new_responses

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"✅ เพิ่ม 'res_id' และ 'sentence' เรียบร้อย: {OUTPUT_JSON}")



# -----------------------------
# STEP 2: สร้างเสียงจากข้อความใน intents.json
# -----------------------------
processor = CuteVoice(output_path=TMP_AUDIO)

async def generate_and_play(text: str, file_save: str):
    try:
        os.makedirs(os.path.dirname(file_save), exist_ok=True)

        print(f"[Generate] Using EdgeTTS for: {text}")
        communicate = edge_tts.Communicate(
            text,
            voice="th-TH-PremwadeeNeural",
            rate="-30%",
            pitch="+10Hz"
        )

        await communicate.save(TMP_AUDIO)

        print(f"[Robotizing] {file_save}.wav")
        processor.cute_robotize(TMP_AUDIO, f"{file_save}.wav")

    except Exception as e:
        print(f"[Error] generate_and_play: {e}")


async def generate_all_voices():
    with open(OUTPUT_JSON, "r", encoding="utf-8") as f:
        intents = json.load(f)

    for intent in intents.get("intents", []):
        for resp in intent.get("responses", []):
            res_id = resp.get("res_id")
            sentence = resp.get("sentence")
            if res_id and sentence:
                output_path = os.path.join(OUTPUT_AUDIO_DIR, res_id)
                print(f"Processing res_id={res_id}: {sentence}")
                await generate_and_play(sentence, output_path)


# -----------------------------
# MAIN
# -----------------------------
def main():
    # ขั้นตอนที่ 1: สร้างไฟล์ intents.json
    generate_intents_with_resid()

    # ขั้นตอนที่ 2: สร้างเสียงทั้งหมด
    asyncio.run(generate_all_voices())

if __name__ == "__main__":
    main()
