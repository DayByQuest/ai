from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from dependencies import get_queue_file_creation
from queue import Queue
from pydantic import BaseModel
from model.model import classifier
from typing import List

router = APIRouter()

class DataToSend(BaseModel):
  label_list: List[str]
  questid: int

instant_classifier = classifier()

@router.patch('/result/creation')
async def classify(queue: Queue = Depends(get_queue_file_creation)):
  data = queue.get()
  images = data['images']
  quest_id = data['questid']

  top_probs, label_list = instant_classifier.classify_creation(images)
  label_list = list(set(label_list))
  
  data_to_send = DataToSend(label_list=label_list, questid=quest_id)
  return JSONResponse(content=data_to_send.dict())
