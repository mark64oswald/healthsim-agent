"""
Tests for HealthSim Agent Terminal UI.
"""

import pytest
from unittest.mock import MagicMock, patch

from healthsim_agent.ui.terminal import TerminalUI, ToolCallbackHandler
from healthsim_agent.ui.theme import HEALTHSIM_THEME


class TestTerminalUI:
    """Tests for TerminalUI class."""
    
    @pytest.fixture
    def ui(self):
        """Create TerminalUI instance."""
        return TerminalUI(debug=True)
    
    def test_init(self, ui):
        """Should initialize with default state."""
        assert ui.debug is True
        assert ui._current_cohort is None
        assert ui._entity_count == 0
        assert ui._message_count == 0
    
    def test_console_has_theme(self, ui):
        """Console should have HealthSim theme."""
        assert ui.console is not None
    
    def test_update_context_cohort(self, ui):
        """Should update cohort name."""
        ui.update_context(cohort_name="test_cohort")
        assert ui._current_cohort == "test_cohort"
    
    def test_update_context_entity_count(self, ui):
        """Should update entity count."""
        ui.update_context(entity_count=100)
        assert ui._entity_count == 100
    
    def test_update_context_message_count(self, ui):
        """Should update message count."""
        ui.update_context(message_count=5)
        assert ui._message_count == 5
    
    def test_update_context_all(self, ui):
        """Should update all context fields."""
        ui.update_context(
            cohort_name="my_cohort",
            entity_count=50,
            message_count=10,
        )
        assert ui._current_cohort == "my_cohort"
        assert ui._entity_count == 50
        assert ui._message_count == 10


class TestTerminalUIComponents:
    """Tests for TerminalUI component methods."""
    
    @pytest.fixture
    def ui(self):
        return TerminalUI(debug=True)
    
    def test_show_result_success(self, ui):
        """show_result_success should not raise."""
        ui.show_result_success("Operation complete")
    
    def test_show_result_error(self, ui):
        """show_result_error should not raise."""
        ui.show_result_error("Operation failed")
    
    def test_show_result_warning(self, ui):
        """show_result_warning should not raise."""
        ui.show_result_warning("Partial success")
    
    def test_clear_screen(self, ui):
        """clear_screen should not raise."""
        ui.clear_screen()
    
    def test_show_tool_start(self, ui):
        """show_tool_start should not raise."""
        ui.show_tool_start("test_tool")


class TestTerminalUICommands:
    """Tests for slash command handling."""
    
    @pytest.fixture
    def ui(self):
        return TerminalUI(debug=True)
    
    @pytest.fixture
    def mock_agent(self):
        """Create mock agent for testing."""
        agent = MagicMock()
        agent.is_connected = True
        agent.session.messages = []
        return agent
    
    def test_handle_quit_command(self, ui, mock_agent):
        """Quit command should return True (exit)."""
        result = ui._handle_command("/quit", mock_agent)
        assert result is True  # Should exit
    
    def test_handle_exit_command(self, ui, mock_agent):
        """Exit command should return True (exit)."""
        result = ui._handle_command("/exit", mock_agent)
        assert result is True  # Should exit
    
    def test_handle_q_command(self, ui, mock_agent):
        """q command should return True (exit)."""
        result = ui._handle_command("/q", mock_agent)
        assert result is True  # Should exit
    
    def test_handle_help_command(self, ui, mock_agent):
        """Help command should return False (continue)."""
        result = ui._handle_command("/help", mock_agent)
        assert result is False  # Should continue
    
    def test_handle_status_command(self, ui, mock_agent):
        """Status command should return False (continue)."""
        result = ui._handle_command("/status", mock_agent)
        assert result is False  # Should continue
    
    def test_handle_clear_command(self, ui, mock_agent):
        """Clear command should return False (continue)."""
        result = ui._handle_command("/clear", mock_agent)
        assert result is False  # Should continue
    
    def test_handle_unknown_command(self, ui, mock_agent):
        """Unknown command should return False (continue)."""
        result = ui._handle_command("/unknown", mock_agent)
        assert result is False  # Should continue


class TestToolCallbackHandler:
    """Tests for ToolCallbackHandler class."""
    
    @pytest.fixture
    def ui(self):
        return TerminalUI(debug=True)
    
    @pytest.fixture
    def handler(self, ui):
        return ToolCallbackHandler(ui)
    
    def test_init(self, handler, ui):
        """Should initialize with UI reference."""
        assert handler.ui is ui
        assert handler._current_tool is None
    
    def test_on_tool_start_sets_tool(self, handler):
        """on_tool_start should track current tool."""
        handler.on_tool_start("test_tool", {})
        assert handler._current_tool == "test_tool"
    
    def test_on_tool_end_clears_tool(self, handler):
        """on_tool_end should clear current tool."""
        handler._current_tool = "test_tool"
        handler.on_tool_end("test_tool", {"success": True})
        assert handler._current_tool is None
    
    def test_on_tool_error_clears_tool(self, handler):
        """on_tool_error should clear current tool."""
        handler._current_tool = "test_tool"
        handler.on_tool_error("test_tool", Exception("Test error"))
        assert handler._current_tool is None
    
    def test_generate_headline_add_entities(self, handler):
        """Should generate headline for add_entities."""
        result = {
            "entities_added_this_batch": 50,
            "entity_counts": {"patients": 50},
        }
        headline = handler._generate_headline("add_entities", result)
        assert "50" in headline
        assert "patients" in headline
    
    def test_generate_headline_save_cohort(self, handler):
        """Should generate headline for save_cohort."""
        result = {"cohort_name": "my_cohort"}
        headline = handler._generate_headline("save_cohort", result)
        assert "my_cohort" in headline
    
    def test_generate_headline_search_providers(self, handler):
        """Should generate headline for search_providers."""
        result = {"result_count": 100}
        headline = handler._generate_headline("search_providers", result)
        assert "100" in headline
    
    def test_generate_headline_query(self, handler):
        """Should generate headline for query."""
        result = {"row_count": 25}
        headline = handler._generate_headline("query", result)
        assert "25" in headline
    
    def test_generate_headline_unknown_tool(self, handler):
        """Should generate generic headline for unknown tool."""
        headline = handler._generate_headline("unknown_tool", {})
        assert "unknown_tool" in headline
        assert "completed" in headline


