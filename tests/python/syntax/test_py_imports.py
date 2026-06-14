import ast

from backend.python.syntax import parse_imports


def test_import_simple():
    code = "import sys"

    tree = ast.parse(code)
    for item in ast.walk(tree):
        if isinstance(item, ast.Import):
            i = parse_imports(item)
            assert len(i) == 1
            assert i[0].module == "sys"
            assert i[0].name is None
            assert i[0].alias is None
            assert i[0].level == 0
            break


def test_import_simple_with_alias():
    code = "import sys as s"

    tree = ast.parse(code)
    for item in ast.walk(tree):
        if isinstance(item, ast.Import):
            i = parse_imports(item)
            assert len(i) == 1
            assert i[0].module == "sys"
            assert i[0].name is None
            assert i[0].alias == "s"
            assert i[0].level == 0
            break


def test_import_simple_multiple():
    code = "import sys, functools, itertools"

    tree = ast.parse(code)
    for item in ast.walk(tree):
        if isinstance(item, ast.Import):
            i = parse_imports(item)
            assert len(i) == 3
            assert i[0].module == "sys"
            assert i[0].name is None
            assert i[1].module == "functools"
            assert i[1].name is None
            assert i[2].module == "itertools"
            assert i[2].name is None
            break


def test_import_from():
    code = "from sys import argv"

    tree = ast.parse(code)
    for item in ast.walk(tree):
        if isinstance(item, ast.ImportFrom):
            i = parse_imports(item)
            assert len(i) == 1
            assert i[0].module == "sys"
            assert i[0].name == "argv"
            assert i[0].alias is None
            assert i[0].level == 0
            break


def test_import_from_all():
    code = "from sys import *"

    tree = ast.parse(code)
    for item in ast.walk(tree):
        if isinstance(item, ast.ImportFrom):
            i = parse_imports(item)
            assert len(i) == 1
            assert i[0].module == "sys"
            assert i[0].name == "*"
            assert i[0].alias is None
            assert i[0].level == 0
            break
