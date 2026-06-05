import ast
from dataclasses import dataclass, field

from src.python.metadata.position_meta import PositionMeta
from src.python.utils.ast_utils import unparse_annotation


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

def parse_colon_pair(ast_node: ast.arg | ast.AnnAssign) -> PyColonPair:
    """
    Парсит указанный узел в `PyColonPair`.
    Узел должен представлять собой либо аргумент функции (`ast.arg`),
    либо поле класса (`ast.AnnAssign`).

    :param ast_node: Узел
    :return: PyColonPair
    """
    if isinstance(ast_node, ast.arg):
        return PyColonPair(
            name=ast_node.arg,
            ty=unparse_annotation(ast_node.annotation)
        )
    else:
        # TODO: сделать проверку на различные типы ast_node.target
        return PyColonPair(
            name=ast_node.target.id,
            ty=unparse_annotation(ast_node.annotation)
        )
