"""
Tests for temporal/periods.py - Date period and range management.
"""
import pytest
from datetime import date, datetime, timedelta

from healthsim_agent.temporal.periods import (
    Period,
    PeriodCollection,
    TimePeriod,
)


class TestPeriod:
    """Tests for the Period dataclass."""
    
    def test_create_period_with_end_date(self):
        """Create period with both start and end dates."""
        period = Period(
            start_date=date(2024, 1, 1),
            end_date=date(2024, 12, 31)
        )
        
        assert period.start_date == date(2024, 1, 1)
        assert period.end_date == date(2024, 12, 31)
        assert not period.is_open
    
    def test_create_open_ended_period(self):
        """Create period without end date."""
        period = Period(start_date=date(2024, 1, 1))
        
        assert period.end_date is None
        assert period.is_open
    
    def test_period_with_label(self):
        """Period can have a label."""
        period = Period(
            start_date=date(2024, 1, 1),
            end_date=date(2024, 6, 30),
            label="Q1-Q2 Coverage"
        )
        
        assert period.label == "Q1-Q2 Coverage"
    
    def test_duration_days_bounded(self):
        """Duration calculated for bounded period (inclusive)."""
        period = Period(
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 10)
        )
        
        # Inclusive: Jan 1-10 is 10 days
        assert period.duration_days == 10
    
    def test_duration_days_open_ended(self):
        """Duration is None for open-ended period."""
        period = Period(start_date=date(2024, 1, 1))
        
        assert period.duration_days is None
    
    def test_contains_date_within(self):
        """Date within period returns True."""
        period = Period(
            start_date=date(2024, 1, 1),
            end_date=date(2024, 12, 31)
        )
        
        assert period.contains(date(2024, 6, 15))
    
    def test_contains_date_at_boundaries(self):
        """Dates at boundaries are included."""
        period = Period(
            start_date=date(2024, 1, 1),
            end_date=date(2024, 12, 31)
        )
        
        assert period.contains(date(2024, 1, 1))  # Start
        assert period.contains(date(2024, 12, 31))  # End
    
    def test_contains_date_before(self):
        """Date before period returns False."""
        period = Period(
            start_date=date(2024, 1, 1),
            end_date=date(2024, 12, 31)
        )
        
        assert not period.contains(date(2023, 12, 31))
    
    def test_contains_date_after(self):
        """Date after period returns False."""
        period = Period(
            start_date=date(2024, 1, 1),
            end_date=date(2024, 12, 31)
        )
        
        assert not period.contains(date(2025, 1, 1))
    
    def test_contains_open_ended(self):
        """Open-ended period contains any date after start."""
        period = Period(start_date=date(2024, 1, 1))
        
        assert period.contains(date(2024, 1, 1))
        assert period.contains(date(2030, 12, 31))
        assert not period.contains(date(2023, 12, 31))


class TestPeriodOverlaps:
    """Tests for Period overlap detection."""
    
    def test_overlapping_periods(self):
        """Overlapping periods detected."""
        p1 = Period(start_date=date(2024, 1, 1), end_date=date(2024, 6, 30))
        p2 = Period(start_date=date(2024, 4, 1), end_date=date(2024, 9, 30))
        
        assert p1.overlaps(p2)
        assert p2.overlaps(p1)
    
    def test_non_overlapping_periods(self):
        """Non-overlapping periods not detected as overlapping."""
        p1 = Period(start_date=date(2024, 1, 1), end_date=date(2024, 3, 31))
        p2 = Period(start_date=date(2024, 7, 1), end_date=date(2024, 9, 30))
        
        assert not p1.overlaps(p2)
        assert not p2.overlaps(p1)
    
    def test_adjacent_periods_not_overlapping(self):
        """Adjacent periods don't overlap."""
        p1 = Period(start_date=date(2024, 1, 1), end_date=date(2024, 3, 31))
        p2 = Period(start_date=date(2024, 4, 1), end_date=date(2024, 6, 30))
        
        assert not p1.overlaps(p2)
    
    def test_open_ended_overlaps_bounded(self):
        """Open-ended period overlaps bounded after start."""
        p1 = Period(start_date=date(2024, 1, 1))  # Open-ended
        p2 = Period(start_date=date(2024, 4, 1), end_date=date(2024, 6, 30))
        
        assert p1.overlaps(p2)


