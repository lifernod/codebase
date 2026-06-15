import ast
from dataclasses import dataclass


@dataclass
class PyCode:
    """
        Используется для представления top-level кода (If, For, While, Try и т.д.)
        модулей, функций и методов класса
    """
    code: str
    line_start: str
    line_end: str


def parse_code(ast_node: ast.Expr) -> PyCode:
    """
        Парсит указанный узел в `PyCode`.
        Узел должен представлять собой ast.Expr

        :param ast_node: Узел
        :return: PyCode
    """
    return PyCode(
        line_start=str(getattr(ast_node, "lineno", "")),
        line_end=str(getattr(ast_node, "end_lineno", "")),
        code=ast.unparse(ast_node)
    )