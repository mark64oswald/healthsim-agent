"""
HealthSim Agent - Terminal UI Implementation

Main terminal interface using Rich for rendering.
Implements UX specification with streaming responses,
tool indicators, and contextual suggestions.
"""

import asyncio
from typing import TYPE_CHECKING, Optional, Callable, Any, AsyncIterator

from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from rich.console import Console, Group
from rich.panel import Panel
from rich.text import Text
from rich.markdown import Markdown
from rich.live import Live
from rich.spinner import Spinner

from .theme import COLORS, ICONS, HEALTHSIM_THEME
from .components import (
    WelcomePanel,
    ToolIndicator,
    ResultHeadline,
    SuggestionBox,
    StatusBar,
    ThinkingSpinner,
    HelpDisplay,
    DataPreview,
)
from .formatters import (
    format_tool_indicator,
    format_result_headline,
    format_data_panel,
    format_data_table,
    format_suggestions,
    format_error,
    format_cohort_summary,
    format_provider_results,
)
from .suggestions import get_suggestion_generator, get_suggestions_for_tool

if TYPE_CHECKING:
    from healthsim_agent.agent import HealthSimAgent


class TerminalUI:
    """
    Rich-based terminal interface for HealthSim.
    
    Provides:
    - Styled welcome banner with database info
    - Streaming display of agent responses
    - Tool invocation indicators
    - Result headlines with status icons
    - Contextual suggestions
    - Session status bar
    """
    
    def __init__(self, debug: bool = False):
        self.debug = debug
        self.console = Console(theme=HEALTHSIM_THEME)
        self._history_file = ".healthsim_history"
        self._session: Optional[PromptSession] = None
        
        # UI Components
        self._welcome = WelcomePanel(self.console)
        self._tool_indicator = ToolIndicator(self.console)
        self._headline = ResultHeadline(self.console)
        self._suggestions = SuggestionBox(self.console)
        self._status_bar = StatusBar(self.console)
        self._spinner = ThinkingSpinner(self.console)
        self._help = HelpDisplay(self.console)
        self._data_preview = DataPreview(self.console)
        
        # Suggestion generator
        self._suggestion_gen = get_suggestion_generator()
        
        # Session context
        self._current_cohort: Optional[str] = None
        self._entity_count: int = 0
        self._message_count: int = 0
    
    def show_welcome(
        self,
        version: str = "1.0.0",
        db_path: str = "~/.healthsim/healthsim.duckdb",
        provider_count: str = "8.9M",
        connected: bool = True,
    ) -> None:
        """Display the welcome banner."""
        self.console.print()
        self.console.print(self._welcome.render(
            version=version,
            db_path=db_path,
            provider_count=provider_count,
            connected=connected,
        ))
        self.console.print(self._welcome.render_quick_start())
        self.console.print()
    
    def show_goodbye(self) -> None:
        """Display goodbye message."""
        self.console.print()
        self.console.print(
            f"[bold {COLORS['command']}]Thank you for using HealthSim![/]"
        )
        self.console.print()
    
    def get_input(self) -> str:
        """Get user input with prompt styling."""
        if not self._session:
            self._session = PromptSession(
                history=FileHistory(self._history_file),
                auto_suggest=AutoSuggestFromHistory(),
            )
        
        # Create styled prompt - "You: "
        prompt_text = [
            (COLORS['user'], "You"),
            (COLORS['muted'], ": "),
        ]
        
        return self._session.prompt(prompt_text)
    
    def show_user_message(self, message: str) -> None:
        """Display user message (for async mode where input is separate)."""
        text = Text()
        text.append("You", style=f"bold {COLORS['user']}")
        text.append(": ", style=COLORS['muted'])
        text.append(message, style=COLORS['text'])
        self.console.print(text)
        self.console.print()
    
    def show_tool_start(self, tool_name: str) -> None:
        """Show tool invocation indicator."""
        self._tool_indicator.show(tool_name)
    
    def show_thinking(self, message: str = "Thinking...") -> Live:
        """Show thinking spinner and return Live context."""
        return self._spinner.start(message)
    
    def stop_thinking(self) -> None:
        """Stop the thinking spinner."""
        self._spinner.stop()
    
    def show_result_success(self, message: str) -> None:
        """Show success headline."""
        self.console.print()
        self._headline.success(message)
    
    def show_result_error(self, message: str) -> None:
        """Show error headline."""
        self.console.print()
        self._headline.error(message)
    
    def show_result_warning(self, message: str) -> None:
        """Show warning headline."""
        self.console.print()
        self._headline.warning(message)
    
    def show_data_panel(self, data: Any, title: str = "Data") -> None:
        """Show data in a formatted panel."""
        panel = format_data_panel(data, title)
        self.console.print(panel)
    
    def show_data_table(self, records: list, title: str = "Records") -> None:
        """Show records in a formatted table."""
        panel = format_data_table(records, title)
        self.console.print(panel)
    
    def show_cohort_summary(self, summary: dict) -> None:
        """Show cohort summary panel."""
        panel = format_cohort_summary(summary)
        self.console.print(panel)
    
    def show_provider_results(self, result: dict) -> None:
        """Show provider search results."""
        panel = format_provider_results(result)
        self.console.print(panel)
    
    def show_error(self, message: str, details: str = None, suggestions: list = None) -> None:
        """Display error message with optional recovery suggestions."""
        panel = format_error(message, details, suggestions)
        self.console.print(panel)
    
    def show_response(self, response: str) -> None:
        """Display agent response with markdown formatting."""
        md = Markdown(response)
        self.console.print()
        self.console.print(md)
        self.console.print()
    
    def show_suggestions(self, suggestions: list) -> None:
        """Show contextual suggestions."""
        self._suggestions.show(suggestions)
    
    def show_suggestions_for_tool(self, tool_name: str, result: dict) -> None:
        """Show suggestions based on tool result."""
        suggestions = get_suggestions_for_tool(tool_name, result)
        if suggestions:
            self.console.print()
            self._suggestions.show(suggestions)
    
    def show_status_bar(self) -> None:
        """Show session status bar."""
        self._status_bar.show(
            cohort_name=self._current_cohort,
            entity_count=self._entity_count,
            message_count=self._message_count,
        )
    
    def update_context(
        self,
        cohort_name: Optional[str] = None,
        entity_count: Optional[int] = None,
        message_count: Optional[int] = None,
    ) -> None:
        """Update session context for status bar."""
        if cohort_name is not None:
            self._current_cohort = cohort_name
        if entity_count is not None:
            self._entity_count = entity_count
        if message_count is not None:
            self._message_count = message_count
    
    def show_status(self, agent: "HealthSimAgent") -> None:
        """Display current session status."""
        from rich.table import Table
        
        table = Table(show_header=False, box=None)
        table.add_column("Key", style=COLORS['muted'])
        table.add_column("Value", style=COLORS['text'])
        
        table.add_row("Database", "Connected" if agent.is_connected else "Not connected")
        table.add_row("Messages", str(len(agent.session.messages)))
        if self._current_cohort:
            table.add_row("Cohort", self._current_cohort)
            table.add_row("Entities", str(self._entity_count))
        table.add_row("Mode", "Interactive")
        
        panel = Panel(
            table,
            title="[bold]Session Status[/bold]",
            border_style=COLORS['border'],
        )
        self.console.print(panel)
    
    def show_help(self) -> None:
        """Display help information."""
        self._help.show()
    
    def clear_screen(self) -> None:
        """Clear the terminal screen."""
        self.console.clear()
    
    async def stream_response(
        self,
        stream: AsyncIterator[str],
        show_cursor: bool = True,
    ) -> str:
        """Stream response text with live display.
        
        Args:
            stream: Async iterator yielding text chunks
            show_cursor: Whether to show blinking cursor during stream
            
        Returns:
            Complete response text
        """
        full_text = ""
        
        with Live(console=self.console, refresh_per_second=15) as live:
            async for chunk in stream:
                full_text += chunk
                # Create display text with optional cursor
                display = Text(full_text)
                if show_cursor:
                    display.append("▌", style=COLORS["command"])
                live.update(display)
        
        # Final update without cursor
        self.console.print(Text(full_text))
        return full_text
    
    def stream_response_sync(
        self,
        text_generator: Callable[[], str],
        delay: float = 0.02,
    ) -> str:
        """Synchronous streaming simulation for non-async contexts.
        
        Args:
            text_generator: Function that returns the full text
            delay: Delay between characters (for effect)
            
        Returns:
            Complete response text
        """
        import time
        
        full_text = text_generator()
        displayed = ""
        
        with Live(console=self.console, refresh_per_second=30) as live:
            for char in full_text:
                displayed += char
                display = Text(displayed)
                display.append("▌", style=COLORS["command"])
                live.update(display)
                time.sleep(delay)
        
        return full_text
    
    def run(self, agent: "HealthSimAgent") -> None:
        """
        Run the interactive session loop.
        
        Handles user input, commands, and agent responses.
        Uses streaming for real-time response display.
        """
        while True:
            try:
                # Get user input
                user_input = self.get_input().strip()
                
                if not user_input:
                    continue
                
                self._message_count += 1
                
                # Handle commands
                if user_input.startswith("/"):
                    if self._handle_command(user_input, agent):
                        break
                    continue
                
                # Process message through agent with streaming
                self.console.print()
                
                # Collect response text
                response_text = []
                
                def on_text(chunk: str) -> None:
                    """Handle streamed text chunks."""
                    self.console.print(chunk, end="")
                    response_text.append(chunk)
                
                def on_tool_start(name: str, args: dict) -> None:
                    """Show tool execution indicator."""
                    self.show_tool_start(name)
                
                def on_tool_end(name: str, result: dict) -> None:
                    """Show tool completion."""
                    if result.get("error"):
                        self.show_result_error(f"{name}: {result['error']}")
                    else:
                        self.show_result_success(f"{name} completed")
                
                try:
                    # Try streaming first
                    response = agent.process_message_streaming(
                        user_input,
                        on_text=on_text,
                        on_tool_start=on_tool_start,
                        on_tool_end=on_tool_end,
                    )
                except AttributeError:
                    # Fall back to non-streaming
                    live = self.show_thinking()
                    try:
                        response = agent.process_message(user_input)
                    finally:
                        self.stop_thinking()
                    self.show_response(response)
                else:
                    # Finish streaming output
                    self.console.print()
                
                # Show status bar periodically
                if self._message_count % 5 == 0:
                    self.show_status_bar()
                
            except KeyboardInterrupt:
                self.console.print(f"\n[{COLORS['muted']}]Use /quit to exit[/]")
            except EOFError:
                break
    
    def _handle_command(self, command_str: str, agent: "HealthSimAgent") -> bool:
        """Handle slash commands.
        
        Returns:
            True if should exit, False otherwise
        """
        parts = command_str[1:].split()
        command = parts[0].lower() if parts else ""
        args = parts[1:] if len(parts) > 1 else []
        
        if command in ("quit", "exit", "q"):
            return True
        elif command == "help":
            self.show_help()
        elif command == "status":
            self.show_status(agent)
        elif command == "clear":
            agent.clear_session()
            self.console.print(f"[{COLORS['muted']}]Session cleared.[/]")
        elif command == "sql" and args:
            # Direct SQL execution
            sql = " ".join(args)
            self._execute_sql(sql, agent)
        elif command == "save" and args:
            # Save session
            path = args[0]
            agent.save_session(path)
            self.console.print(f"[{COLORS['success']}]Session saved to {path}[/]")
        elif command == "load" and args:
            # Load session
            path = args[0]
            if agent.load_session(path):
                self.console.print(f"[{COLORS['success']}]Session loaded from {path}[/]")
            else:
                self.console.print(f"[{COLORS['error']}]Failed to load session from {path}[/]")
        elif command == "new":
            # Start new session
            agent.clear_session()
            self.console.print(f"[{COLORS['muted']}]Started new session.[/]")
        else:
            self.console.print(f"[{COLORS['warning']}]Unknown command: {command}[/]")
            self.console.print(f"[{COLORS['muted']}]Type /help for available commands[/]")
        
        return False
    
    def _execute_sql(self, sql: str, agent: "HealthSimAgent") -> None:
        """Execute direct SQL command."""
        try:
            from rich.table import Table
            from healthsim_agent.tools.query_tools import query
            
            # Execute through query tool
            result = query(sql=sql, limit=100)
            
            if result.success and result.data:
                rows = result.data.get("rows", [])
                columns = result.data.get("columns", [])
                
                if rows and columns:
                    table = Table(show_header=True, header_style="bold cyan")
                    for col in columns:
                        table.add_column(col)
                    
                    for row in rows[:50]:  # Limit display
                        table.add_row(*[str(v) if v is not None else "" for v in row])
                    
                    self.console.print(table)
                    self.console.print(f"[{COLORS['muted']}]{len(rows)} rows returned[/]")
                else:
                    self.console.print(f"[{COLORS['muted']}]Query executed, no rows returned[/]")
            else:
                self.show_error(result.error or "Query failed")
                
        except Exception as e:
            self.show_error(f"SQL execution failed: {e}")


