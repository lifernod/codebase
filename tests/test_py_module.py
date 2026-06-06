import ast

from python.syntax import *

def test_module_file():
    code = """
MESSAGE = "hello "

class Hello:
    name: str
    def __init__(self, name: str):
        self.name = name
    def say_hello(self):
        print(MESSAGE + self.name)
        
def say_hello():
    print("hello")
    """

    tree = ast.parse(code)
    for item in ast.walk(tree):
        if isinstance(item, ast.Assign):
            a = parse_assign(item)
            assert a is not None
            assert a.name == "MESSAGE"
            assert a.ty is None
            assert a.value == "'hello '"
        elif isinstance(item, ast.ClassDef):
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
            assert c.methods[0].name == "say_hello"
            assert len(c.methods[0].args) == 1
            assert c.methods[0].args[0].name == "self"
            assert c.methods[0].args[0].ty == "Hello"
        elif isinstance(item, ast.FunctionDef):
            f = parse_function(item)
            assert len(f.args) == 0

            assert f.return_ty is None
            assert f.is_async == False
            assert f.body_str == "print('hello')"
            assert f.related_class_name is None
            break