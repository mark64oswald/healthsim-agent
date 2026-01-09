"""
HealthSim Agent - Database Package

Provides database connectivity and query helpers for:
- Reference data (NPPES, CDC PLACES, Census)
- Schema definitions for canonical tables
- Query result handling
"""

from healthsim_agent.db.connection import DatabaseConnection
from healthsim_agent.db.queries import QueryResult, ReferenceQueries
from healthsim_agent.db.schema import (
    SCHEMA_VERSION,
    ALL_DDL,
    get_canonical_tables,
    get_state_tables,
    get_system_tables,
)

__all__ = [
    "DatabaseConnection",
    "QueryResult", 
    "ReferenceQueries",
    "SCHEMA_VERSION",
    "ALL_DDL",
    "get_canonical_tables",
    "get_state_tables",
    "get_system_tables",
]
