"""Tests for RxMemberSim claims module.

Tests claim models, adjudication engine, and claim factory.
"""

from datetime import date, timedelta
from decimal import Decimal

import pytest

from healthsim_agent.products.rxmembersim.claims.claim import (
    PharmacyClaim,
    TransactionCode,
)
from healthsim_agent.products.rxmembersim.claims.response import (
    ClaimResponse,
    DURResponseAlert,
    RejectCode,
)
from healthsim_agent.products.rxmembersim.claims.adjudication import (
    AdjudicationEngine,
    EligibilityResult,
    PricingResult,
)
from healthsim_agent.products.rxmembersim.claims.factory import (
    PharmacyClaimGenerator,
    COMMON_DRUGS,
)


# ============================================================================
# CLAIM MODELS TESTS
# ============================================================================

class TestTransactionCode:
    """Tests for TransactionCode enum."""
    
    def test_billing_code(self):
        """Test billing transaction code value."""
        assert TransactionCode.BILLING.value == "B1"
    
    def test_reversal_code(self):
        """Test reversal transaction code value."""
        assert TransactionCode.REVERSAL.value == "B2"
    
    def test_rebill_code(self):
        """Test rebill transaction code value."""
        assert TransactionCode.REBILL.value == "B3"


class TestPharmacyClaim:
    """Tests for PharmacyClaim model."""
    
    @pytest.fixture
    def sample_claim(self) -> PharmacyClaim:
        """Create a sample pharmacy claim."""
        return PharmacyClaim(
            claim_id="CLM-123456789012",
            transaction_code=TransactionCode.BILLING,
            service_date=date(2025, 1, 10),
            pharmacy_npi="1234567890",
            pharmacy_ncpdp="1234567",
            member_id="MEM-001",
            cardholder_id="CARD-001",
            person_code="01",
            bin="610014",
            pcn="RXTEST",
            group_number="GRP001",
            prescription_number="RX1234567",
            fill_number=0,
            ndc="00071015523",
            quantity_dispensed=Decimal("30"),
            days_supply=30,
            daw_code="0",
            compound_code="0",
            prescriber_npi="9876543210",
            ingredient_cost_submitted=Decimal("100.00"),
            dispensing_fee_submitted=Decimal("2.00"),
            usual_customary_charge=Decimal("107.00"),
            gross_amount_due=Decimal("102.00"),
        )
    
    def test_create_claim_basic(self, sample_claim):
        """Test basic claim creation."""
        assert sample_claim.claim_id == "CLM-123456789012"
        assert sample_claim.transaction_code == TransactionCode.BILLING
    
    def test_claim_service_date(self, sample_claim):
        """Test service date field."""
        assert sample_claim.service_date == date(2025, 1, 10)
    
    def test_claim_pharmacy_fields(self, sample_claim):
        """Test pharmacy-related fields."""
        assert sample_claim.pharmacy_npi == "1234567890"
        assert sample_claim.pharmacy_ncpdp == "1234567"
    
    def test_claim_member_fields(self, sample_claim):
        """Test member-related fields."""
        assert sample_claim.member_id == "MEM-001"
        assert sample_claim.cardholder_id == "CARD-001"
        assert sample_claim.bin == "610014"
        assert sample_claim.pcn == "RXTEST"
        assert sample_claim.group_number == "GRP001"
    
    def test_claim_prescription_fields(self, sample_claim):
        """Test prescription-related fields."""
        assert sample_claim.prescription_number == "RX1234567"
        assert sample_claim.fill_number == 0
        assert sample_claim.ndc == "00071015523"
        assert sample_claim.quantity_dispensed == Decimal("30")
        assert sample_claim.days_supply == 30
    
    def test_claim_pricing_fields(self, sample_claim):
        """Test pricing fields."""
        assert sample_claim.ingredient_cost_submitted == Decimal("100.00")
        assert sample_claim.dispensing_fee_submitted == Decimal("2.00")
        assert sample_claim.gross_amount_due == Decimal("102.00")
    
    def test_claim_optional_prior_auth(self, sample_claim):
        """Test optional prior auth fields default to None."""
        assert sample_claim.prior_auth_number is None
        assert sample_claim.prior_auth_type is None
    
    def test_claim_with_prior_auth(self):
        """Test claim with prior authorization."""
        claim = PharmacyClaim(
            claim_id="CLM-PA-001",
            transaction_code=TransactionCode.BILLING,
            service_date=date(2025, 1, 10),
            pharmacy_npi="1234567890",
            member_id="MEM-001",
            cardholder_id="CARD-001",
            person_code="01",
            bin="610014",
            pcn="RXTEST",
            group_number="GRP001",
            prescription_number="RX1234567",
            fill_number=0,
            ndc="00071015523",
            quantity_dispensed=Decimal("30"),
            days_supply=30,
            daw_code="0",
            prescriber_npi="9876543210",
            ingredient_cost_submitted=Decimal("100.00"),
            dispensing_fee_submitted=Decimal("2.00"),
            usual_customary_charge=Decimal("107.00"),
            gross_amount_due=Decimal("102.00"),
            prior_auth_number="PA12345",
            prior_auth_type="1",
        )
        assert claim.prior_auth_number == "PA12345"
        assert claim.prior_auth_type == "1"


