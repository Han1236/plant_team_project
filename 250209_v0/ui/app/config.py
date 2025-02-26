import os

# 환경 변수에서 웹 서버 URL 가져오기 (기본값 설정)
WEB_SERVER_URL = os.getenv("WEB_SERVER_URL", 
                           #"http://web-server:8000"
                           )

# 앱 설정
APP_TITLE = "슈카월드 AI 어시스턴트"
APP_ICON = "👋"

# API 엔드포인트
API_ENDPOINTS = {
    "video_info": f"{WEB_SERVER_URL}/video/info",
    "playlist_info": f"{WEB_SERVER_URL}/playlist/info",
    "summarize": f"{WEB_SERVER_URL}/summarize",
    "chat_stream": f"{WEB_SERVER_URL}/chat/stream",
    "playlist_videos": f"{WEB_SERVER_URL}/playlist_videos",
    "create_chromadb": f"{WEB_SERVER_URL}/create_chromadb",
    "chromadb_videos": f"{WEB_SERVER_URL}/chromadb_videos" 
}