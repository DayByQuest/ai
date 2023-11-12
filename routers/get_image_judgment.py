from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from typing import List
import httpx
import asyncio
import io
from queue import Queue
from dependencies import get_queue_key_judgment
from dependencies import get_queue_file_judgment

router = APIRouter()

async def get_image_from_cdn(cdn_url: str) -> bytes:
    async with httpx.AsyncClient() as client:
        response = await client.get(cdn_url)

    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="이미지를 가져오는데 실패했습니다.")

    return response.content

@router.get("/post/get-images/{POST_ID}/judge")
async def get_images(queue_key: Queue = Depends(get_queue_key_judgment), queue_file: Queue = Depends(get_queue_file_judgment)):
    data = queue_key.get()
    identifiers = data['image_identifiers']
    label = data['label']
    
    images = await asyncio.gather(*[get_image_from_cdn(cdn_url) for cdn_url in identifiers])
    
    image_data = { 
        "images": images,
        "label": label, 
    }
    queue_file.put(image_data)

    return StreamingResponse(io.BytesIO(images[0]), media_type="image/jpeg")