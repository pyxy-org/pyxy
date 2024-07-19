import json
import subprocess
import sys
from typing import Callable

from pyxy.run.util import ToolResults, ToolError, ToolEdit


def run_ruff(args: list[str]) -> ToolResults:
    if "check" not in sys.argv:
        capture = False
    else:
        capture = True
        args = [*args, "--output-format", "json"]

    result = subprocess.run(["ruff", *args], capture_output=capture, text=capture)

    if not capture:
        sys.exit(result.returncode)

    sys.stderr.write(result.stderr)
    sys.stderr.flush()

    status = result.returncode
    output_obj = json.loads(result.stdout)

    errors: list[ToolError] = list()
    edits: list[ToolEdit] = list()

    for error in output_obj:
        filename = error["filename"]
        fix = error["fix"]
        if fix is not None:
            for edit in fix["edits"]:
                edits.append(ToolEdit(
                    filename,
                    edit["location"]["row"],
                    edit["location"]["column"],
                    edit["content"]
                ))
        errors.append(ToolError(
            filename,
            error["location"]["row"],
            error["location"]["column"],
            error["message"]
        ))

    return ToolResults("ruff", status, tuple(errors), tuple(edits))


# JSON output hasn't landed yet in mypy: https://github.com/python/mypy/commit/35fbd2a852be2c47e8006429afe9b3ad4b1bfac2
# Release tracking: https://github.com/python/mypy/issues/17285
def run_mypy(args: list[str]) -> tuple[int, str]:
    ...


TOOL_HANDLERS: dict[str, Callable[[list[str]], ToolResults]] = {
    "ruff": run_ruff,
    # "mypy": run_mypy,
}
