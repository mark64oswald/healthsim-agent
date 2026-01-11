"""
Tests for temporal/timeline.py - Timeline and event management.
"""
import pytest
from datetime import date, datetime, timedelta

from healthsim_agent.temporal.timeline import (
    EventStatus,
    EventDelay,
    TimelineEvent,
    Timeline,
)


class TestEventStatus:
    """Tests for EventStatus enum."""
    
    def test_status_values(self):
        """Status enum has expected values."""
        assert EventStatus.PENDING == "pending"
        assert EventStatus.EXECUTED == "executed"
        assert EventStatus.SKIPPED == "skipped"
        assert EventStatus.FAILED == "failed"
    
    def test_status_is_string_enum(self):
        """Status values are strings."""
        assert isinstance(EventStatus.PENDING.value, str)


class TestEventDelay:
    """Tests for EventDelay dataclass."""
    
    def test_default_delay(self):
        """Default delay is zero."""
        delay = EventDelay()
        
        assert delay.min_days == 0
        assert delay.max_days == 0
        assert delay.min_hours == 0
        assert delay.max_hours == 0
    
    def test_calculate_fixed_delay(self):
        """Calculate fixed delay (no range)."""
        delay = EventDelay(min_days=5, max_days=5)
        result = delay.calculate()
        
        assert result == timedelta(days=5)
    
    def test_calculate_with_hours(self):
        """Calculate delay with hours."""
        delay = EventDelay(min_days=1, max_days=1, min_hours=8, max_hours=8)
        result = delay.calculate()
        
        assert result == timedelta(days=1, hours=8)
    
    def test_calculate_range_days(self):
        """Calculate delay with range returns within range."""
        delay = EventDelay(min_days=1, max_days=10)
        
        # Run multiple times to verify range
        for _ in range(10):
            result = delay.calculate()
            assert timedelta(days=1) <= result <= timedelta(days=10)
    
    def test_calculate_range_hours(self):
        """Calculate delay with hour range."""
        delay = EventDelay(min_hours=1, max_hours=24)
        
        for _ in range(10):
            result = delay.calculate()
            assert timedelta(hours=1) <= result <= timedelta(hours=24)
    
    def test_calculate_with_custom_rng(self):
        """Calculate uses custom random generator."""
        import random
        
        delay = EventDelay(min_days=1, max_days=100)
        
        # Use seeded random for reproducibility
        rng = random.Random(42)
        result1 = delay.calculate(rng)
        
        rng = random.Random(42)
        result2 = delay.calculate(rng)
        
        assert result1 == result2


class TestTimelineEvent:
    """Tests for TimelineEvent dataclass."""
    
    def test_create_event_defaults(self):
        """Create event with minimal parameters."""
        event = TimelineEvent()
        
        assert event.event_id  # Auto-generated
        assert event.event_type == ""
        assert event.status == EventStatus.PENDING
        assert event.payload == {}
        assert event.result is None
    
    def test_create_event_with_values(self):
        """Create event with specified values."""
        event = TimelineEvent(
            event_type="encounter",
            name="Initial Visit",
            scheduled_date=date(2024, 3, 15),
            payload={"provider_id": "P001"}
        )
        
        assert event.event_type == "encounter"
        assert event.name == "Initial Visit"
        assert event.scheduled_date == date(2024, 3, 15)
        assert event.payload["provider_id"] == "P001"
    
    def test_timestamp_from_date(self):
        """Timestamp initialized from scheduled_date."""
        event = TimelineEvent(scheduled_date=date(2024, 3, 15))
        
        assert event.timestamp == datetime(2024, 3, 15, 0, 0)
    
    def test_timestamp_from_datetime(self):
        """Timestamp uses datetime directly."""
        dt = datetime(2024, 3, 15, 14, 30)
        event = TimelineEvent(scheduled_date=dt)
        
        assert event.timestamp == dt
    
    def test_mark_executed(self):
        """Mark event as executed."""
        event = TimelineEvent()
        event.mark_executed(result="Success")
        
        assert event.status == EventStatus.EXECUTED
        assert event.result == "Success"
    
    def test_mark_executed_no_result(self):
        """Mark executed without result."""
        event = TimelineEvent()
        event.mark_executed()
        
        assert event.status == EventStatus.EXECUTED
        assert event.result is None
    
    def test_mark_failed(self):
        """Mark event as failed."""
        event = TimelineEvent()
        event.mark_failed("Connection timeout")
        
        assert event.status == EventStatus.FAILED
        assert event.error == "Connection timeout"
    
    def test_mark_skipped(self):
        """Mark event as skipped."""
        event = TimelineEvent()
        event.mark_skipped("Dependency failed")
        
        assert event.status == EventStatus.SKIPPED
        assert event.error == "Dependency failed"
    
    def test_mark_skipped_no_reason(self):
        """Mark skipped without reason."""
        event = TimelineEvent()
        event.mark_skipped()
        
        assert event.status == EventStatus.SKIPPED
        assert event.error == ""
    
    def test_event_comparison_dates(self):
        """Events compared by date."""
        e1 = TimelineEvent(scheduled_date=date(2024, 1, 1))
        e2 = TimelineEvent(scheduled_date=date(2024, 1, 15))
        
        assert e1 < e2
        assert not e2 < e1
    
    def test_event_comparison_datetimes(self):
        """Events compared by datetime."""
        e1 = TimelineEvent(scheduled_date=datetime(2024, 1, 1, 9, 0))
        e2 = TimelineEvent(scheduled_date=datetime(2024, 1, 1, 14, 0))
        
        assert e1 < e2
    
    def test_event_comparison_mixed(self):
        """Events compared with mixed date/datetime."""
        e1 = TimelineEvent(scheduled_date=date(2024, 1, 1))  # Becomes 00:00
        e2 = TimelineEvent(scheduled_date=datetime(2024, 1, 1, 14, 0))
        
        assert e1 < e2
    
    def test_event_comparison_none_dates(self):
        """Events with None dates not less than each other."""
        e1 = TimelineEvent()
        e2 = TimelineEvent(scheduled_date=date(2024, 1, 1))
        
        assert not e1 < e2  # None is not less than anything
    
    def test_event_tags(self):
        """Event can have tags."""
        event = TimelineEvent(tags=["urgent", "followup"])
        
        assert "urgent" in event.tags
        assert "followup" in event.tags


