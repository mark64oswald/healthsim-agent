"""
HealthSim Agent - UI Components

Enhanced Rich components for the terminal UI.
Based on UX specification.
"""

from typing import Any, Dict, List, Optional, TYPE_CHECKING

from rich.console import Console, RenderableType, Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskID
from rich.syntax import Syntax
from rich.tree import Tree
from rich.rule import Rule
from rich.live import Live
from rich.spinner import Spinner

from .theme import (
    COLORS, ICONS, HEALTHSIM_THEME, BANNER_ART,
    SPINNER_FRAMES, get_status_style, get_icon,
)

if TYPE_CHECKING:
    from healthsim_agent.state.session import SessionState


class WelcomePanel:
    """
    Welcome screen with ASCII art banner and quick start info.
    
    Displayed on startup. Sets context and offers quick-start options.
    """
    
    def __init__(self, console: Console | None = None):
        self.console = console or Console(theme=HEALTHSIM_THEME)
    
    def render(
        self,
        version: str = "1.0.0",
        db_path: str = "~/.healthsim/healthsim.duckdb",
        provider_count: str = "8.9M",
        connected: bool = True,
    ) -> Panel:
        """Render the welcome panel."""
        content = Text()
        
        # ASCII art banner
        content.append(BANNER_ART, style=COLORS["command"])
        content.append("\n")
        
        # Subtitle
        content.append(f"   Healthcare Simulation Agent v{version}\n", style=COLORS["text"])
        content.append("   Powered by Claude • DuckDB Backend\n", style=COLORS["muted"])
        content.append("\n")
        
        # Database info
        content.append(f"   Database: ", style=COLORS["muted"])
        content.append(f"{db_path}\n", style=COLORS["text"])
        
        content.append(f"   Reference Data: ", style=COLORS["muted"])
        content.append(f"{provider_count} providers", style=COLORS["cyan"])
        content.append(" │ ", style=COLORS["muted"])
        content.append("100% US geography\n", style=COLORS["cyan"])
        
        # Connection status
        status_icon = ICONS["connected"] if connected else ICONS["disconnected"]
        status_style = COLORS["success"] if connected else COLORS["error"]
        status_text = "Connected" if connected else "Not connected"
        content.append(f"   Status: ", style=COLORS["muted"])
        content.append(f"{status_icon} {status_text}", style=status_style)
        
        return Panel(
            content,
            border_style=COLORS["border"],
            padding=(0, 1),
        )
    
    def render_quick_start(self) -> Text:
        """Render quick start suggestions."""
        text = Text()
        text.append("\n  Quick Start:\n", style=COLORS["muted"])
        
        examples = [
            "Generate 100 members in Texas",
            "Create a diabetic patient with complications",
            "Show me providers in ZIP 92101",
        ]
        
        for example in examples:
            text.append(f"    {ICONS['bullet']} ", style=COLORS["muted"])
            text.append(f'"{example}"\n', style=COLORS["command"])
        
        text.append("\n  Type ", style=COLORS["muted"])
        text.append("/help", style=COLORS["command"])
        text.append(" for commands or just describe what you need.\n", style=COLORS["muted"])
        
        return text


class ToolIndicator:
    """
    Tool invocation indicator.
    
    Shows "→ tool_name" when a tool is being executed.
    """
    
    def __init__(self, console: Console | None = None):
        self.console = console or Console(theme=HEALTHSIM_THEME)
    
    def render(self, tool_name: str) -> Text:
        """Render tool indicator."""
        text = Text()
        text.append(ICONS["arrow"], style=COLORS["tool"])
        text.append(f" {tool_name}", style=COLORS["tool"])
        return text
    
    def show(self, tool_name: str) -> None:
        """Print tool indicator to console."""
        self.console.print(self.render(tool_name))


class ResultHeadline:
    """
    Result headline with status icon.
    
    Shows "✓ Success message" or "✗ Error message" or "⚠ Warning"
    """
    
    def __init__(self, console: Console | None = None):
        self.console = console or Console(theme=HEALTHSIM_THEME)
    
    def render(
        self,
        message: str,
        success: bool = True,
        warning: bool = False,
    ) -> Text:
        """Render result headline."""
        text = Text()
        
        if warning:
            text.append(ICONS["warning"], style=get_status_style("warning"))
        elif success:
            text.append(ICONS["success"], style=get_status_style("success"))
        else:
            text.append(ICONS["error"], style=get_status_style("error"))
        
        text.append(f" {message}", style=COLORS["text"])
        return text
    
    def success(self, message: str) -> None:
        """Print success headline."""
        self.console.print(self.render(message, success=True))
    
    def error(self, message: str) -> None:
        """Print error headline."""
        self.console.print(self.render(message, success=False))
    
    def warning(self, message: str) -> None:
        """Print warning headline."""
        self.console.print(self.render(message, warning=True))


