# web_server_main.py
from typing import Union, List, Dict, AsyncGenerator
from fastapi import FastAPI, HTTPException
import requests
from pydantic import BaseModel
import os
import httpx

# video_utils.py에서 제공하는 함수들 임포트
from video_utils import (
    get_video_info_and_subtitles,
    generate_markdown_timeline,
    get_videos_from_playlist,
    format_view_count,
)

app = FastAPI()

# ==== 환경설정 ====
MODEL_SERVER_URL = os.getenv("MODEL_SERVER_URL", "http://localhost:8001")

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "web_server is running"}

@app.get("/")
def index():
    return {"message": "Hello from FastAPI with Python!"}

# ==== 데이터 모델 ====
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

# ==== 전역 변수 ====
processed_videos = {}

# ==== 엔드포인트 ====

@app.post("/video_info")
def get_video_info(request: VideoRequest):
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
        "timeline": generate_markdown_timeline(info.get("chapters"))
        if "chapters" in info
        else "타임라인 정보가 없습니다.",
        "subtitle": clean_subtitle,
    }
    processed_videos[video_url] = result
    return result

@app.post("/summarize")
def summarize(request: TextRequest):
    try:
        payload = {"text": request.prompt}
        response = requests.post(f"{MODEL_SERVER_URL}/summarize", json=payload, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=str(e))

@app.post("/chat") 
def qna(request: QnARequest):
    """
    모델 서버에 QnA 요청을 보내고, 응답을 반환하는 엔드포인트 (Non-streaming)
    """
    # print("Received request:", request.model_dump()) # Received request 출력
    try:
        payload = {
            "prompt": request.prompt,
            "video_id": request.video_id
        }

        response = requests.post(f"{MODEL_SERVER_URL}/chat", json=payload, timeout=60)
        response.raise_for_status()
        return response.json()


    except requests.RequestException as e: # requests 예외 처리
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.post("/create_chromadb")
def create_chromadb(request: ChromaDBRequest):
    try:
        payload = {"video_id": request.video_id, "title": request.title, "subtitle":request.subtitle}
        response = requests.post(
            f"{MODEL_SERVER_URL}/create_chromadb", json=payload, timeout=60
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=str(e))


@app.get("/chromadb_videos", response_model=List[Dict])
def get_chromadb_videos():
    try:
        response = requests.get(f"{MODEL_SERVER_URL}/chromadb_videos")
        response.raise_for_status()

        chromadb_list = response.json()
        return chromadb_list

    except requests.RequestException as e:
        raise HTTPException(
            status_code=502, detail=f"Failed to get ChromaDB list: {str(e)}"
        )

@app.get("/playlist_videos", response_model=PlaylistVideosResponse)
def get_playlist_videos(playlist_url: str):
    videos_info = get_videos_from_playlist(playlist_url, playlist_start=0, playlist_end=6)

    if not videos_info:
        raise HTTPException(
            status_code=404, detail="플레이리스트에서 비디오 정보를 가져오는데 실패했습니다."
        )

    videos = []
    for video_info in videos_info:
        thumbnails = video_info.get("thumbnails", [])
        thumbnail_url = thumbnails[-1]["url"] if thumbnails else None
        duration = video_info.get("duration", 0)
        formatted_duration = f"{duration // 60:02}:{duration % 60:02}"
        formatted_count = format_view_count(video_info["view_count"])

        videos.append(
            {
                "title": video_info["title"],
                "url": video_info["url"],
                "thumbnail_url": thumbnail_url,
                "formatted_duration": formatted_duration,
                "view_count": video_info["view_count"],
                "formatted_view_count": formatted_count,
            }
        )
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