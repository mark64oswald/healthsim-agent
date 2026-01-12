"""Tests for export_tools module."""

import pytest
import tempfile
import os
import json
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from pathlib import Path

from healthsim_agent.tools.export_tools import (
    export_json,
    export_csv,
    export_ndjson,
    _json_serializer,
)


class TestExportJson:
    """Tests for export_json function."""
    
    def test_export_dict_to_string(self):
        """Export dict to JSON string."""
        data = {"name": "Test", "value": 42}
        
        result = export_json(data, filepath=None, include_metadata=False)
        
        assert result.success is True
        assert "json" in result.data
        parsed = json.loads(result.data["json"])
        assert parsed["name"] == "Test"
        assert parsed["value"] == 42
    
    def test_export_list_to_string(self):
        """Export list of dicts to JSON string."""
        data = [{"id": 1}, {"id": 2}]
        
        result = export_json(data, filepath=None, include_metadata=False)
        
        assert result.success is True
        parsed = json.loads(result.data["json"])
        assert len(parsed) == 2
    
    def test_export_with_metadata(self):
        """Export includes metadata when requested."""
        data = {"test": "data"}
        
        result = export_json(data, filepath=None, include_metadata=True)
        
        assert result.success is True
        parsed = json.loads(result.data["json"])
        assert "metadata" in parsed
        assert "data" in parsed
        assert parsed["metadata"]["format"] == "json"
        assert parsed["metadata"]["source"] == "healthsim-agent"
    
    def test_export_to_file(self):
        """Export to file."""
        data = {"name": "FileTest"}
        
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "test.json")
            
            result = export_json(data, filepath=filepath, include_metadata=False)
            
            assert result.success is True
            assert os.path.exists(filepath)
            assert result.data["filepath"] == filepath
            
            # Read back and verify
            with open(filepath) as f:
                loaded = json.load(f)
            assert loaded["name"] == "FileTest"
    
    def test_export_creates_parent_dirs(self):
        """Export creates parent directories."""
        data = {"test": True}
        
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "nested", "deep", "test.json")
            
            result = export_json(data, filepath=filepath, include_metadata=False)
            
            assert result.success is True
            assert os.path.exists(filepath)
    
    def test_export_pretty_formatting(self):
        """Pretty formatting adds indentation."""
        data = {"a": 1, "b": 2}
        
        result = export_json(data, filepath=None, pretty=True, include_metadata=False)
        
        assert result.success is True
        json_str = result.data["json"]
        assert "\n" in json_str  # Pretty has newlines
    
    def test_export_no_pretty(self):
        """Non-pretty is compact."""
        data = {"a": 1, "b": 2}
        
        result = export_json(data, filepath=None, pretty=False, include_metadata=False)
        
        assert result.success is True
        json_str = result.data["json"]
        assert "\n" not in json_str
    
    def test_export_with_datetime(self):
        """Datetime serializes correctly."""
        data = {"timestamp": datetime(2025, 1, 15, 10, 30)}
        
        result = export_json(data, filepath=None, include_metadata=False)
        
        assert result.success is True
        parsed = json.loads(result.data["json"])
        assert "2025-01-15" in parsed["timestamp"]
    
    def test_export_with_date(self):
        """Date serializes correctly."""
        data = {"date": date(2025, 1, 15)}
        
        result = export_json(data, filepath=None, include_metadata=False)
        
        assert result.success is True
        parsed = json.loads(result.data["json"])
        assert parsed["date"] == "2025-01-15"


class TestExportCsv:
    """Tests for export_csv function."""
    
    def test_export_basic_list(self):
        """Export list of dicts to CSV string."""
        data = [
            {"name": "Alice", "age": 30},
            {"name": "Bob", "age": 25},
        ]
        
        result = export_csv(data, filepath=None)
        
        assert result.success is True
        assert "csv" in result.data
        assert result.data["rows"] == 2
        csv_str = result.data["csv"]
        assert "Alice" in csv_str
        assert "Bob" in csv_str
    
    def test_export_empty_data(self):
        """Empty data returns error."""
        result = export_csv([], filepath=None)
        
        assert result.success is False
        assert "No data" in result.error
    
    def test_export_with_columns(self):
        """Specific columns in order."""
        data = [
            {"z": 1, "a": 2, "m": 3},
        ]
        
        result = export_csv(data, filepath=None, columns=["a", "z"])
        
        assert result.success is True
        csv_str = result.data["csv"]
        assert result.data["columns"] == 2
        # First line should be header with columns in specified order
        lines = csv_str.strip().split("\n")
        assert lines[0].strip() == "a,z"
    
    def test_export_without_header(self):
        """Export without header row."""
        data = [{"a": 1}]
        
        result = export_csv(data, filepath=None, include_header=False)
        
        assert result.success is True
        csv_str = result.data["csv"]
        assert csv_str.strip() == "1"  # Just the value, no header
    
    def test_export_to_file(self):
        """Export CSV to file."""
        data = [{"name": "Test", "value": 100}]
        
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "test.csv")
            
            result = export_csv(data, filepath=filepath)
            
            assert result.success is True
            assert os.path.exists(filepath)
            
            with open(filepath) as f:
                content = f.read()
            assert "Test" in content
            assert "100" in content
    
    def test_export_with_datetime_values(self):
        """Datetime values serialized."""
        data = [{"created": datetime(2025, 1, 15, 10, 30)}]
        
        result = export_csv(data, filepath=None)
        
        assert result.success is True
        csv_str = result.data["csv"]
        assert "2025-01-15" in csv_str
    
    def test_export_with_nested_dict(self):
        """Nested dict serialized as JSON."""
        data = [{"config": {"key": "value"}}]
        
        result = export_csv(data, filepath=None)
        
        assert result.success is True
        csv_str = result.data["csv"]
        # Nested should be JSON string
        assert '"key"' in csv_str or "key" in csv_str
    
    def test_export_with_missing_keys(self):
        """Handles records with different keys."""
        data = [
            {"a": 1, "b": 2},
            {"a": 3},  # Missing 'b'
        ]
        
        result = export_csv(data, filepath=None, columns=["a", "b"])
        
        assert result.success is True
        # Should handle missing gracefully
        assert result.data["rows"] == 2


