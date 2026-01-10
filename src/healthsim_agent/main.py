"""
HealthSim Agent - Main Entry Point

A conversational AI agent for healthcare data simulation.
"""
import sys
from pathlib import Path

import click
from rich.console import Console

console = Console()

# Version info
VERSION = "1.0.0"


@click.group(invoke_without_command=True)
@click.option('--debug', is_flag=True, help='Enable debug mode')
@click.option('--config', type=click.Path(), help='Path to configuration file')
@click.version_option(version=VERSION, prog_name='healthsim')
@click.pass_context
def main(ctx: click.Context, debug: bool, config: str | None) -> None:
    """HealthSim - Conversational Healthcare Data Simulation
    
    Generate realistic synthetic healthcare data through natural conversation.
    
    Examples:
    
    \b
        healthsim              # Start interactive chat
        healthsim chat         # Start interactive chat (explicit)
        healthsim status       # Show database and config status
        healthsim query "..."  # Execute a SQL query
    """
    ctx.ensure_object(dict)
    ctx.obj['debug'] = debug
    ctx.obj['config'] = config
    
    # If no subcommand, run interactive chat
    if ctx.invoked_subcommand is None:
        ctx.invoke(chat)


@main.command()
@click.pass_context
def chat(ctx: click.Context) -> None:
    """Start an interactive chat session."""
    from healthsim_agent.agent import HealthSimAgent
    from healthsim_agent.ui.terminal import TerminalUI
    
    debug = ctx.obj.get('debug', False)
    config = ctx.obj.get('config')
    
    # Initialize the terminal UI
    ui = TerminalUI(debug=debug)
    
    # Get database info
    try:
        from healthsim_agent.tools.connection import get_manager, get_db_path
        db_path = str(get_db_path())
        manager = get_manager()
        conn = manager.get_read_connection()
        
        # Get provider count
        try:
            result = conn.execute(
                "SELECT COUNT(*) FROM network.nppes_providers"
            ).fetchone()
            provider_count = f"{result[0]:,.0f}" if result else "N/A"
        except:
            provider_count = "N/A"
        
        connected = True
    except Exception as e:
        db_path = "Not configured"
        provider_count = "N/A"
        connected = False
        if debug:
            console.print(f"[yellow]Database connection error: {e}[/yellow]")
    
    # Display welcome banner
    ui.show_welcome(
        version=VERSION,
        db_path=db_path,
        provider_count=provider_count,
        connected=connected,
    )
    
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


@main.command()
@click.pass_context
def status(ctx: click.Context) -> None:
    """Show database and configuration status."""
    from rich.table import Table
    from rich.panel import Panel
    
    debug = ctx.obj.get('debug', False)
    
    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Component", style="dim")
    table.add_column("Status")
    table.add_column("Details")
    
    # Database status
    try:
        from healthsim_agent.tools.connection import get_manager, get_db_path
        db_path = get_db_path()
        manager = get_manager()
        conn = manager.get_read_connection()
        
        # Check tables
        tables = conn.execute(
            "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'main'"
        ).fetchone()[0]
        
        table.add_row(
            "Database",
            "[green]Connected[/green]",
            f"{db_path}"
        )
        table.add_row(
            "Tables",
            f"[green]{tables}[/green]",
            "main schema"
        )
        
        # Provider count
        try:
            result = conn.execute(
                "SELECT COUNT(*) FROM network.nppes_providers"
            ).fetchone()
            prov_count = f"{result[0]:,}" if result else "0"
            table.add_row(
                "NPPES Providers",
                f"[green]{prov_count}[/green]",
                "network.nppes_providers"
            )
        except:
            table.add_row(
                "NPPES Providers",
                "[yellow]N/A[/yellow]",
                "Table not loaded"
            )
        
        # Population data
        try:
            result = conn.execute(
                "SELECT COUNT(*) FROM population.places"
            ).fetchone()
            places_count = f"{result[0]:,}" if result else "0"
            table.add_row(
                "CDC PLACES",
                f"[green]{places_count}[/green]",
                "population.places"
            )
        except:
            table.add_row(
                "CDC PLACES",
                "[yellow]N/A[/yellow]",
                "Table not loaded"
            )
        
    except Exception as e:
        table.add_row(
            "Database",
            "[red]Disconnected[/red]",
            str(e) if debug else "Connection failed"
        )
    
    # Cohorts
    try:
        result = conn.execute("SELECT COUNT(*) FROM cohorts").fetchone()
        cohort_count = result[0] if result else 0
        table.add_row(
            "Cohorts",
            f"[green]{cohort_count}[/green]",
            "Saved cohorts"
        )
    except:
        table.add_row(
            "Cohorts",
            "[yellow]0[/yellow]",
            "No cohorts"
        )
    
    panel = Panel(
        table,
        title="[bold]HealthSim Status[/bold]",
        border_style="cyan",
    )
    console.print(panel)


@main.command()
@click.argument('sql')
@click.option('--format', '-f', type=click.Choice(['table', 'json', 'csv']), 
              default='table', help='Output format')
