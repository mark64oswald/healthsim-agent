"""Core patient simulation models and data structures."""

from healthsim_agent.person import Address, ContactInfo, PersonName

from healthsim_agent.products.patientsim.core.generator import (
    PatientGenerator,
    PatientFactory,
    generate_patient,
)
from healthsim_agent.products.patientsim.core.models import (
    ClinicalNote,
    Diagnosis,
    DiagnosisType,
    Encounter,
    EncounterClass,
    EncounterStatus,
    Gender,
    LabResult,
    Medication,
    MedicationStatus,
    Patient,
    Procedure,
    VitalSign,
)
from healthsim_agent.products.patientsim.core.reference_data import (
    CLINICAL_SCENARIOS,
    COMMON_DIAGNOSES,
    ICD10Code,
    LAB_TESTS,
    LabTest,
    MEDICATIONS,
    MedicationInfo,
    VITAL_RANGES,
    get_diagnosis_by_code,
    get_diagnoses_by_category,
    get_lab_test,
    get_medication,
)

__all__ = [
    # Person components
    "PersonName",
    "Address",
    "ContactInfo",
    # Models
    "Patient",
    "Encounter",
    "Diagnosis",
    "Procedure",
    "Medication",
    "LabResult",
    "VitalSign",
    "ClinicalNote",
    # Enums
    "Gender",
    "EncounterClass",
    "EncounterStatus",
    "DiagnosisType",
    "MedicationStatus",
    # Generator
    "PatientGenerator",
    "PatientFactory",
    "generate_patient",
    # Reference data
    "ICD10Code",
    "LabTest",
    "MedicationInfo",
    "COMMON_DIAGNOSES",
    "LAB_TESTS",
    "MEDICATIONS",
    "VITAL_RANGES",
    "CLINICAL_SCENARIOS",
    "get_diagnosis_by_code",
    "get_diagnoses_by_category",
    "get_lab_test",
    "get_medication",
]
