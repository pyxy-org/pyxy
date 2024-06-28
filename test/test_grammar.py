import parso

from .util import assert_no_error_leaf

pi_script = """
def outer():
    def calculate_pi(n_terms):
        pi = 0
        for i in range(n_terms):
            pi += (-1)**i / (2*i + 1)
        return pi * 4

    # Example usage
    script = "?\\nasdf"
    n_terms = 1000000
    print(calculate_pi(n_terms))
""".strip("\n")


pyxy_script = f"""
def outer():
    node = <div>Hello {{value}}!</div>
    node2 = <pre>{pi_script}</pre>
"""


def test_self_closing_element(grammar: parso.Grammar):
    assert_no_error_leaf(grammar.parse('<img />'))
    assert_no_error_leaf(grammar.parse('<img src="test.img" />'))


def test_element_with_body(grammar: parso.Grammar):
    assert_no_error_leaf(grammar.parse('<div></div>'))
    assert_no_error_leaf(grammar.parse('<div class="container">asdf</div>'))


def test_sibling(grammar: parso.Grammar):
    assert_no_error_leaf(grammar.parse('<ul><li>one</li><li>two</li></ul>'))


def test_wrapping(grammar: parso.Grammar):
    assert_no_error_leaf(grammar.parse('(<div></div>)'))
    assert_no_error_leaf(grammar.parse('[<div></div>]'))
    assert_no_error_leaf(grammar.parse('([<div></div>])'))
    assert_no_error_leaf(grammar.parse('(<img />)'))
    assert_no_error_leaf(grammar.parse('(<ul><li>one</li><li>two</li></ul>)'))


def test_normal_script(grammar: parso.Grammar):
    assert_no_error_leaf(grammar.parse(pi_script))


def test_wrapped_python_script(grammar: parso.Grammar):
    assert_no_error_leaf(grammar.parse(pyxy_script))
