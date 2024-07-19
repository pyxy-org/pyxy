from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Self

from pyxy.util import line_col_to_index, index_to_line_col


@dataclass(frozen=True)
class ToolResults:
    tool_name: str
    status: int
    errors: tuple[ToolError, ...]
    edits: tuple[ToolEdit, ...]


@dataclass(frozen=True)
class ToolError:
    filename: str
    line: int
    column: int
    message: str


@dataclass(frozen=True)
class ToolEdit:
    filename: str
    line: int
    column: int
    replacement: str


class PyxyRemapper:
    def __init__(self, map_path: Path, py_path: Path, pyxy_path: Path):
        assert map_path.exists()
        assert py_path.exists()
        assert pyxy_path.exists()
        self.map_path = map_path
        self.py_path = py_path
        self.pyxy_path = pyxy_path

        with self.map_path.open("r") as fh:
            self.map = json.load(fh)
        with self.py_path.open("r") as fh:
            self.py_text = fh.read()
        with self.pyxy_path.open("r") as fh:
            self.pyxy_text = fh.read()

    @classmethod
    def from_py_file(cls, py_path: Path) -> Self:
        pyxy_path = py_path.with_suffix(".pyxy")
        map_path = py_path.with_name("." + py_path.name).with_suffix(".map")
        return cls(map_path, py_path, pyxy_path)

    def py_to_pyxy(self, line: int, column: int) -> tuple[int, int]:
        # TODO: This is not even close to a good design. Remove the file reads and optimize this all.

        idx = line_col_to_index(self.py_text, line, column)

        remapped_idx = None
        for py_idx, pyxy_idx in self.map:
            py_idx_start, py_idx_end = py_idx
            if py_idx_start < idx < py_idx_end:
                pyxy_idx_start, pyxy_idx_end = pyxy_idx
                # TODO: This isn't necessarily correct
                percentage_through_chunk = (idx - py_idx_start) / (py_idx_end - py_idx_start)
                remapped_idx = pyxy_idx_start + int(percentage_through_chunk * (pyxy_idx_end - pyxy_idx_start)) - 1
        assert remapped_idx is not None

        return index_to_line_col(self.pyxy_text, remapped_idx)
