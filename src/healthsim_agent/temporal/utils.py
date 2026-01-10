"""Date and time utility functions.

Provides common date/time operations used throughout HealthSim.
"""

import random
from datetime import date, datetime, timedelta

from dateutil.parser import parse as dateutil_parse


def calculate_age(birth_date: date, as_of: date | None = None) -> int:
    """Calculate age in years from a birth date.

    Args:
        birth_date: Date of birth
        as_of: Reference date (defaults to today)

    Returns:
        Age in complete years
    """
    if as_of is None:
        as_of = date.today()

    age = as_of.year - birth_date.year

    # Adjust if birthday hasn't occurred yet this year
    if (as_of.month, as_of.day) < (birth_date.month, birth_date.day):
        age -= 1

    return age


def format_datetime_iso(dt: datetime) -> str:
    """Format datetime as ISO 8601 string."""
    return dt.isoformat()


def format_date_iso(d: date) -> str:
    """Format date as ISO 8601 string (YYYY-MM-DD)."""
    return d.isoformat()


def parse_datetime(s: str) -> datetime:
    """Parse a datetime string in various formats using dateutil."""
    return dateutil_parse(s)


def parse_date(s: str) -> date:
    """Parse a date string in various formats."""
    return dateutil_parse(s).date()


def random_date_in_range(
    start: date,
    end: date,
    rng: random.Random | None = None,
) -> date:
    """Generate a random date within a range (inclusive)."""
    if rng is None:
        rng = random.Random()

    delta = end - start
    random_days = rng.randint(0, delta.days)
    return start + timedelta(days=random_days)


def random_datetime_in_range(
    start: datetime,
    end: datetime,
    rng: random.Random | None = None,
) -> datetime:
    """Generate a random datetime within a range (inclusive)."""
    if rng is None:
        rng = random.Random()

    delta = end - start
    random_seconds = rng.randint(0, int(delta.total_seconds()))
    return start + timedelta(seconds=random_seconds)


def date_range(
    start: date,
    end: date,
    step: timedelta = timedelta(days=1),
) -> list[date]:
    """Generate a list of dates in a range (inclusive)."""
    dates = []
    current = start
    while current <= end:
        dates.append(current)
        current += step
    return dates


def days_between(d1: date, d2: date) -> int:
    """Calculate the number of days between two dates."""
    return (d2 - d1).days


def relative_date(
    base: date, years: int = 0, months: int = 0, days: int = 0, direction: str = "after"
) -> date:
    """Calculate a date relative to a base date."""
    multiplier = 1 if direction == "after" else -1

    # Handle days simply
    result = base + timedelta(days=days * multiplier)

    # Handle months (approximate as 30 days)
    result += timedelta(days=months * 30 * multiplier)

    # Handle years
    try:
        result = result.replace(year=result.year + (years * multiplier))
    except ValueError:
        # Handle Feb 29 edge case
        result = result.replace(month=2, day=28, year=result.year + (years * multiplier))

    return result


def business_days_between(start: date, end: date) -> int:
    """Count business days (Mon-Fri) between two dates (inclusive)."""
    if end < start:
        return 0
    count = 0
    current = start
    while current <= end:
        if current.weekday() < 5:  # Monday = 0, Friday = 4
            count += 1
        current += timedelta(days=1)
    return count


def next_business_day(from_date: date) -> date:
    """Get the next business day (Mon-Fri) from a date."""
    current = from_date + timedelta(days=1)
    while current.weekday() >= 5:  # Skip weekends
        current += timedelta(days=1)
    return current


def is_future_date(check_date: date, reference: date | None = None) -> bool:
    """Check if a date is in the future relative to reference (default: today)."""
    ref = reference or date.today()
    return check_date > ref
