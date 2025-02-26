from fastapi import APIRouter, HTTPException
from schemas.requests import VideoRequest, PlaylistRequest
from services.youtube_service import process_video_url, process_playlist
# from utils.youtube_utils import get_videos_from_playlist, format_view_count
# from schemas.responses import PlaylistVideosResponse

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
    
# @router.get("/playlist_videos", response_model=PlaylistVideosResponse)
# def get_playlist_videos(playlist_url: str = Query(..., description="유튜브 플레이리스트 URL")):
#     """유튜브 플레이리스트에서 비디오 목록을 가져옵니다."""
#     videos_info = get_videos_from_playlist(playlist_url, playlist_start=0, playlist_end=6)
#     if not videos_info:
#         raise HTTPException(status_code=404, detail="플레이리스트에서 비디오 정보를 가져오는데 실패했습니다.")
    
#     videos = []
#     for video_info in videos_info:
#         thumbnails = video_info.get("thumbnails", [])
#         thumbnail_url = thumbnails[-1]["url"] if thumbnails else None
#         duration = video_info.get("duration", 0)
#         formatted_duration = f"{duration // 60:02}:{duration % 60:02}"
#         formatted_count = format_view_count(video_info.get("view_count", 0))
        
#         videos.append({
#             "title": video_info["title"],
#             "url": video_info["url"],
#             "thumbnail_url": thumbnail_url,
#             "formatted_duration": formatted_duration,
#             "view_count": video_info.get("view_count", 0),
#             "formatted_view_count": formatted_count,
#         })
    
#     return PlaylistVideosResponse(videos=videos)