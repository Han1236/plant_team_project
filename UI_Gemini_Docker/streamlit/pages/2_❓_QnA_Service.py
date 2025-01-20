import streamlit as st
import random
import time
import requests

# 페이지 설정
st.set_page_config(
    page_title="QnA 서비스",
    page_icon="❓",
)

# 제목과 서브헤더
st.write("# QnA 서비스")
st.write("")
st.subheader("챗봇과 대화를 시작합니다😊")

# FastAPI 백엔드 엔드포인트
API_URL_QNA = "http://fastapi-backend:8000/api/qna/"

# Streamlit UI를 위한 챗봇 메시지 처리 함수
def display_chat_message(role, content):
    with st.chat_message(role):
        st.markdown(content)

# FastAPI 백엔드로 질의응답 요청하는 함수
def get_chatbot_response(prompt, chat_history):
    try:
        response = requests.post(API_URL_QNA, json={"prompt": prompt, "history": chat_history})
        if response.status_code == 200:
            return response.json().get("response", "응답이 없습니다.")
        else:
            st.error("백엔드에서 응답을 받지 못했습니다.")
            return "오류가 발생했습니다."
    except requests.exceptions.RequestException as e:
        st.error(f"백엔드 연결 오류: {e}")
        return "백엔드 연결 오류"

# 세션 상태에서 메시지 기록 확인
if "messages" not in st.session_state:
    st.session_state.messages = []

# 앱이 새로고침 될 때마다 이전 메시지 표시
for message in st.session_state.messages:
    display_chat_message(message["role"], message["content"])

# 사용자가 입력한 메시지 처리
if prompt := st.chat_input("질문을 입력하세요:"):
    # 사용자 메시지를 화면에 표시
    display_chat_message("user", prompt)
    # 사용자 메시지를 세션 상태에 저장 (대화 기록)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 백엔드에 질문을 보내고 응답을 받음
    with st.chat_message("assistant"):
        with st.spinner("메시지 처리 중입니다."):
            # 현재까지 대화 기록을 함께 보냄
            chat_history = [{"role": msg["role"], "content": msg["content"]} for msg in st.session_state.messages]
            response = get_chatbot_response(prompt, chat_history)
            
            # 응답 표시
            st.markdown(response)

    # 어시스턴트의 응답을 세션 상태에 저장 (대화 기록)
    st.session_state.messages.append({"role": "assistant", "content": response})













# ######################################################################
# # Streamed response emulator (응답을 일정 간격으로 보내는 기능)
# def response_generator():
#     response = random.choice(
#         [
#             "안녕하세요! 무엇을 도와드릴까요?",
#             "안녕하세요, 도와드릴 일이 있나요?",
#             "반갑습니다! 도움이 필요하신가요?",
#         ]
#     )
#     # 응답을 한 단어씩 띄우면서 반환 (실제 챗봇처럼 느리게 응답)
#     for word in response.split():
#         yield word + " "
#         time.sleep(0.05)

# # 세션 상태에서 메시지 기록 확인
# if "messages" not in st.session_state:
#         st.session_state.messages = [] # 세션 상태에 'messages'가 없으면 새로 생성
    
# # 앱이 새로고침 될 때마다 이전 메시지 표시
# for message in st.session_state.messages:
#     with st.chat_message(message["role"]): # 사용자/어시스턴트 역할에 맞춰 메시지 표시
#         st.markdown(message["content"])
    
# # 사용자가 입력한 메시지 처리
# if prompt := st.chat_input("Say somfething"):
#     # 사용자 메시지를 화면에 표시
#     with st.chat_message("user"):
#         st.markdown(prompt)
#     # 사용자 메시지를 세션 상태에 저장 (대화 기록)
#     st.session_state.messages.append({"role": "user", "content": prompt})
    
#     # 어시스턴트의 응답을 처리
#     with st.chat_message("assistant"):
#         with st.spinner("메시지 처리 중입니다."):
#             response = st.write_stream(response_generator())

#     # 어시스턴트의 응답을 세션 상태에 저장 (대화 기록)
#     st.session_state.messages.append({"role": "assistant", "content": response})
