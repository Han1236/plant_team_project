import streamlit as st
from utils.api import get_video_info

def youtube_url_input():
    """YouTube URL 입력 컴포넌트"""
    st.subheader("YouTube 영상 URL을 입력하세요")
    
    # URL 입력 필드
    video_url = st.text_input(
        "자막 추출 후, 하단의 ChromaDB 생성 버튼을 클릭하면 QnA 서비스용 데이터가 생성됩니다.",
        value=st.session_state.get('video_url', ''),  # 세션에 저장된 URL 사용
        placeholder="https://www.youtube.com/watch?v=...",
        key="video_url_input"
    )
    
    # URL이 입력되면 세션 상태 업데이트
    if video_url:
        # URL이 변경되었을 때만 상태 업데이트
        if video_url != st.session_state.get('prev_video_url', ''):
            st.session_state['prev_video_url'] = video_url  # 이전 URL 업데이트
            
        st.session_state['video_url'] = video_url
        
        with st.spinner("YouTube 자막 및 정보를 가져오는 중..."):
            # API를 통해 비디오 정보 가져오기
            video_info = get_video_info(video_url)
            
            if video_info and "error" not in video_info:
                st.session_state.video_info = video_info
                st.success(f"'{video_info['title']}' 영상 정보를 가져왔습니다!")
                return True
            else:
                error_msg = video_info.get("error", "알 수 없는 오류가 발생했습니다.")
                st.error(f"오류: {error_msg}")
                return False
    
    return False