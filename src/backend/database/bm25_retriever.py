import bm25s
import json
import os
from pathlib import Path

BM25_PATH = Path(__file__).parent.parent.parent / "data/bm25_index"

# Состояние модуля — загружается один раз, живёт всё время работы программы
_retriever = None
_documents = None
_metadatas = None


def _ensure_loaded():
    """Загружает индекс если ещё не загружен."""
    global _retriever, _documents, _metadatas

    if _retriever is not None:
        return  # уже загружен — ничего не делаем

    _retriever = bm25s.BM25.load(BM25_PATH)

    with open(os.path.join(BM25_PATH, "documents.json"), encoding="utf-8") as f:
        data = json.load(f)

    _documents = data["documents"]
    _metadatas = data["metadatas"]


def build_bm25_index(documents: list[str], metadatas: list[dict]):
    """Строит и сохраняет BM25 индекс. Сбрасывает кэш в памяти."""
    global _retriever, _documents, _metadatas

    corpus_tokens = bm25s.tokenize(documents)

    retriever = bm25s.BM25()
    retriever.index(corpus_tokens)

    os.makedirs(BM25_PATH, exist_ok=True)
    retriever.save(BM25_PATH)

    with open(os.path.join(BM25_PATH, "documents.json"), "w", encoding="utf-8") as f:
        json.dump({"documents": documents, "metadatas": metadatas}, f, ensure_ascii=False)

    # Обновляем состояние в памяти — следующий поиск не будет лезть на диск
    _retriever = retriever
    _documents = documents
    _metadatas = metadatas

    print(f"BM25 индекс построен: {len(documents)} документов")


def search_bm25(query: str, n_results: int = 5) -> list[dict]:
    """Поиск по BM25. Индекс загружается один раз при первом вызове."""
    _ensure_loaded()

    query_tokens = bm25s.tokenize([query])
    results, scores = _retriever.retrieve(query_tokens, k=n_results)

    return [
        {
            "code":       _documents[idx],
            "metadata":   _metadatas[idx],
            "bm25_score": float(score),
        }
        for idx, score in zip(results[0], scores[0])
    ]