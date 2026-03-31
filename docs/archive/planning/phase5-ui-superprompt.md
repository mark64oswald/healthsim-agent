# HealthSim Agent - Phase 5: UI Enhancements Super-Prompt

**Date**: January 10, 2026  
**Phase**: 5 of 7 - UI Enhancements  
**Estimated Duration**: 10-12 hours  
**Dependencies**: Phase 4 complete (256 tests passing)

---

## Context Summary

Phases 0-4 are complete with 256 tests passing. The UI foundation exists but needs enhancement to match the UX specification in `docs/ux-specification.md`.

**Current State**:
- Basic TerminalUI with Rich console
- Simple welcome banner (text only)
- Basic thinking spinner
- Markdown response rendering
- Basic help/status displays

**Target State**:
- GitHub Dark themed interface
- Streaming response display
- Tool invocation indicators
- Result headlines with icons
- Claude-generated contextual suggestions
- Session status bar

---

## Design Decisions

1. **Streaming**: Yes - better UX, implement Agent SDK streaming callback
2. **Suggestions**: Claude-generated based on recent tools and conversation context
3. **Cost Display**: No - not needed for v1
4. **Status Bar**: Yes - show cohort context and session info

---

## Deliverables

### Target Structure

```
src/healthsim_agent/ui/
├── __init__.py           # Re-export components
├── theme.py              # GitHub Dark color palette (NEW)
├── components.py         # Enhanced Rich components (UPDATE)
├── terminal.py           # Main UI loop (UPDATE)
├── formatters.py         # Data → Rich renderable (NEW)
└── suggestions.py        # Contextual suggestions (NEW)
```

---

## Implementation Steps

### Step 1: Create Theme Module

**File**: `src/healthsim_agent/ui/theme.py`

```python
"""GitHub Dark theme for HealthSim terminal UI."""

from rich.theme import Theme

# GitHub Dark color palette (from UX spec Section 4)
COLORS = {
    "background": "#0d1117",
    "surface": "#161b22",
    "border": "#30363d",
    "text": "#c9d1d9",
    "muted": "#8b949e",
    "user": "#7ee787",
    "command": "#58a6ff",
    "success": "#3fb950",
    "warning": "#e3b341",
    "error": "#f85149",
    "accent": "#d2a8ff",
    "cyan": "#39c5cf",
}

# Rich theme object
HEALTHSIM_THEME = Theme({
    "info": COLORS["command"],
    "success": COLORS["success"],
    "warning": COLORS["warning"],
    "error": COLORS["error"],
    "muted": COLORS["muted"],
    "user": COLORS["user"],
    "command": COLORS["command"],
    "accent": COLORS["accent"],
    "cyan": COLORS["cyan"],
})

# Icons
ICONS = {
    "success": "✓",
    "error": "✗",
    "warning": "⚠",
    "arrow": "→",
    "bullet": "•",
}

# Spinner frames
SPINNER_FRAMES = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
```

### Step 2: Create Formatters Module

**File**: `src/healthsim_agent/ui/formatters.py`

Formatters for converting tool results to Rich renderables:
- `format_tool_indicator(tool_name)` → "→ tool_name"
- `format_result_headline(success, message)` → "✓ Generated 500 patients"
- `format_data_panel(data, title)` → Rich Panel
- `format_data_table(records, title)` → Rich Table with pagination
- `format_suggestions(suggestions)` → Suggestion box

### Step 3: Create Suggestions Module

**File**: `src/healthsim_agent/ui/suggestions.py`

```python
"""Claude-generated contextual suggestions."""

from typing import List, Optional

class SuggestionGenerator:
    """Generate contextual next-action suggestions."""
    
    def __init__(self, skill_router=None):
        self.skill_router = skill_router
        self._last_tool: Optional[str] = None
        self._last_entity_type: Optional[str] = None
    
    def update_context(self, tool_name: str, result: dict) -> None:
        """Update context from last tool execution."""
        self._last_tool = tool_name
        # Extract entity type if present
        if "entity_counts" in result:
            types = list(result["entity_counts"].keys())
            self._last_entity_type = types[0] if types else None
    
    def get_suggestions(self, conversation_summary: str = "") -> List[str]:
        """Generate suggestions based on context."""
        # Rule-based suggestions as fallback
        suggestions = []
        
        if self._last_tool == "add_entities":
            if self._last_entity_type == "patients":
                suggestions = [
                    "Add encounters for these patients",
                    "Generate claims history",
                    "Export to FHIR Bundle",
                ]
            elif self._last_entity_type == "members":
                suggestions = [
                    "Add claims for these members",
                    "Assign PCPs from local providers",
                    "Generate pharmacy claims",
                ]
        elif self._last_tool == "search_providers":
            suggestions = [
                "Create member PCP assignments",
                "Show provider specialties breakdown",
                "Search in a different area",
            ]
        elif self._last_tool == "query":
            suggestions = [
                "Export these results to CSV",
                "Visualize this data",
                "Refine the query",
            ]
        
        return suggestions[:3]  # Max 3 suggestions
```

