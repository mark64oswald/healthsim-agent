"""MemberSim product package.

Provides health plan member simulation models and generators.
"""

from healthsim_agent.products.membersim.core import (
    Accumulator,
    Address,
    Claim,
    ClaimLine,
    ClaimStatus,
    Coverage,
    CoverageType,
    Enrollment,
    Member,
    MemberGenerator,
    Name,
    Plan,
    SAMPLE_PLANS,
)
from healthsim_agent.products.membersim.authorization import (
    Authorization,
    AuthorizationStatus,
    DENIAL_REASONS,
    PRIOR_AUTH_REQUIRED,
)
from healthsim_agent.products.membersim.claims import (
    Claim as MedicalClaim,
    ClaimLine as MedicalClaimLine,
    LinePayment,
    Payment,
    CARC_CODES,
)

__all__ = [
    # Core models
    "Member",
    "Coverage",
    "Enrollment",
    "Claim",
    "ClaimLine",
    "CoverageType",
    "ClaimStatus",
    "MemberGenerator",
    "Name",
    "Address",
    "Plan",
    "SAMPLE_PLANS",
    "Accumulator",
    # Authorization
    "Authorization",
    "AuthorizationStatus",
    "DENIAL_REASONS",
    "PRIOR_AUTH_REQUIRED",
    # Claims (detailed)
    "MedicalClaim",
    "MedicalClaimLine",
    "LinePayment",
    "Payment",
    "CARC_CODES",
]
