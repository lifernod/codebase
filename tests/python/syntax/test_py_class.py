import ast

from python.syntax import parse_class


def test_class_with_only_constructor():
    code = """
class Hello:
    def __init__(self, name: str):
        ...
    """

    tree = ast.parse(code)
    for item in ast.walk(tree):
        if isinstance(item, ast.ClassDef):
            c = parse_class(item)
            assert c.name == "Hello"

            assert len(c.fields) == 0
            assert len(c.methods) == 0

            assert c.constructor is not None
            assert c.constructor.name == "__init__"

            assert len(c.constructor.args) == 2
            assert c.constructor.args[0].name == "self"
            assert c.constructor.args[0].ty == "Hello"
            break


def test_class_with_only_fields():
    code = """
class Hello:
    name: str
    age: int
        """

    tree = ast.parse(code)
    for item in ast.walk(tree):
        if isinstance(item, ast.ClassDef):
            c = parse_class(item)
            assert c.name == "Hello"

            assert c.constructor is None
            assert len(c.methods) == 0

            assert len(c.fields) == 2
            assert c.fields[0].name == "name"
            assert c.fields[0].ty == "str"
            assert c.fields[1].name == "age"
            assert c.fields[1].ty == "int"
            break


def test_class_with_method_and_ctor():
    code = """
class Hello:
    def __init__(self):
        ...
    def hello(self, name: str):
        ...
        """

    tree = ast.parse(code)
    for item in ast.walk(tree):
        if isinstance(item, ast.ClassDef):
            c = parse_class(item)
            assert c.name == "Hello"

            assert len(c.fields) == 0

            assert c.constructor is not None
            assert c.constructor.name == "__init__"

            assert len(c.constructor.args) == 1
            assert c.constructor.args[0].name == "self"
            assert c.constructor.args[0].ty == "Hello"

            assert len(c.methods) == 1
            assert c.methods[0].name == "hello"
            assert len(c.methods[0].args) == 2
            assert c.methods[0].args[0].name == "self"
            assert c.methods[0].args[0].ty == "Hello"

            break


def test_class_full():
    code = """
class Hello:
    name: str
    def __init__(self, name: str):
        ...
    def hello(self, name: int):
        ...
    """
    tree = ast.parse(code)
    for item in ast.walk(tree):
        if isinstance(item, ast.ClassDef):
            c = parse_class(item)
            assert c.name == "Hello"

            assert len(c.fields) == 1
            assert c.fields[0].name == "name"
            assert c.fields[0].ty == "str"

            assert c.constructor is not None
            assert c.constructor.name == "__init__"

            assert len(c.constructor.args) == 2
            assert c.constructor.args[0].name == "self"
            assert c.constructor.args[0].ty == "Hello"
            assert c.constructor.args[1].name == "name"
            assert c.constructor.args[1].ty == "str"

            assert len(c.methods) == 1
            assert c.methods[0].name == "hello"
            assert len(c.methods[0].args) == 2
            assert c.methods[0].args[0].name == "self"
            assert c.methods[0].args[0].ty == "Hello"
            assert c.methods[0].args[1].name == "name"
            assert c.methods[0].args[1].ty == "int"

            break
