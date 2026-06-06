import ast
from dataclasses import dataclass, field

from src.python.syntax.py_class import PyClass, parse_class
from src.python.syntax.py_colon_pair import PyColonPair, parse_colon_pair
from src.python.syntax.py_function import PyFunction, parse_function


@dataclass
class PyModule:
    """
    Содержимое .py файла или директории с .py файлами.

    Attributes:
        path (str): Путь до модуля.
        doc (str | None): Документация файла (модуля) (default = `None`).
        assigns (list[PyColonPair]): Глобальные переменные в модуле (default = `[]`).
        functions (list[PyFunction]): top-level (глобальные) функции в модуле (default = `[]`).
        classes (list[PyClass]): Классы в модуле (default = `[]`).

    Examples:
        # /example/hello.py
        >>> MESSAGE = "Hello"
        ... class Foo: ...
        ... def bar(...): ...
        PyModule(
            path="/example/hello.py",
            doc=None,
            assigns=[PyColonPair(name="MESSAGE", ty=None)],
            functions=[...],
            classes=[...]
        )
    """

    path: str
    doc: str | None = field(default=None)

    assigns: list[PyColonPair] = field(default_factory=list)
    functions: list[PyFunction] = field(default_factory=list)
    classes: list[PyClass] = field(default_factory=list)

    def add_assign(self, a: PyColonPair):
        self.assigns.append(a)

    def add_function(self, f: PyFunction):
        self.functions.append(f)

    def add_class(self, c: PyClass):
        self.classes.append(c)


#########################################################################
## Parsers
#########################################################################

# TODO: параллельно(?) парсить массив файлов
# TODO: собирать импорты
# принять на веру, что все импорты используются
def parse_module(path: str, content: bytes) -> PyModule:
    """
    Парсит входной код в `PyModule`.
    Преобразовывает классы, функции (в планах глобальные переменные)
    :param path: Путь до файла (или имя файла)
    :param content: Содержимое файла
    :return: PyModule
    """
    mod = PyModule(path=path)

    ast_tree = ast.parse(content)
    for item in ast.walk(ast_tree):
        # TODO: парсинг глобальных переменных
        # if isinstance(item, ast.Assign | ast.AnnAssign):
        if isinstance(item, ast.AnnAssign):
            mod.add_assign(parse_colon_pair(item))
        elif isinstance(item, ast.ClassDef):
            mod.add_class(parse_class(item))
        elif isinstance(item, ast.FunctionDef | ast.AsyncFunctionDef):
            mod.add_function(parse_function(item))
        else:
            # Not implemented yet
            continue

    return mod
