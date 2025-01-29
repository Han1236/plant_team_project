import streamlit as st
import requests

# 페이지 설정
st.set_page_config(
    page_title="자막 파일 업로드",
    page_icon="📜",
)

st.write("# 자막 업로드 및 요약")

WEB_SERVER_URL = "http://localhost:8000"

uploaded_file = st.file_uploader("자막 파일 업로드", type=["txt", "srt"])
if uploaded_file is not None:
    content = uploaded_file.read().decode("utf-8")
    response = requests.post(f"{WEB_SERVER_URL}/summarize_file", files={"file": uploaded_file})
    st.write("요약 결과:")
    st.write(response.json().get("summary", "요약 실패"))