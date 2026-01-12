"""Extended tests for generation/journey_engine module."""

import pytest
from datetime import date, timedelta


class TestJourneyEngineImports:
    """Tests for journey_engine module imports."""
    
    def test_import_journey_engine(self):
        """Test JourneyEngine can be imported."""
        from healthsim_agent.generation.journey_engine import JourneyEngine
        assert JourneyEngine is not None
    
    def test_import_event_definition(self):
        """Test EventDefinition can be imported."""
        from healthsim_agent.generation.journey_engine import EventDefinition
        assert EventDefinition is not None
    
    def test_import_journey_specification(self):
        """Test JourneySpecification can be imported."""
        from healthsim_agent.generation.journey_engine import JourneySpecification
        assert JourneySpecification is not None
    
    def test_import_timeline(self):
        """Test Timeline can be imported."""
        from healthsim_agent.generation.journey_engine import Timeline
        assert Timeline is not None
    
    def test_import_create_journey_engine(self):
        """Test create_journey_engine can be imported."""
        from healthsim_agent.generation.journey_engine import create_journey_engine
        assert create_journey_engine is not None
    
    def test_import_create_simple_journey(self):
        """Test create_simple_journey can be imported."""
        from healthsim_agent.generation.journey_engine import create_simple_journey
        assert create_simple_journey is not None


class TestEventTypes:
    """Tests for event type enums."""
    
    def test_patient_event_type(self):
        """Test PatientEventType enum."""
        from healthsim_agent.generation.journey_engine import PatientEventType
        assert PatientEventType is not None
        assert len(list(PatientEventType)) > 0
    
    def test_member_event_type(self):
        """Test MemberEventType enum."""
        from healthsim_agent.generation.journey_engine import MemberEventType
        assert MemberEventType is not None
    
    def test_rx_event_type(self):
        """Test RxEventType enum."""
        from healthsim_agent.generation.journey_engine import RxEventType
        assert RxEventType is not None
    
    def test_trial_event_type(self):
        """Test TrialEventType enum."""
        from healthsim_agent.generation.journey_engine import TrialEventType
        assert TrialEventType is not None


class TestDelaySpec:
    """Tests for DelaySpec dataclass."""
    
    def test_create_delay_spec(self):
        """Test creating DelaySpec."""
        from healthsim_agent.generation.journey_engine import DelaySpec
        
        spec = DelaySpec(days=7)
        assert spec.days == 7
    
    def test_delay_spec_with_range(self):
        """Test DelaySpec with min/max range."""
        from healthsim_agent.generation.journey_engine import DelaySpec
        
        spec = DelaySpec(days_min=1, days_max=30)
        assert spec.days_min == 1
        assert spec.days_max == 30


class TestJourneyTimelineEvent:
    """Tests for JourneyTimelineEvent dataclass."""
    
    def test_create_timeline_event(self):
        """Test creating JourneyTimelineEvent."""
        from healthsim_agent.generation.journey_engine import JourneyTimelineEvent
        
        event = JourneyTimelineEvent(
            timeline_event_id="evt-001",
            journey_id="journey-001",
            event_definition_id="def-001",
            scheduled_date=date.today(),
            event_type="encounter",
            event_name="Initial Visit"
        )
        assert event.event_type == "encounter"
        assert event.scheduled_date == date.today()


class TestJourneyTemplates:
    """Tests for journey templates."""
    
    def test_journey_templates_exist(self):
        """Test JOURNEY_TEMPLATES exists."""
        from healthsim_agent.generation.journey_engine import JOURNEY_TEMPLATES
        assert JOURNEY_TEMPLATES is not None
        assert isinstance(JOURNEY_TEMPLATES, dict)
    
    def test_get_journey_template_diabetic(self):
        """Test get_journey_template for diabetic template."""
        from healthsim_agent.generation.journey_engine import get_journey_template
        
        result = get_journey_template("diabetic-first-year")
        assert result is not None
    
    def test_get_journey_template_new_member(self):
        """Test get_journey_template for new member template."""
        from healthsim_agent.generation.journey_engine import get_journey_template
        
        result = get_journey_template("new-member-onboarding")
        assert result is not None


class TestCreateSimpleJourney:
    """Tests for create_simple_journey function."""
    
    def test_create_simple_journey(self):
        """Test creating simple journey."""
        from healthsim_agent.generation.journey_engine import create_simple_journey
        
        journey = create_simple_journey(
            journey_id="journey-001",
            name="test_journey",
            events=[{"event_id": "evt-001", "event_type": "encounter", "name": "Visit"}]
        )
        assert journey is not None
        assert journey.name == "test_journey"
