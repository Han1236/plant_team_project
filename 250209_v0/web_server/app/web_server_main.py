from fastapi import FastAPI
from routes import youtube, summarize, chat, chromadb
import os
from dotenv import load_dotenv

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)