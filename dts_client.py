import os
from pathlib import Path
from typing import Any

import httpx


def normalize_with_dts(file_path: str) -> dict[str, Any]:
    endpoint = os.getenv("DTS_NORMALIZATION_URL", "").rstrip("/")
    route = os.getenv("DTS_NORMALIZATION_PATH", "/normalize")
    if not endpoint:
        return normalize_locally(file_path)
    try:
        with Path(file_path).open("rb") as workbook:
            response = httpx.post(
                f"{endpoint}/{route.lstrip('/')}",
                files={
                    "file": (
                        Path(file_path).name,
                        workbook,
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    )
                },
                timeout=float(os.getenv("DTS_TIMEOUT_SECONDS", "120")),
            )
        response.raise_for_status()
        return response.json()
    except (httpx.HTTPError, OSError, ValueError) as error:
        if os.getenv("DTS_REQUIRED", "false").lower() == "true":
            raise RuntimeError(f"DTS normalization failed for {file_path}") from error
        return normalize_locally(file_path)


def normalize_locally(file_path: str) -> dict[str, Any]:
    import pandas as pd

    frame = pd.concat(pd.read_excel(file_path, sheet_name=None), ignore_index=True)
    numeric_totals = {
        str(column): float(value)
        for column, value in frame.select_dtypes(include="number").sum().items()
    }
    return {
        "file_name": Path(file_path).name,
        "row_count": int(len(frame.index)),
        "columns": [str(column) for column in frame.columns],
        "null_cells": int(frame.isna().sum().sum()),
        "numeric_totals": numeric_totals,
    }