import json
from pathlib import Path

from sarif_om import from_json, to_json

from pyxy.util import line_col_to_index, index_to_line_col


def remap_sarif(sarif_data: str) -> str:
    sarif_log = from_json(sarif_data)

    for run in sarif_log.runs:
        # print(run.tool.driver.name)
        for result in run.results:
            rule = next(r for r in run.tool.driver.rules if r.id == result.rule_id)
            for location in result.locations:
                file = location.physical_location.artifact_location.uri.removeprefix("file://")
                region = location.physical_location.region
                line, col = region.start_line, region.start_column

                py_filepath = Path(file)
                pyxy_filepath = py_filepath.with_suffix(".pyxy")
                if pyxy_filepath.exists():
                    map_filepath = py_filepath.with_name("." + py_filepath.name).with_suffix(".map")
                    with map_filepath.open("r") as fh:
                        map = json.load(fh)

                    # TODO: Optimize
                    with py_filepath.open("r") as fh:
                        py_text = fh.read()
                    idx = line_col_to_index(py_text, line, col)

                    remapped_idx = None
                    for py_idx, pyxy_idx in map:
                        py_idx_start, py_idx_end = py_idx
                        if py_idx_start < idx < py_idx_end:
                            pyxy_idx_start, pyxy_idx_end = pyxy_idx
                            # TODO: This isn't necessarily correct
                            percentage_through_chunk = (idx - py_idx_start) / (py_idx_end - py_idx_start)
                            remapped_idx = pyxy_idx_start + int(percentage_through_chunk * (pyxy_idx_end - pyxy_idx_start)) - 1
                    assert remapped_idx is not None

                    with pyxy_filepath.open("r") as fh:
                        pyxy_text = fh.read()

                    file = str(pyxy_filepath)
                    line, col = index_to_line_col(pyxy_text, remapped_idx)

                print(f"{file}:{line}:{col} {result.level}: {rule.id} {rule.short_description.text}")

    return to_json(sarif_log)
