import streamlit as st
from utils.api import get_video_info

def youtube_url_input():
    """YouTube URL 입력 컴포넌트"""
    st.subheader("YouTube 영상 URL을 입력하세요")
    
    url = st.text_input(
        "YouTube URL",
        placeholder="Youtube 영상 URL을 입력하세요:(https://www.youtube.com/watch?v=...)",
        value=st.session_state['video_url']
    )
    
    submit_button = st.button("정보 가져오기")
    
    if submit_button and url:
        with st.spinner("YouTube 자막 및 정보를 가져오는 중..."):
            # API를 통해 비디오 정보 가져오기
            video_info = get_video_info(url)
            
            if video_info and "error" not in video_info:
                st.session_state.video_info = video_info
                st.success(f"'{video_info['title']}' 영상 정보를 가져왔습니다!")
                return True
            else:
                error_msg = video_info.get("error", "알 수 없는 오류가 발생했습니다.")
                st.error(f"오류: {error_msg}")
                return False
    
    return False