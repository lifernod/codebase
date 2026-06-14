import ast


def unparse_annotation(node: ast.expr | None) -> str | None:
    """
    Превращает `ast.expr` в строку (получает строковое значение).
    :param node: Узел для преобразования в строку.
    :return: Строковое представление узла, если удалось его преобразовать.
    """
    if node is None:
        return None
    return ast.unparse(node)
