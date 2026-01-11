"""Core data models for TrialSim.

Enhanced with clinical data models for comprehensive SDTM support:
- VitalSign (VS domain)
- LabResult (LB domain)
- MedicalHistory (MH domain)
- ConcomitantMedication (CM domain)
- EligibilityCriteria (IE domain)
"""

from datetime import date
from decimal import Decimal
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


# =============================================================================
# Enumerations
# =============================================================================

class ArmType(str, Enum):
    """Treatment arm types."""
    TREATMENT = "treatment"
    PLACEBO = "placebo"
    ACTIVE_COMPARATOR = "active_comparator"
    NO_INTERVENTION = "no_intervention"


class SubjectStatus(str, Enum):
    """Subject enrollment status."""
    SCREENING = "screening"
    SCREEN_FAILED = "screen_failed"
    ENROLLED = "enrolled"
    RANDOMIZED = "randomized"
    ON_TREATMENT = "on_treatment"
    COMPLETED = "completed"
    WITHDRAWN = "withdrawn"
    LOST_TO_FOLLOWUP = "lost_to_followup"


class VisitType(str, Enum):
    """Visit classification."""
    SCREENING = "screening"
    BASELINE = "baseline"
    RANDOMIZATION = "randomization"
    SCHEDULED = "scheduled"
    UNSCHEDULED = "unscheduled"
    EARLY_TERMINATION = "early_termination"
    FOLLOW_UP = "follow_up"
    END_OF_STUDY = "end_of_study"


class AESeverity(str, Enum):
    """Adverse event severity (CTCAE grading)."""
    GRADE_1 = "grade_1_mild"
    GRADE_2 = "grade_2_moderate"
    GRADE_3 = "grade_3_severe"
    GRADE_4 = "grade_4_life_threatening"
    GRADE_5 = "grade_5_death"


class AECausality(str, Enum):
    """Adverse event causality assessment."""
    NOT_RELATED = "not_related"
    UNLIKELY = "unlikely"
    POSSIBLY = "possibly"
    PROBABLY = "probably"
    DEFINITELY = "definitely"


class AEOutcome(str, Enum):
    """Adverse event outcome."""
    RECOVERED = "recovered"
    RECOVERING = "recovering"
    NOT_RECOVERED = "not_recovered"
    RECOVERED_WITH_SEQUELAE = "recovered_with_sequelae"
    FATAL = "fatal"
    UNKNOWN = "unknown"


class LabCategory(str, Enum):
    """Laboratory test categories."""
    HEMATOLOGY = "hematology"
    CHEMISTRY = "chemistry"
    URINALYSIS = "urinalysis"
    COAGULATION = "coagulation"
    IMMUNOLOGY = "immunology"
    MICROBIOLOGY = "microbiology"


class CriterionType(str, Enum):
    """Eligibility criterion type."""
    INCLUSION = "inclusion"
    EXCLUSION = "exclusion"


# =============================================================================
# Core Models
# =============================================================================

class Site(BaseModel):
    """Clinical trial site."""
    site_id: str = Field(default_factory=lambda: f"SITE-{uuid4().hex[:8].upper()}")
    name: str
    country: str = "USA"
    region: str | None = None
    principal_investigator: str | None = None
    is_active: bool = True
    activation_date: date | None = None

    model_config = {"frozen": False}


class Protocol(BaseModel):
    """Clinical trial protocol definition."""
    protocol_id: str
    study_title: str
    phase: str = "Phase 3"
    therapeutic_area: str = "Oncology"
    indication: str | None = None
    sponsor: str | None = None
    arms: list[dict[str, Any]] = Field(default_factory=list)
    planned_enrollment: int = 100
    duration_weeks: int = 52
    visit_schedule: list[dict[str, Any]] = Field(default_factory=list)

    model_config = {"frozen": False}


