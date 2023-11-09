from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from dependencies import get_queue_file_judgment
from queue import Queue
from pydantic import BaseModel
from model.model import classifier
from typing import List
import httpx
import os
import json

router = APIRouter()

class DataToSend(BaseModel):
  judgement: str

instant_classifier = classifier()

@router.patch('/post/{POST_ID}/judge')
async def classify(queue: Queue = Depends(get_queue_file_judgment)):
  data = queue.get()
  images = data['images']
  label = data['label']
  post_id = data['postid']

  # 백엔드 서버의 엔드포인트 URL
  BACKEND_URL = os.getenv('BACKEND_URL')  
  BACKEND_URL = BACKEND_URL + "/post/" + str(post_id) + "/judge"
  success = instant_classifier.classify_judgment(images, label)
  # success="SUCCESS" # 디버깅용 코드
  
  data_to_send = DataToSend(judgement=success)
  try:
      # 비동기 클라이언트를 사용하여 백엔드 서버에 PATCH 요청을 보냅니다.
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
  except httpx.HTTPStatusError as e:
      # 오류 상태 코드 처리
      raise HTTPException(status_code=e.response.status_code, detail=str(e))
