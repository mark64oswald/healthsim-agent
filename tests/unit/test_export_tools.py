"""Tests for export tools."""

import pytest
import json
from healthsim_agent.tools.export_tools import export_json, export_csv, export_ndjson


class TestExportJson:
    """Tests for JSON export."""
    
    def test_export_dict(self):
        """Export a dictionary."""
        data = {"name": "test", "value": 123}
        result = export_json(data)
        assert result.success is True
        assert "json" in result.data
        parsed = json.loads(result.data["json"])
        assert parsed["data"]["name"] == "test"
    
    def test_export_list(self):
        """Export a list of dicts."""
        data = [{"id": 1}, {"id": 2}]
        result = export_json(data)
        assert result.success is True
        parsed = json.loads(result.data["json"])
        assert len(parsed["data"]) == 2
    
    def test_export_without_metadata(self):
        """Export without metadata wrapper."""
        data = {"name": "test"}
        result = export_json(data, include_metadata=False)
        assert result.success is True
        parsed = json.loads(result.data["json"])
        assert parsed["name"] == "test"  # No 'data' wrapper
    
    def test_export_not_pretty(self):
        """Export without pretty formatting."""
        data = {"name": "test"}
        result = export_json(data, pretty=False, include_metadata=False)
        assert result.success is True
        # Should be compact (no indentation)
        assert "\n" not in result.data["json"]
    
    def test_export_to_file(self, tmp_path):
        """Export to file."""
        data = {"name": "test"}
        filepath = str(tmp_path / "test.json")
        result = export_json(data, filepath=filepath)
        assert result.success is True
        assert result.data["filepath"] == filepath
        # Verify file exists and is valid JSON
        import json
        with open(filepath) as f:
            parsed = json.load(f)
        assert parsed["data"]["name"] == "test"


class TestExportCsv:
    """Tests for CSV export."""
    
    def test_export_simple(self):
        """Export simple list of dicts."""
        data = [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"},
        ]
        result = export_csv(data)
        assert result.success is True
        assert result.data["rows"] == 2
        assert "csv" in result.data
        lines = result.data["csv"].strip().split("\n")
        assert len(lines) == 3  # header + 2 rows
    
    def test_export_with_columns(self):
        """Export with specific columns."""
        data = [
            {"id": 1, "name": "Alice", "age": 30},
            {"id": 2, "name": "Bob", "age": 25},
        ]
        result = export_csv(data, columns=["id", "name"])
        assert result.success is True
        assert result.data["columns"] == 2
        # 'age' should not be in output
        assert "age" not in result.data["csv"]
    
    def test_export_no_header(self):
        """Export without header row."""
        data = [{"id": 1, "name": "Alice"}]
        result = export_csv(data, include_header=False)
        assert result.success is True
        lines = result.data["csv"].strip().split("\n")
        assert len(lines) == 1  # No header
    
    def test_export_empty(self):
        """Handle empty list."""
        result = export_csv([])
        assert result.success is False
        assert "No data" in result.error
    
    def test_export_to_file(self, tmp_path):
        """Export to file."""
        data = [{"id": 1, "name": "Test"}]
        filepath = str(tmp_path / "test.csv")
        result = export_csv(data, filepath=filepath)
        assert result.success is True
        assert result.data["filepath"] == filepath


class TestExportNdjson:
    """Tests for NDJSON export."""
    
    def test_export_simple(self):
        """Export list to NDJSON."""
        data = [{"id": 1}, {"id": 2}, {"id": 3}]
        result = export_ndjson(data)
        assert result.success is True
        assert result.data["records"] == 3
        lines = result.data["ndjson"].strip().split("\n")
        assert len(lines) == 3
        # Each line should be valid JSON
        for line in lines:
            json.loads(line)
    
    def test_export_empty(self):
        """Handle empty list."""
        result = export_ndjson([])
        assert result.success is False
    
    def test_export_to_file(self, tmp_path):
        """Export to file."""
        data = [{"id": 1}, {"id": 2}]
        filepath = str(tmp_path / "test.ndjson")
        result = export_ndjson(data, filepath=filepath)
        assert result.success is True
        assert result.data["filepath"] == filepath
