import os
from pprint import pprint

import parso

g = parso.load_grammar(path=f"{os.getcwd()}/pyxy/grammar/pyxy312.txt")

def dump_parse_for(code: str) -> None:
    print("################################################################################")
    print(code)
    print("--------------------------------------------------------------------------------")
    v = g.parse(code)
    pprint(v.children[0])
    pprint(v.children[0].children)
    print()
    print()


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


if __name__ == "__main__":
    dump_parse_for("(<div></div>)")
    dump_parse_for("(<div><a>test</a></div>)")
    dump_parse_for("(<ul><li>one</li><li>two</li></ul>)")
    dump_parse_for("(<div>asdf</div>)")
    # dump_parse_for("(<div>)</div>)")
    # dump_parse_for("(<div>\\\\</div>)")
    dump_parse_for('(<img src="http://example.com" />)')
    dump_parse_for("(<img />)")
    dump_parse_for(pi_script)
    dump_parse_for(pyxy_script)
