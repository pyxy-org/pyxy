from pathlib import Path

import parso
import pytest


@pytest.fixture
def grammar():
    grammar_file = Path(__file__).parent.parent / "pyxy" / "grammar" / "pyxy312.txt"
    return parso.load_grammar(path=str(grammar_file))
