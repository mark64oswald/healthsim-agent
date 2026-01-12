"""Extended tests for generation framework - event handlers.

Covers additional handlers and edge cases for handlers.py.
"""

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


class TestPatientSimHandlersExtended:
    """Extended tests for PatientSim event handlers."""
    
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
    
    def test_handle_admission(self, handlers, patient):
        """Test handling admission event."""
        event = TimelineEvent(
            timeline_event_id="EVT-001",
            event_type="admission",
            event_name="Hospital Admission",
            scheduled_date=date(2024, 1, 15),
            parameters={"admission_type": "emergency"},
        )
        
        result = handlers.handle_admission(patient, event, {})
        
        assert "encounter_id" in result
        assert result["patient_id"] == "PAT-001"
        assert result["encounter_type"] == "inpatient"
        assert result["admission_type"] == "emergency"
        assert result["adt_type"] == "A01"
        assert result["status"] == "active"
    
    def test_handle_discharge(self, handlers, patient):
        """Test handling discharge event."""
        event = TimelineEvent(
            timeline_event_id="EVT-002",
            event_type="discharge",
            event_name="Hospital Discharge",
            scheduled_date=date(2024, 1, 20),
            parameters={"disposition": "skilled_nursing", "status": "alive"},
        )
        
        result = handlers.handle_discharge(patient, event, {"active_encounter_id": "ENC-123"})
        
        assert result["encounter_id"] == "ENC-123"
        assert result["discharge_disposition"] == "skilled_nursing"
        assert result["adt_type"] == "A03"
        assert result["status"] == "completed"
    
    def test_handle_lab_order(self, handlers, patient):
        """Test handling lab order event."""
        event = TimelineEvent(
            timeline_event_id="EVT-003",
            event_type="lab_order",
            event_name="Order A1C",
            scheduled_date=date(2024, 1, 15),
            parameters={"loinc": "4548-4", "test_name": "Hemoglobin A1c", "priority": "stat"},
        )
        
        result = handlers.handle_lab_order(patient, event, {})
        
        assert "order_id" in result
        assert result["patient_id"] == "PAT-001"
        assert result["loinc"] == "4548-4"
        assert result["priority"] == "stat"
        assert result["status"] == "ordered"
    
    def test_handle_lab_result_with_order_id(self, handlers, patient):
        """Test lab result with provided order_id."""
        event = TimelineEvent(
            timeline_event_id="EVT-004",
            event_type="lab_result",
            event_name="A1C Result",
            scheduled_date=date(2024, 1, 16),
            parameters={"loinc": "4548-4", "order_id": "ORD-001"},
        )
        
        result = handlers.handle_lab_result(patient, event, {})
        
        assert result["order_id"] == "ORD-001"
        assert result["loinc"] == "4548-4"
        assert result["status"] == "final"
    
    def test_handle_lab_result_glucose(self, handlers, patient):
        """Test lab result for glucose."""
        event = TimelineEvent(
            timeline_event_id="EVT-005",
            event_type="lab_result",
            event_name="Glucose Result",
            scheduled_date=date(2024, 1, 16),
            parameters={"loinc": "2345-7", "test_name": "Glucose"},
        )
        
        result = handlers.handle_lab_result(patient, event, {})
        
        assert result["loinc"] == "2345-7"
        assert result["unit"] == "mg/dL"
    
    def test_handle_lab_result_egfr(self, handlers, patient):
        """Test lab result for eGFR."""
        event = TimelineEvent(
            timeline_event_id="EVT-006",
            event_type="lab_result",
            event_name="eGFR Result",
            scheduled_date=date(2024, 1, 16),
            parameters={"loinc": "33914-3", "test_name": "eGFR"},
        )
        
        result = handlers.handle_lab_result(patient, event, {})
        
        assert result["loinc"] == "33914-3"
        assert result["unit"] == "mL/min/1.73m2"
    
    def test_handle_lab_result_unknown_loinc(self, handlers, patient):
        """Test lab result for unknown LOINC code."""
        event = TimelineEvent(
            timeline_event_id="EVT-007",
            event_type="lab_result",
            event_name="Unknown Result",
            scheduled_date=date(2024, 1, 16),
            parameters={"loinc": "99999-9", "test_name": "Unknown Test"},
        )
        
        result = handlers.handle_lab_result(patient, event, {})
        
        assert result["unit"] == "unit"
    
    def test_handle_encounter_with_specialty(self, handlers, patient):
        """Test encounter with specialty provider."""
        event = TimelineEvent(
            timeline_event_id="EVT-008",
            event_type="encounter",
            event_name="Specialist Visit",
            scheduled_date=date(2024, 1, 15),
            parameters={"specialty": "Endocrinology"},
        )
        
        result = handlers.handle_encounter(patient, event, {})
        
        assert result["provider"]["specialty"] == "Endocrinology"
    
    def test_get_entity_id_from_object(self, handlers):
        """Test extracting entity ID from object."""
        class MockPatient:
            patient_id = "PAT-OBJ"
        
        patient = MockPatient()
        event = TimelineEvent(
            timeline_event_id="EVT-001",
            event_type="encounter",
            event_name="Visit",
            scheduled_date=date(2024, 1, 15),
        )
        
        result = handlers.handle_encounter(patient, event, {})
        assert result["patient_id"] == "PAT-OBJ"
    
    def test_patient_without_diabetes(self, handlers):
        """Test A1C for patient without diabetes."""
        patient = {"patient_id": "PAT-002", "conditions": []}
        event = TimelineEvent(
            timeline_event_id="EVT-001",
            event_type="lab_result",
            event_name="A1C",
            scheduled_date=date(2024, 1, 15),
            parameters={"loinc": "4548-4"},
        )
        
        result = handlers.handle_lab_result(patient, event, {})
        
        # Non-diabetic should have normal A1C range
        assert result["value"] < 8.0  # Most likely normal


