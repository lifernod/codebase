import os
import json


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
            f"# Путь: {file_path}\n"
            f"# Название: {func['name']}\n"
            f"# Возвращаемый тип: {func['return_ty']}\n"
            f"# Код функции:\n{func['body_str']}"
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
                f"# # Путь: {file_path}\n"
                f"# Класс: {class_name}\n"
                f"# Название: {method['name']}\n"
                f"# Возвращаемый тип: {method['return_ty']}\n"
                f"# Код метода:\n{method['body_str']}"
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


def get_all_chunks(path: str) -> list[dict]:
    global count_meya
    all_project_chunks = []
    project_call_stack = {}

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

                    if global_chunk:
                        all_project_chunks.extend(global_chunk)
                    if atomic_chunks:
                        all_project_chunks.extend(atomic_chunks)

                    call_stack_node = get_call_stack_node(metadata)
                    project_call_stack.update(call_stack_node)

                except Exception as e:
                    pass

    try:
        with open('call_stack.json', 'w', encoding='utf-8') as f:
            json.dump(project_call_stack, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Ошибка при сохранении call_stack.json: {e}")

    return all_project_chunks


def get_call_stack_node(module_data: dict) -> dict:
    """
    Формирует узел графа вызовов для конкретного модуля.
    Возвращает словарь вида { "путь_к_файлу": { "global": ..., "functions": ..., "classes": ... } }
    """
    path = module_data.get('path', 'unknown_path')

    node_structure = {
        'imports': module_data.get('imports', []),
        'global': module_data.get('calls', []),
        'functions': {},
        'classes': {}
    }

    if module_data.get("functions"):
        for function in module_data["functions"]:
            node_structure['functions'][function['name']] = function.get('calls', [])

    if module_data.get("classes"):
        for cls in module_data["classes"]:
            class_name = cls['name']
            node_structure['classes'][class_name] = {}

            for method in cls.get("methods", []):
                node_structure['classes'][class_name][method['name']] = method.get('calls', [])

    return {path: node_structure}