class TestPeriodAdjacent:
    """Tests for Period adjacency detection."""
    
    def test_adjacent_periods(self):
        """Adjacent periods detected."""
        p1 = Period(start_date=date(2024, 1, 1), end_date=date(2024, 3, 31))
        p2 = Period(start_date=date(2024, 4, 1), end_date=date(2024, 6, 30))
        
        assert p1.adjacent_to(p2)
    
    def test_not_adjacent_with_gap(self):
        """Periods with gap not adjacent."""
        p1 = Period(start_date=date(2024, 1, 1), end_date=date(2024, 3, 30))
        p2 = Period(start_date=date(2024, 4, 1), end_date=date(2024, 6, 30))
        
        assert not p1.adjacent_to(p2)
    
    def test_open_ended_not_adjacent(self):
        """Open-ended periods cannot be adjacent."""
        p1 = Period(start_date=date(2024, 1, 1))  # Open-ended
        p2 = Period(start_date=date(2024, 4, 1), end_date=date(2024, 6, 30))
        
        assert not p1.adjacent_to(p2)


class TestPeriodMerge:
    """Tests for Period merging."""
    
    def test_merge_overlapping(self):
        """Merge overlapping periods."""
        p1 = Period(start_date=date(2024, 1, 1), end_date=date(2024, 6, 30))
        p2 = Period(start_date=date(2024, 4, 1), end_date=date(2024, 9, 30))
        
        merged = p1.merge_with(p2)
        
        assert merged.start_date == date(2024, 1, 1)
        assert merged.end_date == date(2024, 9, 30)
    
    def test_merge_adjacent(self):
        """Merge adjacent periods."""
        p1 = Period(start_date=date(2024, 1, 1), end_date=date(2024, 3, 31))
        p2 = Period(start_date=date(2024, 4, 1), end_date=date(2024, 6, 30))
        
        merged = p1.merge_with(p2)
        
        assert merged.start_date == date(2024, 1, 1)
        assert merged.end_date == date(2024, 6, 30)
    
    def test_merge_with_open_ended(self):
        """Merging with open-ended period results in open-ended."""
        p1 = Period(start_date=date(2024, 1, 1), end_date=date(2024, 6, 30))
        p2 = Period(start_date=date(2024, 4, 1))  # Open-ended
        
        merged = p1.merge_with(p2)
        
        assert merged.start_date == date(2024, 1, 1)
        assert merged.end_date is None


class TestPeriodIterDates:
    """Tests for Period date iteration."""
    
    def test_iter_dates(self):
        """Iterate through dates in period."""
        period = Period(
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 5)
        )
        
        dates = list(period.iter_dates())
        
        assert len(dates) == 5
        assert dates[0] == date(2024, 1, 1)
        assert dates[-1] == date(2024, 1, 5)
    
    def test_iter_open_ended_raises(self):
        """Iterating open-ended period raises error."""
        period = Period(start_date=date(2024, 1, 1))
        
        with pytest.raises(ValueError, match="open-ended"):
            list(period.iter_dates())


