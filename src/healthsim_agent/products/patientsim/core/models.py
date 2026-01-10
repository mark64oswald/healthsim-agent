"""Core data models for PatientSim.

Ported from: healthsim-workspace/packages/patientsim/src/patientsim/core/models.py

This module defines the internal representation of patient data, clinical encounters,
and related healthcare information. All models use Pydantic v2 for validation.
"""

from datetime import date, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from healthsim_agent.person import Gender, Person  # noqa: F401


class EncounterClass(str, Enum):
    """Type of encounter."""
    INPATIENT = "I"
    OUTPATIENT = "O"
    EMERGENCY = "E"
    URGENT_CARE = "U"
    OBSERVATION = "OBS"


class EncounterStatus(str, Enum):
    """Status of the encounter."""
    PLANNED = "planned"
    ARRIVED = "arrived"
    IN_PROGRESS = "in-progress"
    ON_HOLD = "on-hold"
    FINISHED = "finished"
    CANCELLED = "cancelled"


class DiagnosisType(str, Enum):
    """Type of diagnosis."""
    ADMITTING = "admitting"
    WORKING = "working"
    FINAL = "final"
    DIFFERENTIAL = "differential"


class MedicationStatus(str, Enum):
    """Status of medication."""
    ACTIVE = "active"
    COMPLETED = "completed"
    STOPPED = "stopped"
    ON_HOLD = "on-hold"


class Patient(Person):
    """Core patient model with demographics and identifiers."""
    mrn: str = Field(..., description="Medical Record Number", min_length=1)
    ssn: str | None = Field(None, description="Social Security Number", pattern=r"^\d{9}$")
    race: str | None = Field(None, description="Race/ethnicity")
    language: str = Field("en", description="Preferred language code")
    created_at: datetime = Field(default_factory=datetime.now)

    model_config = ConfigDict(use_enum_values=True)


class Encounter(BaseModel):
    """Clinical encounter (visit, admission, etc.)."""
    encounter_id: str = Field(..., description="Unique encounter identifier", min_length=1)
    patient_mrn: str = Field(..., description="Patient MRN", min_length=1)
    class_code: EncounterClass = Field(..., description="Type of encounter")
    status: EncounterStatus = Field(..., description="Current status")

    admission_time: datetime = Field(..., description="When patient was admitted/arrived")
    discharge_time: datetime | None = Field(None, description="When patient was discharged")

    facility: str | None = Field(None, description="Facility/hospital name")
    department: str | None = Field(None, description="Department/unit")
    room: str | None = Field(None, description="Room number")
    bed: str | None = Field(None, description="Bed identifier")

    chief_complaint: str | None = Field(None, description="Patient's chief complaint")
    admitting_diagnosis: str | None = Field(None, description="Diagnosis on admission")
    discharge_disposition: str | None = Field(None, description="Where patient went after")

    attending_physician: str | None = Field(None, description="Attending physician ID")
    admitting_physician: str | None = Field(None, description="Admitting physician ID")

    @field_validator("discharge_time")
    @classmethod
    def discharge_after_admission(cls, v: datetime | None, info: Any) -> datetime | None:
        if v and "admission_time" in info.data and v < info.data["admission_time"]:
            raise ValueError("Discharge time cannot be before admission time")
        return v

    @property
    def length_of_stay_hours(self) -> float | None:
        if not self.discharge_time:
            return None
        delta = self.discharge_time - self.admission_time
        return delta.total_seconds() / 3600

    model_config = ConfigDict(use_enum_values=True)


class Diagnosis(BaseModel):
    """Patient diagnosis/condition."""
    code: str = Field(..., description="ICD-10 diagnosis code", min_length=1)
    description: str = Field(..., description="Diagnosis description", min_length=1)
    type: DiagnosisType = Field(DiagnosisType.FINAL, description="Type of diagnosis")

    patient_mrn: str = Field(..., description="Patient MRN", min_length=1)
    encounter_id: str | None = Field(None, description="Associated encounter")

    diagnosed_date: date = Field(..., description="When diagnosis was made")
    resolved_date: date | None = Field(None, description="When condition resolved")

    @field_validator("resolved_date")
    @classmethod
    def resolved_after_diagnosed(cls, v: date | None, info: Any) -> date | None:
        if v and "diagnosed_date" in info.data and v < info.data["diagnosed_date"]:
            raise ValueError("Resolved date cannot be before diagnosed date")
        return v

    model_config = ConfigDict(use_enum_values=True)


class Procedure(BaseModel):
    """Clinical procedure performed on patient."""
    code: str = Field(..., description="ICD-10-PCS or CPT procedure code", min_length=1)
    description: str = Field(..., description="Procedure description", min_length=1)

    patient_mrn: str = Field(..., description="Patient MRN", min_length=1)
    encounter_id: str | None = Field(None, description="Associated encounter")

    performed_date: datetime = Field(..., description="When procedure was performed")
    performer: str | None = Field(None, description="Clinician who performed procedure")
    location: str | None = Field(None, description="Where procedure was performed")


