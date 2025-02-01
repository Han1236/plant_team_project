from typing import Union, List, Dict
from fastapi import FastAPI, HTTPException
import yt_dlp
import os
import re
from pydantic import BaseModel
import requests
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

app = FastAPI()


# ==== 환경설정 ====
MODEL_SERVER_URL = "http://model-server:8001"

# ==== DB 연결 정보 설정 ====
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:mypassword@db:5432/mydatabase")

# ==== DB 연결 설정 ====
engine = create_async_engine(DATABASE_URL, echo=True, future=True)
AsyncSessionLocal = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session

@app.get("/health")
async def health():
    async with AsyncSessionLocal() as session:
        result = await session.execute("SELECT version();")
        version = result.fetchone()[0]
    return {"status": "ok", "db_version": version}

@app.get("/")
def index():
    return {"message": "Hello from FastAPI with PostgreSQL!"}


# ==== 데이터 모델 정의 ====
class VideoRequest(BaseModel):
    video_url: str

class TextRequest(BaseModel):
    prompt: str

class QnARequest(BaseModel):
    prompt: str
    history: List[Dict[str, str]] = []  # [{"role": "user"/"assistant", "content": "..."}]

# ==== 전역 변수 ====
processed_videos = {}  # 캐싱 용도 (실제 운영에서는 Redis/Memcached/DB 등 사용 고려)

# ==== 유튜브 자막 처리 ====
# SUBTITLE_DIR = "/app/data/subtitles"

# ==== 유틸 함수 ====
def get_video_info_and_subtitles(video_url: str):
    """
    yt-dlp를 이용해 유튜브 영상 정보를 추출하고,
    한글 자막(ko)이 있으면 VTT 파일을 읽어 텍스트로 정제해 반환합니다.
    """
    opts = {
        "writesubtitles": True,           # 자막 다운로드
        "writeautomaticsub": True,        # 자동 자막 다운로드
        "skip_download": True,            # 비디오 다운로드는 하지 않음
        "subtitlesformat": "vtt",         # 자막 형식
        "outtmpl": "%(id)s.%(ext)s",      # 영상 ID로 파일명 지정
        "subtitleslangs": ["ko"],         # 한국어 자막만 다운로드
    }

    try:
        with yt_dlp.YoutubeDL(opts) as yt:
            # 영상 정보 추출
            info = yt.extract_info(video_url, download=False)
            video_title = info.get('title', None)

            if video_title:
                # 영상 ID를 기반으로 파일명을 지정
                video_id = info.get('id', '')
                subtitle_file = f"{video_id}.ko.vtt"
                print(f"다운로드된 자막 파일 경로: {subtitle_file}")

                # 자막 다운로드
                yt.download([video_url])

                # 자막 파일이 존재하면 텍스트 추출
                if os.path.exists(subtitle_file):
                    with open(subtitle_file, "r", encoding="utf-8") as f:
                        content = f.read()

                    # 1. 'WEBVTT' 또는 'Kind' 같은 메타데이터 제거
                    # 2. 타임스탬프 및 HTML 태그 제거
                    clean_content = re.sub(r'WEBVTT.*?Kind.*?Language.*?\n', '', content, flags=re.DOTALL)  # 메타데이터 제거
                    clean_content = re.sub(r'<.*?>', '', clean_content)  # <c> 태그 및 HTML 태그 제거
                    clean_content = re.sub(r'<\d{2}:\d{2}:\d{2}\.\d{3}>', '', clean_content)  # 타임스탬프 제거
                    clean_content = re.sub(r'\d{2}:\d{2}:\d{2}\.\d{3} --> \d{2}:\d{2}:\d{2}\.\d{3}', '', clean_content)  # 타임스탬프 형식 제거

                    # 3. 'align:start position:0%' 제거
                    clean_content = re.sub(r'align:start position:\d+%', '', clean_content)  # align:start 제거

                    # 4. 중복된 자막 제거 (텍스트가 반복되면 중복된 부분 제거)
                    clean_content = "\n".join(sorted(set(clean_content.splitlines()), key=lambda x: clean_content.index(x)))

                    # 자막 내용 정리(불필요한 줄이나 빈 줄 제거)
                    clean_content = "\n".join([line.strip() for line in clean_content.splitlines() if line.strip()])

                    return info, clean_content
                else:
                    # 자막이 없는 경우 처리
                    return info, "자막이 없습니다."
        
            else:
                    # 영상 정보가 없을 경우
                    return None, "영상 정보를 찾을 수 없습니다."
    except Exception as e:
        print(f"오류 발생: {e}")
        return None, None

def generate_markdown_timeline(chapters):
    """
    yt-dlp가 추출한 'chapters' 정보를 바탕으로 Markdown 형식 타임라인을 생성
    """
    if not chapters:
        return "타임라인 정보가 없습니다."
    markdown_text = "#### 영상 타임라인\n"
    for ch in chapters:
        start_time = f"{int(ch['start_time']) // 60}:{int(ch['start_time']) % 60:02d}"
        end_time = f"{int(ch['end_time']) // 60}:{int(ch['end_time']) % 60:02d}"
        markdown_text += f"**{start_time} ~ {end_time}**\n"
        markdown_text += f"{ch['title']}\n\n"
    return markdown_text

# ==== 엔드포인트 ====

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "web_server is running"}

@app.post("/video_info")
def get_video_info(request: VideoRequest):
    """
    1) 유튜브 영상의 기본 정보, 자막을 추출하여 반환
    2) 이미 처리된 url이면 cached data 반환
    """
    video_url = request.video_url

    # 이미 처리된 URL인지 확인
    if video_url in processed_videos:
        return processed_videos[video_url] # 이미 처리된 결과 반환

    # 새로 처리하는 경우
    info, clean_subtitle = get_video_info_and_subtitles(video_url)
    if info is None:
        raise HTTPException(status_code=400, detail="영상 정보 추출 실패")

    result = {
        "title": info.get("title", ""),
        "channel": info.get("channel", ""),
        "view_count": info.get("view_count", 0),
        "upload_date": info.get("upload_date", ""),
        "duration_string": info.get("duration_string", ""),
        "timeline": generate_markdown_timeline(info.get('chapters')) if 'chapters' in info else "타임라인 정보가 없습니다.",
        "subtitle": clean_subtitle
    }
    processed_videos[video_url] = result
    return result

@app.post("/summarize")  # 요약
def summarize(request: TextRequest):
    """
    웹 서버에서는 model-server에 요약 요청을 보냄
    """
    try:
        payload = {"text": request.prompt}  # model_server의 SummarizeRequest(text)와 맞춤
        response = requests.post(f"{MODEL_SERVER_URL}/summarize", json=payload, timeout=30)
        response.raise_for_status()
        return response.json()  # {"summary": "..."}
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=str(e))

@app.post("/chat")  # 챗/QnA
def qna(request: QnARequest):
    """
    웹 서버에서 model-server에 챗 요청을 보냄 (히스토리 포함)
    """
    print("Received request:", request.dict())  # 요청 데이터 로그 출력
    try:
        payload = {
            "prompt": request.prompt,
            "history": request.history  # [{"role":..., "content":...}, ...]
        }
        response = requests.post(f"{MODEL_SERVER_URL}/chat", json=payload, timeout=30)
        response.raise_for_status()
        return response.json()  # {"response": "..."}
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