class TestMemberSimHandlersExtended:
    """Extended tests for MemberSim event handlers."""
    
    @pytest.fixture
    def handlers(self):
        return MemberSimHandlers(seed=42)
    
    @pytest.fixture
    def member(self):
        return {"member_id": "MBR-001", "id": "MBR-001", "subscriber_id": "SUB-001"}
    
    def test_handle_disenrollment(self, handlers, member):
        """Test handling disenrollment event."""
        event = TimelineEvent(
            timeline_event_id="EVT-001",
            event_type="disenrollment",
            event_name="Disenrollment",
            scheduled_date=date(2024, 12, 31),
            parameters={"reason": "moved_out_of_area"},
        )
        
        result = handlers.handle_disenrollment(member, event, {})
        
        assert "disenrollment_id" in result
        assert result["member_id"] == "MBR-001"
        assert result["reason"] == "moved_out_of_area"
        assert result["status"] == "terminated"
    
    def test_handle_claim_with_charge(self, handlers, member):
        """Test claim with specified charge amount."""
        event = TimelineEvent(
            timeline_event_id="EVT-002",
            event_type="claim",
            event_name="Claim",
            scheduled_date=date(2024, 3, 15),
            parameters={"charge": 500.00, "claim_type": "INSTITUTIONAL"},
        )
        
        result = handlers.handle_claim(member, event, {})
        
        assert result["total_charge"] == 500.00
        assert result["claim_type"] == "INSTITUTIONAL"
    
    def test_get_entity_id_from_object(self, handlers):
        """Test extracting entity ID from object."""
        class MockMember:
            member_id = "MBR-OBJ"
        
        member = MockMember()
        event = TimelineEvent(
            timeline_event_id="EVT-001",
            event_type="enrollment",
            event_name="Enrollment",
            scheduled_date=date(2024, 1, 1),
        )
        
        result = handlers.handle_enrollment(member, event, {})
        assert result["member_id"] == "MBR-OBJ"
    
    def test_get_handler(self, handlers):
        """Test getting handlers."""
        assert handlers.get_handler("enrollment") is not None
        assert handlers.get_handler("disenrollment") is not None
        assert handlers.get_handler("claim") is not None
        assert handlers.get_handler("unknown") is None


