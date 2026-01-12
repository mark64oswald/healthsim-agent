"""
Tests for benefits/accumulators.py.

Covers:
- Enum types (AccumulatorType, AccumulatorLevel, NetworkTier, BenefitType)
- Accumulator model - computed fields and methods
- AccumulatorSet - apply and check methods
- Factory functions for creating accumulator sets
"""

import pytest
from datetime import date
from decimal import Decimal

from healthsim_agent.benefits.accumulators import (
    AccumulatorType,
    AccumulatorLevel,
    NetworkTier,
    BenefitType,
    Accumulator,
    AccumulatorSet,
    create_medical_accumulators,
    create_pharmacy_accumulators,
    create_integrated_accumulators,
)


class TestAccumulatorTypeEnum:
    """Tests for AccumulatorType enum."""
    
    def test_deductible_type(self):
        """Test deductible type."""
        assert AccumulatorType.DEDUCTIBLE.value == "deductible"
    
    def test_oop_max_type(self):
        """Test OOP max type."""
        assert AccumulatorType.OUT_OF_POCKET_MAX.value == "oop_max"
    
    def test_rx_types(self):
        """Test pharmacy-specific types."""
        assert AccumulatorType.RX_DEDUCTIBLE.value == "rx_deductible"
        assert AccumulatorType.RX_OOP_MAX.value == "rx_oop_max"
        assert AccumulatorType.SPECIALTY_OOP.value == "specialty_oop"


class TestAccumulatorLevelEnum:
    """Tests for AccumulatorLevel enum."""
    
    def test_individual_level(self):
        """Test individual level."""
        assert AccumulatorLevel.INDIVIDUAL.value == "individual"
    
    def test_family_level(self):
        """Test family level."""
        assert AccumulatorLevel.FAMILY.value == "family"


class TestNetworkTierEnum:
    """Tests for NetworkTier enum."""
    
    def test_in_network(self):
        """Test in-network tier."""
        assert NetworkTier.IN_NETWORK.value == "in_network"
    
    def test_out_of_network(self):
        """Test out-of-network tier."""
        assert NetworkTier.OUT_OF_NETWORK.value == "out_of_network"
    
    def test_pharmacy_tiers(self):
        """Test pharmacy network tiers."""
        assert NetworkTier.PREFERRED_PHARMACY.value == "preferred_pharmacy"
        assert NetworkTier.MAIL_ORDER.value == "mail_order"
        assert NetworkTier.SPECIALTY_PHARMACY.value == "specialty_pharmacy"


class TestBenefitTypeEnum:
    """Tests for BenefitType enum."""
    
    def test_medical_type(self):
        """Test medical benefit type."""
        assert BenefitType.MEDICAL.value == "medical"
    
    def test_pharmacy_type(self):
        """Test pharmacy benefit type."""
        assert BenefitType.PHARMACY.value == "pharmacy"
    
    def test_combined_type(self):
        """Test combined benefit type."""
        assert BenefitType.COMBINED.value == "combined"


class TestAccumulatorModel:
    """Tests for Accumulator model."""
    
    def test_create_basic_accumulator(self):
        """Test creating basic accumulator."""
        acc = Accumulator(
            accumulator_type=AccumulatorType.DEDUCTIBLE,
            limit=Decimal("1000"),
            plan_year=2024
        )
        
        assert acc.accumulator_type == AccumulatorType.DEDUCTIBLE
        assert acc.limit == Decimal("1000")
        assert acc.applied == Decimal("0")
        assert acc.plan_year == 2024
    
    def test_accumulator_defaults(self):
        """Test accumulator default values."""
        acc = Accumulator(
            accumulator_type=AccumulatorType.DEDUCTIBLE,
            limit=Decimal("500"),
            plan_year=2024
        )
        
        assert acc.level == AccumulatorLevel.INDIVIDUAL
        assert acc.network_tier == NetworkTier.IN_NETWORK
        assert acc.benefit_type == BenefitType.COMBINED


