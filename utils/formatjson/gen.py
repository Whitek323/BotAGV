import asyncio
import edge_tts
from cute_voice import CuteVoice
import os
import json

processor = CuteVoice(output_path="./tmp_output.wav")

async def generate_and_play(text: str = None,file_save: str = None, act: int = None, path: str = None):
    global ser
    try:
        if path and os.path.exists(path):
            print(f"[Play] Using provided audio file: {path}")

        else:
            print(f"[Generate] Using EdgeTTS for: {text}")
            communicate = edge_tts.Communicate(
                text, voice="th-TH-PremwadeeNeural", rate="-30%", pitch="+10Hz"
            )
            input_audio_path = f"./output/tmp_output.wav"
            output_audio_path = f"{file_save}.wav"
            await communicate.save(input_audio_path)

            print("Audio file saved "+file_save+".wav")

            processor.cute_robotize(input_audio_path, output_audio_path)


    except Exception as e:
        print(f"[Error] generate_and_play: {e}")


def main():
    def gen_all_from_file():
        with open("../data/intents/intents.json", "r", encoding="utf-8") as f:
            intents = json.load(f)

        # loop *response
        for intent in intents["intents"]:
            for resp in intent.get("responses", []):
                res_id = resp.get("res_id")
                sentence = resp.get("sentence")
                if res_id and sentence:
                    print(f"Processing res_id={res_id}, sentence={sentence}")
                    path = "../static/sound/intent/"
                    asyncio.run(generate_and_play(sentence,path+res_id, act=0))
    def gen_one_file():
        filename = "../static/sound/sys/unknown1"
        sentence = "อาอัสยังไม่เข้าใจคำถามนี้เลย... ช่วยถามใหม่ได้ไหมครับ"
        asyncio.run(generate_and_play(sentence, filename, act=0))
    
    gen_all_from_file()
    
if __name__ == "__main__":
    main()
