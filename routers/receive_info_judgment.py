from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class DataPayload(BaseModel):
  key: str
  postid: int
  label: str

@router.post("/receive-data/")
async def receive_data(payload: DataPayload):
  received_data = {
    "received_key": payload.key, 
    "received_postid": payload.postid, 
    "received_label": payload.label
  }
  return received_data
