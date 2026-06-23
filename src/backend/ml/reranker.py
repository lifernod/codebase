from sentence_transformers import CrossEncoder

from python.utils.chunker import Chunk

model = CrossEncoder("Qwen/Qwen3-Reranker-0.6B")


def rerank_chunks(query: str, chunks: list[Chunk]) -> list[Chunk]:
    """
    Рассчитывает очки очки соответствия запросу для каждого чанка и возвращает отсортированный список наиболее релевантных чанков.
    :param query: Запрос пользователя
    :param chunks: Чанки, полученные из поиска
    :return: Топ 5 релевантных чанков
    """

    text_chunks = [one_chunk.chunk for one_chunk in chunks]
    pairs = [(query, chunk) for chunk in text_chunks]
    scores = model.predict(pairs)
    for i in range(len(chunks)):
        chunks[i].score = float(scores[i])
    res = sorted(chunks, key=lambda x: x.score, reverse=True)[:5]
    return res
