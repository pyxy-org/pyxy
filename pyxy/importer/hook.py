import importlib.util
import os
import sys
from importlib.abc import Loader, MetaPathFinder
from pathlib import Path

from pyxy.main import convert_file


class PyxyToPyLoader(Loader):
    def __init__(self, name, path):
        self.name = name
        self.path = path
        self.py_filename = f"{self.path}.py"
        self.pyxy_filename = f"{self.path}.pyxy"

    def _compile_pyxy(self):
        convert_file(Path(self.pyxy_filename), quiet=True, mapping=True)

    def create_module(self, spec):
        return None

    def exec_module(self, module):
        self._compile_pyxy()

        # Execute the generated Python file in the module's namespace
        with open(self.py_filename, 'r') as file:
            exec(file.read(), module.__dict__)

    def get_code(self, fullname):
        self._compile_pyxy()

        with open(self.py_filename, 'r') as file:
            return compile(file.read(), self.py_filename, 'exec')

    def get_source(self, fullname):
        self._compile_pyxy()

        with open(self.py_filename, 'r') as file:
            return file.read()

    def is_package(self, fullname):
        return False


class PyxyToPyFinder(MetaPathFinder):
    def find_spec(self, fullname, path, target=None):
        module_path = fullname.replace('.', '/')
        pyxy_filename = f"{module_path}.pyxy"
        if os.path.exists(pyxy_filename):
            return importlib.util.spec_from_loader(fullname, PyxyToPyLoader(fullname, module_path))
        return None


sys.meta_path.append(PyxyToPyFinder())
