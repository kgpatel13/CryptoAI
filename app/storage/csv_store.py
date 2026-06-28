from __future__ import annotations

import csv
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Iterable, Any


class CsvStore:
    def __init__(self, file_path: str | Path):
        self.file_path = Path(file_path)
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

    def append_rows(self, rows: Iterable[Any]) -> None:
        normalized_rows = []
        for row in rows:
            if is_dataclass(row):
                normalized_rows.append(asdict(row))
            elif isinstance(row, dict):
                normalized_rows.append(row)
            else:
                raise TypeError(f"Unsupported row type: {type(row)}")

        if not normalized_rows:
            return

        fieldnames = list(normalized_rows[0].keys())
        file_exists = self.file_path.exists() and self.file_path.stat().st_size > 0

        with self.file_path.open("a", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            writer.writerows(normalized_rows)
