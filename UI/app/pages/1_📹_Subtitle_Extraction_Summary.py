import streamlit as st
import requests
from yt_dlp import YoutubeDL
import datetime

# 웹 서버 URL 설정
WEB_SERVER_URL = "http://localhost:8000/summarize_file"

# 페이지 설정
st.set_page_config(
    page_title="자막 추출 및 요약",
    page_icon="📹",
)

st.write("# Youtube 자막 추출 및 요약")

# 유튜브 비디오 URL 입력
video_url = st.text_input("Youtube 영상 URL을 입력하세요:", "https://www.youtube.com/watch?v=2J8ORNpH3Uk")

# yt-dlp를 사용하여 비디오 정보 추출 함수 (캐시 사용)
@st.cache_resource
def get_video_info(video_url):
    opts = {}
    with YoutubeDL(opts) as yt:
        info = yt.extract_info(video_url, download=False)
    return info

# 타임라인 생성 함수 (캐시 사용)
@st.cache_data
def generate_markdown_timeline(chapters):
    """
    주어진 chapters 데이터를 바탕으로 Markdown 형식의 영상 타임라인을 생성합니다.
    """
    markdown_text = "#### 영상 타임라인\n"
    for chapter in chapters:
        start_time = f"{int(chapter['start_time']) // 60}:{int(chapter['start_time']) % 60:02d}"
        end_time = f"{int(chapter['end_time']) // 60}:{int(chapter['end_time']) % 60:02d}"
        markdown_text += f":blue-background[**{start_time} ~ {end_time}**]\n"
        markdown_text += f"{chapter['title']}\n\n"
    return markdown_text


# 자막 다운로드 함수
@st.cache_resource
def download_subtitle(subtitle_url, filename="subtitle.vtt"):
    """
    주어진 URL에서 자막을 다운로드합니다.
    """
    try:
        response = requests.get(subtitle_url, stream=True)
        response.raise_for_status()
        
        # 파일 저장
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)

        st.success(f"자막 파일이 {filename}으로 저장되었습니다.")
    except requests.exceptions.RequestException as e:
        st.error(f"자막 다운로드 실패: {e}")

# 비디오 정보가 있을 때 출력
if video_url:
    # 비디오 정보 추출
    info = get_video_info(video_url)
    title = info.get("title")
    channel = info.get('channel')
    views = info.get("view_count")
    likes = info.get("like_count")
    upload_date = info.get("upload_date")
    duration = info.get('duration_string')

    # 조회수 포맷: 천 단위로 쉼표 추가
    formatted_views = f"{views:,}"

    # 업로드 날짜 포맷: YYYY.MM.DD
    formatted_upload_date = datetime.datetime.strptime(upload_date, "%Y%m%d").strftime("%Y.%m.%d")

    # 타임라인 생성
    markdown_result = generate_markdown_timeline(info.get('chapters')) if 'chapters' in info else "타임라인 정보가 없습니다."

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
        st.markdown(markdown_result)

    # 자막 보기 체크박스
    if st.checkbox("전체 자막 보기"):
        st.subheader("자막 정보")
        
        # 자막 형식 필터링: JSON3, TTML, VTT만 출력
        for subtitle in info['subtitles']['ko']:
            subtitle_ext = subtitle['ext']
            
            # JSON3, TTML, VTT 형식만 필터링
            if subtitle_ext in ['json3', 'srv1', 'ttml', 'vtt']:
                subtitle_url = subtitle['url']
                # URL을 보기 좋게 링크로 표시
                st.write(f"- {subtitle_ext}: [링크로 열기]({subtitle_url})")
                
                # 다운로드 버튼
                if st.button(f"다운로드 ({subtitle_ext})", key=subtitle_url):
                    download_subtitle(subtitle_url)
                    
    # 요약 요청
        if st.button("자막 요약 요청"):
            subtitle_url = download_subtitle.split(" - ")[1]
            response = requests.get(subtitle_url)
            if response.status_code == 200:
                subtitle_text = response.text
                st.text_area("자막 내용", subtitle_text[:500], height=200)

                # 웹 서버로 요약 요청
                try:
                    with st.spinner("요약 요청 중..."):
                        summarize_response = requests.post(
                            WEB_SERVER_URL,
                            files={"file": ("subtitle.vtt", subtitle_text.encode("utf-8"))}
                        )
                        summarize_response.raise_for_status()
                        summary = summarize_response.json().get("summary", "요약 결과 없음")
                        st.subheader("📚 요약 결과")
                        st.markdown(summary)
                except requests.exceptions.RequestException as e:
                    st.error(f"요약 요청 실패: {e}")
            else:
                st.error("자막을 가져오는 데 실패했습니다.")
    # except Exception as e:
    #     st.error(f"유튜브 정보를 가져오는 데 실패했습니다: {e}")

    # 요약 보기 체크박스
    if st.checkbox("요약 보기"):
        st.subheader(":cherry_blossom: 요약 결과 :cherry_blossom:")
        st.markdown("요약 내용을 여기에 추가하세요.")