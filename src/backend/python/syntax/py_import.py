import ast
from dataclasses import dataclass, field


@dataclass
class PyImport:
    """
    Представляет собой объект импорта и его алиас.

    Attributes:
        module (str | None): Модуль, из которого импортируются объекты. `None` появляется только в случаях ``from . import foo``.
        name (str | None): Имя импортируемого объекта. Если импортируется сам модуль, то `None` (default = `None).
        alias (str | None): Алиас импортируемого объекта (default = `None`).
        level (int): Уровень относительного импорта (0 - ``import foo``, 1 - ``from .foo import bar``, 2 - ``from ..foo import bar``) (default = 0).

    Examples:
        >>> import sys
        PyImportItem(module="sys", name=None, alias=None, level=0)

        >>> import sys as s
        PyImportItem(module="sys", name=None, alias="s", level=0)

        >>> from . import bar
        PyImportItem(module=None, name="bar", alias=None, level=0)

        >>> from ..foo import bar
        PyImportItem(module="foo", name="bar", alias=None, level=2)

        >>> from sys import argv
        PyImportItem(module="sys", name="argv", alias=None, level=0)

        >>> from sys import *
        PyImportItem(module="sys", name="*", alias=None, level=0)

        >>> from sys import argv as args
        PyImportItem(module="sys", name="argv", alias="args", level=0)
    """
    module: str | None
    name: str | None = field(default=None)
    alias: str | None = field(default=None)
    level: int = field(default=0)


#########################################################################
## Parsers
#########################################################################

def parse_imports(ast_node: ast.Import | ast.ImportFrom) -> list[PyImport]:
    """
        Парсит указанный узел в `list[PyImport]`.
        Узел должен представлять собой либо простой импорт (`ast.Import`),
        либо импорт из модуля (`ast.ImportFrom`).

        :param ast_node: Узел
        :return: Список импортов
        """
    items: list[PyImport] = []

    if isinstance(ast_node, ast.ImportFrom):
        for item in ast_node.names:
            items.append(PyImport(
                module=ast_node.module,
                name=item.name,
                alias=None,
                level=ast_node.level
            ))
    else:
        for item in ast_node.names:
            items.append(PyImport(
                module=item.name,
                alias=item.asname,
            ))

    return items
