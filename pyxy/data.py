from __future__ import annotations

from dataclasses import dataclass
from typing import Self

import parso.python.tree
import parso.tree

from .util import split_list, is_node, is_leaf, line_col_to_index


@dataclass(frozen=True)
class Tag:
    name: str
    attrs: tuple[str | tuple[str, str | PyData], ...]
    self_closing: bool

    @classmethod
    def build(cls, decoded: str, contents: list[parso.tree.Leaf], self_closing: bool) -> Self:
        attrs: list[str | tuple[str, str | PyData]] = list()
        parts = split_list(contents, lambda c: is_leaf(c, value="="))
        last_attr_name: str | None = None

        for part in parts:
            name_parts = part
            if is_leaf(part[0], kind="string"):
                assert last_attr_name is not None
                attrs.pop()
                attrs.append((last_attr_name, part[0].value))
                last_attr_name = None
                name_parts = part[1:]
            elif is_node(part[0], kind="fstring_expr"):
                assert last_attr_name is not None
                attrs.pop()
                attrs.append((last_attr_name, PyData.build(decoded, part[0].children)))
                last_attr_name = None
                name_parts = part[1:]

            if name_parts:
                name_start = line_col_to_index(decoded, *name_parts[0].start_pos)
                name_end = line_col_to_index(decoded, *name_parts[-1].end_pos)
                joined_name = decoded[name_start:name_end]
                split_names = joined_name.split(" ")
                extra_names = split_names[:-1]
                real_name = split_names[-1]
                attrs.extend(extra_names)
                attrs.append(real_name)
                last_attr_name = real_name

        tag_name = attrs[0]
        assert isinstance(tag_name, str)

        return cls(tag_name, tuple(attrs[1:]), self_closing=self_closing)


@dataclass(frozen=True)
class CloseTag:
    name: str

    @classmethod
    def build(cls, decoded: str, contents: list[parso.tree.Leaf]) -> Self:
        name_start = line_col_to_index(decoded, *contents[0].start_pos)
        name_end = line_col_to_index(decoded, *contents[-1].end_pos)
        joined_name = decoded[name_start:name_end]
        assert " " not in joined_name
        return cls(joined_name)


@dataclass(frozen=True)
class CData:
    value: str

    @classmethod
    def build(cls, decoded: str, start_item: parso.tree.NodeOrLeaf, end_item: parso.tree.NodeOrLeaf) -> Self:
        content_start = line_col_to_index(decoded, *start_item.start_pos)
        content_end = line_col_to_index(decoded, *end_item.start_pos)
        joined_content = decoded[content_start:content_end]
        return cls(joined_content)


@dataclass(frozen=True)
class PyData:
    value: str

    @classmethod
    def build(cls, decoded: str, contents: list[parso.tree.NodeOrLeaf]) -> Self:
        contents = contents[1:-1]
        content_start = line_col_to_index(decoded, *contents[0].start_pos)
        content_end = line_col_to_index(decoded, *contents[-1].end_pos)
        joined_content = decoded[content_start:content_end]
        return cls(joined_content)