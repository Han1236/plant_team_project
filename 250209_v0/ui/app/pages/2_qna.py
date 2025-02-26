import streamlit as st
from utils.api import chat_stream_with_api
from utils.chat_utils import display_chat_message
from components.video_list import video_list_component
from utils.session import get_current_video


st.set_page_config(page_title="QnA", page_icon="❓", layout="wide")

st.header("😀챗봇 서비스")

st.write("""
영상에 대해 궁금한 점을 자유롭게 질문해보세요.
AI가 영상 내용을 기반으로 답변을 제공합니다.
""")

# # 채팅 기록 초기화
# if "chat_history" not in st.session_state:
#     st.session_state.chat_history = []

# QnA 가능한 영상 목록 표시
st.markdown("#### QnA 가능한 영상 목록")
video_list_component()

if "messages" not in st.session_state:
    st.session_state.messages = []

# 현재 선택된 비디오 가져오기
current_video_id = get_current_video()

for message in st.session_state.messages:
    display_chat_message(message["role"], message["content"])

# 선택된 비디오가 없으면 입력 비활성화
if not current_video_id:
    st.chat_input("QnA 가능한 영상 목록에서 영상을 선택해주세요.", disabled=True)
else:
    if query := st.chat_input("질문을 입력하세요:"):
        display_chat_message("user", query)
        # 사용자 메시지를 즉시 session_state에 추가
        st.session_state.messages.append({"role": "user", "content": query})

        with st.chat_message("assistant"):
            with st.spinner("메시지 처리 중입니다."):
                placeholder = st.empty()
                video_id = st.session_state["current_video_id"]
                
                # 스트리밍 응답 처리
                full_response = ""
                for response_chunk in chat_stream_with_api(query, video_id):
                    full_response += response_chunk
                    placeholder.markdown(full_response + "▌")
                placeholder.markdown(full_response)
                
                # 최종 응답을 세션에 저장
                st.session_state.messages.append({"role": "assistant", "content": full_response})

        st.rerun()