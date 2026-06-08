from pprint import pprint

from python.syntax.py_module import parse_module


def test_module_file():
    code = """
from sys import argv
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

    mod = parse_module("test.py", code.encode("utf-8"))
    pprint(mod)
    assert len(mod.imports) == 1
    assert len(mod.assigns) == 1
    assert len(mod.functions) == 1
    assert len(mod.classes) == 1

    # Imports
    assert mod.imports[0].module == "sys"
    assert mod.imports[0].name == "argv"

    # Assigns
    assert mod.assigns[0].name == "MESSAGE"
    assert mod.assigns[0].ty is None
    assert mod.assigns[0].value == "'hello '"

    # Functions
    assert mod.functions[0].name == "say_hello"
    assert mod.functions[0].return_ty is None
    assert mod.functions[0].is_async == False
    assert mod.functions[0].body_str == "print('hello')"
    assert mod.functions[0].related_class_name is None

    # Classes
    assert mod.classes[0].name == "Hello"
    assert len(mod.classes[0].fields) == 1
    assert mod.classes[0].fields[0].name == "name"
    assert mod.classes[0].fields[0].ty == "str"

    assert mod.classes[0].constructor is not None
    assert mod.classes[0].constructor.name == "__init__"

    assert len(mod.classes[0].constructor.args) == 2
    assert mod.classes[0].constructor.args[0].name == "self"
    assert mod.classes[0].constructor.args[0].ty == "Hello"
    assert mod.classes[0].constructor.args[1].name == "name"
    assert mod.classes[0].constructor.args[1].ty == "str"

    assert mod.classes[0].methods[0].name == "say_hello"
    assert mod.classes[0].methods[0].args[0].name == "self"
    assert mod.classes[0].methods[0].args[0].ty == "Hello"