### Step 4: Update Components Module

**File**: `src/healthsim_agent/ui/components.py`

Add new components:
- `WelcomePanel` - ASCII art banner with database info
- `ToolIndicator` - Shows "→ tool_name" during execution
- `ResultHeadline` - "✓ Success message" with appropriate icon/color
- `DataPanel` - Enhanced bordered panel
- `SuggestionBox` - Contextual next actions
- `StatusBar` - Session info at bottom

### Step 5: Update Terminal Module

**File**: `src/healthsim_agent/ui/terminal.py`

Major updates:
- Use HEALTHSIM_THEME
- Streaming response display with Rich Live
- Tool indicator during execution
- Result headlines after tool completion
- Suggestion display after responses
- Status bar with cohort context

### Step 6: Streaming Integration

Integrate with Agent SDK streaming:
```python
async def stream_response(self, user_input: str) -> None:
    """Stream agent response with live display."""
    with Live(console=self.console, refresh_per_second=10) as live:
        text = Text()
        async for chunk in self.agent.stream_message(user_input):
            text.append(chunk)
            live.update(text)
```

---

## Visual Examples (from UX Spec)

### Welcome Screen
```
╭──────────────────────────────────────────────────────────────────╮
│                                                                  │
│   █  █ █▀▀ ▄▀█ █   ▀█▀ █  █ █▀ █ █▀▄▀█                          │
│   █▀▀█ ██▄ █▀█ █▄▄  █  █▀▀█ ▄█ █ █ ▀ █                          │
│                                                                  │
│   Healthcare Simulation Agent v1.0                               │
│   Powered by Claude • DuckDB Backend                             │
│                                                                  │
│   Database: ~/.healthsim/healthsim.duckdb                        │
│   Reference Data: 8.9M providers │ 100% US geography             │
│                                                                  │
╰──────────────────────────────────────────────────────────────────╯

  Quick Start:
    • "Generate 100 members in Texas"
    • "Create a diabetic patient with complications"
    • "Show me providers in ZIP 92101"
```

### Tool Execution Flow
```
You: Generate 500 diabetic patients in California

→ generate_population

⠋ Generating patients...

✓ Generated 500 patients

┌─ Population Summary ─────────────────────────────────────────────┐
│ Patients: 500 │ Age: 45-78 (mean 62) │ State: CA                 │
│ Controlled (A1c <7%): 215 (43%)                                  │
│ Uncontrolled (A1c ≥7%): 285 (57%)                                │
└──────────────────────────────────────────────────────────────────┘

  Suggested:
    → "Add 12 months of claims history"
    → "Stratify by complication risk"
    → "Export to FHIR Bundle"
```

### Status Bar
```
──────────────────────────────────────────────────────────────────
 Cohort: diabetes_ca_500 │ 500 patients │ Session: 12 messages
```

---

## Test Strategy

Since UI is visual, testing focuses on:
1. Component rendering (no exceptions)
2. Theme color validation
3. Formatter output structure
4. Suggestion generation logic

Add tests to `tests/unit/test_ui_components.py`

---

## Success Criteria

- [ ] GitHub Dark theme applied throughout
- [ ] Welcome screen matches UX spec
- [ ] Tool indicators display during execution
- [ ] Result headlines with appropriate icons
- [ ] Streaming responses display progressively
- [ ] Suggestions appear after substantive responses
- [ ] Status bar shows session context
- [ ] All existing tests still pass
- [ ] New UI tests pass

---

## Post-Implementation

- [ ] Update DEVELOPMENT-PLAN.md Phase 5 section
- [ ] Update CHANGELOG.md
- [ ] Git commit and push
