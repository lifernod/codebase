import ast

from python.syntax import parse_function


def test_function_without_args_with_return_type():
    code = """
def hello() -> str:
    print("hello")
    """

    tree = ast.parse(code)
    for item in ast.walk(tree):
        if isinstance(item, ast.FunctionDef):
            f = parse_function(item)
            assert f.name == "hello"
            assert len(f.args) == 0
            assert f.return_ty == "str"
            assert f.is_async == False
            assert f.body_str == "print('hello')"
            assert f.related_class_name is None
            break


def test_function_without_args_without_return_type():
    code = """
def hello():
    return 123
    """

    tree = ast.parse(code)
    for item in ast.walk(tree):
        if isinstance(item, ast.FunctionDef):
            f = parse_function(item)
            assert f.name == "hello"
            assert len(f.args) == 0
            assert f.return_ty is None
            assert f.is_async == False
            assert f.body_str == "return 123"
            assert f.related_class_name is None
            break


def test_function_with_args():
    code = """
def hello(name: str, age):
    ...
    """

    tree = ast.parse(code)
    for item in ast.walk(tree):
        if isinstance(item, ast.FunctionDef):
            f = parse_function(item)
            assert f.name == "hello"

            assert len(f.args) == 2
            assert f.args[0].name == "name"
            assert f.args[0].ty == "str"
            assert f.args[1].name == "age"
            assert f.args[1].ty is None

            assert f.return_ty is None
            assert f.is_async == False
            assert f.body_str == "..."
            assert f.related_class_name is None
            break


def test_function_class_init():
    code = """
class Hello:
    def __init__(self, name: str):
        ...
        """

    tree = ast.parse(code)
    for item in ast.walk(tree):
        if isinstance(item, ast.FunctionDef):
            f = parse_function(item, class_name="Hello")
            assert f.name == "__init__"

            assert len(f.args) == 2
            assert f.args[0].name == "self"
            assert f.args[0].ty == "Hello"
            assert f.args[1].name == "name"
            assert f.args[1].ty == "str"

            assert f.return_ty is None
            assert f.is_async == False
            assert f.body_str == "..."
            assert f.related_class_name == "Hello"
            break


def test_function_class_method():
    code = """
class Hello:
    def world(self):
        ...
        """

    tree = ast.parse(code)
    for item in ast.walk(tree):
        if isinstance(item, ast.FunctionDef):
            f = parse_function(item, class_name="Hello")
            assert f.name == "world"

            assert len(f.args) == 1
            assert f.args[0].name == "self"
            assert f.args[0].ty == "Hello"

            assert f.return_ty is None
            assert f.is_async == False
            assert f.body_str == "..."
            assert f.related_class_name == "Hello"
            break
