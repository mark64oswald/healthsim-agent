"""Temporal utilities for HealthSim.

Provides date/time utilities, period management, and timeline infrastructure
for managing temporal relationships in synthetic data generation.
"""

from healthsim_agent.temporal.periods import Period, PeriodCollection, TimePeriod
from healthsim_agent.temporal.timeline import (
    EventDelay,
    EventStatus,
    Timeline,
    TimelineEvent,
)
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

__all__ = [
    # Periods
    "Period",
    "PeriodCollection",
    "TimePeriod",
    # Timeline
    "EventDelay",
    "EventStatus",
    "Timeline",
    "TimelineEvent",
    # Utils
    "calculate_age",
    "format_datetime_iso",
    "format_date_iso",
    "parse_datetime",
    "parse_date",
    "random_date_in_range",
    "random_datetime_in_range",
    "date_range",
    "days_between",
    "relative_date",
    "business_days_between",
    "next_business_day",
    "is_future_date",
]