class TestPeriodCollection:
    """Tests for PeriodCollection."""
    
    def test_add_period(self):
        """Add period to collection."""
        collection = PeriodCollection()
        period = Period(start_date=date(2024, 1, 1), end_date=date(2024, 3, 31))
        
        collection.add(period)
        
        assert len(collection.periods) == 1
    
    def test_add_sorts_by_start(self):
        """Periods sorted by start date when added."""
        collection = PeriodCollection()
        collection.add(Period(start_date=date(2024, 7, 1), end_date=date(2024, 9, 30)))
        collection.add(Period(start_date=date(2024, 1, 1), end_date=date(2024, 3, 31)))
        
        assert collection.periods[0].start_date == date(2024, 1, 1)
        assert collection.periods[1].start_date == date(2024, 7, 1)
    
    def test_find_gaps(self):
        """Find gaps between periods."""
        collection = PeriodCollection()
        collection.add(Period(start_date=date(2024, 1, 1), end_date=date(2024, 3, 31)))
        collection.add(Period(start_date=date(2024, 7, 1), end_date=date(2024, 9, 30)))
        
        gaps = collection.find_gaps()
        
        assert len(gaps) == 1
        assert gaps[0].start_date == date(2024, 4, 1)
        assert gaps[0].end_date == date(2024, 6, 30)
        assert gaps[0].label == "gap"
    
    def test_find_gaps_no_gaps(self):
        """No gaps when periods are adjacent."""
        collection = PeriodCollection()
        collection.add(Period(start_date=date(2024, 1, 1), end_date=date(2024, 3, 31)))
        collection.add(Period(start_date=date(2024, 4, 1), end_date=date(2024, 6, 30)))
        
        gaps = collection.find_gaps()
        
        assert len(gaps) == 0
    
    def test_find_gaps_single_period(self):
        """No gaps with single period."""
        collection = PeriodCollection()
        collection.add(Period(start_date=date(2024, 1, 1), end_date=date(2024, 3, 31)))
        
        gaps = collection.find_gaps()
        
        assert len(gaps) == 0
    
    def test_find_overlaps(self):
        """Find overlapping periods."""
        collection = PeriodCollection()
        collection.add(Period(start_date=date(2024, 1, 1), end_date=date(2024, 6, 30)))
        collection.add(Period(start_date=date(2024, 4, 1), end_date=date(2024, 9, 30)))
        
        overlaps = collection.find_overlaps()
        
        assert len(overlaps) == 1
    
    def test_consolidate(self):
        """Consolidate overlapping and adjacent periods."""
        collection = PeriodCollection()
        collection.add(Period(start_date=date(2024, 1, 1), end_date=date(2024, 3, 31)))
        collection.add(Period(start_date=date(2024, 4, 1), end_date=date(2024, 6, 30)))  # Adjacent
        collection.add(Period(start_date=date(2024, 10, 1), end_date=date(2024, 12, 31)))  # Gap
        
        consolidated = collection.consolidate()
        
        assert len(consolidated) == 2
        assert consolidated[0].end_date == date(2024, 6, 30)
    
    def test_consolidate_empty(self):
        """Consolidate empty collection."""
        collection = PeriodCollection()
        
        consolidated = collection.consolidate()
        
        assert consolidated == []
    
    def test_contains_date(self):
        """Check if any period contains date."""
        collection = PeriodCollection()
        collection.add(Period(start_date=date(2024, 1, 1), end_date=date(2024, 3, 31)))
        collection.add(Period(start_date=date(2024, 7, 1), end_date=date(2024, 9, 30)))
        
        assert collection.contains_date(date(2024, 2, 15))
        assert collection.contains_date(date(2024, 8, 15))
        assert not collection.contains_date(date(2024, 5, 15))  # In gap
    
    def test_get_period_at(self):
        """Get the specific period containing a date."""
        collection = PeriodCollection()
        p1 = Period(start_date=date(2024, 1, 1), end_date=date(2024, 3, 31), label="Q1")
        p2 = Period(start_date=date(2024, 7, 1), end_date=date(2024, 9, 30), label="Q3")
        collection.add(p1)
        collection.add(p2)
        
        result = collection.get_period_at(date(2024, 2, 15))
        
        assert result is not None
        assert result.label == "Q1"
    
    def test_get_period_at_none(self):
        """Return None when date not in any period."""
        collection = PeriodCollection()
        collection.add(Period(start_date=date(2024, 1, 1), end_date=date(2024, 3, 31)))
        
        result = collection.get_period_at(date(2024, 5, 15))
        
        assert result is None


