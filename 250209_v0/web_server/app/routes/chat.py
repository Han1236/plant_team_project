from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from schemas.requests import QnARequest
from services.model_service import stream_chat
import json
import traceback
import asyncio
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Chat"])

@router.post("/chat/stream")
async def chat_stream(request: QnARequest):
    """모델과의 스트리밍 채팅을 처리합니다."""
    try:
        if not request.query:
            raise HTTPException(status_code=400, detail="Query is required.")
        
        # 직접 prompt와 video_id 사용
        return StreamingResponse(
            stream_chat(request.query, request.video_id),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            }
        )
    except Exception as e:
        logger.error(f"스트리밍 채팅 오류: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
    
    # try:
    #     # 프롬프트와 비디오 ID 파싱
    #     data = json.loads(request.prompt)
    #     prompt = data.get("prompt", "")
    #     video_id = data.get("video_id", "")
        
    #     async def generate():
    #         async for chunk in chat_stream_with_model(prompt, video_id):
    #             yield f"data: {chunk}\n\n"
    #         yield "data: [DONE]\n\n"
        
    #     return StreamingResponse(
    #         generate(),
    #         media_type="text/event-stream",
    #         headers={
    #             "Cache-Control": "no-cache",
    #             "Connection": "keep-alive",
    #             "X-Accel-Buffering": "no"
    #         }
    #     )
    # except Exception as e:
    #     print(f"Error in chat_stream: {str(e)}")
    #     print(traceback.format_exc())
    #     raise HTTPException(status_code=500, detail=str(e))