from dataclasses import is_dataclass, fields

def as_str_dict(obj) -> dict | list | str:
    """
    Преобразует объект в словарь с ключами и значениями строкового типа.
    Рекурсивно проделывает ту же операцию на вложенных объектах.

    Examples:
        >>> Hello(name="world", age=1, cars=[Car(id=15, new=True)])
        {
            "name": "world",
            "age": "1",
            "cars": [
                {"id": "15", "new": "True"}
            ]
        }

    :param obj: Объект
    :return: Преобразованный объект
    """

    # Если это датакласс, разбираем его по полям
    if is_dataclass(obj):
        result = {}
        for f in fields(obj):
            value = getattr(obj, f.name)
            result[f.name] = as_str_dict(value)
        return result

    # Если это список, тообрабатываем элементы
    elif isinstance(obj, (list, tuple)):
        return [as_str_dict(item) for item in obj]

    # Если это словарь, обрабатываем ключи и значения
    elif isinstance(obj, dict):
        return {str(k): as_str_dict(v) for k, v in obj.items()}

    # Все остальные приводим к строке
    else:
        return str(obj)
