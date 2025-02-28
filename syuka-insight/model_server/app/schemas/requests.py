from pydantic import BaseModel

class SummarizeRequest(BaseModel):
    timeline: str
    subtitle: str

class ChatHistoryRequest(BaseModel):
    query: str
    video_id: str

class CreateChromaDBRequest(BaseModel):
    video_id: str
    subtitle: str
    title: str