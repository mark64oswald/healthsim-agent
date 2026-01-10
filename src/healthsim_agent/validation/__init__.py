"""Validation framework for HealthSim.

Provides base classes and utilities for validation throughout
the HealthSim ecosystem.
"""

from healthsim_agent.validation.framework import (
    BaseValidator,
    CompositeValidator,
    StructuralValidator,
    ValidationIssue,
    ValidationMessage,
    ValidationResult,
    ValidationSeverity,
    Validator,
)
from healthsim_agent.validation.structural import ReferentialIntegrityValidator
from healthsim_agent.validation.temporal import TemporalValidator

__all__ = [
    # Framework
    "BaseValidator",
    "Validator",
    "CompositeValidator",
    "StructuralValidator",
    "ValidationIssue",
    "ValidationMessage",
    "ValidationResult",
    "ValidationSeverity",
    # Structural
    "ReferentialIntegrityValidator",
    # Temporal
    "TemporalValidator",
]
