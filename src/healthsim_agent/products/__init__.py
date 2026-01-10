"""HealthSim product packages.

Each product provides domain-specific models and generators:
- patientsim: Clinical/EMR patient data (FHIR, HL7v2, C-CDA)
- membersim: Health plan member/claims data (X12 837/835/834)
- rxmembersim: Pharmacy benefit data (NCPDP D.0)
- trialsim: Clinical trial data (CDISC SDTM/ADaM)
"""

# Re-export key classes from each product for convenience
from healthsim_agent.products.patientsim import (
    Patient,
    PatientGenerator,
    generate_patient,
)
from healthsim_agent.products.membersim import (
    Member,
    MemberGenerator,
)
from healthsim_agent.products.rxmembersim import (
    RxMember,
    RxMemberFactory,
)
from healthsim_agent.products.trialsim import (
    Subject,
    TrialSubjectGenerator,
)

__all__ = [
    # PatientSim
    "Patient",
    "PatientGenerator",
    "generate_patient",
    # MemberSim
    "Member",
    "MemberGenerator",
    # RxMemberSim
    "RxMember",
    "RxMemberFactory",
    # TrialSim
    "Subject",
    "TrialSubjectGenerator",
]
