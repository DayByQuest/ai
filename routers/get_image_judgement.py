from fastapi import FastAPI, HTTPException
import boto3
from botocore.exceptions import NoCredentialsError

app = FastAPI()

# AWS 설정
AWS_ACCESS_KEY = "YOUR_AWS_ACCESS_KEY"
AWS_SECRET_KEY = "YOUR_AWS_SECRET_KEY"
BUCKET_NAME = "YOUR_BUCKET_NAME"
REGION_NAME = "YOUR_REGION_NAME"

# boto3 클라이언트 초기화
s3 = boto3.client('s3', region_name=REGION_NAME, aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY)

@app.get("/get-image/")
async def get_image_from_s3(file_key: str):
    try:
        file_byte_string = s3.get_object(Bucket=BUCKET_NAME, Key=file_key)["Body"].read()
        return {"file": file_byte_string}
    except NoCredentialsError:
        raise HTTPException(status_code=400, detail="Credentials not available")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 서버 실행: uvicorn 파일이름:app --reload