class SuggestionBox:
    """
    Contextual suggestions display.
    
    Shows next actions the user might want to take.
    """
    
    def __init__(self, console: Console | None = None):
        self.console = console or Console(theme=HEALTHSIM_THEME)
    
    def render(self, suggestions: List[str]) -> Text:
        """Render suggestion box."""
        if not suggestions:
            return Text()
        
        text = Text()
        text.append("\n  Suggested:\n", style=COLORS["muted"])
        
        for suggestion in suggestions[:3]:
            text.append(f"    {ICONS['arrow']} ", style=COLORS["muted"])
            text.append(f'"{suggestion}"\n', style=COLORS["command"])
        
        return text
    
    def show(self, suggestions: List[str]) -> None:
        """Print suggestions to console."""
        if suggestions:
            self.console.print(self.render(suggestions))


class StatusBar:
    """
    Session status bar.
    
    Shows current cohort context and session info.
    Displayed at bottom of screen.
    """
    
    def __init__(self, console: Console | None = None):
        self.console = console or Console(theme=HEALTHSIM_THEME)
    
    def render(
        self,
        cohort_name: Optional[str] = None,
        entity_count: int = 0,
        message_count: int = 0,
    ) -> Text:
        """Render status bar."""
        text = Text()
        
        # Separator line
        # text.append("─" * 70 + "\n", style=COLORS["border"])
        
        # Cohort context
        if cohort_name:
            text.append(f" Cohort: ", style=COLORS["muted"])
            text.append(f"{cohort_name}", style=COLORS["text"])
            text.append(" │ ", style=COLORS["border"])
            text.append(f"{entity_count} entities", style=COLORS["cyan"])
            text.append(" │ ", style=COLORS["border"])
        
        # Session info
        text.append(f"Session: ", style=COLORS["muted"])
        text.append(f"{message_count} messages", style=COLORS["text"])
        text.append(" │ ", style=COLORS["border"])
        text.append("/help", style=COLORS["command"])
        
        return text
    
    def show(
        self,
        cohort_name: Optional[str] = None,
        entity_count: int = 0,
        message_count: int = 0,
    ) -> None:
        """Print status bar to console."""
        self.console.print(Rule(style=COLORS["border"]))
        self.console.print(self.render(cohort_name, entity_count, message_count))


class ThinkingSpinner:
    """
    Animated thinking indicator.
    
    Shows "⠋ Thinking..." with spinning animation.
    """
    
    def __init__(self, console: Console | None = None):
        self.console = console or Console(theme=HEALTHSIM_THEME)
        self._live: Optional[Live] = None
    
    def start(self, message: str = "Thinking...") -> Live:
        """Start the spinner."""
        spinner = Spinner("dots", text=message, style=COLORS["spinner"])
        self._live = Live(spinner, console=self.console, refresh_per_second=10)
        self._live.start()
        return self._live
    
    def update(self, message: str) -> None:
        """Update spinner message."""
        if self._live:
            spinner = Spinner("dots", text=message, style=COLORS["spinner"])
            self._live.update(spinner)
    
    def stop(self) -> None:
        """Stop the spinner."""
        if self._live:
            self._live.stop()
            self._live = None


class ProgressDisplay:
    """
    Progress display for long-running operations.
    
    Shows progress bar with percentage for batch operations.
    """
    
    def __init__(self, console: Console | None = None):
        self.console = console or Console(theme=HEALTHSIM_THEME)
        self._progress: Optional[Progress] = None
        self._task_id: Optional[TaskID] = None
    
    def create(self, description: str = "Processing", total: int = 100) -> Progress:
        """Create a new progress display."""
        self._progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(complete_style=COLORS["success"]),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=self.console,
        )
        return self._progress
    
    def start(self, description: str = "Processing", total: int = 100) -> TaskID:
        """Start progress tracking."""
        if not self._progress:
            self.create(description, total)
        self._progress.start()
        self._task_id = self._progress.add_task(description, total=total)
        return self._task_id
    
    def update(self, advance: int = 1, description: Optional[str] = None) -> None:
        """Update progress."""
        if self._progress and self._task_id is not None:
            kwargs = {"advance": advance}
            if description:
                kwargs["description"] = description
            self._progress.update(self._task_id, **kwargs)
    
    def stop(self) -> None:
        """Stop the progress display."""
        if self._progress:
            self._progress.stop()
            self._progress = None
            self._task_id = None


