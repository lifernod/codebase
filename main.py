import os
import sys
import json
import logging
from src.python.utils.as_str_dict import as_str_dict
from src.python.syntax.py_module import parse_module

from src.python.utils.chunker import *

path = 'archive/gymhero/gymhero'


if __name__ == "__main__":
    get_all_chunks(path)
    # for chunk in get_all_chunks(path):
    #     print(json.dumps(chunk, indent=4, ensure_ascii=False))