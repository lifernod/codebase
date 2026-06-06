import ast
from dataclasses import dataclass, field

from .py_colon_pair import PyColonPair, parse_colon_pair
from .py_function import PyFunction, parse_function
from ..metadata import AnnotatedMeta, PositionMeta


@dataclass
class PyClass(PositionMeta, AnnotatedMeta):
    """
    Сигнатура класса.
    Используется для представления класса.

    В случаях, когда метод класса принимает аргумент с именем `self`, то его тип автоматически заменяется на
    тип класса, т.е. `class Hello` -> `self: Hello`.

    Attributes:
        name (str): Имя класса.
        constructor (PyFunction | None): Конструктор класса (метод `__init__`). Если конструктора нет, то `None` (default = `None`).
        fields (list[PyColonPair]): Поля класса, указанные явно в теле класса (default = `[]`).
        methods (list[PyFunction]): Методы класса, исключая конструктор (default = `[]`).

    Examples:
        >>> class Hello:
        ...     name: str
        ...     def __init__(self, name: str): ...
        ...     def hello(self) -> str: ...
        PyClass(
            name="Hello",
            constructor=PyFunction(
                name="__init__",
                related_class_name="Hello",
                is_async=False,
                args=[PyColonPair(name="self", ty="Hello")],
                return_ty=None
            ),
            fields=[PyColonPair(name="name", ty="str")],
            methods=[PyFunction(
                name="hello",
                related_class_name="Hello",
                is_async=False,
                args=[PyColonPair(name="self", ty="Hello")],
                return_ty="str"
            )]
        )
    """

    name: str

    constructor: PyFunction | None = field(default=None)
    fields: list[PyColonPair] = field(default_factory=list)
    methods: list[PyFunction] = field(default_factory=list)

    def add_field(self, f: PyColonPair):
        self.fields.append(f)

    def add_method(self, f: PyFunction):
        self.methods.append(f)


#########################################################################
## Parsers
#########################################################################

def parse_class(ast_node: ast.ClassDef) -> PyClass:
    """
    Парсит указанный узел в `PyClass`.
    Узел должен представлять собой класс (`ast.ClassDef`).

    :param ast_node: Узел
    :return: PyClass с вызванным методом PyClass.propagate_self_type
    """
    name = ast_node.name

    line_start = ast_node.lineno
    line_end = ast_node.end_lineno
    col_start = ast_node.col_offset
    col_end = ast_node.end_col_offset

    doc = ast.get_docstring(ast_node)

    cls = PyClass(
        name=name,
        line_start=line_start,
        line_end=line_end,
        col_start=col_start,
        col_end=col_end,
        doc=doc
    )

    # Собираем поля класса и его методы
    for item in ast_node.body:
        if isinstance(item, ast.AnnAssign):
            cls.add_field(parse_colon_pair(item))
        elif isinstance(item, ast.FunctionDef | ast.AsyncFunctionDef):

            if item.name == "__init__":
                cls.constructor = parse_function(item, class_name=cls.name)
            else:
                cls.add_method(parse_function(item, class_name=cls.name))
        else:
            continue

    return cls