class Medication(BaseModel):
    """Medication order or administration."""
    name: str = Field(..., description="Medication name", min_length=1)
    code: str | None = Field(None, description="RxNorm or NDC code")

    dose: str = Field(..., description="Dose (e.g., '500 mg')", min_length=1)
    route: str = Field(..., description="Route of administration", min_length=1)
    frequency: str = Field(..., description="Frequency (QD, BID, etc.)", min_length=1)

    patient_mrn: str = Field(..., description="Patient MRN", min_length=1)
    encounter_id: str | None = Field(None, description="Associated encounter")

    start_date: datetime = Field(..., description="When medication started")
    end_date: datetime | None = Field(None, description="When medication stopped")
    status: MedicationStatus = Field(MedicationStatus.ACTIVE, description="Current status")

    prescriber: str | None = Field(None, description="Prescribing clinician")
    indication: str | None = Field(None, description="Reason for medication")

    @field_validator("end_date")
    @classmethod
    def end_after_start(cls, v: datetime | None, info: Any) -> datetime | None:
        if v and "start_date" in info.data and v < info.data["start_date"]:
            raise ValueError("End date cannot be before start date")
        return v

    model_config = ConfigDict(use_enum_values=True)


class LabResult(BaseModel):
    """Laboratory test result."""
    test_name: str = Field(..., description="Name of the test", min_length=1)
    loinc_code: str | None = Field(None, description="LOINC code")

    value: str = Field(..., description="Test result value", min_length=1)
    unit: str | None = Field(None, description="Unit of measure")
    reference_range: str | None = Field(None, description="Normal reference range")
    abnormal_flag: str | None = Field(None, description="Abnormal flag (H, L, etc.)")

    patient_mrn: str = Field(..., description="Patient MRN", min_length=1)
    encounter_id: str | None = Field(None, description="Associated encounter")

    collected_time: datetime = Field(..., description="When specimen was collected")
    resulted_time: datetime | None = Field(None, description="When result was finalized")

    performing_lab: str | None = Field(None, description="Lab that performed the test")
    ordering_provider: str | None = Field(None, description="Provider who ordered")

    @field_validator("resulted_time")
    @classmethod
    def resulted_after_collected(cls, v: datetime | None, info: Any) -> datetime | None:
        if v and "collected_time" in info.data and v < info.data["collected_time"]:
            raise ValueError("Resulted time cannot be before collected time")
        return v


class VitalSign(BaseModel):
    """Vital sign observation."""
    patient_mrn: str = Field(..., description="Patient MRN", min_length=1)
    encounter_id: str | None = Field(None, description="Associated encounter")

    observation_time: datetime = Field(..., description="When vitals were taken")

    temperature: float | None = Field(None, description="Temperature in Fahrenheit", ge=90, le=110)
    heart_rate: int | None = Field(None, description="Heart rate in bpm", ge=0, le=300)
    respiratory_rate: int | None = Field(None, description="Respiratory rate", ge=0, le=100)
    systolic_bp: int | None = Field(None, description="Systolic blood pressure", ge=0, le=300)
    diastolic_bp: int | None = Field(None, description="Diastolic blood pressure", ge=0, le=200)
    spo2: int | None = Field(None, description="Oxygen saturation %", ge=0, le=100)
    height_cm: float | None = Field(None, description="Height in cm", ge=0, le=300)
    weight_kg: float | None = Field(None, description="Weight in kg", ge=0, le=500)

    @property
    def blood_pressure(self) -> str | None:
        if self.systolic_bp is not None and self.diastolic_bp is not None:
            return f"{self.systolic_bp}/{self.diastolic_bp}"
        return None

    @property
    def bmi(self) -> float | None:
        if self.height_cm is not None and self.weight_kg is not None:
            height_m = self.height_cm / 100
            return round(self.weight_kg / (height_m**2), 1)
        return None

    @model_validator(mode="after")
    def validate_bp_pair(self) -> "VitalSign":
        has_systolic = self.systolic_bp is not None
        has_diastolic = self.diastolic_bp is not None

        if has_systolic != has_diastolic:
            raise ValueError("Both systolic and diastolic BP must be provided together")

        if has_systolic and has_diastolic and self.systolic_bp <= self.diastolic_bp:
            raise ValueError("Systolic BP must be greater than diastolic BP")

        return self


class ClinicalNote(BaseModel):
    """Clinical note or documentation."""
    note_type: str = Field(..., description="Type of note", min_length=1)

    patient_mrn: str = Field(..., description="Patient MRN", min_length=1)
    encounter_id: str | None = Field(None, description="Associated encounter")

    note_time: datetime = Field(..., description="When note was written")
    text: str = Field(..., description="Note content", min_length=1)

    author: str | None = Field(None, description="Clinician who wrote the note")
    service: str | None = Field(None, description="Clinical service")


__all__ = [
    # Enums
    "EncounterClass",
    "EncounterStatus",
    "DiagnosisType",
    "MedicationStatus",
    # Models
    "Patient",
    "Encounter",
    "Diagnosis",
    "Procedure",
    "Medication",
    "LabResult",
    "VitalSign",
    "ClinicalNote",
    # Re-exports
    "Gender",
    "Person",
]