class TestTerminalUIFormatting:
    """Tests for data formatting methods."""
    
    @pytest.fixture
    def ui(self):
        return TerminalUI(debug=True)
    
    def test_show_data_panel(self, ui):
        """show_data_panel should not raise."""
        ui.show_data_panel({"key": "value"}, title="Test")
    
    def test_show_data_table(self, ui):
        """show_data_table should not raise."""
        data = [{"id": 1, "name": "Test"}]
        ui.show_data_table(data, title="Records")
    
    def test_show_cohort_summary(self, ui):
        """show_cohort_summary should not raise."""
        summary = {
            "name": "test",
            "entity_counts": {"patients": 10},
            "total_entities": 10,
        }
        ui.show_cohort_summary(summary)
    
    def test_show_provider_results(self, ui):
        """show_provider_results should not raise."""
        result = {
            "providers": [{"name": "Dr. Test", "npi": "123"}],
            "result_count": 1,
        }
        ui.show_provider_results(result)
    
    def test_show_error_basic(self, ui):
        """show_error should not raise."""
        ui.show_error("Test error")
    
    def test_show_error_with_details(self, ui):
        """show_error with details should not raise."""
        ui.show_error("Test error", details="Some details")
    
    def test_show_error_with_suggestions(self, ui):
        """show_error with suggestions should not raise."""
        ui.show_error("Test error", suggestions=["Try this"])
    
    def test_show_suggestions(self, ui):
        """show_suggestions should not raise."""
        ui.show_suggestions(["Suggestion 1", "Suggestion 2"])
    
    def test_show_suggestions_empty(self, ui):
        """show_suggestions with empty list should not raise."""
        ui.show_suggestions([])
    
    def test_show_suggestions_for_tool(self, ui):
        """show_suggestions_for_tool should not raise."""
        ui.show_suggestions_for_tool("add_entities", {
            "entity_counts": {"patients": 10}
        })


class TestTerminalUIDisplay:
    """Tests for display methods."""
    
    @pytest.fixture
    def ui(self):
        return TerminalUI(debug=True)
    
    def test_show_welcome(self, ui):
        """show_welcome should not raise."""
        ui.show_welcome()
    
    def test_show_welcome_custom(self, ui):
        """show_welcome with custom params should not raise."""
        ui.show_welcome(
            version="2.0.0",
            db_path="/custom/path.db",
            provider_count="10M",
            connected=False,
        )
    
    def test_show_goodbye(self, ui):
        """show_goodbye should not raise."""
        ui.show_goodbye()
    
    def test_show_help(self, ui):
        """show_help should not raise."""
        ui.show_help()
    
    def test_show_response(self, ui):
        """show_response should not raise."""
        ui.show_response("# Test Response\n\nThis is **markdown**.")
    
    def test_show_status_bar(self, ui):
        """show_status_bar should not raise."""
        ui.show_status_bar()
    
    def test_show_status_bar_with_context(self, ui):
        """show_status_bar with context should not raise."""
        ui._current_cohort = "test_cohort"
        ui._entity_count = 100
        ui._message_count = 5
        ui.show_status_bar()
    
    def test_show_status(self, ui):
        """show_status should not raise."""
        mock_agent = MagicMock()
        mock_agent.is_connected = True
        mock_agent.session.messages = ["msg1", "msg2"]
        ui.show_status(mock_agent)
    
    def test_show_user_message(self, ui):
        """show_user_message should not raise."""
        ui.show_user_message("Hello, generate some patients")


class TestTerminalUIThinking:
    """Tests for thinking/spinner functionality."""
    
    @pytest.fixture
    def ui(self):
        return TerminalUI(debug=True)
    
    def test_show_thinking_returns_live(self, ui):
        """show_thinking should return Live context."""
        from rich.live import Live
        live = ui.show_thinking()
        assert live is not None
        ui.stop_thinking()
    
    def test_stop_thinking_after_show(self, ui):
        """stop_thinking should work after show_thinking."""
        ui.show_thinking()
        ui.stop_thinking()  # Should not raise
    
    def test_stop_thinking_without_show(self, ui):
        """stop_thinking should not raise if not started."""
        ui.stop_thinking()  # Should not raise
