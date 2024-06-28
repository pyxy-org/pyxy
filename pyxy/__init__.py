from __future__ import annotations

import codecs
import enum
import re
from collections import deque
from dataclasses import dataclass
from encodings import utf_8
from typing import Self

import parso.python.tree
import parso.tree

from .util import split_list, is_node, is_leaf, chain_lookup, line_col_to_index, format_attr

type XmlName = str
type XmlAttrValue = str


def inject_htpy(transformed_source: str) -> str:
    pattern = re.compile(r'^(?!#|import|from\s+\w+\s+import).+', re.MULTILINE)
    match = pattern.search(transformed_source)
    index = match.start() if match else len(transformed_source)
    return transformed_source[:index] + "import htpy as _pyxy_htpy\n" + transformed_source[index:]


class XmlParserState(enum.Enum):
    INITIAL = enum.auto()
    TAG_CONTENTS = enum.auto()
    TAG_CONTENTS_CLOSING = enum.auto()
    TAG_OR_CDATA = enum.auto()


@dataclass(frozen=True)
class Tag:
    name: str
    attrs: tuple[str | tuple[str, str], ...]
    self_closing: bool

    @classmethod
    def build(cls, decoded: str, contents: list[parso.tree.Leaf], self_closing: bool) -> Self:
        attrs: list[XmlName | tuple[XmlName, XmlAttrValue]] = list()
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

        return Tag(tag_name, tuple(attrs[1:]), self_closing=self_closing)


@dataclass(frozen=True)
class CloseTag:
    name: str

    @classmethod
    def build(cls, decoded: str, contents: list[parso.tree.Leaf]) -> CloseTag:
        name_start = line_col_to_index(decoded, *contents[0].start_pos)
        name_end = line_col_to_index(decoded, *contents[-1].end_pos)
        joined_name = decoded[name_start:name_end]
        assert " " not in joined_name
        return CloseTag(joined_name)


@dataclass(frozen=True)
class CData:
    value: str

    @classmethod
    def build(cls, decoded: str, contents: list[parso.tree.Leaf]) -> CData:
        content_start = line_col_to_index(decoded, *contents[0].start_pos)
        content_end = line_col_to_index(decoded, *contents[-1].end_pos)
        joined_content = decoded[content_start:content_end]
        return CData(joined_content)


def transform_xml_node(node: parso.python.tree.PythonNode, decoded: str) -> str:
    state = XmlParserState.INITIAL
    queue: deque[parso.tree.NodeOrLeaf] = deque([node])

    current_tag_is_closing: bool = False
    current_tag_contents: list = list()
    current_cdata: list = list()
    entries: list[Tag | CloseTag | CData] = list()

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
                    entries.append(Tag.build(decoded, current_tag_contents.copy(), self_closing=self_closing))
                else:
                    entries.append(CloseTag.build(decoded, current_tag_contents.copy()))
                current_tag_contents.clear()
                current_tag_is_closing = False
                state = XmlParserState.TAG_OR_CDATA

            case XmlParserState.TAG_OR_CDATA:
                if is_leaf(item, value="<"):
                    if current_cdata:
                        entries.append(CData.build(decoded, current_cdata.copy()))
                        current_cdata.clear()
                    state = XmlParserState.TAG_CONTENTS
                elif is_leaf(item):
                    current_cdata.append(item)
                elif is_node(item):
                    current_cdata.extend(item.children)
                else:
                    assert False

    # Build code from the list of entries
    tag_stack = list()
    built_code = ""
    for entry in entries:
        if isinstance(entry, Tag):
            ending = ""
            if not entry.self_closing:
                tag_stack.append(entry)
                ending = "["
            built_code += f"getattr(_pyxy_htpy, {entry.name!r})({{{", ".join(format_attr(a) for a in entry.attrs)}}}){ending}"
        elif isinstance(entry, CloseTag):
            assert entry.name == tag_stack[-1].name
            tag_stack.pop()
            built_code += "]"
        elif isinstance(entry, CData):
            built_code += repr(entry.value)
        else:
            assert False

    return built_code


def pyxy_decode(input: bytes | memoryview, errors: str = 'strict') -> tuple[str, int]:
    from pathlib import Path

    if isinstance(input, memoryview):
        input = bytes(input)

    # First, convert bytes to str. Assumes utf-8.
    decoded = input.decode('utf-8', errors=errors)

    # Then, parse the code
    pyxy_grammar = parso.load_grammar(path=str(Path(__file__).parent / "grammar" / "pyxy312.txt"))
    parsed: parso.tree.BaseNode = pyxy_grammar.parse(decoded)

    # Find all instances of an xml node. Keep track of where we should cut and paste in the generated code.
    replacements: list[tuple[int, int, str]] = list()
    tree_search: list[parso.tree.NodeOrLeaf] = [parsed]
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
        # print(node)
        if isinstance(node, parso.python.tree.PythonNode) and node.type == "xml":
            replacements.append((
                line_col_to_index(decoded, *node.start_pos),
                line_col_to_index(decoded, *node.end_pos),
                transform_xml_node(node, decoded)
            ))

    # Paste in the replacements
    result_items: list[str] = list()
    last_end = 0
    for replacement in replacements:
        rp_start, rp_end, rp_text = replacement
        result_items.append(decoded[last_end:rp_start])
        result_items.append(rp_text)
        last_end = rp_end
    result_items.append(decoded[last_end:len(decoded)])

    # Join the items and inject the htpy import
    joined_result_items = "".join(result_items)
    result = inject_htpy(joined_result_items)

    return result, len(input)


class PyxyStreamReader(utf_8.StreamReader):
    decode = pyxy_decode


class PyxyIncrementalDecoder(codecs.BufferedIncrementalDecoder):
    def decode(self, input: bytes, final: bool = False) -> str:
        self.buffer += input
        if final:
            decoded, _ = pyxy_decode(self.buffer)
            self.buffer = b''
            return decoded
        else:
            return ''


def search_function(name):
    if name != 'pyxy':
        return None

    import encodings

    utf8 = encodings.search_function('utf8')
    return codecs.CodecInfo(
        name='pyxy',
        encode=utf8.encode,
        decode=pyxy_decode,
        incrementalencoder=utf8.incrementalencoder,
        incrementaldecoder=PyxyIncrementalDecoder,
        streamreader=PyxyStreamReader,
        streamwriter=utf8.streamwriter
    )


codecs.register(search_function)
