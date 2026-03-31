# HealthSim Agent — Terminal UX Requirements

## Executive Summary

This document specifies the user experience requirements for the HealthSim Agent terminal interface. The goal is a conversational, rich-text CLI that feels modern and approachable while maintaining the simplicity of a traditional terminal application.

**Design Philosophy**: Simple elegance over feature complexity. The interface should feel like a knowledgeable colleague who happens to communicate through a beautifully formatted terminal.

---

## 1. User Personas & Workflows

### Primary Persona: Healthcare Data Analyst
- **Context**: Needs synthetic healthcare data for testing, demos, or research
- **Technical Level**: Comfortable with command line, not necessarily a developer
- **Workflow**: Conversational exploration → Generate data → Query/analyze → Export

### Secondary Persona: Developer/Integrator
- **Context**: Building healthcare applications, needs realistic test data
- **Technical Level**: High technical proficiency
- **Workflow**: Scripted generation → Integration testing → Format validation

### Tertiary Persona: Healthcare Educator
- **Context**: Creating patient scenarios for training
- **Technical Level**: Moderate, may be clinically focused
- **Workflow**: Describe scenario → Generate patient/encounter → Review clinical accuracy

---

## 2. Interaction Model

### 2.1 Conversational Flow
The primary interaction is natural language conversation, not commands.

```
┌─────────────────────────────────────────────────────────────────┐
│  HealthSim Agent v1.0                                           │
│  Healthcare simulation through conversation                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  You: Generate 500 diabetic patients in California with a mix   │
│       of controlled and uncontrolled A1c levels                 │
│                                                                 │
│  → generate_population                                          │
│                                                                 │
│  ✓ Generated 500 patients                                       │
│                                                                 │
│  ┌─ Population Summary ─────────────────────────────────────┐   │
│  │ Patients: 500 │ Age: 45-78 (mean 62) │ State: CA         │   │
│  │ Controlled (A1c <7%): 215 (43%)                          │   │
│  │ Uncontrolled (A1c ≥7%): 285 (57%)                        │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                 │
│  Suggested:                                                     │
│    → "Add 12 months of claims history"                          │
│    → "Stratify by complication risk"                            │
│    → "Export to FHIR Bundle"                                    │
│                                                                 │
│  You: █                                                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Input Handling
- **Primary**: Natural language prompts
- **Secondary**: Slash commands for system functions (`/help`, `/clear`, `/exit`, `/export`)
- **Tertiary**: Direct SQL for power users (`/sql SELECT ...`)

### 2.3 Response Structure
Every agent response follows a consistent structure:

1. **Tool Indicator** (when applicable): Shows which tool is being invoked
2. **Result Headline**: Clear success/failure with key metric
3. **Data Panel**: Formatted summary, table, or preview
4. **Suggestions**: Contextual next actions
5. **Cost Badge** (optional): API cost for transparency

---

## 3. Visual Components

### 3.1 Welcome Screen
Displayed on startup. Sets context and offers quick-start options.

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
    
  Type /help for commands or just describe what you need.
```

### 3.2 User Prompt
Clean, minimal prefix indicating user input.

```
You: Generate 50 patients with heart failure
```

Color: Green for "You:" label, default for text.

### 3.3 Tool Indicator
Shows when the agent invokes a tool. Appears immediately, before results.

```
→ generate_population
```

Color: Dim/muted cyan. Arrow indicates action in progress.

### 3.4 Progress Indicator
For operations that take time (>1 second).

```
⠋ Generating 500 patients...
```

Spinner animation: `['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']`

For operations with known progress:

```
Generating claims ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 67% 0:00:12
```

### 3.5 Result Headlines
Clear, scannable summaries.

```
✓ Generated 500 patients                    # Success - green checkmark
✓ Exported 127,483 claims to X12 837P       # Success with detail
⚠ Generated 487 patients (13 failed validation)  # Partial success - yellow
✗ Failed to connect to database             # Error - red X
```

### 3.6 Data Panels
Bordered panels for structured information.

```
┌─ Population Summary ─────────────────────────────────────────────┐
│ Patients: 500 │ Age Range: 45-78 (mean 62) │ State: CA           │
│                                                                  │
│ A1c Distribution:                                                │
│   Controlled (<7%):    215 (43%)  ████████████░░░░░░░░           │
│   Uncontrolled (≥7%):  285 (57%)  ████████████████░░░░           │
│                                                                  │
│ Top Comorbidities:                                               │
│   • Hypertension: 423 (85%)                                      │
│   • Hyperlipidemia: 312 (62%)                                    │
│   • CKD Stage 2-3: 145 (29%)                                     │
└──────────────────────────────────────────────────────────────────┘
```

