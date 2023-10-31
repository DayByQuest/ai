from fastapi import APIRouter, Depends
from pydantic import BaseModel
from dependencies import get_queue_key_creation
from queue import Queue

router = APIRouter()

class DataPayload(BaseModel):
  image_identifiers: list

@router.post("/post/{QUEST_ID}/shot")
async def receive_data(QUEST_ID: int, payload: DataPayload,  queue: Queue = Depends(get_queue_key_creation)):
  received_data = {
    "image_identifiers": payload.image_identifiers,
    "questid": QUEST_ID
  }
  queue.put(received_data)
  return payload.image_identifiers, QUEST_ID, queue.qsize()
