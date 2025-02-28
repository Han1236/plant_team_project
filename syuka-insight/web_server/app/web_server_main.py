from fastapi import FastAPI
from routes import youtube, summarize, chat, chromadb
import os
from dotenv import load_dotenv
from models.database import engine, Base

# 환경 변수 로드
load_dotenv()
MODEL_SERVER_URL = os.getenv("MODEL_SERVER_URL", "http://model-server:8001")

# FastAPI 앱 생성
app = FastAPI(title="Web Server for Video Processing and Model API")

# 라우터 등록
app.include_router(youtube.router)
app.include_router(summarize.router)
app.include_router(chat.router)
app.include_router(chromadb.router)

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "web_server is running"}

@app.on_event("startup")
async def startup():
    # 데이터베이스 테이블 생성
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)