import asyncio
import os
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from .process_file import process_file

MIN_FILES_FOR_PARALLEL = 20
POOL = ProcessPoolExecutor(max_workers=os.cpu_count())

async def process_archive(extract_dir: Path) -> list[bool]:
    """
    Обрабатывает .py файлы в архиве по указанному пути.
    :param extract_dir: Путь до разархивированных файлов
    :return: Результат обработки файлов
    """
    loop = asyncio.get_event_loop()

    py_files = [
        p
        for p in extract_dir.rglob("*.py")
        if not should_skip(p)
    ]

    if len(py_files) >= MIN_FILES_FOR_PARALLEL:
        futures = [
            loop.run_in_executor(
                POOL,
                process_file,
                path
            )
            for path in py_files
        ]

        return await asyncio.gather(*futures)
    else:
        return [process_file(f) for f in py_files]

#########################################################################
## Utils
#########################################################################
EXCLUDED_DIRS = {
    "venv",
    ".venv",
    "__pycache__"
}

def should_skip(path: Path) -> bool:
    """
    Проверяет следует ли исключить указанный путь из парсинга
    :param path: Путь
    :return: Исключить?
    """
    if any(part in EXCLUDED_DIRS for part in path.parts):
        return True

    if path.name == "__init__.py":
        return True

    return False