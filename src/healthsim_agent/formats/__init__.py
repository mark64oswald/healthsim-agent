"""Format transformation and export utilities.

Provides base classes for transforming generated data into
various output formats (FHIR, HL7v2, X12, CSV, JSON, etc.).
"""

from healthsim_agent.formats.base import (
    BaseTransformer,
    BidirectionalTransformer,
    ChainedTransformer,
)

from healthsim_agent.formats.transformer import (
    Transformer,
    JsonTransformer,
    CsvTransformer,
)

from healthsim_agent.formats.utils import (
    format_date,
    format_datetime,
    safe_str,
    truncate,
    JSONExporter,
    CSVExporter,
)


__all__ = [
    # Base classes
    "BaseTransformer",
    "BidirectionalTransformer",
    "ChainedTransformer",
    # Transformer classes
    "Transformer",
    "JsonTransformer",
    "CsvTransformer",
    # Utility functions
    "format_date",
    "format_datetime",
    "safe_str",
    "truncate",
    # Exporter classes
    "JSONExporter",
    "CSVExporter",
]
