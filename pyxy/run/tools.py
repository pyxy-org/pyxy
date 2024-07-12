import importlib.metadata
import io
import json
import subprocess
import sys
from typing import Callable, Any


def run_ruff(args: list[str]) -> tuple[int, str]:
    if "check" not in sys.argv:
        capture = False
    else:
        capture = True
        args = [*args, "--output-format", "sarif"]

    result = subprocess.run(["ruff", *args], capture_output=capture, text=capture)

    if not capture:
        sys.exit(result.returncode)

    sys.stderr.write(result.stderr)
    sys.stderr.flush()

    status = result.returncode
    sarif_str = result.stdout

    return status, sarif_str


# JSON output hasn't landed yet in mypy: https://github.com/python/mypy/commit/35fbd2a852be2c47e8006429afe9b3ad4b1bfac2
# Release tracking: https://github.com/python/mypy/issues/17285
def run_mypy(args: list[str]) -> tuple[int, str]:
    ...


TOOL_HANDLERS: dict[str, Callable[[list[str]], tuple[int, str]]] = {
    "ruff": run_ruff,
    # "mypy": run_mypy,
}


# https://gist.github.com/tusharsadhwani/5fd7a3c32d73f10fcb86e8deac4b60cf
def _mypy_output_to_sarif(mypy_output: str) -> dict[str, Any]:
    sarif_issues: list[dict[str, Any]] = []

    mypy_output_io = io.StringIO(mypy_output)
    for line in mypy_output_io:
        issue = json.loads(line)
        sarif_issues.append(
            {
                "ruleId": issue["code"],
                "level": issue["severity"],
                "message": {"text": issue["message"]},
                "locations": [
                    {
                        "physicalLocation": {
                            "artifactLocation": {"uri": issue["file"]},
                            "region": {"startLine": issue["column"], "startColumn": issue["line"]},
                        }
                    }
                ],
            }
        )

    sarif_template = {
        "version": "2.1.0",
        "$schema": "https://schemastore.azurewebsites.net/schemas/json/sarif-2.1.0.json",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "mypy",
                        "version": importlib.metadata.distribution("mypy").version,
                    }
                },
                "results": sarif_issues,
            }
        ],
    }
    return sarif_template
