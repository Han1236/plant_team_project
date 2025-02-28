from fastapi import APIRouter, HTTPException
from schemas.requests import VideoRequest, PlaylistRequest
from services.youtube_service import process_video_url, process_playlist

router = APIRouter(tags=["Youtube"])

# 전역 캐시
processed_videos = {}

@router.post("/video/info")
def get_video_info(request: VideoRequest):
    """유튜브 비디오 정보와 자막을 가져옵니다."""
    try:
        video_url = request.video_url
        if video_url in processed_videos:
            return processed_videos[video_url]
        else:
            result = process_video_url(video_url)
            processed_videos[video_url] = result
            return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/playlist_videos")
def get_playlist_info(request: PlaylistRequest):
    """유튜브 플레이리스트 정보를 가져옵니다."""
    try:
        return process_playlist(request.playlist_url, request.start, request.end)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))