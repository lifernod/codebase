from dataclasses import dataclass


@dataclass
class AnnotatedMeta:
    """
    Информация об аннотациях и документации объекта.

    Attributes:
        doc (str | None): Документация объекта. Если документация не указана или не поддерживается, то `None`.
    """

    doc: str | None
