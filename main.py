from fastapi import FastAPI
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
import os

load_dotenv()

from routers.judgment import router as total_judge
from routers.creation import router as total_shot

BACKEND_URL = os.getenv('BACKEND_URL')  

origins = [
    BACKEND_URL
]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(total_judge)
app.include_router(total_shot)

@app.get("/")
async def root():
    return {"DayByQuest. The default page."}