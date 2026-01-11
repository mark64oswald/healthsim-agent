"""Export tools for HealthSim Agent.

Provides generic export capabilities beyond format-specific transforms.
"""

import json
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from pathlib import Path
from typing import Any

from healthsim_agent.tools.base import ToolResult, ok, err


def export_json(
    data: dict[str, Any] | list[dict[str, Any]],
    filepath: str | None = None,
    pretty: bool = True,
    include_metadata: bool = True,
) -> ToolResult:
    """Export data to JSON format.
    
    Args:
        data: Data to export (dict or list of dicts)
        filepath: Optional file path to save to. If None, returns JSON string.
        pretty: Use pretty formatting with indentation
        include_metadata: Include export metadata (timestamp, version)
    
    Returns:
        ToolResult with JSON string or file path
    """
    try:
        # Prepare export data
        if include_metadata:
            export_data = {
                "metadata": {
                    "exported_at": datetime.now().isoformat(),
                    "format": "json",
                    "version": "1.0",
                    "source": "healthsim-agent",
                },
                "data": data,
            }
        else:
            export_data = data
        
        # Serialize
        indent = 2 if pretty else None
        json_str = json.dumps(export_data, indent=indent, default=_json_serializer)
        
        # Write to file if path provided
        if filepath:
            path = Path(filepath)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json_str)
            
            return ok(
                data={"filepath": str(path), "size_bytes": len(json_str)},
                message=f"Exported JSON to {filepath} ({len(json_str):,} bytes)"
            )
        else:
            return ok(
                data={"json": json_str, "size_bytes": len(json_str)},
                message=f"Generated JSON ({len(json_str):,} bytes)"
            )
        
    except Exception as e:
        return err(f"Export failed: {str(e)}")


def export_csv(
    data: list[dict[str, Any]],
    filepath: str | None = None,
    columns: list[str] | None = None,
    include_header: bool = True,
) -> ToolResult:
    """Export data to CSV format.
    
    Args:
        data: List of dictionaries to export
        filepath: Optional file path to save to. If None, returns CSV string.
        columns: Specific columns to include (in order). If None, uses all keys.
        include_header: Include header row
    
    Returns:
        ToolResult with CSV string or file path
    """
    try:
        import csv
        import io
        
        if not data:
            return err("No data to export")
        
        # Determine columns
        if columns:
            fieldnames = columns
        else:
            # Get all unique keys across all records
            all_keys = set()
            for record in data:
                all_keys.update(record.keys())
            fieldnames = sorted(all_keys)
        
        # Write to string buffer
        buffer = io.StringIO()
        writer = csv.DictWriter(buffer, fieldnames=fieldnames, extrasaction='ignore')
        
        if include_header:
            writer.writeheader()
        
        for record in data:
            # Serialize complex values
            row = {}
            for key in fieldnames:
                value = record.get(key)
                if isinstance(value, (dict, list)):
                    row[key] = json.dumps(value)
                elif isinstance(value, (date, datetime)):
                    row[key] = value.isoformat()
                elif isinstance(value, Decimal):
                    row[key] = str(value)
                elif isinstance(value, Enum):
                    row[key] = value.value
                else:
                    row[key] = value
            writer.writerow(row)
        
        csv_str = buffer.getvalue()
        
        # Write to file if path provided
        if filepath:
            path = Path(filepath)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(csv_str)
            
            return ok(
                data={"filepath": str(path), "rows": len(data), "columns": len(fieldnames)},
                message=f"Exported {len(data)} rows to {filepath}"
            )
        else:
            return ok(
                data={"csv": csv_str, "rows": len(data), "columns": len(fieldnames)},
                message=f"Generated CSV with {len(data)} rows, {len(fieldnames)} columns"
            )
        
    except Exception as e:
        return err(f"CSV export failed: {str(e)}")


def export_ndjson(
    data: list[dict[str, Any]],
    filepath: str | None = None,
) -> ToolResult:
    """Export data to NDJSON (newline-delimited JSON) format.
    
    This format is ideal for streaming and large datasets.
    
    Args:
        data: List of dictionaries to export
        filepath: Optional file path to save to. If None, returns NDJSON string.
    
    Returns:
        ToolResult with NDJSON string or file path
    """
    try:
        if not data:
            return err("No data to export")
        
        lines = []
        for record in data:
            line = json.dumps(record, default=_json_serializer)
            lines.append(line)
        
        ndjson_str = "\n".join(lines)
        
        # Write to file if path provided
        if filepath:
            path = Path(filepath)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(ndjson_str)
            
            return ok(
                data={"filepath": str(path), "records": len(data)},
                message=f"Exported {len(data)} records to {filepath}"
            )
        else:
            return ok(
                data={"ndjson": ndjson_str, "records": len(data)},
                message=f"Generated NDJSON with {len(data)} records"
            )
        
    except Exception as e:
        return err(f"NDJSON export failed: {str(e)}")


# =============================================================================
# Helper Functions
# =============================================================================

def _json_serializer(obj: Any) -> Any:
    """Custom JSON serializer for non-standard types."""
    if isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, date):
        return obj.isoformat()
    elif isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, Enum):
        return obj.value
    elif hasattr(obj, "model_dump"):
        return obj.model_dump()
    elif hasattr(obj, "__dict__"):
        return obj.__dict__
    else:
        raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "export_json",
    "export_csv",
    "export_ndjson",
]
