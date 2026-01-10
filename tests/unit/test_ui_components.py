"""
Tests for HealthSim Agent UI Components.

Since UI is visual, testing focuses on:
1. Component rendering (no exceptions)
2. Theme color validation
3. Formatter output structure
4. Suggestion generation logic
"""

import pytest
from rich.console import Console
from rich.text import Text
from rich.panel import Panel

from healthsim_agent.ui.theme import (
    COLORS,
    ICONS,
    HEALTHSIM_THEME,
    BANNER_ART,
    SPINNER_FRAMES,
    get_status_style,
    get_icon,
)
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
from healthsim_agent.ui.suggestions import (
    SuggestionGenerator,
    get_suggestion_generator,
    get_suggestions_for_tool,
)


# =============================================================================
# Theme Tests
# =============================================================================

class TestTheme:
    """Tests for theme module."""
    
    def test_colors_defined(self):
        """All required colors should be defined."""
        required_colors = [
            "background", "surface", "border", "text", "muted",
            "user", "command", "success", "warning", "error",
            "accent", "cyan",
        ]
        for color in required_colors:
            assert color in COLORS, f"Missing color: {color}"
            assert COLORS[color].startswith("#"), f"Color {color} should be hex"
    
    def test_icons_defined(self):
        """All required icons should be defined."""
        required_icons = ["success", "error", "warning", "arrow", "bullet"]
        for icon in required_icons:
            assert icon in ICONS, f"Missing icon: {icon}"
    
    def test_healthsim_theme_is_rich_theme(self):
        """Theme should be a Rich Theme object."""
        from rich.theme import Theme
        assert isinstance(HEALTHSIM_THEME, Theme)
    
    def test_banner_art_exists(self):
        """Banner art should be defined."""
        assert BANNER_ART is not None
        assert len(BANNER_ART) > 0
    
    def test_spinner_frames(self):
        """Spinner frames should be defined."""
        assert len(SPINNER_FRAMES) > 0
        assert all(isinstance(f, str) for f in SPINNER_FRAMES)
    
    def test_get_status_style(self):
        """get_status_style should return valid styles."""
        assert "bold" in get_status_style("success")
        assert "bold" in get_status_style("error")
        assert COLORS["text"] in get_status_style("unknown")
    
    def test_get_icon(self):
        """get_icon should return icons."""
        assert get_icon("success") == "✓"
        assert get_icon("error") == "✗"
        assert get_icon("nonexistent") == ""


# =============================================================================
# Component Tests
# =============================================================================

class TestWelcomePanel:
    """Tests for WelcomePanel component."""
    
    def test_render_returns_panel(self):
        """render() should return a Panel."""
        panel = WelcomePanel()
        result = panel.render()
        assert isinstance(result, Panel)
    
    def test_render_with_custom_values(self):
        """render() should accept custom values."""
        panel = WelcomePanel()
        result = panel.render(
            version="2.0.0",
            db_path="/custom/path.db",
            provider_count="10M",
            connected=False,
        )
        assert isinstance(result, Panel)
    
    def test_render_quick_start_returns_text(self):
        """render_quick_start() should return Text."""
        panel = WelcomePanel()
        result = panel.render_quick_start()
        assert isinstance(result, Text)


class TestToolIndicator:
    """Tests for ToolIndicator component."""
    
    def test_render_returns_text(self):
        """render() should return Text."""
        indicator = ToolIndicator()
        result = indicator.render("test_tool")
        assert isinstance(result, Text)
    
    def test_render_contains_tool_name(self):
        """render() should include tool name."""
        indicator = ToolIndicator()
        result = indicator.render("search_providers")
        plain = result.plain
        assert "search_providers" in plain
        assert "→" in plain


class TestResultHeadline:
    """Tests for ResultHeadline component."""
    
    def test_success_headline(self):
        """Success headline should have checkmark."""
        headline = ResultHeadline()
        result = headline.render("Test passed", success=True)
        assert "✓" in result.plain
        assert "Test passed" in result.plain
    
    def test_error_headline(self):
        """Error headline should have X mark."""
        headline = ResultHeadline()
        result = headline.render("Test failed", success=False)
        assert "✗" in result.plain
        assert "Test failed" in result.plain
    
    def test_warning_headline(self):
        """Warning headline should have warning icon."""
        headline = ResultHeadline()
        result = headline.render("Test warning", warning=True)
        assert "⚠" in result.plain
        assert "Test warning" in result.plain


