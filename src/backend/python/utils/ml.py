from dataclasses import dataclass


@dataclass
class FinalAnswer:
    answer: str
    faithfulness: int
    relevance: int
    precision: int | None = None
    recall: int | None = None


