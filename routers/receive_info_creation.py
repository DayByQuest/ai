from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class DataPayload(BaseModel):
  key1: str
  key2: str
  key3: str
  questid: int

@router.post("/receive-data/")
async def receive_data(payload: DataPayload):
  received_data = {
    "received_key1": payload.key1,
    "received_key2": payload.key2,
    "received_key3": payload.key3, 
    "received_questid": payload.questid
  }
  return received_data