class TestAccumulatorComputedFields:
    """Tests for Accumulator computed fields."""
    
    def test_remaining_with_no_applied(self):
        """Test remaining when nothing applied."""
        acc = Accumulator(
            accumulator_type=AccumulatorType.DEDUCTIBLE,
            limit=Decimal("1000"),
            plan_year=2024
        )
        
        assert acc.remaining == Decimal("1000")
    
    def test_remaining_with_partial_applied(self):
        """Test remaining with partial amount applied."""
        acc = Accumulator(
            accumulator_type=AccumulatorType.DEDUCTIBLE,
            limit=Decimal("1000"),
            applied=Decimal("300"),
            plan_year=2024
        )
        
        assert acc.remaining == Decimal("700")
    
    def test_remaining_with_over_applied(self):
        """Test remaining caps at zero."""
        acc = Accumulator(
            accumulator_type=AccumulatorType.DEDUCTIBLE,
            limit=Decimal("1000"),
            applied=Decimal("1500"),  # Over limit
            plan_year=2024
        )
        
        assert acc.remaining == Decimal("0")
    
    def test_met_when_not_met(self):
        """Test met is False when limit not reached."""
        acc = Accumulator(
            accumulator_type=AccumulatorType.DEDUCTIBLE,
            limit=Decimal("1000"),
            applied=Decimal("500"),
            plan_year=2024
        )
        
        assert acc.met is False
    
    def test_met_when_exactly_met(self):
        """Test met is True when limit exactly reached."""
        acc = Accumulator(
            accumulator_type=AccumulatorType.DEDUCTIBLE,
            limit=Decimal("1000"),
            applied=Decimal("1000"),
            plan_year=2024
        )
        
        assert acc.met is True
    
    def test_met_when_exceeded(self):
        """Test met is True when limit exceeded."""
        acc = Accumulator(
            accumulator_type=AccumulatorType.DEDUCTIBLE,
            limit=Decimal("1000"),
            applied=Decimal("1200"),
            plan_year=2024
        )
        
        assert acc.met is True
    
    def test_percent_used_at_zero(self):
        """Test percent_used at zero."""
        acc = Accumulator(
            accumulator_type=AccumulatorType.DEDUCTIBLE,
            limit=Decimal("1000"),
            applied=Decimal("0"),
            plan_year=2024
        )
        
        assert acc.percent_used == 0.0
    
    def test_percent_used_at_50(self):
        """Test percent_used at 50%."""
        acc = Accumulator(
            accumulator_type=AccumulatorType.DEDUCTIBLE,
            limit=Decimal("1000"),
            applied=Decimal("500"),
            plan_year=2024
        )
        
        assert acc.percent_used == 50.0
    
    def test_percent_used_at_100(self):
        """Test percent_used at 100%."""
        acc = Accumulator(
            accumulator_type=AccumulatorType.DEDUCTIBLE,
            limit=Decimal("1000"),
            applied=Decimal("1000"),
            plan_year=2024
        )
        
        assert acc.percent_used == 100.0
    
    def test_percent_used_zero_limit(self):
        """Test percent_used with zero limit."""
        acc = Accumulator(
            accumulator_type=AccumulatorType.DEDUCTIBLE,
            limit=Decimal("0"),
            plan_year=2024
        )
        
        assert acc.percent_used == 100.0  # Edge case


class TestAccumulatorApply:
    """Tests for Accumulator.apply method."""
    
    def test_apply_full_amount(self):
        """Test applying amount under remaining."""
        acc = Accumulator(
            accumulator_type=AccumulatorType.DEDUCTIBLE,
            limit=Decimal("1000"),
            plan_year=2024
        )
        
        new_acc, applied = acc.apply(Decimal("300"))
        
        assert applied == Decimal("300")
        assert new_acc.applied == Decimal("300")
        assert acc.applied == Decimal("0")  # Original unchanged
    
    def test_apply_partial_amount(self):
        """Test applying amount that exceeds remaining."""
        acc = Accumulator(
            accumulator_type=AccumulatorType.DEDUCTIBLE,
            limit=Decimal("1000"),
            applied=Decimal("800"),
            plan_year=2024
        )
        
        new_acc, applied = acc.apply(Decimal("500"))
        
        assert applied == Decimal("200")  # Only remaining applied
        assert new_acc.applied == Decimal("1000")
    
    def test_apply_when_already_met(self):
        """Test applying when accumulator already met."""
        acc = Accumulator(
            accumulator_type=AccumulatorType.DEDUCTIBLE,
            limit=Decimal("1000"),
            applied=Decimal("1000"),
            plan_year=2024
        )
        
        new_acc, applied = acc.apply(Decimal("500"))
        
        assert applied == Decimal("0")
        assert new_acc.applied == Decimal("1000")


class TestAccumulatorReset:
    """Tests for Accumulator.reset method."""
    
    def test_reset_clears_applied(self):
        """Test reset clears applied amount."""
        acc = Accumulator(
            accumulator_type=AccumulatorType.DEDUCTIBLE,
            limit=Decimal("1000"),
            applied=Decimal("750"),
            plan_year=2024
        )
        
        new_acc = acc.reset()
        
        assert new_acc.applied == Decimal("0")
        assert new_acc.plan_year == 2025  # Incremented
        assert acc.applied == Decimal("750")  # Original unchanged
    
    def test_reset_with_specific_year(self):
        """Test reset with specific plan year."""
        acc = Accumulator(
            accumulator_type=AccumulatorType.DEDUCTIBLE,
            limit=Decimal("1000"),
            plan_year=2024
        )
        
        new_acc = acc.reset(new_plan_year=2026)
        
        assert new_acc.plan_year == 2026


