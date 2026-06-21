import streamlit as st
import pandas as pd
from utils import render_sidebar, load_css
from eval_questions import EVAL_QUESTIONS, EVAL_QUERY_TO_ID

st.set_page_config(page_title="Метрики", layout="centered", initial_sidebar_state="expanded")

load_css("style.css")

if "messages" not in st.session_state:
    st.session_state.messages = []

render_sidebar()

INDEXED_FILES = 84  # TODO: подтянуть из ответа /api/upload, если нужно динамически


def get_eval_results() -> dict:
    """
    Возвращает {question_id: message} только для тех eval-вопросов,
    на которые уже был получен УСПЕШНЫЙ ответ (ok=True) с precision/recall.
    """
    results = {}
    for message in st.session_state.messages:
        if message["role"] != "assistant" or "latency" not in message:
            continue
        if message.get("ok") is False:
            continue
        query = message.get("query")
        qid = EVAL_QUERY_TO_ID.get(query)
        if qid is not None and message.get("precision") is not None:
            results[qid] = message
    return results


def build_general_dataframe() -> pd.DataFrame:
    """
    DataFrame для общей статистики (latency, faithfulness/relevance)
    по ВСЕМ успешным ответам, включая обычные вопросы вне eval-набора.
    """
    rows = []
    qid = 0
    for message in st.session_state.messages:
        if message["role"] != "assistant" or "latency" not in message:
            continue
        if message.get("ok") is False:
            continue
        qid += 1
        rows.append({
            "id": qid,
            "query": message.get("query", "—"),
            "faithfulness": message.get("faithfulness", 0),
            "relevance": message.get("relevance", 0),
            "latency": message["latency"],
            "is_eval": message.get("is_eval_question", False),
        })
    return pd.DataFrame(rows)


# ── Fallback styles ───────────────────────────────────────────────────────


st.markdown("<div class='page-heading'>Метрики качества поиска</div>", unsafe_allow_html=True)

general_df = build_general_dataframe()
eval_results = get_eval_results()

# ── KPI cards ─────────────────────────────────────────────────────────────
if not general_df.empty:
    mean_latency = general_df["latency"].mean()
    mean_relevance = general_df["relevance"].mean()
else:
    mean_latency = 0.0
    mean_relevance = 0.0

if eval_results:
    mean_precision = sum(m["precision"] for m in eval_results.values()) / len(eval_results)
    mean_recall = sum(m["recall"] for m in eval_results.values()) / len(eval_results)
else:
    mean_precision = None
    mean_recall = None

kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    precision_display = f"{mean_precision:.0f}%" if mean_precision is not None else "—"
    st.markdown(f"""
    <div class="metric-box">
        <div class="metric-box-label">PRECISION</div>
        <div class="metric-box-value metric-green">{precision_display}</div>
        <div class="metric-box-sub">{len(eval_results)}/{len(EVAL_QUESTIONS)} эталонных вопросов</div>
    </div>
    """, unsafe_allow_html=True)

with kpi2:
    recall_display = f"{mean_recall:.0f}%" if mean_recall is not None else "—"
    st.markdown(f"""
    <div class="metric-box">
        <div class="metric-box-label">RECALL</div>
        <div class="metric-box-value metric-blue">{recall_display}</div>
        <div class="metric-box-sub">По эталонным вопросам</div>
    </div>
    """, unsafe_allow_html=True)

with kpi3:
    st.markdown(f"""
    <div class="metric-box">
        <div class="metric-box-label">AVG LATENCY</div>
        <div class="metric-box-value metric-purple">{mean_latency:.2f} с</div>
        <div class="metric-box-sub">По всем {len(general_df)} запросам</div>
    </div>
    """, unsafe_allow_html=True)

with kpi4:
    st.markdown(f"""
    <div class="metric-box">
        <div class="metric-box-label">INDEXED FILES</div>
        <div class="metric-box-value metric-green">{INDEXED_FILES}</div>
        <div class="metric-box-sub">Python файлов</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height:24px;'></div>", unsafe_allow_html=True)

# ── Charts: latency + relevance over all queries ────────────────────────────
if not general_df.empty:
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.markdown("""
        <div class="chart-card">
            <div class="chart-card-title">Время ответа (latency)</div>
        """, unsafe_allow_html=True)
        latency_chart_df = general_df.set_index("id")[["latency"]].rename(columns={"latency": "Latency, с"})
        st.line_chart(latency_chart_df, height=300, color="#60a5fa")
        st.markdown("</div>", unsafe_allow_html=True)

    with chart_col2:
        st.markdown("""
        <div class="chart-card">
            <div class="chart-card-title">Релевантность по запросу</div>
        """, unsafe_allow_html=True)
        relevance_chart_df = general_df.set_index("id")[["relevance"]].rename(columns={"relevance": "Relevance (0-10)"})
        st.bar_chart(relevance_chart_df, height=300, color="#a855f7")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='height:24px;'></div>", unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="metric-box" style="text-align:center; padding:32px 20px;">
        <div class="metric-box-sub" style="font-size:14px;">
            Пока нет данных — задайте хотя бы один вопрос в чате.
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<div style='height:24px;'></div>", unsafe_allow_html=True)

# ── 15 eval questions: status + quick launch ────────────────────────────────
st.markdown("""
<div class="chart-card-title" style="font-size:16px;margin-bottom:14px;">
    15 эталонных вопросов
</div>
""", unsafe_allow_html=True)

for q in EVAL_QUESTIONS:
    qid = q["question_id"]
    result = eval_results.get(qid)

    if result:
        status_class = "done"
        status_text = f"✓ Precision {result['precision']}% · Recall {result['recall']}%"
    else:
        status_class = "pending"
        status_text = "Не задан"

    row_col, btn_col = st.columns([5, 1])
    with row_col:
        st.markdown(f"""
        <div class="eval-row {status_class}">
            <span>{q['query']}</span>
            <span style="font-size:11px; color:#8a8a92;">{status_text}</span>
        </div>
        """, unsafe_allow_html=True)
    with btn_col:
        if st.button("Задать", key=f"eval_btn_{qid}", use_container_width=True):
            st.session_state.pending_first_query = q["query"]
            st.switch_page("pages/chat.py")

st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)

# ── Detailed table for all queries ───────────────────────────────────────────
if not general_df.empty:
    with st.expander("Подробная таблица по всем запросам"):
        display_df = general_df.copy()
        display_df["latency"] = display_df["latency"].apply(lambda x: f"{x:.2f} с")
        display_df["is_eval"] = display_df["is_eval"].apply(lambda x: "✓" if x else "")
        display_df = display_df.rename(columns={
            "id": "№",
            "query": "Запрос",
            "faithfulness": "Faithfulness",
            "relevance": "Relevance",
            "latency": "Latency",
            "is_eval": "Эталонный?",
        })
        st.dataframe(display_df, use_container_width=True, hide_index=True)