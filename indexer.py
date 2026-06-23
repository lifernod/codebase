import asyncio
from pathlib import Path
from sys import argv

from src.backend.api.parse_archive import process_archive
from src.backend.database.bd_setup import save_chunks


async def process_code():
    if len(argv) != 2:
        print("Не указан путь до директории, которую необходимо обработать")
        exit(1)

    p = Path(argv[1])
    if not p.exists() or not p.is_dir():
        print(
            "Указанный путь не существует или не является директорией: "
            + str(p.absolute())
        )
        exit(1)

    (count, chunks) = await process_archive(p)
    save_chunks(chunks)
    print(f"Работа завершена успешно: Сохранено чанков {count}")


if __name__ == "__main__":
    asyncio.run(process_code())