class TestExportNdjson:
    """Tests for export_ndjson function."""
    
    def test_export_to_string(self):
        """Export list to NDJSON string."""
        data = [
            {"id": 1, "name": "First"},
            {"id": 2, "name": "Second"},
        ]
        
        result = export_ndjson(data, filepath=None)
        
        assert result.success is True
        assert "ndjson" in result.data
        assert result.data["records"] == 2
        
        # Verify format - each line is valid JSON
        lines = result.data["ndjson"].split("\n")
        assert len(lines) == 2
        for line in lines:
            parsed = json.loads(line)
            assert "id" in parsed
    
    def test_export_empty_data(self):
        """Empty data returns error."""
        result = export_ndjson([], filepath=None)
        
        assert result.success is False
        assert "No data" in result.error
    
    def test_export_to_file(self):
        """Export NDJSON to file."""
        data = [{"x": 1}, {"x": 2}, {"x": 3}]
        
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "test.ndjson")
            
            result = export_ndjson(data, filepath=filepath)
            
            assert result.success is True
            assert os.path.exists(filepath)
            assert result.data["filepath"] == filepath
            assert result.data["records"] == 3
    
    def test_export_with_complex_types(self):
        """Complex types serialized correctly."""
        data = [
            {"date": date(2025, 1, 15), "value": Decimal("123.45")},
        ]
        
        result = export_ndjson(data, filepath=None)
        
        assert result.success is True
        line = result.data["ndjson"]
        parsed = json.loads(line)
        assert parsed["date"] == "2025-01-15"
        assert parsed["value"] == 123.45


class TestJsonSerializer:
    """Tests for _json_serializer helper."""
    
    def test_serialize_datetime(self):
        """Datetime serializes to ISO string."""
        dt = datetime(2025, 1, 15, 10, 30, 45)
        result = _json_serializer(dt)
        assert result == "2025-01-15T10:30:45"
    
    def test_serialize_date(self):
        """Date serializes to ISO string."""
        d = date(2025, 1, 15)
        result = _json_serializer(d)
        assert result == "2025-01-15"
    
    def test_serialize_decimal(self):
        """Decimal serializes to float."""
        d = Decimal("123.456")
        result = _json_serializer(d)
        assert result == 123.456
    
    def test_serialize_enum(self):
        """Enum serializes to value."""
        class Color(Enum):
            RED = "red"
            BLUE = "blue"
        
        result = _json_serializer(Color.RED)
        assert result == "red"
    
    def test_serialize_pydantic_model(self):
        """Object with model_dump method."""
        class MockModel:
            def model_dump(self):
                return {"field": "value"}
        
        result = _json_serializer(MockModel())
        assert result == {"field": "value"}
    
    def test_serialize_object_with_dict(self):
        """Object with __dict__ attribute."""
        class SimpleObject:
            def __init__(self):
                self.a = 1
                self.b = "test"
        
        result = _json_serializer(SimpleObject())
        assert result["a"] == 1
        assert result["b"] == "test"
    
    def test_serialize_unknown_type_raises(self):
        """Unknown type raises TypeError."""
        # Complex number is not handled by the serializer
        with pytest.raises(TypeError):
            _json_serializer(complex(1, 2))


class TestExportEdgeCases:
    """Edge case tests for export functions."""
    
    def test_json_with_special_characters(self):
        """JSON handles special characters."""
        data = {"text": "Line1\nLine2\tTab\"Quote"}
        
        result = export_json(data, filepath=None, include_metadata=False)
        
        assert result.success is True
        parsed = json.loads(result.data["json"])
        assert parsed["text"] == "Line1\nLine2\tTab\"Quote"
    
    def test_csv_with_comma_in_value(self):
        """CSV handles commas in values."""
        data = [{"text": "Hello, World"}]
        
        result = export_csv(data, filepath=None)
        
        assert result.success is True
        # Value should be quoted
        csv_str = result.data["csv"]
        assert '"Hello, World"' in csv_str
    
    def test_large_dataset(self):
        """Handle reasonably large dataset."""
        data = [{"id": i, "value": f"item-{i}"} for i in range(1000)]
        
        result = export_json(data, filepath=None, include_metadata=False)
        
        assert result.success is True
        assert result.data["size_bytes"] > 10000
