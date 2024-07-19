import shutil
import sys
from pathlib import Path

import pyxy.main
from pyxy.run.tools import TOOL_HANDLERS
from pyxy.run.util import PyxyRemapper


def main(args: list[str]):
    if len(args) < 2:
        print("usage: pyxy.run tool ...")
        sys.exit(1)

    tool = args[1]
    tool_args = args[2:]

    if not shutil.which(tool):
        print(f"Tool not found: {tool}")
        sys.exit(127)

    if tool not in TOOL_HANDLERS:
        print(f"Unrecognized tool: {tool}")
        sys.exit(1)

    pyxy.main.main(quiet=True)
    tool_result = TOOL_HANDLERS[tool](tool_args)

    for error in tool_result.errors:
        # TODO: Don't instantiate this every time
        remapper = PyxyRemapper.from_py_file(Path(error.filename))
        line, column = remapper.py_to_pyxy(error.line, error.column)
        print(f"{remapper.pyxy_path}:{line}:{column} - {error.message}")

    sys.exit(tool_result.status)
