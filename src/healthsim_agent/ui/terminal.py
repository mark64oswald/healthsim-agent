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
                    """Show tool completion and display results for key tools."""
                    if result.get("error"):
                        self.show_result_error(f"{name}: {result['error']}")
                    else:
                        # Generate informative headline
                        data = result.get("data")
                        if name == "list_cohorts" and isinstance(data, list):
                            self.show_result_success(f"Found {len(data)} cohorts")
                            # Display cohort list directly
                            if data:
                                from rich.table import Table
                                table = Table(show_header=True, header_style="bold cyan")
                                table.add_column("Name")
                                table.add_column("Entities", justify="right")
                                table.add_column("Updated")
                                for c in data[:20]:  # Limit display
                                    table.add_row(
                                        c.get("name", "?"),
                                        str(c.get("entity_count", 0)),
                                        str(c.get("updated_at", ""))[:10]
                                    )
                                self.console.print(table)
                        elif name == "load_cohort" and isinstance(data, dict):
                            cohort_name = data.get("name", "?")
                            entity_counts = data.get("entity_counts", {})
                            total = sum(entity_counts.values()) if entity_counts else 0
                            self.show_result_success(f"Loaded '{cohort_name}' ({total} entities)")
                            # Display entity breakdown
                            if entity_counts:
                                from rich.table import Table
                                table = Table(show_header=True, header_style="bold cyan", title="Entity Breakdown")
                                table.add_column("Type")
                                table.add_column("Count", justify="right")
                                for etype, count in sorted(entity_counts.items()):
                                    table.add_row(etype, str(count))
                                table.add_row("[bold]Total[/bold]", f"[bold]{total}[/bold]")
                                self.console.print(table)
                            # Show description if present
                            if data.get("description"):
                                self.console.print(f"[dim]Description:[/dim] {data['description']}")
                            # Show tags if present  
                            if data.get("tags"):
                                self.console.print(f"[dim]Tags:[/dim] {', '.join(data['tags'])}")
                        elif name == "save_cohort" and isinstance(data, dict):
                            cohort_name = data.get("cohort_name", data.get("name", "?"))
                            self.show_result_success(f"Saved cohort '{cohort_name}'")
                        elif name == "add_entities" and isinstance(data, dict):
                            added = data.get("entities_added_this_batch", 0)
                            total = data.get("total_entities", added)
                            self.show_result_success(f"Added {added} entities (total: {total})")
                        elif name == "get_summary" and isinstance(data, dict):
                            self.show_result_success(f"Cohort: {data.get('name', '?')}")
                            self.show_cohort_summary(data)
                        elif name == "search_providers":
                            count = result.get("result_count", len(data) if data else 0)
                            self.show_result_success(f"Found {count} providers")
                        elif name == "query":
                            rows = data.get("rows", []) if isinstance(data, dict) else []
                            self.show_result_success(f"Query returned {len(rows)} rows")
                        elif name == "transform_to_hl7v2" and isinstance(data, dict):
                            count = data.get("count", 0)
                            msg_type = data.get("message_type", "HL7v2")
                            self.show_result_success(f"Generated {count} {msg_type} messages")
                            # Display the actual messages
                            messages = data.get("messages", [])
                            if messages:
                                from rich.panel import Panel
                                for i, msg in enumerate(messages[:5], 1):  # Limit to 5
                                    # HL7v2 uses \r as segment delimiter - convert to newlines for display
                                    formatted_msg = msg.replace('\r', '\n')
                                    panel = Panel(
                                        formatted_msg[:2000] + ("..." if len(formatted_msg) > 2000 else ""),
                                        title=f"[bold cyan]Message {i}[/bold cyan]",
                                        border_style="dim"
                                    )
                                    self.console.print(panel)
                                if len(messages) > 5:
                                    self.console.print(f"[dim]... and {len(messages) - 5} more messages[/dim]")
                        elif name == "transform_to_fhir" and isinstance(data, dict):
                            # Data IS the bundle (not nested under "bundle" key)
                            entries = data.get("entry", [])
                            count = len(entries)
                            self.show_result_success(f"Generated FHIR Bundle with {count} resources")
                            # Show summary of resource types
                            if entries:
                                from collections import Counter
                                types = Counter(e.get("resource", {}).get("resourceType", "?") for e in entries)
                                self.console.print(f"[dim]Resources: {dict(types)}[/dim]")
                                # Show JSON preview of first resource
                                import json
                                from rich.panel import Panel
                                from rich.syntax import Syntax
                                first_resource = entries[0].get("resource", {})
                                preview_json = json.dumps(first_resource, indent=2)[:1500]
                                if len(json.dumps(first_resource, indent=2)) > 1500:
                                    preview_json += "\n..."
                                syntax = Syntax(preview_json, "json", theme="monokai", line_numbers=False)
                                panel = Panel(syntax, title=f"[bold cyan]Sample: {first_resource.get('resourceType', 'Resource')}[/bold cyan]", border_style="dim")
                                self.console.print(panel)
                        elif name == "transform_to_ccda" and isinstance(data, dict):
                            doc_type = data.get("document_type", "C-CDA")
                            self.show_result_success(f"Generated {doc_type} document")
                            # Show document snippet
                            xml_content = data.get("document", "")
                            if xml_content:
                                from rich.panel import Panel
                                preview = xml_content[:1500] + ("..." if len(xml_content) > 1500 else "")
                                panel = Panel(preview, title="[bold cyan]C-CDA Document (preview)[/bold cyan]", border_style="dim")
                                self.console.print(panel)
                        elif name == "transform_to_x12" and isinstance(data, dict):
                            tx_type = data.get("type", "X12")
                            claim_count = data.get("claim_count", 0)
                            self.show_result_success(f"Generated X12 {tx_type} ({claim_count} claims)")
                            # Show EDI content
                            edi = data.get("transaction", "")
                            if edi:
                                from rich.panel import Panel
                                preview = edi[:2000] + ("..." if len(edi) > 2000 else "")
                                panel = Panel(preview, title=f"[bold cyan]X12 {tx_type}[/bold cyan]", border_style="dim")
                                self.console.print(panel)
                        elif name == "transform_to_ncpdp" and isinstance(data, dict):
                            count = data.get("claim_count", 0)
                            self.show_result_success(f"Generated NCPDP D.0 ({count} claims)")
                            # Show transaction content
                            tx = data.get("transaction", "")
                            if tx:
                                from rich.panel import Panel
                                preview = tx[:2000] + ("..." if len(tx) > 2000 else "")
                                panel = Panel(preview, title="[bold cyan]NCPDP D.0 Transaction[/bold cyan]", border_style="dim")
                                self.console.print(panel)
                        elif name == "transform_to_mimic" and isinstance(data, dict):
                            tables = [k for k in data.keys() if k.isupper()]
                            self.show_result_success(f"Generated MIMIC-III tables: {', '.join(tables)}")
                            # Show row counts per table
                            from rich.table import Table
                            table = Table(show_header=True, header_style="bold cyan", title="MIMIC-III Tables")
                            table.add_column("Table")
                            table.add_column("Rows", justify="right")
                            for tbl_name in tables:
                                rows = data.get(tbl_name, [])
                                table.add_row(tbl_name, str(len(rows) if isinstance(rows, list) else 1))
                            self.console.print(table)
                        elif name == "delete_cohort" and isinstance(data, dict):
                            cohort_name = data.get("cohort_name", data.get("name", "cohort"))
                            self.show_result_success(f"Deleted cohort '{cohort_name}'")
                        elif name == "list_tables" and isinstance(data, dict):
                            total = data.get("total", 0)
                            self.show_result_success(f"Found {total} tables")
                            from rich.table import Table
                            table = Table(show_header=True, header_style="bold cyan")
                            table.add_column("Category")
                            table.add_column("Tables")
                            for cat in ["reference_tables", "entity_tables", "system_tables"]:
                                tables = data.get(cat, [])
                                if tables:
                                    table.add_row(cat.replace("_", " ").title(), ", ".join(tables[:10]) + ("..." if len(tables) > 10 else ""))
                            self.console.print(table)
                        elif name == "list_skills" and isinstance(data, dict):
                            total_skills = sum(len(v) for v in data.values())
                            self.show_result_success(f"Found {total_skills} skills across {len(data)} products")
                            from rich.table import Table
                            table = Table(show_header=True, header_style="bold cyan")
                            table.add_column("Product")
                            table.add_column("Skills", justify="right")
                            for product, skills in data.items():
                                table.add_row(product, str(len(skills)))
                            self.console.print(table)
                        elif name == "describe_skill" and isinstance(data, dict):
                            skill_name = data.get("name", "?")
                            self.show_result_success(f"Skill: {skill_name}")
                            if data.get("description"):
                                self.console.print(f"[dim]{data['description'][:500]}[/dim]")
                        elif name == "list_output_formats" and isinstance(data, dict):
                            self.show_result_success(f"Found {len(data)} output formats")
                            from rich.table import Table
                            table = Table(show_header=True, header_style="bold cyan")
                            table.add_column("Format")
                            table.add_column("Tool")
                            table.add_column("Products")
                            for fmt_id, fmt in data.items():
                                table.add_row(fmt.get("name", fmt_id), fmt.get("tool", "?"), ", ".join(fmt.get("products", [])))
                            self.console.print(table)
                        elif name == "list_profiles" and isinstance(data, dict):
                            profiles = data.get("profiles", [])
                            self.show_result_success(f"Found {len(profiles)} profiles")
                            if profiles:
                                from rich.table import Table
                                table = Table(show_header=True, header_style="bold cyan")
                                table.add_column("Name")
                                table.add_column("Description")
                                for p in profiles[:20]:
                                    table.add_row(p.get("name", "?"), (p.get("description", "") or "")[:50])
                                self.console.print(table)
                        elif name == "list_journeys" and isinstance(data, dict):
                            journeys = data.get("journeys", [])
                            self.show_result_success(f"Found {len(journeys)} journeys")
                            if journeys:
                                from rich.table import Table
                                table = Table(show_header=True, header_style="bold cyan")
                                table.add_column("Name")
                                table.add_column("Steps")
                                for j in journeys[:20]:
                                    table.add_row(j.get("name", "?"), str(len(j.get("steps", []))))
                                self.console.print(table)
                        elif name in ("save_profile", "load_profile", "delete_profile") and isinstance(data, dict):
                            profile_name = data.get("profile_name", data.get("name", "profile"))
                            action = name.replace("_profile", "").replace("_", " ").title() + "d"
                            self.show_result_success(f"{action} profile '{profile_name}'")
                        elif name in ("save_journey", "load_journey", "delete_journey") and isinstance(data, dict):
                            journey_name = data.get("journey_name", data.get("name", "journey"))
                            action = name.replace("_journey", "").replace("_", " ").title() + "d"
                            self.show_result_success(f"{action} journey '{journey_name}'")
                        elif name in ("execute_profile", "execute_journey") and isinstance(data, dict):
                            entity_name = name.replace("execute_", "")
                            self.show_result_success(f"Executed {entity_name}")
                            # Show execution results
                            if data.get("entities_generated"):
                                self.console.print(f"[dim]Entities generated: {data['entities_generated']}[/dim]")
                        elif name == "export_json" and isinstance(data, dict):
                            size = data.get("size_bytes", 0)
                            self.show_result_success(f"Exported JSON ({size:,} bytes)")
                            # Show preview
                            json_content = data.get("json", "")
                            if json_content:
                                from rich.panel import Panel
                                from rich.syntax import Syntax
                                preview = json_content[:2000] + ("..." if len(json_content) > 2000 else "")
                                syntax = Syntax(preview, "json", theme="monokai", line_numbers=False)
                                panel = Panel(syntax, title="[bold cyan]JSON Export[/bold cyan]", border_style="dim")
                                self.console.print(panel)
                        elif name == "export_ndjson" and isinstance(data, dict):
                            records = data.get("records", 0)
                            self.show_result_success(f"Exported NDJSON ({records} records)")
                            # Show preview
                            ndjson_content = data.get("ndjson", "")
                            if ndjson_content:
                                from rich.panel import Panel
                                lines = ndjson_content.split('\n')[:5]
                                preview = '\n'.join(lines) + ("\n..." if len(ndjson_content.split('\n')) > 5 else "")
                                panel = Panel(preview, title="[bold cyan]NDJSON Export (first 5 records)[/bold cyan]", border_style="dim")
                                self.console.print(panel)
                        elif name == "validate_data" and isinstance(data, dict):
                            valid = data.get("valid", False)
                            errors = data.get("errors", [])
                            warnings = data.get("warnings", [])
                            if valid:
                                self.show_result_success(f"Validation passed ({len(warnings)} warnings)")
                            else:
                                self.show_result_warning(f"Validation failed: {len(errors)} errors, {len(warnings)} warnings")
                            if errors:
                                for err in errors[:5]:
                                    self.console.print(f"  [red]✗[/red] {err}")
                            if warnings:
                                for warn in warnings[:5]:
                                    self.console.print(f"  [yellow]⚠[/yellow] {warn}")
                        elif name == "fix_validation_issues" and isinstance(data, dict):
                            fixed = data.get("fixed_count", 0)
                            self.show_result_success(f"Fixed {fixed} validation issues")
                        elif name == "check_formulary" and isinstance(data, dict):
                            covered = data.get("covered", False)
                            tier = data.get("tier", "?")
                            if covered:
                                self.show_result_success(f"Drug covered - Tier {tier}")
                            else:
                                self.show_result_warning("Drug not covered")
                            if data.get("alternatives"):
                                self.console.print(f"[dim]Alternatives: {', '.join(data['alternatives'][:3])}[/dim]")
                        elif name == "query_reference" and isinstance(data, dict):
                            # PopulationSim reference data query
                            table_name = data.get("table", "reference")
                            row_count = data.get("row_count", 0)
                            self.show_result_success(f"Found {row_count} rows from {table_name}")
                            # Show data table preview
                            rows = data.get("rows", [])
                            columns = data.get("columns", [])
                            if rows and columns:
                                from rich.table import Table
                                table = Table(show_header=True, header_style="bold cyan", title=f"[dim]{table_name}[/dim]")
                                # Limit columns for display
                                display_cols = columns[:8]
                                for col in display_cols:
                                    table.add_column(col)
                                if len(columns) > 8:
                                    table.add_column("...")
                                for row in rows[:10]:  # Limit rows
                                    row_values = [str(row.get(c, ""))[:30] for c in display_cols]
                                    if len(columns) > 8:
                                        row_values.append("...")
                                    table.add_row(*row_values)
                                self.console.print(table)
                                if row_count > 10:
                                    self.console.print(f"[dim]... and {row_count - 10} more rows[/dim]")
                        elif name.startswith("generate_") and isinstance(data, dict):
                            # Generation tools return entities under their type key (e.g., "patients", "members")
                            entity_type = name.replace("generate_", "")
                            # Look for entities under their type key
                            primary_key = entity_type  # e.g., "patients", "members", "subjects", "rx_members"
                            entities = data.get(primary_key, data.get("entities", []))
                            count = len(entities) if entities else data.get("count", 0)
                            self.show_result_success(f"Generated {count} {entity_type}")
                            # Show summary of what was generated
                            if data:
                                entity_summary = []
                                for key, value in data.items():
                                    if isinstance(value, list) and value:
                                        entity_summary.append(f"{len(value)} {key}")
                                if entity_summary:
                                    self.console.print(f"[dim]Contains: {', '.join(entity_summary)}[/dim]")
                            # Show preview of first entity
                            if entities:
                                import json
                                from rich.panel import Panel
                                from rich.syntax import Syntax
                                preview = json.dumps(entities[0], indent=2, default=str)[:1000]
                                if len(json.dumps(entities[0], indent=2, default=str)) > 1000:
                                    preview += "\n..."
                                syntax = Syntax(preview, "json", theme="monokai", line_numbers=False)
                                # Singularize entity type for label
                                singular = entity_type.rstrip('s') if entity_type.endswith('s') else entity_type
                                panel = Panel(syntax, title=f"[bold cyan]Sample {singular}[/bold cyan]", border_style="dim")
                                self.console.print(panel)
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
