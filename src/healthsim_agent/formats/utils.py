"""Format export utilities.

Ported from: healthsim-workspace/packages/core/src/healthsim/formats/utils.py
"""

import csv
import json
from datetime import date, datetime
from io import StringIO
from pathlib import Path
from typing import Any

from pydantic import BaseModel


def format_date(d: date | datetime | None, format_str: str = "%Y-%m-%d") -> str | None:
    """Format a date to string."""
    if d is None:
        return None
    return d.strftime(format_str)


def format_datetime(dt: datetime | None, format_str: str = "%Y-%m-%dT%H:%M:%S") -> str | None:
    """Format a datetime to ISO-like string."""
    if dt is None:
        return None
    return dt.strftime(format_str)


def safe_str(value: Any) -> str:
    """Safely convert any value to string."""
    if value is None:
        return ""
    return str(value)


def truncate(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate text to max length with suffix."""
    if len(text) <= max_length:
        return text
    return text[: max_length - len(suffix)] + suffix


class JSONExporter:
    """Export data to JSON format."""

    def __init__(
        self,
        indent: int | None = 2,
        exclude_none: bool = True,
        by_alias: bool = False,
    ) -> None:
        self.indent = indent
        self.exclude_none = exclude_none
        self.by_alias = by_alias

    def export(self, obj: BaseModel | dict | list) -> str:
        """Export object to JSON string."""
        if isinstance(obj, BaseModel):
            return obj.model_dump_json(
                indent=self.indent,
                exclude_none=self.exclude_none,
                by_alias=self.by_alias,
            )
        else:
            return json.dumps(obj, indent=self.indent, default=str)

    def export_to_file(self, obj: BaseModel | dict | list, path: Path) -> None:
        """Export object to JSON file."""
        path.write_text(self.export(obj))

    def export_list(self, items: list[BaseModel | dict]) -> str:
        """Export a list of items to JSON."""
        result = []
        for item in items:
            if isinstance(item, BaseModel):
                result.append(
                    item.model_dump(
                        exclude_none=self.exclude_none,
                        by_alias=self.by_alias,
                    )
                )
            else:
                result.append(item)
        return json.dumps(result, indent=self.indent, default=str)


class CSVExporter:
    """Export tabular data to CSV format."""

    def __init__(
        self,
        delimiter: str = ",",
        quotechar: str = '"',
        include_header: bool = True,
    ) -> None:
        self.delimiter = delimiter
        self.quotechar = quotechar
        self.include_header = include_header

    def export(
        self,
        data: list[dict[str, Any]],
        columns: list[str] | None = None,
    ) -> str:
        """Export data to CSV string."""
        if not data:
            return ""

        if columns is None:
            columns = list(data[0].keys())

        output = StringIO()
        writer = csv.DictWriter(
            output,
            fieldnames=columns,
            delimiter=self.delimiter,
            quotechar=self.quotechar,
            quoting=csv.QUOTE_MINIMAL,
            extrasaction="ignore",
        )

        if self.include_header:
            writer.writeheader()

        for row in data:
            str_row = {k: str(v) if v is not None else "" for k, v in row.items()}
            writer.writerow(str_row)

        return output.getvalue()

    def export_to_file(
        self,
        data: list[dict[str, Any]],
        path: Path,
        columns: list[str] | None = None,
    ) -> None:
        """Export data to CSV file."""
        path.write_text(self.export(data, columns))

    def export_models(
        self,
        models: list[BaseModel],
        columns: list[str] | None = None,
        exclude_none: bool = True,
    ) -> str:
        """Export Pydantic models to CSV."""
        data = []
        for model in models:
            row = model.model_dump(exclude_none=exclude_none)
            flat_row = self._flatten_dict(row)
            data.append(flat_row)
        return self.export(data, columns)

    def _flatten_dict(
        self,
        d: dict[str, Any],
        parent_key: str = "",
        sep: str = "_",
    ) -> dict[str, Any]:
        """Flatten a nested dictionary."""
        items: list[tuple[str, Any]] = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep).items())
            else:
                items.append((new_key, v))
        return dict(items)


__all__ = [
    "format_date",
    "format_datetime",
    "safe_str",
    "truncate",
    "JSONExporter",
    "CSVExporter",
]
