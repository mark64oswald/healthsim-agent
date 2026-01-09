"""
HealthSim Agent - Main Entry Point

A conversational AI agent for healthcare data simulation.
"""
import click
from rich.console import Console

from healthsim_agent.agent import HealthSimAgent
from healthsim_agent.ui.terminal import TerminalUI


console = Console()


@click.command()
@click.option('--debug', is_flag=True, help='Enable debug mode')
@click.option('--config', type=click.Path(), help='Path to configuration file')
@click.version_option(version='0.1.0', prog_name='healthsim')
def main(debug: bool, config: str | None) -> None:
    """HealthSim - Conversational Healthcare Data Simulation"""
    
    # Initialize the terminal UI
    ui = TerminalUI(debug=debug)
    
    # Display welcome banner
    ui.show_welcome()
    
    # Initialize the agent
    agent = HealthSimAgent(config_path=config, debug=debug)
    
    # Start the interactive session
    try:
        ui.run(agent)
    except KeyboardInterrupt:
        ui.show_goodbye()
    except Exception as e:
        if debug:
            console.print_exception()
        else:
            console.print(f"[red]Error:[/red] {e}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
