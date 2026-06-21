import time
import streamlit as st
from utils import render_sidebar, load_css
from api_client import ask
from eval_questions import EVAL_QUERY_TO_ID

st.set_page_config(page_title="Чат", layout="centered", initial_sidebar_state="expanded")

load_css("style.css")

if "messages" not in st.session_state:
    st.session_state.messages = []

render_sidebar()


def send_query(query: str):
    """
    Отправляет запрос на бэкенд и сохраняет результат в историю.

    Время ответа считается ЛОКАЛЬНО на фронте (time.perf_counter() вокруг
    вызова ask()) — бэкенд latency не присылает и не должен.

    Если query совпадает с одним из 15 эталонных вопросов из
    eval_questions.json, бэкенд дополнительно вернёт recall/precision —
    это определяется самим бэкендом по тексту запроса, фронт просто
    сохраняет то, что пришло.
    """
    if not query:
        return

    st.session_state.messages.append({"role": "user", "content": query})

    start = time.perf_counter()
    result = ask(query)
    elapsed = time.perf_counter() - start  # время ответа — считается только здесь, локально

    st.session_state.messages.append({
        "role": "assistant",
        "content": result["answer"],
        "latency": elapsed,
        "faithfulness": result["faithfulness"],
        "relevance": result["relevance"],
        "recall": result["recall"],        # None, если это не один из 15 эталонных вопросов
        "precision": result["precision"],  # None, если это не один из 15 эталонных вопросов
        "ok": result["ok"],
        "query": query,
        "is_eval_question": query in EVAL_QUERY_TO_ID,
    })


# Если первый вопрос был введён на главной странице — обработать его здесь.
if "pending_first_query" in st.session_state:
    first_query = st.session_state.pop("pending_first_query")
    send_query(first_query)


for message in st.session_state.messages:
    role_class = "user-message" if message["role"] == "user" else "bot-message"
    with st.chat_message(message["role"]):
        st.markdown(f'<div class="{role_class}">{message["content"]}</div>', unsafe_allow_html=True)

        if message["role"] == "assistant" and "latency" in message:
            if message.get("ok") is False:
                st.markdown(
                    f'<div style="font-size:12px;color:#e07a5f;margin-top:-8px;margin-bottom:8px;">'
                    f'⚠ Запрос не выполнен · ⏱ {message["latency"]:.2f} с</div>',
                    unsafe_allow_html=True,
                )
            else:
                parts = [f"⏱ {message['latency']:.2f} с"]

                relevance = message.get("relevance")
                if relevance is not None:
                    parts.append(f"Релевантность: {relevance}/10")

                precision = message.get("precision")
                recall = message.get("recall")
                if precision is not None and recall is not None:
                    parts.append(f"Precision: {precision}%")
                    parts.append(f"Recall: {recall}%")

                st.markdown(
                    f'<div style="font-size:12px;color:#8a8a92;margin-top:-8px;margin-bottom:8px;">'
                    f'{" · ".join(parts)}</div>',
                    unsafe_allow_html=True,
                )


def continue_chat():
    query = st.session_state.chat_page_input
    send_query(query)
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