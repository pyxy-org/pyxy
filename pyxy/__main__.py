import arguably

from pyxy.main import main


@arguably.command
def __root__(target: str | None = None, *, quiet: bool = False, no_map: bool = False) -> None:
    """
    :param target: file to convert or directory to recursively convert
    :param quiet: [-q] suppress unnecessary output
    """
    main(target, quiet=quiet, no_map=no_map)


if __name__ == "__main__":
    arguably.run(name="pyxy")
