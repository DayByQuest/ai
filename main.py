from fastapi import FastAPI
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
import os
import uvicorn
from uvicorn.config import LOGGING_CONFIG
from dependencies import get_model

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

if __name__ == '__main__':
    get_model()
    DATE_FMT = "%Y-%m-%d %H:%M:%S"
    LOGGING_CONFIG["formatters"]["access"]["fmt"] = '%(asctime)s [%(levelname)s] [%(filename)s] [%(process)d] %(client_addr)s - "%(request_line)s" %(status_code)s'
    LOGGING_CONFIG["formatters"]["default"]["fmt"] = "%(asctime)s [%(levelname)s] [%(filename)s] - %(message)s"
    LOGGING_CONFIG["formatters"]["default"]["datefmt"] = DATE_FMT
    LOGGING_CONFIG["formatters"]["access"]["datefmt"] = DATE_FMT

    uvicorn.run("main:app", host="0.0.0.0")