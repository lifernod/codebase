import shutil
import tempfile
import time
import zipfile
from pathlib import Path

from fastapi.params import Query
from starlette import status
from tabulate import tabulate
from fastapi import FastAPI, UploadFile, File, HTTPException
from starlette.status import HTTP_400_BAD_REQUEST

from src.api.parse_archive import process_archive
from src.api.types.process_response import ProcessResponse

app = FastAPI(
    title="codebase.py",
    version="0.0.1",
    description="Понимаем ваш код и помогаем вам понять его"
)

#########################################################################
## Пинг - понг
#########################################################################
@app.get(
    "/api/ping",
    status_code=200,
    summary="Проверка жизнеспособности сервера",
    description="Если возвращает `pong`, то все номарльно :)",
)
async def ping():
    return "pong"

#########################################################################
## Загрузка файлов
#########################################################################
@app.post(
    "/api/upload",
    tags=["files"],
    summary="Загрузка и обработка архива с кодом."
)
async def upload_archive(file: UploadFile = File(description="Архив с файлами")) -> ProcessResponse:
    """
    Поддерживается только `.zip` архивы, а все файлы, кроме `.py` пропускаются (не обрабатываются).
    """
    if not file.filename.lower().endswith('.zip'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Допускаются только файлы с расширением .zip"
        )

    work_start = time.perf_counter()

    with tempfile.TemporaryDirectory() as tmpdir:
        archive_path = Path(tmpdir) / file.filename

        copy_start = time.perf_counter()
        with open(archive_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        copy_end = time.perf_counter()

        extract_dir = Path(tmpdir) / "extract"
        extract_dir.mkdir()

        zip_extraction_start = time.perf_counter()
        try:
            with zipfile.ZipFile(archive_path) as archive:
                archive.extractall(extract_dir)
        except zipfile.BadZipFile:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Приложенный файл не является '.zip' архивом")
        zip_extraction_end = time.perf_counter()

        processing_start = time.perf_counter()
        results = await process_archive(extract_dir)
        processing_end = time.perf_counter()

    work_end = time.perf_counter()

    # Показать перформанс обработки
    print(f"Количество файлов: {len(results)}")
    print(tabulate(
        [
            ["Копирование архива", copy_end-copy_start],
            ["Разархивирование", zip_extraction_end-zip_extraction_start],
            ["Обработка", processing_end-processing_start],
            ["Итог", work_end-work_start]
        ],
        headers=["Операция", "Затраченное время, с."],
        tablefmt="fancy_grid"
    ))

    total = len(results)
    ok = sum([1 for r in results if r])
    fail = total - ok

    return ProcessResponse(
        ok=ok,
        fail=fail,
        total=total
    )

#########################################################################
## Вопрос
#########################################################################
@app.get(
    "/api/ask",
    deprecated=True,
    summary="Ответ на вопрос пользователя",
    description="Not implemented yet",
    status_code=status.HTTP_501_NOT_IMPLEMENTED
)
async def ask(q: str):
    # TODO: Обработать вопрос и вернуть результат
    return HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)
