import torch
import torch.nn as nn
import random
import json
import re
import numpy as np
from pythainlp import word_tokenize
from neural_net import NeuralNet
class BotUtils :
    def load_model(model_path, intent_path):
       data = torch.load(model_path, map_location=torch.device("cpu"))
       input_size = data["input_size"]
       hidden_size = data["hidden_size"]
       output_size = data["output_size"]
       all_words = data["all_words"]
       tags = data["tags"]
       model_state = data["model_state"]

       with open(intent_path, encoding="utf8") as f:
           intents = json.load(f)

       model = NeuralNet(input_size, hidden_size, output_size)
       model.load_state_dict(model_state)
       model.eval()
       return model, all_words, tags, intents

  
    def bag_of_words(tokenized_sentence, all_words):
        bag = np.zeros(len(all_words), dtype=np.float32)
        for idx, w in enumerate(all_words):
            if w in tokenized_sentence:
                bag[idx] = 1.0
        return bag

    def clean_text(text):
        return re.sub(r'(ค่ะ/|/ค่ะ|ดิฉัน|ดิฉัน/|/ดิฉัน|\*|/คะ|คะ )', '', text)

    def get_response(tag, intents):
        for intent in intents["intents"]:
            if intent["tag"] == tag:
                response = random.choice(intent["responses"])
                return response["sentence"], response["res_id"]
        return "ขอโทษ ฉันไม่เข้าใจ", -1


    # === Chat logic (was ChatBot class) ===
    def predict_intent(model, sentence, all_words, tags, device="cpu"):
        tokens = word_tokenize(sentence, engine="newmm", keep_whitespace=False)
        X = BotUtils.bag_of_words(tokens, all_words)
        X = torch.from_numpy(X).reshape(1, -1).to(torch.device(device))
        output = model(X)
        _, predicted = torch.max(output, dim=1)
        probs = torch.softmax(output, dim=1)
        return tags[predicted.item()], probs[0][predicted.item()].item()





