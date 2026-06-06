import ast
from dataclasses import dataclass, field

from .py_assign import PyAssign, parse_assign
from .py_class import PyClass, parse_class
from .py_function import PyFunction, parse_function
from .py_import import PyImport, parse_imports


@dataclass
class PyModule:
    """
    Содержимое .py файла или директории с .py файлами.

    Attributes:
        path (str): Путь до модуля.
        doc (str | None): Документация файла (модуля) (default = `None`).
        imports (list[PyImport]): Импорты (default = `[]`).
        assigns (list[PyAssign]): Глобальные переменные в модуле (default = `[]`).
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
            assigns=[PyAssign(name="MESSAGE", ty=None, value="Hello")],
            functions=[...],
            classes=[...]
        )
    """

    path: str
    doc: str | None = field(default=None)

    imports: list[PyImport] = field(default_factory=list)
    assigns: list[PyAssign] = field(default_factory=list)
    functions: list[PyFunction] = field(default_factory=list)
    classes: list[PyClass] = field(default_factory=list)

    def add_import(self, i: PyImport):
        self.imports.append(i)

    def add_imports(self, i: list[PyImport]):
        self.imports.extend(i)

    def add_assign(self, a: PyAssign):
        self.assigns.append(a)

    def add_function(self, f: PyFunction):
        self.functions.append(f)

    def add_class(self, c: PyClass):
        self.classes.append(c)


#########################################################################
## Parsers
#########################################################################

# TODO: параллельно(?) парсить массив файлов
def parse_module(path: str, content: bytes) -> PyModule:
    """
    Парсит входной код в `PyModule`.

    Поддерживаются:
        1. Импорты (обычные, from, относительные, см :class:`python.syntax.py_import.PyImport`)
        2. Глобальные переменные (простые присваивания, см :class:`python.syntax.py_assign.PyAssign`)
        3. Глобальные функции (см :class:`python.syntax.py_function.PyFunction`)
        4. Классы (см :class:`python.syntax.py_class.PyClass`)

    :param path: Путь до файла (или имя файла)
    :param content: Содержимое файла
    :return: PyModule
    """
    mod = PyModule(path=path)

    ast_tree = ast.parse(content)
    for item in ast_tree.body:
        if isinstance(item, ast.Import | ast.ImportFrom):
            i = parse_imports(item)
            if i is not None:
                mod.add_imports(i)
        elif isinstance(item, ast.ClassDef):
            mod.add_class(parse_class(item))
        elif isinstance(item, ast.FunctionDef | ast.AsyncFunctionDef):
            mod.add_function(parse_function(item))
        elif isinstance(item, ast.Assign | ast.AnnAssign):
            a = parse_assign(item)
            if a is not None:
                mod.add_assign(a)
        else:
            # Not implemented yet
            continue

    return mod
