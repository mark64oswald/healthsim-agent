"""Tests for generation framework - event handlers."""

import pytest
from datetime import date

from healthsim_agent.generation import (
    TimelineEvent,
    PatientSimHandlers,
    MemberSimHandlers,
    RxMemberSimHandlers,
    TrialSimHandlers,
    HandlerRegistry,
)


class TestTimelineEvent:
    """Tests for TimelineEvent dataclass."""
    
    def test_create_event(self):
        """Test creating a timeline event."""
        event = TimelineEvent(
            timeline_event_id="EVT-001",
            event_type="encounter",
            event_name="Office Visit",
            scheduled_date=date(2024, 1, 15),
        )
        
        assert event.timeline_event_id == "EVT-001"
        assert event.event_type == "encounter"
        assert event.status == "scheduled"
    
    def test_event_with_parameters(self):
        """Test event with parameters."""
        event = TimelineEvent(
            timeline_event_id="EVT-002",
            event_type="lab_result",
            event_name="A1C Test",
            scheduled_date=date(2024, 1, 15),
            parameters={"loinc": "4548-4", "test_name": "Hemoglobin A1c"},
        )
        
        assert event.parameters["loinc"] == "4548-4"


class TestPatientSimHandlers:
    """Tests for PatientSim event handlers."""
    
    @pytest.fixture
    def handlers(self):
        return PatientSimHandlers(seed=42)
    
    @pytest.fixture
    def patient(self):
        return {
            "patient_id": "PAT-001",
            "id": "PAT-001",
            "given_name": "John",
            "family_name": "Doe",
            "conditions": [{"code": "E11"}],
        }
    
    def test_handle_encounter(self, handlers, patient):
        """Test handling encounter event."""
        event = TimelineEvent(
            timeline_event_id="EVT-001",
            event_type="encounter",
            event_name="Office Visit",
            scheduled_date=date(2024, 1, 15),
            parameters={"encounter_type": "outpatient"},
        )
        
        result = handlers.handle_encounter(patient, event, {})
        
        assert "encounter_id" in result
        assert result["patient_id"] == "PAT-001"
        assert result["encounter_type"] == "outpatient"
        assert result["status"] == "completed"
    
    def test_handle_diagnosis(self, handlers, patient):
        """Test handling diagnosis event."""
        event = TimelineEvent(
            timeline_event_id="EVT-002",
            event_type="diagnosis",
            event_name="New Diagnosis",
            scheduled_date=date(2024, 1, 15),
            parameters={"icd10": "E11", "description": "Type 2 diabetes"},
        )
        
        result = handlers.handle_diagnosis(patient, event, {})
        
        assert "condition_id" in result
        assert result["icd10"] == "E11"
        assert result["clinical_status"] == "active"
    
    def test_handle_lab_result(self, handlers, patient):
        """Test handling lab result event."""
        event = TimelineEvent(
            timeline_event_id="EVT-003",
            event_type="lab_result",
            event_name="A1C Result",
            scheduled_date=date(2024, 1, 15),
            parameters={"loinc": "4548-4", "test_name": "Hemoglobin A1c"},
        )
        
        result = handlers.handle_lab_result(patient, event, {})
        
        assert "result_id" in result
        assert result["loinc"] == "4548-4"
        assert "value" in result
        assert "unit" in result
        # Patient has diabetes, so A1C should be higher
        assert result["value"] >= 4.0
    
    def test_get_handler(self, handlers):
        """Test getting handler by event type."""
        handler = handlers.get_handler("encounter")
        assert handler is not None
        assert callable(handler)
        
        # Unknown type returns None
        assert handlers.get_handler("unknown") is None


class TestMemberSimHandlers:
    """Tests for MemberSim event handlers."""
    
    @pytest.fixture
    def handlers(self):
        return MemberSimHandlers(seed=42)
    
    @pytest.fixture
    def member(self):
        return {
            "member_id": "MBR-001",
            "id": "MBR-001",
            "subscriber_id": "SUB-001",
        }
    
    def test_handle_enrollment(self, handlers, member):
        """Test handling enrollment event."""
        event = TimelineEvent(
            timeline_event_id="EVT-001",
            event_type="enrollment",
            event_name="New Enrollment",
            scheduled_date=date(2024, 1, 1),
            parameters={"plan_code": "PPO-001", "coverage_type": "Commercial"},
        )
        
        result = handlers.handle_enrollment(member, event, {})
        
        assert "enrollment_id" in result
        assert result["member_id"] == "MBR-001"
        assert result["plan_code"] == "PPO-001"
        assert result["status"] == "active"
    
    def test_handle_claim(self, handlers, member):
        """Test handling claim event."""
        event = TimelineEvent(
            timeline_event_id="EVT-002",
            event_type="claim",
            event_name="Office Visit Claim",
            scheduled_date=date(2024, 1, 15),
            parameters={
                "claim_type": "PROFESSIONAL",
                "diagnosis": "E11",
                "procedure": "99213",
            },
        )
        
        result = handlers.handle_claim(member, event, {})
        
        assert "claim_id" in result
        assert result["member_id"] == "MBR-001"
        assert result["claim_type"] == "PROFESSIONAL"
        assert result["total_paid"] <= result["total_allowed"]


