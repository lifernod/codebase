from dataclasses import dataclass


@dataclass
class FinalAnswer:
    """
    Финальный ответ LLM.

    Attributes:
        answer (str): ответ ллмки
        faithfulness (int): параметр от 0 до 10 насколько ответ основывается на чанках
        relevance (int): параметр от 0 до 10 насколько релевантен ответ
        precision (int | None): Precision@5 от 0 до 100, если query из списка заготовленных вопросов
        recall (int | None): Recall@5 от 0 до 100, если query из списка заготовленных вопросов
    """

    answer: str
    faithfulness: int
    relevance: int
    precision: int | None = None
    recall: int | None = None
