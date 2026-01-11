"""ADaM domain definitions.

CDISC ADaM (Analysis Data Model) defines analysis-ready datasets:
- ADSL: Subject-Level Analysis Dataset (required)
- ADAE: Adverse Events Analysis Dataset
- ADEX: Exposure Analysis Dataset
- ADEFF: Efficacy Analysis Dataset (BDS structure)
"""

from enum import Enum
from dataclasses import dataclass


class ADAMDataset(str, Enum):
    """Standard ADaM analysis datasets."""
    ADSL = "ADSL"  # Subject-Level Analysis Dataset (required)
    ADAE = "ADAE"  # Adverse Events Analysis Dataset
    ADEX = "ADEX"  # Exposure Analysis Dataset
    ADEFF = "ADEFF"  # Efficacy Analysis Dataset


@dataclass
class ADAMVariable:
    """ADaM variable definition."""
    name: str
    label: str
    data_type: str  # "text", "integer", "float", "date", "datetime"
    length: int | None = None
    required: bool = False


# ADSL - Subject-Level Analysis Dataset variables
ADSL_VARIABLES = [
    ADAMVariable("STUDYID", "Study Identifier", "text", 20, True),
    ADAMVariable("USUBJID", "Unique Subject Identifier", "text", 40, True),
    ADAMVariable("SUBJID", "Subject Identifier", "text", 20),
    ADAMVariable("SITEID", "Site Identifier", "text", 10),
    ADAMVariable("AGE", "Age", "integer", required=True),
    ADAMVariable("AGEU", "Age Units", "text", 10),
    ADAMVariable("AGEGR1", "Age Group 1", "text", 20),
    ADAMVariable("SEX", "Sex", "text", 1),
    ADAMVariable("RACE", "Race", "text", 50),
    ADAMVariable("ETHNIC", "Ethnicity", "text", 50),
    ADAMVariable("COUNTRY", "Country", "text", 3),
    ADAMVariable("TRT01P", "Planned Treatment for Period 01", "text", 50),
    ADAMVariable("TRT01A", "Actual Treatment for Period 01", "text", 50),
    ADAMVariable("TRTSDT", "Date of First Exposure to Treatment", "date"),
    ADAMVariable("TRTEDT", "Date of Last Exposure to Treatment", "date"),
    ADAMVariable("SAFFL", "Safety Population Flag", "text", 1),
    ADAMVariable("ITTFL", "Intent-to-Treat Population Flag", "text", 1),
    ADAMVariable("PPROTFL", "Per-Protocol Population Flag", "text", 1),
    ADAMVariable("RANDFL", "Randomized Population Flag", "text", 1),
    ADAMVariable("RANDDT", "Date of Randomization", "date"),
    ADAMVariable("DTHFL", "Subject Death Flag", "text", 1),
    ADAMVariable("DTHDT", "Date of Death", "date"),
    ADAMVariable("EOSDT", "End of Study Date", "date"),
    ADAMVariable("EOSSTT", "End of Study Status", "text", 20),
]

