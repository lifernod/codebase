from dataclasses import dataclass


@dataclass
class BodyMeta:
    r"""
    Информация о содержимом тела объекта. На данный момент подходит только для функций и классов.

    Attributes:
        body_str (str): Строковое представление тела функции. Содержит исходное тело, без использования trim и т.п. манипуляций, разве что таб будет представлен в виде `\t`

    Examples:
        >>> def hello():
        ...     b = 15
        ...     for a in range(b):
        ...         print(a)
        b = 15\nfor a in range(b):\n\tprint(a)
    """
    body_str: str

    def normalize_tabs(self):
        """
        Превращает таб (четыре пробела) в \t.
        """
        self.body_str.replace("    ", "\t")