class TestSuggestionBox:
    """Tests for SuggestionBox component."""
    
    def test_render_empty_returns_empty_text(self):
        """Empty suggestions should return empty Text."""
        box = SuggestionBox()
        result = box.render([])
        assert isinstance(result, Text)
        assert len(result.plain) == 0
    
    def test_render_with_suggestions(self):
        """Suggestions should be formatted."""
        box = SuggestionBox()
        result = box.render(["First suggestion", "Second suggestion"])
        plain = result.plain
        assert "Suggested:" in plain
        assert "First suggestion" in plain
        assert "Second suggestion" in plain
    
    def test_render_max_three_suggestions(self):
        """Should only show max 3 suggestions."""
        box = SuggestionBox()
        result = box.render(["One", "Two", "Three", "Four", "Five"])
        plain = result.plain
        assert "One" in plain
        assert "Two" in plain
        assert "Three" in plain
        assert "Four" not in plain


class TestStatusBar:
    """Tests for StatusBar component."""
    
    def test_render_minimal(self):
        """StatusBar should render with minimal info."""
        bar = StatusBar()
        result = bar.render(message_count=5)
        assert isinstance(result, Text)
        assert "5 messages" in result.plain
    
    def test_render_with_cohort(self):
        """StatusBar should include cohort info."""
        bar = StatusBar()
        result = bar.render(
            cohort_name="test_cohort",
            entity_count=100,
            message_count=10,
        )
        plain = result.plain
        assert "test_cohort" in plain
        assert "100 entities" in plain


class TestHelpDisplay:
    """Tests for HelpDisplay component."""
    
    def test_render_returns_panel(self):
        """render() should return Panel."""
        help_display = HelpDisplay()
        result = help_display.render()
        assert isinstance(result, Panel)


class TestDataPreview:
    """Tests for DataPreview component."""
    
    def test_render_json(self):
        """render_json() should return Panel."""
        preview = DataPreview()
        result = preview.render_json({"key": "value"})
        assert isinstance(result, Panel)
    
    def test_render_table_empty(self):
        """render_table() should handle empty data."""
        preview = DataPreview()
        result = preview.render_table([])
        assert isinstance(result, Panel)
    
    def test_render_table_with_data(self):
        """render_table() should format records."""
        preview = DataPreview()
        data = [
            {"name": "Alice", "age": 30},
            {"name": "Bob", "age": 25},
        ]
        result = preview.render_table(data)
        assert isinstance(result, Panel)


# =============================================================================
# Formatter Tests
# =============================================================================

class TestFormatters:
    """Tests for formatter functions."""
    
    def test_format_tool_indicator(self):
        """format_tool_indicator should return Text."""
        result = format_tool_indicator("test_tool")
        assert isinstance(result, Text)
        assert "test_tool" in result.plain
    
    def test_format_result_headline_success(self):
        """format_result_headline success should have checkmark."""
        result = format_result_headline(True, "Success!")
        assert "✓" in result.plain
    
    def test_format_result_headline_error(self):
        """format_result_headline error should have X."""
        result = format_result_headline(False, "Failed!")
        assert "✗" in result.plain
    
    def test_format_data_panel_string(self):
        """format_data_panel should handle strings."""
        result = format_data_panel("Test content", "Test Title")
        assert isinstance(result, Panel)
    
    def test_format_data_panel_dict(self):
        """format_data_panel should handle dicts."""
        result = format_data_panel({"key": "value"}, "Dict Panel")
        assert isinstance(result, Panel)
    
    def test_format_data_panel_list(self):
        """format_data_panel should handle lists."""
        result = format_data_panel(["item1", "item2"], "List Panel")
        assert isinstance(result, Panel)
    
    def test_format_data_table_empty(self):
        """format_data_table should handle empty list."""
        result = format_data_table([], "Empty Table")
        assert isinstance(result, Panel)
    
    def test_format_data_table_with_records(self):
        """format_data_table should format records."""
        records = [{"id": 1, "name": "Test"}]
        result = format_data_table(records, "Test Table")
        assert isinstance(result, Panel)
    
    def test_format_suggestions_empty(self):
        """format_suggestions should handle empty list."""
        result = format_suggestions([])
        assert isinstance(result, Text)
        assert len(result.plain) == 0
    
    def test_format_suggestions_with_items(self):
        """format_suggestions should format suggestions."""
        result = format_suggestions(["Suggestion 1", "Suggestion 2"])
        assert isinstance(result, Text)
        assert "Suggested:" in result.plain
    
    def test_format_sql(self):
        """format_sql should return syntax-highlighted Panel."""
        result = format_sql("SELECT * FROM patients")
        assert isinstance(result, Panel)
    
    def test_format_json(self):
        """format_json should return syntax-highlighted Panel."""
        result = format_json({"test": "data"})
        assert isinstance(result, Panel)
    
    def test_format_error_basic(self):
        """format_error should create error panel."""
        result = format_error("Test error")
        assert isinstance(result, Panel)
    
    def test_format_error_with_suggestions(self):
        """format_error should include suggestions."""
        result = format_error(
            "Test error",
            details="More info",
            suggestions=["Try this", "Or this"],
        )
        assert isinstance(result, Panel)
    
    def test_format_cohort_summary(self):
        """format_cohort_summary should format summary dict."""
        summary = {
            "name": "test_cohort",
            "description": "A test cohort",
            "entity_counts": {"patients": 10, "claims": 50},
            "total_entities": 60,
        }
        result = format_cohort_summary(summary)
        assert isinstance(result, Panel)
    
    def test_format_provider_results(self):
        """format_provider_results should format search results."""
        result_data = {
            "providers": [
                {"name": "Dr. Smith", "npi": "1234567890", "practice_city": "Austin", "practice_state": "TX"},
            ],
            "result_count": 1,
            "filters_applied": {"state": "TX"},
        }
        result = format_provider_results(result_data)
        assert isinstance(result, Panel)