# ============================================================================
# RESPONSE MODELS TESTS
# ============================================================================

class TestRejectCode:
    """Tests for RejectCode model."""
    
    def test_create_reject_code(self):
        """Test creating a reject code."""
        code = RejectCode(code="70", description="Product/Service Not Covered")
        assert code.code == "70"
        assert code.description == "Product/Service Not Covered"


class TestDURResponseAlert:
    """Tests for DURResponseAlert model."""
    
    def test_create_dur_alert_minimal(self):
        """Test creating DUR alert with minimal fields."""
        alert = DURResponseAlert(
            reason_for_service="DD",
            clinical_significance="1",
        )
        assert alert.reason_for_service == "DD"
        assert alert.clinical_significance == "1"
        assert alert.other_pharmacy_indicator is None
    
    def test_create_dur_alert_full(self):
        """Test creating DUR alert with all fields."""
        alert = DURResponseAlert(
            reason_for_service="DD",
            clinical_significance="1",
            other_pharmacy_indicator="N",
            previous_fill_date="20250101",
            quantity_of_previous_fill=Decimal("30"),
            database_indicator="2",
            other_prescriber_indicator="N",
            message="Drug-drug interaction detected",
        )
        assert alert.message == "Drug-drug interaction detected"
        assert alert.quantity_of_previous_fill == Decimal("30")


class TestClaimResponse:
    """Tests for ClaimResponse model."""
    
    def test_create_approved_response(self):
        """Test creating an approved claim response."""
        response = ClaimResponse(
            claim_id="CLM-001",
            transaction_response_status="A",
            response_status="P",
            authorization_number="AUTH123456789",
            ingredient_cost_paid=Decimal("100.00"),
            dispensing_fee_paid=Decimal("2.00"),
            total_amount_paid=Decimal("82.00"),
            patient_pay_amount=Decimal("20.00"),
            copay_amount=Decimal("20.00"),
        )
        assert response.response_status == "P"
        assert response.authorization_number == "AUTH123456789"
        assert response.total_amount_paid == Decimal("82.00")
    
    def test_create_rejected_response(self):
        """Test creating a rejected claim response."""
        response = ClaimResponse(
            claim_id="CLM-002",
            transaction_response_status="R",
            response_status="R",
            reject_codes=[
                RejectCode(code="70", description="Product/Service Not Covered"),
                RejectCode(code="75", description="Prior Authorization Required"),
            ],
        )
        assert response.response_status == "R"
        assert len(response.reject_codes) == 2
        assert response.reject_codes[0].code == "70"
    
    def test_response_defaults(self):
        """Test response default values."""
        response = ClaimResponse(
            claim_id="CLM-003",
            transaction_response_status="A",
            response_status="P",
        )
        assert response.reject_codes == []
        assert response.dur_alerts == []
        assert response.copay_amount is None


# ============================================================================
# ADJUDICATION ENGINE TESTS
# ============================================================================

class TestEligibilityResult:
    """Tests for EligibilityResult dataclass."""
    
    def test_eligible_result(self):
        """Test eligible result."""
        result = EligibilityResult(eligible=True, reject_codes=[])
        assert result.eligible is True
        assert len(result.reject_codes) == 0
    
    def test_ineligible_result(self):
        """Test ineligible result with reject codes."""
        codes = [RejectCode(code="65", description="Patient Not Covered")]
        result = EligibilityResult(eligible=False, reject_codes=codes)
        assert result.eligible is False
        assert len(result.reject_codes) == 1


