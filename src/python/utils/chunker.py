def create_global_chunk(module_data: list[dict]) -> list[dict]:
    chunks = []
    file_path = module_data["path"]

    global_text_parts = [f"# Путь: {file_path}"]

    # Импорты
    if module_data.get("imports"):
        global_text_parts.append("\n# Импорты:")
        for imp in module_data["imports"]:
            if imp["name"] and imp["name"] != "None":
                global_text_parts.append(f"from {imp['module']} import {imp['name']}")
            else:
                global_text_parts.append(f"import {imp['module']}")

    # Глобальные переменные
    if module_data.get("assigns"):
        global_text_parts.append("\n# Глобальные переменные:")
        for assign in module_data["assigns"]:
            global_text_parts.append(f"{assign['name']} = {assign['value']}")

    # Код верхнего уровня
    if module_data.get("top_level_code"):
        global_text_parts.append("\n# Логика выполнения верхнего уровня:")
        for code_block in module_data["top_level_code"]:
            global_text_parts.append(code_block["code"])

    # # Функции
    # if module_data.get("functions"):
    #     global_text_parts.append("\n# Доступные функции:")
    #     for func in module_data["functions"]:
    #         global_text_parts.append(f"def {func['name']}")
    #
    # # Классы
    # if module_data.get("classes"):
    #     global_text_parts.append("\n# Доступные классы:")
    #     for c in module_data["classes"]:
    #         global_text_parts.append(f"Class {c['name']}")

    global_chunk = {
        "id": f"{file_path}:global",
        "chunk": "\n".join(global_text_parts),
        "metadata": {
            "chunk_type": "global_module",
            "path": file_path,
            "doc": module_data["doc"]
            # "calls_json": json.dumps(module_data.get("calls", []))  # Храним граф вызовов в метаданных
        }
    }
    chunks.append(global_chunk)
    return chunks


def create_chunks(module_data: list[dict]) -> list[str]:
    chunks = []
    file_path = module_data["path"]

    for func in module_data.get("functions", []):
        func_text = (
            f"Путь: {file_path}\n"
            f"Название: {func['name']}\n"
            f"Возвращаемый тип: {func['return_ty']}\n"
            f"Код функции:\n{func['body_str']}"
        )

        func_chunk = {
            "id": f"{file_path}:function:{func['name']}:{func['line_start']}",
            "chunk": func_text,
            "metadata": {
                "doc": func["doc"],
                "chunk_type": "function",
                "path": file_path,
                "name": func["name"],
                "line_start": func["line_start"],
                "line_end": func["line_end"],
                "is_async": str(func["is_async"])
                # "calls_json": json.dumps(func.get("calls", []))  # Вызовы внутри конкретной функции
            }
        }
        chunks.append(func_chunk)

    for c in module_data.get("classes", []):
        class_name = c["name"]

        for method in c.get("methods", []):
            method_text = (
                f"Путь: {file_path}\n"
                f"Класс: {class_name}\n"
                f"Название: {method['name']}\n"
                f"Возвращаемый тип: {method['return_ty']}\n"
                f"Код метода:\n{method['body_str']}"
            )

            chunk_id = f"{file_path}:{class_name}:methodс:{method['name']}:{method['line_start']}"

            method_chunk = {
                "id": chunk_id,
                "chunk": method_text,
                "metadata": {
                    "doc": method.get("doc", "None"),
                    "chunk_type": "method",
                    "path": file_path,
                    "class_name": class_name,
                    "name": method["name"],
                    "line_start": method["line_start"],
                    "line_end": method["line_end"],
                    "is_async": str(method["is_async"]),
                    # "calls_json": json.dumps(method.get("calls", []))
                }
            }
            chunks.append(method_chunk)
    return chunks