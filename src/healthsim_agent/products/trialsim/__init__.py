"""TrialSim product package.

Provides clinical trial simulation models and generators.
"""

from healthsim_agent.products.trialsim.core import (
    # Enums
    ArmType,
    SubjectStatus,
    VisitType,
    AESeverity,
    AECausality,
    AEOutcome,
    # Models
    Site,
    Protocol,
    Subject,
    Visit,
    AdverseEvent,
    Exposure,
    # Generators
    TrialSubjectGenerator,
    VisitGenerator,
    AdverseEventGenerator,
    ExposureGenerator,
)

__all__ = [
    "ArmType",
    "SubjectStatus",
    "VisitType",
    "AESeverity",
    "AECausality",
    "AEOutcome",
    "Site",
    "Protocol",
    "Subject",
    "Visit",
    "AdverseEvent",
    "Exposure",
    "TrialSubjectGenerator",
    "VisitGenerator",
    "AdverseEventGenerator",
    "ExposureGenerator",
]