class DataPreview:
    """
    Data preview component for generated healthcare data.
    
    Supports:
    - JSON syntax highlighting
    - Table view for records
    - Tree view for hierarchical data
    """
    
    def __init__(self, console: Console | None = None):
        self.console = console or Console(theme=HEALTHSIM_THEME)
    
    def render_json(self, data: dict | list, title: str = "Generated Data") -> Panel:
        """Render JSON data with syntax highlighting."""
        import json
        json_str = json.dumps(data, indent=2, default=str)
        syntax = Syntax(json_str, "json", theme="monokai", line_numbers=False)
        
        return Panel(
            syntax,
            title=f"[bold]{title}[/bold]",
            border_style=COLORS["border"],
        )
    
    def render_table(
        self,
        data: list[dict],
        title: str = "Records",
        max_rows: int = 10,
    ) -> Panel:
        """Render data as a table."""
        if not data:
            return Panel(
                Text("No data", style=COLORS["muted"]),
                title=title,
                border_style=COLORS["border"],
            )
        
        # Get columns from first record
        columns = list(data[0].keys())
        
        table = Table(
            show_header=True,
            header_style=f"bold {COLORS['text']}",
            border_style=COLORS["border"],
        )
        for col in columns[:6]:  # Limit columns for display
            table.add_column(col)
        
        # Add rows
        for record in data[:max_rows]:
            values = [str(record.get(col, ""))[:30] for col in columns[:6]]
            table.add_row(*values)
        
        if len(data) > max_rows:
            table.add_row(*["..." for _ in columns[:6]])
        
        return Panel(
            table,
            title=f"[bold]{title}[/bold] ({len(data)} records)",
            border_style=COLORS["border"],
        )
    
    def render_tree(self, data: dict, title: str = "Structure") -> Panel:
        """Render hierarchical data as a tree."""
        tree = Tree(f"[bold]{title}[/bold]")
        self._build_tree(tree, data)
        
        return Panel(
            tree,
            border_style=COLORS["border"],
        )
    
    def _build_tree(self, tree: Tree, data: Any, max_depth: int = 3, depth: int = 0) -> None:
        """Recursively build tree structure."""
        if depth >= max_depth:
            tree.add(f"[{COLORS['muted']}]...[/]")
            return
        
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    branch = tree.add(f"[bold]{key}[/bold]")
                    self._build_tree(branch, value, max_depth, depth + 1)
                else:
                    tree.add(f"{key}: [{COLORS['muted']}]{value}[/]")
        elif isinstance(data, list):
            tree.add(f"[{COLORS['muted']}]({len(data)} items)[/]")
            for i, item in enumerate(data[:3]):
                branch = tree.add(f"[{i}]")
                self._build_tree(branch, item, max_depth, depth + 1)
            if len(data) > 3:
                tree.add(f"[{COLORS['muted']}]...[/]")


class HelpDisplay:
    """
    Categorized help display.
    
    Organized by category with examples.
    """
    
    def __init__(self, console: Console | None = None):
        self.console = console or Console(theme=HEALTHSIM_THEME)
    
    def render(self) -> Panel:
        """Render help panel."""
        content = Text()
        
        # Generation
        content.append("\n📦 Generation\n", style=f"bold {COLORS['text']}")
        content.append('  "Generate 1000 members in California"\n', style=COLORS["command"])
        content.append('  "Create a patient with CHF and diabetes"\n', style=COLORS["command"])
        content.append('  "Add 12 months of claims history"\n', style=COLORS["command"])
        
        # Analytics
        content.append("\n📊 Analytics\n", style=f"bold {COLORS['text']}")
        content.append('  "Profile this population"\n', style=COLORS["command"])
        content.append('  "Stratify by risk level"\n', style=COLORS["command"])
        content.append('  "What are the top cost drivers?"\n', style=COLORS["command"])
        
        # Data
        content.append("\n🗄️  Data\n", style=f"bold {COLORS['text']}")
        content.append('  "Show tables" • "Describe patients"\n', style=COLORS["command"])
        content.append('  /sql SELECT ... — Run custom SQL\n', style=COLORS["command"])
        content.append('  "Export to FHIR" • "Export to CSV"\n', style=COLORS["command"])
        
        # System commands
        content.append("\n⚙️  System\n", style=f"bold {COLORS['text']}")
        content.append("  /help — This message\n", style=COLORS["muted"])
        content.append("  /clear — Clear screen\n", style=COLORS["muted"])
        content.append("  /status — Show session status\n", style=COLORS["muted"])
        content.append("  /exit or quit — Exit application\n", style=COLORS["muted"])
        
        return Panel(
            content,
            title="[bold]HealthSim Commands[/bold]",
            border_style=COLORS["border"],
            padding=(0, 1),
        )
    
    def show(self) -> None:
        """Print help to console."""
        self.console.print(self.render())
