import os
import sys
import json
import logging
from src.python.utils.as_str_dict import as_str_dict
from src.python.syntax.py_module import parse_module

from src.python.utils.chunker import *

path = 'archive/gymhero/gymhero'

if __name__ == "__main__":
    all_project_chunks = []

    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)

                try:
                    with open(file_path, 'rb') as f:
                        content = f.read()

                    module = parse_module(file_path, content)
                    metadata = as_str_dict(module)

                    global_chunk = create_global_chunk(metadata)
                    atomic_chunks = create_chunks(metadata)
                    all_project_chunks.extend(global_chunk)
                    all_project_chunks.extend(atomic_chunks)
                except Exception as e:
                    pass

    print("-" * 50)
    print(f"Индексация завершена успешно!")
    print(f"Всего сгенерировано чанков для ChromaDB: {len(all_project_chunks)}")
    print(json.dumps(all_project_chunks, indent=4, ensure_ascii=False))

    """
    Считаем длины чанков и делим нацело на средние 3.2,
    чтобы получить примерные затраты по токенам
    
    MAX: 650 (мб такие придется резать)
    MIN: 13
    AVG: 221
    Количество чанков, требующих больше 500 токенов: 4
    """

    lens_of_chunks = []
    lens_of_chunks_over_500 = []
    count = 0
    for chunk in all_project_chunks:
        n = len(chunk["chunk"]) // 3.2
        lens_of_chunks.append(n)
        if n >= 500:
            lens_of_chunks_over_500.append(n)
    print(lens_of_chunks)
    print(lens_of_chunks_over_500)