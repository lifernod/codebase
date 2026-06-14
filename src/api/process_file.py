from pathlib import Path


def process_file(path: Path) -> bool:
    """
    Обрабатывает файл по входящему пути.
    :param path: Путь до .py файла
    :return: Успешно ли завершена обработка?
    """
    source = path.read_text(
        encoding="utf-8",
        errors="ignore"
    )

    # TODO: Заменить вызов
    # metadata = prepare_metadata()
    # chunk = prepare_chunk_for_database(metadata)
    # return chunk
    return True