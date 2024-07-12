from __future__ import annotations

import enum
import json
import re
from abc import ABC
from collections import deque, defaultdict
from dataclasses import dataclass
from typing import Self

import parso.python.tree
import parso.tree

from .util import split_list, is_node, is_leaf, line_col_to_index, PatchedString


class XmlParserState(enum.Enum):
    INITIAL = enum.auto()
    TAG_CONTENTS = enum.auto()
    TAG_CONTENTS_CLOSING = enum.auto()
    TAG_OR_CDATA = enum.auto()


@dataclass(frozen=True)
class XmlEntry(ABC):
    ...


@dataclass(frozen=True)
class Tag(XmlEntry):
    name: str
    attrs: tuple[str | tuple[str, str | PyData], ...]
    self_closing: bool

    @classmethod
    def build(cls, transpiler: PyxyTranspiler, contents: list[parso.tree.Leaf], self_closing: bool) -> Self:
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
                attrs.append((last_attr_name, PyData.build(transpiler, part[0].children)))
                last_attr_name = None
                name_parts = part[1:]

            if name_parts:
                name_start = line_col_to_index(transpiler.string.original, *name_parts[0].start_pos)
                name_end = line_col_to_index(transpiler.string.original, *name_parts[-1].end_pos)
                joined_name = transpiler.string[name_start:name_end]
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
class CloseTag(XmlEntry):
    name: str

    @classmethod
    def build(cls, transpiler: PyxyTranspiler, contents: list[parso.tree.Leaf]) -> Self:
        name_start = line_col_to_index(transpiler.string.original, *contents[0].start_pos)
        name_end = line_col_to_index(transpiler.string.original, *contents[-1].end_pos)
        joined_name = transpiler.string.original[name_start:name_end]
        assert " " not in joined_name
        return cls(joined_name)


@dataclass(frozen=True)
class CData(XmlEntry):
    value: str

    @classmethod
    def build(cls, transpiler: PyxyTranspiler, start_item: parso.tree.NodeOrLeaf, end_item: parso.tree.NodeOrLeaf) -> Self:
        content_start = line_col_to_index(transpiler.string.original, *start_item.start_pos)
        content_end = line_col_to_index(transpiler.string.original, *end_item.start_pos)
        joined_content = transpiler.string.original[content_start:content_end]
        return cls(joined_content)


@dataclass(frozen=True)
class PyData(XmlEntry):
    """Represents Python code inside curly braces within XML markup"""
    value: str

    @classmethod
    def build(cls, transpiler: PyxyTranspiler, contents: list[parso.tree.NodeOrLeaf]) -> Self:
        transpiler.find_and_replace_xml(contents)
        contents = contents[1:-1]
        content_start = line_col_to_index(transpiler.string.original, *contents[0].start_pos)
        content_end = line_col_to_index(transpiler.string.original, *contents[-1].end_pos)
        joined_content = transpiler.string[content_start:content_end]
        return cls(joined_content)


