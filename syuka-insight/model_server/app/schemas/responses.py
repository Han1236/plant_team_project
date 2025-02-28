from pydantic import BaseModel

class SummarizeResponse(BaseModel):
    summary: str

class ChatHistoryResponse(BaseModel):
    answer: str

class CreateChromaDBResponse(BaseModel):
    success: bool
    message: str = ""