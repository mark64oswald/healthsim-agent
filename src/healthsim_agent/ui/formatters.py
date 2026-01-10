"""
HealthSim Agent - UI Formatters

Convert tool results and data to Rich renderables.
"""

from typing import Any, Dict, List, Optional, Union

from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.syntax import Syntax
from rich.columns import Columns

from .theme import COLORS, ICONS, get_status_style


def format_tool_indicator(tool_name: str) -> Text:
    """Format tool invocation indicator.
    
    Returns: "→ tool_name" in muted style
    """
    text = Text()
    text.append(ICONS["arrow"], style=COLORS["tool"])
    text.append(f" {tool_name}", style=COLORS["tool"])
    return text


def format_result_headline(
    success: bool,
    message: str,
    warning: bool = False,
) -> Text:
    """Format result headline with appropriate icon.
    
    Returns: "✓ Message" or "✗ Message" or "⚠ Message"
    """
    text = Text()
    
    if warning:
        text.append(ICONS["warning"], style=get_status_style("warning"))
        text.append(f" {message}", style=COLORS["text"])
    elif success:
        text.append(ICONS["success"], style=get_status_style("success"))
        text.append(f" {message}", style=COLORS["text"])
    else:
        text.append(ICONS["error"], style=get_status_style("error"))
        text.append(f" {message}", style=COLORS["text"])
    
    return text


def format_data_panel(
    content: Union[str, Dict, List],
    title: str = "Data",
    border_style: str = "dim",
) -> Panel:
    """Format data as a bordered panel.
    
    Handles:
    - String content directly
    - Dict as key-value pairs
    - List as bullet points
    """
    if isinstance(content, str):
        body = Text(content)
    elif isinstance(content, dict):
        body = _format_dict_content(content)
    elif isinstance(content, list):
        body = _format_list_content(content)
    else:
        body = Text(str(content))
    
    return Panel(
        body,
        title=f"[bold]{title}[/bold]",
        border_style=border_style,
        padding=(0, 1),
    )


def _format_dict_content(data: Dict) -> Text:
    """Format dictionary as key-value text."""
    text = Text()
    for i, (key, value) in enumerate(data.items()):
        if i > 0:
            text.append("\n")
        text.append(f"{key}: ", style=COLORS["muted"])
        text.append(str(value), style=COLORS["text"])
    return text


def _format_list_content(data: List) -> Text:
    """Format list as bullet points."""
    text = Text()
    for i, item in enumerate(data):
        if i > 0:
            text.append("\n")
        text.append(f"{ICONS['bullet']} ", style=COLORS["muted"])
        text.append(str(item), style=COLORS["text"])
    return text


def format_data_table(
    records: List[Dict],
    title: str = "Records",
    max_rows: int = 10,
    max_cols: int = 6,
) -> Panel:
    """Format records as a data table with pagination hint.
    
    Args:
        records: List of dictionaries with consistent keys
        title: Table title
        max_rows: Maximum rows to display
        max_cols: Maximum columns to display
    """
    if not records:
        return Panel(
            Text("No data", style=COLORS["muted"]),
            title=title,
            border_style="dim",
        )
    
    # Get columns from first record
    all_columns = list(records[0].keys())
    columns = all_columns[:max_cols]
    
    table = Table(
        show_header=True,
        header_style=f"bold {COLORS['text']}",
        border_style=COLORS["border"],
        row_styles=[COLORS["text"], COLORS["muted"]],
    )
    
    # Add columns
    for col in columns:
        table.add_column(col)
    
    if len(all_columns) > max_cols:
        table.add_column("...", style=COLORS["muted"])
    
    # Add rows
    displayed_rows = records[:max_rows]
    for record in displayed_rows:
        values = [_truncate(str(record.get(col, "")), 25) for col in columns]
        if len(all_columns) > max_cols:
            values.append("...")
        table.add_row(*values)
    
    # Add pagination hint if needed
    total = len(records)
    if total > max_rows:
        table.add_row(
            *["..." for _ in range(len(columns) + (1 if len(all_columns) > max_cols else 0))]
        )
    
    # Create panel with count in title
    panel_title = f"{title} ({total} records)"
    if total > max_rows:
        panel_title += f" - showing {max_rows}"
    
    return Panel(
        table,
        title=f"[bold]{panel_title}[/bold]",
        border_style="dim",
        padding=(0, 0),
    )


def _truncate(s: str, max_len: int) -> str:
    """Truncate string with ellipsis."""
    if len(s) <= max_len:
        return s
    return s[:max_len - 3] + "..."


def format_suggestions(suggestions: List[str]) -> Text:
    """Format suggestion box.
    
    Returns:
        Suggested:
          → "Add 12 months of claims history"
          → "Stratify by complication risk"
    """
    if not suggestions:
        return Text()
    
    text = Text()
    text.append("\n")
    text.append("Suggested:", style=COLORS["muted"])
    
    for suggestion in suggestions[:3]:  # Max 3 suggestions
        text.append("\n  ")
        text.append(ICONS["arrow"], style=COLORS["muted"])
        text.append(" ", style=COLORS["muted"])
        text.append(f'"{suggestion}"', style=COLORS["command"])
    
    return text


