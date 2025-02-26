import yt_dlp
import os
import re
from typing import List, Dict, Any, Optional
import datetime

def get_video_info_and_subtitles(video_url: str):
    """
    yt-dlp를 이용해 유튜브 영상 정보를 추출하고,
    한글 자막(ko)이 있으면 VTT 파일을 읽어 텍스트로 정제해 반환합니다.
    """
    opts = {
        "writesubtitles": True,           # 자막 다운로드
        "writeautomaticsub": True,        # 자동 자막 다운로드
        "skip_download": True,            # 비디오 다운로드는 하지 않음
        "subtitlesformat": "vtt",         # 자막 형식
        "outtmpl": "%(id)s.%(ext)s",      # 영상 ID로 파일명 지정
        "subtitleslangs": ["ko"],         # 한국어 자막만 다운로드
    }

    try:
        with yt_dlp.YoutubeDL(opts) as yt:
            # 영상 정보 추출
            info = yt.extract_info(video_url, download=False)
            video_title = info.get('title', None)

            if video_title:
                # 영상 ID를 기반으로 파일명을 지정
                video_id = info.get('id', '')
                subtitle_file = f"{video_id}.ko.vtt"
                print(f"다운로드된 자막 파일 경로: {subtitle_file}")

                # 자막 다운로드
                yt.download([video_url])

                # 자막 파일이 존재하면 텍스트 추출
                if os.path.exists(subtitle_file):
                    with open(subtitle_file, "r", encoding="utf-8") as f:
                        content = f.read()

                    # 자막 처리 로직
                    clean_content = clean_subtitle_content(content)

                    return info, clean_content
                else:
                    # 자막이 없는 경우 처리
                    return info, "자막이 없습니다."

            else:
                    # 영상 정보가 없을 경우
                    return None, "영상 정보를 찾을 수 없습니다."
    except Exception as e:
        print(f"오류 발생: {e}")
        return None, None

def clean_subtitle_content(content):
    """자막 콘텐츠 정제 함수"""
    # 1. 'WEBVTT' 또는 'Kind' 같은 메타데이터 제거
    clean_content = re.sub(r'WEBVTT.*?Kind.*?Language.*?\n', '', content, flags=re.DOTALL)  # 메타데이터 제거
    
    # 2. 타임스탬프 및 HTML 태그 제거
    clean_content = re.sub(r'<.*?>', '', clean_content)  # <c> 태그 및 HTML 태그 제거
    clean_content = re.sub(r'<\d{2}:\d{2}:\d{2}\.\d{3}>', '', clean_content)  # 타임스탬프 제거
    clean_content = re.sub(r'\d{2}:\d{2}:\d{2}\.\d{3} --> \d{2}:\d{2}:\d{2}\.\d{3}', '', clean_content)  # 타임스탬프 형식 제거

    # 3. 'align:start position:0%' 제거
    clean_content = re.sub(r'align:start position:\d+%', '', clean_content)  # align:start 제거

    # 4. 중복된 자막 제거 (텍스트가 반복되면 중복된 부분 제거)
    clean_content = "\n".join(sorted(set(clean_content.splitlines()), key=lambda x: clean_content.index(x)))

    # 5. 자막 내용 정리(불필요한 줄이나 빈 줄 제거)
    clean_content = "\n".join([line.strip() for line in clean_content.splitlines() if line.strip()])

    return clean_content

def generate_markdown_timeline(chapters):
    """
    yt-dlp가 추출한 'chapters' 정보를 바탕으로 Markdown 형식 타임라인을 생성
    """
    if not chapters:
        return "타임라인 정보가 없습니다."
    markdown_text = "#### 영상 타임라인\n"
    for ch in chapters:
        start_time = f"{int(ch['start_time']) // 60}:{int(ch['start_time']) % 60:02d}"
        end_time = f"{int(ch['end_time']) // 60}:{int(ch['end_time']) % 60:02d}"
        markdown_text += f"**{start_time} ~ {end_time}**\n"
        markdown_text += f"{ch['title']}\n\n"
    return markdown_text

# def get_videos_from_playlist(playlist_url, playlist_start, playlist_end):
#     """
#     yt-dlp를 사용하여 유튜브 플레이리스트에서 비디오 목록을 가져옵니다.
#     """
#     opts = {
#         'quiet': True,  # 최소한의 로그만 출력
#         'extract_flat': True,  # 비디오의 상세 정보를 추출하지만 다운로드하지 않음
#         'playliststart': playlist_start,  # 플레이리스트에서 시작할 비디오 인덱스
#         'playlistend': playlist_end,  # 플레이리스트에서 끝낼 비디오 인덱스
#         'writethumbnail': False,  # 썸네일을 저장
#         'download': False,  # 실제 비디오 다운로드하지 않음
#     }

#     with yt_dlp.YoutubeDL(opts) as ydl:
#         # 플레이리스트 URL에서 비디오 정보 추출 (다운로드하지 않고 정보만 추출)
#         info_dict = ydl.extract_info(playlist_url, download=False)

#         # 추출된 비디오들에 대해 필요한 정보만 출력
#         videos = info_dict.get('entries', [])

#         if not videos:
#             print("플레이리스트에서 비디오를 찾을 수 없습니다.")
#             return []

#         # 비디오 목록을 반환
#         return videos

def format_view_count(view_count: int):
    """
    조회수를 한국어 형식에 맞춰 변환합니다.
    """
    view_count = int(view_count)

    if view_count < 1000:
        return f"{view_count}회"
    elif view_count < 10000:
        thousands = view_count / 1000
        return f"{thousands:.1f}천회" # 소수점 한자리까지 표시
    else:
        mans = view_count / 10000
        return f"{int(mans)}만회" # 만 단위는 정수로 표시


def get_videos_from_playlist(playlist_url: str, playlist_start: int = 0, playlist_end: int = 6):
    """
    yt-dlp를 사용하여 유튜브 플레이리스트에서 비디오 목록을 가져옵니다.
    """
    opts = {
        'quiet': True,  # 최소한의 로그만 출력
        'extract_flat': True,  # 비디오의 상세 정보를 추출하지만 다운로드하지 않음
        'playliststart': playlist_start,  # 플레이리스트에서 시작할 비디오 인덱스
        'playlistend': playlist_end,  # 플레이리스트에서 끝낼 비디오 인덱스
        'writethumbnail': False,  # 썸네일을 저장
        'download': False,  # 실제 비디오 다운로드하지 않음
    }

    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            # 플레이리스트 URL에서 비디오 정보 추출 (다운로드하지 않고 정보만 추출)
            info_dict = ydl.extract_info(playlist_url, download=False)
            
            # 추출된 비디오들에 대해 필요한 정보만 출력
            videos = info_dict.get('entries', [])
            
            if not videos:
                print("플레이리스트에서 비디오를 찾을 수 없습니다.")
                return []
                
            # 비디오 목록을 반환
            return videos
        
    except Exception as e:
        print(f"플레이리스트 정보 추출 중 오류 발생: {str(e)}")
        return []
    
def format_upload_date(upload_date: str):
    """
    업로드 날짜를 포맷팅합니다.
    """
    return datetime.datetime.strptime(upload_date, "%Y%m%d").strftime("%Y.%m.%d")