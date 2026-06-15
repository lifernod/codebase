import chromadb
from chromadb.utils import embedding_functions
import sqlite3
from pathlib import Path

sentence_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="microsoft/codebert-base"
)

DATA_DIR = Path(__file__).parent.parent.parent / "data"

chroma_client = chromadb.PersistentClient(path=str(DATA_DIR / "chroma"))

collection = chroma_client.get_or_create_collection(
    name="codebase",
    metadata={"hnsw:space": "cosine"}
)

def add_chunks(docs:dict):
    collection.add(
        ids=docs["ids"],
        documents=docs["chunk"],
        metadatas=docs["metadatas"]
    )

def get_chunks(queries:str) -> dict:
    results = collection.query(
        query_texts=[queries],
        n_results=5
    )

    return dict(results)