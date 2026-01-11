"""Tests for temporal validation utilities.

Tests cover:
- TemporalValidator
- Date not in future validation
- Date order validation
- Duration validation
- Age range validation
"""

import pytest
from datetime import date, datetime, timedelta

from healthsim_agent.validation.temporal import TemporalValidator
from healthsim_agent.validation.framework import ValidationSeverity


class TestTemporalValidator:
    """Tests for TemporalValidator class."""

    @pytest.fixture
    def validator(self):
        """Create validator instance."""
        return TemporalValidator()

    def test_generic_validate_returns_valid(self, validator):
        """Test that generic validate returns valid result."""
        result = validator.validate()
        assert result.valid is True


class TestValidateDateNotFuture:
    """Tests for validate_date_not_future method."""

    @pytest.fixture
    def validator(self):
        return TemporalValidator()

    def test_past_date_valid(self, validator):
        """Test validation passes for past date."""
        past_date = date(2020, 1, 1)
        result = validator.validate_date_not_future(past_date, "birth_date")
        assert result.valid is True

    def test_today_valid(self, validator):
        """Test validation passes for today's date."""
        today = date.today()
        result = validator.validate_date_not_future(today, "event_date")
        assert result.valid is True

    def test_future_date_invalid(self, validator):
        """Test validation fails for future date."""
        future_date = date.today() + timedelta(days=365)
        result = validator.validate_date_not_future(future_date, "event_date")
        assert result.valid is False
        assert any("TEMP_001" in i.code for i in result.issues)

    def test_datetime_past_valid(self, validator):
        """Test validation passes for past datetime."""
        past_dt = datetime(2020, 1, 1, 10, 30, 0)
        result = validator.validate_date_not_future(past_dt, "event_time")
        assert result.valid is True

    def test_datetime_future_invalid(self, validator):
        """Test validation fails for future datetime."""
        future_dt = datetime.now() + timedelta(days=30)
        result = validator.validate_date_not_future(future_dt, "event_time")
        assert result.valid is False

    def test_custom_as_of_date(self, validator):
        """Test validation with custom as_of date."""
        test_date = date(2023, 6, 15)
        as_of = date(2023, 12, 31)
        result = validator.validate_date_not_future(test_date, "event_date", as_of=as_of)
        assert result.valid is True

    def test_future_relative_to_as_of(self, validator):
        """Test validation fails when date is after as_of."""
        test_date = date(2024, 1, 1)
        as_of = date(2023, 12, 31)
        result = validator.validate_date_not_future(test_date, "event_date", as_of=as_of)
        assert result.valid is False


class TestValidateDateOrder:
    """Tests for validate_date_order method."""

    @pytest.fixture
    def validator(self):
        return TemporalValidator()

    def test_correct_order_valid(self, validator):
        """Test validation passes when earlier date is before later."""
        earlier = date(2020, 1, 1)
        later = date(2020, 12, 31)
        result = validator.validate_date_order(
            earlier, later, "start_date", "end_date"
        )
        assert result.valid is True

    def test_same_date_valid_by_default(self, validator):
        """Test validation passes when dates are equal (allow_equal=True)."""
        same_date = date(2020, 6, 15)
        result = validator.validate_date_order(
            same_date, same_date, "start_date", "end_date"
        )
        assert result.valid is True

    def test_same_date_invalid_when_not_allowed(self, validator):
        """Test validation fails when dates equal and allow_equal=False."""
        same_date = date(2020, 6, 15)
        result = validator.validate_date_order(
            same_date, same_date, "start_date", "end_date",
            allow_equal=False
        )
        assert result.valid is False
        assert any("TEMP_002" in i.code for i in result.issues)

    def test_wrong_order_invalid(self, validator):
        """Test validation fails when earlier date is after later."""
        earlier = date(2020, 12, 31)
        later = date(2020, 1, 1)
        result = validator.validate_date_order(
            earlier, later, "start_date", "end_date"
        )
        assert result.valid is False

    def test_none_earlier_valid(self, validator):
        """Test validation passes when earlier date is None."""
        later = date(2020, 12, 31)
        result = validator.validate_date_order(
            None, later, "start_date", "end_date"
        )
        assert result.valid is True

    def test_none_later_valid(self, validator):
        """Test validation passes when later date is None."""
        earlier = date(2020, 1, 1)
        result = validator.validate_date_order(
            earlier, None, "start_date", "end_date"
        )
        assert result.valid is True

    def test_datetime_order(self, validator):
        """Test validation with datetime objects."""
        earlier = datetime(2020, 6, 15, 10, 0, 0)
        later = datetime(2020, 6, 15, 14, 30, 0)
        result = validator.validate_date_order(
            earlier, later, "start_time", "end_time"
        )
        assert result.valid is True

    def test_mixed_date_datetime(self, validator):
        """Test validation with mixed date and datetime."""
        earlier = date(2020, 6, 14)
        later = datetime(2020, 6, 15, 14, 30, 0)
        result = validator.validate_date_order(
            earlier, later, "start_date", "end_time"
        )
        assert result.valid is True


