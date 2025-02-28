import streamlit as st

def display_chat_message(role, content):
    with st.chat_message(role):
        st.markdown(content)