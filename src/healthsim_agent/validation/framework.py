"""Core validation framework.

Provides the base classes and data structures for validation throughout
the HealthSim ecosystem.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ValidationSeverity(str, Enum):
    """Severity level of a validation issue."""

    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ValidationIssue:
    """A single validation issue.

    Attributes:
        code: Unique identifier for this type of issue (e.g., "DATE_001")
        message: Human-readable description of the issue
        severity: Severity level of the issue
        field_path: Path to the field with the issue (e.g., "person.birth_date")
        context: Additional context about the issue
    """

    code: str
    message: str
    severity: ValidationSeverity
    field_path: str | None = None
    context: dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        """Return string representation of the issue."""
        location = f" at {self.field_path}" if self.field_path else ""
        return f"[{self.severity.value.upper()}] {self.code}{location}: {self.message}"


@dataclass
class ValidationResult:
    """Result of a validation operation.

    Collects all validation issues found during validation and provides
    convenience methods for checking validity and filtering issues.
    """

    valid: bool = True
    issues: list[ValidationIssue] = field(default_factory=list)

    @property
    def errors(self) -> list[ValidationIssue]:
        """Get all ERROR severity issues."""
        return [i for i in self.issues if i.severity == ValidationSeverity.ERROR]

    @property
    def warnings(self) -> list[ValidationIssue]:
        """Get all WARNING severity issues."""
        return [i for i in self.issues if i.severity == ValidationSeverity.WARNING]

    @property
    def infos(self) -> list[ValidationIssue]:
        """Get all INFO severity issues."""
        return [i for i in self.issues if i.severity == ValidationSeverity.INFO]

    def add_issue(
        self,
        code: str,
        message: str,
        severity: ValidationSeverity,
        field_path: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> None:
        """Add a validation issue."""
        issue = ValidationIssue(
            code=code,
            message=message,
            severity=severity,
            field_path=field_path,
            context=context or {},
        )
        self.issues.append(issue)

        if severity == ValidationSeverity.ERROR:
            self.valid = False

    def merge(self, other: "ValidationResult") -> None:
        """Merge another validation result into this one."""
        self.issues.extend(other.issues)
        if not other.valid:
            self.valid = False

    def __str__(self) -> str:
        """Return string representation of the result."""
        status = "VALID" if self.valid else "INVALID"
        err_count = len(self.errors)
        warn_count = len(self.warnings)
        info_count = len(self.infos)
        counts = f"({err_count} errors, {warn_count} warnings, {info_count} info)"
        return f"ValidationResult: {status} {counts}"


class BaseValidator(ABC):
    """Abstract base class for validators."""

    @abstractmethod
    def validate(self, *args: Any, **kwargs: Any) -> ValidationResult:
        """Perform validation and return results."""
        ...

    def __call__(self, *args: Any, **kwargs: Any) -> ValidationResult:
        """Allow validators to be called directly."""
        return self.validate(*args, **kwargs)


# Aliases for compatibility
Validator = BaseValidator
ValidationMessage = ValidationIssue


class CompositeValidator(BaseValidator):
    """Validator that combines multiple validators."""

    def __init__(self, validators: list[BaseValidator] | None = None):
        self.validators = validators or []

    def add(self, validator: BaseValidator) -> None:
        """Add a validator to the composite."""
        self.validators.append(validator)

    def validate(self, *args: Any, **kwargs: Any) -> ValidationResult:
        """Run all validators and merge results."""
        result = ValidationResult()
        for validator in self.validators:
            result.merge(validator.validate(*args, **kwargs))
        return result


class StructuralValidator(BaseValidator):
    """Validator for structural/schema requirements."""

    def __init__(self, required_fields: list[str] | None = None):
        self.required_fields = required_fields or []

    def validate(self, entity: Any) -> ValidationResult:
        """Validate structural requirements."""
        result = ValidationResult()

        for field_name in self.required_fields:
            if not hasattr(entity, field_name):
                result.add_issue(
                    code="STRUCT_001",
                    message="Required field is missing",
                    severity=ValidationSeverity.ERROR,
                    field_path=field_name,
                )
            else:
                value = getattr(entity, field_name)
                if value is None or value == "":
                    result.add_issue(
                        code="STRUCT_002",
                        message="Required field cannot be empty",
                        severity=ValidationSeverity.ERROR,
                        field_path=field_name,
                    )

        return result
