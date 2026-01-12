"""
Tests for generation/triggers module.

Covers:
- TriggerPriority enum
- RegisteredTrigger dataclass
- TriggerRegistry registration and firing
- LinkedEntity dataclass
- CrossProductCoordinator coordination
"""

import pytest
from datetime import date, timedelta
from unittest.mock import MagicMock


class TestTriggerPriority:
    """Tests for TriggerPriority enum."""
    
    def test_priority_values(self):
        """Test priority value ordering."""
        from healthsim_agent.generation.triggers import TriggerPriority
        
        assert TriggerPriority.IMMEDIATE.value == 0
        assert TriggerPriority.HIGH.value == 1
        assert TriggerPriority.NORMAL.value == 2
        assert TriggerPriority.LOW.value == 3
    
    def test_priority_comparison(self):
        """Test priorities can be compared by value."""
        from healthsim_agent.generation.triggers import TriggerPriority
        
        assert TriggerPriority.IMMEDIATE.value < TriggerPriority.HIGH.value
        assert TriggerPriority.HIGH.value < TriggerPriority.NORMAL.value


class TestRegisteredTrigger:
    """Tests for RegisteredTrigger dataclass."""
    
    def test_create_basic_trigger(self):
        """Test creating a basic trigger."""
        from healthsim_agent.generation.triggers import (
            RegisteredTrigger, TriggerPriority
        )
        from healthsim_agent.generation.journey_engine import DelaySpec
        
        trigger = RegisteredTrigger(
            source_product="patientsim",
            source_event_type="diagnosis",
            target_product="membersim",
            target_event_type="claim",
        )
        
        assert trigger.source_product == "patientsim"
        assert trigger.target_product == "membersim"
        assert trigger.priority == TriggerPriority.NORMAL
    
    def test_trigger_with_delay(self):
        """Test trigger with delay specification."""
        from healthsim_agent.generation.triggers import RegisteredTrigger
        from healthsim_agent.generation.journey_engine import DelaySpec
        
        delay = DelaySpec(days=3, days_min=1, days_max=7)
        
        trigger = RegisteredTrigger(
            source_product="patientsim",
            source_event_type="lab_order",
            target_product="patientsim",
            target_event_type="lab_result",
            delay=delay,
        )
        
        assert trigger.delay.days == 3
    
    def test_trigger_with_parameter_map(self):
        """Test trigger with parameter mapping."""
        from healthsim_agent.generation.triggers import RegisteredTrigger
        
        trigger = RegisteredTrigger(
            source_product="patientsim",
            source_event_type="medication_order",
            target_product="rxmembersim",
            target_event_type="fill",
            parameter_map={"ndc": "rxnorm", "quantity": "qty"},
        )
        
        assert trigger.parameter_map["ndc"] == "rxnorm"


def _make_event(event_type: str, product: str, scheduled_date: date) -> "JourneyTimelineEvent":
    """Helper to create a JourneyTimelineEvent with required fields."""
    from healthsim_agent.generation.journey_engine import JourneyTimelineEvent
    return JourneyTimelineEvent(
        timeline_event_id=f"evt-{event_type}",
        journey_id="journey-1",
        event_definition_id="def-1",
        scheduled_date=scheduled_date,
        event_type=event_type,
        event_name=f"{event_type} event",
        product=product,
    )


def _make_timeline(entity_id: str, entity_type: str = "patient") -> "Timeline":
    """Helper to create a Timeline with required fields."""
    from healthsim_agent.generation.journey_engine import Timeline
    return Timeline(entity_id=entity_id, entity_type=entity_type)


