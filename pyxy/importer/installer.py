import os
import site
from pathlib import Path


def install(*, dev: bool = False):
    site_packages = site.getsitepackages()[0]
    pth_file_path = os.path.join(site_packages, 'pyxyimport.pth')
    with open(pth_file_path, 'w') as file:
        if dev:
            file.write(str(Path(__file__).parent.parent.parent) + "\n")
        file.write(f'import pyxy.importer.hook\n')


def uninstall():
    site_packages = site.getsitepackages()[0]
    pth_file_path = os.path.join(site_packages, 'pyxyimport.pth')
    os.unlink(pth_file_path)
