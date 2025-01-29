import streamlit as st
import requests

# 페이지 설정
st.set_page_config(
    page_title="웹 검색 챗봇",
    page_icon="🤖",
)

st.write("# 웹 검색을 포함한 챗봇")

WEB_SERVER_URL = "http://localhost:8000"

user_input = st.text_input("질문 입력")
if st.button("전송"):
    response = requests.post(f"{WEB_SERVER_URL}/chat", json={"message": user_input})
    st.write("응답:")
    st.write(response.json().get("response", "응답 실패"))