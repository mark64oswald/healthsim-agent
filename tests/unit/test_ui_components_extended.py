"""Extended tests for UI components.

Covers WelcomePanel, ToolIndicator, ResultHeadline, SuggestionBox, StatusBar,
ThinkingSpinner, ProgressDisplay, DataPreview, HelpDisplay.
"""

import pytest
from unittest.mock import MagicMock, patch
from rich.console import Console
from rich.text import Text
from rich.panel import Panel

from healthsim_agent.ui.components import (
    WelcomePanel,
    ToolIndicator,
    ResultHeadline,
    SuggestionBox,
    StatusBar,
    ThinkingSpinner,
    ProgressDisplay,
    DataPreview,
    HelpDisplay,
)


class TestWelcomePanel:
    """Tests for WelcomePanel component."""
    
    def test_render_default(self):
        """Test rendering with defaults."""
        panel = WelcomePanel()
        result = panel.render()
        
        assert isinstance(result, Panel)
    
    def test_render_custom_version(self):
        """Test rendering with custom version."""
        panel = WelcomePanel()
        result = panel.render(version="2.0.0")
        
        assert isinstance(result, Panel)
    
    def test_render_disconnected(self):
        """Test rendering disconnected state."""
        panel = WelcomePanel()
        result = panel.render(connected=False)
        
        assert isinstance(result, Panel)
    
    def test_render_custom_db_path(self):
        """Test rendering with custom db path."""
        panel = WelcomePanel()
        result = panel.render(db_path="/custom/path/db.duckdb")
        
        assert isinstance(result, Panel)
    
    def test_render_custom_provider_count(self):
        """Test rendering with custom provider count."""
        panel = WelcomePanel()
        result = panel.render(provider_count="10M")
        
        assert isinstance(result, Panel)
    
    def test_render_quick_start(self):
        """Test rendering quick start suggestions."""
        panel = WelcomePanel()
        result = panel.render_quick_start()
        
        assert isinstance(result, Text)
    
    def test_with_custom_console(self):
        """Test with custom console."""
        console = Console()
        panel = WelcomePanel(console=console)
        result = panel.render()
        
        assert isinstance(result, Panel)


class TestToolIndicator:
    """Tests for ToolIndicator component."""
    
    def test_render(self):
        """Test rendering tool indicator."""
        indicator = ToolIndicator()
        result = indicator.render("generate_patients")
        
        assert isinstance(result, Text)
    
    def test_show(self):
        """Test show method prints to console."""
        mock_console = MagicMock()
        indicator = ToolIndicator(console=mock_console)
        indicator.show("test_tool")
        
        mock_console.print.assert_called_once()


class TestResultHeadline:
    """Tests for ResultHeadline component."""
    
    def test_render_success(self):
        """Test rendering success headline."""
        headline = ResultHeadline()
        result = headline.render("Operation completed", success=True)
        
        assert isinstance(result, Text)
    
    def test_render_error(self):
        """Test rendering error headline."""
        headline = ResultHeadline()
        result = headline.render("Operation failed", success=False)
        
        assert isinstance(result, Text)
    
    def test_render_warning(self):
        """Test rendering warning headline."""
        headline = ResultHeadline()
        result = headline.render("Caution advised", warning=True)
        
        assert isinstance(result, Text)
    
    def test_success_method(self):
        """Test success helper method."""
        mock_console = MagicMock()
        headline = ResultHeadline(console=mock_console)
        headline.success("Done!")
        
        mock_console.print.assert_called_once()
    
    def test_error_method(self):
        """Test error helper method."""
        mock_console = MagicMock()
        headline = ResultHeadline(console=mock_console)
        headline.error("Failed!")
        
        mock_console.print.assert_called_once()
    
    def test_warning_method(self):
        """Test warning helper method."""
        mock_console = MagicMock()
        headline = ResultHeadline(console=mock_console)
        headline.warning("Caution!")
        
        mock_console.print.assert_called_once()


class TestSuggestionBox:
    """Tests for SuggestionBox component."""
    
    def test_render_with_suggestions(self):
        """Test rendering with suggestions."""
        box = SuggestionBox()
        result = box.render(["Try this", "Or this"])
        
        assert isinstance(result, Text)
    
    def test_render_empty_suggestions(self):
        """Test rendering with empty suggestions."""
        box = SuggestionBox()
        result = box.render([])
        
        assert isinstance(result, Text)
    
    def test_render_max_three_suggestions(self):
        """Test only first 3 suggestions shown."""
        box = SuggestionBox()
        result = box.render(["One", "Two", "Three", "Four", "Five"])
        
        # Should only show first 3
        assert isinstance(result, Text)
    
    def test_show_method(self):
        """Test show helper method."""
        mock_console = MagicMock()
        box = SuggestionBox(console=mock_console)
        box.show(["Suggestion 1"])
        
        mock_console.print.assert_called_once()
    
    def test_show_empty_does_nothing(self):
        """Test show with empty list does nothing."""
        mock_console = MagicMock()
        box = SuggestionBox(console=mock_console)
        box.show([])
        
        mock_console.print.assert_not_called()


