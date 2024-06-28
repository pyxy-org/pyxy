from __future__ import annotations

from typing import TypeGuard

import parso.python.tree
import parso.tree


def split_list(lst, func):
    result = []
    current = []

    for item in lst:
        if func(item):
            if current:
                result.append(current)
            current = []
        else:
            current.append(item)

    if current:
        result.append(current)

    return result


def line_col_to_index(text: str, line: int, col: int):
    lines = text.splitlines(True)  # Keep line breaks
    index = sum(len(lines[i]) for i in range(line - 1)) + col
    return index


def chain_lookup(some_dict, keys):
    result = some_dict
    for key in keys:
        result = result[key]
    return result


def is_leaf(item: parso.tree.NodeOrLeaf, kind: str | None = None, value: str | None = None) -> TypeGuard[parso.tree.Leaf]:
    if not isinstance(item, parso.tree.Leaf):
        return False
    if value is not None and item.value != value:
        return False
    if kind is not None and item.type != kind:
        return False
    return True


def is_node(item: parso.tree.NodeOrLeaf, kind: str | None = None) -> TypeGuard[parso.tree.BaseNode]:
    if not isinstance(item, parso.tree.BaseNode):
        return False
    if kind is not None and item.type != kind:
        return False
    return True