### 3.7 Data Tables
For tabular data display.

```
┌─ Sample Patients ────────────────────────────────────────────────┐
│ ID        │ Name              │ Age │ A1c  │ Risk   │ Cost/Year  │
├───────────┼───────────────────┼─────┼──────┼────────┼────────────┤
│ P-001     │ Maria Garcia      │ 67  │ 8.2% │ High   │ $45,230    │
│ P-002     │ James Wilson      │ 54  │ 6.8% │ Medium │ $12,450    │
│ P-003     │ Sarah Chen        │ 71  │ 9.1% │ High   │ $67,890    │
│ P-004     │ Robert Johnson    │ 48  │ 6.4% │ Low    │ $8,120     │
│ P-005     │ Jennifer Smith    │ 62  │ 7.5% │ Medium │ $23,560    │
├───────────┴───────────────────┴─────┴──────┴────────┴────────────┤
│ Showing 5 of 500 • "Show more" or "Show patient P-003"           │
└──────────────────────────────────────────────────────────────────┘
```

### 3.8 Code/Query Display
Syntax-highlighted code blocks for SQL, JSON, or generated formats.

```
┌─ Generated SQL ──────────────────────────────────────────────────┐
│ SELECT                                                           │
│     p.patient_id,                                                │
│     p.name,                                                      │
│     d.diagnosis_code,                                            │
│     d.diagnosis_date                                             │
│ FROM patients p                                                  │
│ JOIN diagnoses d ON p.patient_id = d.patient_id                  │
│ WHERE d.diagnosis_code LIKE 'E11%'                               │
│ ORDER BY d.diagnosis_date DESC                                   │
│ LIMIT 10;                                                        │
└──────────────────────────────────────────────────────────────────┘
```

### 3.9 Suggestion Box
Contextual next actions, always present after substantive responses.

```
  Suggested:
    → "Add 12 months of claims history"
    → "Stratify by complication risk"
    → "Export to FHIR Bundle"
```

Color: Muted text, commands in cyan.

### 3.10 Cost Badge
API cost transparency (optional, configurable).

```
Cost: $0.0198
```

Color: Dim gray, right-aligned.

### 3.11 Error Display
Clear error messages with actionable guidance.

```
┌─ Error ──────────────────────────────────────────────────────────┐
│ ✗ Database connection failed                                     │
│                                                                  │
│ The DuckDB database at ~/.healthsim/healthsim.duckdb could not   │
│ be opened. This may happen if another process has a write lock.  │
│                                                                  │
│ Try:                                                             │
│   1. Close other HealthSim sessions                              │
│   2. Run: healthsim --repair-db                                  │
│   3. Check file permissions                                      │
└──────────────────────────────────────────────────────────────────┘
```

### 3.12 Help Display
Organized by category with examples.

```
╭─ HealthSim Commands ─────────────────────────────────────────────╮
│                                                                  │
│ 📦 Generation                                                    │
│   "Generate 1000 members in California"                          │
│   "Create a patient with CHF and diabetes"                       │
│   "Add 12 months of claims history"                              │
│                                                                  │
│ 📊 Analytics                                                     │
│   "Profile this population"                                      │
│   "Stratify by risk level"                                       │
│   "What are the top cost drivers?"                               │
│                                                                  │
│ 🗄️ Data                                                          │
│   "Show tables" • "Describe patients"                            │
│   "/sql SELECT ..." — Run custom SQL                             │
│   "Export to FHIR" • "Export to CSV"                             │
│                                                                  │
│ ⚙️ System                                                         │
│   /help — This message                                           │
│   /clear — Clear screen                                          │
│   /cost — Show session cost                                      │
│   /exit or quit — Exit application                               │
│                                                                  │
╰──────────────────────────────────────────────────────────────────╯
```

---

## 4. Color Palette

Based on GitHub Dark theme (as shown in healthsim-agent-cli-ux-examples.html):

