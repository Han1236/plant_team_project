from utils.youtube_utils import (
    get_video_info_and_subtitles,
    generate_markdown_timeline,
    get_videos_from_playlist,
    format_view_count,
    format_upload_date
)
from schemas.responses import VideoInfoResponse, PlaylistResponse

def process_video_url(video_url: str):
    """비디오 URL을 처리하여 정보와 자막을 반환합니다."""
    info, clean_subtitle = get_video_info_and_subtitles(video_url)
    
    if not info:
        return {"error": "영상 정보를 가져오는데 실패했습니다."}

    result = {
        "video_id": info.get("id", ""),
        "title": info.get("title", ""),
        "channel": info.get("channel", ""),
        "view_count": info.get("view_count", 0),
        "upload_date": format_upload_date(info.get("upload_date", "")),
        "duration_string": info.get("duration_string", ""),
        "timeline": generate_markdown_timeline(info.get("chapters")) if "chapters" in info else "타임라인 정보가 없습니다.",
        "subtitle": clean_subtitle,
    }
    
    # 응답 데이터 준비
    return VideoInfoResponse(**result)

def process_playlist(playlist_url: str, start: int, end: int):
    """플레이리스트 URL을 처리하여 비디오 목록을 반환합니다."""
    videos_info = get_videos_from_playlist(playlist_url, start, end) # start=0, end=6 기본값

    if not videos_info:
        return {"error": "플레이리스트 정보를 가져오는데 실패했습니다."}
    
    videos = []
    for video_info in videos_info:
        thumbnails = video_info.get("thumbnails", [])
        thumbnail_url = thumbnails[-1]["url"] if thumbnails else None
        duration = video_info.get("duration", 0)
        formatted_duration = f"{duration // 60:02}:{duration % 60:02}"
        formatted_view_count = format_view_count(video_info["view_count"])

        videos.append(
            {
                "title": video_info["title"],
                "url": video_info["url"],
                "thumbnail_url": thumbnail_url,
                "formatted_duration": formatted_duration,
                "view_count": video_info["view_count"],
                "formatted_view_count": formatted_view_count,
            }
        )

    # 응답 데이터 준비
    return PlaylistResponse(videos=videos)