class TestTriggerRegistry:
    """Tests for TriggerRegistry."""
    
    def test_create_empty_registry(self):
        """Test creating an empty registry."""
        from healthsim_agent.generation.triggers import TriggerRegistry
        
        registry = TriggerRegistry()
        
        assert len(registry._triggers) == 0
    
    def test_register_trigger(self):
        """Test registering a trigger."""
        from healthsim_agent.generation.triggers import TriggerRegistry
        
        registry = TriggerRegistry()
        registry.register(
            source_product="patientsim",
            source_event_type="diagnosis",
            target_product="membersim",
            target_event_type="claim",
        )
        
        triggers = registry.get_triggers("patientsim", "diagnosis")
        assert len(triggers) == 1
        assert triggers[0].target_product == "membersim"
    
    def test_register_multiple_triggers_same_source(self):
        """Test registering multiple triggers for same source."""
        from healthsim_agent.generation.triggers import TriggerRegistry
        
        registry = TriggerRegistry()
        registry.register(
            source_product="patientsim",
            source_event_type="medication_order",
            target_product="membersim",
            target_event_type="claim",
        )
        registry.register(
            source_product="patientsim",
            source_event_type="medication_order",
            target_product="rxmembersim",
            target_event_type="fill",
        )
        
        triggers = registry.get_triggers("patientsim", "medication_order")
        assert len(triggers) == 2
    
    def test_get_triggers_empty(self):
        """Test getting triggers for unregistered source."""
        from healthsim_agent.generation.triggers import TriggerRegistry
        
        registry = TriggerRegistry()
        triggers = registry.get_triggers("unknown", "event")
        
        assert triggers == []
    
    def test_register_target_handler(self):
        """Test registering a target handler."""
        from healthsim_agent.generation.triggers import TriggerRegistry
        
        registry = TriggerRegistry()
        handler = MagicMock()
        
        registry.register_target_handler("membersim", handler)
        
        assert registry._target_handlers["membersim"] is handler
    
    def test_fire_triggers_no_triggers(self):
        """Test firing triggers when none registered."""
        from healthsim_agent.generation.triggers import TriggerRegistry
        
        registry = TriggerRegistry()
        event = _make_event("test", "unknown", date.today())
        
        triggered = registry.fire_triggers(event, {}, {})
        
        assert triggered == []
    
    def test_fire_triggers_basic(self):
        """Test basic trigger firing."""
        from healthsim_agent.generation.triggers import TriggerRegistry
        
        registry = TriggerRegistry()
        registry.register(
            source_product="patientsim",
            source_event_type="diagnosis",
            target_product="membersim",
            target_event_type="claim",
        )
        
        event = _make_event("diagnosis", "patientsim", date.today())
        
        triggered = registry.fire_triggers(event, {}, {})
        
        assert len(triggered) == 1
        assert triggered[0]["target_product"] == "membersim"
        assert triggered[0]["target_event_type"] == "claim"
    
    def test_fire_triggers_with_handler(self):
        """Test trigger firing calls target handler."""
        from healthsim_agent.generation.triggers import TriggerRegistry
        
        registry = TriggerRegistry()
        handler = MagicMock()
        
        registry.register(
            source_product="patientsim",
            source_event_type="diagnosis",
            target_product="membersim",
            target_event_type="claim",
        )
        registry.register_target_handler("membersim", handler)
        
        event = _make_event("diagnosis", "patientsim", date.today())
        
        registry.fire_triggers(event, {}, {})
        
        handler.assert_called_once()
    
    def test_fire_triggers_with_condition_true(self):
        """Test trigger with passing condition."""
        from healthsim_agent.generation.triggers import TriggerRegistry
        from healthsim_agent.generation.journey_engine import EventCondition
        
        registry = TriggerRegistry()
        condition = MagicMock(spec=EventCondition)
        condition.evaluate.return_value = True
        
        registry.register(
            source_product="patientsim",
            source_event_type="diagnosis",
            target_product="membersim",
            target_event_type="claim",
            condition=condition,
        )
        
        event = _make_event("diagnosis", "patientsim", date.today())
        
        triggered = registry.fire_triggers(event, {}, {"test": "context"})
        
        assert len(triggered) == 1
        condition.evaluate.assert_called_once()
    
    def test_fire_triggers_with_condition_false(self):
        """Test trigger with failing condition is skipped."""
        from healthsim_agent.generation.triggers import TriggerRegistry
        from healthsim_agent.generation.journey_engine import EventCondition
        
        registry = TriggerRegistry()
        condition = MagicMock(spec=EventCondition)
        condition.evaluate.return_value = False
        
        registry.register(
            source_product="patientsim",
            source_event_type="diagnosis",
            target_product="membersim",
            target_event_type="claim",
            condition=condition,
        )
        
        event = _make_event("diagnosis", "patientsim", date.today())
        
        triggered = registry.fire_triggers(event, {}, {})
        
        assert len(triggered) == 0
    
    def test_fire_triggers_with_parameter_map(self):
        """Test parameter mapping during trigger firing."""
        from healthsim_agent.generation.triggers import TriggerRegistry
        
        registry = TriggerRegistry()
        handler = MagicMock()
        
        registry.register(
            source_product="patientsim",
            source_event_type="diagnosis",
            target_product="membersim",
            target_event_type="claim",
            parameter_map={"diagnosis_code": "icd10"},
        )
        registry.register_target_handler("membersim", handler)
        
        event = _make_event("diagnosis", "patientsim", date.today())
        
        registry.fire_triggers(event, {"icd10": "E11.9"}, {})
        
        call_args = handler.call_args
        assert call_args[0][2]["parameters"]["diagnosis_code"] == "E11.9"
    
    def test_fire_triggers_handler_exception(self):
        """Test trigger firing handles handler exceptions gracefully."""
        from healthsim_agent.generation.triggers import TriggerRegistry
        
        registry = TriggerRegistry()
        handler = MagicMock(side_effect=Exception("Handler error"))
        
        registry.register(
            source_product="patientsim",
            source_event_type="diagnosis",
            target_product="membersim",
            target_event_type="claim",
        )
        registry.register_target_handler("membersim", handler)
        
        event = _make_event("diagnosis", "patientsim", date.today())
        
        # Should not raise
        triggered = registry.fire_triggers(event, {}, {})
        assert len(triggered) == 1