class TestRxMemberSimHandlersExtended:
    """Extended tests for RxMemberSim event handlers."""
    
    @pytest.fixture
    def handlers(self):
        return RxMemberSimHandlers(seed=42)
    
    @pytest.fixture
    def member(self):
        return {"member_id": "MBR-001", "id": "MBR-001"}
    
    def test_handle_prescription_specific_medication(self, handlers, member):
        """Test prescription with specific medication."""
        event = TimelineEvent(
            timeline_event_id="EVT-001",
            event_type="prescription",
            event_name="New Rx",
            scheduled_date=date(2024, 1, 15),
            parameters={"medication": "lisinopril", "refills": 5},
        )
        
        result = handlers.handle_prescription(member, event, {})
        
        assert result["medication_name"] == "Lisinopril"
        assert result["brand_name"] == "Zestril"
        assert result["refills_authorized"] == 5
    
    def test_handle_prescription_unknown_medication(self, handlers, member):
        """Test prescription with unknown medication defaults to metformin."""
        event = TimelineEvent(
            timeline_event_id="EVT-001",
            event_type="prescription",
            event_name="New Rx",
            scheduled_date=date(2024, 1, 15),
            parameters={"medication": "unknown_drug"},
        )
        
        result = handlers.handle_prescription(member, event, {})
        
        # Falls back to metformin
        assert result["brand_name"] == "Glucophage"
    
    def test_handle_fill_with_cost(self, handlers, member):
        """Test fill with specified cost."""
        event = TimelineEvent(
            timeline_event_id="EVT-002",
            event_type="fill",
            event_name="Rx Fill",
            scheduled_date=date(2024, 1, 20),
            parameters={"cost": 100.00, "quantity": 90, "days_supply": 90},
        )
        
        result = handlers.handle_fill(member, event, {})
        
        assert result["quantity"] == 90
        assert result["days_supply"] == 90
    
    def test_get_entity_id_from_object(self, handlers):
        """Test extracting entity ID from object."""
        class MockMember:
            member_id = "MBR-OBJ"
        
        member = MockMember()
        event = TimelineEvent(
            timeline_event_id="EVT-001",
            event_type="prescription",
            event_name="New Rx",
            scheduled_date=date(2024, 1, 15),
        )
        
        result = handlers.handle_prescription(member, event, {})
        assert result["member_id"] == "MBR-OBJ"
    
    def test_get_handler(self, handlers):
        """Test getting handlers."""
        assert handlers.get_handler("prescription") is not None
        assert handlers.get_handler("fill") is not None
        assert handlers.get_handler("unknown") is None


class TestTrialSimHandlersExtended:
    """Extended tests for TrialSim event handlers."""
    
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
    
    def test_handle_treatment_visit(self, handlers, subject):
        """Test handling treatment visit event."""
        event = TimelineEvent(
            timeline_event_id="EVT-001",
            event_type="treatment_visit",
            event_name="Week 4 Visit",
            scheduled_date=date(2024, 2, 20),
            parameters={"visit_number": 3, "study_day": 28},
        )
        
        result = handlers.handle_treatment_visit(subject, event, {})
        
        assert "visit_id" in result
        assert result["visit_type"] == "TREATMENT"
        assert result["visit_number"] == 3
        assert result["study_day"] == 28
    
    def test_handle_study_completion(self, handlers, subject):
        """Test handling study completion event."""
        event = TimelineEvent(
            timeline_event_id="EVT-002",
            event_type="study_completion",
            event_name="Study Completion",
            scheduled_date=date(2024, 6, 1),
            parameters={"status": "COMPLETED"},
        )
        
        result = handlers.handle_study_completion(subject, event, {})
        
        assert "completion_id" in result
        assert result["completion_status"] == "COMPLETED"
    
    def test_handle_study_discontinuation(self, handlers, subject):
        """Test handling study completion with discontinuation."""
        event = TimelineEvent(
            timeline_event_id="EVT-003",
            event_type="study_completion",
            event_name="Early Termination",
            scheduled_date=date(2024, 4, 1),
            parameters={"status": "DISCONTINUED", "reason": "adverse_event"},
        )
        
        result = handlers.handle_study_completion(subject, event, {})
        
        assert result["completion_status"] == "DISCONTINUED"
        assert result["discontinuation_reason"] == "adverse_event"
    
    def test_handle_screening_ineligible(self, handlers, subject):
        """Test handling ineligible screening."""
        event = TimelineEvent(
            timeline_event_id="EVT-004",
            event_type="screening",
            event_name="Screening",
            scheduled_date=date(2024, 1, 10),
            parameters={"inclusion_met": False, "eligible": False},
        )
        
        result = handlers.handle_screening(subject, event, {})
        
        assert result["inclusion_met"] is False
        assert result["eligible"] is False
    
    def test_handle_adverse_event_serious(self, handlers, subject):
        """Test handling serious adverse event."""
        event = TimelineEvent(
            timeline_event_id="EVT-005",
            event_type="adverse_event",
            event_name="SAE",
            scheduled_date=date(2024, 3, 15),
            parameters={
                "term": "Myocardial Infarction",
                "severity": "SEVERE",
                "serious": True,
                "related": "UNLIKELY",
                "outcome": "RESOLVED_WITH_SEQUELAE",
            },
        )
        
        result = handlers.handle_adverse_event(subject, event, {})
        
        assert result["ae_term"] == "Myocardial Infarction"
        assert result["ae_severity"] == "SEVERE"
        assert result["ae_serious"] is True
        assert result["ae_related"] == "UNLIKELY"
    
    def test_get_entity_id_from_object(self, handlers):
        """Test extracting entity ID from object."""
        class MockSubject:
            usubjid = "STUDY-SUBJ-001"
        
        subject = MockSubject()
        event = TimelineEvent(
            timeline_event_id="EVT-001",
            event_type="screening",
            event_name="Screening",
            scheduled_date=date(2024, 1, 10),
        )
        
        result = handlers.handle_screening(subject, event, {})
        assert result["subject_id"] == "STUDY-SUBJ-001"
    
    def test_get_handler(self, handlers):
        """Test getting handlers."""
        assert handlers.get_handler("screening") is not None
        assert handlers.get_handler("randomization") is not None
        assert handlers.get_handler("treatment_visit") is not None
        assert handlers.get_handler("adverse_event") is not None
        assert handlers.get_handler("study_completion") is not None
        assert handlers.get_handler("unknown") is None


