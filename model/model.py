import numpy as np
import torch
from PIL import Image
import clip
import jax
import json
import requests
import io
import os
from typing import List

class classifier():
  def __init__(self):
    self.device = torch.device("cuda:1" if torch.cuda.is_available() else "cpu")
    self.model, self.preprocess = clip.load("ViT-L/14@336px")

    # 외부 레이블 가져오기
    DATASET = os.getenv('DATASET')
    with open(DATASET, "r") as f:
      self.labels = json.load(f)
    self.labels = [item.replace('_', ' ') for item in self.labels]

    # 직접 입력으로 추가된 레이블 가져오기
    LABEL_PATH = os.getenv('LABEL_PATH')
    with open(LABEL_PATH, "r") as f:
      for line in f:
        self.labels.append(line.strip())
    text_descriptions = [f"This is a photo of a {label}" for label in self.labels]
    self.text_tokens = clip.tokenize(text_descriptions).to(self.device)
    self.model.to(self.device).eval()

    self.url_for_deepl = 'https://api-free.deepl.com/v2/translate'
    AUTH_KEY = os.getenv('AUTH_KEY')
    self.params = {'auth_key' : AUTH_KEY, 'text' : '', 'source_lang' : 'EN', 'target_lang': 'KO' }

  def __del__(self):
    print("메모리를 해제합니다.")

  def classify_creation(self, source: List[str]):
    images = []
    for src in source:
      image = Image.open(io.BytesIO(src))
      images.append(self.preprocess(image))
    image_input = torch.tensor(np.stack(images)).to(self.device)

    with torch.no_grad():
      image_features = self.model.encode_image(image_input).float()
      text_features = self.model.encode_text(self.text_tokens).float()

      image_features /= image_features.norm(dim=-1, keepdim=True)
      text_features /= text_features.norm(dim=-1, keepdim=True)

    text_probs = (100.0 * image_features @ text_features.T).softmax(dim=-1)
    top_probs, top_labels = text_probs.cpu().topk(5, dim=-1)
    label_list = [[self.labels[index] for index in top_labels[i].numpy()] for i in range(len(images))]
    label_list = np.array(label_list).flatten().tolist()
    print(label_list)

    # 영어 -> 한국어로 번역해서 레이블 리스트 전달
    self.params['text'] = label_list
    self.params['source_lang'] = 'EN' 
    self.params['target_lang'] = 'KO'
    result = requests.post(self.url_for_deepl, data=self.params, verify=False)
    ko_label_list = [result.json()['translations'][i]["text"] for i in range(len(result.json()['translations']))]
    print(ko_label_list)
    
    return top_probs, ko_label_list

  def classify_judgment(self, source: List[str], label: str):
    # 한국어 -> 영어
    message = label
    self.params['text'] = message
    self.params['source_lang'] = 'KO'
    self.params['target_lang'] = 'EN-US'
    result = requests.post(self.url_for_deepl, data=self.params, verify=False)
    label = result.json()['translations'][0]["text"]
    print(label)

    images = []
    for src in source:
      image = Image.open(io.BytesIO(src))
      images.append(self.preprocess(image))
    image_input = torch.tensor(np.stack(images)).to(self.device)
    
    with torch.no_grad():
      image_features = self.model.encode_image(image_input).float()
      text_features = self.model.encode_text(self.text_tokens).float()

      image_features /= image_features.norm(dim=-1, keepdim=True)
      text_features /= text_features.norm(dim=-1, keepdim=True)

    text_probs = (100.0 * image_features @ text_features.T).softmax(dim=-1)
    top_probs, top_labels = text_probs.cpu().topk(5, dim=-1)
    
    candidates = []
    for i in range(len(images)):
      if self.labels[top_labels[i][0]] == label:
        candidates.append(i)
    
    if len(candidates) == 0:
      print("FAIL")
      return "FAIL"
    else:
      print("SUCCESS")
      return "SUCCESS"

    # for candidate in candidates:
    #   if top_probs[candidate][0] < 0.6 or top_probs[candidate][0] <= 2 * top_probs[candidate][1]:
    #     print(self.labels[top_labels[candidate][0]], self.labels[top_labels[candidate][1]])
    #     print(top_probs[candidate][0], top_probs[candidate][1])
    #     print("FAIL")
    #     return "FAIL"
    #   else:
    #     print("SUCCESS")
    #     return "SUCCESS"

  def update_labels(self, label):
    # 한국어 -> 영어
    message = label
    self.params['text'] = message
    self.params['source_lang'] = 'KO'
    self.params['target_lang'] = 'EN-US'
    result = requests.post(self.url_for_deepl, data=self.params, verify=False)
    label = result.json()['translations'][0]["text"]

    # label이 전체 label list에 없을 경우, 추가해준다.
    if label not in self.labels:
      LABEL_PATH = os.getenv('LABEL_PATH')
      with open(LABEL_PATH, "a") as f:
        f.write(label+"\n")
      self.labels.append(label)
      text_descriptions = [f"This is a photo of a {label}" for label in self.labels]
      self.text_tokens = clip.tokenize(text_descriptions).to(self.device)
      self.model.to(self.device).eval()