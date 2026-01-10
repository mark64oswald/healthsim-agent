"""Dimensional model writers package.

Provides writers for persisting dimensional models to various targets.
"""

from healthsim_agent.dimensional.writers.base import BaseDimensionalWriter
from healthsim_agent.dimensional.writers.duckdb_writer import DuckDBDimensionalWriter
from healthsim_agent.dimensional.writers.registry import WriterRegistry

# Databricks is optional
try:
    from healthsim_agent.dimensional.writers.databricks_writer import DatabricksDimensionalWriter
except ImportError:
    DatabricksDimensionalWriter = None

__all__ = [
    "BaseDimensionalWriter",
    "DuckDBDimensionalWriter",
    "DatabricksDimensionalWriter",
    "WriterRegistry",
]
