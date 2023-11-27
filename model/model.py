import numpy as np
import torch
from PIL import Image
import clip
import json
import requests
import io
import os
from typing import List
from koclip.koclip import load_koclip

class classifier():
  def __init__(self):
    self.device = torch.device("cuda:1" if torch.cuda.is_available() else "cpu")
    self.model, self.processor = load_koclip("koclip-large")

    with open("labels.txt", "r") as f:
      labels = f.read()
      print(labels)
    self.text = [f"이것은 {label}이다." for label in labels]

    self.model.to(self.device).eval()

  def __del__(self):
    print("메모리를 해제합니다.")

  def classify_creation(self, source: List[str]):
    images = []
    for src in source:
      image = Image.open(io.BytesIO(src))
      images.append(self.preprocess(image))
    image_input = torch.tensor(np.stack(images)).to(self.device)

    with torch.no_grad():
      inputs = processor(
        text=self.text,
        images=images, 
        return_tensors="jax", # could also be "pt" 
        padding=True
      )
      outputs = model(**inputs)
      probs = jax.nn.softmax(outputs.logits_per_image, axis=1)

    top_probs = []
    top_labels = []
    for prob in probs:
      for idx, prob in sorted(enumerate(prob), key=lambda x: x[1], reverse=True):
        tmp_probs = []
        tmp_labels = []
        tmp_probs.append(prob)
        tmp_labels.append(self.text[idx])
      
      top_probs.append(tmp_probs)
      top_labels.append(tmp_labels)

    label_list = [[label for label in top_labels[i].numpy()] for i in range(len(images))]
    label_list = np.array(label_list).flatten().tolist()

    return top_probs, label_list

  def classify_judgment(self, source: List[str], label: str):
    images = []
    for src in source:
      image = Image.open(io.BytesIO(src))
      images.append(self.preprocess(image))
    image_input = torch.tensor(np.stack(images)).to(self.device)
    
    with torch.no_grad():
      inputs = processor(
        text=self.text,
        images=images, 
        return_tensors="jax", # could also be "pt" 
        padding=True
      )
      outputs = model(**inputs)
      probs = jax.nn.softmax(outputs.logits_per_image, axis=1)

    top_probs = []
    top_labels = []
    for prob in probs:
      for idx, prob in sorted(enumerate(prob), key=lambda x: x[1], reverse=True):
        tmp_probs = []
        tmp_labels = []
        tmp_probs.append(prob)
        tmp_labels.append(self.text[idx])
      
      top_probs.append(tmp_probs)
      top_labels.append(tmp_labels)

    candidates = []
    for i in range(len(images)):
      if self.imagenet_labels[top_labels[i][0]] == label:
        candidates.append(i)
    
    if len(candidates) == 0:
      return "FAIL"

    for candidate in candidates:
      if top_probs[candidate][0] < 0.6 or top_probs[candidate][0] <= 2 * top_probs[candidate][1]:
        return "FAIL"
      else:
        return "SUCCESS"
