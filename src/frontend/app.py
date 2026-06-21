import streamlit as st
from utils import load_css, render_sidebar

st.set_page_config(page_title="Главная", layout="centered", initial_sidebar_state="expanded")
load_css("style.css")

if "messages" not in st.session_state:
    st.session_state.messages = []

render_sidebar()

st.markdown("<div class='centered-title'>Чем займемся сегодня?</div>", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 10, 1])

with col2:
    input_col, btn_col = st.columns([0.9, 0.1])

    with input_col:
        st.text_area(
            "Label",
            placeholder="Задайте вопрос, и получите ответ",
            label_visibility="collapsed",
            key="my_chat_input"
        )

    with btn_col:
        if st.button("➤"):
            query = st.session_state.my_chat_input
            if query:
                # Главная страница не вызывает API сама — передаёт вопрос
                # в чат, где он обрабатывается тем же путём, что и обычные
                # сообщения (включая замер времени и метрики).
                st.session_state.pending_first_query = query
                st.switch_page("pages/chat.py")