class TestPricingResult:
    """Tests for PricingResult dataclass."""
    
    def test_pricing_result(self):
        """Test pricing result fields."""
        result = PricingResult(
            ingredient_cost=Decimal("100.00"),
            dispensing_fee=Decimal("2.00"),
            plan_pays=Decimal("72.00"),
            patient_pays=Decimal("30.00"),
            copay=Decimal("30.00"),
            deductible_applied=Decimal("0.00"),
        )
        assert result.ingredient_cost == Decimal("100.00")
        assert result.plan_pays == Decimal("72.00")
        assert result.patient_pays == Decimal("30.00")


class TestAdjudicationEngine:
    """Tests for AdjudicationEngine."""
    
    @pytest.fixture
    def engine(self):
        """Create adjudication engine with test formulary."""
        from healthsim_agent.products.rxmembersim.formulary.formulary import (
            Formulary, FormularyDrug, FormularyTier,
        )
        formulary = Formulary(
            formulary_id="TEST-001",
            name="Test Formulary",
            effective_date="2025-01-01",
            tiers=[
                FormularyTier(tier_number=1, tier_name="Generic", copay_amount=Decimal("10")),
                FormularyTier(tier_number=2, tier_name="Brand", copay_amount=Decimal("30")),
            ],
        )
        formulary.add_drug(FormularyDrug(
            ndc="00071015523",
            gpi="39400010000310",
            drug_name="Atorvastatin 10mg",
            tier=1,
        ))
        formulary.add_drug(FormularyDrug(
            ndc="00069015430",
            gpi="39400050000310",
            drug_name="Lipitor 10mg",
            tier=2,
            requires_pa=True,
        ))
        return AdjudicationEngine(formulary=formulary)
    
    @pytest.fixture
    def member(self):
        """Create test member."""
        from healthsim_agent.products.rxmembersim.core.member import (
            RxMember, BenefitAccumulators, MemberDemographics
        )
        return RxMember(
            member_id="MEM-001",
            cardholder_id="CARD-001",
            person_code="01",
            bin="610014",
            pcn="RXTEST",
            group_number="GRP001",
            demographics=MemberDemographics(
                first_name="John",
                last_name="Doe",
                date_of_birth=date(1980, 5, 15),
                gender="M",
            ),
            effective_date=date(2025, 1, 1),
            accumulators=BenefitAccumulators(
                deductible_remaining=Decimal("500.00"),
                oop_remaining=Decimal("3000.00"),
            ),
        )
    
    @pytest.fixture
    def sample_claim(self):
        """Create sample claim for testing."""
        return PharmacyClaim(
            claim_id="CLM-TEST-001",
            transaction_code=TransactionCode.BILLING,
            service_date=date(2025, 1, 10),
            pharmacy_npi="1234567890",
            member_id="MEM-001",
            cardholder_id="CARD-001",
            person_code="01",
            bin="610014",
            pcn="RXTEST",
            group_number="GRP001",
            prescription_number="RX1234567",
            fill_number=0,
            ndc="00071015523",
            quantity_dispensed=Decimal("30"),
            days_supply=30,
            daw_code="0",
            prescriber_npi="9876543210",
            ingredient_cost_submitted=Decimal("100.00"),
            dispensing_fee_submitted=Decimal("2.00"),
            usual_customary_charge=Decimal("107.00"),
            gross_amount_due=Decimal("102.00"),
        )
    
    def test_adjudicate_approved_claim(self, engine, member, sample_claim):
        """Test successful claim adjudication."""
        response = engine.adjudicate(sample_claim, member)
        
        assert response.response_status == "P"
        assert response.transaction_response_status == "A"
        assert response.authorization_number is not None
        assert response.total_amount_paid is not None
    
    def test_adjudicate_ineligible_member_terminated(self, engine, member, sample_claim):
        """Test rejection when member is terminated."""
        member.termination_date = date(2025, 1, 5)
        sample_claim.service_date = date(2025, 1, 10)
        
        response = engine.adjudicate(sample_claim, member)
        
        assert response.response_status == "R"
        assert any(rc.code == "65" for rc in response.reject_codes)
    
    def test_adjudicate_ineligible_before_effective(self, engine, member, sample_claim):
        """Test rejection when service date before effective date."""
        sample_claim.service_date = date(2024, 12, 15)
        
        response = engine.adjudicate(sample_claim, member)
        
        assert response.response_status == "R"
        assert any(rc.code == "65" for rc in response.reject_codes)
    
    def test_adjudicate_wrong_bin(self, engine, member, sample_claim):
        """Test rejection for BIN mismatch."""
        sample_claim.bin = "999999"
        
        response = engine.adjudicate(sample_claim, member)
        
        assert response.response_status == "R"
        assert any(rc.code == "25" for rc in response.reject_codes)
    
    def test_adjudicate_wrong_pcn(self, engine, member, sample_claim):
        """Test rejection for PCN mismatch."""
        sample_claim.pcn = "WRONGPCN"
        
        response = engine.adjudicate(sample_claim, member)
        
        assert response.response_status == "R"
        assert any(rc.code == "26" for rc in response.reject_codes)
    
    def test_adjudicate_wrong_group(self, engine, member, sample_claim):
        """Test rejection for group ID mismatch."""
        sample_claim.group_number = "WRONGGRP"
        
        response = engine.adjudicate(sample_claim, member)
        
        assert response.response_status == "R"
        assert any(rc.code == "64" for rc in response.reject_codes)
    
    def test_adjudicate_not_covered_drug(self, engine, member, sample_claim):
        """Test rejection for non-formulary drug."""
        sample_claim.ndc = "99999999999"  # Not on formulary
        
        response = engine.adjudicate(sample_claim, member)
        
        assert response.response_status == "R"
        assert any(rc.code == "70" for rc in response.reject_codes)
    
    def test_adjudicate_pa_required_no_auth(self, engine, member, sample_claim):
        """Test rejection when PA required but not provided."""
        sample_claim.ndc = "00069015430"  # Lipitor (requires PA)
        
        response = engine.adjudicate(sample_claim, member)
        
        assert response.response_status == "R"
        assert any(rc.code == "75" for rc in response.reject_codes)
    
    def test_adjudicate_pa_required_with_auth(self, engine, member, sample_claim):
        """Test approval when PA required and provided."""
        sample_claim.ndc = "00069015430"  # Lipitor (requires PA)
        sample_claim.prior_auth_number = "PA12345"
        
        response = engine.adjudicate(sample_claim, member)
        
        assert response.response_status == "P"
    
    def test_create_default_engine(self):
        """Test creating engine with default formulary."""
        engine = AdjudicationEngine()
        assert engine.formulary is not None
        assert engine.formulary.formulary_id == "DEFAULT"