# =============================================================================
# Suggestion Tests
# =============================================================================

class TestSuggestionGenerator:
    """Tests for SuggestionGenerator."""
    
    def test_default_suggestions(self):
        """Should return default suggestions with no context."""
        gen = SuggestionGenerator()
        suggestions = gen.get_suggestions()
        assert len(suggestions) > 0
        assert len(suggestions) <= 3
    
    def test_update_context_tracks_tool(self):
        """update_context should track last tool."""
        gen = SuggestionGenerator()
        gen.update_context("test_tool", {"success": True})
        assert gen._last_tool == "test_tool"
    
    def test_suggestions_after_add_entities_patients(self):
        """Should give patient-specific suggestions."""
        gen = SuggestionGenerator()
        gen.update_context("add_entities", {
            "entity_counts": {"patients": 10},
            "entities_added_this_batch": 10,
        })
        suggestions = gen.get_suggestions()
        assert len(suggestions) > 0
        # Should suggest patient follow-ups
        assert any("encounter" in s.lower() or "claim" in s.lower() or "fhir" in s.lower() 
                   for s in suggestions)
    
    def test_suggestions_after_add_entities_members(self):
        """Should give member-specific suggestions."""
        gen = SuggestionGenerator()
        gen.update_context("add_entities", {
            "entity_counts": {"members": 5},
            "entities_added_this_batch": 5,
        })
        suggestions = gen.get_suggestions()
        assert len(suggestions) > 0
    
    def test_suggestions_after_search_providers(self):
        """Should give provider search follow-up suggestions."""
        gen = SuggestionGenerator()
        gen.update_context("search_providers", {
            "result_count": 50,
            "providers": [{"npi": "123"}],
        })
        suggestions = gen.get_suggestions()
        assert len(suggestions) > 0
    
    def test_suggestions_after_query(self):
        """Should give query follow-up suggestions."""
        gen = SuggestionGenerator()
        gen.update_context("query", {"row_count": 100})
        suggestions = gen.get_suggestions()
        assert len(suggestions) > 0
    
    def test_clear_context(self):
        """clear_context should reset state."""
        gen = SuggestionGenerator()
        gen.update_context("test_tool", {"test": "data"})
        gen.clear_context()
        assert gen._last_tool is None
        assert gen._last_entity_type is None


class TestSuggestionHelpers:
    """Tests for suggestion helper functions."""
    
    def test_get_suggestion_generator_singleton(self):
        """get_suggestion_generator should return singleton."""
        gen1 = get_suggestion_generator()
        gen2 = get_suggestion_generator()
        assert gen1 is gen2
    
    def test_get_suggestions_for_tool(self):
        """get_suggestions_for_tool should return suggestions."""
        suggestions = get_suggestions_for_tool(
            "add_entities",
            {"entity_counts": {"patients": 5}},
        )
        assert isinstance(suggestions, list)
        assert len(suggestions) <= 3


# =============================================================================
# Integration Tests
# =============================================================================

class TestUIIntegration:
    """Integration tests for UI components working together."""
    
    def test_console_with_theme(self):
        """Console should work with HealthSim theme."""
        console = Console(theme=HEALTHSIM_THEME, force_terminal=True)
        # Should not raise
        console.print("[success]Test[/success]")
        console.print("[error]Test[/error]")
        console.print("[muted]Test[/muted]")
    
    def test_all_components_render_without_error(self):
        """All components should render without exceptions."""
        console = Console(theme=HEALTHSIM_THEME, force_terminal=True)
        
        # Create all components
        welcome = WelcomePanel(console)
        tool = ToolIndicator(console)
        headline = ResultHeadline(console)
        suggestions = SuggestionBox(console)
        status = StatusBar(console)
        help_display = HelpDisplay(console)
        preview = DataPreview(console)
        
        # Render all - should not raise
        welcome.render()
        welcome.render_quick_start()
        tool.render("test")
        headline.render("test", success=True)
        suggestions.render(["test"])
        status.render(message_count=1)
        help_display.render()
        preview.render_json({"test": 1})
        preview.render_table([{"a": 1}])
