"""Pharmacy benefit member model.

Ported from: healthsim-workspace/packages/rxmembersim/src/rxmembersim/core/member.py
"""

from datetime import date
from decimal import Decimal

from healthsim_agent.benefits import AccumulatorSet as CoreAccumulatorSet
from healthsim_agent.benefits import BenefitType, create_pharmacy_accumulators
from pydantic import BaseModel, Field


class MemberDemographics(BaseModel):
    """Member demographic information."""
    first_name: str
    last_name: str
    date_of_birth: date
    gender: str  # M, F, U
    address_line1: str | None = None
    address_line2: str | None = None
    city: str | None = None
    state: str | None = None
    zip_code: str | None = None
    phone: str | None = None


class BenefitAccumulators(BaseModel):
    """Member benefit accumulators."""
    deductible_met: Decimal = Field(default=Decimal("0"), description="Amount applied to deductible")
    deductible_remaining: Decimal = Field(..., description="Remaining deductible amount")
    oop_met: Decimal = Field(default=Decimal("0"), description="Amount applied to OOP max")
    oop_remaining: Decimal = Field(..., description="Remaining OOP amount")

    @property
    def deductible_limit(self) -> Decimal:
        return self.deductible_met + self.deductible_remaining

    @property
    def oop_limit(self) -> Decimal:
        return self.oop_met + self.oop_remaining

    @property
    def is_deductible_met(self) -> bool:
        return self.deductible_remaining <= Decimal("0")

    @property
    def is_oop_met(self) -> bool:
        return self.oop_remaining <= Decimal("0")

    def apply(self, deductible_amount: Decimal, oop_amount: Decimal) -> "BenefitAccumulators":
        """Apply amounts to accumulators."""
        new_ded_applied = min(deductible_amount, self.deductible_remaining)
        new_oop_applied = min(oop_amount, self.oop_remaining)

        return BenefitAccumulators(
            deductible_met=self.deductible_met + new_ded_applied,
            deductible_remaining=self.deductible_remaining - new_ded_applied,
            oop_met=self.oop_met + new_oop_applied,
            oop_remaining=self.oop_remaining - new_oop_applied,
        )

    def to_accumulator_set(self, member_id: str, plan_year: int) -> CoreAccumulatorSet:
        """Convert to a core AccumulatorSet."""
        acc_set = create_pharmacy_accumulators(
            member_id=member_id,
            plan_year=plan_year,
            deductible=self.deductible_limit,
            oop_max=self.oop_limit,
        )

        if self.deductible_met > 0:
            acc_set, _ = acc_set.apply_to_deductible(
                self.deductible_met, benefit_type=BenefitType.PHARMACY
            )
        if self.oop_met > 0:
            acc_set, _ = acc_set.apply_to_oop(
                self.oop_met, benefit_type=BenefitType.PHARMACY
            )

        return acc_set

    @classmethod
    def from_accumulator_set(cls, acc_set: CoreAccumulatorSet) -> "BenefitAccumulators":
        """Create from a core AccumulatorSet."""
        rx_ded = acc_set.rx_deductible
        rx_oop = acc_set.rx_oop

        return cls(
            deductible_met=rx_ded.applied if rx_ded else Decimal("0"),
            deductible_remaining=rx_ded.remaining if rx_ded else Decimal("0"),
            oop_met=rx_oop.applied if rx_oop else Decimal("0"),
            oop_remaining=rx_oop.remaining if rx_oop else Decimal("0"),
        )


class RxMember(BaseModel):
    """Pharmacy benefit member."""
    member_id: str
    cardholder_id: str
    person_code: str = "01"

    bin: str
    pcn: str
    group_number: str

    demographics: MemberDemographics

    effective_date: date
    termination_date: date | None = None

    accumulators: BenefitAccumulators

    plan_code: str | None = None
    formulary_id: str | None = None

    def get_accumulator_set(self, plan_year: int | None = None) -> CoreAccumulatorSet:
        """Get accumulators as a core AccumulatorSet."""
        year = plan_year or self.effective_date.year
        return self.accumulators.to_accumulator_set(self.member_id, year)


class RxMemberGenerator:
    """Generator for creating pharmacy benefit members."""

    def generate(
        self,
        bin: str = "610014",
        pcn: str = "RXTEST",
        group_number: str = "GRP001",
    ) -> RxMember:
        """Generate a random pharmacy member."""
        from faker import Faker

        fake = Faker()
        member_id = f"RXM-{fake.random_number(digits=8, fix_len=True)}"

        return RxMember(
            member_id=member_id,
            cardholder_id=str(fake.random_number(digits=9, fix_len=True)),
            person_code="01",
            bin=bin,
            pcn=pcn,
            group_number=group_number,
            demographics=MemberDemographics(
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                date_of_birth=fake.date_of_birth(minimum_age=18, maximum_age=85),
                gender=fake.random_element(["M", "F"]),
                address_line1=fake.street_address(),
                city=fake.city(),
                state=fake.state_abbr(),
                zip_code=fake.zipcode(),
            ),
            effective_date=date(2025, 1, 1),
            accumulators=BenefitAccumulators(
                deductible_remaining=Decimal("250"),
                oop_remaining=Decimal("3000"),
            ),
        )


__all__ = [
    "MemberDemographics",
    "BenefitAccumulators",
    "RxMember",
    "RxMemberGenerator",
]