class ToolCallbackHandler:
    """
    Handler for tool execution callbacks.
    
    Integrates with the agent to show tool indicators,
    progress, and results in the UI.
    """
    
    def __init__(self, ui: TerminalUI):
        self.ui = ui
        self._current_tool: Optional[str] = None
    
    def on_tool_start(self, tool_name: str, args: dict) -> None:
        """Called when a tool starts executing."""
        self._current_tool = tool_name
        self.ui.show_tool_start(tool_name)
        self.ui._spinner.start(f"Executing {tool_name}...")
    
    def on_tool_end(self, tool_name: str, result: dict) -> None:
        """Called when a tool finishes executing."""
        self.ui.stop_thinking()
        
        # Determine success/failure
        success = result.get("success", True)
        error = result.get("error")
        
        if error:
            self.ui.show_result_error(f"{tool_name} failed: {error}")
        else:
            # Generate appropriate headline
            headline = self._generate_headline(tool_name, result)
            self.ui.show_result_success(headline)
            
            # Show data if present
            self._show_result_data(tool_name, result)
            
            # Show suggestions
            self.ui.show_suggestions_for_tool(tool_name, result)
        
        self._current_tool = None
    
    def on_tool_error(self, tool_name: str, error: Exception) -> None:
        """Called when a tool raises an exception."""
        self.ui.stop_thinking()
        self.ui.show_error(
            f"{tool_name} failed",
            str(error),
            ["Check your input parameters", "Try a simpler query"],
        )
        self._current_tool = None
    
    def _generate_headline(self, tool_name: str, result: dict) -> str:
        """Generate appropriate headline for tool result."""
        if tool_name == "add_entities":
            count = result.get("entities_added_this_batch", 0)
            entity_type = list(result.get("entity_counts", {}).keys())
            type_str = entity_type[0] if entity_type else "entities"
            return f"Added {count} {type_str}"
        
        elif tool_name == "save_cohort":
            name = result.get("cohort_name", "cohort")
            return f"Saved cohort '{name}'"
        
        elif tool_name == "load_cohort":
            name = result.get("cohort_name", "cohort")
            return f"Loaded cohort '{name}'"
        
        elif tool_name == "search_providers":
            count = result.get("result_count", 0)
            return f"Found {count} providers"
        
        elif tool_name == "query":
            count = result.get("row_count", 0)
            return f"Query returned {count} rows"
        
        elif tool_name == "query_reference":
            count = result.get("row_count", 0)
            return f"Found {count} reference records"
        
        elif tool_name == "list_cohorts":
            count = len(result.get("cohorts", []))
            return f"Found {count} cohorts"
        
        elif tool_name == "delete_cohort":
            name = result.get("cohort_name", "cohort")
            return f"Deleted cohort '{name}'"
        
        else:
            return f"{tool_name} completed"
    
    def _show_result_data(self, tool_name: str, result: dict) -> None:
        """Show appropriate data display for tool result."""
        if tool_name == "search_providers":
            self.ui.show_provider_results(result)
        
        elif tool_name in ("get_summary", "load_cohort"):
            if "cohort_totals" in result:
                self.ui.show_cohort_summary(result)
        
        elif tool_name == "query" and result.get("rows"):
            self.ui.show_data_table(result["rows"], "Query Results")
        
        elif tool_name == "list_cohorts" and result.get("cohorts"):
            self.ui.show_data_table(result["cohorts"], "Cohorts")
