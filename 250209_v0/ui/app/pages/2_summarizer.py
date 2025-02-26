import streamlit as st
from utils.api import summarize_with_api
from utils.formatters import format_summary

st.set_page_config(page_title="자막 요약", page_icon="📋")

st.title("📋 자막 요약")

st.write("""
저장된 자막과 타임라인을 분석하여 내용을 요약합니다.
AI가 영상의 핵심 내용을 간결하게 정리해줍니다.
""")

# 세션 상태 확인
if "subtitle" not in st.session_state:
    st.warning("먼저 '자막 추출' 페이지에서 YouTube 영상의 자막을 저장해주세요.")
    st.stop()

# 자막과 타임라인 정보 불러오기
subtitle = st.session_state.subtitle
timeline = st.session_state.get("timeline", "타임라인 정보가 없습니다.")

# 요약 섹션
st.subheader("요약 생성")

if st.button("요약 시작"):
    with st.spinner("영상 내용을 요약하는 중..."):
        summary = summarize_with_api(subtitle, timeline)
        
        if summary:
            st.session_state.summary = summary
            st.success("요약이 완료되었습니다!")

# 요약 결과 표시
if "summary" in st.session_state:
    st.subheader("📝 요약 결과")
    st.markdown(format_summary(st.session_state.summary))
    
    # 요약 결과 다운로드 버튼
    st.download_button(
        label="요약 결과 다운로드",
        data=st.session_state.summary,
        file_name="summary.md",
        mime="text/markdown"
    )