# pyxy.run

This is designed to allow static analysis tools to be run against a `.py` file, while correlating results against a `.pyxy` file.

Example usage:
```
$ python3 -m pyxy.run ruff check pyxy_tests/scripts/script7.py
.../pyxy/pyxy_tests/scripts/script7.pyxy:2:8 error: F811 Redefinition of unused `{name}` from {row}
.../pyxy/pyxy_tests/scripts/script7.pyxy:5:1 error: E402 Module level import not at top of cell
.../pyxy/pyxy_tests/scripts/script7.pyxy:5:1 error: F403 `from {name} import *` used; unable to detect undefined names
```
