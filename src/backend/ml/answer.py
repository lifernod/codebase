import json
import os
from typing import Tuple, List
from dotenv import load_dotenv
from httpx import AsyncClient
from json import load

from python.utils.chunker import Chunk
from python.utils.ml import FinalAnswer
from logging import info

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

SYSTEM_PROMPT = """
You are a RAG agent.

I will provide you with a user query and 3-5 chunks with metadata.
You must answer only based on the information present in the chunks.
If the needed information is not there, politely respond that this information is not found in the codebase. Don't try to come up with an answer if the required code fragments are not there, just answer directly that they are not there.
In case of irrelevant code fragments, do not mention the fragments that were given to you.
Answer in the same language as the user's question — if the question is in Russian, answer in Russian; if in English, answer in English.
Please indicate which files contain the code for what you are explaining (only filenames), and write code fragments (from the chunks given to you).
Write code fragment ALWAYS.

Each chunk is a JSON object.

Evaluate:
- faithfulness: 0 = answer is not based on the chunks at all, 10 = answer is fully based on the chunks
- relevance: 0 = answer is completely irrelevant, 10 = maximally relevant
If no relevant information is found in the provided chunks, return faithfulness and relevance as 0.

Return only JSON without markdown and without ```json wrappers.

Response format:
{{"answer": "Your answer to the user", "faithfulness": 0-10, "relevance": 0-10}}
""".strip()

EVAL_DATA = []
EVAL_FILE_PATH = "eval_questions.json"

if os.path.exists(EVAL_FILE_PATH):
    with open(EVAL_FILE_PATH, "r", encoding="utf-8") as f:
        EVAL_DATA = load(f)
else:
    info(
        f"Файл {EVAL_FILE_PATH} не найден. Метрики Precision и Recall рассчитываться не будут."
    )


def format_user_prompt(query: str, chunks: list[Chunk]) -> str:
    dict_chunks = []
    for c in chunks:
        dict_chunks.append({"id": c.id, "chunk": c.chunk, "metadata": c.metadata})
    return f"User query: {query}\nChunks: {json.dumps(dict_chunks, indent=2, ensure_ascii=False)}"



async def get_llm_response(
    client: AsyncClient, query: str, chunks: List[Chunk]
) -> FinalAnswer:
    """
    Отправляет запрос в OpenRouter API на получение финального ответа пользователю

    :param client: httpx.AsyncClient
    :param query: запрос пользователя
    :param chunks: список словарей чанков
    :return: FinalAnswer
        answer: ответ ллмки
        faithfulness: параметр от 0 до 10 насколько ответ основывается на чанках
        relevance: параметр от 0 до 10 насколько релевантен ответ
        precision: Precision@5 от 0 до 100, если query из списка заготовленных вопросов
        recall: Recall@5 от 0 до 100, если query из списка заготовленных вопросов
    """
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    }
    payload = {
        "model": "google/gemini-2.5-flash-lite",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": format_user_prompt(query, chunks)},
        ],
        "response_format": {"type": "json_object"},
        "provider": {"order": ["Google AI Studio"]},
    }

    precision_val, recall_val = calculate_rag_metrics(query, chunks)

    response = await client.post(url, headers=headers, json=payload)
    if response.status_code != 200:
        return FinalAnswer(
            answer="Сервис временно недоступен, попробуйте позже",
            faithfulness=0,
            relevance=0,
            precision=precision_val,
            recall=recall_val,
        )

    try:
        content = response.json().get("choices")[0].get("message").get("content")
        answer_json = json.loads(content)
    except Exception as e:
        info(f"Ошибка парсинга ответа LLM: {e}", exc_info=True)
        return FinalAnswer(
            answer="Произошла ошибка генерации ответа, попробуйте позже.",
            faithfulness=0,
            relevance=0,
            precision=precision_val,
            recall=recall_val,
        )

    return FinalAnswer(
        answer=answer_json.get("answer", "Произошла ошибка генерации ответа"),
        faithfulness=int(answer_json.get("faithfulness", 0)),
        relevance=int(answer_json.get("relevance", 0)),
        precision=precision_val,
        recall=recall_val,
    )


def calculate_rag_metrics(
    query: str, chunks: List[Chunk]
) -> Tuple[int | None, int | None]:
    """
    Ищет запрос в базе эталонных вопросов и считает Precision@5 и Recall@5 (от 0 до 100).
    Возвращает (precision, recall) в виде целых чисел или (None, None), если вопрос не тестовый.
    """
    # Ищем вопрос в загруженных данных (предполагается, что EVAL_DATA уже загружен из eval_questions.json)
    eval_item = next(
        (
            item
            for item in EVAL_DATA
            if item["query"].strip().lower() == query.strip().lower()
        ),
        None,
    )
    if not eval_item:
        return None, None

    correct_chunk_ids = eval_item.get("correct_chunk_ids", [])
    if not correct_chunk_ids:
        return 0, 0

    # Берем топ-5 объектов Chunk
    top_k_chunks = chunks[:5]
    if not top_k_chunks:
        return 0, 0

    true_positives = 0

    for chunk in top_k_chunks:
        # Подготавливаем строку для поиска, объединяя id и значения метаданных
        search_area = (
            f"{chunk.id} {json.dumps(chunk.metadata, ensure_ascii=False)}".lower().replace('\\', '/')
        )
        is_match = False

        for gt_id in correct_chunk_ids:
            # Разбиваем эталонный ID: "gymhero/security.py:create_access_token:12"
            parts = gt_id.split(":")
            if len(parts) >= 2:
                file_path = parts[0].lower()
                name = parts[1].lower()

                # Проверяем, есть ли путь к файлу и имя функции в id или метаданных чанка
                if file_path in search_area and name in search_area:
                    is_match = True
                    break

        if is_match:
            true_positives += 1

    # Считаем метрики в процентах и приводим к int
    precision = int((true_positives / len(top_k_chunks)) * 100)
    recall = int((true_positives / len(correct_chunk_ids)) * 100)
    return precision, recall
