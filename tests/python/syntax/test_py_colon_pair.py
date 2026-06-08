import ast

from python.syntax import parse_colon_pair


def test_function_typed_arg():
    code = "def hello(name: str): ..."

    tree = ast.parse(code)
    for item in ast.walk(tree):
        if isinstance(item, ast.arg):
            pair = parse_colon_pair(item)
            assert pair.name == "name"
            assert pair.ty == "str"
            assert pair.line_start == 1
            assert pair.line_end == 1
            assert pair.col_start == 10
            assert pair.col_end == 19
            break


def test_function_untyped_arg():
    code = "def hello(name): ..."

    tree = ast.parse(code)
    for item in ast.walk(tree):
        if isinstance(item, ast.arg):
            pair = parse_colon_pair(item)
            assert pair.name == "name"
            assert pair.ty is None
            assert pair.line_start == 1
            assert pair.line_end == 1
            assert pair.col_start == 10
            assert pair.col_end == 14
            break


def test_class_field():
    code = """
class Hello:
    world: str
    """

    tree = ast.parse(code)
    for item in ast.walk(tree):
        if isinstance(item, ast.AnnAssign):
            pair = parse_colon_pair(item)
            assert pair.name == "world"
            assert pair.ty == "str"
            assert pair.line_start == 3
            assert pair.line_end == 3
            assert pair.col_start == 4
            assert pair.col_end == 14
            break