class Subject(BaseModel):
    """Clinical trial subject."""
    subject_id: str = Field(default_factory=lambda: f"SUBJ-{uuid4().hex[:8].upper()}")
    protocol_id: str
    site_id: str

    age: int
    sex: str = "M"
    race: str | None = None
    ethnicity: str | None = None

    screening_date: date | None = None
    randomization_date: date | None = None
    arm: ArmType | None = None
    status: SubjectStatus = SubjectStatus.SCREENING

    patient_id: str | None = None

    model_config = {"frozen": False}


class Visit(BaseModel):
    """Clinical trial visit record."""
    visit_id: str = Field(default_factory=lambda: f"VST-{uuid4().hex[:8].upper()}")
    subject_id: str
    protocol_id: str
    site_id: str

    visit_number: int
    visit_name: str
    visit_type: VisitType = VisitType.SCHEDULED

    planned_date: date | None = None
    actual_date: date | None = None
    visit_status: str = "scheduled"

    assessments: list[str] = Field(default_factory=list)

    model_config = {"frozen": False}


class AdverseEvent(BaseModel):
    """Adverse event record with MedDRA coding."""
    ae_id: str = Field(default_factory=lambda: f"AE-{uuid4().hex[:8].upper()}")
    subject_id: str
    protocol_id: str

    ae_term: str
    ae_description: str | None = None
    system_organ_class: str | None = None
    
    # MedDRA coding
    meddra_pt_code: str | None = Field(None, description="MedDRA Preferred Term code")
    meddra_pt_name: str | None = Field(None, description="MedDRA Preferred Term name")
    meddra_soc_code: str | None = Field(None, description="MedDRA SOC code")
    meddra_llt_code: str | None = Field(None, description="MedDRA LLT code")

    onset_date: date
    resolution_date: date | None = None
    duration_days: int | None = None

    severity: AESeverity = AESeverity.GRADE_1
    is_serious: bool = False
    causality: AECausality = AECausality.POSSIBLY
    outcome: AEOutcome = AEOutcome.RECOVERED

    action_taken: str | None = None
    treatment_required: bool = False

    model_config = {"frozen": False}


class Exposure(BaseModel):
    """Drug exposure record."""
    exposure_id: str = Field(default_factory=lambda: f"EXP-{uuid4().hex[:8].upper()}")
    subject_id: str
    protocol_id: str

    drug_name: str
    drug_code: str | None = None
    dose: float
    dose_unit: str = "mg"
    route: str = "oral"

    start_date: date
    end_date: date | None = None

    doses_planned: int = 1
    doses_taken: int = 1
    compliance_pct: float = 100.0

    model_config = {"frozen": False}


# =============================================================================
# Clinical Data Models (NEW)
# =============================================================================

class VitalSign(BaseModel):
    """Vital signs measurement (SDTM VS domain)."""
    vs_id: str = Field(default_factory=lambda: f"VS-{uuid4().hex[:8].upper()}")
    subject_id: str
    protocol_id: str
    visit_id: str | None = None
    
    # Test identification
    vs_test: str = Field(..., description="Vital sign test name (e.g., SYSBP, DIABP)")
    vs_test_name: str = Field(..., description="Full test name")
    
    # Result
    vs_result: float = Field(..., description="Numeric result")
    vs_unit: str = Field(..., description="Unit of measure")
    vs_position: str | None = Field(None, description="Position (STANDING, SITTING, SUPINE)")
    vs_location: str | None = Field(None, description="Location (LEFT ARM, RIGHT ARM)")
    
    # Date/time
    collection_date: date = Field(..., description="Collection date")
    collection_time: str | None = Field(None, description="Collection time HH:MM")
    
    model_config = {"frozen": False}


