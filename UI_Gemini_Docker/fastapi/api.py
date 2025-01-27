from typing import Union, List, Dict
from fastapi import FastAPI
import yt_dlp
import os
import re
import google.generativeai as genai
from pydantic import BaseModel
from gemini_api import gen_text, gen_chat
from langchain_community.chat_message_histories import ChatMessageHistory

app = FastAPI()

# 요청을 받을 모델 정의
class TextRequest(BaseModel):
    prompt: str

class VideoRequest(BaseModel):
    video_url: str

class QnARequest(BaseModel):
    prompt: str
    history: List[Dict[str, str]]

# 이미 처리된 비디오 URL을 저장하는 전역 변수 (또는 Redis 사용)
processed_videos = {}

# 유튜브 비디오 정보 및 자막 다운로드 함수
def get_video_info_and_subtitles(video_url: str):
    opts = {
        'writesubtitles': True,  # 첨부된 자막 다운로드
        'writeautomaticsub': True,  # 자동 생성된 자막 다운로드
        'skip_download': True,  # 비디오 다운로드 안 함
        'subtitlesformat': 'vtt',  # 자막 형식
        'outtmpl': '%(title)s',  # 영상 제목을 파일명으로 사용
        'subtitleslangs': ['ko'],  # 다운로드할 자막 언어 (한국어)
    }
    
    try:
        with yt_dlp.YoutubeDL(opts) as yt:
            info = yt.extract_info(video_url, download=False)
            video_title = info.get('title', None)
            
            if video_title:
                sanitized_title = re.sub(r'[\\/*?:"<>|]', "", video_title)
                yt.download([video_url])
                subtitle_file = f'{sanitized_title}.ko.vtt'
                
                # 자막 파일이 존재하면 텍스트 추출
                if os.path.exists(subtitle_file):
                    with open(subtitle_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    # 자막 내용 정리(메타데이터와 타임스탬프, 자막 번호를 제거)
                    clean_content = "\n".join([line for line in content.splitlines() if '-->' not in line and not line.strip().isdigit() 
                                               and not line.startswith("WEBVTT") 
                                               and not line.startswith("Kind:") 
                                               and not line.startswith("Language:")])
                    return info, clean_content
                else:
                    # 자막이 없을 경우 처리 (첨부된 자막, 자동 생성된 자막이 없는 경우)
                    return info, "자막이 없습니다."
            else:
                # 영상 정보가 없을 경우
                return None, "영상 정보를 찾을 수 없습니다."
    except Exception as e:
        return None, None
    
def generate_markdown_timeline(chapters):
    """
    주어진 chapters 데이터를 바탕으로 Markdown 형식의 영상 타임라인을 생성합니다.
    """
    markdown_text = "#### 영상 타임라인\n"
    for chapter in chapters:
        start_time = f"{int(chapter['start_time']) // 60}:{int(chapter['start_time']) % 60:02d}"
        end_time = f"{int(chapter['end_time']) // 60}:{int(chapter['end_time']) % 60:02d}"
        markdown_text += f":blue-background[**{start_time} ~ {end_time}**]\n"
        markdown_text += f"{chapter['title']}\n\n"
    return markdown_text

# 영상 정보와 자막을 처리하는 엔드포인트
@app.post("/api/video_info/")
def get_video_info(request: VideoRequest):
    video_url = request.video_url
    # 이미 처리된 URL인지 확인
    if video_url in processed_videos:
        return processed_videos[video_url]  # 이미 처리된 결과 반환
    
    # 새로 처리하는 경우
    info, clean_transcript = get_video_info_and_subtitles(video_url)
    
    if info:
        result = {
            "title": info["title"],
            "channel": info["channel"],
            "view_count": info.get("view_count", 0),
            "upload_date": info.get("upload_date", ""),
            "duration_string": info.get("duration_string", ""),
            "timeline": generate_markdown_timeline(info.get('chapters')) if 'chapters' in info else "타임라인 정보가 없습니다.",
            "subtitle": clean_transcript
        }
        # 처리된 URL 결과 캐시
        processed_videos[video_url] = result
        
        return result
    else:
        return {"error": "자막 다운로드 또는 영상 정보 추출에 실패했습니다."}

# 텍스트 요약 요청을 받는 엔드포인트
@app.post("/api/gemini/")
def summarize(request: TextRequest):
    return {"summary": gen_text(request.prompt)}

# 챗봇 질의응답 요청을 받는 엔드포인트
@app.post("/api/qna/")
def qna(request: QnARequest):
    history = ChatMessageHistory()
    for msg in request.history:
        if msg['role'] == 'user':
            history.add_user_message(msg['content'])
        elif msg['role'] == 'assistant':
            history.add_ai_message(msg['content'])
            
    response = gen_chat(request.prompt, history)
    return {"response": response}