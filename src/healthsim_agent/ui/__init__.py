"""
HealthSim Agent - UI Package

Terminal user interface components using Rich.
"""

from .theme import (
    COLORS,
    ICONS,
    HEALTHSIM_THEME,
    BANNER_ART,
    SPINNER_FRAMES,
    get_status_style,
    get_icon,
)

from .components import (
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

from .formatters import (
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

from .suggestions import (
    SuggestionGenerator,
    get_suggestion_generator,
    get_suggestions_for_tool,
)

from .terminal import (
    TerminalUI,
    ToolCallbackHandler,
)

__all__ = [
    # Theme
    "COLORS",
    "ICONS", 
    "HEALTHSIM_THEME",
    "BANNER_ART",
    "SPINNER_FRAMES",
    "get_status_style",
    "get_icon",
    
    # Components
    "WelcomePanel",
    "ToolIndicator",
    "ResultHeadline",
    "SuggestionBox",
    "StatusBar",
    "ThinkingSpinner",
    "ProgressDisplay",
    "DataPreview",
    "HelpDisplay",
    
    # Formatters
    "format_tool_indicator",
    "format_result_headline",
    "format_data_panel",
    "format_data_table",
    "format_suggestions",
    "format_sql",
    "format_json",
    "format_error",
    "format_cohort_summary",
    "format_provider_results",
    
    # Suggestions
    "SuggestionGenerator",
    "get_suggestion_generator",
    "get_suggestions_for_tool",
    
    # Terminal
    "TerminalUI",
    "ToolCallbackHandler",
]
