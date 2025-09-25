
import asyncio
import math
import random
import edge_tts
import sounddevice as sd
import soundfile as sf
from cute_voice import CuteVoice
import os
processor = CuteVoice(output_path="./output.wav")

async def generate_and_play(text: str = None, act: int = None, path: str = None):
    global ser
    try:
        if path and os.path.exists(path):
            print(f"[Play] Using provided audio file: {path}")
            data, sample_rate = sf.read(path)
        else:
            print(f"[Generate] Using EdgeTTS for: {text}")
            communicate = edge_tts.Communicate(text, voice="th-TH-PremwadeeNeural", rate="-30%", pitch="+10Hz")
            input_audio_path = f"./output/tmp_output.wav"
            output_audio_path = f"./output/output.wav"
            await communicate.save(input_audio_path)

            print("Audio file saved.")


            processor.cute_robotize(input_audio_path, output_audio_path)

            data, sample_rate = sf.read(output_audio_path)

        duration = len(data) / sample_rate
        rounded_duration = int(math.ceil(duration))
        print(f"Audio duration: {math.ceil(duration)} seconds")
        sd.play(data, sample_rate)
        if act == 0:
            while rounded_duration > 0:
                act_rand = random.randint(1,4)
                act_dur = random.randint(1,3)
                if rounded_duration > act_dur:
                    rounded_duration -= act_dur
                else:
                    act_dur = rounded_duration
                    rounded_duration = 0

    except Exception as e:
        print(f"[Error] generate_and_play: {e}")
        
asyncio.run(generate_and_play("สวัสดีค่ะ", act=0))