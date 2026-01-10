"""SDTM Domain Definitions.

Ported from: healthsim-workspace/packages/trialsim/src/trialsim/formats/sdtm/domains.py
"""

from dataclasses import dataclass
from enum import Enum


class SDTMDomain(str, Enum):
    """SDTM domain codes."""
    DM = "DM"  # Demographics
    AE = "AE"  # Adverse Events
    EX = "EX"  # Exposure
    SV = "SV"  # Subject Visits
    DS = "DS"  # Disposition
    MH = "MH"  # Medical History
    CM = "CM"  # Concomitant Medications
    VS = "VS"  # Vital Signs
    LB = "LB"  # Laboratory Test Results


@dataclass
class SDTMVariable:
    """Definition of an SDTM variable."""
    name: str
    label: str
    data_type: str  # "Char", "Num", "Date"
    length: int | None = None
    required: bool = False
    codelist: str | None = None
    origin: str = "Derived"


DM_VARIABLES = [
    SDTMVariable("STUDYID", "Study Identifier", "Char", 20, True),
    SDTMVariable("DOMAIN", "Domain Abbreviation", "Char", 2, True),
    SDTMVariable("USUBJID", "Unique Subject Identifier", "Char", 40, True),
    SDTMVariable("SUBJID", "Subject Identifier for the Study", "Char", 20, True),
    SDTMVariable("SITEID", "Study Site Identifier", "Char", 10, True),
    SDTMVariable("RFSTDTC", "Subject Reference Start Date/Time", "Char", 20),
    SDTMVariable("RFENDTC", "Subject Reference End Date/Time", "Char", 20),
    SDTMVariable("AGE", "Age", "Num", 8),
    SDTMVariable("AGEU", "Age Units", "Char", 6),
    SDTMVariable("SEX", "Sex", "Char", 1, True),
    SDTMVariable("RACE", "Race", "Char", 50),
    SDTMVariable("ETHNIC", "Ethnicity", "Char", 50),
    SDTMVariable("ARMCD", "Planned Arm Code", "Char", 20),
    SDTMVariable("ARM", "Description of Planned Arm", "Char", 200),
    SDTMVariable("COUNTRY", "Country", "Char", 3),
]

AE_VARIABLES = [
    SDTMVariable("STUDYID", "Study Identifier", "Char", 20, True),
    SDTMVariable("DOMAIN", "Domain Abbreviation", "Char", 2, True),
    SDTMVariable("USUBJID", "Unique Subject Identifier", "Char", 40, True),
    SDTMVariable("AESEQ", "Sequence Number", "Num", 8, True),
    SDTMVariable("AETERM", "Reported Term for the Adverse Event", "Char", 200, True),
    SDTMVariable("AEDECOD", "Dictionary-Derived Term", "Char", 200),
    SDTMVariable("AEBODSYS", "Body System or Organ Class", "Char", 200),
    SDTMVariable("AESEV", "Severity/Intensity", "Char", 10),
    SDTMVariable("AESER", "Serious Event", "Char", 1),
    SDTMVariable("AEREL", "Causality", "Char", 20),
    SDTMVariable("AEOUT", "Outcome of Adverse Event", "Char", 50),
    SDTMVariable("AESTDTC", "Start Date/Time of Adverse Event", "Char", 20),
    SDTMVariable("AEENDTC", "End Date/Time of Adverse Event", "Char", 20),
]

EX_VARIABLES = [
    SDTMVariable("STUDYID", "Study Identifier", "Char", 20, True),
    SDTMVariable("DOMAIN", "Domain Abbreviation", "Char", 2, True),
    SDTMVariable("USUBJID", "Unique Subject Identifier", "Char", 40, True),
    SDTMVariable("EXSEQ", "Sequence Number", "Num", 8, True),
    SDTMVariable("EXTRT", "Name of Actual Treatment", "Char", 200, True),
    SDTMVariable("EXDOSE", "Dose per Administration", "Num", 8),
    SDTMVariable("EXDOSU", "Dose Units", "Char", 25),
    SDTMVariable("EXROUTE", "Route of Administration", "Char", 50),
    SDTMVariable("EXSTDTC", "Start Date/Time of Treatment", "Char", 20),
    SDTMVariable("EXENDTC", "End Date/Time of Treatment", "Char", 20),
]

SV_VARIABLES = [
    SDTMVariable("STUDYID", "Study Identifier", "Char", 20, True),
    SDTMVariable("DOMAIN", "Domain Abbreviation", "Char", 2, True),
    SDTMVariable("USUBJID", "Unique Subject Identifier", "Char", 40, True),
    SDTMVariable("VISITNUM", "Visit Number", "Num", 8, True),
    SDTMVariable("VISIT", "Visit Name", "Char", 200),
    SDTMVariable("EPOCH", "Epoch", "Char", 50),
    SDTMVariable("SVSTDTC", "Start Date/Time of Visit", "Char", 20),
    SDTMVariable("SVENDTC", "End Date/Time of Visit", "Char", 20),
]

DOMAIN_VARIABLES = {
    SDTMDomain.DM: DM_VARIABLES,
    SDTMDomain.AE: AE_VARIABLES,
    SDTMDomain.EX: EX_VARIABLES,
    SDTMDomain.SV: SV_VARIABLES,
}


def get_domain_variables(domain: SDTMDomain) -> list[SDTMVariable]:
    """Get variable definitions for a domain."""
    return DOMAIN_VARIABLES.get(domain, [])


def get_required_variables(domain: SDTMDomain) -> list[str]:
    """Get required variable names for a domain."""
    return [v.name for v in get_domain_variables(domain) if v.required]


__all__ = [
    "SDTMDomain", "SDTMVariable",
    "DM_VARIABLES", "AE_VARIABLES", "EX_VARIABLES", "SV_VARIABLES",
    "DOMAIN_VARIABLES", "get_domain_variables", "get_required_variables",
]
