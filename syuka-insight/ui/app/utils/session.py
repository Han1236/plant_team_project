import streamlit as st

def set_current_video(video_id):
    """현재 선택한 비디오 ID를 세션에 저장"""
    st.session_state["current_video_id"] = video_id
    st.session_state.messages = []

def get_current_video():
    """현재 선택한 비디오 ID를 반환"""
    return st.session_state.get("current_video_id", None)
