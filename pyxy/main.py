import os
import sys
from pathlib import Path
from typing import Iterable

from pyxy.lang import PyxyTranspiler


def main(target: str | None = None, *, quiet: bool = False, no_map: bool = False) -> None:
    if target is None:
        target = os.getcwd()
    input_path = Path(target)
    if input_path.is_file():
        convert_file(input_path, quiet, not no_map)
    elif input_path.is_dir():
        for file_path in find_pyxy_files(input_path):
            convert_file(file_path, quiet, not no_map)
    else:
        print(f"Bad input: {target}")
        sys.exit(1)


def convert_file(pyxy_filepath: Path, quiet: bool, mapping: bool) -> None:
    if not pyxy_filepath.suffix == ".pyxy":
        print(f"Only pyxy files should be passed as input")
        return

    py_filepath = pyxy_filepath.with_suffix(".py")
    map_filepath = pyxy_filepath.with_name("." + pyxy_filepath.name).with_suffix(".map")
    if os.path.exists(py_filepath) and os.path.getmtime(pyxy_filepath) <= os.path.getmtime(py_filepath):
        if not quiet:
            print(f"Skipping conversion of {pyxy_filepath}")
        return

    with pyxy_filepath.open("r") as fh:
        pyxy_input = fh.read()

    transpiler = PyxyTranspiler(pyxy_input)
    py_output = transpiler.run()
    with py_filepath.open("w") as fh:
        fh.write(py_output)

    if mapping:
        with map_filepath.open("w") as fh:
            fh.write(transpiler.dump_map())

    if not quiet:
        print(f"Converted {pyxy_filepath} to {py_filepath}")


def find_pyxy_files(directory: Path) -> Iterable[Path]:
    return directory.rglob(f'*.pyxy')