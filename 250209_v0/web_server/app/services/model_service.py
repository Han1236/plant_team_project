import requests
import json
import os
from fastapi import HTTPException
import aiohttp

MODEL_SERVER_URL = os.getenv("MODEL_SERVER_URL", "http://model-server:8001")

def summarize_text(timeline: str, subtitle: str):
    """텍스트 요약을 모델 서버에 요청합니다."""
    try:
        # 요약 요청 페이로드 구성
        payload = {
            "timeline": timeline,
            "subtitle": subtitle
        }

        # 모델 서버에 요청
        response = requests.post(f"{MODEL_SERVER_URL}/summarize", json=payload, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=str(e))
    
async def stream_chat(query: str, video_id: str):
    """모델과의 스트리밍 채팅을 처리합니다."""
    try:
        # 요청 페이로드 구성
        payload = {
            "query": query,
            "video_id": video_id
        }

        # 모델 서버에 요청
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{MODEL_SERVER_URL}/chat/stream", 
                json=payload, 
                timeout=60
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise HTTPException(status_code=response.status, detail=error_text)
                
                # 모델 서버로부터 받은 스트리밍 응답을 그대로 클라이언트에 전달
                async for chunk in response.content:
                    if chunk:
                        yield chunk.decode('utf-8')
    except Exception as e:
        yield f"data: 오류가 발생했습니다: {str(e)}\n\n"

# async def chat_stream_with_model(prompt: str, video_id: str):
#     """모델과의 스트리밍 채팅을 처리합니다."""
#     try:
#         # 요청 페이로드 구성
#         payload = {
#             "prompt": prompt,
#             "video_id": video_id
#         }

#         # 스트리밍 응답을 위한 비동기 요청
#         async with aiohttp.ClientSession() as session:
#             async with session.post(
#                 f"{MODEL_SERVER_URL}/chat/stream", 
#                 json=payload, 
#                 timeout=60
#             ) as response:
#                 if response.status != 200:
#                     error_text = await response.text()
#                     raise HTTPException(status_code=response.status, detail=error_text)
                
#                 # 스트리밍 응답 처리
#                 async for chunk in response.content.iter_any():
#                     if chunk:
#                         text = chunk.decode('utf-8')
#                         if text.startswith('data: '):
#                             text = text.replace('data: ', '', 1)
#                             if text.strip() == '[DONE]':
#                                 break
#                             yield text
#     except Exception as e:
#         raise HTTPException(status_code=502, detail=str(e))