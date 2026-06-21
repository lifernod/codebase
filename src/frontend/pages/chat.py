import streamlit as st
from utils import render_sidebar, load_css

st.set_page_config(page_title="Чат", layout="centered", initial_sidebar_state="expanded")

load_css("style.css")

if "messages" not in st.session_state:
    st.session_state.messages = []

render_sidebar()


for message in st.session_state.messages:
    role_class = "user-message" if message["role"] == "user" else "bot-message"
    with st.chat_message(message["role"]):
        st.markdown(f'<div class="{role_class}">{message["content"]}</div>', unsafe_allow_html=True)


def continue_chat():
    if st.session_state.chat_page_input:
        st.session_state.messages.append({"role": "user", "content": st.session_state.chat_page_input})
        st.session_state.messages.append({"role": "assistant", "content": "Ответ на ваше новое сообщение!"})

        st.session_state.chat_page_input = ""


input_container = st.container()

with input_container:
    st.markdown('<div class="chat-input-anchor"></div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 10, 1])

    with col2:
        input_col, btn_col = st.columns([0.9, 0.1])
        with input_col:
            st.text_area(
                "ChatInput",
                placeholder="Напишите сообщение...",
                label_visibility="collapsed",
                key="chat_page_input"
            )
        with btn_col:
            st.button("➤", on_click=continue_chat, key="chat_page_submit")