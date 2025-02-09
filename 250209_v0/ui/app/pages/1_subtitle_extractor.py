import streamlit as st
import requests
import datetime
import os

# --- UI 설정 ---
st.set_page_config(
    page_title="자막 추출 및 DB생성",
    page_icon="📹",
)

# 세션 상태 초기화
if 'db_created' not in st.session_state:
     st.session_state['db_created'] = False

# 비디오 URL 변수 초기화
if 'video_url' not in st.session_state:
    st.session_state['video_url'] = ""


st.write("# Youtube 자막 추출 및 ChromaDB 생성")



# ==== 환경설정 ====
WEB_SERVER_URL = os.getenv("WEB_SERVER_URL", "http://localhost:8000")  # 환경변수에서 URL 읽어오기, 기본값 설정

# --- web_server API 호출 함수 ---
def get_video_info(video_url):
    response = requests.post(f"{WEB_SERVER_URL}/video_info", json={"video_url": video_url})
    if response.status_code == 200:
        return response.json()
    else:
        st.error("영상 정보 또는 자막 다운로드에 실패했습니다.")
        return None

def summarize_with_api(transcript_text):
    response = requests.post(f"{WEB_SERVER_URL}/summarize", json={"prompt": transcript_text})
    if response.status_code == 200:
        return response.json().get("summary")
    else:
        return "요약에 실패했습니다."

def get_playlist_videos_from_api(playlist_url): # 플레이리스트 비디오 목록 API 호출 함수
    response = requests.get(f"{WEB_SERVER_URL}/playlist_videos", params={"playlist_url": playlist_url})
    if response.status_code == 200:
        return response.json()
    else:
        st.error("플레이리스트 비디오 목록을 불러오는데 실패했습니다.")
        return None


# --- UI 로직  ---
def display_video_list(playlist_url):
    videos = get_playlist_videos_from_api(playlist_url) # web_server API 호출
    video_list = videos['videos']
    if videos:
        # 비디오를 3개씩 열에 나누어 표시
        num_columns = 3
        columns = st.columns(num_columns)

        # 버튼 스타일 커스터마이징
        st.markdown("""
        <style>
        div.stButton > button {
            padding: 3px 10px !important;
            margin-top: 10px !important;
            background-color: #FBFBFC !important;
        }
        div.stButton {
            margin-bottom: 0px !important;
        }
        </style>
        """, unsafe_allow_html=True)

        # 각 비디오를 열에 맞게 표시
        for i, video in enumerate(video_list):
            column_index = i % num_columns
            col = columns[column_index]

            # 썸네일 이미지와 비디오 정보 표시
            thumbnail_url = video.get('thumbnail_url') # web_server 에서 썸네일 url 제공
            formatted_duration = video.get('formatted_duration') # web_server 에서 포맷팅된 시간 제공
            formatted_count = video.get('formatted_view_count') # web_server 에서 포맷팅된 조회수 제공
            video_url = video.get('url')
            title = video.get('title')

            col.markdown(f"""
                    <a href="{video_url}" style="display: block; text-decoration: none; color: inherit;">
                        <div style="display: flex; flex-direction: column; height: 200px;">
                            <div style="position: relative; display: inline-block;">
                                <img src="{thumbnail_url}" width="240" style="border-radius: 10px;" />
                                <div style="position: absolute; bottom: 5px; right: 5px; color: white; font-weight: bold; font-size: 14px; background-color: rgba(0, 0, 0, 0.5); padding: 2px 5px; border-radius: 5px;">
                                    {formatted_duration}
                                </div>
                            </div>
                            <div style="color: black; font-size: 15px; font-family: 'Noto Sans KR', sans-serif; margin-top: 5px;">
                                {title}
                            </div>
                            <div style="color: gray; font-size: 13px; font-family: 'Noto Sans KR', sans-serif; margin-top: 2px;">
                                조회수 {formatted_count}
                            </div>
                        </div>
                    </a>
                """, unsafe_allow_html=True)

            # URL 자동입력 버튼
            if col.button("URL 자동입력", key=f"copy_{i}"):
                st.session_state['video_url'] = video_url
                st.session_state['db_created'] = False  # DB 재생성 플래그 초기화

            # 각 비디오마다 세로 구분선 추가
            col.markdown("---")

# 유튜브 플레이리스트에서 비디오 목록 표시
playlist_url = "https://www.youtube.com/playlist?list=PLJPjg3It2DXQUdlAocHh5FASozqwtJavv"  # 슈카월드 playlist URL
display_video_list(playlist_url)

# 예시 URL 입력 버튼
if st.button("예시 url 입력"):
    st.session_state['video_url'] = "https://www.youtube.com/watch?v=2J8ORNpH3Uk"  # 예시 URL로 설정

# 유튜브 비디오 URL 입력
video_url = st.text_input("Youtube 영상 URL을 입력하세요:", value=st.session_state['video_url'])

# 비디오 URL 이 있을 때만 영상 정보 및 UI 표시
if video_url:
    with st.spinner("잠시 기다려주세요..."):
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
        video_id = video_info.get("id", "id없음")

        # 세션 상태에 video_id 저장
        st.session_state['current_video_id'] = video_id

        # 조회수 포맷
        formatted_views = f"{views:,}"
        formatted_upload_date = datetime.datetime.strptime(upload_date, "%Y%m%d").strftime("%Y.%m.%d")

        # 비디오 정보 표시
        col1, col2 = st.columns([1, 1])
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

        # ChromaDB 생성 버튼 (API 호출)
        if st.button("ChromaDB 생성", disabled=st.session_state['db_created']):
            with st.spinner("ChromaDB를 생성 중입니다..."):
                response = requests.post(f"{WEB_SERVER_URL}/create_chromadb", json={"video_id": video_id, "title": title, "subtitle":subtitle}) # 웹 서버에 DB 생성 요청
                res = response.json()
                if response.status_code == 200:
                    st.session_state['db_created'] = True
                    # st.success("ChromaDB 생성 완료!")
                    st.success(f"{res['message']}")

                else:
                    # st.error("ChromaDB 생성 실패.")
                    st.info(f"{res['message']}")
                    st.session_state['db_created'] = False

        # 요약 보기 체크박스
        if st.checkbox("요약 보기"):
            st.subheader(":cherry_blossom: 요약 결과 :cherry_blossom:")
            with st.spinner("자막을 요약중입니다. 잠시 기다려주세요..."):
                summary = summarize_with_api(subtitle) # 웹 서버 요약 API 호출
            st.markdown(summary)