def format_sql(sql: str, title: str = "SQL Query") -> Panel:
    """Format SQL query with syntax highlighting."""
    syntax = Syntax(
        sql.strip(),
        "sql",
        theme="monokai",
        line_numbers=False,
        word_wrap=True,
    )
    return Panel(
        syntax,
        title=f"[bold]{title}[/bold]",
        border_style="dim",
    )


def format_json(data: Union[Dict, List], title: str = "Data") -> Panel:
    """Format JSON data with syntax highlighting."""
    import json
    json_str = json.dumps(data, indent=2, default=str)
    syntax = Syntax(
        json_str,
        "json",
        theme="monokai",
        line_numbers=False,
        word_wrap=True,
    )
    return Panel(
        syntax,
        title=f"[bold]{title}[/bold]",
        border_style="dim",
    )


def format_error(
    message: str,
    details: Optional[str] = None,
    suggestions: Optional[List[str]] = None,
) -> Panel:
    """Format error display with actionable guidance.
    
    Returns a panel with:
    - Error icon and message
    - Optional details
    - Optional recovery suggestions
    """
    content = Text()
    content.append(ICONS["error"], style=get_status_style("error"))
    content.append(f" {message}\n", style=COLORS["text"])
    
    if details:
        content.append("\n")
        content.append(details, style=COLORS["muted"])
    
    if suggestions:
        content.append("\n\nTry:")
        for i, suggestion in enumerate(suggestions, 1):
            content.append(f"\n  {i}. ", style=COLORS["muted"])
            content.append(suggestion, style=COLORS["text"])
    
    return Panel(
        content,
        title="[bold]Error[/bold]",
        border_style=COLORS["error"],
        padding=(0, 1),
    )


def format_cohort_summary(summary: Dict) -> Panel:
    """Format cohort summary for display.
    
    Expected summary keys:
    - cohort_id, name, description
    - entity_counts: {type: count}
    - total_entities
    - samples (optional)
    """
    content = Text()
    
    # Name and description
    name = summary.get("name", "Unknown")
    desc = summary.get("description", "")
    
    content.append(f"Name: ", style=COLORS["muted"])
    content.append(f"{name}\n", style=COLORS["text"])
    
    if desc:
        content.append(f"Description: ", style=COLORS["muted"])
        content.append(f"{desc}\n", style=COLORS["text"])
    
    # Entity counts
    entity_counts = summary.get("entity_counts", {})
    if entity_counts:
        content.append("\n")
        content.append("Entities:\n", style=COLORS["muted"])
        for entity_type, count in entity_counts.items():
            content.append(f"  {ICONS['bullet']} ", style=COLORS["muted"])
            content.append(f"{entity_type}: ", style=COLORS["text"])
            content.append(f"{count}\n", style=COLORS["cyan"])
    
    total = summary.get("total_entities", sum(entity_counts.values()))
    content.append(f"\nTotal: ", style=COLORS["muted"])
    content.append(str(total), style=f"bold {COLORS['text']}")
    
    return Panel(
        content,
        title="[bold]Cohort Summary[/bold]",
        border_style="dim",
        padding=(0, 1),
    )


def format_provider_results(result: Dict) -> Panel:
    """Format provider search results."""
    providers = result.get("providers", [])
    count = result.get("result_count", len(providers))
    filters = result.get("filters_applied", {})
    
    # Build filter description
    filter_parts = []
    if filters.get("state"):
        filter_parts.append(f"State: {filters['state']}")
    if filters.get("city"):
        filter_parts.append(f"City: {filters['city']}")
    if filters.get("specialty"):
        filter_parts.append(f"Specialty: {filters['specialty']}")
    
    content = Text()
    content.append(f"Found {count} providers", style=COLORS["text"])
    if filter_parts:
        content.append(f" ({', '.join(filter_parts)})", style=COLORS["muted"])
    content.append("\n\n")
    
    # Show first few providers
    for i, provider in enumerate(providers[:5]):
        name = provider.get("name", "Unknown")
        npi = provider.get("npi", "")
        city = provider.get("practice_city", "")
        state = provider.get("practice_state", "")
        
        content.append(f"{ICONS['bullet']} ", style=COLORS["muted"])
        content.append(f"{name}", style=COLORS["text"])
        content.append(f" (NPI: {npi})", style=COLORS["cyan"])
        if city and state:
            content.append(f" - {city}, {state}", style=COLORS["muted"])
        content.append("\n")
    
    if count > 5:
        content.append(f"\n... and {count - 5} more", style=COLORS["muted"])
    
    return Panel(
        content,
        title="[bold]Provider Search Results[/bold]",
        border_style="dim",
        padding=(0, 1),
    )
