from pathlib import Path

import arguably

from pyxy.lang import PyxyTranspiler


@arguably.command
def __root__(filename: str) -> None:
    filepath = Path(filename)
    if not filepath.suffix == ".pyxy":
        print(f"Only pyxy files should be passed as input")
        return

    with filepath.open("r") as fh:
        pyxy_input = fh.read()

    py_output = PyxyTranspiler(pyxy_input).run()
    with filepath.with_suffix(".py").open("w") as fh:
        fh.write(py_output)


if __name__ == "__main__":
    arguably.run(name="pyxy")
