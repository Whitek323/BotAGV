import asyncio
import math
import random
import edge_tts
import sounddevice as sd
import soundfile as sf
from cute_voice import CuteVoice
import os
import json

processor = CuteVoice(output_path="./output.wav")

async def generate_and_play(text: str = None, filename: str = None, act: int = None, path: str = None):
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
            output_audio_path = f"./output/{filename}.wav"
            await communicate.save(input_audio_path)

            print("Audio file saved.")

            processor.cute_robotize(input_audio_path, output_audio_path)


    except Exception as e:
        print(f"[Error] generate_and_play: {e}")


def main():
    # โหลด intents.json
    with open("../data/intents/intents.json", "r", encoding="utf-8") as f:
        intents = json.load(f)

    # loop ทุก response
    for intent in intents["intents"]:
        for resp in intent.get("responses", []):
            res_id = resp.get("res_id")
            sentence = resp.get("sentence")
            if res_id and sentence:
                print(f"Processing res_id={res_id}, sentence={sentence}")
                asyncio.run(generate_and_play(sentence, res_id, act=0))


if __name__ == "__main__":
    main()
