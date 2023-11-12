from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ValidationError
from dependencies import get_queue_key_judgment
from queue import Queue

router = APIRouter()

class DataPayload(BaseModel):
    image_identifiers: list
    label: str

@router.post("/post/{POST_ID}/judge/judge")
async def receive_data(POST_ID: int, payload: DataPayload, queue: Queue = Depends(get_queue_key_judgment)):
    try:
        # 유효성 검사를 포함한 데이터 처리
        received_data = {
            "image_identifiers": payload.image_identifiers, 
            "label": payload.label
        }
        queue.put(received_data)
        return received_data
    except ValidationError as e:
        # 유효성 검사 실패 시 예외 처리
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        # 기타 예외 처리
        raise HTTPException(status_code=500, detail="Internal Server Error")
