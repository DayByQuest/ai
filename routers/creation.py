from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, ValidationError
from typing import List
from fastapi.responses import JSONResponse
from model.model import classifier
import httpx
import asyncio
import io
import os
import json

router = APIRouter()

class DataPayload(BaseModel):
    imageIdentifiers: list

class DataToSend(BaseModel):
    label_list: List[str]

instant_classifier = classifier()

async def get_image_from_cdn(cdn_url: str) -> bytes:
    async with httpx.AsyncClient() as client:
        response = await client.get(cdn_url)

    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="이미지를 가져오는데 실패했습니다.")

    return response.content

@router.post("/quest/{QUEST_ID}/shot")
async def receive_data(QUEST_ID: int, payload: DataPayload):
    try:
        if not payload.imageIdentifiers:  # 리스트가 비어있는지 확인
            raise ValueError("No image identifiers provided")
        
        images = await asyncio.gather(*[get_image_from_cdn("https://d1idwg6sscgubz.cloudfront.net/" + cdn_url) for cdn_url in payload.imageIdentifiers])

        # 백엔드 서버의 엔드포인트 URL
        BACKEND_URL = os.getenv('BACKEND_URL')  
        BACKEND_URL = BACKEND_URL + "/quest/" + str(QUEST_ID) + "/shot"

        # top_probs, label_list = instant_classifier.classify_creation(images)
        # label_list = list(set(label_list))
        label_list = ['banana', 'apple', 'train'] # 디버깅용 코드

        data_to_send = DataToSend(label_list=label_list)
        async with httpx.AsyncClient() as client:
          response = await client.patch(BACKEND_URL, json=data_to_send.dict(), headers={"Authorization": "UserId 5"})
          if response.status_code == 200:
            # 응답 코드가 200일 때, OK를 반환합니다.
            return "OK"
          else:
            # 응답 코드가 200이 아닐 때, 에러 코드와 메시지를 출력합니다.
            error_message = f"Error: {response.status_code}, {response.text}"
            print(error_message)
            return error_message
    except ValidationError as e:
        # 유효성 검사 실패 시 예외 처리
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        # 기타 예외 처리
        print(e)
        raise HTTPException(status_code=500, detail="Internal Server Error")
