# web-server/app/web-server.py
from typing import Union, List, Dict
from fastapi import FastAPI, HTTPException, Depends, File, UploadFile
from pydantic import BaseModel
import requests
import os
import httpx

# 기존 video_utils.py 함수 임포트 (영상 정보, 자막 처리)
from video_utils import (
    get_video_info_and_subtitles,
    generate_markdown_timeline,
    get_videos_from_playlist,
    format_view_count,
)

# SQLAlchemy 관련 임포트 (비동기)
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, String, Text, Date, DateTime, Float, BigInteger, ForeignKey
from datetime import datetime

# 웹 서버 앱 생성
app = FastAPI()

# 환경변수 설정 (Docker Compose에서 전달됨)
MODEL_SERVER_URL = os.getenv("MODEL_SERVER_URL", "http://localhost:8001")
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:mypassword@db:5432/mydatabase")

# DB 연결 설정
engine = create_async_engine(DATABASE_URL, echo=True, future=True)
AsyncSessionLocal = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
Base = declarative_base()

# ORM 모델 정의
class Video(Base):
    __tablename__ = "videos"
    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(String, unique=True, index=True, nullable=False)
    title = Column(Text)
    channel = Column(Text)
    upload_date = Column(Date)
    duration = Column(Integer)
    view_count = Column(BigInteger)
    created_at = Column(DateTime, default=datetime.utcnow)

class Subtitle(Base):
    __tablename__ = "subtitles"
    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(String, ForeignKey("videos.video_id"), nullable=False)
    start_time = Column(Float, nullable=False)
    end_time = Column(Float, nullable=False)
    subtitle_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

# DB 세션 의존성
async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session

# 요청 모델
class VideoRequest(BaseModel):
    video_url: str

class TextRequest(BaseModel):
    prompt: str

class QnARequest(BaseModel):
    prompt: str
    video_id: str

class ChromaDBRequest(BaseModel):
    video_id: str
    title: str
    subtitle: str

class PlaylistVideosRequest(BaseModel):
    playlist_url: str

class PlaylistVideosResponse(BaseModel):
    videos: List[Dict[str, Union[str, int]]]

# 전역 캐시
processed_videos = {}

# === DB 연동용 함수 ===
# DB에 영상 정보 및 자막을 저장하는 함수
async def save_video_info(db: AsyncSession, video_id: str, info: dict, subtitle: str):
    from sqlalchemy import select
    # videos 테이블에 영상 정보 저장
    result = await db.execute(select(Video).where(Video.video_id == video_id))
    video_obj = result.scalars().first()
    if not video_obj:
        try:
            upload_date = datetime.strptime(info.get("upload_date", ""), "%Y%m%d").date()
        except Exception:
            upload_date = None
        video_obj = Video(
            video_id=video_id,
            title=info.get("title", ""),
            channel=info.get("channel", ""),
            upload_date=upload_date,
            duration=int(info.get("duration", 0)),
            view_count=int(info.get("view_count", 0)),
        )
        db.add(video_obj)
        await db.commit()
    
    # subtitles 테이블에 자막 정보 저장
    if subtitle and subtitle.strip() and subtitle != "자막이 없습니다.":
        result = await db.execute(select(Subtitle).where(Subtitle.video_id == video_id))
        subtitle_obj = result.scalars().first()
        if not subtitle_obj:
            # 현재 자막 전체를 하나의 레코드로 저장합니다.
            # 만약 자막의 각 구간을 분리하여 저장하고 싶다면, VTT 파일을 파싱해 start_time과 end_time을 추출하는 로직이 필요(추후 진행예정)
            subtitle_obj = Subtitle(
                video_id=video_id,
                start_time=0,   # 기본값 
                end_time=0,     # 기본값 
                subtitle_text=subtitle
            )
            db.add(subtitle_obj)
            await db.commit()
    return


# === ChromaDB 연동 ===
# ChromaDB는 모델 서버에서 관리하므로, 여기서는 create_chromadb, chromadb_videos 등의 프록시 요청만 처리합니다.

