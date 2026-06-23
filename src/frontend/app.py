import streamlit as st
from utils import load_css, render_sidebar

st.set_page_config(page_title="Главная", layout="centered", initial_sidebar_state="expanded")
load_css("style.css")

if "messages" not in st.session_state:
    st.session_state.messages = []

render_sidebar()

st.markdown("<div class='centered-title'>Чем займемся сегодня?</div>", unsafe_allow_html=True)

input_container = st.container()

with input_container:
    col1, col2, col3 = st.columns([1, 10, 1])

    with col2:
        prompt = st.chat_input("Задайте вопрос, и получите ответ")
        if prompt:
            st.session_state.pending_first_query = prompt
            st.switch_page("pages/chat.py")