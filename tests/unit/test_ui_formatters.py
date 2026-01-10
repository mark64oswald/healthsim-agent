"""
Tests for HealthSim Agent UI Formatters.
"""

import pytest
from rich.text import Text
from rich.panel import Panel

from healthsim_agent.ui.formatters import (
    format_tool_indicator,
    format_result_headline,
    format_data_panel,
    format_data_table,
    format_suggestions,
    format_sql,
    format_json,
    format_error,
    format_cohort_summary,
    format_provider_results,
)


class TestFormatToolIndicator:
    """Tests for tool indicator formatting."""
    
    def test_returns_text(self):
        """Should return a Rich Text object."""
        result = format_tool_indicator("test_tool")
        assert isinstance(result, Text)
    
    def test_contains_arrow(self):
        """Should contain arrow symbol."""
        result = format_tool_indicator("test_tool")
        assert "→" in result.plain
    
    def test_contains_tool_name(self):
        """Should contain the tool name."""
        result = format_tool_indicator("my_special_tool")
        assert "my_special_tool" in result.plain


class TestFormatResultHeadline:
    """Tests for result headline formatting."""
    
    def test_success_has_checkmark(self):
        """Success headline should have checkmark."""
        result = format_result_headline(True, "Operation complete")
        assert "✓" in result.plain
    
    def test_error_has_x(self):
        """Error headline should have X."""
        result = format_result_headline(False, "Operation failed")
        assert "✗" in result.plain
    
    def test_warning_has_triangle(self):
        """Warning headline should have warning symbol."""
        result = format_result_headline(False, "Partial success", warning=True)
        assert "⚠" in result.plain
    
    def test_contains_message(self):
        """Should contain the message text."""
        result = format_result_headline(True, "Custom message here")
        assert "Custom message here" in result.plain


class TestFormatDataPanel:
    """Tests for data panel formatting."""
    
    def test_string_content(self):
        """Should handle string content."""
        result = format_data_panel("Hello world", title="Test")
        assert isinstance(result, Panel)
    
    def test_dict_content(self):
        """Should handle dict content."""
        data = {"name": "Test", "value": 123}
        result = format_data_panel(data, title="Dict Test")
        assert isinstance(result, Panel)
    
    def test_list_content(self):
        """Should handle list content."""
        data = ["Item 1", "Item 2", "Item 3"]
        result = format_data_panel(data, title="List Test")
        assert isinstance(result, Panel)
    
    def test_custom_title(self):
        """Should use custom title."""
        result = format_data_panel("Content", title="Custom Title")
        assert isinstance(result, Panel)


class TestFormatDataTable:
    """Tests for data table formatting."""
    
    def test_empty_data_returns_panel(self):
        """Empty data should still return a panel."""
        result = format_data_table([], title="Empty")
        assert isinstance(result, Panel)
    
    def test_single_record(self):
        """Should handle single record."""
        data = [{"id": 1, "name": "Test"}]
        result = format_data_table(data)
        assert isinstance(result, Panel)
    
    def test_multiple_records(self):
        """Should handle multiple records."""
        data = [
            {"id": 1, "name": "Test 1"},
            {"id": 2, "name": "Test 2"},
            {"id": 3, "name": "Test 3"},
        ]
        result = format_data_table(data)
        assert isinstance(result, Panel)
    
    def test_respects_max_rows(self):
        """Should limit rows to max_rows."""
        data = [{"id": i} for i in range(100)]
        result = format_data_table(data, max_rows=5)
        assert isinstance(result, Panel)
    
    def test_handles_wide_data(self):
        """Should handle data with many columns."""
        data = [{f"col{i}": f"val{i}" for i in range(20)}]
        result = format_data_table(data, max_cols=6)
        assert isinstance(result, Panel)