| Element | Color | Hex |
|---------|-------|-----|
| Background | Dark gray | `#0d1117` |
| Surface (panels) | Slightly lighter | `#161b22` |
| Border | Subtle gray | `#30363d` |
| Primary text | Light gray | `#c9d1d9` |
| Muted text | Medium gray | `#8b949e` |
| User prompt label | Green | `#7ee787` |
| Commands/links | Blue | `#58a6ff` |
| Success | Teal/green | `#3fb950` |
| Warning | Yellow | `#e3b341` |
| Error | Red | `#f85149` |
| Accent (highlights) | Purple | `#d2a8ff` |
| Table refs | Cyan | `#39c5cf` |

---

## 5. Interaction States

### 5.1 Idle
Cursor blinking at input prompt, ready for user input.

### 5.2 Thinking
Agent is processing but hasn't invoked a tool yet.
```
⠋ Thinking...
```

### 5.3 Tool Executing
Agent has invoked a tool, waiting for result.
```
→ generate_population
⠋ Generating 500 patients...
```

### 5.4 Streaming Response
Agent is returning text response (streamed).
Text appears progressively, character by character or word by word.

### 5.5 Awaiting Confirmation (optional, for destructive actions)
```
⚠ This will delete cohort 'diabetes_study'. Continue? [y/N]
```

---

## 6. Keyboard & Input

### 6.1 Standard Input
- **Enter**: Submit prompt
- **Ctrl+C**: Cancel current operation / Clear input
- **Ctrl+D**: Exit application
- **Up/Down arrows**: Command history navigation (if implemented)

### 6.2 Slash Commands
| Command | Action |
|---------|--------|
| `/help` | Show help |
| `/clear` | Clear screen |
| `/exit`, `/quit` | Exit application |
| `/cost` | Show session cost summary |
| `/sql <query>` | Execute raw SQL |
| `/export <format>` | Quick export (csv, fhir, x12) |
| `/history` | Show conversation history |

---

## 7. Session & State

### 7.1 Persistent State
- Current cohort/population context
- Conversation history (within session)
- Generated tables and their row counts

### 7.2 Session Status Bar (optional)
Minimal status at bottom of screen:

```
──────────────────────────────────────────────────────────────────
 Cohort: diabetes_ca_500 │ 500 patients │ Cost: $0.12 │ /help
```

---

## 8. Accessibility Considerations

1. **Color is not the only indicator**: Icons (✓, ✗, ⚠) accompany colors
2. **High contrast**: Text meets WCAG contrast guidelines
3. **No animation dependency**: Spinners are informative but not required
4. **Screen reader friendly**: Logical text flow, no decorative-only content

---

## 9. Non-Requirements (Explicitly Out of Scope)

- **Split panes**: Not needed for initial version
- **Mouse interaction**: Keyboard-only interface
- **Persistent panels**: No dashboard-style fixed regions
- **Real-time updates**: No live-updating displays
- **Image rendering**: Text-only output
- **Tab completion**: Nice-to-have for future, not v1

---

## 10. Technology Recommendation

### Decision: Python + Rich Library

#### Rationale

| Factor | Claude Code Stack (TypeScript/Ink) | Python/Rich | Winner |
|--------|-----------------------------------|-------------|--------|
| **Language alignment** | Would require TypeScript UI + Python backend | Single language for entire app | **Python** |
| **Existing codebase** | 0 lines TypeScript | ~20,000 lines Python | **Python** |
| **Learning curve** | React paradigm, JSX, npm ecosystem | Pythonic API, familiar | **Python** |
| **Feature coverage** | Full (tables, progress, syntax) | Full (tables, progress, syntax) | Tie |
| **Maintenance** | Separate UI codebase | Unified codebase | **Python** |
| **Agent SDK** | Available (TypeScript version) | Available (Python version) | Tie |
| **Flickering issues** | Known issue with Ink | No flicker (not React-based) | **Python** |

#### Why Not Claude Code's Stack?

Claude Code uses TypeScript + React + Ink because:
1. Claude (the model) is very proficient with React/TypeScript ("on distribution")
2. The Claude Code team has extensive React expertise
3. They rebuilt parts of Ink to address flickering

For HealthSim:
1. The entire existing codebase is Python
2. We're using the Python Agent SDK
3. Rich provides all required visual components without React complexity
4. Maintaining a single language stack reduces cognitive overhead

#### Rich Library Capabilities

