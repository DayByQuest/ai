from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from dependencies import get_queue_file_creation
from queue import Queue
from pydantic import BaseModel
from model.model import classifier
from typing import List
import httpx 
import os
import requests

router = APIRouter()

class DataToSend(BaseModel):
    label_list: List[str]

instant_classifier = classifier()

@router.patch('/result/shot')
async def classify(queue: Queue = Depends(get_queue_file_creation)):
    data = queue.get()
    images = data['images']
    quest_id = data['questid']

    # 백엔드 서버의 엔드포인트 URL
    BACKEND_URL = os.getenv('BACKEND_URL')
    BACKEND_URL = BACKEND_URL + "/quest/" + str(quest_id) + "/shot"

    top_probs, label_list = instant_classifier.classify_creation(images)
    label_list = list(set(label_list))
    # label_list = ['banana', 'apple', 'train'] # 디버깅용 코드

    data_to_send = DataToSend(label_list=label_list)
    try:
        # 비동기 클라이언트를 사용하여 백엔드 서버에 PATCH 요청을 보냅니다.
        async with httpx.AsyncClient() as client:
            response = await client.patch(BACKEND_URL, json=data_to_send.dict(), headers={"Authorization": "UserId 5"})
            if response.status_cod == 200:
                # 응답코드가 200일 때, OK 반환
                return "OK"
            else:
                error_message = f"Error: {response.status_code}, {response.text}"
                print(error_message)
                return error_message
    except httpx.HTTPStatusError as e:
        # 오류 상태 코드 처리
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