class TestTimeline:
    """Tests for Timeline class."""
    
    def test_create_timeline_defaults(self):
        """Create timeline with defaults."""
        timeline = Timeline()
        
        assert timeline.timeline_id
        assert timeline.events == []
        assert isinstance(timeline.start_date, date)
    
    def test_create_timeline_with_values(self):
        """Create timeline with specified values."""
        timeline = Timeline(
            name="Patient Journey",
            start_date=date(2024, 1, 1),
            entity_id="P001"
        )
        
        assert timeline.name == "Patient Journey"
        assert timeline.start_date == date(2024, 1, 1)
        assert timeline.entity_id == "P001"
    
    def test_entity_id_from_timeline_id(self):
        """Entity ID defaults to timeline ID."""
        timeline = Timeline()
        
        assert timeline.entity_id == timeline.timeline_id
    
    def test_add_event(self):
        """Add event to timeline."""
        timeline = Timeline()
        event = TimelineEvent(event_type="test")
        
        result = timeline.add_event(event)
        
        assert len(timeline.events) == 1
        assert result is event
    
    def test_add_event_maintains_sort_order(self):
        """Events sorted by date when added."""
        timeline = Timeline()
        
        timeline.add_event(TimelineEvent(scheduled_date=date(2024, 3, 1)))
        timeline.add_event(TimelineEvent(scheduled_date=date(2024, 1, 1)))
        timeline.add_event(TimelineEvent(scheduled_date=date(2024, 2, 1)))
        
        assert timeline.events[0].scheduled_date == date(2024, 1, 1)
        assert timeline.events[1].scheduled_date == date(2024, 2, 1)
        assert timeline.events[2].scheduled_date == date(2024, 3, 1)
    
    def test_create_event(self):
        """Create and add event in one call."""
        timeline = Timeline()
        
        event = timeline.create_event(
            event_type="encounter",
            name="Initial Visit",
            provider_id="P001"
        )
        
        assert len(timeline.events) == 1
        assert event.event_type == "encounter"
        assert event.name == "Initial Visit"
        assert event.payload["provider_id"] == "P001"
    
    def test_create_event_with_delay(self):
        """Create event with delay specification."""
        timeline = Timeline()
        delay = EventDelay(min_days=7, max_days=14)
        
        event = timeline.create_event(
            event_type="followup",
            delay=delay
        )
        
        assert event.delay_from_previous.min_days == 7
        assert event.delay_from_previous.max_days == 14
    
    def test_create_event_default_name(self):
        """Event name defaults to event_type."""
        timeline = Timeline()
        
        event = timeline.create_event(event_type="lab_test")
        
        assert event.name == "lab_test"
    
    def test_schedule_events(self):
        """Schedule events calculates dates."""
        timeline = Timeline(start_date=date(2024, 1, 1))
        
        timeline.create_event("event1", delay=EventDelay(min_days=0))
        timeline.create_event("event2", delay=EventDelay(min_days=7, max_days=7))
        timeline.create_event("event3", delay=EventDelay(min_days=14, max_days=14))
        
        timeline.schedule_events()
        
        assert timeline.events[0].scheduled_date == date(2024, 1, 1)
        assert timeline.events[1].scheduled_date == date(2024, 1, 8)
        assert timeline.events[2].scheduled_date == date(2024, 1, 22)
    
    def test_schedule_events_with_datetime_start(self):
        """Schedule with datetime start date."""
        timeline = Timeline(start_date=datetime(2024, 1, 1, 9, 0))
        
        timeline.create_event("event1", delay=EventDelay(min_hours=2, max_hours=2))
        timeline.schedule_events()
        
        assert timeline.events[0].scheduled_date == datetime(2024, 1, 1, 11, 0)
    
    def test_get_pending_events(self):
        """Get pending events up to date."""
        timeline = Timeline()
        
        e1 = TimelineEvent(scheduled_date=date(2024, 1, 1), status=EventStatus.PENDING)
        e2 = TimelineEvent(scheduled_date=date(2024, 2, 1), status=EventStatus.EXECUTED)
        e3 = TimelineEvent(scheduled_date=date(2024, 3, 1), status=EventStatus.PENDING)
        
        timeline.add_event(e1)
        timeline.add_event(e2)
        timeline.add_event(e3)
        
        pending = list(timeline.get_pending_events(up_to_date=date(2024, 2, 15)))
        
        assert len(pending) == 1
        assert pending[0] is e1
    
    def test_get_pending_events_no_cutoff(self):
        """Get all pending events when no cutoff specified."""
        timeline = Timeline()
        
        e1 = TimelineEvent(scheduled_date=date(2024, 1, 1), status=EventStatus.PENDING)
        e2 = TimelineEvent(scheduled_date=date(2030, 1, 1), status=EventStatus.PENDING)
        
        timeline.add_event(e1)
        timeline.add_event(e2)
        
        # With no cutoff, uses today's date
        pending = list(timeline.get_pending_events())
        
        assert e1 in pending  # Past date should be included
    
    def test_get_events_by_type(self):
        """Get events filtered by type."""
        timeline = Timeline()
        
        timeline.create_event("encounter")
        timeline.create_event("encounter")
        timeline.create_event("lab_test")
        
        encounters = timeline.get_events_by_type("encounter")
        
        assert len(encounters) == 2
    
    def test_get_events_by_status(self):
        """Get events filtered by status."""
        timeline = Timeline()
        
        timeline.create_event("e1")
        timeline.create_event("e2")
        timeline.events[0].mark_executed()
        
        executed = timeline.get_events_by_status(EventStatus.EXECUTED)
        pending = timeline.get_events_by_status(EventStatus.PENDING)
        
        assert len(executed) == 1
        assert len(pending) == 1
    
    def test_get_event_by_id(self):
        """Get event by ID."""
        timeline = Timeline()
        event = timeline.create_event("test")
        
        found = timeline.get_event(event.event_id)
        
        assert found is event
    
    def test_get_event_by_id_not_found(self):
        """Get event returns None when not found."""
        timeline = Timeline()
        
        found = timeline.get_event("nonexistent")
        
        assert found is None
    
    def test_get_event_by_id_alias(self):
        """get_event_by_id is alias for get_event."""
        timeline = Timeline()
        event = timeline.create_event("test")
        
        found = timeline.get_event_by_id(event.event_id)
        
        assert found is event
    
    def test_get_events_in_range(self):
        """Get events within datetime range."""
        timeline = Timeline()
        
        timeline.add_event(TimelineEvent(scheduled_date=datetime(2024, 1, 15, 10, 0)))
        timeline.add_event(TimelineEvent(scheduled_date=datetime(2024, 2, 15, 10, 0)))
        timeline.add_event(TimelineEvent(scheduled_date=datetime(2024, 3, 15, 10, 0)))
        
        events = timeline.get_events_in_range(
            datetime(2024, 2, 1),
            datetime(2024, 2, 28)
        )
        
        assert len(events) == 1
        assert events[0].scheduled_date == datetime(2024, 2, 15, 10, 0)
    
    def test_get_events_in_range_empty(self):
        """Get events returns empty when none in range."""
        timeline = Timeline()
        
        timeline.add_event(TimelineEvent(scheduled_date=datetime(2024, 1, 15)))
        
        events = timeline.get_events_in_range(
            datetime(2024, 6, 1),
            datetime(2024, 6, 30)
        )
        
        assert events == []
    
    def test_get_first_event(self):
        """Get earliest event."""
        timeline = Timeline()
        
        timeline.add_event(TimelineEvent(scheduled_date=date(2024, 2, 1)))
        timeline.add_event(TimelineEvent(scheduled_date=date(2024, 1, 1)))
        
        first = timeline.get_first_event()
        
        assert first.scheduled_date == date(2024, 1, 1)
    
    def test_get_first_event_empty(self):
        """Get first returns None when empty."""
        timeline = Timeline()
        
        assert timeline.get_first_event() is None
    
    def test_get_last_event(self):
        """Get most recent event."""
        timeline = Timeline()
        
        timeline.add_event(TimelineEvent(scheduled_date=date(2024, 1, 1)))
        timeline.add_event(TimelineEvent(scheduled_date=date(2024, 2, 1)))
        
        last = timeline.get_last_event()
        
        assert last.scheduled_date == date(2024, 2, 1)
    
    def test_get_last_event_empty(self):
        """Get last returns None when empty."""
        timeline = Timeline()
        
        assert timeline.get_last_event() is None
    
    def test_remove_event(self):
        """Remove event by ID."""
        timeline = Timeline()
        event = timeline.create_event("test")
        event_id = event.event_id
        
        result = timeline.remove_event(event_id)
        
        assert result is True
        assert len(timeline.events) == 0
    
    def test_remove_event_not_found(self):
        """Remove returns False when not found."""
        timeline = Timeline()
        
        result = timeline.remove_event("nonexistent")
        
        assert result is False
    
    def test_clear(self):
        """Clear removes all events."""
        timeline = Timeline()
        timeline.create_event("e1")
        timeline.create_event("e2")
        
        timeline.clear()
        
        assert len(timeline.events) == 0
    
    def test_is_complete_all_executed(self):
        """Timeline complete when all executed."""
        timeline = Timeline()
        timeline.create_event("e1")
        timeline.create_event("e2")
        
        timeline.events[0].mark_executed()
        timeline.events[1].mark_executed()
        
        assert timeline.is_complete
    
    def test_is_complete_mixed_executed_skipped(self):
        """Timeline complete with executed and skipped."""
        timeline = Timeline()
        timeline.create_event("e1")
        timeline.create_event("e2")
        
        timeline.events[0].mark_executed()
        timeline.events[1].mark_skipped()
        
        assert timeline.is_complete
    
    def test_is_complete_has_pending(self):
        """Timeline not complete with pending events."""
        timeline = Timeline()
        timeline.create_event("e1")
        timeline.create_event("e2")
        
        timeline.events[0].mark_executed()
        # events[1] still pending
        
        assert not timeline.is_complete
    
    def test_is_complete_empty(self):
        """Empty timeline is complete."""
        timeline = Timeline()
        
        assert timeline.is_complete
    
    def test_len(self):
        """Timeline length is number of events."""
        timeline = Timeline()
        timeline.create_event("e1")
        timeline.create_event("e2")
        
        assert len(timeline) == 2
    
    def test_iter(self):
        """Timeline is iterable."""
        timeline = Timeline()
        timeline.create_event("e1")
        timeline.create_event("e2")
        
        events = list(timeline)
        
        assert len(events) == 2
    
    def test_contains(self):
        """Check if event ID in timeline."""
        timeline = Timeline()
        event = timeline.create_event("test")
        
        assert event.event_id in timeline
        assert "nonexistent" not in timeline


class TestSchedulingWithDependencies:
    """Test event scheduling with dependencies."""
    
    def test_schedule_with_explicit_dependency(self):
        """Events can depend on specific events."""
        timeline = Timeline(start_date=date(2024, 1, 1))
        
        e1 = timeline.create_event("surgery", delay=EventDelay())
        e2 = timeline.create_event(
            "followup",
            depends_on=e1.event_id,
            delay=EventDelay(min_days=14, max_days=14)
        )
        
        timeline.schedule_events()
        
        assert e1.scheduled_date == date(2024, 1, 1)
        assert e2.scheduled_date == date(2024, 1, 15)
