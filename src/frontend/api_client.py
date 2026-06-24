"""
Клиент для общения с FastAPI-бэкендом CodeLens.

Схема бэкенда:
    GET /api/ask?q=<вопрос>

Ответ всегда содержит:
    {"answer": str, "faithfulness": 0-10, "relevance": 0-10}

Для заранее прописанных eval-вопросов (см. eval_questions.json) ответ
дополнительно содержит:
    {"recall": 0-100, "precision": 0-100}

Время ответа НЕ приходит от бэкенда — оно считается локально на фронте
(в chat.py, через time.perf_counter() вокруг вызова ask()).
"""
import ast

import httpx
import requests
import logging

API_BASE_URL = "http://backend:8000"  # поменяй под свой адрес бэкенда

ASK_ENDPOINT = f"{API_BASE_URL}/api/ask"
UPLOAD_ENDPOINT = f"{API_BASE_URL}/api/upload"

REQUEST_TIMEOUT = 30.0


def upload_archive(files: dict):
    try:
        response = requests.post(UPLOAD_ENDPOINT, files=files)

        if response.status_code == 200:
            data = response.json()
            if data.get("total", 0) == 0:
                logging.error("В архиве нет .py файлов")
                return {
                    "status": "Ошибка индексации",
                    "files_count": 0,
                    "chunks_count": 0
                }
            return {
                "status": "Проиндексирован",
                "files_count": data.get("total", 0),
                "chunks_count": data.get("chunks", 0)
            }

    except requests.exceptions.RequestException as e:
        logging.error(f"Ошибка запроса: {e}")
        return {
            "status": "Ошибка индексации",
            "files_count": 0,
            "chunks_count": 0
        }



def ask(query: str) -> dict:
    """
    Синхронный вызов GET /api/ask?q=<query>.

    Возвращает dict вида:
        {
            "answer": str,
            "faithfulness": int (0-10),
            "relevance": int (0-10),
            "recall": int | None,      # 0-100, только для eval-вопросов
            "precision": int | None,   # 0-100, только для eval-вопросов
            "ok": bool,                # False = технический сбой запроса
        }

    При сетевой ошибке / таймауте / не-200 ответе возвращает заглушку
    с ok=False вместо падения с исключением.
    """
    try:
        response = httpx.get(
            ASK_ENDPOINT,
            params={"q": query},
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        data = response.json()

        return {
            "answer": data.get("answer", "Не удалось получить ответ."),
            "faithfulness": data.get("faithfulness", 0),
            "relevance": data.get("relevance", 0),
            "recall": data.get("recall"),  # None, если это не eval-вопрос
            "precision": data.get("precision"),  # None, если это не eval-вопрос
            "ok": True,
        }

    except httpx.TimeoutException:
        return _error_result("Сервис не ответил вовремя, попробуйте ещё раз.")
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 501:
            detail = "Эндпоинт /api/ask пока не реализован на бэкенде (501)."
        else:
            detail = f"Сервис вернул ошибку ({e.response.status_code})."
        return _error_result(detail)
    except httpx.RequestError:
        return _error_result(
            "Не удалось соединиться с сервисом. Проверьте, что бэкенд запущен."
        )


def _error_result(message: str) -> dict:
    return {
        "answer": message,
        "faithfulness": 0,
        "relevance": 0,
        "recall": None,
        "precision": None,
        "ok": False,
    }
