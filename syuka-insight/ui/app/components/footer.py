import streamlit as st

def show_footer():
    """앱 푸터를 표시합니다."""
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: gray; font-size: 0.8em;">
        © 2025 슈카월드 AI 어시스턴트
    </div>
    """, unsafe_allow_html=True)