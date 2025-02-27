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
                logger.info(f"[WEB] 모델 서버에서 받은 원본 chunk: {chunk}")
                yield chunk

            #     if chunk.startswith('data: '):  # 이미 data: 가 포함된 경우
            #         logger.info(f"[WEB] data: 포함된 chunk 그대로 전달: {chunk}")
            #         yield chunk
            #     else:  # data: 가 없는 경우, 개행문자를 HTML <br> 태그로 변환
            #         formatted_chunk = chunk.replace('\n\n', '<br><br>')
            #         formatted_chunk = formatted_chunk.replace('\n', ' ')
            #         logger.info(f"[WEB] 변환 후 전송할 chunk: data: {formatted_chunk}\n\n")
            #         yield f"data: {formatted_chunk}\n\n"
            
            # logger.info("[WEB] 스트리밍 종료 신호 전송")
            # yield "data: [DONE]\n\n"
        
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

# @router.post("/chat/stream")
# async def chat_stream(request: QnARequest):
#     try:
#         async def generate():
#             async for chunk in chat_stream_with_api(query, video_id):
#                 # 개행문자를 HTML <br> 태그로 변환
#                 formatted_chunk = chunk.replace('\n', '<br>')
#                 yield f"data: {formatted_chunk}\n\n"
#             yield "data: [DONE]\n\n"
        
#         return StreamingResponse(
#             generate(),
#             media_type="text/event-stream"
#         )
#     except Exception as e:
#         logger.error(f"스트리밍 채팅 오류: {str(e)}")
#         logger.error(traceback.format_exc())
#         raise HTTPException(status_code=500, detail=str(e))