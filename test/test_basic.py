from __future__ import annotations

from typing import Any


def test_basic() -> Any:
    import pyxy  # noqa
    html = b"<a>foo</a>"
    assert html.decode(encoding="pyxy") == html.decode(encoding="utf-8")
