import ast

from backend.python.syntax import parse_assign


def test_assign_variable():
    code = "name = 'Hello'"

    tree = ast.parse(code)
    for item in ast.walk(tree):
        if isinstance(item, ast.Assign):
            a = parse_assign(item)
            assert a is not None
            assert a.name == "name"
            assert a.ty is None
            assert a.value == "'Hello'"
            break


def test_assign_with_ty():
    code = "name: str = 'Hello'"

    tree = ast.parse(code)
    for item in ast.walk(tree):
        if isinstance(item, ast.Assign):
            a = parse_assign(item)
            assert a is not None
            assert a.name == "name"
            assert a.ty == "str"
            assert a.value == "'Hello'"
            break


def test_fail_assign_multiple():
    code = "name, age = 'Hello', 52"

    tree = ast.parse(code)
    for item in ast.walk(tree):
        if isinstance(item, ast.Assign):
            a = parse_assign(item)
            assert a is None
            break
