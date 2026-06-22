"""
Список из 15 заранее прописанных eval-вопросов.
Источник: eval_questions.json (предоставлен бэкендером).

Используется на странице метрик, чтобы:
1. Дать пользователю возможность быстро отправить ровно эти вопросы в чат
   (тогда бэкенд распознает их и дополнительно вернёт recall/precision).
2. Понять, какие из 15 эталонных вопросов уже были заданы и получили
   полную оценку (с recall/precision), а какие ещё нет.
"""

import json
from pathlib import Path

_EVAL_FILE = Path(__file__).parent / "eval_questions.json"


def load_eval_questions() -> list[dict]:
    """Возвращает список словарей вида {question_id, query, language, difficulty, category, ...}."""
    if not _EVAL_FILE.exists():
        return []
    with open(_EVAL_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


EVAL_QUESTIONS = load_eval_questions()

# Быстрый доступ "текст вопроса -> question_id", чтобы по запросу пользователя
# можно было определить, является ли это одним из 15 эталонных вопросов.
EVAL_QUERY_TO_ID = {q["query"]: q["question_id"] for q in EVAL_QUESTIONS}