@click.option('--limit', '-n', type=int, default=100, help='Max rows to return')
@click.pass_context
def query(ctx: click.Context, sql: str, format: str, limit: int) -> None:
    """Execute a SQL query against the database.
    
    Example:
        healthsim query "SELECT * FROM cohorts LIMIT 5"
    """
    import json
    
    debug = ctx.obj.get('debug', False)
    
    try:
        from healthsim_agent.tools.connection import get_manager
        
        manager = get_manager()
        conn = manager.get_read_connection()
        
        # Add limit if not present
        if 'limit' not in sql.lower():
            sql = f"{sql} LIMIT {limit}"
        
        result = conn.execute(sql)
        rows = result.fetchall()
        columns = [desc[0] for desc in result.description]
        
        if format == 'json':
            data = [dict(zip(columns, row)) for row in rows]
            console.print_json(json.dumps(data, default=str, indent=2))
        
        elif format == 'csv':
            import csv
            import io
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(columns)
            writer.writerows(rows)
            console.print(output.getvalue())
        
        else:  # table
            from rich.table import Table
            
            table = Table(show_header=True, header_style="bold cyan")
            for col in columns:
                table.add_column(col)
            
            for row in rows[:limit]:
                table.add_row(*[str(v) if v is not None else "" for v in row])
            
            console.print(table)
            console.print(f"[dim]{len(rows)} rows returned[/dim]")
        
    except Exception as e:
        if debug:
            console.print_exception()
        else:
            console.print(f"[red]Query failed:[/red] {e}")
        raise SystemExit(1)


@main.command()
@click.pass_context
def cohorts(ctx: click.Context) -> None:
    """List all saved cohorts."""
    from rich.table import Table
    
    try:
        from healthsim_agent.tools.connection import get_manager
        
        manager = get_manager()
        conn = manager.get_read_connection()
        
        result = conn.execute("""
            SELECT 
                c.id,
                c.name,
                c.description,
                c.created_at,
                COUNT(ce.id) as entity_count
            FROM cohorts c
            LEFT JOIN cohort_entities ce ON c.id = ce.cohort_id
            GROUP BY c.id, c.name, c.description, c.created_at
            ORDER BY c.created_at DESC
        """)
        
        rows = result.fetchall()
        
        if not rows:
            console.print("[yellow]No cohorts found.[/yellow]")
            return
        
        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("ID", style="dim")
        table.add_column("Name")
        table.add_column("Description", max_width=40)
        table.add_column("Entities", justify="right")
        table.add_column("Created", style="dim")
        
        for row in rows:
            created = row[3].strftime("%Y-%m-%d %H:%M") if row[3] else "N/A"
            table.add_row(
                row[0][:12] + "..." if len(row[0]) > 15 else row[0],
                row[1] or "Unnamed",
                (row[2] or "")[:40],
                str(row[4]),
                created,
            )
        
        console.print(table)
        console.print(f"[dim]{len(rows)} cohorts total[/dim]")
        
    except Exception as e:
        console.print(f"[red]Failed to list cohorts:[/red] {e}")
        raise SystemExit(1)


@main.command()
@click.argument('cohort_id')
@click.option('--format', '-f', type=click.Choice(['summary', 'json', 'fhir', 'csv']),
              default='summary', help='Export format')
@click.option('--output', '-o', type=click.Path(), help='Output file path')
@click.pass_context
def export(ctx: click.Context, cohort_id: str, format: str, output: str | None) -> None:
    """Export a cohort to various formats.
    
    Example:
        healthsim export my-cohort --format fhir -o patients.json
    """
    import json
    
    try:
        from healthsim_agent.tools.connection import get_manager
        
        manager = get_manager()
        conn = manager.get_read_connection()
        
        # Get cohort
        cohort = conn.execute(
            "SELECT * FROM cohorts WHERE id = ? OR name = ?",
            [cohort_id, cohort_id]
        ).fetchone()
        
        if not cohort:
            console.print(f"[red]Cohort not found: {cohort_id}[/red]")
            raise SystemExit(1)
        
        actual_id = cohort[0]
        
        # Get entities
        entities = conn.execute(
            "SELECT entity_type, entity_data FROM cohort_entities WHERE cohort_id = ?",
            [actual_id]
        ).fetchall()
        
        # Build data
        data = {}
        for entity_type, entity_data in entities:
            if entity_type not in data:
                data[entity_type] = []
            if isinstance(entity_data, str):
                import json as json_module
                entity_data = json_module.loads(entity_data)
            data[entity_type].append(entity_data)
        
        if format == 'summary':
            from rich.table import Table
            
            table = Table(show_header=True, header_style="bold cyan")
            table.add_column("Entity Type")
            table.add_column("Count", justify="right")
            
            for entity_type, items in sorted(data.items()):
                table.add_row(entity_type, str(len(items)))
            
            console.print(table)
        
        elif format == 'json':
            output_data = json.dumps(data, default=str, indent=2)
            if output:
                Path(output).write_text(output_data)
                console.print(f"[green]Exported to {output}[/green]")
            else:
                console.print_json(output_data)
        
        elif format == 'fhir':
            from healthsim_agent.tools.format_tools import transform_to_fhir
            result = transform_to_fhir(actual_id)
            if result.success:
                output_data = json.dumps(result.data, default=str, indent=2)
                if output:
                    Path(output).write_text(output_data)
                    console.print(f"[green]Exported FHIR bundle to {output}[/green]")
                else:
                    console.print_json(output_data)
            else:
                console.print(f"[red]FHIR export failed: {result.error}[/red]")
        
        elif format == 'csv':
            import csv
            import io
            
            for entity_type, items in data.items():
                if not items:
                    continue
                
                output_file = output or f"{cohort_id}_{entity_type}.csv"
                if output and len(data) > 1:
                    # Multiple entity types - add suffix
                    base, ext = Path(output).stem, Path(output).suffix
                    output_file = f"{base}_{entity_type}{ext or '.csv'}"
                
                keys = items[0].keys() if items else []
                
                out = io.StringIO()
                writer = csv.DictWriter(out, fieldnames=keys)
                writer.writeheader()
                writer.writerows(items)
                
                Path(output_file).write_text(out.getvalue())
                console.print(f"[green]Exported {len(items)} {entity_type} to {output_file}[/green]")
        
    except Exception as e:
        console.print(f"[red]Export failed:[/red] {e}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
