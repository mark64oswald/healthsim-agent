"""Tests for temporal utility functions.

Tests the date/time utility functions used throughout HealthSim.
"""

import random
from datetime import date, datetime, timedelta

import pytest

from healthsim_agent.temporal.utils import (
    business_days_between,
    calculate_age,
    date_range,
    days_between,
    format_date_iso,
    format_datetime_iso,
    is_future_date,
    next_business_day,
    parse_date,
    parse_datetime,
    random_date_in_range,
    random_datetime_in_range,
    relative_date,
)


class TestCalculateAge:
    """Tests for calculate_age function."""

    def test_exact_birthday_today(self):
        """Test age on exact birthday."""
        today = date.today()
        birth = date(today.year - 30, today.month, today.day)
        assert calculate_age(birth) == 30

    def test_birthday_not_yet_this_year(self):
        """Test age when birthday hasn't occurred yet this year."""
        as_of = date(2024, 3, 15)
        birth = date(1990, 6, 20)  # Birthday in June, as_of is March
        assert calculate_age(birth, as_of) == 33

    def test_birthday_already_passed_this_year(self):
        """Test age when birthday has passed this year."""
        as_of = date(2024, 8, 15)
        birth = date(1990, 6, 20)  # Birthday in June, as_of is August
        assert calculate_age(birth, as_of) == 34

    def test_custom_as_of_date(self):
        """Test with explicit as_of date."""
        birth = date(2000, 5, 10)
        as_of = date(2020, 5, 10)  # Exactly 20 years
        assert calculate_age(birth, as_of) == 20

    def test_day_before_birthday(self):
        """Test age the day before birthday."""
        birth = date(1985, 7, 20)
        as_of = date(2024, 7, 19)
        assert calculate_age(birth, as_of) == 38


class TestFormatFunctions:
    """Tests for format functions."""

    def test_format_datetime_iso(self):
        """Test datetime ISO formatting."""
        dt = datetime(2024, 6, 15, 14, 30, 45)
        result = format_datetime_iso(dt)
        assert result == "2024-06-15T14:30:45"

    def test_format_datetime_iso_with_microseconds(self):
        """Test datetime ISO formatting with microseconds."""
        dt = datetime(2024, 6, 15, 14, 30, 45, 123456)
        result = format_datetime_iso(dt)
        assert "2024-06-15T14:30:45" in result

    def test_format_date_iso(self):
        """Test date ISO formatting."""
        d = date(2024, 6, 15)
        result = format_date_iso(d)
        assert result == "2024-06-15"


class TestParseFunctions:
    """Tests for parse functions."""

    def test_parse_datetime_iso(self):
        """Test parsing ISO datetime string."""
        result = parse_datetime("2024-06-15T14:30:45")
        assert result.year == 2024
        assert result.month == 6
        assert result.day == 15
        assert result.hour == 14
        assert result.minute == 30

    def test_parse_datetime_with_timezone(self):
        """Test parsing datetime with timezone."""
        result = parse_datetime("2024-06-15T14:30:45Z")
        assert result.year == 2024
        assert result.month == 6

    def test_parse_date_iso(self):
        """Test parsing ISO date string."""
        result = parse_date("2024-06-15")
        assert result == date(2024, 6, 15)

    def test_parse_date_various_formats(self):
        """Test parsing various date formats."""
        # Month/day/year
        result = parse_date("06/15/2024")
        assert result == date(2024, 6, 15)


class TestRandomDateInRange:
    """Tests for random_date_in_range function."""

    def test_random_date_within_bounds(self):
        """Test that random date is within range."""
        start = date(2024, 1, 1)
        end = date(2024, 12, 31)
        rng = random.Random(42)

        for _ in range(100):
            result = random_date_in_range(start, end, rng)
            assert start <= result <= end

    def test_random_date_same_day(self):
        """Test with same start and end date."""
        same_day = date(2024, 6, 15)
        result = random_date_in_range(same_day, same_day)
        assert result == same_day

    def test_random_date_default_rng(self):
        """Test with default RNG."""
        start = date(2024, 1, 1)
        end = date(2024, 12, 31)
        result = random_date_in_range(start, end)
        assert start <= result <= end

    def test_random_date_reproducible_with_seed(self):
        """Test that same seed produces same results."""
        start = date(2024, 1, 1)
        end = date(2024, 12, 31)

        rng1 = random.Random(12345)
        rng2 = random.Random(12345)

        result1 = random_date_in_range(start, end, rng1)
        result2 = random_date_in_range(start, end, rng2)
        assert result1 == result2


class TestRandomDatetimeInRange:
    """Tests for random_datetime_in_range function."""

    def test_random_datetime_within_bounds(self):
        """Test that random datetime is within range."""
        start = datetime(2024, 1, 1, 0, 0, 0)
        end = datetime(2024, 12, 31, 23, 59, 59)
        rng = random.Random(42)

        for _ in range(100):
            result = random_datetime_in_range(start, end, rng)
            assert start <= result <= end

    def test_random_datetime_default_rng(self):
        """Test with default RNG."""
        start = datetime(2024, 1, 1, 0, 0, 0)
        end = datetime(2024, 12, 31, 23, 59, 59)
        result = random_datetime_in_range(start, end)
        assert start <= result <= end


