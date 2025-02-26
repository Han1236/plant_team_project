import streamlit as st
import json
import time
import requests
from utils.api import chat_stream_with_api
from config import WEB_SERVER_URL

st.set_page_config(page_title="QnA", page_icon="❓")

st.title("❓ 영상 내용 질문하기")

st.write("""
영상 내용에 대해 궁금한 점을 자유롭게 질문해보세요.
AI가 자막을 분석하여 답변을 제공합니다.
""")

# 채팅 기록 초기화
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# QnA 가능한 영상 목록 표시
st.subheader("QnA 가능한 영상 목록")
try:
    response = requests.get(f"{WEB_SERVER_URL}/chromadb_videos")
    if response.status_code == 200:
        videos = response.json()
        if videos:
            # 리스트를 3열로 정렬하여 표시
            cols = st.columns(3)
            for i, video in enumerate(videos):
                with cols[i % 3]:
                    if st.button(f"{video['title']}", key=f"video_button_{video['video_id']}"):
                        st.session_state.video_info = {
                            "video_id": video['video_id'],
                            "title": video['title']
                        }
                        st.session_state.chat_history = []
                        st.rerun()
        else:
            st.info("아직 QnA 가능한 영상이 없습니다. '자막 추출' 페이지에서 영상을 선택하고 ChromaDB를 생성해보세요.")
            st.stop()
    else:
        st.error("QnA 가능한 영상 목록을 불러오는데 실패했습니다.")
        st.stop()
except Exception as e:
    st.error(f"오류 발생: {str(e)}")
    st.stop()

# 세션 상태 확인
if "video_info" not in st.session_state:
    st.warning("위의 영상 목록에서 질문할 영상을 선택해주세요.")
    st.stop()

video_id = st.session_state.video_info.get("video_id", "")
video_title = st.session_state.video_info.get("title", "")

# 메시지 컨테이너
st.subheader(f"'{video_title}' 영상에 대해 질문하기")
messages_container = st.container()

# 채팅 기록 표시
with messages_container:
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])

# 질문 입력
with st.form("chat_form", clear_on_submit=True):
    prompt = st.text_input("질문을 입력하세요:", key="user_input")
    submitted = st.form_submit_button("질문하기")

# 사용자가 질문을 제출했을 때
if submitted and prompt:
    # 사용자 메시지 추가
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    
    # 사용자 메시지 표시
    with st.chat_message("user"):
        st.write(prompt)
    
    # AI 응답 생성 및 표시
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        # 실제 스트리밍 응답 처리
        with st.spinner("응답 생성 중..."):
            for chunk in chat_stream_with_api(prompt, video_id, streaming=True):
                full_response += chunk
                message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
    
    # AI 메시지 추가
    st.session_state.chat_history.append({"role": "assistant", "content": full_response})

# 채팅 기록 초기화 버튼
if st.button("대화 기록 초기화"):
    st.session_state.chat_history = []
    st.rerun()