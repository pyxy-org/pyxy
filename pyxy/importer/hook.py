import importlib.util
import os
import sys
from importlib.abc import Loader, MetaPathFinder


class PyxyToPyLoader(Loader):
    def __init__(self, name, path):
        self.name = name
        self.path = path
        self.py_filename = f"{self.path}.py"
        self.pyxy_filename = f"{self.path}.pyxy"

    def _compile_pyxy(self):
        pyxy_modified = os.path.getmtime(self.pyxy_filename) > os.path.getmtime(self.py_filename)
        if not os.path.exists(self.py_filename) or pyxy_modified:
            from pyxy.lang import PyxyTranspiler

            # print(f"regenerating {py_filename}")
            with open(self.pyxy_filename, 'r') as file:
                contents = file.read()

            converted = PyxyTranspiler(contents).run()

            with open(self.py_filename, 'w') as file:
                file.write(converted)

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
