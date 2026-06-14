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

    # TODO: Вызывать на python.syntax.parse_module
    # parse_module()
    return True