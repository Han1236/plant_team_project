from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from schemas.requests import ChatHistoryRequest
from services.rag_service import get_rag_response_stream
import traceback

router = APIRouter()

@router.post("/chat/stream")
async def chat_stream(req: ChatHistoryRequest):
    """스트리밍 채팅 응답을 제공합니다."""
    try:
        # 응답 스트림 변환 및 반환
        async def convert_to_sse():
            async for chunk in get_rag_response_stream(req.prompt, req.video_id):
                yield f"data: {chunk}\n\n"
            yield "data: [DONE]\n\n"
        
        return StreamingResponse(
            convert_to_sse(),
            media_type="text/event-stream"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# @router.post("/chat/stream")
# async def chat_stream(req: ChatHistoryRequest):
#     """QnA 스트리밍 요청 처리."""
#     try:
#         async def generate():
#             async for chunk in get_rag_response_stream(req.prompt, req.video_id):
#                 yield f"data: {chunk}\n\n"
#             yield "data: [DONE]\n\n"

#         return StreamingResponse(
#             generate(),
#             media_type="text/event-stream",
#             headers={
#                 "Cache-Control": "no-cache",
#                 "Connection": "keep-alive",
#                 "X-Accel-Buffering": "no"
#             }
#         )
#     except Exception as e:
#         print(f"Error in chat_stream: {str(e)}")
#         print(f"Error details: {traceback.format_exc()}")
#         raise HTTPException(status_code=500, detail=str(e))