# 엔드포인트: Health 체크 (DB 연결 포함)
@app.get("/health")
async def health(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute("SELECT version();")
        version = result.fetchone()[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB 연결 오류: {str(e)}")
    return {"status": "ok", "db_version": version, "message": "web_server is running"}

@app.get("/")
def index():
    return {"message": "Hello from FastAPI with Python!"}

# 엔드포인트: 영상 정보 요청 및 DB 저장
@app.post("/video_info")
async def get_video_info(request: VideoRequest, db: AsyncSession = Depends(get_db)):
    video_url = request.video_url
    if video_url in processed_videos:
        return processed_videos[video_url]

    info, clean_subtitle = get_video_info_and_subtitles(video_url)
    if info is None:
        raise HTTPException(status_code=400, detail="영상 정보 추출 실패")

    result = {
        "id": info.get("id", ""),
        "title": info.get("title", ""),
        "channel": info.get("channel", ""),
        "view_count": info.get("view_count", 0),
        "upload_date": info.get("upload_date", ""),
        "duration_string": info.get("duration_string", ""),
        "timeline": generate_markdown_timeline(info.get("chapters")) if "chapters" in info else "타임라인 정보가 없습니다.",
        "subtitle": clean_subtitle,
    }
    processed_videos[video_url] = result

    # DB에 저장 (영상 정보 및 자막)
    video_id = info.get("id") or info.get("url")
    await save_video_info(db, video_id, info, clean_subtitle)
    return result

# 엔드포인트: 요약 요청 (모델 서버 호출)
@app.post("/summarize")
def summarize(request: TextRequest):
    try:
        payload = {"text": request.prompt}
        response = requests.post(f"{MODEL_SERVER_URL}/summarize", json=payload, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=str(e))

# 엔드포인트: 챗 요청 (모델 서버 호출)
@app.post("/chat")
def qna(request: QnARequest):
    try:
        payload = {"prompt": request.prompt, "video_id": request.video_id}
        response = requests.post(f"{MODEL_SERVER_URL}/chat", json=payload, timeout=60)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# 엔드포인트: ChromaDB 관련 프록시 (모델 서버의 create_chromadb 호출)
@app.post("/create_chromadb")
def create_chromadb(request: ChromaDBRequest):
    try:
        payload = {"video_id": request.video_id, "title": request.title, "subtitle": request.subtitle}
        response = requests.post(f"{MODEL_SERVER_URL}/create_chromadb", json=payload, timeout=60)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=str(e))

@app.get("/chromadb_videos", response_model=List[Dict])
def get_chromadb_videos():
    try:
        response = requests.get(f"{MODEL_SERVER_URL}/chromadb_videos")
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Failed to get ChromaDB list: {str(e)}")

# 엔드포인트: 플레이리스트 비디오 목록 조회
@app.get("/playlist_videos", response_model=PlaylistVideosResponse)
def get_playlist_videos(playlist_url: str):
    videos_info = get_videos_from_playlist(playlist_url, playlist_start=0, playlist_end=6)
    if not videos_info:
        raise HTTPException(status_code=404, detail="플레이리스트에서 비디오 정보를 가져오는데 실패했습니다.")
    videos = []
    for video_info in videos_info:
        thumbnails = video_info.get("thumbnails", [])
        thumbnail_url = thumbnails[-1]["url"] if thumbnails else None
        duration = video_info.get("duration", 0)
        formatted_duration = f"{duration // 60:02}:{duration % 60:02}"
        formatted_count = format_view_count(video_info["view_count"])
        videos.append({
            "title": video_info["title"],
            "url": video_info["url"],
            "thumbnail_url": thumbnail_url,
            "formatted_duration": formatted_duration,
            "view_count": video_info["view_count"],
            "formatted_view_count": formatted_count,
        })
    return PlaylistVideosResponse(videos=videos)

def format_view_count(view_count):
    view_count = int(view_count)
    if view_count < 1000:
        return f"{view_count}회"
    elif view_count < 10000:
        thousands = view_count / 1000
        return f"{thousands:.1f}천회"
    else:
        mans = view_count / 10000
        return f"{int(mans)}만회"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

@app.on_event("startup")
async def on_startup():
    # 데이터베이스에 테이블이 없으면 모두 생성
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)