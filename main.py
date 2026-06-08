import shutil
import tempfile
import time
import zipfile
from pathlib import Path

from tabulate import tabulate
from fastapi import FastAPI, UploadFile, File, HTTPException
from starlette.status import HTTP_400_BAD_REQUEST

from src.api.parse_archive import process_archive
from src.api.types.process_response import ProcessResponse

app = FastAPI()

@app.post("/api/upload")
async def upload_archive(file: UploadFile = File(...)) -> ProcessResponse:
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

    # Print performance results
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
