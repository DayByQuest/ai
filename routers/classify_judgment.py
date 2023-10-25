import numpy as np
import torch
from PIL import Image
import clip
import json
import requests

def classify(config) -> list:
	device = torch.device("cuda:1" if torch.cuda.is_available() else "cpu")
	model, preprocess = clip.load("ViT-L/14@336px")
	model.to(device).eval()

	labels_url = 'https://storage.googleapis.com/download.tensorflow.org/data/imagenet_class_index.json'
	labels = json.loads(requests.get(labels_url).text)
	imagenet_labels = []
	imagenet_labels = [labels[str(k)][1] for k in range(len(labels))]
	text_descriptions = [f"This is a photo of a {label}" for label in imagenet_labels]
	text_tokens = clip.tokenize(text_descriptions).to(device)

	image = "instance"
	image_input = torch.tensor(image).to(device)

	with torch.no_grad():
			image_features = model.encode_image(image_input).float()
			text_features = model.encode_text(text_tokens).float()
			
			image_features /= image_features.norm(dim=-1, keepdim=True)
			text_features /= text_features.norm(dim=-1, keepdim=True)

	text_probs = (100.0 * image_features @ text_features.T).softmax(dim=-1)
	top_probs, top_labels = text_probs.cpu().topk(config.top_k, dim=-1)
