from pydantic import BaseModel
from typing import Optional

class VideoRequest(BaseModel):
    video_url: str

# class PlaylistVideosRequest(BaseModel):
#     playlist_url: str

class TextRequest(BaseModel):
    prompt: str

class ChromaDBRequest(BaseModel):
    video_id: str
    title: str
    subtitle: str

class QnARequest(BaseModel):
    prompt: str
    video_id: str

class PlaylistRequest(BaseModel):
    playlist_url: str
    start: int 
    end: int

# class ChatHistoryRequest(BaseModel):
#     prompt: str
#     video_id: str