import numpy as np
from sentence_transformers import SentenceTransformer
from chromadb import EmbeddingFunction, Embeddings
import torch


class F2LLMEmbeddingFunction(EmbeddingFunction):
    def __init__(self, model_name: str = "codefuse-ai/F2LLM-v2-0.6B"):
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Используем устройство: {device}")

        self.model = SentenceTransformer(
            model_name,
            model_kwargs={"torch_dtype": "bfloat16"},
            device=device
        )
        # Флаг — ChromaDB будет выставлять его сам через query/add
        self._is_query = False

    def __call__(self, input: list[str]) -> Embeddings:
        """
        ChromaDB вызывает этот метод и для документов (add),
        и для запросов (query) — различаем через флаг.
        """
        if self._is_query:
            embeddings = self.model.encode_query(input)
        else:
            embeddings = self.model.encode_document(input)

        # ChromaDB ожидает list[list[float]]
        return embeddings.tolist()

    def encode_queries(self, queries: list[str]) -> Embeddings:
        """Явный метод для запросов — используем в retriever вручную."""
        embeddings = self.model.encode_query(queries)
        return embeddings.tolist()

    def encode_documents(self, documents: list[str]) -> Embeddings:
        """Явный метод для документов — используем в indexer вручную."""
        embeddings = self.model.encode_document(documents)
        return embeddings.tolist()