class TestTimePeriod:
    """Tests for TimePeriod Pydantic model."""
    
    def test_create_time_period(self):
        """Create TimePeriod with start and end."""
        tp = TimePeriod(
            start=datetime(2024, 1, 1, 9, 0),
            end=datetime(2024, 1, 1, 17, 0)
        )
        
        assert tp.start == datetime(2024, 1, 1, 9, 0)
        assert tp.end == datetime(2024, 1, 1, 17, 0)
    
    def test_create_open_ended(self):
        """Create open-ended TimePeriod."""
        tp = TimePeriod(start=datetime(2024, 1, 1, 9, 0))
        
        assert tp.end is None
    
    def test_parse_from_string(self):
        """TimePeriod parses datetime strings."""
        tp = TimePeriod(
            start="2024-01-01T09:00:00",
            end="2024-01-01T17:00:00"
        )
        
        assert tp.start == datetime(2024, 1, 1, 9, 0)
        assert tp.end == datetime(2024, 1, 1, 17, 0)
    
    def test_end_before_start_raises(self):
        """End before start raises validation error."""
        with pytest.raises(ValueError, match="end must be after start"):
            TimePeriod(
                start=datetime(2024, 1, 1, 17, 0),
                end=datetime(2024, 1, 1, 9, 0)
            )
    
    def test_duration(self):
        """Duration calculated correctly."""
        tp = TimePeriod(
            start=datetime(2024, 1, 1, 9, 0),
            end=datetime(2024, 1, 1, 17, 0)
        )
        
        assert tp.duration == timedelta(hours=8)
    
    def test_duration_open_ended(self):
        """Duration is None for open-ended period."""
        tp = TimePeriod(start=datetime(2024, 1, 1, 9, 0))
        
        assert tp.duration is None
    
    def test_duration_hours(self):
        """Duration in hours calculated correctly."""
        tp = TimePeriod(
            start=datetime(2024, 1, 1, 9, 0),
            end=datetime(2024, 1, 1, 17, 0)
        )
        
        assert tp.duration_hours == 8.0
    
    def test_duration_days(self):
        """Duration in days calculated correctly."""
        tp = TimePeriod(
            start=datetime(2024, 1, 1, 0, 0),
            end=datetime(2024, 1, 3, 0, 0)
        )
        
        assert tp.duration_days == 2.0
    
    def test_contains_datetime(self):
        """Check if datetime is within period."""
        tp = TimePeriod(
            start=datetime(2024, 1, 1, 9, 0),
            end=datetime(2024, 1, 1, 17, 0)
        )
        
        assert tp.contains(datetime(2024, 1, 1, 12, 0))
        assert not tp.contains(datetime(2024, 1, 1, 8, 0))
        assert not tp.contains(datetime(2024, 1, 1, 18, 0))
    
    def test_contains_open_ended(self):
        """Open-ended contains any datetime after start."""
        tp = TimePeriod(start=datetime(2024, 1, 1, 9, 0))
        
        assert tp.contains(datetime(2024, 1, 1, 12, 0))
        assert tp.contains(datetime(2030, 12, 31, 23, 59))
        assert not tp.contains(datetime(2024, 1, 1, 8, 0))
    
    def test_overlaps_bounded(self):
        """Detect overlapping bounded periods."""
        tp1 = TimePeriod(
            start=datetime(2024, 1, 1, 9, 0),
            end=datetime(2024, 1, 1, 14, 0)
        )
        tp2 = TimePeriod(
            start=datetime(2024, 1, 1, 12, 0),
            end=datetime(2024, 1, 1, 18, 0)
        )
        
        assert tp1.overlaps(tp2)
        assert tp2.overlaps(tp1)
    
    def test_not_overlapping(self):
        """Non-overlapping periods detected."""
        tp1 = TimePeriod(
            start=datetime(2024, 1, 1, 9, 0),
            end=datetime(2024, 1, 1, 12, 0)
        )
        tp2 = TimePeriod(
            start=datetime(2024, 1, 1, 14, 0),
            end=datetime(2024, 1, 1, 18, 0)
        )
        
        assert not tp1.overlaps(tp2)
        assert not tp2.overlaps(tp1)
    
    def test_merge_overlapping(self):
        """Merge overlapping time periods."""
        tp1 = TimePeriod(
            start=datetime(2024, 1, 1, 9, 0),
            end=datetime(2024, 1, 1, 14, 0)
        )
        tp2 = TimePeriod(
            start=datetime(2024, 1, 1, 12, 0),
            end=datetime(2024, 1, 1, 18, 0)
        )
        
        merged = tp1.merge(tp2)
        
        assert merged.start == datetime(2024, 1, 1, 9, 0)
        assert merged.end == datetime(2024, 1, 1, 18, 0)
    
    def test_merge_non_overlapping_raises(self):
        """Merging non-overlapping periods raises error."""
        tp1 = TimePeriod(
            start=datetime(2024, 1, 1, 9, 0),
            end=datetime(2024, 1, 1, 12, 0)
        )
        tp2 = TimePeriod(
            start=datetime(2024, 1, 1, 14, 0),
            end=datetime(2024, 1, 1, 18, 0)
        )
        
        with pytest.raises(ValueError, match="non-overlapping"):
            tp1.merge(tp2)
    
    def test_merge_with_open_ended(self):
        """Merging with open-ended results in open-ended."""
        tp1 = TimePeriod(
            start=datetime(2024, 1, 1, 9, 0),
            end=datetime(2024, 1, 1, 14, 0)
        )
        tp2 = TimePeriod(
            start=datetime(2024, 1, 1, 12, 0)
        )
        
        merged = tp1.merge(tp2)
        
        assert merged.end is None
