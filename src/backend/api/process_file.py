from pathlib import Path
from python.utils.chunker import Chunk, get_all_chunks_of_file


def process_file(path: Path) -> list[Chunk]:
    """
    Обрабатывает файл по входящему пути.
    :param path: Путь до .py файла
    :return: Успешно ли завершена обработка?
    """
    return get_all_chunks_of_file(path)
