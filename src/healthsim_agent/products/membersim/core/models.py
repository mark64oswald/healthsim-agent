"""Core models for health plan member data.

Ported from: healthsim-workspace/packages/membersim/src/membersim/core/models.py
"""

from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from healthsim_agent.benefits import (
    Accumulator as CoreAccumulator,
    AccumulatorSet,
    AccumulatorType,
    AccumulatorLevel,
    NetworkTier,
    BenefitType,
    create_medical_accumulators,
)


class CoverageType(str, Enum):
    """Types of health coverage."""
    MEDICAL = "medical"
    DENTAL = "dental"
    VISION = "vision"
    PHARMACY = "pharmacy"


class ClaimStatus(str, Enum):
    """Status of a claim."""
    SUBMITTED = "submitted"
    PENDING = "pending"
    APPROVED = "approved"
    DENIED = "denied"
    PAID = "paid"


class Name(BaseModel):
    """Person name structure."""
    given_name: str
    family_name: str
    middle_name: str | None = None
    prefix: str | None = None
    suffix: str | None = None


class Address(BaseModel):
    """Postal address structure."""
    street_address: str
    city: str
    state: str
    postal_code: str
    country: str = "US"


class Plan(BaseModel):
    """Benefit plan with cost sharing details."""

    model_config = {"frozen": True}

    plan_code: str = Field(..., description="Plan identifier")
    plan_name: str = Field(..., description="Human-readable plan name")
    plan_type: str = Field(..., description="HMO, PPO, EPO, POS, HDHP")
    coverage_type: str = Field("MEDICAL", description="MEDICAL, DENTAL, VISION, RX")

    # Deductibles
    deductible_individual: Decimal = Field(
        Decimal("500"), description="Annual individual deductible"
    )
    deductible_family: Decimal = Field(Decimal("1500"), description="Annual family deductible")

    # Out-of-pocket maximums
    oop_max_individual: Decimal = Field(Decimal("3000"), description="Individual OOP maximum")
    oop_max_family: Decimal = Field(Decimal("6000"), description="Family OOP maximum")

    # Cost sharing
    copay_pcp: Decimal = Field(Decimal("25"), description="Primary care copay")
    copay_specialist: Decimal = Field(Decimal("50"), description="Specialist copay")
    copay_er: Decimal = Field(Decimal("250"), description="Emergency room copay")
    coinsurance: Decimal = Field(Decimal("0.20"), description="Coinsurance percentage (0.20 = 20%)")

    # Network
    requires_pcp: bool = Field(False, description="Requires PCP assignment (HMO)")
    requires_referral: bool = Field(False, description="Requires referral for specialists")


# Sample plan configurations
SAMPLE_PLANS = {
    "PPO_GOLD": Plan(
        plan_code="PPO_GOLD",
        plan_name="Gold PPO Plan",
        plan_type="PPO",
        deductible_individual=Decimal("500"),
        deductible_family=Decimal("1000"),
        oop_max_individual=Decimal("3000"),
        oop_max_family=Decimal("6000"),
        copay_pcp=Decimal("20"),
        copay_specialist=Decimal("40"),
        copay_er=Decimal("150"),
        coinsurance=Decimal("0.20"),
    ),
    "HMO_STANDARD": Plan(
        plan_code="HMO_STANDARD",
        plan_name="Standard HMO Plan",
        plan_type="HMO",
        deductible_individual=Decimal("250"),
        deductible_family=Decimal("500"),
        oop_max_individual=Decimal("2500"),
        oop_max_family=Decimal("5000"),
        copay_pcp=Decimal("15"),
        copay_specialist=Decimal("30"),
        copay_er=Decimal("100"),
        coinsurance=Decimal("0.10"),
        requires_pcp=True,
        requires_referral=True,
    ),
    "HDHP_HSA": Plan(
        plan_code="HDHP_HSA",
        plan_name="High Deductible Health Plan with HSA",
        plan_type="HDHP",
        deductible_individual=Decimal("1500"),
        deductible_family=Decimal("3000"),
        oop_max_individual=Decimal("7500"),
        oop_max_family=Decimal("15000"),
        copay_pcp=Decimal("0"),
        copay_specialist=Decimal("0"),
        copay_er=Decimal("0"),
        coinsurance=Decimal("0.20"),
    ),
}


class Accumulator(BaseModel):
    """Track deductible and OOP accumulations for a member."""

    member_id: str = Field(..., description="Member reference")
    plan_year: int = Field(..., description="Benefit year")

    # Deductible tracking
    deductible_applied: Decimal = Field(
        default=Decimal("0"), description="Amount applied to deductible"
    )
    deductible_limit: Decimal = Field(..., description="Deductible limit for this member")

    # OOP tracking
    oop_applied: Decimal = Field(
        default=Decimal("0"), description="Amount applied to OOP max"
    )
    oop_limit: Decimal = Field(..., description="OOP maximum for this member")

    last_updated: datetime = Field(default_factory=datetime.now)

    @property
    def deductible_remaining(self) -> Decimal:
        """Calculate remaining deductible."""
        return max(Decimal("0"), self.deductible_limit - self.deductible_applied)

    @property
    def deductible_met(self) -> bool:
        """Check if deductible has been met."""
        return self.deductible_applied >= self.deductible_limit

    @property
    def oop_remaining(self) -> Decimal:
        """Calculate remaining OOP."""
        return max(Decimal("0"), self.oop_limit - self.oop_applied)

    @property
    def oop_met(self) -> bool:
        """Check if OOP max has been reached."""
        return self.oop_applied >= self.oop_limit

    def apply_payment(
        self, deductible_amount: Decimal, oop_amount: Decimal
    ) -> "Accumulator":
        """Apply a payment to accumulators, returning new accumulator state."""
        return Accumulator(
            member_id=self.member_id,
            plan_year=self.plan_year,
            deductible_applied=min(
                self.deductible_limit, self.deductible_applied + deductible_amount
            ),
            deductible_limit=self.deductible_limit,
            oop_applied=min(self.oop_limit, self.oop_applied + oop_amount),
            oop_limit=self.oop_limit,
            last_updated=datetime.now(),
        )