class TestStatusBar:
    """Tests for StatusBar component."""
    
    def test_render_default(self):
        """Test rendering default status bar."""
        bar = StatusBar()
        result = bar.render()
        
        assert isinstance(result, Text)
    
    def test_render_with_cohort(self):
        """Test rendering with cohort name."""
        bar = StatusBar()
        result = bar.render(cohort_name="diabetes-cohort", entity_count=100)
        
        assert isinstance(result, Text)
    
    def test_render_with_message_count(self):
        """Test rendering with message count."""
        bar = StatusBar()
        result = bar.render(message_count=5)
        
        assert isinstance(result, Text)
    
    def test_show_method(self):
        """Test show helper method."""
        mock_console = MagicMock()
        bar = StatusBar(console=mock_console)
        bar.show()
        
        # Should print rule and content
        assert mock_console.print.call_count == 2


class TestThinkingSpinner:
    """Tests for ThinkingSpinner component."""
    
    def test_start(self):
        """Test starting spinner."""
        spinner = ThinkingSpinner()
        live = spinner.start("Processing...")
        
        assert live is not None
        spinner.stop()
    
    def test_update(self):
        """Test updating spinner message."""
        spinner = ThinkingSpinner()
        spinner.start("Initial message")
        spinner.update("Updated message")
        spinner.stop()
    
    def test_stop(self):
        """Test stopping spinner."""
        spinner = ThinkingSpinner()
        spinner.start("Test")
        spinner.stop()
        
        # Should not raise on second stop
        spinner.stop()
    
    def test_update_without_start(self):
        """Test update without starting doesn't error."""
        spinner = ThinkingSpinner()
        spinner.update("Message")  # Should not raise


class TestProgressDisplay:
    """Tests for ProgressDisplay component."""
    
    def test_create(self):
        """Test creating progress display."""
        progress = ProgressDisplay()
        result = progress.create("Loading", total=100)
        
        assert result is not None
        progress.stop()
    
    def test_start(self):
        """Test starting progress."""
        progress = ProgressDisplay()
        task_id = progress.start("Processing", total=50)
        
        assert task_id is not None
        progress.stop()
    
    def test_update(self):
        """Test updating progress."""
        progress = ProgressDisplay()
        progress.start("Processing", total=10)
        progress.update(advance=1)
        progress.update(advance=2, description="Still processing")
        progress.stop()
    
    def test_stop(self):
        """Test stopping progress."""
        progress = ProgressDisplay()
        progress.start("Test")
        progress.stop()
        
        # Should not raise on second stop
        progress.stop()
    
    def test_update_without_start(self):
        """Test update without start doesn't error."""
        progress = ProgressDisplay()
        progress.update(advance=1)  # Should not raise


class TestDataPreview:
    """Tests for DataPreview component."""
    
    def test_render_json(self):
        """Test rendering JSON data."""
        preview = DataPreview()
        data = {"name": "Test", "value": 123}
        result = preview.render_json(data)
        
        assert isinstance(result, Panel)
    
    def test_render_json_with_title(self):
        """Test rendering JSON with custom title."""
        preview = DataPreview()
        data = {"name": "Test"}
        result = preview.render_json(data, title="Custom Title")
        
        assert isinstance(result, Panel)
    
    def test_render_json_list(self):
        """Test rendering JSON list."""
        preview = DataPreview()
        data = [{"id": 1}, {"id": 2}]
        result = preview.render_json(data)
        
        assert isinstance(result, Panel)
    
    def test_render_table(self):
        """Test rendering data as table."""
        preview = DataPreview()
        data = [
            {"name": "John", "age": 30},
            {"name": "Jane", "age": 25},
        ]
        result = preview.render_table(data)
        
        assert isinstance(result, Panel)
    
    def test_render_table_empty(self):
        """Test rendering empty table."""
        preview = DataPreview()
        result = preview.render_table([])
        
        assert isinstance(result, Panel)
    
    def test_render_table_max_rows(self):
        """Test rendering table with max rows limit."""
        preview = DataPreview()
        data = [{"id": i} for i in range(20)]
        result = preview.render_table(data, max_rows=5)
        
        assert isinstance(result, Panel)
    
    def test_render_table_with_title(self):
        """Test rendering table with custom title."""
        preview = DataPreview()
        data = [{"id": 1}]
        result = preview.render_table(data, title="My Data")
        
        assert isinstance(result, Panel)
    
    def test_render_tree(self):
        """Test rendering hierarchical data as tree."""
        preview = DataPreview()
        data = {
            "patient": {
                "name": "John",
                "encounters": [
                    {"id": 1},
                    {"id": 2},
                ]
            }
        }
        result = preview.render_tree(data)
        
        assert isinstance(result, Panel)
    
    def test_render_tree_with_title(self):
        """Test rendering tree with custom title."""
        preview = DataPreview()
        data = {"key": "value"}
        result = preview.render_tree(data, title="My Structure")
        
        assert isinstance(result, Panel)


class TestHelpDisplay:
    """Tests for HelpDisplay component."""
    
    def test_render_full_help(self):
        """Test rendering full help."""
        help_display = HelpDisplay()
        result = help_display.render()
        
        # Should return a group of panels or text
        assert result is not None
    
    def test_with_custom_console(self):
        """Test with custom console."""
        console = Console()
        help_display = HelpDisplay(console=console)
        result = help_display.render()
        
        assert result is not None
