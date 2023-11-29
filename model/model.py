import numpy as np
import torch
from PIL import Image
import jax
import json
import requests
import io
import os
from typing import List
from koclip.koclip import load_koclip

class classifier():
  def __init__(self):
    self.device = torch.device("cuda:1" if torch.cuda.is_available() else "cpu")
    self.model, self.processor = load_koclip("koclip-base")

    self.LABEL_PATH = os.getenv('LABEL_PATH')  
    with open(self.LABEL_PATH, "r") as f:
      self.labels = f.readlines()
    self.labels = [label.strip() for label in self.labels]

    self.text = [f"이것은 {label}이다." for label in self.labels]

    # self.model.to(self.device).eval()

  def __del__(self):
    print("메모리를 해제합니다.")

  def classify_creation(self, source: List[str]):
    images = []
    for src in source:
      image = Image.open(io.BytesIO(src))
      images.append(image)
      # 이미지 사이즈 전처리
    image_input = torch.tensor(np.stack(images)).to(self.device)

    with torch.no_grad():
      inputs = self.processor(
        text=self.text,
        images=images, 
        return_tensors="jax",
        padding=True
      )
      outputs = self.model(**inputs)
      probs = jax.nn.softmax(outputs.logits_per_image, axis=1)

    top_probs = []
    top_labels = []
    for prob in probs:
      tmp_probs = []
      tmp_labels = []
      for idx, p in sorted(enumerate(prob), key=lambda x: x[1], reverse=True):
        print(idx, p, self.labels[idx])
        tmp_probs.append(p)
        tmp_labels.append(idx)
        if len(tmp_probs) == 5: break
      
      top_probs.append(tmp_probs)
      top_labels.append(tmp_labels)

    label_list = [[self.labels[idx] for idx in top_labels[i]] for i in range(len(images))]
    label_list = np.array(label_list).flatten().tolist()
    label_list = list(set(label_list))
    print(label_list)
    return top_probs, label_list

  def classify_judgment(self, source: List[str], label: str):
    # label이 전체 label list에 없을 경우, 추가해준다.
    if label not in self.labels:
      with open(self.LABEL_PATH, "a") as f:
        f.write(label+"\n")
      self.labels.append(label)
      self.text = [f"이것은 {label}이다." for label in self.labels]

    images = []
    for src in source:
      image = Image.open(io.BytesIO(src))
      images.append(image)
      # 이미지 사이즈 전처리
    image_input = torch.tensor(np.stack(images)).to(self.device)
    
    with torch.no_grad():
      inputs = self.processor(
        text=self.text,
        images=images, 
        return_tensors="jax",
        padding=True
      )
      outputs = self.model(**inputs)
      probs = jax.nn.softmax(outputs.logits_per_image, axis=1)

    top_probs = []
    top_labels = []
    for prob in probs:
      tmp_probs = []
      tmp_labels = []
      for idx, p in sorted(enumerate(prob), key=lambda x: x[1], reverse=True):
        print(idx, p, self.labels[idx])
        tmp_probs.append(p)
        tmp_labels.append(idx)
        if len(tmp_probs) == 5: break
      
      top_probs.append(tmp_probs)
      top_labels.append(tmp_labels)

    candidates = []
    for i in range(len(images)):
      if self.labels[top_labels[i][0]] == label:
        candidates.append(i)
    
    if len(candidates) == 0:
      print("FAIL")
      return "FAIL"

    for candidate in candidates:
      if top_probs[candidate][0] < 0.6 or top_probs[candidate][0] <= 2 * top_probs[candidate][1]:
        print(top_probs[candidate][0], top_probs[candidate][1])
        print("FAIL")
        return "FAIL"
      else:
        print("SUCCESS")
        return "SUCCESS"