class TestLinkedEntity:
    """Tests for LinkedEntity dataclass."""
    
    def test_create_basic_linked_entity(self):
        """Test creating a basic linked entity."""
        from healthsim_agent.generation.triggers import LinkedEntity
        
        linked = LinkedEntity(core_id="core-123")
        
        assert linked.core_id == "core-123"
        assert linked.patient_id is None
        assert linked.member_id is None
    
    def test_create_linked_entity_with_ids(self):
        """Test creating linked entity with product IDs."""
        from healthsim_agent.generation.triggers import LinkedEntity
        
        linked = LinkedEntity(
            core_id="core-123",
            patient_id="patient-456",
            member_id="member-789",
        )
        
        assert linked.patient_id == "patient-456"
        assert linked.member_id == "member-789"
    
    def test_linked_entity_timelines_default_empty(self):
        """Test timelines default to empty dict."""
        from healthsim_agent.generation.triggers import LinkedEntity
        
        linked = LinkedEntity(core_id="core-123")
        
        assert linked.timelines == {}


class TestCrossProductCoordinator:
    """Tests for CrossProductCoordinator."""
    
    def test_create_coordinator(self):
        """Test creating a coordinator."""
        from healthsim_agent.generation.triggers import CrossProductCoordinator
        
        coord = CrossProductCoordinator()
        
        assert len(coord._linked_entities) == 0
        assert coord._trigger_registry is not None
    
    def test_create_linked_entity(self):
        """Test creating a linked entity via coordinator."""
        from healthsim_agent.generation.triggers import CrossProductCoordinator
        
        coord = CrossProductCoordinator()
        linked = coord.create_linked_entity("core-123")
        
        assert linked.core_id == "core-123"
        assert coord._linked_entities["core-123"] is linked
    
    def test_create_linked_entity_with_product_ids(self):
        """Test creating linked entity with product IDs."""
        from healthsim_agent.generation.triggers import CrossProductCoordinator
        
        coord = CrossProductCoordinator()
        linked = coord.create_linked_entity(
            "core-123",
            product_ids={
                "patient_id": "pat-1",
                "member_id": "mem-1",
                "rx_member_id": "rx-1",
                "trial_subject_id": "subj-1",
            }
        )
        
        assert linked.patient_id == "pat-1"
        assert linked.member_id == "mem-1"
        assert linked.rx_member_id == "rx-1"
        assert linked.trial_subject_id == "subj-1"
    
    def test_get_linked_entity(self):
        """Test getting a linked entity."""
        from healthsim_agent.generation.triggers import CrossProductCoordinator
        
        coord = CrossProductCoordinator()
        coord.create_linked_entity("core-123")
        
        result = coord.get_linked_entity("core-123")
        
        assert result is not None
        assert result.core_id == "core-123"
    
    def test_get_linked_entity_not_found(self):
        """Test getting non-existent linked entity."""
        from healthsim_agent.generation.triggers import CrossProductCoordinator
        
        coord = CrossProductCoordinator()
        
        result = coord.get_linked_entity("unknown")
        
        assert result is None
    
    def test_register_product_engine(self):
        """Test registering a product engine."""
        from healthsim_agent.generation.triggers import CrossProductCoordinator
        
        coord = CrossProductCoordinator()
        engine = MagicMock()
        
        coord.register_product_engine("patientsim", engine)
        
        assert coord._product_engines["patientsim"] is engine
    
    def test_add_timeline(self):
        """Test adding a timeline to linked entity."""
        from healthsim_agent.generation.triggers import CrossProductCoordinator
        
        coord = CrossProductCoordinator()
        linked = coord.create_linked_entity("core-123")
        timeline = _make_timeline("entity-1", "patient")
        
        coord.add_timeline(linked, "patientsim", timeline)
        
        assert "patientsim" in linked.timelines
        assert linked.timelines["patientsim"] is timeline
    
    def test_add_multiple_timelines_links_them(self):
        """Test adding multiple timelines creates links."""
        from healthsim_agent.generation.triggers import CrossProductCoordinator
        
        coord = CrossProductCoordinator()
        linked = coord.create_linked_entity("core-123")
        timeline1 = _make_timeline("patient-1", "patient")
        timeline2 = _make_timeline("member-1", "member")
        
        coord.add_timeline(linked, "patientsim", timeline1)
        coord.add_timeline(linked, "membersim", timeline2)
        
        # Timelines should be cross-linked
        assert "membersim" in timeline1.linked_timelines
        assert "patientsim" in timeline2.linked_timelines
    
    def test_get_product_entity_patientsim(self):
        """Test getting entity dict for patientsim."""
        from healthsim_agent.generation.triggers import CrossProductCoordinator
        
        coord = CrossProductCoordinator()
        linked = coord.create_linked_entity(
            "core-123",
            product_ids={"patient_id": "pat-1"}
        )
        
        entity = coord._get_product_entity(linked, "patientsim")
        
        assert entity["patient_id"] == "pat-1"
        assert entity["core_id"] == "core-123"
    
    def test_get_product_entity_membersim(self):
        """Test getting entity dict for membersim."""
        from healthsim_agent.generation.triggers import CrossProductCoordinator
        
        coord = CrossProductCoordinator()
        linked = coord.create_linked_entity(
            "core-123",
            product_ids={"member_id": "mem-1"}
        )
        
        entity = coord._get_product_entity(linked, "membersim")
        
        assert entity["member_id"] == "mem-1"
    
    def test_get_product_entity_rxmembersim(self):
        """Test getting entity dict for rxmembersim."""
        from healthsim_agent.generation.triggers import CrossProductCoordinator
        
        coord = CrossProductCoordinator()
        linked = coord.create_linked_entity(
            "core-123",
            product_ids={"rx_member_id": "rx-1"}
        )
        
        entity = coord._get_product_entity(linked, "rxmembersim")
        
        assert entity["rx_member_id"] == "rx-1"
    
    def test_get_product_entity_trialsim(self):
        """Test getting entity dict for trialsim."""
        from healthsim_agent.generation.triggers import CrossProductCoordinator
        
        coord = CrossProductCoordinator()
        linked = coord.create_linked_entity(
            "core-123",
            product_ids={"trial_subject_id": "subj-1"}
        )
        
        entity = coord._get_product_entity(linked, "trialsim")
        
        assert entity["subject_id"] == "subj-1"
    
    def test_get_product_entity_unknown(self):
        """Test getting entity dict for unknown product."""
        from healthsim_agent.generation.triggers import CrossProductCoordinator
        
        coord = CrossProductCoordinator()
        linked = coord.create_linked_entity("core-123")
        
        entity = coord._get_product_entity(linked, "unknown")
        
        assert entity == {"core_id": "core-123"}
    
    def test_default_triggers_registered(self):
        """Test default triggers are registered on creation."""
        from healthsim_agent.generation.triggers import CrossProductCoordinator
        
        coord = CrossProductCoordinator()
        
        # Check diagnosis -> claim trigger exists
        triggers = coord._trigger_registry.get_triggers("patientsim", "diagnosis")
        assert len(triggers) >= 1
        
        # Check medication_order -> claim trigger exists
        triggers = coord._trigger_registry.get_triggers("patientsim", "medication_order")
        assert len(triggers) >= 1


