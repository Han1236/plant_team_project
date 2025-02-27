import streamlit as st
from utils.api import get_chromadb_video_list
from utils.session import set_current_video

def video_list_component():
    """QnA 가능한 영상 목록을 출력하는 UI 컴포넌트"""

    video_db_list = get_chromadb_video_list()

    if not video_db_list:
        st.info("ChromaDB가 생성된 영상이 없습니다. '자막 추출 및 DB생성' 페이지에서 먼저 ChromaDB를 생성해주세요.")
        return

    for video_info in video_db_list:
        if st.button(video_info["title"], key=f"video_button_{video_info['video_id']}"):
            set_current_video(video_info["video_id"])
            st.success(f"'{video_info['title']}' 영상에 대한 질문을 시작하세요.")