class LabResult(BaseModel):
    """Laboratory result (SDTM LB domain)."""
    lb_id: str = Field(default_factory=lambda: f"LB-{uuid4().hex[:8].upper()}")
    subject_id: str
    protocol_id: str
    visit_id: str | None = None
    
    # Test identification
    lb_test: str = Field(..., description="Lab test code (e.g., ALT, AST, HGB)")
    lb_test_name: str = Field(..., description="Full test name")
    lb_category: LabCategory = Field(LabCategory.CHEMISTRY, description="Test category")
    lb_spec: str = Field("BLOOD", description="Specimen type")
    
    # Result
    lb_result: float | None = Field(None, description="Numeric result")
    lb_result_c: str | None = Field(None, description="Character result")
    lb_unit: str | None = Field(None, description="Unit of measure")
    
    # Reference range
    lb_low: float | None = Field(None, description="Lower reference limit")
    lb_high: float | None = Field(None, description="Upper reference limit")
    lb_flag: str | None = Field(None, description="Flag (N=normal, L=low, H=high)")
    
    # Date/time
    collection_date: date = Field(..., description="Collection date")
    collection_time: str | None = Field(None, description="Collection time HH:MM")
    
    # LOINC coding
    loinc_code: str | None = Field(None, description="LOINC code")
    
    model_config = {"frozen": False}


class MedicalHistory(BaseModel):
    """Medical history record (SDTM MH domain)."""
    mh_id: str = Field(default_factory=lambda: f"MH-{uuid4().hex[:8].upper()}")
    subject_id: str
    protocol_id: str
    
    # Condition
    mh_term: str = Field(..., description="Medical history term")
    mh_category: str | None = Field(None, description="Category (e.g., CARDIOVASCULAR)")
    
    # MedDRA coding
    meddra_pt_code: str | None = Field(None, description="MedDRA PT code")
    meddra_soc: str | None = Field(None, description="System Organ Class")
    
    # Dates
    start_date: date | None = Field(None, description="Condition start date")
    end_date: date | None = Field(None, description="Condition end date")
    is_ongoing: bool = Field(True, description="Is condition ongoing")
    
    # Status
    is_preexisting: bool = Field(True, description="Existed prior to study")
    
    model_config = {"frozen": False}


class ConcomitantMedication(BaseModel):
    """Concomitant medication record (SDTM CM domain)."""
    cm_id: str = Field(default_factory=lambda: f"CM-{uuid4().hex[:8].upper()}")
    subject_id: str
    protocol_id: str
    
    # Drug identification
    cm_drug: str = Field(..., description="Drug name")
    cm_class: str | None = Field(None, description="Drug class")
    atc_code: str | None = Field(None, description="ATC code")
    
    # Dosing
    dose: float | None = Field(None, description="Dose amount")
    dose_unit: str | None = Field(None, description="Dose unit")
    frequency: str | None = Field(None, description="Dosing frequency")
    route: str | None = Field(None, description="Route of administration")
    
    # Indication
    indication: str | None = Field(None, description="Indication for use")
    
    # Dates
    start_date: date | None = Field(None, description="Start date")
    end_date: date | None = Field(None, description="End date")
    is_ongoing: bool = Field(True, description="Is medication ongoing")
    
    # Prior/concomitant
    is_prior: bool = Field(False, description="Started before study")
    
    model_config = {"frozen": False}


class EligibilityCriterion(BaseModel):
    """Eligibility criterion assessment (SDTM IE domain)."""
    ie_id: str = Field(default_factory=lambda: f"IE-{uuid4().hex[:8].upper()}")
    subject_id: str
    protocol_id: str
    
    # Criterion
    criterion_id: str = Field(..., description="Criterion identifier (e.g., IN01, EX03)")
    criterion_type: CriterionType = Field(..., description="Inclusion or exclusion")
    criterion_text: str = Field(..., description="Criterion description")
    
    # Assessment
    is_met: bool = Field(..., description="Was criterion met")
    assessment_date: date = Field(..., description="Assessment date")
    
    # Comments
    comment: str | None = Field(None, description="Comment if not met")
    
    model_config = {"frozen": False}


__all__ = [
    # Enums
    "ArmType",
    "SubjectStatus",
    "VisitType",
    "AESeverity",
    "AECausality",
    "AEOutcome",
    "LabCategory",
    "CriterionType",
    # Core models
    "Site",
    "Protocol",
    "Subject",
    "Visit",
    "AdverseEvent",
    "Exposure",
    # Clinical data models
    "VitalSign",
    "LabResult",
    "MedicalHistory",
    "ConcomitantMedication",
    "EligibilityCriterion",
]
