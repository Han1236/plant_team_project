from pydantic import BaseModel
from typing import Optional

class VideoRequest(BaseModel):
    video_url: str

class TextRequest(BaseModel):
    summary_info: str

class ChromaDBRequest(BaseModel):
    video_id: str
    title: str
    subtitle: str

class QnARequest(BaseModel):
    query: str
    video_id: str

class PlaylistRequest(BaseModel):
    playlist_url: str
    start: int 
    end: int