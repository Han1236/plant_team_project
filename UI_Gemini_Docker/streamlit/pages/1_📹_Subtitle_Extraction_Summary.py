import streamlit as st
import requests
import datetime

# 페이지 설정
st.set_page_config(
    page_title="자막 추출 및 요약",
    page_icon="📹",
)

st.write("# Youtube 자막 추출 및 요약")

# 유튜브 비디오 URL 입력
video_url = st.text_input("Youtube 영상 URL을 입력하세요:", "https://www.youtube.com/watch?v=2J8ORNpH3Uk")

# 요약 API URL (FastAPI 백엔드 엔드포인트)
API_URL_VIDEO_INFO = "http://fastapi-backend:8000/api/video_info/"
API_URL_SUMMARY = "http://fastapi-backend:8000/api/gemini/"

# 비디오 정보 및 자막을 요청하는 함수
def get_video_info(video_url):
    response = requests.post(API_URL_VIDEO_INFO, json={"video_url": video_url})
    if response.status_code == 200:
        return response.json()
    else:
        st.error("영상 정보 또는 자막 다운로드에 실패했습니다.")
        return None

# 요약 요청 함수
def summarize_with_api(transcript_text):
    response = requests.post(API_URL_SUMMARY, json={"prompt": transcript_text})
    if response.status_code == 200:
        return response.json().get("summary")
    else:
        return "요약에 실패했습니다."
    


# 영상 정보가 있을 때 출력
if video_url:
    with st.spinner("잠시 기다려주세요..."):
        # 비디오 정보 및 자막 요청
        video_info = get_video_info(video_url)

    if video_info:
        # 비디오 정보 추출
        title = video_info.get("title", "")
        channel = video_info.get("channel", "")
        views = video_info.get("view_count", "")
        upload_date = video_info.get("upload_date", "")
        duration = video_info.get("duration_string", "")
        timeline = video_info.get("timeline", "")
        subtitle = video_info.get("subtitle", "")

        # 조회수 포맷: 천 단위로 쉼표 추가
        formatted_views = f"{views:,}"

        # 업로드 날짜 포맷: YYYY.MM.DD
        formatted_upload_date = datetime.datetime.strptime(upload_date, "%Y%m%d").strftime("%Y.%m.%d")

        # 비디오 정보 출력
        col1, col2 = st.columns([1, 1])  # 1:1 비율로 두 칸 분리
        with col1:
            st.subheader("📷 영상 정보")
            st.markdown(f"""
                        #### 제목:
                        :blue-background[**{title}**]
                        #### 입력된 Youtube URL:
                        {video_url}
                        ##### 채널: {channel} | 조회수: **{formatted_views}** 회
                        ##### 업로드날짜: {formatted_upload_date}
                        ##### 영상 길이: {duration}
                        """)
            
        with col2:
            st.subheader("📝 타임라인")
            st.markdown(timeline)

        # 자막 텍스트 출력
        st.subheader("자막 내용")
        st.text_area("전체 자막", subtitle, height=300)

        # 요약 보기 체크박스
        if st.checkbox("요약 보기"):
            st.subheader(":cherry_blossom: 요약 결과 :cherry_blossom:")
            with st.spinner("자막을 요약중입니다. 잠시 기다려주세요..."):
                summary = summarize_with_api(subtitle)
            st.markdown(summary)
            
