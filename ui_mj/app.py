import streamlit as st
import requests

WEB_SERVER_URL = "http://web-server:8000"

st.title("자막 요약 및 챗봇")

option = st.selectbox("기능 선택", ["자막 요약", "챗봇"])

if option == "자막 요약":
    uploaded_file = st.file_uploader("자막 파일 업로드", type=["txt", "srt"])
    if uploaded_file:
        try:
            response = requests.post(
                f"{WEB_SERVER_URL}/summarize_file",
                files={"file": uploaded_file}
            )
            if response.status_code == 200:
                data = response.json()
                st.write(data.get("summary", "요약 실패"))
            else:
                st.error(f"요청 실패: 상태 코드 {response.status_code}")
                st.write(response.text)  # 디버깅용: 응답 내용 출력
        except requests.exceptions.RequestException as e:
            st.error(f"서버 요청 중 오류 발생: {e}")
        except requests.exceptions.JSONDecodeError:
            st.error("서버에서 올바른 JSON 응답을 받지 못했습니다.")
    
    # if uploaded_file is not None:
    #     content = uploaded_file.read().decode("utf-8")
    #     response = requests.post(f"{WEB_SERVER_URL}/summarize_file", files={"file": uploaded_file})
    #     st.write("요약 결과:")
    #     st.write(response.json().get("summary", "요약 실패"))
elif option == "챗봇":
    user_input = st.text_input("질문 입력")
    if st.button("전송"):
        response = requests.post(f"{WEB_SERVER_URL}/chat", json={"message": user_input})
        st.write("응답:")
        st.write(response.json().get("response", "응답 실패"))
