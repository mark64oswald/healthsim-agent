"""Tests for generation framework orchestrator."""

import pytest
from datetime import date, timedelta
from unittest.mock import Mock, patch, MagicMock

from healthsim_agent.generation.orchestrator import (
    EntityWithTimeline,
    OrchestratorResult,
    ProfileJourneyOrchestrator,
    orchestrate,
)
from healthsim_agent.generation.profile_executor import GeneratedEntity
from healthsim_agent.generation.journey_engine import Timeline


class TestEntityWithTimeline:
    """Tests for EntityWithTimeline dataclass."""
    
    def test_entity_with_timeline_creation(self):
        """Test creating entity with timeline."""
        mock_entity = Mock(spec=GeneratedEntity)
        mock_entity.index = 0
        mock_entity.identifiers = {"entity_id": "patient-001"}
        
        mock_timeline = Mock(spec=Timeline)
        mock_timeline.events = []
        mock_timeline.get_pending_events.return_value = []
        
        entity = EntityWithTimeline(
            entity=mock_entity,
            timeline=mock_timeline,
            journey_ids=["diabetic-care"],
        )
        
        assert entity.entity == mock_entity
        assert entity.timeline == mock_timeline
        assert "diabetic-care" in entity.journey_ids
    
    def test_entity_with_empty_journey_ids(self):
        """Test entity with no journey IDs."""
        mock_entity = Mock(spec=GeneratedEntity)
        mock_entity.index = 0
        
        mock_timeline = Mock(spec=Timeline)
        mock_timeline.events = []
        mock_timeline.get_pending_events.return_value = []
        
        entity = EntityWithTimeline(
            entity=mock_entity,
            timeline=mock_timeline,
        )
        
        assert entity.journey_ids == []
    
    def test_pending_events_property(self):
        """Test pending_events property."""
        mock_entity = Mock(spec=GeneratedEntity)
        mock_entity.index = 0
        
        mock_timeline = Mock(spec=Timeline)
        mock_timeline.events = [Mock(), Mock(), Mock()]
        mock_timeline.get_pending_events.return_value = [Mock(), Mock()]
        
        entity = EntityWithTimeline(
            entity=mock_entity,
            timeline=mock_timeline,
        )
        
        assert entity.pending_events == 2


class TestOrchestratorResult:
    """Tests for OrchestratorResult dataclass."""
    
    def test_orchestrator_result_creation(self):
        """Test creating orchestrator result."""
        result = OrchestratorResult(
            profile_id="test-profile",
            journey_ids=["journey-1"],
            seed=42,
            entities=[],
            duration_seconds=0.5,
        )
        
        assert result.profile_id == "test-profile"
        assert "journey-1" in result.journey_ids
        assert result.seed == 42
        assert result.duration_seconds == 0.5
    
    def test_entity_count_property(self):
        """Test entity_count property."""
        mock_entity = Mock(spec=EntityWithTimeline)
        mock_entity.timeline = Mock()
        mock_entity.timeline.events = []
        mock_entity.pending_events = 0
        
        result = OrchestratorResult(
            profile_id="test",
            journey_ids=[],
            seed=42,
            entities=[mock_entity, mock_entity],
        )
        
        assert result.entity_count == 2
    
    def test_event_count_property(self):
        """Test event_count property."""
        mock_entity1 = Mock(spec=EntityWithTimeline)
        mock_entity1.timeline = Mock()
        mock_entity1.timeline.events = [Mock(), Mock()]
        
        mock_entity2 = Mock(spec=EntityWithTimeline)
        mock_entity2.timeline = Mock()
        mock_entity2.timeline.events = [Mock()]
        
        result = OrchestratorResult(
            profile_id="test",
            journey_ids=[],
            seed=42,
            entities=[mock_entity1, mock_entity2],
        )
        
        assert result.event_count == 3


class TestProfileJourneyOrchestrator:
    """Tests for ProfileJourneyOrchestrator."""
    
    def test_orchestrator_initialization(self):
        """Test orchestrator initialization."""
        orchestrator = ProfileJourneyOrchestrator()
        
        assert orchestrator is not None
        assert orchestrator.seed == 42  # Default seed
    
    def test_orchestrator_with_seed(self):
        """Test orchestrator with custom seed."""
        orchestrator = ProfileJourneyOrchestrator(seed=123)
        
        assert orchestrator.seed == 123
    
    def test_register_executor(self):
        """Test registering a product executor."""
        orchestrator = ProfileJourneyOrchestrator()
        
        class MockExecutor:
            pass
        
        orchestrator.register_executor("patientsim", MockExecutor)
        
        assert "patientsim" in orchestrator._profile_executors


class TestOrchestrateFunction:
    """Tests for orchestrate convenience function."""
    
    def test_orchestrate_with_profile_string(self):
        """Test orchestrate function with profile template name."""
        result = orchestrate(
            profile="diabetic-cohort",
            count=1,
            seed=42,
        )
        
        assert isinstance(result, OrchestratorResult)
    
    def test_orchestrate_with_profile_dict(self):
        """Test orchestrate function with profile dict."""
        profile_spec = {
            "id": "test-profile",
            "name": "Test Profile",
            "demographics": {
                "age_range": [30, 50],
            },
        }
        
        result = orchestrate(
            profile=profile_spec,
            count=1,
            seed=42,
        )
        
        assert isinstance(result, OrchestratorResult)
        assert result.seed == 42