class TestAccumulatorSetBasics:
    """Tests for AccumulatorSet basics."""
    
    def test_create_empty_set(self):
        """Test creating empty accumulator set."""
        acc_set = AccumulatorSet(
            member_id="MEM001",
            plan_year=2024
        )
        
        assert acc_set.member_id == "MEM001"
        assert acc_set.plan_year == 2024
        assert acc_set.deductible_individual_in is None


class TestAccumulatorSetIsInNetwork:
    """Tests for AccumulatorSet._is_in_network method."""
    
    def test_in_network_is_in_network(self):
        """Test IN_NETWORK is considered in-network."""
        acc_set = AccumulatorSet(member_id="M1", plan_year=2024)
        
        assert acc_set._is_in_network(NetworkTier.IN_NETWORK) is True
    
    def test_tier1_is_in_network(self):
        """Test TIER_1 is considered in-network."""
        acc_set = AccumulatorSet(member_id="M1", plan_year=2024)
        
        assert acc_set._is_in_network(NetworkTier.TIER_1) is True
    
    def test_out_of_network_is_not_in_network(self):
        """Test OUT_OF_NETWORK is not considered in-network."""
        acc_set = AccumulatorSet(member_id="M1", plan_year=2024)
        
        assert acc_set._is_in_network(NetworkTier.OUT_OF_NETWORK) is False
    
    def test_tier3_is_not_in_network(self):
        """Test TIER_3 is not considered in-network."""
        acc_set = AccumulatorSet(member_id="M1", plan_year=2024)
        
        assert acc_set._is_in_network(NetworkTier.TIER_3) is False


class TestAccumulatorSetApplyToDeductible:
    """Tests for AccumulatorSet.apply_to_deductible method."""
    
    def test_apply_to_deductible_in_network(self):
        """Test applying to in-network deductible."""
        acc_set = create_medical_accumulators(
            member_id="M1",
            plan_year=2024,
            deductible_individual=Decimal("1000"),
            deductible_family=Decimal("2500"),
            oop_individual=Decimal("5000"),
            oop_family=Decimal("10000")
        )
        
        new_set, applied = acc_set.apply_to_deductible(Decimal("300"))
        
        assert applied == Decimal("300")
        assert new_set.deductible_individual_in.applied == Decimal("300")
        assert new_set.deductible_family_in.applied == Decimal("300")
    
    def test_apply_to_deductible_out_of_network(self):
        """Test applying to out-of-network deductible."""
        acc_set = create_medical_accumulators(
            member_id="M1",
            plan_year=2024,
            deductible_individual=Decimal("1000"),
            deductible_family=Decimal("2500"),
            oop_individual=Decimal("5000"),
            oop_family=Decimal("10000")
        )
        
        new_set, applied = acc_set.apply_to_deductible(
            Decimal("500"),
            network=NetworkTier.OUT_OF_NETWORK
        )
        
        assert applied == Decimal("500")
        assert new_set.deductible_individual_out.applied == Decimal("500")
    
    def test_apply_to_deductible_when_family_met(self):
        """Test no application when family deductible met."""
        acc_set = create_medical_accumulators(
            member_id="M1",
            plan_year=2024,
            deductible_individual=Decimal("1000"),
            deductible_family=Decimal("2500"),
            oop_individual=Decimal("5000"),
            oop_family=Decimal("10000")
        )
        
        # Manually set family deductible as met
        acc_set = acc_set.model_copy(
            update={
                "deductible_family_in": acc_set.deductible_family_in.model_copy(
                    update={"applied": Decimal("2500")}
                )
            }
        )
        
        new_set, applied = acc_set.apply_to_deductible(Decimal("500"))
        
        assert applied == Decimal("0")
    
    def test_apply_to_rx_deductible(self):
        """Test applying to pharmacy deductible."""
        acc_set = create_pharmacy_accumulators(
            member_id="M1",
            plan_year=2024,
            deductible=Decimal("500"),
            oop_max=Decimal("2000")
        )
        
        new_set, applied = acc_set.apply_to_deductible(
            Decimal("100"),
            benefit_type=BenefitType.PHARMACY
        )
        
        assert applied == Decimal("100")
        assert new_set.rx_deductible.applied == Decimal("100")