| Requirement | Rich Feature |
|-------------|--------------|
| Syntax highlighting | `rich.syntax.Syntax` |
| Tables | `rich.table.Table` |
| Progress bars | `rich.progress.Progress` |
| Panels/boxes | `rich.panel.Panel` |
| Markdown rendering | `rich.markdown.Markdown` |
| Spinners | `rich.status.Status` |
| Colors/styles | `rich.style.Style`, markup syntax |
| Tree views | `rich.tree.Tree` |
| Live updating | `rich.live.Live` |
| Columns layout | `rich.columns.Columns` |

#### Implementation Architecture

```
healthsim-agent/
├── src/
│   └── healthsim_agent/
│       ├── __init__.py
│       ├── main.py              # Entry point, conversation loop
│       ├── agent.py             # Claude Agent SDK integration
│       ├── ui/
│       │   ├── __init__.py
│       │   ├── console.py       # Rich Console wrapper
│       │   ├── components.py    # Reusable UI components
│       │   ├── themes.py        # Color palette definitions
│       │   └── formatters.py    # Data → Rich renderable conversion
│       ├── tools/               # Agent tool definitions
│       ├── state/               # Ported from workspace
│       ├── generation/          # Ported from workspace
│       └── db/                  # Ported from workspace
├── pyproject.toml
└── README.md
```

#### Sample Implementation

```python
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.syntax import Syntax
from rich.theme import Theme

# Custom theme matching our color palette
healthsim_theme = Theme({
    "info": "#58a6ff",
    "success": "#3fb950",
    "warning": "#e3b341",
    "error": "#f85149",
    "muted": "#8b949e",
    "user": "#7ee787",
    "command": "#58a6ff",
    "table_ref": "#39c5cf",
})

console = Console(theme=healthsim_theme)

# User prompt
console.print("[user]You:[/user] Generate 500 diabetic patients")

# Tool indicator
console.print("[muted]→ generate_population[/muted]")

# Progress spinner
with console.status("[muted]Generating patients...[/muted]", spinner="dots"):
    # ... generation happens here
    pass

# Success headline
console.print("[success]✓[/success] Generated 500 patients")

# Summary panel
summary = Panel(
    "Patients: 500 │ Age: 45-78 (mean 62) │ State: CA\n"
    "Controlled (A1c <7%): 215 (43%)\n"
    "Uncontrolled (A1c ≥7%): 285 (57%)",
    title="Population Summary",
    border_style="dim",
)
console.print(summary)

# Suggestions
console.print("\n[muted]Suggested:[/muted]")
console.print("  [muted]→[/muted] [command]\"Add 12 months of claims history\"[/command]")
console.print("  [muted]→[/muted] [command]\"Stratify by complication risk\"[/command]")
```

---

## 11. Implementation Phases

### Phase 1: Core UI Shell (3-4 hours)
- Welcome screen
- Input prompt loop
- Basic response display (text, headlines)
- Slash command handling

### Phase 2: Rich Components (4-5 hours)
- Panels and tables
- Syntax highlighting for SQL/JSON
- Progress indicators
- Error display

### Phase 3: Agent Integration (4-5 hours)
- Connect to Claude Agent SDK
- Tool invocation display
- Streaming response handling
- Cost tracking

### Phase 4: Polish (2-3 hours)
- Suggestion system
- Help display
- Session status
- Edge case handling

**Total Estimated Effort**: 13-17 hours

---

## 12. Success Criteria

1. **User can have a natural conversation** to generate healthcare data
2. **Tool invocations are visible** but not intrusive
3. **Data is displayed clearly** in tables and panels
4. **Errors provide actionable guidance**
5. **Interface feels responsive** (no perceptible lag for UI updates)
6. **Works in standard terminals** (macOS Terminal, iTerm2, Windows Terminal, Linux terminals)

---

## Appendix A: Reference Mockup

See: `docs/design/cli-ux-mockup.html`

This HTML document contains the visual mockups that inspired this specification. The implementation should match these designs as closely as terminal capabilities allow.

---

## Appendix B: Alternative Considered

### Textual (Full TUI Framework)

Textual is Rich's sister project for building full terminal user interfaces with widgets, mouse support, and complex layouts.

**Why not Textual for v1:**
- Overkill for conversational interface
- Adds complexity without clear benefit
- Mouse support not needed
- Could be considered for v2 if dashboard features are requested

**When to reconsider Textual:**
- If users request persistent data panels
- If split-pane views become a requirement
- If interactive data exploration (clicking rows, etc.) is needed
