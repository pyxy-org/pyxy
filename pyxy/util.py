from __future__ import annotations

from collections import OrderedDict
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
    """TODO: This is slow"""
    lines = text.splitlines(True)  # Keep line breaks
    index = sum(len(lines[i]) for i in range(line - 1)) + col
    return index


def index_to_line_col(text, index):
    lines = text.splitlines()
    line_number = 0
    total_chars = 0

    for line in lines:
        total_line_length = len(line) + 1  # +1 for newline character
        if total_chars + total_line_length > index:
            col_number = index - total_chars
            return line_number + 1, col_number + 1
        total_chars += total_line_length
        line_number += 1

    raise Exception("Index out of range")


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


class PatchedString:
    def __init__(self, original: str):
        self.original = original
        self._patches: list[tuple[int, int, str | PatchedString]] = list()

    def patch(self, start: int, end: int, new_value: str | PatchedString):
        patches_to_remove = list()
        for idx, patch in enumerate(self._patches):
            patch_start, patch_end, patch_value = patch
            if patch_start >= start and patch_end <= end:
                patches_to_remove.append(idx)
                continue
            assert start < patch_start or start >= patch_end
            assert end - 1 < patch_start or end - 1 >= patch_end
        self._patches = [patch for idx, patch in enumerate(self._patches) if idx not in patches_to_remove]
        self._patches.append((start, end, new_value))
        self._patches.sort()

    def get_mapping(self) -> OrderedDict[tuple[int, int], tuple[int, int]]:
        result = OrderedDict()
        src_idx = 0
        dst_idx = 0
        for patch in self._patches:
            patch_start, patch_end, patch_value = patch
            if src_idx < patch_start:
                unpatched_len = patch_start - src_idx
                result[(dst_idx, dst_idx + unpatched_len)] = (src_idx, src_idx + unpatched_len)
                src_idx += unpatched_len
                dst_idx += unpatched_len
            assert src_idx == patch_start
            result[(dst_idx, dst_idx + len(patch_value))] = (patch_start, patch_end)
            dst_idx += len(patch_value)
            src_idx = patch_end
        return result

    def __getitem__(self, item):
        assert isinstance(item, slice)
        assert item.step is None or item.step == 1
        parts = list()
        idx = item.start
        stop = len(self.original) if item.stop is None else item.stop
        for patch in self._patches:
            patch_start, patch_end, patch_value = patch
            if item.start > patch_end:
                continue
            if stop <= patch_start:
                parts.append(self.original[idx:stop])
                break
            parts.append(self.original[idx:patch_start])
            assert stop >= patch_end
            parts.append(str(patch_value))
            idx = patch_end
        parts.append(self.original[idx:stop])
        return "".join(parts)

    def __str__(self):
        return self[0:]

    def __len__(self):
        return len(str(self))
