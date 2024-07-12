import arguably

from .installer import install as _install, uninstall as _uninstall


@arguably.command
def install(*, dev: bool = False):
    _install(dev=dev)

@arguably.command
def uninstall():
    _uninstall()

if __name__ == "__main__":
    arguably.run(name="pyxyimport")