class Member(BaseModel):
    """Health plan member."""
    member_id: str = Field(..., description="Unique member identifier")
    subscriber_id: str = Field(..., description="Subscriber/policyholder ID")

    # Name - supports both direct fields and Name object
    given_name: str = Field(..., description="First name")
    family_name: str = Field(..., description="Last name")
    birth_date: date = Field(..., description="Date of birth")
    gender: str = Field(..., description="M/F/O/U")

    # Address
    street_address: str | None = Field(None, description="Street address")
    city: str | None = Field(None, description="City")
    state: str | None = Field(None, description="State")
    postal_code: str | None = Field(None, description="Postal code")
    phone: str | None = Field(None, description="Phone number")
    email: str | None = Field(None, description="Email address")

    # Plan/Group info
    group_number: str | None = Field(None, alias="group_id", description="Employer group number")
    plan_code: str | None = Field(None, description="Plan identifier")
    relationship_code: str = Field("18", description="Subscriber relationship code")

    # Coverage dates
    coverage_start: date = Field(default_factory=date.today, description="Coverage start date")
    coverage_end: date | None = Field(None, description="Coverage end date")

    @property
    def full_name(self) -> str:
        return f"{self.given_name} {self.family_name}"

    @property
    def age(self) -> int:
        today = date.today()
        return (
            today.year
            - self.birth_date.year
            - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
        )

    @property
    def is_active(self) -> bool:
        """Check if member has active coverage."""
        today = date.today()
        if self.coverage_end:
            return self.coverage_start <= today <= self.coverage_end
        return self.coverage_start <= today

    @property
    def group_id(self) -> str | None:
        """Alias for group_number."""
        return self.group_number

    @property
    def name(self) -> Name:
        """Return structured name object."""
        return Name(given_name=self.given_name, family_name=self.family_name)

    @property
    def address(self) -> Address | None:
        """Return structured address object if available."""
        if self.street_address and self.city and self.state and self.postal_code:
            return Address(
                street_address=self.street_address,
                city=self.city,
                state=self.state,
                postal_code=self.postal_code,
            )
        return None


class Coverage(BaseModel):
    """Coverage period for a member."""
    coverage_id: str = Field(..., description="Coverage identifier")
    member_id: str = Field(..., description="Member this coverage is for")
    coverage_type: CoverageType = Field(..., description="Type of coverage")

    start_date: date = Field(..., description="Coverage start date")
    end_date: date | None = Field(None, description="Coverage end date")

    plan_name: str | None = Field(None, description="Plan name")
    network: str | None = Field(None, description="Network (HMO, PPO, etc.)")

    deductible: Decimal | None = Field(None, description="Annual deductible")
    copay: Decimal | None = Field(None, description="Standard copay amount")

    @property
    def is_active(self) -> bool:
        today = date.today()
        if self.end_date:
            return self.start_date <= today <= self.end_date
        return self.start_date <= today


class Enrollment(BaseModel):
    """Enrollment record for a member."""
    enrollment_id: str = Field(..., description="Enrollment record ID")
    member_id: str = Field(..., description="Member ID")

    enrollment_date: date = Field(..., description="Date enrolled")
    disenrollment_date: date | None = Field(None, description="Date disenrolled")
    reason_code: str | None = Field(None, description="Enrollment/disenrollment reason")


class ClaimLine(BaseModel):
    """Individual line item on a claim."""
    line_number: int = Field(..., description="Line number")
    procedure_code: str = Field(..., description="CPT/HCPCS code")
    diagnosis_code: str | None = Field(None, description="ICD-10 code")

    quantity: int = Field(1, description="Units/quantity")
    billed_amount: Decimal = Field(..., description="Amount billed")
    allowed_amount: Decimal | None = Field(None, description="Amount allowed")
    paid_amount: Decimal | None = Field(None, description="Amount paid")


class Claim(BaseModel):
    """Health insurance claim."""
    claim_id: str = Field(..., description="Unique claim identifier")
    member_id: str = Field(..., description="Member ID")

    service_date: date = Field(..., description="Date of service")
    submission_date: date = Field(..., description="Date claim submitted")

    provider_npi: str | None = Field(None, description="Provider NPI")
    provider_name: str | None = Field(None, description="Provider name")
    facility_name: str | None = Field(None, description="Facility name")

    status: ClaimStatus = Field(ClaimStatus.SUBMITTED, description="Claim status")
    claim_type: str | None = Field(None, description="Professional/Institutional")

    total_billed: Decimal = Field(..., description="Total billed amount")
    total_allowed: Decimal | None = Field(None, description="Total allowed amount")
    total_paid: Decimal | None = Field(None, description="Total paid amount")
    member_responsibility: Decimal | None = Field(None, description="Member owes")

    lines: list[ClaimLine] = Field(default_factory=list, description="Claim lines")


__all__ = [
    "CoverageType",
    "ClaimStatus",
    "Name",
    "Address",
    "Plan",
    "SAMPLE_PLANS",
    "Accumulator",
    "Member",
    "Coverage",
    "Enrollment",
    "ClaimLine",
    "Claim",
]
