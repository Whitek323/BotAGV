
INTENT_PATH = "../data/intents/intents.json"
MODEL_OUTPUT_PATH = "../data/model/new/data.pth"

import numpy as np
def bag_of_words(tokenized_sentence, all_words):
    """
    sentence = ['มี', 'สถานที่', 'ที่', 'แนะนำ', 'ไหม']
    words    = ['มี', 'ที่อื่น', 'แนะนำ', 'มั้ย']
    bag      = [ 1 ,    0 ,     1,     0]
    """

    tokenized_sentence = [w for w in tokenized_sentence]
    bag = np.zeros(len(all_words), dtype=np.float32)
    for idx, w in enumerate(all_words):
        if w in tokenized_sentence:
            bag[idx] = 1.0

    return bag

"""### Import File"""

import json
from pythainlp import word_tokenize

with open(INTENT_PATH ,'r',encoding="utf-8") as f:
    intents = json.load(f)

all_words = []
tags = []
xy = []
for intent in intents['intents']:
    tag = intent['tag']
    tags.append(tag)
    for pattern in intent['patterns']:
        w = word_tokenize(pattern, engine="newmm", keep_whitespace=False)
        all_words.extend(w)
        xy.append((w,tag))

"""### Difine ignore words"""

ignore_words = ["?", "!", ".", ",", "ๆ", "ฯ", "'", "(", ")"]

# ignore_words = ["?", "!", ".", ",", "ๆ", "ฯ", "'", "(", ")",
#                 "หรอ","เหรอ","ค่ะ","คะ","ครับ","ค่า","หน่อย","อ่ะ","ให้หน่อย",
#                  "จ้า", "จ๋า", "ฮะ", "แหละ", "นะ", "น้า", "เนอะ", "ล่ะ", "หละ",
#                 "เอง", "มั้ย", "ไหม", "ละ","บ้าง","ฮ่ะ","เฮอะ","อยาก"]

all_words = [w for w in all_words if w not in ignore_words]
all_words = sorted(set(all_words))

X_train = []
y_train = []

for(pattern_sentece,tag) in xy:
    bag = bag_of_words(pattern_sentece, all_words)
    X_train.append(bag)

    label = tags.index(tag)
    y_train.append(label)

X_train = np.array(X_train)
y_train = np.array(y_train)

from torch.utils.data import Dataset, DataLoader
class ChatDataset(Dataset):
    def __init__(self):
        self.n_samples = len(X_train)
        self.x_data = X_train
        self.y_data = y_train

    def __getitem__(self,index):
        return self.x_data[index],self.y_data[index]

    def __len__(self):
        return self.n_samples

"""### Hyper Parameter"""

input_size = len(X_train[0])
batch_size = 8
hidden_size = input_size
output_size = len(tags)
learning_rate = 0.001
num_epochs = 100
print(input_size)
print(hidden_size)

import torch
dataset = ChatDataset()
train_loader = DataLoader(dataset=dataset, batch_size=batch_size, shuffle=True, num_workers=2)

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

import torch.nn as nn

class NeuralNet(nn.Module):
    def __init__(self, input_size, hidden_size, num_classes):
        super(NeuralNet,self).__init__()
        self.l1 = nn.Linear(input_size, hidden_size)
        self.l2 = nn.Linear(hidden_size, hidden_size)
        self.l3 = nn.Linear(hidden_size, num_classes)
        self.relu = nn.ReLU()

    def forward(self, x):
        out = self.l1(x)
        out = self.relu(out)
        out = self.l2(out)
        out = self.relu(out)
        out = self.l3(out)
        # no activation and no softmax
        return out

model = NeuralNet(input_size,hidden_size,output_size).to(device)

"""### loss and optimizer"""

criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)

for epoch in range(num_epochs):
    for (words,labels) in train_loader:
        words = words.to(device)
        labels = labels.to(device)

        # forward
        outputs = model(words)
        loss = criterion(outputs, labels)

        # backward and optimizer step
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

    if (epoch +1) % 10 == 0:
        print(f'epoch {epoch+1}/{num_epochs}, loss={loss.item():.4f}')

print(f'final loss, loss={loss.item():.4f}')

data = {
    "model_state": model.state_dict(),
    "input_size": input_size,
    "output_size": output_size,
    "hidden_size": hidden_size,
    "all_words": all_words,
    "tags": tags
}

torch.save(data, MODEL_OUTPUT_PATH)

print(f'training complete. file saved to {MODEL_OUTPUT_PATH}')

data = torch.load(MODEL_OUTPUT_PATH)

input_size = data["input_size"]
hidden_size = data["hidden_size"]
output_size = data["output_size"]
all_words = data["all_words"]
tags = data["tags"]
model_state = data["model_state"]

with open(INTENT_PATH , 'r') as f:
    intents = json.load(f)

import random

model.load_state_dict(model_state)
model.eval()

bot_name = "น้องกำปัด"
print("Let's chat! type 'quit' to exit")

while True:
    sentence = input('You: ')
    if sentence == "quit":
        break

    sentence = word_tokenize(sentence, engine="newmm", keep_whitespace=False)
    filtered_sentence = [w for w in sentence if w not in ignore_words]
    X = bag_of_words(filtered_sentence,all_words)
    print("Token หลังกรอง:", filtered_sentence)
    print("All words",all_words)
    X = X.reshape(1, X.shape[0])
    X = torch.from_numpy(X).to(device)

    output = model(X)
    _, predicted = torch.max(output, dim=1)
    tag = tags[predicted.item()]

    probs = torch.softmax(output, dim=1)
    prob = probs[0][predicted.item()]
    print(prob.item())
    if prob.item() > 0.8:
        for intent in intents["intents"]:
            if tag == intent["tag"]:
                response = random.choice(intent["responses"])  # ดึง response แบบ dict
                sentence = response["sentence"]

                print(f"{bot_name}: {sentence}")


    else:
        print(f"{bot_name}: I don't understand...")