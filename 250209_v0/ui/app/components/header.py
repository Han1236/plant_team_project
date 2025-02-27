import streamlit as st

def show_header():
    """앱 헤더를 표시합니다."""
    col1, col2 = st.columns([1, 5])
    
    with col1:
        st.image("assets/images/syuka.jpg", width=100)
    
    with col2:
        st.markdown("""
        <div style="padding-top: 20px;">
            <h1>슈카월드 AI 어시스턴트 Welcome! 👋</h1>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")