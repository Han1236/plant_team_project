import requests
import json
from config import API_ENDPOINTS

def get_video_info(video_url):
    """YouTube 비디오 정보와 자막을 가져옵니다."""
    try:
        response = requests.post(
            API_ENDPOINTS["video_info"],
            json={"video_url": video_url}
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"서버 오류: {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}

def summarize_with_api(transcript_text, timeline_text):
    """자막과 타임라인을 요약합니다."""
    try:
        request_data = {
            "prompt": json.dumps({
                "timeline": timeline_text,
                "subtitle": transcript_text
            })
        }
        
        response = requests.post(
            API_ENDPOINTS["summarize"],
            json=request_data
        )
        
        if response.status_code == 200:
            return response.json().get("summary")
        else:
            return f"요약에 실패했습니다. 오류: {response.status_code}"
    except Exception as e:
        return f"요약에 실패했습니다. 오류: {str(e)}"

def chat_stream_with_api(prompt, video_id, streaming=True):
    """모델과 채팅합니다."""
    request_data = {
            "prompt": json.dumps({
                "prompt": prompt,
                "video_id": video_id
            })
        }
    
    endpoint = API_ENDPOINTS["chat_stream"]
    with requests.post(endpoint, json=request_data, stream=True) as response:
        if response.status_code == 200:
            # SSE 형식으로 응답 처리
            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith('data:'):
                        data = line[5:]
                        if data != "[DONE]":  # 스트림 종료 표시가 아니면 데이터 반환
                            yield data
        else:
            yield f"응답 실패. 오류: {response.status_code}"