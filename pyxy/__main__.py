import os
import sys
from pathlib import Path
from typing import Iterable

import arguably

from pyxy.lang import PyxyTranspiler


@arguably.command
def __root__(target: str | None, *, verbose: bool = False) -> None:
    """
    :param target: file to convert or directory to recursively convert
    :param verbose: [-v] verbose output
    """
    if target is None:
        target = os.getcwd()
    input_path = Path(target)
    if not input_path.is_file():
        convert_file(input_path, verbose)
    elif input_path.is_dir():
        for file_path in find_pyxy_files(input_path):
            convert_file(file_path, verbose)
    else:
        print(f"Bad input: {target}")
        sys.exit(1)

def convert_file(filepath: Path, verbose: bool) -> None:
    if not filepath.suffix == ".pyxy":
        print(f"Only pyxy files should be passed as input")
        return

    with filepath.open("r") as fh:
        pyxy_input = fh.read()

    py_output = PyxyTranspiler(pyxy_input).run()
    out_path = filepath.with_suffix(".py")
    with out_path.open("w") as fh:
        fh.write(py_output)

    if verbose:
        print(f"Converted {filepath} to {out_path}")


def find_pyxy_files(directory: Path) -> Iterable[Path]:
    return directory.rglob(f'*.pyxy')


if __name__ == "__main__":
    arguably.run(name="pyxy")
