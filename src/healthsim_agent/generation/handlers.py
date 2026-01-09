"""
Event handlers for healthcare journey events.

Product-specific handlers that generate data when timeline events occur:
- PatientSim: Clinical events (encounters, diagnoses, labs)
- MemberSim: Enrollment and claims events
- RxMemberSim: Prescription events
- TrialSim: Clinical trial events

Ported from: healthsim-workspace/packages/core/src/healthsim/generation/handlers.py
"""

import hashlib
import random
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import Any, Callable, Protocol


@dataclass
class TimelineEvent:
    """Represents an event on a patient/member timeline."""
    timeline_event_id: str
    event_type: str
    event_name: str
    scheduled_date: date
    parameters: dict[str, Any] = field(default_factory=dict)
    result: dict[str, Any] | None = None
    status: str = "scheduled"  # scheduled, completed, cancelled


class EventHandler(Protocol):
    """Protocol for event handlers."""
    
    def __call__(
        self,
        entity: Any,
        event: TimelineEvent,
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """Handle an event and return generated data."""
        ...


class BaseEventHandler(ABC):
    """Base class for event handlers with common utilities."""
    
    def __init__(self, seed: int | None = None):
        self.seed = seed
        self._rng = random.Random(seed)
    
    def _generate_id(self, prefix: str, entity_id: str, event_id: str) -> str:
        """Generate a deterministic ID."""
        combined = f"{self.seed or 0}:{entity_id}:{event_id}"
        hash_val = hashlib.md5(combined.encode()).hexdigest()[:8]
        return f"{prefix}-{hash_val.upper()}"
    
    def _generate_uuid(self, entity_id: str, event_id: str) -> str:
        """Generate a deterministic UUID."""
        combined = f"{self.seed or 0}:{entity_id}:{event_id}"
        hash_bytes = hashlib.md5(combined.encode()).digest()
        return str(uuid.UUID(bytes=hash_bytes[:16]))
    
    @abstractmethod
    def handle(
        self,
        entity: Any,
        event: TimelineEvent,
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """Handle the event and return results."""
        pass
    
    def __call__(
        self,
        entity: Any,
        event: TimelineEvent,
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """Make handler callable."""
        return self.handle(entity, event, context)


# =============================================================================
# PatientSim Handlers
# =============================================================================

class PatientSimHandlers:
    """Collection of PatientSim event handlers."""
    
    def __init__(self, seed: int | None = None):
        self.seed = seed
        self._rng = random.Random(seed)
        
        self.default_facility = {
            "facility_id": "FAC-001",
            "name": "Community General Hospital",
            "npi": "1234567890",
            "address": {"city": "Austin", "state": "TX", "zip": "78701"}
        }
        
        self.providers = [
            {"provider_id": "PROV-001", "name": "Dr. Sarah Chen", "npi": "1111111111", "specialty": "Internal Medicine"},
            {"provider_id": "PROV-002", "name": "Dr. Michael Brown", "npi": "2222222222", "specialty": "Family Medicine"},
            {"provider_id": "PROV-003", "name": "Dr. Lisa Rodriguez", "npi": "3333333333", "specialty": "Endocrinology"},
        ]
    
    def _get_entity_id(self, entity: Any) -> str:
        if isinstance(entity, dict):
            return entity.get("patient_id", entity.get("id", "unknown"))
        return getattr(entity, "patient_id", getattr(entity, "id", "unknown"))
    
    def _select_provider(self, specialty: str | None = None) -> dict:
        if specialty:
            matching = [p for p in self.providers if p["specialty"] == specialty]
            if matching:
                return self._rng.choice(matching)
        return self._rng.choice(self.providers)
    
    def handle_admission(
        self,
        entity: Any,
        event: TimelineEvent,
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """Handle patient admission event."""
        patient_id = self._get_entity_id(entity)
        params = event.parameters
        
        encounter_id = self._generate_id("ENC", patient_id, event.timeline_event_id)
        
        return {
            "encounter_id": encounter_id,
            "patient_id": patient_id,
            "encounter_type": "inpatient",
            "admission_date": event.scheduled_date.isoformat(),
            "admission_type": params.get("admission_type", "elective"),
            "facility": self.default_facility,
            "attending_provider": self._select_provider(),
            "status": "active",
            "adt_type": "A01",
        }
    
    def handle_discharge(
        self,
        entity: Any,
        event: TimelineEvent,
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """Handle patient discharge event."""
        patient_id = self._get_entity_id(entity)
        params = event.parameters
        
        encounter_id = context.get("active_encounter_id", 
                                   self._generate_id("ENC", patient_id, event.timeline_event_id))
        
        return {
            "encounter_id": encounter_id,
            "patient_id": patient_id,
            "discharge_date": event.scheduled_date.isoformat(),
            "discharge_disposition": params.get("disposition", "home"),
            "discharge_status": params.get("status", "alive"),
            "status": "completed",
            "adt_type": "A03",
        }
    
    def handle_encounter(
        self,
        entity: Any,
        event: TimelineEvent,
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """Handle outpatient encounter event."""
        patient_id = self._get_entity_id(entity)
        params = event.parameters
        
        encounter_id = self._generate_id("ENC", patient_id, event.timeline_event_id)
        
        return {
            "encounter_id": encounter_id,
            "patient_id": patient_id,
            "encounter_type": params.get("encounter_type", "outpatient"),
            "encounter_date": event.scheduled_date.isoformat(),
            "reason": params.get("reason", event.event_name),
            "facility": self.default_facility,
            "provider": self._select_provider(params.get("specialty")),
            "status": "completed",
        }
    
    def handle_diagnosis(
        self,
        entity: Any,
        event: TimelineEvent,
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """Handle diagnosis event."""
        patient_id = self._get_entity_id(entity)
        params = event.parameters
        
        condition_id = self._generate_id("COND", patient_id, event.timeline_event_id)
        
        return {
            "condition_id": condition_id,
            "patient_id": patient_id,
            "icd10": params.get("icd10", "R69"),
            "description": params.get("description", "Illness, unspecified"),
            "onset_date": event.scheduled_date.isoformat(),
            "clinical_status": "active",
            "verification_status": "confirmed",
            "category": params.get("category", "encounter-diagnosis"),
        }
    
    def handle_lab_order(
        self,
        entity: Any,
        event: TimelineEvent,
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """Handle laboratory order event."""
        patient_id = self._get_entity_id(entity)
        params = event.parameters
        
        order_id = self._generate_id("ORD", patient_id, event.timeline_event_id)
        
        return {
            "order_id": order_id,
            "patient_id": patient_id,
            "order_type": "laboratory",
            "loinc": params.get("loinc", "4548-4"),
            "test_name": params.get("test_name", "Hemoglobin A1c"),
            "order_date": event.scheduled_date.isoformat(),
            "ordering_provider": self._select_provider(),
            "status": "ordered",
            "priority": params.get("priority", "routine"),
        }
    
    def handle_lab_result(
        self,
        entity: Any,
        event: TimelineEvent,
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """Handle laboratory result event."""
        patient_id = self._get_entity_id(entity)
        params = event.parameters
        
        result_id = self._generate_id("RES", patient_id, event.timeline_event_id)
        order_id = params.get("order_id", context.get("last_order_id"))
        
        loinc = params.get("loinc", "4548-4")
        value, unit = self._generate_lab_value(loinc, entity)
        
        return {
            "result_id": result_id,
            "order_id": order_id,
            "patient_id": patient_id,
            "loinc": loinc,
            "test_name": params.get("test_name", "Lab Test"),
            "value": value,
            "unit": unit,
            "result_date": event.scheduled_date.isoformat(),
            "status": "final",
            "interpretation": self._interpret_lab_value(loinc, value),
        }
    
    def _generate_id(self, prefix: str, entity_id: str, event_id: str) -> str:
        combined = f"{self.seed or 0}:{entity_id}:{event_id}"
        hash_val = hashlib.md5(combined.encode()).hexdigest()[:8]
        return f"{prefix}-{hash_val.upper()}"
    
    def _generate_lab_value(self, loinc: str, entity: Any) -> tuple[float, str]:
        """Generate realistic lab value based on LOINC code."""
        # A1C
        if loinc == "4548-4":
            has_diabetes = False
            if isinstance(entity, dict):
                conditions = entity.get("conditions", [])
                has_diabetes = any("E11" in str(c) for c in conditions)
            
            if has_diabetes:
                value = self._rng.gauss(7.8, 1.2)
            else:
                value = self._rng.gauss(5.4, 0.3)
            return round(max(4.0, min(14.0, value)), 1), "%"
        
        # Glucose
        elif loinc == "2345-7":
            return round(self._rng.gauss(100, 25), 0), "mg/dL"
        
        # eGFR
        elif loinc == "33914-3":
            return round(self._rng.gauss(75, 20), 0), "mL/min/1.73m2"
        
        # Default
        return round(self._rng.gauss(100, 10), 1), "unit"
    
    def _interpret_lab_value(self, loinc: str, value: float) -> str:
        """Interpret lab value."""
        if loinc == "4548-4":  # A1C
            if value < 5.7:
                return "N"  # Normal
            elif value < 6.5:
                return "H"  # High (prediabetes)
            else:
                return "HH"  # Very high (diabetes)
        return "N"
    
    def get_handler(self, event_type: str) -> Callable | None:
        """Get handler for event type."""
        handlers = {
            "admission": self.handle_admission,
            "discharge": self.handle_discharge,
            "encounter": self.handle_encounter,
            "diagnosis": self.handle_diagnosis,
            "lab_order": self.handle_lab_order,
            "lab_result": self.handle_lab_result,
        }
        return handlers.get(event_type)


# =============================================================================
# MemberSim Handlers
# =============================================================================

class MemberSimHandlers:
    """Collection of MemberSim event handlers."""
    
    def __init__(self, seed: int | None = None):
        self.seed = seed
        self._rng = random.Random(seed)
    
    def _get_entity_id(self, entity: Any) -> str:
        if isinstance(entity, dict):
            return entity.get("member_id", entity.get("id", "unknown"))
        return getattr(entity, "member_id", getattr(entity, "id", "unknown"))
    
    def _generate_id(self, prefix: str, entity_id: str, event_id: str) -> str:
        combined = f"{self.seed or 0}:{entity_id}:{event_id}"
        hash_val = hashlib.md5(combined.encode()).hexdigest()[:8]
        return f"{prefix}-{hash_val.upper()}"
    
    def handle_enrollment(
        self,
        entity: Any,
        event: TimelineEvent,
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """Handle member enrollment event."""
        member_id = self._get_entity_id(entity)
        params = event.parameters
        
        return {
            "enrollment_id": self._generate_id("ENR", member_id, event.timeline_event_id),
            "member_id": member_id,
            "enrollment_date": event.scheduled_date.isoformat(),
            "plan_code": params.get("plan_code", "PPO-001"),
            "coverage_type": params.get("coverage_type", "Commercial"),
            "status": "active",
        }
    
    def handle_disenrollment(
        self,
        entity: Any,
        event: TimelineEvent,
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """Handle member disenrollment event."""
        member_id = self._get_entity_id(entity)
        params = event.parameters
        
        return {
            "disenrollment_id": self._generate_id("DIS", member_id, event.timeline_event_id),
            "member_id": member_id,
            "disenrollment_date": event.scheduled_date.isoformat(),
            "reason": params.get("reason", "voluntary"),
            "status": "terminated",
        }
    
    def handle_claim(
        self,
        entity: Any,
        event: TimelineEvent,
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """Handle claim submission event."""
        member_id = self._get_entity_id(entity)
        params = event.parameters
        
        claim_id = self._generate_id("CLM", member_id, event.timeline_event_id)
        
        total_charge = params.get("charge", self._rng.uniform(100, 2000))
        allowed = total_charge * self._rng.uniform(0.5, 0.8)
        paid = allowed * self._rng.uniform(0.7, 0.95)
        
        return {
            "claim_id": claim_id,
            "member_id": member_id,
            "claim_type": params.get("claim_type", "PROFESSIONAL"),
            "service_date": event.scheduled_date.isoformat(),
            "provider_npi": params.get("provider_npi", "1234567890"),
            "principal_diagnosis": params.get("diagnosis", "R69"),
            "procedure_code": params.get("procedure", "99213"),
            "total_charge": round(total_charge, 2),
            "total_allowed": round(allowed, 2),
            "total_paid": round(paid, 2),
            "status": "paid",
        }
    
    def get_handler(self, event_type: str) -> Callable | None:
        """Get handler for event type."""
        handlers = {
            "enrollment": self.handle_enrollment,
            "disenrollment": self.handle_disenrollment,
            "claim": self.handle_claim,
        }
        return handlers.get(event_type)


# =============================================================================
# RxMemberSim Handlers
# =============================================================================

class RxMemberSimHandlers:
    """Collection of RxMemberSim event handlers."""
    
    # Common medications
    MEDICATIONS = {
        "metformin": {"ndc": "00378-0080-01", "brand": "Glucophage", "strength": "500mg"},
        "lisinopril": {"ndc": "00378-1831-01", "brand": "Zestril", "strength": "10mg"},
        "atorvastatin": {"ndc": "00378-4083-01", "brand": "Lipitor", "strength": "20mg"},
        "omeprazole": {"ndc": "00378-1840-01", "brand": "Prilosec", "strength": "20mg"},
        "amlodipine": {"ndc": "00378-1082-01", "brand": "Norvasc", "strength": "5mg"},
    }
    
    def __init__(self, seed: int | None = None):
        self.seed = seed
        self._rng = random.Random(seed)
    
    def _get_entity_id(self, entity: Any) -> str:
        if isinstance(entity, dict):
            return entity.get("member_id", entity.get("id", "unknown"))
        return getattr(entity, "member_id", getattr(entity, "id", "unknown"))
    
    def _generate_id(self, prefix: str, entity_id: str, event_id: str) -> str:
        combined = f"{self.seed or 0}:{entity_id}:{event_id}"
        hash_val = hashlib.md5(combined.encode()).hexdigest()[:8]
        return f"{prefix}-{hash_val.upper()}"
    
    def handle_prescription(
        self,
        entity: Any,
        event: TimelineEvent,
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """Handle new prescription event."""
        member_id = self._get_entity_id(entity)
        params = event.parameters
        
        med_name = params.get("medication", self._rng.choice(list(self.MEDICATIONS.keys())))
        med_info = self.MEDICATIONS.get(med_name, self.MEDICATIONS["metformin"])
        
        rx_number = self._generate_id("RX", member_id, event.timeline_event_id)
        
        return {
            "prescription_id": rx_number,
            "rx_number": rx_number,
            "member_id": member_id,
            "prescriber_npi": params.get("prescriber_npi", "1234567890"),
            "medication_name": med_name.title(),
            "brand_name": med_info["brand"],
            "ndc": med_info["ndc"],
            "strength": med_info["strength"],
            "quantity": params.get("quantity", 30),
            "days_supply": params.get("days_supply", 30),
            "refills_authorized": params.get("refills", 3),
            "written_date": event.scheduled_date.isoformat(),
            "status": "active",
        }
    
    def handle_fill(
        self,
        entity: Any,
        event: TimelineEvent,
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """Handle prescription fill event."""
        member_id = self._get_entity_id(entity)
        params = event.parameters
        
        fill_id = self._generate_id("FILL", member_id, event.timeline_event_id)
        
        # Cost breakdown
        total_cost = params.get("cost", self._rng.uniform(10, 200))
        plan_paid = total_cost * self._rng.uniform(0.7, 0.9)
        member_paid = total_cost - plan_paid
        
        return {
            "fill_id": fill_id,
            "prescription_id": params.get("prescription_id", context.get("last_rx_id")),
            "member_id": member_id,
            "pharmacy_npi": params.get("pharmacy_npi", "9876543210"),
            "fill_date": event.scheduled_date.isoformat(),
            "ndc": params.get("ndc", "00378-0080-01"),
            "quantity": params.get("quantity", 30),
            "days_supply": params.get("days_supply", 30),
            "total_cost": round(total_cost, 2),
            "plan_paid": round(plan_paid, 2),
            "member_paid": round(member_paid, 2),
            "refill_number": params.get("refill_number", 0),
            "daw_code": "0",  # Dispense as written
            "status": "completed",
        }
    
    def get_handler(self, event_type: str) -> Callable | None:
        """Get handler for event type."""
        handlers = {
            "prescription": self.handle_prescription,
            "fill": self.handle_fill,
        }
        return handlers.get(event_type)


# =============================================================================
# TrialSim Handlers
# =============================================================================

class TrialSimHandlers:
    """Collection of TrialSim event handlers."""
    
    def __init__(self, seed: int | None = None):
        self.seed = seed
        self._rng = random.Random(seed)
    
    def _get_entity_id(self, entity: Any) -> str:
        if isinstance(entity, dict):
            return entity.get("usubjid", entity.get("subject_id", entity.get("id", "unknown")))
        return getattr(entity, "usubjid", getattr(entity, "subject_id", "unknown"))
    
    def _generate_id(self, prefix: str, entity_id: str, event_id: str) -> str:
        combined = f"{self.seed or 0}:{entity_id}:{event_id}"
        hash_val = hashlib.md5(combined.encode()).hexdigest()[:8]
        return f"{prefix}-{hash_val.upper()}"
    
    def handle_screening(
        self,
        entity: Any,
        event: TimelineEvent,
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """Handle screening visit event."""
        subject_id = self._get_entity_id(entity)
        params = event.parameters
        
        return {
            "visit_id": self._generate_id("VIS", subject_id, event.timeline_event_id),
            "subject_id": subject_id,
            "visit_type": "SCREENING",
            "visit_date": event.scheduled_date.isoformat(),
            "visit_status": "COMPLETED",
            "inclusion_met": params.get("inclusion_met", True),
            "exclusion_met": params.get("exclusion_met", False),
            "eligible": params.get("eligible", True),
        }
    
    def handle_randomization(
        self,
        entity: Any,
        event: TimelineEvent,
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """Handle randomization event."""
        subject_id = self._get_entity_id(entity)
        params = event.parameters
        
        arms = params.get("arms", ["Treatment", "Placebo"])
        arm = params.get("assigned_arm", self._rng.choice(arms))
        
        return {
            "randomization_id": self._generate_id("RND", subject_id, event.timeline_event_id),
            "subject_id": subject_id,
            "randomization_date": event.scheduled_date.isoformat(),
            "treatment_arm": arm,
            "stratification_factors": params.get("strata", {}),
        }
    
    def handle_treatment_visit(
        self,
        entity: Any,
        event: TimelineEvent,
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """Handle treatment period visit event."""
        subject_id = self._get_entity_id(entity)
        params = event.parameters
        
        return {
            "visit_id": self._generate_id("VIS", subject_id, event.timeline_event_id),
            "subject_id": subject_id,
            "visit_type": "TREATMENT",
            "visit_number": params.get("visit_number", 1),
            "visit_date": event.scheduled_date.isoformat(),
            "visit_status": "COMPLETED",
            "study_day": params.get("study_day", 1),
        }
    
    def handle_adverse_event(
        self,
        entity: Any,
        event: TimelineEvent,
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """Handle adverse event."""
        subject_id = self._get_entity_id(entity)
        params = event.parameters
        
        return {
            "ae_id": self._generate_id("AE", subject_id, event.timeline_event_id),
            "subject_id": subject_id,
            "ae_term": params.get("term", "Headache"),
            "ae_start_date": event.scheduled_date.isoformat(),
            "ae_severity": params.get("severity", "MILD"),
            "ae_serious": params.get("serious", False),
            "ae_related": params.get("related", "POSSIBLY"),
            "ae_outcome": params.get("outcome", "RESOLVED"),
        }
    
    def handle_study_completion(
        self,
        entity: Any,
        event: TimelineEvent,
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """Handle study completion event."""
        subject_id = self._get_entity_id(entity)
        params = event.parameters
        
        return {
            "completion_id": self._generate_id("CMP", subject_id, event.timeline_event_id),
            "subject_id": subject_id,
            "completion_date": event.scheduled_date.isoformat(),
            "completion_status": params.get("status", "COMPLETED"),
            "discontinuation_reason": params.get("reason"),
        }
    
    def get_handler(self, event_type: str) -> Callable | None:
        """Get handler for event type."""
        handlers = {
            "screening": self.handle_screening,
            "randomization": self.handle_randomization,
            "treatment_visit": self.handle_treatment_visit,
            "adverse_event": self.handle_adverse_event,
            "study_completion": self.handle_study_completion,
        }
        return handlers.get(event_type)


# =============================================================================
# Handler Registry
# =============================================================================

class HandlerRegistry:
    """Registry for all product event handlers."""
    
    def __init__(self, seed: int | None = None):
        self.seed = seed
        self._handlers = {
            "patientsim": PatientSimHandlers(seed),
            "membersim": MemberSimHandlers(seed),
            "rxmembersim": RxMemberSimHandlers(seed),
            "trialsim": TrialSimHandlers(seed),
        }
    
    def get_handlers(self, product: str) -> Any:
        """Get handlers for a product."""
        return self._handlers.get(product.lower())
    
    def handle_event(
        self,
        product: str,
        event_type: str,
        entity: Any,
        event: TimelineEvent,
        context: dict[str, Any],
    ) -> dict[str, Any] | None:
        """Handle an event using the appropriate product handler."""
        handlers = self.get_handlers(product)
        if not handlers:
            return None
        
        handler = handlers.get_handler(event_type)
        if not handler:
            return None
        
        return handler(entity, event, context)
