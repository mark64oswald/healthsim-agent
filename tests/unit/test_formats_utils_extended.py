"""Extended tests for formats/utils module."""

import pytest
from datetime import date, datetime


class TestFormatDate:
    """Tests for format_date function."""
    
    def test_format_date_basic(self):
        """Test formatting basic date."""
        from healthsim_agent.formats.utils import format_date
        
        d = date(2024, 1, 15)
        result = format_date(d)
        assert result is not None
        assert "2024" in result
    
    def test_format_date_none(self):
        """Test formatting None date."""
        from healthsim_agent.formats.utils import format_date
        
        result = format_date(None)
        assert result is None or result == ""
    
    def test_format_date_with_format(self):
        """Test formatting with custom format."""
        from healthsim_agent.formats.utils import format_date
        
        d = date(2024, 1, 15)
        result = format_date(d, "%m/%d/%Y")
        assert result == "01/15/2024"


class TestFormatDatetime:
    """Tests for format_datetime function."""
    
    def test_format_datetime_basic(self):
        """Test formatting basic datetime."""
        from healthsim_agent.formats.utils import format_datetime
        
        dt = datetime(2024, 1, 15, 10, 30, 0)
        result = format_datetime(dt)
        assert result is not None
        assert "2024" in result
    
    def test_format_datetime_none(self):
        """Test formatting None datetime."""
        from healthsim_agent.formats.utils import format_datetime
        
        result = format_datetime(None)
        assert result is None or result == ""
    
    def test_format_datetime_with_format(self):
        """Test formatting with custom format."""
        from healthsim_agent.formats.utils import format_datetime
        
        dt = datetime(2024, 1, 15, 10, 30, 0)
        result = format_datetime(dt, "%Y-%m-%dT%H:%M:%S")
        assert "10:30:00" in result


class TestSafeStr:
    """Tests for safe_str function."""
    
    def test_safe_str_string(self):
        """Test with string input."""
        from healthsim_agent.formats.utils import safe_str
        
        result = safe_str("hello")
        assert result == "hello"
    
    def test_safe_str_none(self):
        """Test with None input."""
        from healthsim_agent.formats.utils import safe_str
        
        result = safe_str(None)
        assert result == "" or result is None
    
    def test_safe_str_number(self):
        """Test with number input."""
        from healthsim_agent.formats.utils import safe_str
        
        result = safe_str(123)
        assert result == "123"
    
    def test_safe_str_float(self):
        """Test with float input."""
        from healthsim_agent.formats.utils import safe_str
        
        result = safe_str(3.14)
        assert "3.14" in result


class TestTruncate:
    """Tests for truncate function."""
    
    def test_truncate_short_string(self):
        """Test truncating short string."""
        from healthsim_agent.formats.utils import truncate
        
        result = truncate("hello", 10)
        assert result == "hello"
    
    def test_truncate_long_string(self):
        """Test truncating long string."""
        from healthsim_agent.formats.utils import truncate
        
        result = truncate("hello world this is a long string", 10)
        assert len(result) <= 13  # 10 + "..."
    
    def test_truncate_none(self):
        """Test truncating None raises error."""
        from healthsim_agent.formats.utils import truncate
        
        with pytest.raises(TypeError):
            truncate(None, 10)
    
    def test_truncate_exact_length(self):
        """Test truncating exact length string."""
        from healthsim_agent.formats.utils import truncate
        
        result = truncate("hello", 5)
        assert result == "hello"


class TestCSVExporter:
    """Tests for CSVExporter class."""
    
    def test_create_exporter(self):
        """Test creating CSV exporter."""
        from healthsim_agent.formats.utils import CSVExporter
        
        exporter = CSVExporter()
        assert exporter is not None
    
    def test_export_empty_data(self):
        """Test exporting empty data."""
        from healthsim_agent.formats.utils import CSVExporter
        
        exporter = CSVExporter()
        result = exporter.export([])
        assert result is not None


class TestJSONExporter:
    """Tests for JSONExporter class."""
    
    def test_create_exporter(self):
        """Test creating JSON exporter."""
        from healthsim_agent.formats.utils import JSONExporter
        
        exporter = JSONExporter()
        assert exporter is not None
    
    def test_export_empty_data(self):
        """Test exporting empty data."""
        from healthsim_agent.formats.utils import JSONExporter
        
        exporter = JSONExporter()
        result = exporter.export([])
        assert result is not None
    
    def test_export_dict(self):
        """Test exporting dict."""
        from healthsim_agent.formats.utils import JSONExporter
        
        exporter = JSONExporter()
        result = exporter.export({"name": "test", "value": 123})
        assert result is not None
        assert "test" in result
