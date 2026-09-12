from pathlib import Path

from agent_summary import deterministic_summary
from function_app import erase_etl_data


def test_deterministic_summary_totals_rows_and_nulls():
    result = deterministic_summary(
        [
            {"row_count": 2, "null_cells": 1},
            {"row_count": 3, "null_cells": 4},
        ]
    )
    assert "5 combined rows" in result
    assert "5 null cells" in result


def test_erase_etl_data_removes_files(tmp_path, monkeypatch):
    input_folder = tmp_path / "incoming"
    output_folder = tmp_path / "output"
    work_folder = tmp_path / "work"
    for folder in (input_folder, output_folder, work_folder):
        folder.mkdir()
        (folder / "payload.txt").write_text("temporary")
    monkeypatch.setenv("ETL_OUTPUT_FOLDER", str(output_folder))
    monkeypatch.setenv("ETL_WORK_FOLDER", str(work_folder))

    erase_etl_data({"input_folder": str(input_folder)})

    assert all(not any(Path(folder).iterdir()) for folder in (input_folder, output_folder, work_folder))