class TestCreateCoordinator:
    """Tests for create_coordinator convenience function."""
    
    def test_create_coordinator(self):
        """Test create_coordinator returns initialized coordinator."""
        from healthsim_agent.generation.triggers import create_coordinator
        
        coord = create_coordinator()
        
        assert coord is not None
        assert len(coord._linked_entities) == 0


class TestExecuteCoordinated:
    """Tests for execute_coordinated method."""
    
    def test_execute_coordinated_no_engine(self):
        """Test execution skips events when no engine registered."""
        from healthsim_agent.generation.triggers import CrossProductCoordinator
        
        coord = CrossProductCoordinator()
        linked = coord.create_linked_entity("core-123")
        
        timeline = _make_timeline("patient-1", "patient")
        event = _make_event("diagnosis", "patientsim", date.today() - timedelta(days=1))
        timeline.events.append(event)
        coord.add_timeline(linked, "patientsim", timeline)
        
        results = coord.execute_coordinated(linked, date.today())
        
        assert "patientsim" in results
        assert results["patientsim"][0]["status"] == "skipped"
        assert "No engine registered" in results["patientsim"][0]["reason"]
    
    def test_execute_coordinated_with_engine(self):
        """Test execution calls engine for events."""
        from healthsim_agent.generation.triggers import CrossProductCoordinator
        
        coord = CrossProductCoordinator()
        linked = coord.create_linked_entity(
            "core-123",
            product_ids={"patient_id": "pat-1"}
        )
        
        # Mock engine
        engine = MagicMock()
        engine.execute_event.return_value = {"status": "executed", "outputs": {}}
        coord.register_product_engine("patientsim", engine)
        
        # Create timeline with event
        timeline = _make_timeline("patient-1", "patient")
        event = _make_event("diagnosis", "patientsim", date.today() - timedelta(days=1))
        timeline.events.append(event)
        coord.add_timeline(linked, "patientsim", timeline)
        
        results = coord.execute_coordinated(linked, date.today())
        
        assert "patientsim" in results
        engine.execute_event.assert_called_once()
