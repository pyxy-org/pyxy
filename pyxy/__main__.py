import os
import sys
from pathlib import Path
from typing import Iterable

import arguably

from pyxy.lang import PyxyTranspiler


@arguably.command
def convert(target: str | None = None, *, quiet: bool = False) -> None:
    """
    :param target: file to convert or directory to recursively convert
    :param quiet: [-q] suppress unnecessary output
    """
    if target is None:
        target = os.getcwd()
    input_path = Path(target)
    if input_path.is_file():
        convert_file(input_path, quiet)
    elif input_path.is_dir():
        for file_path in find_pyxy_files(input_path):
            convert_file(file_path, quiet)
    else:
        print(f"Bad input: {target}")
        sys.exit(1)

@arguably.command
def install(*, dev: bool = False):
    import pyxy.pyxyimport
    pyxy.pyxyimport.install(dev=dev)

@arguably.command
def uninstall():
    import pyxy.pyxyimport
    pyxy.pyxyimport.uninstall()

def convert_file(filepath: Path, quiet: bool) -> None:
    if not filepath.suffix == ".pyxy":
        print(f"Only pyxy files should be passed as input")
        return

    with filepath.open("r") as fh:
        pyxy_input = fh.read()

    py_output = PyxyTranspiler(pyxy_input).run()
    out_path = filepath.with_suffix(".py")
    with out_path.open("w") as fh:
        fh.write(py_output)

    if not quiet:
        print(f"Converted {filepath} to {out_path}")


def find_pyxy_files(directory: Path) -> Iterable[Path]:
    return directory.rglob(f'*.pyxy')


if __name__ == "__main__":
    arguably.run(name="pyxy")
