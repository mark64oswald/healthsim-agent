"""Query tools for HealthSim Agent.

These tools execute queries against the HealthSim database:
- query: Execute read-only SQL queries
- get_summary: Get token-efficient cohort summary
- list_tables: List all database tables by category
"""

from typing import Any, Dict, List, Optional
import re

from .base import ToolResult, ok, err
from .connection import get_manager


# =============================================================================
# SQL Query
# =============================================================================

# Dangerous SQL keywords that should never be in a read-only query
DANGEROUS_KEYWORDS = {
    "insert", "update", "delete", "drop", "alter", 
    "create", "truncate", "grant", "revoke"
}


def query(
    sql: str,
    limit: int = 100
) -> ToolResult:
    """Execute a read-only SQL query against the HealthSim database.
    
    Only SELECT, SHOW, DESCRIBE, and WITH queries are allowed.
    Automatically adds LIMIT if not present.
    
    Args:
        sql: SQL query string
        limit: Maximum rows to return (default 100, max 1000)
        
    Returns:
        ToolResult with columns and rows
        
    Available tables:
        - Reference: population.places_county, population.svi_tract, etc.
        - Entity: patients, members, encounters, claims
        - Network: network.providers (8.9M NPPES records)
        - System: cohorts, cohort_entities, cohort_tags
        
    Example:
        >>> result = query("SELECT * FROM cohorts LIMIT 5")
        >>> result.data["columns"]
        ["id", "name", "description", ...]
        >>> result.data["rows"]
        [{"id": "...", "name": "...", ...}, ...]
    """
    if not sql or not sql.strip():
        return err("SQL query is required")
    
    sql = sql.strip()
    sql_lower = sql.lower()
    
    # Validate query type
    if not sql_lower.startswith(("select", "show", "describe", "with")):
        return err(
            "Only SELECT, SHOW, DESCRIBE, and WITH queries are allowed",
            hint="Use cohort tools for write operations"
        )
    
    # Check for dangerous keywords
    # Split on non-word characters to avoid matching within words
    words = set(re.split(r'\W+', sql_lower))
    found_dangerous = words & DANGEROUS_KEYWORDS
    if found_dangerous:
        return err(
            f"Query contains forbidden keyword(s): {', '.join(found_dangerous)}",
            hint="This tool only supports read operations"
        )
    
    # Clamp limit
    limit = max(1, min(limit, 1000))
    
    try:
        conn = get_manager().get_read_connection()
        
        # Add LIMIT if not present (but not for SHOW/DESCRIBE which don't support it)
        if "limit" not in sql_lower and not sql_lower.startswith(("show", "describe")):
            sql = f"{sql.rstrip(';')} LIMIT {limit}"
        
        result = conn.execute(sql).fetchall()
        columns = [desc[0] for desc in conn.description]
        
        # Convert to list of dicts
        rows = []
        for row in result:
            rows.append({col: val for col, val in zip(columns, row)})
        
        return ok({
            "columns": columns,
            "row_count": len(rows),
            "rows": rows,
        })
        
    except Exception as e:
        return err(f"Query failed: {str(e)}")


# =============================================================================
# Get Summary
# =============================================================================

def get_summary(
    cohort_id_or_name: str,
    include_samples: bool = True,
    samples_per_type: int = 3
) -> ToolResult:
    """Get a token-efficient summary of a cohort.
    
    Use this instead of load_cohort when you need context about a cohort
    without loading all entities (~500 tokens vs potentially 10K+).
    
    Args:
        cohort_id_or_name: Cohort name or UUID
        include_samples: Whether to include sample entities (default True)
        samples_per_type: Number of samples per entity type (1-10, default 3)
        
    Returns:
        ToolResult with entity counts, statistics, and optional samples
        
    Example:
        >>> result = get_summary("Demo Cohort", samples_per_type=2)
        >>> result.data["entity_counts"]
        {"patients": 100, "encounters": 250}
        >>> result.data["samples"]["patients"]
        [{"patient_id": "...", ...}, ...]
    """
    if not cohort_id_or_name or not cohort_id_or_name.strip():
        return err("Cohort name or ID is required")
    
    samples_per_type = max(1, min(samples_per_type, 10))
    
    try:
        manager = get_manager().get_read_manager()
        
        summary = manager.get_summary(
            cohort_id_or_name.strip(),
            include_samples=include_samples,
            samples_per_type=samples_per_type,
        )
        
        # Convert to dict for JSON serialization
        return ok(summary.to_dict())
        
    except ValueError as e:
        return err(str(e))
    except Exception as e:
        return err(f"Failed to get summary: {str(e)}")


# =============================================================================
# List Tables
# =============================================================================

def list_tables() -> ToolResult:
    """List all tables in the HealthSim database.
    
    Returns table names grouped by category:
    - Reference tables (population.*, network.*): Real-world data
    - Entity tables: Synthetic healthcare data
    - System tables: Cohort management
    
    Returns:
        ToolResult with categorized table names
        
    Example:
        >>> result = list_tables()
        >>> result.data["reference_tables"]
        ["population.places_county", "population.svi_tract", ...]
        >>> result.data["entity_tables"]
        ["patients", "members", "claims", ...]
    """
    try:
        conn = get_manager().get_read_connection()
        
        # Get all tables
        result = conn.execute("SHOW TABLES").fetchall()
        tables = [row[0] for row in result]
        
        # Try to get schema-qualified tables
        try:
            # Get population schema tables
            pop_tables = conn.execute(
                "SELECT table_name FROM information_schema.tables WHERE table_schema = 'population'"
            ).fetchall()
            population_tables = [f"population.{row[0]}" for row in pop_tables]
        except Exception:
            population_tables = []
        
        try:
            # Get network schema tables
            net_tables = conn.execute(
                "SELECT table_name FROM information_schema.tables WHERE table_schema = 'network'"
            ).fetchall()
            network_tables = [f"network.{row[0]}" for row in net_tables]
        except Exception:
            network_tables = []
        
        # Categorize main schema tables
        reference = population_tables + network_tables
        
        # Reference tables in main schema (legacy naming)
        reference += [t for t in tables if t.startswith("ref_")]
        
        # System tables
        system_names = {"cohorts", "cohort_entities", "cohort_tags", "schema_migrations"}
        system = [t for t in tables if t in system_names]
        
        # Entity tables (everything else)
        entity = [t for t in tables 
                  if t not in system_names 
                  and not t.startswith("ref_")]
        
        return ok({
            "reference_tables": sorted(set(reference)),
            "entity_tables": sorted(entity),
            "system_tables": sorted(system),
            "total": len(tables) + len(population_tables) + len(network_tables),
        })
        
    except Exception as e:
        return err(f"Failed to list tables: {str(e)}")