# ADAE - Adverse Events Analysis Dataset variables
ADAE_VARIABLES = [
    ADAMVariable("STUDYID", "Study Identifier", "text", 20, True),
    ADAMVariable("USUBJID", "Unique Subject Identifier", "text", 40, True),
    ADAMVariable("SUBJID", "Subject Identifier", "text", 20),
    ADAMVariable("SITEID", "Site Identifier", "text", 10),
    ADAMVariable("TRTA", "Actual Treatment", "text", 50),
    ADAMVariable("TRTAN", "Actual Treatment (N)", "integer"),
    ADAMVariable("AGE", "Age", "integer"),
    ADAMVariable("SEX", "Sex", "text", 1),
    ADAMVariable("SAFFL", "Safety Population Flag", "text", 1),
    ADAMVariable("AESEQ", "Sequence Number", "integer"),
    ADAMVariable("AESPID", "Sponsor-Defined Identifier", "text", 20),
    ADAMVariable("AETERM", "Reported Term for the Adverse Event", "text", 200),
    ADAMVariable("AEDECOD", "Dictionary-Derived Term", "text", 200),
    ADAMVariable("AEBODSYS", "Body System or Organ Class", "text", 100),
    ADAMVariable("AESEV", "Severity/Intensity", "text", 20),
    ADAMVariable("AESER", "Serious Event", "text", 1),
    ADAMVariable("AEREL", "Causality", "text", 20),
    ADAMVariable("AEOUT", "Outcome of Adverse Event", "text", 50),
    ADAMVariable("AESTDTC", "Start Date/Time of Adverse Event", "datetime"),
    ADAMVariable("AEENDTC", "End Date/Time of Adverse Event", "datetime"),
    ADAMVariable("ASTDT", "Analysis Start Date", "date"),
    ADAMVariable("AENDT", "Analysis End Date", "date"),
    ADAMVariable("ASTDY", "Analysis Start Relative Day", "integer"),
    ADAMVariable("AENDY", "Analysis End Relative Day", "integer"),
    ADAMVariable("ADURN", "AE Duration (N)", "integer"),
    ADAMVariable("ADURU", "AE Duration Units", "text", 10),
    ADAMVariable("AOCCFL", "1st Occurrence of Any AE Flag", "text", 1),
    ADAMVariable("AOCCSFL", "1st Occurrence of SOC Flag", "text", 1),
    ADAMVariable("AOCCPFL", "1st Occurrence of Preferred Term Flag", "text", 1),
    ADAMVariable("TRTEMFL", "Treatment Emergent Analysis Flag", "text", 1),
]

# ADEX - Exposure Analysis Dataset variables
ADEX_VARIABLES = [
    ADAMVariable("STUDYID", "Study Identifier", "text", 20, True),
    ADAMVariable("USUBJID", "Unique Subject Identifier", "text", 40, True),
    ADAMVariable("SUBJID", "Subject Identifier", "text", 20),
    ADAMVariable("SITEID", "Site Identifier", "text", 10),
    ADAMVariable("TRTA", "Actual Treatment", "text", 50),
    ADAMVariable("TRTAN", "Actual Treatment (N)", "integer"),
    ADAMVariable("SAFFL", "Safety Population Flag", "text", 1),
    ADAMVariable("EXSEQ", "Sequence Number", "integer"),
    ADAMVariable("EXTRT", "Name of Treatment", "text", 100),
    ADAMVariable("EXDOSE", "Dose", "float"),
    ADAMVariable("EXDOSU", "Dose Units", "text", 20),
    ADAMVariable("EXROUTE", "Route of Administration", "text", 50),
    ADAMVariable("EXSTDTC", "Start Date/Time of Treatment", "datetime"),
    ADAMVariable("EXENDTC", "End Date/Time of Treatment", "datetime"),
    ADAMVariable("ASTDT", "Analysis Start Date", "date"),
    ADAMVariable("AENDT", "Analysis End Date", "date"),
    ADAMVariable("ASTDY", "Analysis Start Relative Day", "integer"),
    ADAMVariable("AENDY", "Analysis End Relative Day", "integer"),
    ADAMVariable("AVAL", "Analysis Value", "float"),
    ADAMVariable("AVALC", "Analysis Value (C)", "text", 50),
    ADAMVariable("PARAM", "Parameter", "text", 100),
    ADAMVariable("PARAMCD", "Parameter Code", "text", 20),
    ADAMVariable("PARAMN", "Parameter (N)", "integer"),
]


DATASET_VARIABLES = {
    ADAMDataset.ADSL: ADSL_VARIABLES,
    ADAMDataset.ADAE: ADAE_VARIABLES,
    ADAMDataset.ADEX: ADEX_VARIABLES,
}


def get_dataset_variables(dataset: ADAMDataset) -> list[ADAMVariable]:
    """Get variable definitions for an ADaM dataset."""
    return DATASET_VARIABLES.get(dataset, [])


def get_required_variables(dataset: ADAMDataset) -> list[ADAMVariable]:
    """Get required variables for an ADaM dataset."""
    return [v for v in get_dataset_variables(dataset) if v.required]


__all__ = [
    "ADAMDataset",
    "ADAMVariable",
    "ADSL_VARIABLES",
    "ADAE_VARIABLES", 
    "ADEX_VARIABLES",
    "DATASET_VARIABLES",
    "get_dataset_variables",
    "get_required_variables",
]
