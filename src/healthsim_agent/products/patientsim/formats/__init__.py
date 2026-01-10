"""PatientSim format support.

Export utilities and healthcare format transformers.
"""

from healthsim_agent.products.patientsim.formats.export import (
    JSONEncoder,
    diagnoses_to_csv,
    encounters_to_csv,
    labs_to_csv,
    medications_to_csv,
    patients_to_csv,
    to_csv,
    to_json,
    vitals_to_csv,
)
from healthsim_agent.products.patientsim.formats.fhir import FHIRTransformer
from healthsim_agent.products.patientsim.formats.hl7v2 import HL7v2Generator

# C-CDA exports
from healthsim_agent.products.patientsim.formats.ccda import (
    CCDAConfig,
    CCDATransformer,
    CCDAValidator,
    CODE_SYSTEMS,
    CodedValue,
    CodeSystemRegistry,
    DocumentType,
    HeaderBuilder,
    NarrativeBuilder,
    SectionBuilder,
    ValidationError,
    ValidationResult,
    VITAL_SIGNS_LOINC,
    create_loinc_code,
    create_rxnorm_code,
    create_snomed_code,
    get_code_system,
    get_vital_loinc,
)

__all__ = [
    # Export utilities
    "JSONEncoder",
    "to_json",
    "to_csv",
    "patients_to_csv",
    "encounters_to_csv",
    "diagnoses_to_csv",
    "medications_to_csv",
    "labs_to_csv",
    "vitals_to_csv",
    # FHIR
    "FHIRTransformer",
    # HL7v2
    "HL7v2Generator",
    # C-CDA
    "CCDATransformer",
    "CCDAConfig",
    "DocumentType",
    "HeaderBuilder",
    "NarrativeBuilder",
    "SectionBuilder",
    "CCDAValidator",
    "ValidationResult",
    "ValidationError",
    "CodedValue",
    "CodeSystemRegistry",
    "CODE_SYSTEMS",
    "VITAL_SIGNS_LOINC",
    "create_loinc_code",
    "create_snomed_code",
    "create_rxnorm_code",
    "get_code_system",
    "get_vital_loinc",
]
