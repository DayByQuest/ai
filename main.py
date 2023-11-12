from fastapi import FastAPI
from dotenv import load_dotenv
load_dotenv()


from routers.classify_creation import router as classify_creation
from routers.classify_judgment import router as classify_judgment
from routers.get_image_creation import router as get_image_creation
from routers.get_image_judgment import router as get_image_judgment
from routers.receive_info_creation import router as receive_info_creation
from routers.receive_info_judgment import router as receive_info_judgment

app = FastAPI()

app.include_router(classify_creation)
app.include_router(classify_judgment)
app.include_router(get_image_creation)
app.include_router(get_image_judgment)
app.include_router(receive_info_creation)
app.include_router(receive_info_judgment)


@app.get("/")
async def root():
    return {"message": "Hello Bigger Applications!"}

