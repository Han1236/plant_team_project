from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from schemas.requests import QnARequest
from services.model_service import stream_chat
import json
import traceback
import asyncio
import logging

# 로그 설정
logging.basicConfig(level=logging.DEBUG) # 로그 레벨 설정 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
logger = logging.getLogger(__name__) # 현재 모듈에 대한 로거 생성


router = APIRouter(tags=["Chat"])

@router.post("/chat/stream")
async def chat_stream(request: QnARequest):
    """모델과의 스트리밍 채팅을 처리합니다."""
    try:
        if not request.query:
            raise HTTPException(status_code=400, detail="Query is required.")
        
        async def generate():
            async for chunk in stream_chat(request.query, request.video_id):
                # logger.info(f"[WEB] 모델 서버에서 받은 원본 chunk: {chunk}")
                yield chunk
        
        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            }
        )
    except Exception as e:
        logger.error(f"[WEB] 스트리밍 채팅 오류: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))