class TestValidateDuration:
    """Tests for validate_duration method."""

    @pytest.fixture
    def validator(self):
        return TemporalValidator()

    def test_valid_duration(self, validator):
        """Test validation passes for valid duration."""
        start = datetime(2020, 6, 15, 10, 0, 0)
        end = datetime(2020, 6, 15, 12, 0, 0)
        result = validator.validate_duration(start, end)
        assert result.valid is True

    def test_negative_duration_invalid(self, validator):
        """Test validation fails for negative duration."""
        start = datetime(2020, 6, 15, 14, 0, 0)
        end = datetime(2020, 6, 15, 10, 0, 0)
        result = validator.validate_duration(start, end)
        assert result.valid is False
        assert any("TEMP_003" in i.code for i in result.issues)

    def test_max_duration_exceeded_warning(self, validator):
        """Test validation warns when max duration exceeded."""
        start = datetime(2020, 6, 15, 10, 0, 0)
        end = datetime(2020, 6, 15, 20, 0, 0)  # 10 hours
        max_duration = timedelta(hours=8)
        result = validator.validate_duration(start, end, max_duration=max_duration)
        assert result.valid is True  # Warnings don't make invalid
        assert any("TEMP_004" in i.code for i in result.issues)
        assert result.issues[0].severity == ValidationSeverity.WARNING

    def test_min_duration_not_met_warning(self, validator):
        """Test validation warns when min duration not met."""
        start = datetime(2020, 6, 15, 10, 0, 0)
        end = datetime(2020, 6, 15, 10, 15, 0)  # 15 minutes
        min_duration = timedelta(hours=1)
        result = validator.validate_duration(start, end, min_duration=min_duration)
        assert result.valid is True
        assert any("TEMP_005" in i.code for i in result.issues)

    def test_within_bounds(self, validator):
        """Test validation passes when within bounds."""
        start = datetime(2020, 6, 15, 10, 0, 0)
        end = datetime(2020, 6, 15, 14, 0, 0)  # 4 hours
        result = validator.validate_duration(
            start, end,
            min_duration=timedelta(hours=1),
            max_duration=timedelta(hours=8)
        )
        assert result.valid is True
        assert len(result.issues) == 0

    def test_custom_field_name(self, validator):
        """Test validation uses custom field name."""
        start = datetime(2020, 6, 15, 10, 0, 0)
        end = datetime(2020, 6, 15, 8, 0, 0)
        result = validator.validate_duration(start, end, field_name="visit_duration")
        assert any(i.field_path == "visit_duration" for i in result.issues)


