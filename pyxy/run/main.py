import shutil
import sys

import pyxy.main
from pyxy.run.mapping import remap_sarif
from pyxy.run.tools import TOOL_HANDLERS


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
    status, output = TOOL_HANDLERS[tool](tool_args)

    output = remap_sarif(output)

    # sys.stdout.write(output)
    # sys.stdout.flush()

    sys.exit(status)
