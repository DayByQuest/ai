from fastapi import APIRouter, Depends
from pydantic import BaseModel
from dependencies import get_queue_key_judgment
from queue import Queue

router = APIRouter()

class DataPayload(BaseModel):
  image_identifiers: list
  label: str

@router.post("/post/{POST_ID}/judge")
async def receive_data(POST_ID: int, payload: DataPayload,  queue: Queue = Depends(get_queue_key_judgment)):
  received_data = {
    "image_identifiers": payload.image_identifiers, 
    "label": payload.label,
    "postid": POST_ID
  }
  queue.put(received_data)
  return received_data
