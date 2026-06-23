from dataclasses import dataclass
from typing import Dict, List
from json import dumps, loads
import os
from dotenv import load_dotenv
from httpx import AsyncClient

from src.backend.python.utils.chunker import Chunk

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

SYSTEM_PROMPT = """
You are a RAG agent.

I will provide you with a user query and 3-5 chunks with metadata.
You must answer only based on the information present in the chunks.
If the needed information is not there, politely respond that this information is not found in the codebase.
Answer in the same language as the user's question — if the question is in Russian, answer in Russian; if in English, answer in English.

Each chunk is a JSON object.

Evaluate:
- faithfulness: 0 = answer is not based on the chunks at all, 10 = answer is fully based on the chunks
- relevance: 0 = answer is completely irrelevant, 10 = maximally relevant
If no relevant information is found in the provided chunks, return faithfulness and relevance as 0.

Return only JSON without markdown and without ```json wrappers.

Response format:
{{"answer": "Your answer to the user", "faithfulness": 0-10, "relevance": 0-10}}
""".strip()


@dataclass
class LLMResponse:
    """
    Ответ LLM.

    Attributes:
        answer (str): Ответ LLM.
        faithfullness (int): Насколько ответ основывается на реальных чанках.
        relevance (int): Насколько релевантен ответ.
    """

    answer: str
    faithfullness: int
    relevance: int


def format_user_prompt(query: str, chunks: list[Chunk]) -> str:
    return f"User query: {query}\nChunks: {dumps(chunks, indent=2, ensure_ascii=False)}"


async def get_llm_response(
    client: AsyncClient, query: str, chunks: list[Chunk]
) -> LLMResponse:
    """
    Отправляет запрос в OpenRouter API на получение финального ответа пользователю

    :param client: httpx.AsyncClient
    :param query: запрос пользователя
    :param chunks: список словарей чанков
    :return: Ответ LLM
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
    response = await client.post(url, headers=headers, json=payload)
    if response.status_code != 200:
        return LLMResponse(
            answer="Сервис временно недоступен, попробуйте позже",
            faithfullness=0,
            relevance=0,
        )
    answer = response.json().get("choices")[0].get("message").get("content")
    answer_json = loads(answer)
    return LLMResponse(
        answer=answer_json["answer"],
        faithfullness=answer_json["faithfullness"],
        relevance=answer_json["relevance"],
    )
