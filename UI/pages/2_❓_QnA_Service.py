import streamlit as st
import requests
import os

# 웹 서버 URL 설정
WEB_SERVER_URL = os.getenv("WEB_SERVER_URL", "http://localhost:8000")

# 페이지 설정
st.set_page_config(
    page_title="QnA 서비스",
    page_icon="❓",
)

# 제목과 서브헤더
st.write("# QnA 서비스")
st.write("")
st.subheader("챗봇과 대화를 시작합니다😊")

# # 디버깅 로그
# print(f"DEBUG: WEB_SERVER_URL is set to {WEB_SERVER_URL}")

# 채팅 세션 초기화
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

# 이전 대화 표시
for chat in st.session_state.chat_history:
    role, message = chat
    with st.chat_message(role):
        st.markdown(message)

# 사용자 입력 처리
user_input = st.chat_input("질문을 입력하세요:")
if user_input:
    # 사용자 메시지 저장 및 표시
    st.session_state.chat_history.append(("user", user_input))
    with st.chat_message("user"):
        st.markdown(user_input)

    # 웹 서버 호출 및 응답 처리
    try:
        with st.spinner("Gemini 모델로부터 응답을 기다리고 있습니다..."):
            response = requests.post(
                f"{WEB_SERVER_URL}/chat",
                json={"prompt": user_input, "history": []},
                timeout=10  # 타임아웃 설정
            )
            response.raise_for_status()
            response_data = response.json()
            ai_response = response_data.get("response", "응답이 없습니다.")
    except requests.exceptions.RequestException as e:
        ai_response = f"웹 서버 호출 중 오류 발생: {str(e)}"

    # 모델 응답 저장 및 표시
    st.session_state.chat_history.append(("ai", ai_response))
    with st.chat_message("ai"):
        st.markdown(ai_response)
