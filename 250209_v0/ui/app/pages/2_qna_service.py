# 2_qna_service.py
import streamlit as st
import requests
import os

st.set_page_config(
    page_title="QnA 서비스",
    page_icon="❓",
)

st.write("# QnA 서비스")
st.write("")
st.subheader("ChromaDB 기반 QnA 챗봇입니다 😊")

WEB_SERVER_URL = os.getenv("WEB_SERVER_URL", "http://localhost:8000")

def display_chat_message(role, content):
    with st.chat_message(role):
        st.markdown(content)

# --- QnA 요청 함수 (web_server API 호출) ---
def get_qna_response_from_api(prompt, video_id):
    """Web server API (/chat 엔드포인트) 를 호출하여 QnA 답변을 받아오는 함수."""
    payload = {
        "prompt": prompt,
        "video_id": video_id
    }
    
    try:
        with requests.post(
            f"{WEB_SERVER_URL}/chat/stream",
            json=payload,
            stream=True,
            headers={"Accept": "text/event-stream"}
        ) as response:
            if response.status_code == 200:
                for line in response.iter_lines(decode_unicode=True):
                    if line:
                        if line.startswith('data: '):
                            text = line[6:]  # 'data: ' 제거
                            if text == '[DONE]':
                                break
                            yield text
            else:
                st.error("QnA 답변을 받아오는데 실패했습니다.")
                yield "QnA 오류"
    except Exception as e:
        st.error(f"스트리밍 처리 중 오류 발생: {str(e)}")
        yield f"오류: {str(e)}"


def get_chromadb_video_list_from_api():
    try:
        response = requests.get(f"{WEB_SERVER_URL}/chromadb_videos")
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        st.error(f"ChromaDB 목록을 가져오는 데 실패했습니다: {e}")
        return []

st.subheader("QnA 가능한 영상 목록")
video_db_list = get_chromadb_video_list_from_api()

if not video_db_list:
    st.info("ChromaDB가 생성된 영상이 없습니다. '자막 추출 및 DB생성' 페이지에서 먼저 ChromaDB를 생성해주세요.")
else:
    for video_info in video_db_list:
        if st.button(
            video_info["title"], key=f"video_button_{video_info['video_id']}"
        ):
            st.session_state["current_video_id"] = video_info["video_id"]
            st.success(f"'{video_info['title']}' 영상에 대한 질문을 시작하세요.")
            st.session_state.messages = []

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    display_chat_message(message["role"], message["content"])

if (
    "current_video_id" not in st.session_state
    or not st.session_state["current_video_id"]
):
    st.chat_input("QnA 가능한 영상 목록에서 영상을 선택해주세요.", disabled=True)
else:
    if prompt := st.chat_input("질문을 입력하세요:"):
        display_chat_message("user", prompt)
        # 사용자 메시지를 즉시 session_state에 추가
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("assistant"):
            with st.spinner("메시지 처리 중입니다."):
                placeholder = st.empty()
                video_id = st.session_state["current_video_id"]
                
                # 스트리밍 응답 처리
                full_response = ""
                for response_chunk in get_qna_response_from_api(prompt, video_id):
                    full_response += response_chunk
                    placeholder.markdown(full_response + "▌")
                placeholder.markdown(full_response)
                
                # 최종 응답을 세션에 저장
                st.session_state.messages.append({"role": "assistant", "content": full_response})

        st.rerun()