# ============================================================================
# CLAIM FACTORY TESTS
# ============================================================================

class TestPharmacyClaimGenerator:
    """Tests for PharmacyClaimGenerator."""
    
    def test_generate_claim_without_member(self):
        """Test generating claim without providing member."""
        generator = PharmacyClaimGenerator(seed=42)
        claim = generator.generate()
        
        assert claim is not None
        assert claim.claim_id.startswith("CLM-")
        assert claim.prescription_number.startswith("RX")
        assert claim.transaction_code == TransactionCode.BILLING
    
    def test_generate_claim_with_seed_deterministic_drug(self):
        """Test that seed makes drug selection deterministic."""
        import random
        
        # Reset random state and generate
        random.seed(42)
        gen1 = PharmacyClaimGenerator(seed=42)
        drug1 = random.choice(COMMON_DRUGS)
        
        # Reset random state again
        random.seed(42)
        gen2 = PharmacyClaimGenerator(seed=42)
        drug2 = random.choice(COMMON_DRUGS)
        
        # Same seed should produce same drug selection
        assert drug1["ndc"] == drug2["ndc"]
    
    def test_generate_claim_with_specific_drug(self):
        """Test generating claim with specific drug."""
        generator = PharmacyClaimGenerator()
        drug = COMMON_DRUGS[0]  # Lipitor 10mg
        
        claim = generator.generate(drug=drug)
        
        assert claim.ndc == drug["ndc"]
        assert claim.days_supply == drug["days"]
    
    def test_generate_claim_with_service_date(self):
        """Test generating claim with specific service date."""
        generator = PharmacyClaimGenerator()
        service_date = date(2025, 1, 15)
        
        claim = generator.generate(service_date=service_date)
        
        assert claim.service_date == service_date
    
    def test_generate_claim_with_pharmacy_npi(self):
        """Test generating claim with specific pharmacy NPI."""
        generator = PharmacyClaimGenerator()
        pharmacy_npi = "1234567890"
        
        claim = generator.generate(pharmacy_npi=pharmacy_npi)
        
        assert claim.pharmacy_npi == pharmacy_npi
    
    def test_generate_claim_with_prescriber_npi(self):
        """Test generating claim with specific prescriber NPI."""
        generator = PharmacyClaimGenerator()
        prescriber_npi = "9876543210"
        
        claim = generator.generate(prescriber_npi=prescriber_npi)
        
        assert claim.prescriber_npi == prescriber_npi
    
    def test_generate_claim_with_fill_number(self):
        """Test generating claim with specific fill number."""
        generator = PharmacyClaimGenerator()
        
        claim = generator.generate(fill_number=3)
        
        assert claim.fill_number == 3
    
    def test_generate_claim_pricing_reasonable(self):
        """Test that generated pricing is reasonable."""
        generator = PharmacyClaimGenerator(seed=42)
        claim = generator.generate()
        
        # Ingredient cost should be positive
        assert claim.ingredient_cost_submitted > 0
        # Dispensing fee should be reasonable (1.50-3.00)
        assert Decimal("1.00") <= claim.dispensing_fee_submitted <= Decimal("4.00")
        # Gross amount should be sum of ingredients + dispensing fee
        expected_gross = claim.ingredient_cost_submitted + claim.dispensing_fee_submitted
        assert claim.gross_amount_due == expected_gross
    
    def test_generate_for_member(self):
        """Test generating multiple claims for a member."""
        from healthsim_agent.products.rxmembersim.core.member import (
            RxMember, BenefitAccumulators, MemberDemographics
        )
        
        member = RxMember(
            member_id="MEM-TEST",
            cardholder_id="CARD-TEST",
            person_code="01",
            bin="610014",
            pcn="RXTEST",
            group_number="GRP001",
            demographics=MemberDemographics(
                first_name="Jane",
                last_name="Smith",
                date_of_birth=date(1985, 3, 20),
                gender="F",
            ),
            effective_date=date(2025, 1, 1),
            accumulators=BenefitAccumulators(
                deductible_remaining=Decimal("500.00"),
                oop_remaining=Decimal("3000.00"),
            ),
        )
        
        generator = PharmacyClaimGenerator(seed=42)
        claims = generator.generate_for_member(member, count=5, date_range_days=30)
        
        assert len(claims) == 5
        # All claims should be for this member
        assert all(c.member_id == "MEM-TEST" for c in claims)
        assert all(c.bin == "610014" for c in claims)
        # Claims should be sorted by service date
        for i in range(len(claims) - 1):
            assert claims[i].service_date <= claims[i + 1].service_date
    
    def test_generate_for_member_limited_by_drug_count(self):
        """Test that claim count is limited by available drugs."""
        from healthsim_agent.products.rxmembersim.core.member import (
            RxMember, BenefitAccumulators, MemberDemographics
        )
        
        member = RxMember(
            member_id="MEM-TEST",
            cardholder_id="CARD-TEST",
            person_code="01",
            bin="610014",
            pcn="RXTEST",
            group_number="GRP001",
            demographics=MemberDemographics(
                first_name="Jane",
                last_name="Smith",
                date_of_birth=date(1985, 3, 20),
                gender="F",
            ),
            effective_date=date(2025, 1, 1),
            accumulators=BenefitAccumulators(
                deductible_remaining=Decimal("500.00"),
                oop_remaining=Decimal("3000.00"),
            ),
        )
        
        generator = PharmacyClaimGenerator(seed=42)
        # Request more claims than drugs
        claims = generator.generate_for_member(member, count=100)
        
        # Should be limited to number of available drugs
        assert len(claims) == len(COMMON_DRUGS)


class TestCommonDrugs:
    """Tests for COMMON_DRUGS reference data."""
    
    def test_common_drugs_not_empty(self):
        """Test that COMMON_DRUGS list is not empty."""
        assert len(COMMON_DRUGS) > 0
    
    def test_common_drugs_have_required_fields(self):
        """Test that all drugs have required fields."""
        for drug in COMMON_DRUGS:
            assert "ndc" in drug
            assert "name" in drug
            assert "awp" in drug
            assert "days" in drug
            assert "qty" in drug
    
    def test_common_drugs_valid_ndc_format(self):
        """Test that NDCs are 11-digit format."""
        for drug in COMMON_DRUGS:
            assert len(drug["ndc"]) == 11
            assert drug["ndc"].isdigit()
    
    def test_common_drugs_positive_pricing(self):
        """Test that all drug prices are positive."""
        for drug in COMMON_DRUGS:
            assert drug["awp"] > 0
            assert drug["days"] > 0
            assert drug["qty"] > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