class TestValidateAgeRange:
    """Tests for validate_age_range method."""

    @pytest.fixture
    def validator(self):
        return TemporalValidator()

    def test_valid_age(self, validator):
        """Test validation passes for valid age."""
        # Person born 30 years ago
        birth_date = date.today() - timedelta(days=30*365)
        result = validator.validate_age_range(birth_date)
        assert result.valid is True

    def test_below_min_age_invalid(self, validator):
        """Test validation fails when below min age."""
        # Person born 5 years ago
        birth_date = date.today() - timedelta(days=5*365)
        result = validator.validate_age_range(birth_date, min_age=18)
        assert result.valid is False
        assert any("TEMP_006" in i.code for i in result.issues)

    def test_above_max_age_warning(self, validator):
        """Test validation warns when above max age."""
        # Very old person - 200 years
        birth_date = date(1824, 1, 1)
        as_of = date(2024, 1, 1)
        result = validator.validate_age_range(birth_date, max_age=150, as_of=as_of)
        assert result.valid is True  # Warning doesn't make invalid
        assert any("TEMP_007" in i.code for i in result.issues)
        assert result.issues[0].severity == ValidationSeverity.WARNING

    def test_negative_age_invalid(self, validator):
        """Test validation fails for future birth date (negative age)."""
        future_birth = date.today() + timedelta(days=100)
        result = validator.validate_age_range(future_birth)
        assert result.valid is False

    def test_custom_min_max_age(self, validator):
        """Test validation with custom min/max age."""
        birth_date = date(1990, 6, 15)
        as_of = date(2024, 1, 1)  # Person is ~33
        result = validator.validate_age_range(
            birth_date,
            min_age=21,
            max_age=65,
            as_of=as_of
        )
        assert result.valid is True

    def test_age_calculation_considers_month_day(self, validator):
        """Test that age calculation considers birthday not yet occurred."""
        # Born on July 15, checking on January 1
        birth_date = date(2000, 7, 15)
        as_of = date(2024, 1, 1)
        result = validator.validate_age_range(birth_date, min_age=24, as_of=as_of)
        # Person is only 23 (birthday hasn't happened yet)
        assert result.valid is False

    def test_exact_boundary_age(self, validator):
        """Test validation at exact age boundary."""
        # Born exactly 18 years ago today (accounting for leap years)
        today = date.today()
        try:
            birth_date = today.replace(year=today.year - 18)
        except ValueError:
            # Handle Feb 29 edge case
            birth_date = today.replace(year=today.year - 18, day=28)
        result = validator.validate_age_range(birth_date, min_age=18)
        # Should pass (exactly 18 years old)
        assert result.valid is True


class TestIntegration:
    """Integration tests for temporal validation."""

    def test_validate_encounter_timeline(self):
        """Test validating a healthcare encounter timeline."""
        validator = TemporalValidator()
        
        # Encounter data
        admission = datetime(2024, 1, 10, 8, 0, 0)
        first_procedure = datetime(2024, 1, 10, 10, 30, 0)
        second_procedure = datetime(2024, 1, 11, 14, 0, 0)
        discharge = datetime(2024, 1, 12, 11, 0, 0)
        
        # Validate timeline order
        result1 = validator.validate_date_order(
            admission, first_procedure, "admission", "first_procedure"
        )
        result2 = validator.validate_date_order(
            first_procedure, second_procedure, "first_procedure", "second_procedure"
        )
        result3 = validator.validate_date_order(
            second_procedure, discharge, "second_procedure", "discharge"
        )
        
        # Validate stay duration
        result4 = validator.validate_duration(
            admission, discharge,
            min_duration=timedelta(hours=1),
            max_duration=timedelta(days=30)
        )
        
        assert all([result1.valid, result2.valid, result3.valid, result4.valid])

    def test_validate_clinical_trial_eligibility(self):
        """Test validating clinical trial eligibility dates."""
        validator = TemporalValidator()
        
        # Enrollment criteria: ages 18-65
        birth_date = date(1985, 3, 20)
        enrollment_date = date(2024, 6, 15)
        
        result = validator.validate_age_range(
            birth_date,
            min_age=18,
            max_age=65,
            as_of=enrollment_date
        )
        assert result.valid is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
