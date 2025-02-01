import yt_dlp
import streamlit as st
import requests
import datetime

# 페이지 설정
st.set_page_config(
    page_title="자막 추출 및 요약",
    page_icon="📹",
)

st.write("# Youtube 자막 추출 및 요약")

# video_url 변수를 session_state를 사용하여 초기화
if 'video_url' not in st.session_state:
    st.session_state['video_url'] = ""  # 초기값을 빈 문자열 "" 로 설정

# 웹 서버 URL 설정
WEB_SERVER_URL = "http://web-server:8000"

# 비디오 정보 및 자막을 요청하는 함수
def get_video_info(video_url):
    response = requests.post(f"{WEB_SERVER_URL}/video_info", json={"video_url": video_url})
    if response.status_code == 200:
        return response.json()
    else:
        st.error("영상 정보 또는 자막 다운로드에 실패했습니다.")
        return None

# 요약 요청 함수
def summarize_with_api(transcript_text):
    response = requests.post(f"{WEB_SERVER_URL}/summarize", json={"prompt": transcript_text})
    if response.status_code == 200:
        return response.json().get("summary")
    else:
        return "요약에 실패했습니다."

# 유튜브 채널에서 최신 비디오를 가져오는 함수
def get_videos_from_playlist(playlist_url, playlist_start, playlist_end):
    opts = {
        'quiet': True,  # 최소한의 로그만 출력
        'extract_flat': True,  # 비디오의 상세 정보를 추출하지만 다운로드하지 않음
        'playliststart': playlist_start,  # 플레이리스트에서 시작할 비디오 인덱스
        'playlistend': playlist_end,  # 플레이리스트에서 끝낼 비디오 인덱스
        'writethumbnail': False,  # 썸네일을 저장
        'download': False,  # 실제 비디오 다운로드하지 않음
    }

    with yt_dlp.YoutubeDL(opts) as ydl:
        # 플레이리스트 URL에서 비디오 정보 추출 (다운로드하지 않고 정보만 추출)
        info_dict = ydl.extract_info(playlist_url, download=False)

        # 추출된 비디오들에 대해 필요한 정보만 출력
        videos = info_dict.get('entries', [])

        if not videos:
            st.error("플레이리스트에서 비디오를 찾을 수 없습니다.")
            return []

        # 비디오 목록을 반환
        return videos

# 조회수를 한국어 형식에 맞춰 변환
def format_view_count(view_count):
    view_count = int(view_count)  # Ensure view_count is an integer

    if view_count < 1000:
        return f"{view_count}회"
    elif view_count < 10000:
        thousands = view_count / 1000
        return f"{thousands:.1f}천회" # 소수점 한자리까지 표시
    else:
        mans = view_count / 10000
        return f"{int(mans)}만회" # 만 단위는 정수로 표시

# 조회된 비디오 리스트 표시
def display_video_list(playlist_url):
    # 플레이리스트 URL에서 비디오 목록 가져오기
    videos = get_videos_from_playlist(playlist_url, playlist_start=0, playlist_end=6)

    if videos:
        # 한 줄에 3개의 비디오를 표시하기 위해 3개의 열로 분할
        num_columns = 3
        columns = st.columns(num_columns)

        st.markdown(
        """
        <style>
        div.stButton > button {
            padding: 3px 10px !important;
            margin-top: 10px !important;
            background-color: #FBFBFC !important;
        }

        /* 버튼 아래 간격을 더 좁히기 */
        div.stButton {
            margin-bottom: 0px !important;
        }
        </style>
        """,
        unsafe_allow_html=True
        )

        for i, video in enumerate(videos):
            # 비디오가 3개의 열을 넘지 않게 하기 위해 인덱스 위치 조정
            column_index = i % num_columns
            col = columns[column_index]

            # 썸네일 표시
            thumbnails = video.get('thumbnails', [])
            if thumbnails:
                thumbnail_url = thumbnails[-1]['url']  # 가장 큰 썸네일을 선택
                # 썸네일 이미지를 HTML과 CSS로 겹치게 처리
                duration = video.get('duration', 0)
                formatted_duration = f"{duration // 60:02}:{duration % 60:02}"
                formatted_count = format_view_count(video['view_count'])

                col.markdown(f"""
                    <a href="{video['url']}" style="display: block; text-decoration: none; color: inherit;">
                        <div style="display: flex; flex-direction: column; height: 200px;">
                            <!-- flex container for vertical layout -->
                            <div style="position: relative; display: inline-block;">
                                <!-- 썸네일 래퍼 -->
                                <img src="{thumbnail_url}" width="240" style="border-radius: 10px;" />
                                <div style="position: absolute; bottom: 5px; right: 5px; color: white; font-weight: bold; font-size: 14px; background-color: rgba(0, 0, 0, 0.5); padding: 2px 5px; border-radius: 5px;">
                                    {formatted_duration}
                                </div>
                            </div>
                            <div style="color: black; font-size: 15px; font-family: 'Noto Sans KR', sans-serif; margin-top: 5px;">
                                {video['title']}
                            </div>
                            <div style="color: gray; font-size: 13px; font-family: 'Noto Sans KR', sans-serif; margin-top: 2px;">
                                조회수 {formatted_count}
                            </div>
                        </div>
                    </a>
                """, unsafe_allow_html=True)

            # URL 복사 버튼 (각 버튼에 고유 key 부여)
            if col.button("URL 자동입력", key=f"copy_{i}"): # 스타일 제거
                st.session_state['video_url'] = video["url"] # session_state 값만 업데이트

            # 세로 구분을 위해 각 비디오마다 구분선을 추가
            col.markdown("---")


# 채널에서 최신 비디오 목록을 표시
playlist_url = "https://www.youtube.com/playlist?list=PLJPjg3It2DXQUdlAocHh5FASozqwtJavv"  # 예시 URL
display_video_list(playlist_url)

# "예시 url 입력" 버튼 추가
if st.button("예시 url 입력"):
    st.session_state['video_url'] = "https://www.youtube.com/watch?v=2J8ORNpH3Uk"  # 예시 URL로 설정

# 유튜브 비디오 URL 입력
# st.session_state['video_url'] 값을 value 파라미터로 넣어줍니다.
video_url = st.text_input("Youtube 영상 URL을 입력하세요:", value=st.session_state['video_url'])


# 비디오 정보가 있을 때 출력
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