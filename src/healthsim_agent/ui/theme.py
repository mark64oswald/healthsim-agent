"""
HealthSim Agent - GitHub Dark Theme

Color palette and styling constants for the terminal UI.
Based on UX specification Section 4.
"""

from rich.theme import Theme
from typing import Dict

# GitHub Dark color palette
COLORS: Dict[str, str] = {
    # Backgrounds
    "background": "#0d1117",
    "surface": "#161b22",
    "border": "#30363d",
    
    # Text
    "text": "#c9d1d9",
    "muted": "#8b949e",
    
    # Semantic colors
    "user": "#7ee787",       # Green for user prompt
    "command": "#58a6ff",    # Blue for commands/links
    "success": "#3fb950",    # Teal/green for success
    "warning": "#e3b341",    # Yellow for warnings
    "error": "#f85149",      # Red for errors
    "accent": "#d2a8ff",     # Purple for highlights
    "cyan": "#39c5cf",       # Cyan for table refs
    
    # Additional
    "tool": "#8b949e",       # Muted for tool indicators
    "spinner": "#58a6ff",    # Blue for spinners
}

# Rich theme object for Console
HEALTHSIM_THEME = Theme({
    # Base styles
    "info": COLORS["command"],
    "success": COLORS["success"],
    "warning": COLORS["warning"],
    "error": COLORS["error"],
    "muted": COLORS["muted"],
    
    # Custom styles
    "user": COLORS["user"],
    "user.label": f"bold {COLORS['user']}",
    "command": COLORS["command"],
    "accent": COLORS["accent"],
    "cyan": COLORS["cyan"],
    "tool": COLORS["tool"],
    
    # Panel styles
    "panel.border": COLORS["border"],
    "panel.title": f"bold {COLORS['text']}",
    
    # Table styles
    "table.header": f"bold {COLORS['text']}",
    "table.border": COLORS["border"],
    
    # Progress styles
    "progress.description": COLORS["muted"],
    "progress.percentage": COLORS["text"],
    "progress.bar.complete": COLORS["success"],
    "progress.bar.finished": COLORS["success"],
    
    # Headline styles
    "headline.success": f"bold {COLORS['success']}",
    "headline.error": f"bold {COLORS['error']}",
    "headline.warning": f"bold {COLORS['warning']}",
})

# Icons for status indicators
ICONS: Dict[str, str] = {
    "success": "✓",
    "error": "✗",
    "warning": "⚠",
    "arrow": "→",
    "bullet": "•",
    "connected": "●",
    "disconnected": "○",
}

# Spinner animation frames
SPINNER_FRAMES = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']

# ASCII art banner
BANNER_ART = """
   █  █ █▀▀ ▄▀█ █   ▀█▀ █  █ █▀ █ █▀▄▀█
   █▀▀█ ██▄ █▀█ █▄▄  █  █▀▀█ ▄█ █ █ ▀ █
"""

# Box drawing characters
BOX = {
    "top_left": "╭",
    "top_right": "╮",
    "bottom_left": "╰",
    "bottom_right": "╯",
    "horizontal": "─",
    "vertical": "│",
}


def get_status_style(status: str) -> str:
    """Get style string for a status type."""
    style_map = {
        "success": f"bold {COLORS['success']}",
        "error": f"bold {COLORS['error']}",
        "warning": f"bold {COLORS['warning']}",
        "info": COLORS["command"],
        "muted": COLORS["muted"],
    }
    return style_map.get(status, COLORS["text"])


def get_icon(icon_type: str) -> str:
    """Get icon character for a type."""
    return ICONS.get(icon_type, "")
