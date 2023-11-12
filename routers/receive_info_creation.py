from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from dependencies import get_queue_key_creation
from queue import Queue

router = APIRouter()

class DataPayload(BaseModel):
  image_identifiers: list

@router.post("/quest/{QUEST_ID}/shot/shot")
async def receive_data(QUEST_ID: int, payload: DataPayload, queue: Queue = Depends(get_queue_key_creation)):
    try:
        if not payload.image_identifiers:  # 리스트가 비어있는지 확인
            raise ValueError("No image identifiers provided")

        # 받아온 데이터를 큐에 추가
        received_data = {
            "image_identifiers": payload.image_identifiers,
        }
        queue.put(received_data)

        # 응답 반환
        return {"image_identifiers": payload.image_identifiers, "queue_size": queue.qsize()}
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        # 서버 내부 오류 처리
        return JSONResponse(status_code=500, content={"message": "Internal server error", "error": str(e)})
