import ast
from dataclasses import dataclass, field

from ..metadata import PositionMeta
from ..utils import unparse_annotation


@dataclass
class PyColonPair(PositionMeta):
    """
    Пара вида **`name:ty`**, где `name` - название (левая часть), `ty` - тип (правая часть).
    Используется для представления аргументов функции и полей классов.

    Attributes:
        name (str): Название аргумента или поля.
        ty (str | None): Тип аргумента или поля. Если тип не указан явно, то `None` (default = `None`).

    Examples:
        >>> def say(hello: str, world): ...
        [
            PyColonPair(name="hello", ty="str"),
            PyColonPair(name="world", ty=None)
        ]
    """

    name: str
    ty: str | None = field(default=None)


#########################################################################
## Parsers
#########################################################################

def parse_colon_pair(ast_node: ast.arg | ast.AnnAssign, explicit_type: str | None = None) -> PyColonPair:
    """
    Парсит указанный узел в `PyColonPair`.
    Узел должен представлять собой либо аргумент функции (`ast.arg`),
    либо поле класса (`ast.AnnAssign`).

    :param ast_node: Узел
    :param explicit_type: Формированное указание типа. Если указано, то устанавливает `PyColonPair.ty` равным этому значению вне зависимости от реального типа
    :return: PyColonPair
    """

    line_start = ast_node.lineno
    line_end = ast_node.end_lineno
    col_start = ast_node.col_offset
    col_end = ast_node.end_col_offset
    ty = explicit_type if explicit_type is not None else unparse_annotation(ast_node.annotation)

    if isinstance(ast_node, ast.arg):
        return PyColonPair(
            name=ast_node.arg,
            ty=ty,
            line_start=line_start,
            line_end=line_end,
            col_start=col_start,
            col_end=col_end
        )
    else:
        return PyColonPair(
            name=ast_node.target.id,
            ty=ty,
            line_start=line_start,
            line_end=line_end,
            col_start=col_start,
            col_end=col_end
        )
