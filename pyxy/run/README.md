# pyxy.run

This is designed to allow static analysis tools to be run against a `.py` file, while correlating results against a `.pyxy` file.

Example usage:
```
$ python3 -m pyxy.run ruff check pyxy_tests/scripts/script7.py
/home/user/pyxy/pyxy_tests/scripts/script7.pyxy:2:8 - Redefinition of unused `builtins` from line 1
/home/user/pyxy/pyxy_tests/scripts/script7.pyxy:5:1 - Module level import not at top of file
/home/user/pyxy/pyxy_tests/scripts/script7.pyxy:5:1 - `from textwrap import *` used; unable to detect undefined names
```
