import torch
import torch.nn as nn
import random
import json
import re
import numpy as np
from pythainlp import word_tokenize
from flask import Flask,request,render_template,jsonify
from neural_net import NeuralNet
from bot_utils import BotUtils
from gtts import gTTS
import io
from pydub import AudioSegment
import sounddevice as sd
import speech_recognition as sr

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

# === Configuration replacement ===
APP_PATHS = {
    "DATA_INTENT": "data/intents/intents.json",
    "DATA_MODEL": "data/model/data.pth"
}

model, all_words, tags, intents = BotUtils.load_model(APP_PATHS["DATA_MODEL"], APP_PATHS["DATA_INTENT"])

@app.route("/")
def index():
    return render_template("/index.html")
def mp3_bytes_to_wav_io(mp3_bytes: bytes) -> io.BytesIO:
    audio = AudioSegment.from_file(io.BytesIO(mp3_bytes), format="mp3")
    wav_io = io.BytesIO()
    audio.export(wav_io, format="wav")
    wav_io.seek(0)
    return wav_io

@app.post("/stt")
def stt():
    f = request.files.get("audio") or request.files.get("file")
    if not f:
        return jsonify({"error": "missing file field 'audio'"}), 400

    # optional: ภาษา (ค่าเริ่มต้นไทย)
    language = request.form.get("language", "th-TH")

    # แปลงเป็น wav โดยให้ ffmpeg เดารูปแบบจาก header (รองรับ webm/ogg/mp3/wav)
    try:
        raw = f.read()
        if not raw:
            return jsonify({"error": "empty file"}), 400

        src_io = io.BytesIO(raw)
        wav_io = io.BytesIO()
        AudioSegment.from_file(src_io).export(wav_io, format="wav")
        wav_io.seek(0)
    except Exception as e:
        return jsonify({"error": f"convert_failed: {type(e).__name__}: {e}"}), 400

    # ถอดเสียง
    r = sr.Recognizer()
    try:
        with sr.AudioFile(wav_io) as source:
            audio = r.record(source)
        text = r.recognize_google(audio, language=language)  # ต้องต่อเน็ต
        return jsonify({"text": text})
    except sr.UnknownValueError:
        return jsonify({"text": "", "error": "unrecognized"}), 422
    except sr.RequestError as e:
        return jsonify({"text": "", "error": f"service_error: {e}"}), 503
    except Exception as e:
        return jsonify({"text": "", "error": f"unexpected: {type(e).__name__}: {e}"}), 500

@app.route("/ai", methods=["POST"])
def aiPost():
    data = request.get_json(silent=True) or {}
    sentence = data.get("sentence") or request.form.get("sentence") or request.args.get("sentence")

    if not sentence:
        return jsonify({"error": "missing 'sentence'"}), 400
    tag, prob = BotUtils.predict_intent(model, sentence, all_words, tags)
    if prob >= 0.95:
        response, res_id = BotUtils.get_response(tag, intents)
        return {"response": response}
    else:
        return {"response":"ขออภัย ฉันยังไม่เข้าใจคำถามนี้"}

@app.route("/speak_answer", methods=["POST"])
def speak_answer():
    json_content = request.json
    answer = json_content.get("answer")
    #res_id = json_content.get("res_id")

    cleaned_answer = BotUtils.clean_text(answer)
    # สร้างไฟล์เสียงใหม่หรือเขียนทับไฟล์เสียงเดิม
    tts = gTTS(text=cleaned_answer, lang='th')
    audio_file_path = "static/response.mp3"  # ใช้ชื่อไฟล์เดียวกัน
    tts.save(audio_file_path)
    
    # ส่ง URL กลับไป
    return {"audio_url": "/static/response.mp3"}

def start_app():
    # app.run(host="0.0.0.0", port=8080, debug=True)
    app.run(host="0.0.0.0", debug=False)


if __name__ == "__main__":
    start_app()
