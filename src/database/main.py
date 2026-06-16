import chromadb
from chromadb.utils import embedding_functions
import sqlite3
import time
from pathlib import Path
from ..backend.python.utils.chunker import get_all_chunks
from .bm25_retriever import *
from .embedder import F2LLMEmbeddingFunction

ef = F2LLMEmbeddingFunction()

DATA_DIR = Path(__file__).parent.parent.parent / "data"

chroma_client = chromadb.PersistentClient(path=str(DATA_DIR / "chroma"))

collection = chroma_client.get_or_create_collection(
    name="codebase",
    metadata={"hnsw:space": "cosine"}
)

def create_and_save_chunks_from_file(path: str):
    '''
    Функция для создания чанков из папки проекта и их сохранения
    Пересоздаёт существующий набор чанков
    Args:
        path: путь до папки с файлами проекта для обработки и сохранения (будет переработано для работы с выдаваемым распаковщиком текстом)

    Returns: не возвращает ничего

    '''

    chroma_client.delete_collection("codebase")

    collection = chroma_client.get_or_create_collection(
        name="codebase",
        metadata={"hnsw:space": "cosine"}
    )

    chunks = get_all_chunks(path)
    print(f"Got chunks: {len(chunks)}")

    ids = [i["id"] for i in chunks]
    docs = [i["chunk"] for i in chunks]
    metadatas = [i["metadata"] for i in chunks]

    # Батчинг вместо одного вызова на все чанки
    batch_size = 16
    all_embeddings = []

    for i in range(0, len(docs), batch_size):
        batch = docs[i:i + batch_size]
        print(f"Эмбеддинг батча {i // batch_size + 1}/{(len(docs) + batch_size - 1) // batch_size}...")
        batch_embeddings = ef.encode_documents(batch)
        all_embeddings.extend(batch_embeddings)

    print("Embeddings готовы, добавляем в коллекцию...")
    collection.upsert(
        ids=ids,
        documents=docs,
        embeddings=all_embeddings,
        metadatas=metadatas
    )
    print("added to collection")

    build_bm25_index(docs, metadatas)
    print("added to bm25")

def get_chunks_by_query(vec_queries:list[str], bm25_query:str) -> list[dict]:
    '''
    Функция для получения топ-5 чанков по каждому из 3-х (предполагаемо) запросов, собираемых из векторной бд и bm25
    Args:
        vec_queries: запросы векторной бд (предполагается 2 - прямой от пользователя и изменённый
        bm25_query: запрос к bm25, предполагается прямой от пользователя, но может быть и иной

    Returns: список словарей-чанков с полями chunk_text и filepath

    '''
    query_embeddings = ef.encode_queries(vec_queries)
    vec_results = collection.query(
        query_embeddings=query_embeddings,
        n_results=5
    )

    bm25_results = search_bm25(bm25_query)

    results = []
    for i in range(len(vec_results["ids"])):
        docs = vec_results["documents"][i]
        metas = vec_results["metadatas"][i]

        for j in range(len(docs)):
            results.append({"chunk_text":docs[j], "filepath":metas[j]["path"]})

    for i in range(len(bm25_results)):
        results.append({"chunk_text":bm25_results[i]["code"], "filepath":bm25_results[i]["metadata"]["path"]})

    return results