"""Benefit accumulator tracking.

This module provides shared accumulator models for tracking deductibles,
out-of-pocket maximums, and other benefit limits.

Ported from: healthsim-workspace/packages/core/src/healthsim/benefits/accumulators.py
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, Field, computed_field


class AccumulatorType(str, Enum):
    """Type of benefit accumulator."""

    DEDUCTIBLE = "deductible"
    OUT_OF_POCKET_MAX = "oop_max"
    COPAY_MAX = "copay_max"
    COINSURANCE_MAX = "coinsurance_max"
    RX_DEDUCTIBLE = "rx_deductible"
    RX_OOP_MAX = "rx_oop_max"
    SPECIALTY_OOP = "specialty_oop"
    LIFETIME_MAX = "lifetime_max"


class AccumulatorLevel(str, Enum):
    """Aggregation level for accumulator."""

    INDIVIDUAL = "individual"
    FAMILY = "family"
    CARDHOLDER = "cardholder"


class NetworkTier(str, Enum):
    """Network tier for cost sharing."""

    IN_NETWORK = "in_network"
    OUT_OF_NETWORK = "out_of_network"
    TIER_1 = "tier_1"
    TIER_2 = "tier_2"
    TIER_3 = "tier_3"
    PREFERRED_PHARMACY = "preferred_pharmacy"
    STANDARD_PHARMACY = "standard_pharmacy"
    MAIL_ORDER = "mail_order"
    SPECIALTY_PHARMACY = "specialty_pharmacy"


class BenefitType(str, Enum):
    """Type of benefit for categorizing accumulator application."""

    MEDICAL = "medical"
    PHARMACY = "pharmacy"
    DENTAL = "dental"
    VISION = "vision"
    BEHAVIORAL_HEALTH = "behavioral_health"
    COMBINED = "combined"


class Accumulator(BaseModel):
    """Single benefit accumulator."""

    accumulator_type: AccumulatorType = Field(..., description="Type of accumulator")
    level: AccumulatorLevel = Field(default=AccumulatorLevel.INDIVIDUAL)
    network_tier: NetworkTier = Field(default=NetworkTier.IN_NETWORK)
    benefit_type: BenefitType = Field(default=BenefitType.COMBINED)
    limit: Decimal = Field(..., description="Maximum amount")
    applied: Decimal = Field(default=Decimal("0"), description="Amount applied YTD")
    plan_year: int = Field(..., description="Benefit plan year")
    last_updated: date = Field(default_factory=date.today)

    @computed_field
    @property
    def remaining(self) -> Decimal:
        """Calculate remaining amount until limit is reached."""
        return max(Decimal("0"), self.limit - self.applied)

    @computed_field
    @property
    def met(self) -> bool:
        """Check if accumulator limit has been reached."""
        return self.applied >= self.limit

    @computed_field
    @property
    def percent_used(self) -> float:
        """Calculate percentage of limit used."""
        if self.limit == 0:
            return 100.0
        return float((self.applied / self.limit) * 100)

    def apply(self, amount: Decimal) -> tuple[Accumulator, Decimal]:
        """Apply an amount to this accumulator."""
        applicable = min(amount, self.remaining)
        new_acc = self.model_copy(
            update={
                "applied": self.applied + applicable,
                "last_updated": date.today(),
            }
        )
        return new_acc, applicable

    def reset(self, new_plan_year: int | None = None) -> Accumulator:
        """Reset accumulator for new plan year."""
        return self.model_copy(
            update={
                "applied": Decimal("0"),
                "plan_year": new_plan_year or (self.plan_year + 1),
                "last_updated": date.today(),
            }
        )


class AccumulatorSet(BaseModel):
    """Collection of related accumulators for a member."""

    member_id: str = Field(..., description="Member identifier")
    plan_year: int = Field(..., description="Benefit plan year")

    # Medical accumulators
    deductible_individual_in: Accumulator | None = None
    deductible_individual_out: Accumulator | None = None
    deductible_family_in: Accumulator | None = None
    deductible_family_out: Accumulator | None = None
    oop_individual_in: Accumulator | None = None
    oop_individual_out: Accumulator | None = None
    oop_family_in: Accumulator | None = None
    oop_family_out: Accumulator | None = None

    # Pharmacy-specific accumulators
    rx_deductible: Accumulator | None = None
    rx_oop: Accumulator | None = None
    specialty_oop: Accumulator | None = None

    def _is_in_network(self, network: NetworkTier) -> bool:
        """Check if network tier is considered in-network."""
        return network in (
            NetworkTier.IN_NETWORK,
            NetworkTier.TIER_1,
            NetworkTier.TIER_2,
            NetworkTier.PREFERRED_PHARMACY,
            NetworkTier.MAIL_ORDER,
        )

    def apply_to_deductible(
        self,
        amount: Decimal,
        network: NetworkTier = NetworkTier.IN_NETWORK,
        benefit_type: BenefitType = BenefitType.COMBINED,
    ) -> tuple[AccumulatorSet, Decimal]:
        """Apply amount to deductible accumulators."""
        updates: dict = {}
        total_applied = Decimal("0")

        if benefit_type == BenefitType.PHARMACY and self.rx_deductible:
            new_rx_ded, applied = self.rx_deductible.apply(amount)
            updates["rx_deductible"] = new_rx_ded
            return self.model_copy(update=updates), applied

        if self._is_in_network(network):
            ind_acc = self.deductible_individual_in
            fam_acc = self.deductible_family_in
            ind_key = "deductible_individual_in"
            fam_key = "deductible_family_in"
        else:
            ind_acc = self.deductible_individual_out
            fam_acc = self.deductible_family_out
            ind_key = "deductible_individual_out"
            fam_key = "deductible_family_out"

        if fam_acc and fam_acc.met:
            return self, Decimal("0")

        if ind_acc and not ind_acc.met:
            new_ind, applied = ind_acc.apply(amount)
            updates[ind_key] = new_ind
            total_applied = applied

        if fam_acc and total_applied > 0:
            new_fam, _ = fam_acc.apply(total_applied)
            updates[fam_key] = new_fam

        return self.model_copy(update=updates), total_applied

    def apply_to_oop(
        self,
        amount: Decimal,
        network: NetworkTier = NetworkTier.IN_NETWORK,
        benefit_type: BenefitType = BenefitType.COMBINED,
    ) -> tuple[AccumulatorSet, Decimal]:
        """Apply amount to out-of-pocket accumulators."""
        updates: dict = {}
        total_applied = Decimal("0")

        if benefit_type == BenefitType.PHARMACY and self.rx_oop:
            new_rx_oop, applied = self.rx_oop.apply(amount)
            updates["rx_oop"] = new_rx_oop
            return self.model_copy(update=updates), applied

        if self._is_in_network(network):
            ind_acc = self.oop_individual_in
            fam_acc = self.oop_family_in
            ind_key = "oop_individual_in"
            fam_key = "oop_family_in"
        else:
            ind_acc = self.oop_individual_out
            fam_acc = self.oop_family_out
            ind_key = "oop_individual_out"
            fam_key = "oop_family_out"

        if fam_acc and fam_acc.met:
            return self, Decimal("0")

        if ind_acc and not ind_acc.met:
            new_ind, applied = ind_acc.apply(amount)
            updates[ind_key] = new_ind
            total_applied = applied

        if fam_acc and total_applied > 0:
            new_fam, _ = fam_acc.apply(total_applied)
            updates[fam_key] = new_fam

        return self.model_copy(update=updates), total_applied

    def is_deductible_met(
        self,
        network: NetworkTier = NetworkTier.IN_NETWORK,
        benefit_type: BenefitType = BenefitType.COMBINED,
    ) -> bool:
        """Check if deductible is met."""
        if benefit_type == BenefitType.PHARMACY and self.rx_deductible:
            return self.rx_deductible.met

        if self._is_in_network(network):
            ind = self.deductible_individual_in
            fam = self.deductible_family_in
        else:
            ind = self.deductible_individual_out
            fam = self.deductible_family_out

        if fam and fam.met:
            return True
        return ind.met if ind else False

    def is_oop_met(
        self,
        network: NetworkTier = NetworkTier.IN_NETWORK,
        benefit_type: BenefitType = BenefitType.COMBINED,
    ) -> bool:
        """Check if out-of-pocket maximum is met."""
        if benefit_type == BenefitType.PHARMACY and self.rx_oop:
            return self.rx_oop.met

        if self._is_in_network(network):
            ind = self.oop_individual_in
            fam = self.oop_family_in
        else:
            ind = self.oop_individual_out
            fam = self.oop_family_out

        if fam and fam.met:
            return True
        return ind.met if ind else False

    def get_deductible_remaining(
        self,
        network: NetworkTier = NetworkTier.IN_NETWORK,
        benefit_type: BenefitType = BenefitType.COMBINED,
    ) -> Decimal:
        """Get remaining deductible amount."""
        if benefit_type == BenefitType.PHARMACY and self.rx_deductible:
            return self.rx_deductible.remaining

        if self._is_in_network(network):
            ind = self.deductible_individual_in
            fam = self.deductible_family_in
        else:
            ind = self.deductible_individual_out
            fam = self.deductible_family_out

        if fam and fam.met:
            return Decimal("0")
        return ind.remaining if ind else Decimal("0")

    def reset_for_new_year(self, new_plan_year: int | None = None) -> AccumulatorSet:
        """Reset all accumulators for a new plan year."""
        new_year = new_plan_year or (self.plan_year + 1)
        updates: dict = {"plan_year": new_year}

        for field_name in [
            "deductible_individual_in", "deductible_individual_out",
            "deductible_family_in", "deductible_family_out",
            "oop_individual_in", "oop_individual_out",
            "oop_family_in", "oop_family_out",
            "rx_deductible", "rx_oop", "specialty_oop",
        ]:
            acc = getattr(self, field_name)
            if acc:
                updates[field_name] = acc.reset(new_year)

        return self.model_copy(update=updates)



# =============================================================================
# Factory Functions
# =============================================================================


def create_medical_accumulators(
    member_id: str,
    plan_year: int,
    deductible_individual: Decimal,
    deductible_family: Decimal,
    oop_individual: Decimal,
    oop_family: Decimal,
    deductible_individual_oon: Decimal | None = None,
    deductible_family_oon: Decimal | None = None,
    oop_individual_oon: Decimal | None = None,
    oop_family_oon: Decimal | None = None,
) -> AccumulatorSet:
    """Create accumulator set for medical benefits."""
    return AccumulatorSet(
        member_id=member_id,
        plan_year=plan_year,
        deductible_individual_in=Accumulator(
            accumulator_type=AccumulatorType.DEDUCTIBLE,
            level=AccumulatorLevel.INDIVIDUAL,
            network_tier=NetworkTier.IN_NETWORK,
            benefit_type=BenefitType.MEDICAL,
            limit=deductible_individual,
            plan_year=plan_year,
        ),
        deductible_family_in=Accumulator(
            accumulator_type=AccumulatorType.DEDUCTIBLE,
            level=AccumulatorLevel.FAMILY,
            network_tier=NetworkTier.IN_NETWORK,
            benefit_type=BenefitType.MEDICAL,
            limit=deductible_family,
            plan_year=plan_year,
        ),
        oop_individual_in=Accumulator(
            accumulator_type=AccumulatorType.OUT_OF_POCKET_MAX,
            level=AccumulatorLevel.INDIVIDUAL,
            network_tier=NetworkTier.IN_NETWORK,
            benefit_type=BenefitType.MEDICAL,
            limit=oop_individual,
            plan_year=plan_year,
        ),
        oop_family_in=Accumulator(
            accumulator_type=AccumulatorType.OUT_OF_POCKET_MAX,
            level=AccumulatorLevel.FAMILY,
            network_tier=NetworkTier.IN_NETWORK,
            benefit_type=BenefitType.MEDICAL,
            limit=oop_family,
            plan_year=plan_year,
        ),
        deductible_individual_out=Accumulator(
            accumulator_type=AccumulatorType.DEDUCTIBLE,
            level=AccumulatorLevel.INDIVIDUAL,
            network_tier=NetworkTier.OUT_OF_NETWORK,
            benefit_type=BenefitType.MEDICAL,
            limit=deductible_individual_oon or deductible_individual * 2,
            plan_year=plan_year,
        ),
        deductible_family_out=Accumulator(
            accumulator_type=AccumulatorType.DEDUCTIBLE,
            level=AccumulatorLevel.FAMILY,
            network_tier=NetworkTier.OUT_OF_NETWORK,
            benefit_type=BenefitType.MEDICAL,
            limit=deductible_family_oon or deductible_family * 2,
            plan_year=plan_year,
        ),
        oop_individual_out=Accumulator(
            accumulator_type=AccumulatorType.OUT_OF_POCKET_MAX,
            level=AccumulatorLevel.INDIVIDUAL,
            network_tier=NetworkTier.OUT_OF_NETWORK,
            benefit_type=BenefitType.MEDICAL,
            limit=oop_individual_oon or oop_individual * 2,
            plan_year=plan_year,
        ),
        oop_family_out=Accumulator(
            accumulator_type=AccumulatorType.OUT_OF_POCKET_MAX,
            level=AccumulatorLevel.FAMILY,
            network_tier=NetworkTier.OUT_OF_NETWORK,
            benefit_type=BenefitType.MEDICAL,
            limit=oop_family_oon or oop_family * 2,
            plan_year=plan_year,
        ),
    )


def create_pharmacy_accumulators(
    member_id: str,
    plan_year: int,
    deductible: Decimal,
    oop_max: Decimal,
    specialty_oop: Decimal | None = None,
) -> AccumulatorSet:
    """Create accumulator set for pharmacy benefits."""
    acc_set = AccumulatorSet(
        member_id=member_id,
        plan_year=plan_year,
        rx_deductible=Accumulator(
            accumulator_type=AccumulatorType.RX_DEDUCTIBLE,
            level=AccumulatorLevel.INDIVIDUAL,
            network_tier=NetworkTier.PREFERRED_PHARMACY,
            benefit_type=BenefitType.PHARMACY,
            limit=deductible,
            plan_year=plan_year,
        ),
        rx_oop=Accumulator(
            accumulator_type=AccumulatorType.RX_OOP_MAX,
            level=AccumulatorLevel.INDIVIDUAL,
            network_tier=NetworkTier.PREFERRED_PHARMACY,
            benefit_type=BenefitType.PHARMACY,
            limit=oop_max,
            plan_year=plan_year,
        ),
    )

    if specialty_oop:
        acc_set = acc_set.model_copy(
            update={
                "specialty_oop": Accumulator(
                    accumulator_type=AccumulatorType.SPECIALTY_OOP,
                    level=AccumulatorLevel.INDIVIDUAL,
                    network_tier=NetworkTier.SPECIALTY_PHARMACY,
                    benefit_type=BenefitType.PHARMACY,
                    limit=specialty_oop,
                    plan_year=plan_year,
                )
            }
        )

    return acc_set


def create_integrated_accumulators(
    member_id: str,
    plan_year: int,
    deductible_individual: Decimal,
    deductible_family: Decimal,
    oop_individual: Decimal,
    oop_family: Decimal,
) -> AccumulatorSet:
    """Create accumulator set for integrated medical + pharmacy benefits."""
    return AccumulatorSet(
        member_id=member_id,
        plan_year=plan_year,
        deductible_individual_in=Accumulator(
            accumulator_type=AccumulatorType.DEDUCTIBLE,
            level=AccumulatorLevel.INDIVIDUAL,
            network_tier=NetworkTier.IN_NETWORK,
            benefit_type=BenefitType.COMBINED,
            limit=deductible_individual,
            plan_year=plan_year,
        ),
        deductible_family_in=Accumulator(
            accumulator_type=AccumulatorType.DEDUCTIBLE,
            level=AccumulatorLevel.FAMILY,
            network_tier=NetworkTier.IN_NETWORK,
            benefit_type=BenefitType.COMBINED,
            limit=deductible_family,
            plan_year=plan_year,
        ),
        oop_individual_in=Accumulator(
            accumulator_type=AccumulatorType.OUT_OF_POCKET_MAX,
            level=AccumulatorLevel.INDIVIDUAL,
            network_tier=NetworkTier.IN_NETWORK,
            benefit_type=BenefitType.COMBINED,
            limit=oop_individual,
            plan_year=plan_year,
        ),
        oop_family_in=Accumulator(
            accumulator_type=AccumulatorType.OUT_OF_POCKET_MAX,
            level=AccumulatorLevel.FAMILY,
            network_tier=NetworkTier.IN_NETWORK,
            benefit_type=BenefitType.COMBINED,
            limit=oop_family,
            plan_year=plan_year,
        ),
    )


__all__ = [
    "AccumulatorType",
    "AccumulatorLevel",
    "NetworkTier",
    "BenefitType",
    "Accumulator",
    "AccumulatorSet",
    "create_medical_accumulators",
    "create_pharmacy_accumulators",
    "create_integrated_accumulators",
]
