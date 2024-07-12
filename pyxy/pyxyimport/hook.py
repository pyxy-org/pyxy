import importlib.util
import os
import sys
from importlib.abc import Loader, MetaPathFinder


class PyxyToPyLoader(Loader):
    def __init__(self, name, path):
        self.name = name
        self.path = path

    def create_module(self, spec):
        return None

    def exec_module(self, module):
        pyxy_filename = f"{self.path}.pyxy"
        py_filename = f"{self.path}.py"

        if (not os.path.exists(py_filename) or
                os.path.getmtime(pyxy_filename) > os.path.getmtime(py_filename)):
            from pyxy.lang import PyxyTranspiler

            # print(f"regenerating {py_filename}")
            with open(pyxy_filename, 'r') as file:
                contents = file.read()

            converted = PyxyTranspiler(contents).run()

            with open(py_filename, 'w') as file:
                file.write(converted)

        # Execute the generated Python file in the module's namespace
        with open(py_filename, 'r') as file:
            exec(file.read(), module.__dict__)


class PyxyToPyFinder(MetaPathFinder):
    def find_spec(self, fullname, path, target=None):
        module_path = fullname.replace('.', '/')
        pyxy_filename = f"{module_path}.pyxy"
        if os.path.exists(pyxy_filename):
            return importlib.util.spec_from_loader(fullname, PyxyToPyLoader(fullname, module_path))
        return None


sys.meta_path.append(PyxyToPyFinder())
