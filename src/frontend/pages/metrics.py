import streamlit as st
import pandas as pd
import random
from utils import render_sidebar, load_css

st.set_page_config(page_title="Метрики", layout="centered", initial_sidebar_state="expanded")

load_css("style.css")

if "messages" not in st.session_state:
    st.session_state.messages = []

render_sidebar()

# ── Fallback styles (на случай, если классы ещё не добавлены в style.css) ──


# ── Mock eval data: 15 questions with per-question precision@5 and latency ──
EVAL_QUERIES = [
    "как обрабатываются ошибки авторизации",
    "функция валидации JWT токена",
    "database connection pool setup",
    "pagination for list endpoints",
    "загрузка файлов на сервер",
    "background task queue",
    "настройка CORS политик",
    "caching with Redis",
    "отправка email уведомлений",
    "rate limiting per user",
    "логирование HTTP запросов",
    "health check endpoint",
    "парсинг query параметров",
    "WebSocket connection handler",
    "миграции базы данных Alembic",
]

if "metrics_eval" not in st.session_state:
    random.seed(42)
    rows = []
    for i, q in enumerate(EVAL_QUERIES, start=1):
        precision = random.choice([0.4, 0.6, 0.6, 0.8, 0.8, 1.0])
        latency = round(random.uniform(0.9, 2.8), 2)
        rows.append({
            "id": i,
            "query": q,
            "precision_at_5": precision,
            "latency": latency,
        })
    st.session_state.metrics_eval = rows

eval_data = st.session_state.metrics_eval
df = pd.DataFrame(eval_data)

mean_precision = df["precision_at_5"].mean()
mean_latency = df["latency"].mean()
indexed_files = 84

# ── Page title ────────────────────────────────────────────────────────────────
st.markdown("<div class='page-heading'>Метрики качества поиска</div>", unsafe_allow_html=True)

# ── Top KPI row: 3 cards ─────────────────────────────────────────────────────
kpi1, kpi2, kpi3 = st.columns(3)

with kpi1:
    st.markdown(f"""
    <div class="metric-box">
        <div class="metric-box-label">PRECISION@5</div>
        <div class="metric-box-value metric-green">{mean_precision:.0%}</div>
        <div class="metric-box-sub">Средняя точность</div>
    </div>
    """, unsafe_allow_html=True)

with kpi2:
    st.markdown(f"""
    <div class="metric-box">
        <div class="metric-box-label">AVG LATENCY</div>
        <div class="metric-box-value metric-blue">{mean_latency:.2f} с</div>
        <div class="metric-box-sub">Среднее время задержки</div>
    </div>
    """, unsafe_allow_html=True)

with kpi3:
    st.markdown(f"""
    <div class="metric-box">
        <div class="metric-box-label">INDEXED FILES</div>
        <div class="metric-box-value metric-purple">{indexed_files}</div>
        <div class="metric-box-sub">Python файлов</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height:18px;'></div>", unsafe_allow_html=True)

# ── Bottom row: two chart cards ──────────────────────────────────────────────
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.markdown("""
    <div class="chart-card">
        <div class="chart-card-title">Precision@5 по каждому запросу</div>
    """, unsafe_allow_html=True)

    chart_df = df.set_index("id")[["precision_at_5"]].rename(
        columns={"precision_at_5": "Precision@5"}
    )
    st.bar_chart(
        chart_df,
        height=320,
        color="#a855f7",
    )

    st.markdown("</div>", unsafe_allow_html=True)

with chart_col2:
    st.markdown("""
    <div class="chart-card">
        <div class="chart-card-title">Время ответа (latency)</div>
    """, unsafe_allow_html=True)

    latency_df = df.set_index("id")[["latency"]].rename(
        columns={"latency": "Latency, с"}
    )
    st.line_chart(
        latency_df,
        height=320,
        color="#60a5fa",
    )

    st.markdown("</div>", unsafe_allow_html=True)

# ── Detailed table (optional, collapsible) ──────────────────────────────────
st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)

with st.expander("Подробная таблица по запросам"):
    display_df = df.copy()
    display_df["precision_at_5"] = display_df["precision_at_5"].apply(lambda x: f"{x:.0%}")
    display_df["latency"] = display_df["latency"].apply(lambda x: f"{x:.2f} с")
    display_df = display_df.rename(columns={
        "id": "№",
        "query": "Запрос",
        "precision_at_5": "Precision@5",
        "latency": "Latency",
    })
    st.dataframe(display_df, use_container_width=True, hide_index=True)