class TestHandlerRegistryExtended:
    """Extended tests for HandlerRegistry."""
    
    @pytest.fixture
    def registry(self):
        return HandlerRegistry(seed=42)
    
    def test_handle_event_membersim(self, registry):
        """Test handling event for membersim."""
        member = {"member_id": "MBR-001"}
        event = TimelineEvent(
            timeline_event_id="EVT-001",
            event_type="enrollment",
            event_name="Enrollment",
            scheduled_date=date(2024, 1, 1),
        )
        
        result = registry.handle_event(
            product="membersim",
            event_type="enrollment",
            entity=member,
            event=event,
            context={},
        )
        
        assert result is not None
        assert "enrollment_id" in result
    
    def test_handle_event_rxmembersim(self, registry):
        """Test handling event for rxmembersim."""
        member = {"member_id": "MBR-001"}
        event = TimelineEvent(
            timeline_event_id="EVT-001",
            event_type="prescription",
            event_name="New Rx",
            scheduled_date=date(2024, 1, 15),
        )
        
        result = registry.handle_event(
            product="rxmembersim",
            event_type="prescription",
            entity=member,
            event=event,
            context={},
        )
        
        assert result is not None
        assert "prescription_id" in result
    
    def test_handle_event_trialsim(self, registry):
        """Test handling event for trialsim."""
        subject = {"usubjid": "STUDY-001"}
        event = TimelineEvent(
            timeline_event_id="EVT-001",
            event_type="screening",
            event_name="Screening",
            scheduled_date=date(2024, 1, 10),
        )
        
        result = registry.handle_event(
            product="trialsim",
            event_type="screening",
            entity=subject,
            event=event,
            context={},
        )
        
        assert result is not None
        assert "visit_id" in result
    
    def test_handle_event_unknown_product(self, registry):
        """Test handling event for unknown product."""
        entity = {"id": "1"}
        event = TimelineEvent(
            timeline_event_id="EVT-001",
            event_type="test",
            event_name="Test",
            scheduled_date=date(2024, 1, 1),
        )
        
        result = registry.handle_event(
            product="unknown",
            event_type="test",
            entity=entity,
            event=event,
            context={},
        )
        
        assert result is None


class TestBaseEventHandlerMethods:
    """Test BaseEventHandler utility methods."""
    
    def test_generate_id_deterministic(self):
        """Test that ID generation is deterministic."""
        handlers1 = PatientSimHandlers(seed=42)
        handlers2 = PatientSimHandlers(seed=42)
        
        id1 = handlers1._generate_id("TEST", "entity1", "event1")
        id2 = handlers2._generate_id("TEST", "entity1", "event1")
        
        assert id1 == id2
    
    def test_generate_id_different_seeds(self):
        """Test that different seeds produce different IDs."""
        handlers1 = PatientSimHandlers(seed=42)
        handlers2 = PatientSimHandlers(seed=123)
        
        id1 = handlers1._generate_id("TEST", "entity1", "event1")
        id2 = handlers2._generate_id("TEST", "entity1", "event1")
        
        assert id1 != id2


class TestTimelineEventStatus:
    """Tests for TimelineEvent status management."""
    
    def test_default_status(self):
        """Test default status is scheduled."""
        event = TimelineEvent(
            timeline_event_id="EVT-001",
            event_type="test",
            event_name="Test",
            scheduled_date=date(2024, 1, 1),
        )
        assert event.status == "scheduled"
    
    def test_completed_status(self):
        """Test setting completed status."""
        event = TimelineEvent(
            timeline_event_id="EVT-001",
            event_type="test",
            event_name="Test",
            scheduled_date=date(2024, 1, 1),
            status="completed",
        )
        assert event.status == "completed"
    
    def test_with_result(self):
        """Test event with result."""
        event = TimelineEvent(
            timeline_event_id="EVT-001",
            event_type="test",
            event_name="Test",
            scheduled_date=date(2024, 1, 1),
            result={"data": "test"},
            status="completed",
        )
        assert event.result == {"data": "test"}
