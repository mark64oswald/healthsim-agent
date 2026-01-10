"""C-CDA format support for PatientSim.

Provides tools to generate C-CDA (Consolidated Clinical Document Architecture)
documents from PatientSim clinical data models.
"""

from healthsim_agent.products.patientsim.formats.ccda.header import HeaderBuilder
from healthsim_agent.products.patientsim.formats.ccda.narratives import NarrativeBuilder
from healthsim_agent.products.patientsim.formats.ccda.sections import SectionBuilder
from healthsim_agent.products.patientsim.formats.ccda.transformer import (
    CCDAConfig,
    CCDATransformer,
    DocumentType,
)
from healthsim_agent.products.patientsim.formats.ccda.validators import (
    CCDAValidator,
    ValidationError,
    ValidationResult,
)
from healthsim_agent.products.patientsim.formats.ccda.vocabulary import (
    CODE_SYSTEMS,
    CodedValue,
    CodeSystemRegistry,
    SNOMEDMapping,
    VITAL_SIGNS_LOINC,
    create_loinc_code,
    create_rxnorm_code,
    create_snomed_code,
    get_code_system,
    get_vital_loinc,
)

__all__ = [
    # Transformer
    "CCDATransformer",
    "CCDAConfig",
    "DocumentType",
    # Builders
    "HeaderBuilder",
    "NarrativeBuilder",
    "SectionBuilder",
    # Validation
    "CCDAValidator",
    "ValidationResult",
    "ValidationError",
    # Vocabulary
    "CodedValue",
    "CodeSystemRegistry",
    "SNOMEDMapping",
    "CODE_SYSTEMS",
    "VITAL_SIGNS_LOINC",
    "create_loinc_code",
    "create_snomed_code",
    "create_rxnorm_code",
    "get_code_system",
    "get_vital_loinc",
]
