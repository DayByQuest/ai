from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, ValidationError
from typing import List
from fastapi.responses import JSONResponse
from dependencies import get_model
import httpx
import asyncio
import io
import os
import json

router = APIRouter()

class DataPayload(BaseModel):
    imageIdentifiers: list
    label: str

class DataToSend(BaseModel):
  judgement: str

async def get_image_from_cdn(cdn_url: str) -> bytes:
    async with httpx.AsyncClient() as client:
        response = await client.get(cdn_url)

    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="이미지를 가져오는데 실패했습니다.") # exception이 아니라 로그에 print만 할 것

    return response.content

async def run_model(image_data: list, label: str, BACKEND_URL: str, CLOUDFRONT_URL: str):
    images = await asyncio.gather(*[get_image_from_cdn(CLOUDFRONT_URL + cdn_url) for cdn_url in image_data]) # 안 될 경우 세 번 더 시도, 안 되면 로그로 남기고 종료.
    
    model = get_model()
    success = model.classify_judgment(images, label)
    # success="SUCCESS" # 디버깅용 코드

    print("Inference Finished.")
    data_to_send = DataToSend(judgement=success)
    async with httpx.AsyncClient() as client:
          response = await client.patch(BACKEND_URL, json=data_to_send.dict(), headers={"Authorization": "UserId 5"})

# imageIdentifiers, label 수신, judgement 전송
@router.post("/post/{POST_ID}/judge")
async def receive_data(POST_ID: int, payload: DataPayload, background_tasks: BackgroundTasks):
    try:
        if not payload.imageIdentifiers:  # 리스트가 비어있는지 확인
            raise ValueError("No image identifiers provided")

        # 백엔드 서버의 엔드포인트 URL
        BACKEND_URL = os.getenv('BACKEND_URL')  
        BACKEND_URL = BACKEND_URL + "/post/" + str(POST_ID) + "/judge"

        CLOUDFRONT_URL = os.getenv('CLOUDFRONT_URL')  
        
        # 필요한 데이터 처리 및 클라이언트에게 빠른 응답
        background_tasks.add_task(run_model, payload.imageIdentifiers, payload.label, BACKEND_URL, CLOUDFRONT_URL)
        return {"message": "Data received, processing in background"}

    except ValidationError as e:
        print(e)
        # 유효성 검사 실패 시 예외 처리
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        # 기타 예외 처리
        print(e)
        raise HTTPException(status_code=500, detail="Internal Server Error")