class TestRxMemberSimHandlers:
    """Tests for RxMemberSim event handlers."""
    
    @pytest.fixture
    def handlers(self):
        return RxMemberSimHandlers(seed=42)
    
    @pytest.fixture
    def member(self):
        return {"member_id": "MBR-001", "id": "MBR-001"}
    
    def test_handle_prescription(self, handlers, member):
        """Test handling prescription event."""
        event = TimelineEvent(
            timeline_event_id="EVT-001",
            event_type="prescription",
            event_name="New Rx",
            scheduled_date=date(2024, 1, 15),
            parameters={"medication": "metformin"},
        )
        
        result = handlers.handle_prescription(member, event, {})
        
        assert "prescription_id" in result
        assert result["member_id"] == "MBR-001"
        assert result["medication_name"] == "Metformin"
        assert result["ndc"] is not None
    
    def test_handle_fill(self, handlers, member):
        """Test handling fill event."""
        event = TimelineEvent(
            timeline_event_id="EVT-002",
            event_type="fill",
            event_name="Rx Fill",
            scheduled_date=date(2024, 1, 20),
            parameters={"quantity": 30, "days_supply": 30},
        )
        
        result = handlers.handle_fill(member, event, {"last_rx_id": "RX-001"})
        
        assert "fill_id" in result
        assert result["quantity"] == 30
        assert result["plan_paid"] + result["member_paid"] == pytest.approx(result["total_cost"], rel=0.01)


class TestTrialSimHandlers:
    """Tests for TrialSim event handlers."""
    
    @pytest.fixture
    def handlers(self):
        return TrialSimHandlers(seed=42)
    
    @pytest.fixture
    def subject(self):
        return {
            "usubjid": "STUDY001-SITE01-0001",
            "subject_id": "0001",
            "study_id": "STUDY001",
        }
    
    def test_handle_screening(self, handlers, subject):
        """Test handling screening event."""
        event = TimelineEvent(
            timeline_event_id="EVT-001",
            event_type="screening",
            event_name="Screening Visit",
            scheduled_date=date(2024, 1, 10),
        )
        
        result = handlers.handle_screening(subject, event, {})
        
        assert "visit_id" in result
        assert result["visit_type"] == "SCREENING"
        assert result["visit_status"] == "COMPLETED"
    
    def test_handle_randomization(self, handlers, subject):
        """Test handling randomization event."""
        event = TimelineEvent(
            timeline_event_id="EVT-002",
            event_type="randomization",
            event_name="Randomization",
            scheduled_date=date(2024, 1, 20),
            parameters={"arms": ["Treatment", "Placebo"]},
        )
        
        result = handlers.handle_randomization(subject, event, {})
        
        assert "randomization_id" in result
        assert result["treatment_arm"] in ["Treatment", "Placebo"]
    
    def test_handle_adverse_event(self, handlers, subject):
        """Test handling adverse event."""
        event = TimelineEvent(
            timeline_event_id="EVT-003",
            event_type="adverse_event",
            event_name="AE Reported",
            scheduled_date=date(2024, 2, 15),
            parameters={
                "term": "Nausea",
                "severity": "MILD",
                "serious": False,
            },
        )
        
        result = handlers.handle_adverse_event(subject, event, {})
        
        assert "ae_id" in result
        assert result["ae_term"] == "Nausea"
        assert result["ae_severity"] == "MILD"
        assert result["ae_serious"] is False


class TestHandlerRegistry:
    """Tests for HandlerRegistry."""
    
    @pytest.fixture
    def registry(self):
        return HandlerRegistry(seed=42)
    
    def test_get_handlers(self, registry):
        """Test getting handlers for each product."""
        assert registry.get_handlers("patientsim") is not None
        assert registry.get_handlers("membersim") is not None
        assert registry.get_handlers("rxmembersim") is not None
        assert registry.get_handlers("trialsim") is not None
        
        # Unknown product returns None
        assert registry.get_handlers("unknown") is None
    
    def test_handle_event(self, registry):
        """Test handling event through registry."""
        patient = {"patient_id": "PAT-001", "id": "PAT-001"}
        event = TimelineEvent(
            timeline_event_id="EVT-001",
            event_type="encounter",
            event_name="Office Visit",
            scheduled_date=date(2024, 1, 15),
        )
        
        result = registry.handle_event(
            product="patientsim",
            event_type="encounter",
            entity=patient,
            event=event,
            context={},
        )
        
        assert result is not None
        assert "encounter_id" in result
    
    def test_handle_unknown_event(self, registry):
        """Test handling unknown event type."""
        patient = {"patient_id": "PAT-001"}
        event = TimelineEvent(
            timeline_event_id="EVT-001",
            event_type="unknown",
            event_name="Unknown",
            scheduled_date=date(2024, 1, 15),
        )
        
        result = registry.handle_event(
            product="patientsim",
            event_type="unknown",
            entity=patient,
            event=event,
            context={},
        )
        
        assert result is None