class PyxyTranspiler:
    def __init__(self, pyxy_code: str) -> None:
        from pathlib import Path

        self.string = PatchedString(pyxy_code)

        self.grammar = parso.load_grammar(path=str(Path(__file__).parent / "grammar" / "pyxy312.txt"))
        self.seen_xml = set()

    def find_and_replace_xml(self, initial_nodes: list[parso.tree.NodeOrLeaf]) -> None:
        """Find all instances of an xml node. Keep track of where we should cut and paste in the generated code."""

        tree_search: list[parso.tree.NodeOrLeaf] = initial_nodes.copy()
        while tree_search:
            node = tree_search.pop(0)
            if isinstance(node, (parso.tree.ErrorNode, parso.tree.ErrorLeaf)):
                # from pprint import pprint
                # pprint(parsed.children[0].children)
                raise Exception(f"error node: {node}")
            if isinstance(node, parso.tree.Leaf):
                continue

            assert isinstance(node, parso.tree.BaseNode)
            tree_search.extend(node.children)

            if isinstance(node, parso.python.tree.PythonNode) and node.type == "xml":
                if node in self.seen_xml:
                    continue
                entries = self.xml_node_to_xml_entries(node)
                self.patch_xml_entries(node, entries)
                self.seen_xml.add(node)

    def xml_node_to_xml_entries(self, node: parso.python.tree.PythonNode) -> list[XmlEntry]:
        state = XmlParserState.INITIAL
        queue: deque[parso.tree.NodeOrLeaf] = deque([node])

        current_tag_is_closing: bool = False
        current_tag_contents: list = list()
        current_cdata: list = list()
        entries: list[XmlEntry] = list()

        children_to_search = list()

        while queue:
            item = queue.popleft()

            match state:
                case XmlParserState.INITIAL:
                    if is_node(item, kind="xml"):
                        queue.extendleft(reversed(item.children))
                        state = XmlParserState.TAG_OR_CDATA
                    else:
                        assert False

                case XmlParserState.TAG_CONTENTS:
                    if is_leaf(item):
                        if is_leaf(item, value=">") or (is_leaf(item, value="/") and current_tag_contents):
                            queue.appendleft(item)
                            state = XmlParserState.TAG_CONTENTS_CLOSING
                        elif is_leaf(item, value="/"):
                            current_tag_is_closing = True
                        else:
                            current_tag_contents.append(item)
                    elif is_node(item, kind="xml_tag_content"):
                        current_tag_contents.extend(item.children)
                        state = XmlParserState.TAG_CONTENTS_CLOSING
                    elif is_node(item, kind="xml_opened"):
                        queue.extendleft(reversed(item.children))
                    else:
                        assert False

                case XmlParserState.TAG_CONTENTS_CLOSING:
                    if is_leaf(item, value="/"):
                        item = queue.popleft()
                        assert is_leaf(item, value=">")
                        self_closing = True
                    elif is_leaf(item, value=">"):
                        self_closing = False
                    else:
                        assert False
                    if not current_tag_is_closing:
                        entries.append(Tag.build(self, current_tag_contents.copy(), self_closing=self_closing))
                    else:
                        entries.append(CloseTag.build(self, current_tag_contents.copy()))
                    current_tag_contents.clear()
                    current_tag_is_closing = False
                    state = XmlParserState.TAG_OR_CDATA

                case XmlParserState.TAG_OR_CDATA:
                    if is_leaf(item, value="<"):
                        if current_cdata:
                            entries.append(CData.build(self, start_item=current_cdata[0], end_item=item))
                            current_cdata.clear()
                        state = XmlParserState.TAG_CONTENTS
                    elif is_leaf(item):
                        current_cdata.append(item)
                    elif is_node(item, kind="fstring_expr"):
                        if current_cdata:
                            entries.append(CData.build(self, start_item=current_cdata[0], end_item=item))
                            current_cdata.clear()
                        entries.append(PyData.build(self, item.children))
                        children_to_search.extend(item.children)
                    elif is_node(item):
                        current_cdata.extend(item.children)
                    else:
                        assert False
        return entries

    def patch_xml_entries(self, node: parso.tree.NodeOrLeaf, entries: list[XmlEntry]) -> None:
        # Build code from the list of entries
        tag_stack = list()
        built_code = ""
        empty = defaultdict(lambda: True)
        sibling_data = False
        for entry in entries:
            if isinstance(entry, Tag):
                if not empty[tuple(tag_stack)]:
                    built_code += ", "
                empty[tuple(tag_stack)] = False

                ending = ""
                if not entry.self_closing:
                    tag_stack.append(entry)
                    ending = "[("
                built_code += f"getattr(_pyxy_htpy, {entry.name!r})({{{", ".join(self.format_attr(a) for a in entry.attrs)}}}){ending}"
                sibling_data = False
            elif isinstance(entry, CloseTag):
                assert entry.name == tag_stack[-1].name
                tag_stack.pop()
                built_code += ")]"
                sibling_data = False
            elif isinstance(entry, CData):
                if sibling_data:
                    built_code += " + "
                elif not empty[tuple(tag_stack)]:
                    built_code += ", "
                empty[tuple(tag_stack)] = False

                built_code += "_pyxy_html.unescape(" + repr(entry.value) + ")"
                sibling_data = True
            elif isinstance(entry, PyData):
                if sibling_data:
                    built_code += " + "
                elif not empty[tuple(tag_stack)]:
                    built_code += ", "
                empty[tuple(tag_stack)] = False

                built_code += entry.value
                sibling_data = True
            else:
                assert False

        self.string.patch(
            line_col_to_index(self.string.original, *node.start_pos),
            line_col_to_index(self.string.original, *node.end_pos),
            PatchedString(built_code)
        )

    @staticmethod
    def format_attr(attr: str | tuple[str, str]):
        if not isinstance(attr, tuple):
            return f"{attr!r}: True"

        attr_name, attr_value = attr
        if isinstance(attr_value, PyData):
            attr_value = attr_value.value
        else:
            assert isinstance(attr_value, str)
            attr_value = attr_value
        return f"{attr_name!r}: {attr_value}"

    def inject_imports(self) -> None:
        pattern = re.compile(r'((^(#|\'|"|import|from).*\n)|(^\n))+', re.MULTILINE)
        file_header = pattern.match(str(self.string))
        inject_index = file_header.end() if file_header else 0
        self.string.patch(inject_index, inject_index, "import htpy as _pyxy_htpy\nimport html as _pyxy_html\n\n")

    def run(self) -> str:
        parsed: parso.tree.BaseNode = self.grammar.parse(self.string.original)

        self.find_and_replace_xml([parsed])
        self.inject_imports()

        return str(self.string)

    def dump_map(self) -> str:
        mapping = self.string.get_mapping()
        to_serialize: list[tuple[tuple, tuple]] = list()
        for key, value in mapping.items():
            to_serialize.append((key, value))
        return json.dumps(to_serialize)