class TestAccumulatorSetApplyToOOP:
    """Tests for AccumulatorSet.apply_to_oop method."""
    
    def test_apply_to_oop_in_network(self):
        """Test applying to in-network OOP."""
        acc_set = create_medical_accumulators(
            member_id="M1",
            plan_year=2024,
            deductible_individual=Decimal("1000"),
            deductible_family=Decimal("2500"),
            oop_individual=Decimal("5000"),
            oop_family=Decimal("10000")
        )
        
        new_set, applied = acc_set.apply_to_oop(Decimal("1000"))
        
        assert applied == Decimal("1000")
        assert new_set.oop_individual_in.applied == Decimal("1000")
    
    def test_apply_to_rx_oop(self):
        """Test applying to pharmacy OOP."""
        acc_set = create_pharmacy_accumulators(
            member_id="M1",
            plan_year=2024,
            deductible=Decimal("500"),
            oop_max=Decimal("2000")
        )
        
        new_set, applied = acc_set.apply_to_oop(
            Decimal("300"),
            benefit_type=BenefitType.PHARMACY
        )
        
        assert applied == Decimal("300")
        assert new_set.rx_oop.applied == Decimal("300")


class TestAccumulatorSetIsDeductibleMet:
    """Tests for AccumulatorSet.is_deductible_met method."""
    
    def test_deductible_not_met(self):
        """Test when deductible not met."""
        acc_set = create_medical_accumulators(
            member_id="M1",
            plan_year=2024,
            deductible_individual=Decimal("1000"),
            deductible_family=Decimal("2500"),
            oop_individual=Decimal("5000"),
            oop_family=Decimal("10000")
        )
        
        assert acc_set.is_deductible_met() is False
    
    def test_individual_deductible_met(self):
        """Test when individual deductible met."""
        acc_set = create_medical_accumulators(
            member_id="M1",
            plan_year=2024,
            deductible_individual=Decimal("1000"),
            deductible_family=Decimal("2500"),
            oop_individual=Decimal("5000"),
            oop_family=Decimal("10000")
        )
        
        # Apply full deductible
        new_set, _ = acc_set.apply_to_deductible(Decimal("1000"))
        
        assert new_set.is_deductible_met() is True
    
    def test_family_deductible_met(self):
        """Test when family deductible met."""
        acc_set = create_medical_accumulators(
            member_id="M1",
            plan_year=2024,
            deductible_individual=Decimal("1000"),
            deductible_family=Decimal("2500"),
            oop_individual=Decimal("5000"),
            oop_family=Decimal("10000")
        )
        
        # Set family deductible as met
        acc_set = acc_set.model_copy(
            update={
                "deductible_family_in": acc_set.deductible_family_in.model_copy(
                    update={"applied": Decimal("2500")}
                )
            }
        )
        
        assert acc_set.is_deductible_met() is True


class TestAccumulatorSetIsOOPMet:
    """Tests for AccumulatorSet.is_oop_met method."""
    
    def test_oop_not_met(self):
        """Test when OOP not met."""
        acc_set = create_medical_accumulators(
            member_id="M1",
            plan_year=2024,
            deductible_individual=Decimal("1000"),
            deductible_family=Decimal("2500"),
            oop_individual=Decimal("5000"),
            oop_family=Decimal("10000")
        )
        
        assert acc_set.is_oop_met() is False


class TestAccumulatorSetGetDeductibleRemaining:
    """Tests for AccumulatorSet.get_deductible_remaining method."""
    
    def test_get_deductible_remaining_full(self):
        """Test getting full deductible remaining."""
        acc_set = create_medical_accumulators(
            member_id="M1",
            plan_year=2024,
            deductible_individual=Decimal("1000"),
            deductible_family=Decimal("2500"),
            oop_individual=Decimal("5000"),
            oop_family=Decimal("10000")
        )
        
        remaining = acc_set.get_deductible_remaining()
        
        assert remaining == Decimal("1000")
    
    def test_get_deductible_remaining_partial(self):
        """Test getting partial deductible remaining."""
        acc_set = create_medical_accumulators(
            member_id="M1",
            plan_year=2024,
            deductible_individual=Decimal("1000"),
            deductible_family=Decimal("2500"),
            oop_individual=Decimal("5000"),
            oop_family=Decimal("10000")
        )
        
        new_set, _ = acc_set.apply_to_deductible(Decimal("300"))
        remaining = new_set.get_deductible_remaining()
        
        assert remaining == Decimal("700")


