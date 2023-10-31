from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from dependencies import get_queue_file_judgment
from queue import Queue
from pydantic import BaseModel
from model.model import classifier
from typing import List

router = APIRouter()

class DataToSend(BaseModel):
  success: str
  postid: int

instant_classifier = classifier()

@router.patch('/result/judgment')
async def classify(queue: Queue = Depends(get_queue_file_judgment)):
  data = queue.get()
  images = data['images']
  label = data['label']
  post_id = data['postid']

  success = instant_classifier.classify_judgment(images, label)
  
  data_to_send = DataToSend(success=success, postid=post_id)
  return JSONResponse(content=data_to_send.dict())
