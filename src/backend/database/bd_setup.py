import chromadb
from chromadb.utils import embedding_functions
import sqlite3
import time
from pathlib import Path
from python.utils.chunker import Chunk
from .bm25_retriever import *
from .embedder import F2LLMEmbeddingFunction

ef = F2LLMEmbeddingFunction()

chroma_client = chromadb.PersistentClient(path=str(Path(__file__).parent.parent / "data" / "chroma"))

collection = chroma_client.get_or_create_collection(
    name="codebase",
    metadata={"hnsw:space": "cosine"}
)

def save_chunks(chunks: list[Chunk]):
    '''
    Функция для сохранения чанков в векторную бд и bm25.
    Пересоздаёт существующий набор чанков
    Args:
        chunks: Список всех чанков архива

    Returns: не возвращает ничего
    '''

    global collection

    existing = [c.name for c in chroma_client.list_collections()]

    if "codebase" in existing:
        chroma_client.delete_collection("codebase")

    collection = chroma_client.get_or_create_collection(
        name="codebase",
        metadata={"hnsw:space": "cosine"}
    )

    print(f"Got chunks: {len(chunks)}")

    ids = [i.id for i in chunks]
    docs = [i.chunk for i in chunks]
    metadatas = [i.metadata for i in chunks]

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

def get_chunks_by_query(vec_queries:list[str], bm25_query:str) -> list[Chunk]:
    '''
    Функция для получения топ-5 чанков по каждому из 3-х (предполагаемо) запросов, собираемых из векторной бд и bm25
    Args:
        vec_queries: запросы векторной бд (предполагается 2 - прямой от пользователя и изменённый
        bm25_query: запрос к bm25, предполагается прямой от пользователя, но может быть и иной

    Returns: список чанков
    '''

    global collection

    query_embeddings = ef.encode_queries(vec_queries)
    vec_results = collection.query(
        query_embeddings=query_embeddings,
        n_results=5
    )

    bm25_results = search_bm25(bm25_query)

    results = []
    for i in range(len(vec_results["ids"])):
        ids = vec_results["ids"][i]
        docs = vec_results["documents"][i]
        metas = vec_results["metadatas"][i]

        for j in range(len(docs)):
            results.append(Chunk(id=ids[j],chunk=docs[j], metadata=metas[j]))

    for i in range(len(bm25_results)):
        results.append(Chunk(id=f"bm25_result_{i}",chunk=bm25_results[i]["code"], metadata=bm25_results[i]["metadata"]))

    return results