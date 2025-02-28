from fastapi import FastAPI
from routes import health, summarize, chat, chromadb
import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError(
        "Google API Key가 설정되지 않았습니다. .env 파일에 GOOGLE_API_KEY=YOUR_API_KEY 를 설정해주세요."
    )

# FastAPI 앱 생성
app = FastAPI(title="Model Server for Gemini + LangChain")

# 라우터 등록
app.include_router(health.router)
app.include_router(summarize.router)
app.include_router(chat.router)
app.include_router(chromadb.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
