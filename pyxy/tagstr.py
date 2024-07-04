import ast
import functools
import inspect
import re
import textwrap
from typing import Callable, Any, Iterable

from .util import line_col_to_index


def tagstr[C: Callable](transformer: Callable[..., str], *, target: str = "F") -> C:
    def wrap(wrap_func: Callable) -> Callable:
        return _transform_function(target, wrap_func, transformer)

    return wrap


def html(*args: Any):
    stringified_args = list()
    for arg in args:
        if isinstance(arg, Iterable) and not isinstance(arg, (str, bytes)):
            stringified_args.extend(html(*arg))
        else:
            # TODO: Need to make this more correct
            if stringified_args and stringified_args[-1].endswith("="):
                stringified_args.append(repr(arg))
            else:
                stringified_args.append(str(arg))
    return textwrap.dedent("".join(stringified_args)).strip()


def _transformer_entry(arg_getter: Callable, transformer: Callable[..., str]):
    return transformer(arg_getter())


class _StripTagstrDecorator(ast.NodeTransformer):
    def __init__(self, transformer: Callable[..., str]):
        self.transformer = transformer

    def visit_FunctionDef(self, node):
        node.decorator_list = [d for d in node.decorator_list if not (isinstance(d, ast.Call) and d.func.id == tagstr.__name__)]
        return node


def _transform_function[C: Callable](target: str, func: C, transformer: Callable[..., str]) -> C:
    source = inspect.getsource(func)
    tree = ast.parse(source)

    modified_tree = _JoinedStrReplacer(source, target).visit(tree)
    modified_tree = _StripTagstrDecorator(transformer).visit(modified_tree)
    ast.fix_missing_locations(modified_tree)
    # print(ast.dump(modified_tree))

    code = compile(modified_tree, filename="<transformed>", mode="exec")
    func_globals = func.__globals__.copy()
    func_globals["_pyxy_string_handler"] = functools.partial(_transformer_entry, transformer=transformer)

    namespace = {}
    exec(code, func_globals, namespace)
    return namespace[func.__name__]


class _JoinedStrReplacer(ast.NodeTransformer):
    def __init__(self, source: str, target: str):
        super().__init__()
        self.source = source
        self.target = target

    def _trim_string(self, input_string):
        match = re.search(r"[\"']", input_string)
        if match:
            return input_string[:match.start()]
        return input_string

    def visit_JoinedStr(self, node):
        start_idx = line_col_to_index(self.source, node.lineno, node.col_offset)
        string_spec = self._trim_string(self.source[start_idx:start_idx+3])
        if string_spec != self.target:
            return node

        # print(f"Replacing {node=}")

        list_node = ast.List(
            elts=[
                _JoinedStrReplacer(self.source, self.target).visit(n.value if isinstance(n, ast.FormattedValue) else n)
                for n in node.values
            ],
            ctx=ast.Load()
        )
        lambda_node = ast.Lambda(
            args=ast.arguments(
                posonlyargs=[],
                args=[],
                vararg=None,
                kwonlyargs=[],
                kw_defaults=[],
                kwarg=None,
                defaults=[]
            ),
            body=list_node,
        )
        ast.fix_missing_locations(lambda_node)

        handler_call = ast.Call(
            func=ast.Name(id='_pyxy_string_handler', ctx=ast.Load()),
            args=[lambda_node],
            keywords=[]
        )
        new_node = ast.copy_location(handler_call, node)
        ast.fix_missing_locations(new_node)
        return new_node
