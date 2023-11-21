import numpy as np
import torch
from PIL import Image
import clip
import json
import requests
import io
import os
from typing import List

class classifier():
  def __init__(self):
    self.device = torch.device("cuda:1" if torch.cuda.is_available() else "cpu")
    self.model, self.preprocess = clip.load("RN50")

    LABEL_URL = os.getenv('LABEL_URL')  
    self.labels = json.loads(requests.get(LABEL_URL).text)
	
    self.model.to(self.device).eval()

    self.imagenet_labels = [self.labels[str(k)][1] for k in range(len(self.labels))]
    text_descriptions = [f"This is a photo of a {label}" for label in self.imagenet_labels]
    self.text_tokens = clip.tokenize(text_descriptions).to(self.device)

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
    label_list = [[self.imagenet_labels[index] for index in top_labels[i].numpy()] for i in range(len(images))]
    label_list = np.array(label_list).flatten().tolist()
    return top_probs, label_list

  def classify_judgment(self, source: List[str], label: str):
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
      if self.imagenet_labels[top_labels[i][0]] == label:
        candidates.append(i)
    
    if len(candidates) == 0:
      return "FAIL"

    for candidate in candidates:
      if top_probs[candidate][0] < 0.6 or top_probs[candidate][0] <= 2 * top_probs[candidate][1]:
        return "FAIL"
      else:
        return "SUCCESS"