class TestAccumulatorSetResetForNewYear:
    """Tests for AccumulatorSet.reset_for_new_year method."""
    
    def test_reset_all_accumulators(self):
        """Test resetting all accumulators for new year."""
        acc_set = create_medical_accumulators(
            member_id="M1",
            plan_year=2024,
            deductible_individual=Decimal("1000"),
            deductible_family=Decimal("2500"),
            oop_individual=Decimal("5000"),
            oop_family=Decimal("10000")
        )
        
        # Apply some amounts
        acc_set, _ = acc_set.apply_to_deductible(Decimal("500"))
        acc_set, _ = acc_set.apply_to_oop(Decimal("1000"))
        
        # Reset
        new_set = acc_set.reset_for_new_year()
        
        assert new_set.plan_year == 2025
        assert new_set.deductible_individual_in.applied == Decimal("0")
        assert new_set.oop_individual_in.applied == Decimal("0")
    
    def test_reset_with_specific_year(self):
        """Test resetting with specific year."""
        acc_set = create_medical_accumulators(
            member_id="M1",
            plan_year=2024,
            deductible_individual=Decimal("1000"),
            deductible_family=Decimal("2500"),
            oop_individual=Decimal("5000"),
            oop_family=Decimal("10000")
        )
        
        new_set = acc_set.reset_for_new_year(2030)
        
        assert new_set.plan_year == 2030


class TestCreateMedicalAccumulators:
    """Tests for create_medical_accumulators factory."""
    
    def test_creates_all_medical_accumulators(self):
        """Test factory creates all medical accumulators."""
        acc_set = create_medical_accumulators(
            member_id="M1",
            plan_year=2024,
            deductible_individual=Decimal("1000"),
            deductible_family=Decimal("2500"),
            oop_individual=Decimal("5000"),
            oop_family=Decimal("10000")
        )
        
        # In-network
        assert acc_set.deductible_individual_in is not None
        assert acc_set.deductible_individual_in.limit == Decimal("1000")
        assert acc_set.deductible_family_in.limit == Decimal("2500")
        assert acc_set.oop_individual_in.limit == Decimal("5000")
        assert acc_set.oop_family_in.limit == Decimal("10000")
        
        # Out-of-network (defaults to 2x)
        assert acc_set.deductible_individual_out.limit == Decimal("2000")
        assert acc_set.oop_family_out.limit == Decimal("20000")
    
    def test_creates_with_custom_oon(self):
        """Test factory with custom out-of-network limits."""
        acc_set = create_medical_accumulators(
            member_id="M1",
            plan_year=2024,
            deductible_individual=Decimal("1000"),
            deductible_family=Decimal("2500"),
            oop_individual=Decimal("5000"),
            oop_family=Decimal("10000"),
            deductible_individual_oon=Decimal("3000"),
            oop_individual_oon=Decimal("15000")
        )
        
        assert acc_set.deductible_individual_out.limit == Decimal("3000")
        assert acc_set.oop_individual_out.limit == Decimal("15000")


class TestCreatePharmacyAccumulators:
    """Tests for create_pharmacy_accumulators factory."""
    
    def test_creates_pharmacy_accumulators(self):
        """Test factory creates pharmacy accumulators."""
        acc_set = create_pharmacy_accumulators(
            member_id="M1",
            plan_year=2024,
            deductible=Decimal("500"),
            oop_max=Decimal("2000")
        )
        
        assert acc_set.rx_deductible is not None
        assert acc_set.rx_deductible.limit == Decimal("500")
        assert acc_set.rx_oop.limit == Decimal("2000")
        assert acc_set.specialty_oop is None
    
    def test_creates_with_specialty_oop(self):
        """Test factory with specialty OOP."""
        acc_set = create_pharmacy_accumulators(
            member_id="M1",
            plan_year=2024,
            deductible=Decimal("500"),
            oop_max=Decimal("2000"),
            specialty_oop=Decimal("5000")
        )
        
        assert acc_set.specialty_oop is not None
        assert acc_set.specialty_oop.limit == Decimal("5000")


class TestCreateIntegratedAccumulators:
    """Tests for create_integrated_accumulators factory."""
    
    def test_creates_integrated_accumulators(self):
        """Test factory creates integrated accumulators."""
        acc_set = create_integrated_accumulators(
            member_id="M1",
            plan_year=2024,
            deductible_individual=Decimal("1500"),
            deductible_family=Decimal("3000"),
            oop_individual=Decimal("8000"),
            oop_family=Decimal("16000")
        )
        
        assert acc_set.deductible_individual_in is not None
        assert acc_set.deductible_individual_in.benefit_type == BenefitType.COMBINED
        assert acc_set.deductible_individual_in.limit == Decimal("1500")
        
        # Should not have OON for integrated plans
        assert acc_set.deductible_individual_out is None
