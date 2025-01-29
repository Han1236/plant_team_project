# import streamlit as st
# import random
# import time

# # 페이지 설정
# st.set_page_config(
#     page_title="QnA 서비스",
#     page_icon="❓",
# )

# # 제목과 서브헤더
# st.write("# QnA 서비스")
# st.write("")
# st.subheader("챗봇과 대화를 시작합니다😊")

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

# from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel
# import requests

# app = FastAPI()

# # Define request and response schemas
# class Question(BaseModel):
#     text: str

# class Answer(BaseModel):
#     answer: str

# # Endpoint to ask a question to the Gemini model
# @app.post("/ask", response_model=Answer)
# def ask_question(question: Question):
#     try:
#         # Example: Sending a request to Gemini model server
#         model_server_url = "http://model-server:8001/generate"
#         payload = {"prompt": question.text}

#         response = requests.post(model_server_url, json=payload)
#         response.raise_for_status()

#         # Assuming the model server returns a JSON with a key 'response'
#         model_response = response.json()
#         return Answer(answer=model_response.get("response", "No response from model."))
#     except requests.exceptions.RequestException as e:
#         raise HTTPException(status_code=500, detail=f"Model server error: {e}")

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests

app = FastAPI()

# 데이터 모델 정의
class Question(BaseModel):
    text: str

class Answer(BaseModel):
    answer: str

# 모델 서버 URL
MODEL_SERVER_URL = "http://model-server:8001/generate"

# 질문 엔드포인트
@app.post("/ask", response_model=Answer)
def ask_question(question: Question):
    """
    질문을 받아 모델 서버로 요청을 보낸 뒤 응답을 반환합니다.
    """
    try:
        # 모델 서버로 요청 보내기
        payload = {"prompt": question.text}
        response = requests.post(MODEL_SERVER_URL, json=payload)
        response.raise_for_status()

        # 모델 서버 응답 처리
        model_response = response.json()
        answer_text = model_response.get("response", "No response from model.")
        return Answer(answer=answer_text)

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Model server error: {str(e)}")
