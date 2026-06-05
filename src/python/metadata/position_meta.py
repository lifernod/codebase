from dataclasses import dataclass


@dataclass
class PositionMeta:
    """
    Информация о положении объекта в файле.
    Нумерация всех положений начинается не с 0, а с 1

    Attributes:
        line_start (int): Номер строки, с которой начинается объект.
        col_start (int): Номер колонки, с которой начинается объект.
        line_end (int | None): Номер строки, на которой заканчивается объект.
        col_end (int | None): Номер колонки, на которой заканчивается объект.

    Examples:
        >>> code = '''def hello(name): ...'''
        name    line_start    line_end    col_start    col_end
        hello   1             1           0            20 (заканчивается после троеточия)
        name    1             1           10           14
    """
    line_start: int
    line_end: int | None
    col_start: int
    col_end: int | None
