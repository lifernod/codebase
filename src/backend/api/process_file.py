from pathlib import Path
from python.utils.chunker import *


def process_file(path: Path) -> list[Chunk]:
    """
    Обрабатывает файл по входящему пути.
    :param path: Путь до .py файла
    :return: Успешно ли завершена обработка?
    """
    source = path.read_text(
        encoding="utf-8",
        errors="ignore"
    )

    return get_all_chunks_of_file(path)