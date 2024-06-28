from __future__ import annotations

from typing import Any

import pyxy  # noqa


def test_basic() -> Any:
    exec(b"name='world'\nprint(<div class={1 + 2}>Hello, {name}!</div>)".decode("pyxy"))
