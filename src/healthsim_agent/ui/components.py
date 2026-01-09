"""
HealthSim Agent - UI Components

Reusable Rich components for data display and status.
"""
from typing import Any

from rich.console import Console, RenderableType
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.syntax import Syntax
from rich.tree import Tree


# Color palette
COLORS = {
    "primary": "#4A9BD9",
    "success": "#2E8B57",
    "warning": "#DAA520",
    "error": "#CD5C5C",
    "info": "#708090",
}


class StatusPanel:
    """
    Status panel showing current agent state.
    
    Displays:
    - Connection status
    - Active skill
    - Generation progress
    - Data statistics
    """
    
    def __init__(self, console: Console | None = None):
        self.console = console or Console()
    
    def render(
        self,
        connected: bool = False,
        active_skill: str | None = None,
        message_count: int = 0,
        data_count: int = 0,
    ) -> Panel:
        """Render the status panel."""
        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_column("Key", style="dim")
        table.add_column("Value")
        
        # Connection status with indicator
        status_style = COLORS['success'] if connected else COLORS['error']
        status_text = "● Connected" if connected else "○ Disconnected"
        table.add_row("Database", f"[{status_style}]{status_text}[/]")
        
        # Active skill
        skill_text = active_skill or "None"
        table.add_row("Skill", skill_text)
        
        # Counts
        table.add_row("Messages", str(message_count))
        table.add_row("Generated", str(data_count))
        
        return Panel(
            table,
            title="[bold]Status[/bold]",
            border_style=COLORS['info'],
            width=30,
        )


class DataPreview:
    """
    Data preview component for generated healthcare data.
    
    Supports:
    - JSON syntax highlighting
    - Table view for records
    - Tree view for hierarchical data
    """
    
    def __init__(self, console: Console | None = None):
        self.console = console or Console()
    
    def render_json(self, data: dict | list, title: str = "Generated Data") -> Panel:
        """Render JSON data with syntax highlighting."""
        import json
        json_str = json.dumps(data, indent=2)
        syntax = Syntax(json_str, "json", theme="monokai", line_numbers=True)
        
        return Panel(
            syntax,
            title=f"[bold]{title}[/bold]",
            border_style=COLORS['primary'],
        )
    
    def render_table(
        self,
        data: list[dict],
        title: str = "Records",
        max_rows: int = 10,
    ) -> Panel:
        """Render data as a table."""
        if not data:
            return Panel("[dim]No data[/dim]", title=title)
        
        # Get columns from first record
        columns = list(data[0].keys())
        
        table = Table(show_header=True, header_style="bold")
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
            border_style=COLORS['primary'],
        )
    
    def render_tree(self, data: dict, title: str = "Structure") -> Panel:
        """Render hierarchical data as a tree."""
        tree = Tree(f"[bold]{title}[/bold]")
        self._build_tree(tree, data)
        
        return Panel(
            tree,
            border_style=COLORS['info'],
        )
    
    def _build_tree(self, tree: Tree, data: Any, max_depth: int = 3, depth: int = 0) -> None:
        """Recursively build tree structure."""
        if depth >= max_depth:
            tree.add("[dim]...[/dim]")
            return
        
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    branch = tree.add(f"[bold]{key}[/bold]")
                    self._build_tree(branch, value, max_depth, depth + 1)
                else:
                    tree.add(f"{key}: [dim]{value}[/dim]")
        elif isinstance(data, list):
            tree.add(f"[dim]({len(data)} items)[/dim]")
            for i, item in enumerate(data[:3]):
                branch = tree.add(f"[{i}]")
                self._build_tree(branch, item, max_depth, depth + 1)
            if len(data) > 3:
                tree.add("[dim]...[/dim]")


class ProgressDisplay:
    """
    Progress display for long-running operations.
    
    Used for:
    - Batch data generation
    - Database queries
    - File exports
    """
    
    def __init__(self, console: Console | None = None):
        self.console = console or Console()
        self._progress: Progress | None = None
    
    def create(self, description: str = "Processing") -> Progress:
        """Create a new progress display."""
        self._progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=self.console,
        )
        return self._progress
    
    def start(self) -> None:
        """Start the progress display."""
        if self._progress:
            self._progress.start()
    
    def stop(self) -> None:
        """Stop the progress display."""
        if self._progress:
            self._progress.stop()
