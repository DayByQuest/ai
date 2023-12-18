from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, ValidationError
from typing import List
from fastapi.responses import JSONResponse
from dependencies import get_model
from datetime import datetime
import httpx
import asyncio
import io
import os
import json

router = APIRouter()

class DataPayload(BaseModel):
    imageIdentifiers: list
    imageDescription: str

class DataToSend(BaseModel):
    labels: List[str]

async def get_image_from_cdn(cdn_url: str, trial_num: int = 3) -> bytes:
    # 안 될 경우 세 번 더 시도, 안 되면 로그로 남기고 종료.
    # 위 동작이 필요한 이유 : 스프링 서버에서 이미지를 S3에 업로드하는 시점이 이미지를 가져오는 시점보다 늦을 수 있어서.
    for attempt in range(trial_num):
        async with httpx.AsyncClient() as client:
            response = await client.get(cdn_url)
        if response.status_code == 200:
            return response.content
        else:
            print(f"Attempt {attempt + 1} failed")

        if attempt < trial_num - 1:
            await asyncio.sleep(1)  # 잠시 대기 후 재시도

    print(f"Failed to fetch image from {cdn_url} after {trial_num} attempts.")
    return None 

async def run_model(image_data: list, BACKEND_URL: str, CLOUDFRONT_URL: str, label: str):
    images = await asyncio.gather(*[get_image_from_cdn(CLOUDFRONT_URL + cdn_url) for cdn_url in image_data])
    
    if None in images:
        now = datetime.today().strftime("%Y-%m-%d %H:%M:%S") 
        print(now + " Aborting model inference.")
        return
        
    model = get_model()    
    top_probs, label_list = model.classify_creation(images)
    label_list = list(set(label_list + [label]))
    # label_list = ['banana', 'apple', 'train'] # 디버깅용 코드
    print(label_list)
    
    now = datetime.today().strftime("%Y-%m-%d %H:%M:%S") 
    print(now + " Inference Finished.")
    data_to_send = DataToSend(labels=label_list)
    async with httpx.AsyncClient() as client:
        response = await client.patch(BACKEND_URL, json=data_to_send.dict(), headers={"Authorization": "UserId 5", 'Content-Type': 'application/json'})
    model.update_labels(label)

# imageIdentifiers 수신, labels 전송
@router.post("/quest/{QUEST_ID}/shot")
async def receive_data(QUEST_ID: int, payload: DataPayload, background_tasks: BackgroundTasks):
    try:
        if not payload.imageIdentifiers:  # 리스트가 비어있는지 확인
            raise ValueError("No image identifiers provided")

        # 백엔드 서버의 엔드포인트 URL
        BACKEND_URL = os.getenv('BACKEND_URL')  
        BACKEND_URL = BACKEND_URL + "/quest/" + str(QUEST_ID) + "/shot"

        CLOUDFRONT_URL = os.getenv('CLOUDFRONT_URL')  
        
        # 필요한 데이터 처리 및 클라이언트에게 빠른 응답
        background_tasks.add_task(run_model, payload.imageIdentifiers, BACKEND_URL, CLOUDFRONT_URL, payload.imageDescription)
        return {"message": "Data received, processing in background"}

    except ValidationError as e:
        print(e)
        # 유효성 검사 실패 시 예외 처리
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        # 기타 예외 처리
        print(e)
        raise HTTPException(status_code=500, detail="Internal Server Error")
