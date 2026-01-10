"""Date dimension generator with US federal holidays.

Ported from: healthsim-workspace/packages/core/src/healthsim/dimensional/generators/dim_date.py
"""

from __future__ import annotations

from datetime import date, timedelta

import pandas as pd


def _parse_date(d: str | date) -> date:
    """Parse a date string or return a date object."""
    if isinstance(d, date):
        return d
    return date.fromisoformat(d)


def _get_nth_weekday_of_month(year: int, month: int, weekday: int, n: int) -> date:
    """Get the nth occurrence of a weekday in a month."""
    first_day = date(year, month, 1)
    first_weekday = first_day.weekday()
    days_until_weekday = (weekday - first_weekday) % 7
    first_occurrence = first_day + timedelta(days=days_until_weekday)
    return first_occurrence + timedelta(weeks=n - 1)


def _get_last_weekday_of_month(year: int, month: int, weekday: int) -> date:
    """Get the last occurrence of a weekday in a month."""
    if month == 12:
        next_month = date(year + 1, 1, 1)
    else:
        next_month = date(year, month + 1, 1)

    last_day = next_month - timedelta(days=1)
    days_back = (last_day.weekday() - weekday) % 7
    return last_day - timedelta(days=days_back)


def _get_observed_date(holiday_date: date) -> date:
    """Get the observed date for a holiday."""
    weekday = holiday_date.weekday()
    if weekday == 5:  # Saturday
        return holiday_date - timedelta(days=1)
    elif weekday == 6:  # Sunday
        return holiday_date + timedelta(days=1)
    return holiday_date


def _get_us_federal_holidays(year: int) -> dict[date, str]:
    """Get all US federal holidays for a given year."""
    holidays: dict[date, str] = {}

    # New Year's Day
    new_years = date(year, 1, 1)
    holidays[_get_observed_date(new_years)] = "New Year's Day"

    # MLK Day (3rd Monday of January)
    holidays[_get_nth_weekday_of_month(year, 1, 0, 3)] = "Martin Luther King Jr. Day"

    # Presidents Day (3rd Monday of February)
    holidays[_get_nth_weekday_of_month(year, 2, 0, 3)] = "Presidents Day"

    # Memorial Day (Last Monday of May)
    holidays[_get_last_weekday_of_month(year, 5, 0)] = "Memorial Day"

    # Juneteenth
    juneteenth = date(year, 6, 19)
    holidays[_get_observed_date(juneteenth)] = "Juneteenth"

    # Independence Day
    independence_day = date(year, 7, 4)
    holidays[_get_observed_date(independence_day)] = "Independence Day"

    # Labor Day (1st Monday of September)
    holidays[_get_nth_weekday_of_month(year, 9, 0, 1)] = "Labor Day"

    # Columbus Day (2nd Monday of October)
    holidays[_get_nth_weekday_of_month(year, 10, 0, 2)] = "Columbus Day"

    # Veterans Day
    veterans_day = date(year, 11, 11)
    holidays[_get_observed_date(veterans_day)] = "Veterans Day"

    # Thanksgiving (4th Thursday of November)
    holidays[_get_nth_weekday_of_month(year, 11, 3, 4)] = "Thanksgiving"

    # Christmas Day
    christmas = date(year, 12, 25)
    holidays[_get_observed_date(christmas)] = "Christmas Day"

    return holidays


def generate_dim_date(
    start_date: str | date = "2020-01-01",
    end_date: str | date = "2030-12-31",
) -> pd.DataFrame:
    """Generate a date dimension table with US federal holidays."""
    start = _parse_date(start_date)
    end = _parse_date(end_date)

    if start > end:
        raise ValueError(f"start_date ({start}) must be <= end_date ({end})")

    # Pre-compute all holidays
    all_holidays: dict[date, str] = {}
    for year in range(start.year, end.year + 1):
        all_holidays.update(_get_us_federal_holidays(year))

    # Generate date range
    dates = []
    current = start
    while current <= end:
        dates.append(current)
        current += timedelta(days=1)

    # Build data rows
    rows = []
    for d in dates:
        if d.month == 12:
            next_month_first = date(d.year + 1, 1, 1)
        else:
            next_month_first = date(d.year, d.month + 1, 1)

        is_month_end = d == next_month_first - timedelta(days=1)

        quarter = (d.month - 1) // 3 + 1
        quarter_start_month = (quarter - 1) * 3 + 1
        quarter_end_month = quarter * 3

        is_quarter_start = d.month == quarter_start_month and d.day == 1

        if quarter_end_month == 12:
            quarter_end_date = date(d.year, 12, 31)
        else:
            quarter_end_date = date(d.year, quarter_end_month + 1, 1) - timedelta(days=1)
        is_quarter_end = d == quarter_end_date

        holiday_name = all_holidays.get(d)
        is_holiday = holiday_name is not None

        row = {
            "date_key": int(d.strftime("%Y%m%d")),
            "full_date": d,
            "year": d.year,
            "quarter": quarter,
            "month": d.month,
            "day": d.day,
            "day_of_week": d.isoweekday(),
            "day_of_year": d.timetuple().tm_yday,
            "week_of_year": d.isocalendar()[1],
            "day_name": d.strftime("%A"),
            "month_name": d.strftime("%B"),
            "quarter_name": f"Q{quarter}",
            "year_month": d.strftime("%Y-%m"),
            "year_quarter": f"{d.year}-Q{quarter}",
            "is_weekend": d.weekday() >= 5,
            "is_month_start": d.day == 1,
            "is_month_end": is_month_end,
            "is_quarter_start": is_quarter_start,
            "is_quarter_end": is_quarter_end,
            "is_year_start": d.month == 1 and d.day == 1,
            "is_year_end": d.month == 12 and d.day == 31,
            "is_us_federal_holiday": is_holiday,
            "holiday_name": holiday_name,
        }
        rows.append(row)

    return pd.DataFrame(rows)


__all__ = ["generate_dim_date"]
