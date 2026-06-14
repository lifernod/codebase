import ast


class TopLevelCallVisitor(ast.NodeVisitor):
    def __init__(self):
        self.calls = []

    def visit_Call(self, node):
        call_name = resolve_call_name(node.func)
        self.calls.append({
            "name": call_name,
            "line": node.lineno,
            "code": ast.unparse(node)
        })
        self.generic_visit(node)

    """
    Переопределяем методы, чтобы парсер не доставал
    лишние зависимости на глобальном уровне
    """
    def visit_FunctionDef(self, node):
        # ИГНОРИРУЕМ внутренности объявлений функций!
        # Мы не идем вглубь def, так как их обработает parse_function
        pass

    def visit_AsyncFunctionDef(self, node):
        # ИГНОРИРУЕМ асинхронные функции
        pass

    def visit_ClassDef(self, node):
        # ИГНОРИРУЕМ внутренности классов
        pass


def resolve_call_name(node: ast.expr) -> str:
    if isinstance(node, ast.Name):
        return node.id
    elif isinstance(node, ast.Attribute):
        base = resolve_call_name(node.value)
        return f"{base}.{node.attr}" if base else node.attr
    elif isinstance(node, ast.Call):
        return f"{resolve_call_name(node.func)}()"
    else:
        return ast.unparse(node)