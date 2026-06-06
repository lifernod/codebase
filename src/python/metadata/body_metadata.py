from dataclasses import dataclass


@dataclass
class BodyMeta:
    r"""
    Информация о содержимом тела объекта. На данный момент подходит только для функций и классов.

    `body_str` не содержит в себе первого таба (означающего начало тела), и все табы (четыре пробела) заменены на `\t`.
    А так же все ковычки заменени на одинарные ('').

    Attributes:
        body_str (str): Строковое представление тела функции. Тело записано подряд, т.е. в одну строку с необходимыми табами и переносами строк.

    Examples:
        >>> def hello():
        ...     b = 15
        ...     for a in range(b):
        ...         print(a)
        body_str = "b = 15\nfor a in range(b):\n\tprint(a)"

        >>> def hello():
        ...     name = "aaa"
        body_str = "name = 'aaa'"
    """
    body_str: str

    def __post_init__(self):
        """
        Превращает таб (четыре пробела) в \t.
        """
        self.body_str.replace("    ", "\t")
