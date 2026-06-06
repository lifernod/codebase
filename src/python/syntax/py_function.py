import ast
from dataclasses import dataclass, field

from . import PyColonPair, parse_colon_pair
from ..metadata import BodyMeta, AnnotatedMeta, PositionMeta
from ..utils import unparse_annotation


@dataclass
class PyFunction(PositionMeta, AnnotatedMeta, BodyMeta):
    """
    Сигнатура функции.
    Используется для представления top-level функций и методов класса.

    Attributes:
        name (str): Имя функции.
        related_class_name (str | None): Имя класса, для которого функция является методом. Если не является, то `None` (default = `None`).
        is_async (bool): Является ли функция асинхронной (default = `None`).
        args (list[PyColonPair]): Список аргументов функции (default = `[]`).
        return_ty (str | None): Тип возвращаемого значения. Если не указан явно, то `None`. (default = `None`)

    Examples:
        >>> def hello(world: str) -> str: ...
        PyFunction(
            name="hello",
            related_class_name=None,
            is_async=False,
            args=[PyColonPair(name="world", ty="str")],
            return_ty="str"
        )
    """

    name: str
    related_class_name: str | None = field(default=None)

    is_async: bool = field(default=False)

    args: list[PyColonPair] = field(default_factory=list)
    return_ty: str | None = field(default=None)


#########################################################################
## Parsers
#########################################################################

def parse_function(ast_node: ast.FunctionDef | ast.AsyncFunctionDef, class_name: str | None = None) -> PyFunction:
    """
    Парсит указанный узел в `PyFunction`.
    Узел должен представлять собой либо функцию (в т.ч. метод класса) (`ast.FunctionDef`),
    либо асинхронную функцию (в т.ч. метод класса) (`ast.AsyncFunctionDef`).

    :param ast_node: Узел
    :return: PyFunction
    """
    name = ast_node.name

    line_start = ast_node.lineno
    line_end = ast_node.end_lineno
    col_start = ast_node.col_offset
    col_end = ast_node.end_col_offset

    doc = ast.get_docstring(ast_node)
    is_async = isinstance(ast_node, ast.AsyncFunctionDef)

    args = []
    for arg in ast_node.args.args:
        if arg.arg == 'self' and class_name is not None:
            args.append(parse_colon_pair(arg, explicit_type=class_name))
            continue
        args.append(parse_colon_pair(arg))

    return_ty = unparse_annotation(ast_node.returns)

    body = ast.unparse(ast_node.body)

    return PyFunction(
        name=name,
        related_class_name=class_name,
        line_start=line_start,
        line_end=line_end,
        col_start=col_start,
        col_end=col_end,
        doc=doc,
        is_async=is_async,
        args=args,
        return_ty=return_ty,
        body_str=body
    )