class TestDateRange:
    """Tests for date_range function."""

    def test_basic_date_range(self):
        """Test basic daily date range."""
        start = date(2024, 1, 1)
        end = date(2024, 1, 5)
        result = date_range(start, end)

        assert len(result) == 5
        assert result[0] == date(2024, 1, 1)
        assert result[-1] == date(2024, 1, 5)

    def test_date_range_weekly_step(self):
        """Test date range with weekly step."""
        start = date(2024, 1, 1)
        end = date(2024, 1, 29)
        result = date_range(start, end, timedelta(days=7))

        assert len(result) == 5
        assert result[1] - result[0] == timedelta(days=7)

    def test_date_range_same_day(self):
        """Test range with same start and end."""
        same_day = date(2024, 6, 15)
        result = date_range(same_day, same_day)
        assert result == [same_day]


class TestDaysBetween:
    """Tests for days_between function."""

    def test_days_between_positive(self):
        """Test positive difference."""
        d1 = date(2024, 1, 1)
        d2 = date(2024, 1, 11)
        assert days_between(d1, d2) == 10

    def test_days_between_negative(self):
        """Test negative difference (d1 after d2)."""
        d1 = date(2024, 1, 11)
        d2 = date(2024, 1, 1)
        assert days_between(d1, d2) == -10

    def test_days_between_same_day(self):
        """Test same day difference."""
        d = date(2024, 6, 15)
        assert days_between(d, d) == 0


class TestRelativeDate:
    """Tests for relative_date function."""

    def test_days_after(self):
        """Test adding days."""
        base = date(2024, 1, 1)
        result = relative_date(base, days=10)
        assert result == date(2024, 1, 11)

    def test_days_before(self):
        """Test subtracting days."""
        base = date(2024, 1, 15)
        result = relative_date(base, days=10, direction="before")
        assert result == date(2024, 1, 5)

    def test_months_after(self):
        """Test adding months (approximate)."""
        base = date(2024, 1, 1)
        result = relative_date(base, months=1)
        # Approximately 30 days later
        assert result == date(2024, 1, 31)

    def test_years_after(self):
        """Test adding years."""
        base = date(2024, 1, 15)
        result = relative_date(base, years=2)
        assert result.year == 2026
        assert result.month == 1
        assert result.day == 15

    def test_years_before(self):
        """Test subtracting years."""
        base = date(2024, 6, 15)
        result = relative_date(base, years=5, direction="before")
        assert result.year == 2019

    def test_leap_year_feb29_handling(self):
        """Test handling of Feb 29 when moving years."""
        # Start on Feb 29 in a leap year
        base = date(2024, 2, 29)
        # Move to non-leap year
        result = relative_date(base, years=1)
        assert result.year == 2025
        assert result.month == 2
        assert result.day == 28  # Adjusted to Feb 28


class TestBusinessDaysBetween:
    """Tests for business_days_between function."""

    def test_full_week(self):
        """Test full week has 5 business days."""
        start = date(2024, 6, 10)  # Monday
        end = date(2024, 6, 14)  # Friday
        assert business_days_between(start, end) == 5

    def test_includes_weekend(self):
        """Test range spanning weekend."""
        start = date(2024, 6, 13)  # Thursday
        end = date(2024, 6, 17)  # Monday
        # Thu, Fri, (Sat, Sun skip), Mon = 3 business days
        assert business_days_between(start, end) == 3

    def test_weekend_only(self):
        """Test weekend-only range."""
        start = date(2024, 6, 15)  # Saturday
        end = date(2024, 6, 16)  # Sunday
        assert business_days_between(start, end) == 0

    def test_end_before_start(self):
        """Test when end is before start."""
        start = date(2024, 6, 15)
        end = date(2024, 6, 10)
        assert business_days_between(start, end) == 0

    def test_same_day_weekday(self):
        """Test same day (weekday)."""
        d = date(2024, 6, 13)  # Thursday
        assert business_days_between(d, d) == 1

    def test_same_day_weekend(self):
        """Test same day (weekend)."""
        d = date(2024, 6, 15)  # Saturday
        assert business_days_between(d, d) == 0


class TestNextBusinessDay:
    """Tests for next_business_day function."""

    def test_from_weekday(self):
        """Test next business day from a weekday."""
        thursday = date(2024, 6, 13)
        result = next_business_day(thursday)
        assert result == date(2024, 6, 14)  # Friday

    def test_from_friday(self):
        """Test next business day from Friday."""
        friday = date(2024, 6, 14)
        result = next_business_day(friday)
        assert result == date(2024, 6, 17)  # Monday

    def test_from_saturday(self):
        """Test next business day from Saturday."""
        saturday = date(2024, 6, 15)
        result = next_business_day(saturday)
        assert result == date(2024, 6, 17)  # Monday

    def test_from_sunday(self):
        """Test next business day from Sunday."""
        sunday = date(2024, 6, 16)
        result = next_business_day(sunday)
        assert result == date(2024, 6, 17)  # Monday


class TestIsFutureDate:
    """Tests for is_future_date function."""

    def test_future_date(self):
        """Test date in the future."""
        reference = date(2024, 6, 15)
        future = date(2024, 6, 20)
        assert is_future_date(future, reference) is True

    def test_past_date(self):
        """Test date in the past."""
        reference = date(2024, 6, 15)
        past = date(2024, 6, 10)
        assert is_future_date(past, reference) is False

    def test_same_date(self):
        """Test same date is not future."""
        d = date(2024, 6, 15)
        assert is_future_date(d, d) is False

    def test_default_reference(self):
        """Test with default reference (today)."""
        # Far future date
        future = date(2099, 12, 31)
        assert is_future_date(future) is True

        # Past date
        past = date(2000, 1, 1)
        assert is_future_date(past) is False