class TestFormatSuggestions:
    """Tests for suggestion box formatting."""
    
    def test_empty_suggestions(self):
        """Empty suggestions should return empty text."""
        result = format_suggestions([])
        assert isinstance(result, Text)
        assert result.plain == ""
    
    def test_single_suggestion(self):
        """Should format single suggestion."""
        result = format_suggestions(["Do something"])
        assert "Do something" in result.plain
        assert "→" in result.plain
    
    def test_multiple_suggestions(self):
        """Should format multiple suggestions."""
        suggestions = ["First", "Second", "Third"]
        result = format_suggestions(suggestions)
        assert "First" in result.plain
        assert "Second" in result.plain
        assert "Third" in result.plain
    
    def test_max_three_suggestions(self):
        """Should limit to 3 suggestions."""
        suggestions = ["One", "Two", "Three", "Four", "Five"]
        result = format_suggestions(suggestions)
        assert "Four" not in result.plain
        assert "Five" not in result.plain


class TestFormatSQL:
    """Tests for SQL formatting."""
    
    def test_returns_panel(self):
        """Should return a Rich Panel."""
        result = format_sql("SELECT * FROM users")
        assert isinstance(result, Panel)
    
    def test_handles_multiline_sql(self):
        """Should handle multiline SQL."""
        sql = """
        SELECT
            id,
            name
        FROM users
        WHERE active = true
        """
        result = format_sql(sql)
        assert isinstance(result, Panel)


class TestFormatJSON:
    """Tests for JSON formatting."""
    
    def test_dict_format(self):
        """Should format dict as JSON."""
        data = {"key": "value", "number": 42}
        result = format_json(data)
        assert isinstance(result, Panel)
    
    def test_list_format(self):
        """Should format list as JSON."""
        data = [1, 2, 3, "four"]
        result = format_json(data)
        assert isinstance(result, Panel)
    
    def test_nested_data(self):
        """Should handle nested structures."""
        data = {"nested": {"deep": {"value": 123}}}
        result = format_json(data)
        assert isinstance(result, Panel)


class TestFormatError:
    """Tests for error formatting."""
    
    def test_basic_error(self):
        """Should format basic error message."""
        result = format_error("Something went wrong")
        assert isinstance(result, Panel)
    
    def test_error_with_details(self):
        """Should include details if provided."""
        result = format_error(
            "Connection failed",
            details="The database server is not responding"
        )
        assert isinstance(result, Panel)
    
    def test_error_with_suggestions(self):
        """Should include recovery suggestions."""
        result = format_error(
            "File not found",
            suggestions=["Check the path", "Ensure file exists"]
        )
        assert isinstance(result, Panel)


class TestFormatCohortSummary:
    """Tests for cohort summary formatting."""
    
    def test_basic_summary(self):
        """Should format basic cohort summary."""
        summary = {
            "name": "Test Cohort",
            "entity_counts": {"patients": 100},
            "total_entities": 100,
        }
        result = format_cohort_summary(summary)
        assert isinstance(result, Panel)
    
    def test_summary_with_description(self):
        """Should include description if present."""
        summary = {
            "name": "Test Cohort",
            "description": "A test cohort for validation",
            "entity_counts": {"patients": 50, "claims": 200},
            "total_entities": 250,
        }
        result = format_cohort_summary(summary)
        assert isinstance(result, Panel)


class TestFormatProviderResults:
    """Tests for provider search results formatting."""
    
    def test_empty_results(self):
        """Should handle empty results."""
        result = format_provider_results({
            "providers": [],
            "result_count": 0,
        })
        assert isinstance(result, Panel)
    
    def test_with_providers(self):
        """Should format provider list."""
        result = format_provider_results({
            "providers": [
                {"name": "Dr. Smith", "npi": "1234567890", "practice_city": "Austin", "practice_state": "TX"},
                {"name": "Dr. Jones", "npi": "0987654321", "practice_city": "Dallas", "practice_state": "TX"},
            ],
            "result_count": 2,
            "filters_applied": {"state": "TX"},
        })
        assert isinstance(result, Panel)
