from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class VideoInfoResponse(BaseModel):
    video_id: Optional[str] = None
    title: Optional[str] = None
    channel: Optional[str] = None
    view_count: Optional[int] = None
    upload_date: Optional[str] = None
    duration_string: Optional[str] = None
    timeline: Optional[str] = None
    subtitle: Optional[str] = None

class PlaylistResponse(BaseModel):
    videos: List[Dict[str, Any]]

class SummarizeResponse(BaseModel):
    summary: str