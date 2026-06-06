import ast
from dataclasses import dataclass, field

from ..metadata import PositionMeta
from ..utils import unparse_annotation


@dataclass
class PyAssign(PositionMeta):
    """
    Пара вида **`name:ty=value`**, где `name` - название (левая часть), `ty` - тип (правая часть).
    Используется для представления присвоения.

    Attributes:
        name (str): Название переменной.
        ty (str | None): Тип переменной. Если тип не указан явно, то `None` (default = `None`).
        value (str | None): Значение присваивания. Если не удалось определить значение, то `None`.

    Examples:
        >>> name = "hello"
        PyAssign(
            name="name",
            ty=None,
            value="hello"
        )

        >>> name: str = "hello"
        PyAssign(
            name="name",
            ty="str",
            value="hello"
        )
    """
    name: str
    ty: str | None = field(default=None)
    value: str | None = field(default=None)


#########################################################################
## Parsers
#########################################################################

# TODO: Множественное присваивание и разные виды присваивания
# a = b = ... = 5; a, b = 1, 2; a[0] = 5
def parse_assign(ast_node: ast.Assign | ast.AnnAssign) -> PyAssign | None:
    """
        Парсит указанный узел в `PyAssign`.
        Узел должен представлять собой либо присвоение (`ast.Assign`),
        либо присвоение с аннотацией типа (`ast.AnnAssign`).

        На данный момент поддерживает только простое присваивание (a = 1) и аннотированное типом присваивание
        (a: int = 1). Другие типы присваивания (a = b = 1; a[1] = 1; a, b = 1, 2) не поддерживаются (вернет `None`).

        :param ast_node: Узел
        :return: PyAssign
        """
    line_start = ast_node.lineno
    line_end = ast_node.end_lineno
    col_start = ast_node.col_offset
    col_end = ast_node.end_col_offset
    value = unparse_annotation(ast_node.value)

    if isinstance(ast_node, ast.Assign):
        # Присвоение без явного указания типа
        if len(ast_node.targets) > 1 or any(not isinstance(t, ast.Name) for t in ast_node.targets):
            return None

        name = unparse_annotation(ast_node.targets[0])
        if name is None:
            return None

        return PyAssign(
            name=name,
            value=value,
            line_start=line_start,
            line_end=line_end,
            col_start=col_start,
            col_end=col_end
        )
    else:
        name = ast_node.target.id
        return PyAssign(
            name=name,
            value=value,
            line_start=line_start,
            line_end=line_end,
            col_start=col_start,
            col_end=col_end
        )
