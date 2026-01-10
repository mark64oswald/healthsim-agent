"""Temporal validation utilities.

Provides validators for date and time consistency checks.
"""

from datetime import date, datetime, timedelta
from typing import Any

from healthsim_agent.validation.framework import (
    BaseValidator,
    ValidationResult,
    ValidationSeverity,
)


class TemporalValidator(BaseValidator):
    """Validator for temporal consistency.

    Checks that dates and times are valid and consistent with each other.
    """

    def validate(self, *args: Any, **kwargs: Any) -> ValidationResult:
        """Generic validate method - use specific methods instead."""
        return ValidationResult()

    def validate_date_not_future(
        self,
        d: date | datetime,
        field_name: str,
        as_of: date | datetime | None = None,
    ) -> ValidationResult:
        """Validate that a date is not in the future."""
        result = ValidationResult()

        if as_of is None:
            as_of = datetime.now() if isinstance(d, datetime) else date.today()

        d_date = d.date() if isinstance(d, datetime) else d
        as_of_date = as_of.date() if isinstance(as_of, datetime) else as_of

        if d_date > as_of_date:
            result.add_issue(
                code="TEMP_001",
                message=f"{field_name} cannot be in the future",
                severity=ValidationSeverity.ERROR,
                field_path=field_name,
                context={"value": str(d), "as_of": str(as_of)},
            )

        return result

    def validate_date_order(
        self,
        earlier: date | datetime | None,
        later: date | datetime | None,
        earlier_field: str,
        later_field: str,
        allow_equal: bool = True,
    ) -> ValidationResult:
        """Validate that one date comes before another."""
        result = ValidationResult()

        if earlier is None or later is None:
            return result

        if isinstance(earlier, date) and not isinstance(earlier, datetime):
            earlier = datetime.combine(earlier, datetime.min.time())
        if isinstance(later, date) and not isinstance(later, datetime):
            later = datetime.combine(later, datetime.min.time())

        if allow_equal:
            if earlier > later:
                result.add_issue(
                    code="TEMP_002",
                    message=f"{earlier_field} must be on or before {later_field}",
                    severity=ValidationSeverity.ERROR,
                    field_path=later_field,
                    context={earlier_field: str(earlier), later_field: str(later)},
                )
        else:
            if earlier >= later:
                result.add_issue(
                    code="TEMP_002",
                    message=f"{earlier_field} must be before {later_field}",
                    severity=ValidationSeverity.ERROR,
                    field_path=later_field,
                    context={earlier_field: str(earlier), later_field: str(later)},
                )

        return result

    def validate_duration(
        self,
        start: datetime,
        end: datetime,
        max_duration: timedelta | None = None,
        min_duration: timedelta | None = None,
        field_name: str = "duration",
    ) -> ValidationResult:
        """Validate that a duration is within acceptable bounds."""
        result = ValidationResult()
        duration = end - start

        if duration < timedelta(0):
            result.add_issue(
                code="TEMP_003",
                message=f"{field_name} cannot be negative",
                severity=ValidationSeverity.ERROR,
                field_path=field_name,
                context={"start": str(start), "end": str(end)},
            )
            return result

        if max_duration and duration > max_duration:
            result.add_issue(
                code="TEMP_004",
                message=f"{field_name} exceeds maximum allowed ({max_duration})",
                severity=ValidationSeverity.WARNING,
                field_path=field_name,
                context={"actual": str(duration), "maximum": str(max_duration)},
            )

        if min_duration and duration < min_duration:
            result.add_issue(
                code="TEMP_005",
                message=f"{field_name} is below minimum required ({min_duration})",
                severity=ValidationSeverity.WARNING,
                field_path=field_name,
                context={"actual": str(duration), "minimum": str(min_duration)},
            )

        return result

    def validate_age_range(
        self,
        birth_date: date,
        min_age: int = 0,
        max_age: int = 150,
        as_of: date | None = None,
    ) -> ValidationResult:
        """Validate that a person's age is within bounds."""
        result = ValidationResult()

        if as_of is None:
            as_of = date.today()

        age = as_of.year - birth_date.year
        if (as_of.month, as_of.day) < (birth_date.month, birth_date.day):
            age -= 1

        if age < min_age:
            result.add_issue(
                code="TEMP_006",
                message=f"Age {age} is below minimum {min_age}",
                severity=ValidationSeverity.ERROR,
                field_path="birth_date",
                context={"age": age, "min_age": min_age},
            )

        if age > max_age:
            result.add_issue(
                code="TEMP_007",
                message=f"Age {age} exceeds maximum {max_age}",
                severity=ValidationSeverity.WARNING,
                field_path="birth_date",
                context={"age": age, "max_age": max_age},
            )

        return result
