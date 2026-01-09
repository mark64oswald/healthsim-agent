"""
HealthSim Agent - Terminal UI Implementation

Main terminal interface using Rich for rendering.
"""
from typing import TYPE_CHECKING

from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.markdown import Markdown
from rich.live import Live
from rich.spinner import Spinner
from rich.table import Table

if TYPE_CHECKING:
    from healthsim_agent.agent import HealthSimAgent

# Color palette from UX specification
COLORS = {
    "primary": "#4A9BD9",      # Healthcare Blue
    "success": "#2E8B57",      # Medical Green
    "warning": "#DAA520",      # Alert Gold  
    "error": "#CD5C5C",        # Soft Red
    "info": "#708090",         # Slate Gray
    "background": "#1E1E2E",   # Dark charcoal
    "surface": "#2D2D3D",      # Elevated surface
    "text": "#E8E8E8",         # Primary text
    "muted": "#A0A0A0",        # Secondary text
}


class TerminalUI:
    """
    Rich-based terminal interface for HealthSim.
    
    Provides:
    - Styled welcome banner and prompts
    - Real-time streaming of agent responses
    - Data preview panels
    - Status indicators and progress displays
    """
    
    def __init__(self, debug: bool = False):
        self.debug = debug
        self.console = Console()
        self._history_file = ".healthsim_history"
        self._session: PromptSession | None = None
    
    def show_welcome(self) -> None:
        """Display the welcome banner."""
        banner = Text()
        banner.append("╔══════════════════════════════════════════════════════════╗\n", style=f"bold {COLORS['primary']}")
        banner.append("║", style=f"bold {COLORS['primary']}")
        banner.append("          HealthSim Agent v0.1.0                         ", style=f"bold {COLORS['text']}")
        banner.append("║\n", style=f"bold {COLORS['primary']}")
        banner.append("║", style=f"bold {COLORS['primary']}")
        banner.append("    Conversational Healthcare Data Simulation            ", style=COLORS['muted'])
        banner.append("║\n", style=f"bold {COLORS['primary']}")
        banner.append("╚══════════════════════════════════════════════════════════╝", style=f"bold {COLORS['primary']}")
        
        self.console.print()
        self.console.print(banner)
        self.console.print()
        
        # Quick help
        help_text = Text()
        help_text.append("Commands: ", style=f"bold {COLORS['info']}")
        help_text.append("/help", style=f"bold {COLORS['primary']}")
        help_text.append(" • ", style=COLORS['muted'])
        help_text.append("/status", style=f"bold {COLORS['primary']}")
        help_text.append(" • ", style=COLORS['muted'])
        help_text.append("/quit", style=f"bold {COLORS['primary']}")
        help_text.append(" • ", style=COLORS['muted'])
        help_text.append("Type naturally to generate data", style=COLORS['muted'])
        
        self.console.print(help_text)
        self.console.print()
    
    def show_goodbye(self) -> None:
        """Display goodbye message."""
        self.console.print()
        self.console.print(
            "[bold]Thank you for using HealthSim![/bold]",
            style=COLORS['primary']
        )
        self.console.print()
    
    def get_input(self) -> str:
        """Get user input with prompt styling."""
        if not self._session:
            self._session = PromptSession(
                history=FileHistory(self._history_file),
                auto_suggest=AutoSuggestFromHistory(),
            )
        
        # Create styled prompt
        prompt_text = [
            (COLORS['primary'], "healthsim"),
            (COLORS['muted'], " › "),
        ]
        
        return self._session.prompt(prompt_text)
    
    def show_thinking(self) -> Live:
        """Show thinking indicator."""
        spinner = Spinner("dots", text="Thinking...", style=COLORS['info'])
        return Live(spinner, console=self.console, refresh_per_second=10)
    
    def show_response(self, response: str) -> None:
        """Display agent response with formatting."""
        # Render as markdown for rich formatting
        md = Markdown(response)
        self.console.print()
        self.console.print(md)
        self.console.print()
    
    def show_error(self, message: str) -> None:
        """Display error message."""
        self.console.print(
            Panel(
                message,
                title="Error",
                border_style=COLORS['error'],
            )
        )
    
    def show_status(self, agent: "HealthSimAgent") -> None:
        """Display current session status."""
        table = Table(show_header=False, box=None)
        table.add_column("Key", style=COLORS['muted'])
        table.add_column("Value", style=COLORS['text'])
        
        table.add_row("Database", "Connected" if agent.is_connected else "Not connected")
        table.add_row("Messages", str(len(agent.session.messages)))
        table.add_row("Mode", "Interactive")
        
        panel = Panel(
            table,
            title="Session Status",
            border_style=COLORS['info'],
        )
        self.console.print(panel)
    
    def show_help(self) -> None:
        """Display help information."""
        help_md = """
## HealthSim Commands

| Command | Description |
|---------|-------------|
| `/help` | Show this help message |
| `/status` | Show session status |
| `/clear` | Clear conversation history |
| `/export [file]` | Export generated data |
| `/quit` | Exit HealthSim |

## Generation Examples

- "Generate a 45-year-old diabetic patient"
- "Create a pharmacy claim for metformin"
- "Design a Phase 3 oncology trial"
- "Show providers in Austin, TX"

## Tips

- Be specific about patient demographics for realistic data
- Use clinical terminology for accurate coding
- Reference specific time periods for claims data
"""
        self.console.print(Markdown(help_md))
    
    def run(self, agent: "HealthSimAgent") -> None:
        """
        Run the interactive session loop.
        
        Handles user input, commands, and agent responses.
        """
        while True:
            try:
                # Get user input
                user_input = self.get_input().strip()
                
                if not user_input:
                    continue
                
                # Handle commands
                if user_input.startswith("/"):
                    command = user_input[1:].lower().split()[0]
                    
                    if command in ("quit", "exit", "q"):
                        break
                    elif command == "help":
                        self.show_help()
                    elif command == "status":
                        self.show_status(agent)
                    elif command == "clear":
                        agent.session.clear()
                        self.console.print("[dim]Conversation cleared.[/dim]")
                    else:
                        self.console.print(f"[yellow]Unknown command: {command}[/yellow]")
                    continue
                
                # Process message through agent
                with self.show_thinking():
                    response = agent.process_message(user_input)
                
                self.show_response(response)
                
            except KeyboardInterrupt:
                self.console.print("\n[dim]Use /quit to exit[/dim]")
            except EOFError:
                break
