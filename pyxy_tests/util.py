from pprint import pprint

import parso.tree
import parso.python.tree


def dump_parse_for(parsed: parso.python.tree.Module) -> None:
    print("################################################################################")
    pprint(parsed.children[0])
    pprint(parsed.children[0].children)
    print()
    print()


def _assert_no_error_leaf_inner(root: parso.python.tree.Module, node: parso.tree.NodeOrLeaf):
    if isinstance(node, parso.python.tree.Module):
        for child in node.children:
            _assert_no_error_leaf_inner(root, child)
    elif isinstance(node, parso.tree.BaseNode):
        if isinstance(node, parso.python.tree.PythonErrorNode):
            dump_parse_for(root)
            assert False
        for child in node.children:
            _assert_no_error_leaf_inner(root, child)
    else:
        assert isinstance(node, parso.tree.Leaf), repr(node)
        if isinstance(node, parso.python.tree.PythonErrorLeaf):
            dump_parse_for(root)
            assert False


def assert_no_error_leaf(root: parso.python.tree.Module):
    _assert_no_error_leaf_inner(root, root)
