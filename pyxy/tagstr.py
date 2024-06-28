import ast
import inspect
import re
import textwrap
from dataclasses import dataclass
from typing import Callable, Any, Iterable

from .util import line_col_to_index


def html[C: Callable](func: C | None = None) -> C:
    def wrap(wrap_func: Callable) -> Callable:
        return transform_function(wrap_func)

    return wrap if func is None else wrap(func)


def string_handler_inner(*args: Any):
    stringified_args = list()
    for arg in args:
        if isinstance(arg, Iterable) and not isinstance(arg, (str, bytes)):
            stringified_args.extend(string_handler_inner(*arg))
        else:
            # TODO: Need to make this more correct
            if stringified_args and stringified_args[-1].endswith("="):
                stringified_args.append(repr(arg))
            else:
                stringified_args.append(str(arg))
    return "".join(stringified_args)


def string_handler(arg_getter: Callable):
    # print(f"string_handler for {arg_getter=}")
    return textwrap.dedent(string_handler_inner(arg_getter())).strip()


@dataclass
class FormattedValueContainer:
    formatted_value: ast.FormattedValue


class StripHtmlDecorators(ast.NodeTransformer):
    def visit_FunctionDef(self, node):
        node.decorator_list = [d for d in node.decorator_list if not (isinstance(d, ast.Name) and d.id == html.__name__)]
        return node


def transform_function[C: Callable](func: C) -> C:
    source = inspect.getsource(func)
    tree = ast.parse(source)

    modified_tree = JoinedStrReplacer(source).visit(tree)
    modified_tree = StripHtmlDecorators().visit(modified_tree)
    ast.fix_missing_locations(modified_tree)
    # print(ast.dump(modified_tree))

    code = compile(modified_tree, filename="<transformed>", mode="exec")
    func_globals = func.__globals__.copy()
    func_globals["_pyxy_string_handler"] = string_handler

    namespace = {}
    exec(code, func_globals, namespace)
    return namespace[func.__name__]


class JoinedStrReplacer(ast.NodeTransformer):
    def __init__(self, source: str):
        super().__init__()
        self.source = source

    def _trim_string(self, input_string):
        match = re.search(r"[\"']", input_string)
        if match:
            return input_string[:match.start()]
        return input_string

    def visit_JoinedStr(self, node):
        start_idx = line_col_to_index(self.source, node.lineno, node.col_offset)
        string_spec = self._trim_string(self.source[start_idx:start_idx+3])
        if "F" not in string_spec:
            return node

        # print(f"Replacing {node=}")

        list_node = ast.List(
            elts=[
                JoinedStrReplacer(self.source).visit(n.value if isinstance(n, ast.FormattedValue) else n)
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
