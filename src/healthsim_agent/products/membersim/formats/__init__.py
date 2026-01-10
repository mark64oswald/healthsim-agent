"""MemberSim formats - export to industry standard formats."""

from healthsim_agent.products.membersim.formats.export import (
    JSONEncoder,
    to_json,
    to_csv,
    members_to_csv,
    claims_to_csv,
)
from healthsim_agent.products.membersim.formats.fhir import (
    member_to_fhir_coverage,
    member_to_fhir_patient,
    create_fhir_bundle,
)
from healthsim_agent.products.membersim.formats.x12 import (
    X12Config,
    X12Generator,
    # 270/271 Eligibility
    EDI270Generator,
    EDI271Generator,
    generate_270,
    generate_271,
    # 278 Prior Auth
    EDI278RequestGenerator,
    EDI278ResponseGenerator,
    generate_278_request,
    generate_278_response,
    # 834 Enrollment
    EDI834Generator,
    generate_834,
    # 835 Remittance
    EDI835Generator,
    Payment,
    LinePayment,
    generate_835,
    # 837 Claims
    EDI837PGenerator,
    EDI837IGenerator,
    generate_837p,
    generate_837i,
)

__all__ = [
    # Export utilities
    "JSONEncoder",
    "to_json",
    "to_csv",
    "members_to_csv",
    "claims_to_csv",
    # FHIR
    "member_to_fhir_coverage",
    "member_to_fhir_patient",
    "create_fhir_bundle",
    # X12
    "X12Config",
    "X12Generator",
    "EDI270Generator",
    "EDI271Generator",
    "generate_270",
    "generate_271",
    "EDI278RequestGenerator",
    "EDI278ResponseGenerator",
    "generate_278_request",
    "generate_278_response",
    "EDI834Generator",
    "generate_834",
    "EDI835Generator",
    "Payment",
    "LinePayment",
    "generate_835",
    "EDI837PGenerator",
    "EDI837IGenerator",
    "generate_837p",
    "generate_837i",
]
