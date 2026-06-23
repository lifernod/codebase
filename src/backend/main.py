import shutil
import tempfile
import zipfile
from contextlib import asynccontextmanager
from pathlib import Path

import httpx
from starlette import status
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends

from api.process_codebase import process_codebase
from ml.reranker import rerank_chunks
from ml.answer import LLMResponse, get_llm_response
from database.bd_setup import save_chunks, get_chunks_by_query
from src.backend.python.utils import as_str_dict

#########################################################################
## Настройка https.AsyncClient
#########################################################################
limits = httpx.Limits(
    max_connections=10, max_keepalive_connections=5, keepalive_expiry=30.0
)

timeouts = httpx.Timeout(connect=3.0, read=5.0, write=5.0, pool=1.0)


@asynccontextmanager
async def lifespan(app: FastAPI):
    client = httpx.AsyncClient(limits=limits, timeout=timeouts, trust_env=False)
    app.state.client = client
    try:
        yield
    finally:
        await client.aclose()


app = FastAPI(
    title="codebase.py",
    version="0.0.1",
    description="Понимаем ваш код и помогаем вам понять его",
    lifespan=lifespan,
)


def get_http_client() -> httpx.AsyncClient:
    return app.state.client


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
@app.post("/api/upload", tags=["files"], summary="Загрузка и обработка архива с кодом.")
async def upload_archive(file: UploadFile = File(description="Архив с файлами")) -> str:
    """
    Поддерживается только `.zip` архивы, а все файлы, кроме `.py` пропускаются (не обрабатываются).
    """
    if file.filename is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="У файла, что вы загрузили, нет названия",
        )

    if not file.filename.lower().endswith(".zip"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Допускаются только файлы с расширением .zip",
        )

    with tempfile.TemporaryDirectory() as tmpdir:
        archive_path = Path(tmpdir) / file.filename

        with open(archive_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        extract_dir = Path(tmpdir) / "extract"
        extract_dir.mkdir()

        try:
            with zipfile.ZipFile(archive_path) as archive:
                archive.extractall(extract_dir)
        except zipfile.BadZipFile:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Приложенный файл не является '.zip' архивом",
            )

        (count, chunks) = process_codebase(extract_dir)
        save_chunks(chunks)

    return f"Успешно обработано чанков: {count}"


#########################################################################
## Вопрос
#########################################################################
@app.get("/api/ask", deprecated=True, summary="Ответ на вопрос пользователя")
async def ask(q: str, client: httpx.AsyncClient = Depends(get_http_client)) -> str:
    chunks = get_chunks_by_query([q, q], q)
    reranked_chunks = rerank_chunks(q, chunks)
    answer = await get_llm_response(client=client, query=q, chunks=reranked_chunks)
    return str(answer)
