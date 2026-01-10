"""Dimensional model package for analytics output.

Provides writers for persisting dimensional models to various targets
(DuckDB, Databricks), transformers for converting canonical entities
to dimensional tables, and generators for common dimensions like dim_date.
"""

from healthsim_agent.dimensional.generators import generate_dim_date
from healthsim_agent.dimensional.transformers import BaseDimensionalTransformer
from healthsim_agent.dimensional.writers import (
    BaseDimensionalWriter,
    DuckDBDimensionalWriter,
    WriterRegistry,
)

# Optional Databricks support
try:
    from healthsim_agent.dimensional.writers import DatabricksDimensionalWriter
except ImportError:
    DatabricksDimensionalWriter = None

__all__ = [
    # Writers
    "BaseDimensionalWriter",
    "DuckDBDimensionalWriter",
    "DatabricksDimensionalWriter",
    "WriterRegistry",
    # Transformers
    "BaseDimensionalTransformer",
    # Generators
    "generate_dim_date",
]
