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
            #Вот тут вызываем нейросеть
            if st.session_state.my_chat_input:
                st.session_state.messages.append({"role": "user", "content": st.session_state.my_chat_input})
                st.session_state.messages.append(
                    {"role": "assistant", "content": "Привет! Я получил твое сообщение в чате."}
                )
                st.switch_page("pages/chat.py")