import streamlit as st
from components import video_input
# from utils.api import get_video_info
from utils.formatters import format_subtitle
import requests
from config import API_ENDPOINTS
import os

st.set_page_config(page_title="자막 추출", page_icon="📝")

st.title("📝 YouTube 자막 추출")

st.write("""
YouTube 영상의 URL을 입력하면 해당 영상의 자막을 추출하여 보여줍니다.
추출된 자막은 요약 및 QnA 기능의 기반 데이터로 사용됩니다.
""")

# 세션 상태 초기화
if 'db_created' not in st.session_state:
    st.session_state['db_created'] = False

# 비디오 URL 변수 초기화
if 'video_url' not in st.session_state:
    st.session_state['video_url'] = ""

# 슈카월드 플레이리스트 표시
def display_video_list(playlist_url):
    try:
        response = requests.post(API_ENDPOINTS["playlist_videos"], json={"playlist_url": playlist_url, "start": 0, "end": 6})
        if response.status_code == 200:
            videos = response.json()
            video_list = videos['videos']
            
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
                col = columns[i % num_columns]
                
                video_url = video.get('url')
                title = video.get('title')
                thumbnail_url = video.get('thumbnail_url')
                formatted_view_count = video.get('formatted_view_count')
                formatted_duration = video.get('formatted_duration')
                
                # 비디오 카드 UI
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
                                조회수 {formatted_view_count}
                            </div>
                        </div>
                    </a>
                """, unsafe_allow_html=True)

                     
                # <a href="{video_url}" target="_blank" style="text-decoration: none; color: inherit;">
                #     <div style="border: 1px solid #ddd; border-radius: 5px; padding: 10px; margin-bottom: 10px;">
                #         <div style="position: relative;">
                #             <img src="{thumbnail_url}" style="width: 100%; border-radius: 5px;">
                #             <div style="position: absolute; bottom: 5px; right: 5px; background-color: rgba(0, 0, 0, 0.7); color: white; padding: 2px 5px; border-radius: 3px; font-size: 12px;">
                #                 {formatted_duration}
                #             </div>
                #         </div>
                #         <div style="color: black; font-size: 15px; font-family: 'Noto Sans KR', sans-serif; margin-top: 5px;">
                #             {title}
                #         </div>
                #         <div style="color: gray; font-size: 13px; font-family: 'Noto Sans KR', sans-serif; margin-top: 2px;">
                #             조회수 {formatted_count}
                #         </div>
                #     </div>
                # </a>
                
                # URL 자동입력 버튼
                if col.button("URL 자동입력", key=f"copy_{i}"):
                    st.session_state['video_url'] = video_url
                    st.session_state['db_created'] = False  # DB 재생성 플래그 초기화
                
                # 각 비디오마다 세로 구분선 추가
                col.markdown("---")
        else:
            st.error("플레이리스트 비디오 목록을 불러오는데 실패했습니다.")
    except Exception as e:
        st.error(f"오류 발생: {str(e)}")

# 유튜브 플레이리스트에서 비디오 목록 표시
playlist_url = "https://www.youtube.com/playlist?list=PLJPjg3It2DXQUdlAocHh5FASozqwtJavv"  # 슈카월드 playlist URL
display_video_list(playlist_url)

# 예시 URL 입력 버튼
if st.button("예시 url 입력"):
    st.session_state['video_url'] = "https://www.youtube.com/watch?v=2J8ORNpH3Uk"  # 예시 URL로 설정

# 비디오 URL 입력 컴포넌트
video_loaded = video_input.youtube_url_input()

# # 유튜브 비디오 URL 입력
# video_url = st.text_input("Youtube 영상 URL을 입력하세요:", value=st.session_state['video_url'])

# 비디오 정보가 로드되었으면 자막과 타임라인 표시
if video_loaded or "video_info" in st.session_state:
    video_info = st.session_state.video_info
    video_url = st.session_state.video_url

    video_id = video_info.get("video_id")
    title = video_info.get("title")
    channel = video_info.get("channel")
    view_count = video_info.get("view_count")
    upload_date = video_info.get("upload_date")
    duration = video_info.get("duration_string")
    timeline = video_info.get("timeline")
    subtitle = video_info.get("subtitle")
    
    # 영상 정보 표시
    st.header(f"📺 {title}")
    
    # 탭 생성
    tab1, tab2 = st.tabs(["자막", "영상정보"])
    
    with tab1:
        st.subheader("📄 자막")
        subtitle = format_subtitle(subtitle)
        st.text_area("자막 내용", subtitle, height=400, label_visibility="collapsed")
        
        # 자막 저장 버튼
        if st.button("자막 저장하기"):
            st.session_state.subtitle = subtitle
            st.success("자막이 저장되었습니다! 요약 페이지로 이동하여 요약을 생성할 수 있습니다.")
    
    with tab2:
        col1, col2 = st.columns([1, 1])
        with col1:
            st.subheader("📷 영상 정보")
            st.markdown(f"""
                        #### 제목:
                        :blue-background[**{title}**]
                        #### 입력된 Youtube URL:
                        {video_url}
                        ##### 채널: {channel} | 조회수: **{view_count}** 회
                        ##### 업로드날짜: {upload_date}
                        ##### 영상 길이: {duration}
                        """)

        with col2:
            st.subheader("⏱️ 타임라인")
            timeline = video_info.get("timeline", "타임라인 정보가 없습니다.")
            st.markdown(timeline)
            
            # 타임라인 저장 버튼
            if st.button("타임라인 저장하기"):
                st.session_state.timeline = timeline
                st.success("타임라인이 저장되었습니다!")
    
    # ChromaDB 생성 버튼
    if st.button("ChromaDB 생성", disabled=st.session_state['db_created']):
        with st.spinner("ChromaDB를 생성 중입니다..."):
            response = requests.post(
                API_ENDPOINTS["create_chromadb"], 
                json={
                    "video_id": video_id, 
                    "title": title, 
                    "subtitle": subtitle
                }
            )
            
            if response.status_code == 200:
                res = response.json()
                st.session_state['db_created'] = True
                st.success(f"{res['message']}")
            else:
                st.info("ChromaDB 생성 실패.")
                st.session_state['db_created'] = False