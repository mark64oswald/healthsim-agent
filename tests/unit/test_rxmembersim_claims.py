"""Tests for RxMemberSim claims module.

Tests pharmacy claim models, responses, and adjudication engine.
"""

from datetime import date
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
from healthsim_agent.products.rxmembersim.core.member import (
    RxMember,
    MemberDemographics,
    BenefitAccumulators,
)
from healthsim_agent.products.rxmembersim.formulary.formulary import (
    Formulary,
    FormularyDrug,
    FormularyTier,
)


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def sample_claim() -> PharmacyClaim:
    """Create a sample pharmacy claim."""
    return PharmacyClaim(
        claim_id="CLM001",
        transaction_code=TransactionCode.BILLING,
        service_date=date(2025, 1, 15),
        pharmacy_npi="1234567890",
        pharmacy_ncpdp="1234567",
        member_id="MEM001",
        cardholder_id="123456789",
        person_code="01",
        bin="610014",
        pcn="RXTEST",
        group_number="GRP001",
        prescription_number="RX123456",
        fill_number=0,
        ndc="00000000001",
        quantity_dispensed=Decimal("30"),
        days_supply=30,
        daw_code="0",
        prescriber_npi="9876543210",
        ingredient_cost_submitted=Decimal("100.00"),
        dispensing_fee_submitted=Decimal("5.00"),
        usual_customary_charge=Decimal("125.00"),
        gross_amount_due=Decimal("105.00"),
    )


@pytest.fixture
def sample_member() -> RxMember:
    """Create a sample pharmacy member."""
    return RxMember(
        member_id="MEM001",
        cardholder_id="123456789",
        person_code="01",
        bin="610014",
        pcn="RXTEST",
        group_number="GRP001",
        demographics=MemberDemographics(
            first_name="John",
            last_name="Smith",
            date_of_birth=date(1980, 5, 15),
            gender="M",
            address_line1="123 Main St",
            city="San Diego",
            state="CA",
            zip_code="92101",
        ),
        effective_date=date(2025, 1, 1),
        accumulators=BenefitAccumulators(
            deductible_total=Decimal("500.00"),
            deductible_remaining=Decimal("500.00"),
            oop_total=Decimal("3000.00"),
            oop_remaining=Decimal("3000.00"),
        ),
    )


@pytest.fixture
def test_formulary() -> Formulary:
    """Create a test formulary with covered drugs."""
    return Formulary(
        formulary_id="TEST001",
        name="Test Formulary",
        effective_date="2025-01-01",
        tiers=[
            FormularyTier(tier_number=1, tier_name="Generic", copay_amount=Decimal("10.00")),
            FormularyTier(tier_number=2, tier_name="Preferred Brand", copay_amount=Decimal("30.00")),
            FormularyTier(tier_number=3, tier_name="Non-Preferred", copay_amount=Decimal("50.00")),
        ],
        drugs={
            "00000000001": FormularyDrug(
                ndc="00000000001",
                gpi="00000000000000",
                drug_name="Test Drug",
                tier=1,
                covered=True,
            ),
            "00000000002": FormularyDrug(
                ndc="00000000002",
                gpi="00000000000001",
                drug_name="PA Required Drug",
                tier=2,
                covered=True,
                requires_pa=True,
            ),
        },
    )


# ============================================================================
# Test TransactionCode Enum
# ============================================================================

class TestTransactionCode:
    """Tests for TransactionCode enum."""

    def test_billing_code(self):
        """B1 is billing code."""
        assert TransactionCode.BILLING.value == "B1"

    def test_reversal_code(self):
        """B2 is reversal code."""
        assert TransactionCode.REVERSAL.value == "B2"

    def test_rebill_code(self):
        """B3 is rebill code."""
        assert TransactionCode.REBILL.value == "B3"

    def test_is_string_enum(self):
        """Transaction codes are string enums."""
        assert isinstance(TransactionCode.BILLING, str)
        assert TransactionCode.BILLING == "B1"


# ============================================================================
# Test PharmacyClaim Model
# ============================================================================

class TestPharmacyClaim:
    """Tests for PharmacyClaim model."""

    def test_create_basic_claim(self, sample_claim):
        """Create a basic pharmacy claim."""
        assert sample_claim.claim_id == "CLM001"
        assert sample_claim.transaction_code == TransactionCode.BILLING
        assert sample_claim.ndc == "00000000001"

    def test_claim_has_pharmacy_info(self, sample_claim):
        """Claim includes pharmacy information."""
        assert sample_claim.pharmacy_npi == "1234567890"
        assert sample_claim.pharmacy_ncpdp == "1234567"

    def test_claim_has_member_info(self, sample_claim):
        """Claim includes member information."""
        assert sample_claim.member_id == "MEM001"
        assert sample_claim.cardholder_id == "123456789"
        assert sample_claim.bin == "610014"
        assert sample_claim.pcn == "RXTEST"
        assert sample_claim.group_number == "GRP001"

    def test_claim_has_prescription_info(self, sample_claim):
        """Claim includes prescription details."""
        assert sample_claim.prescription_number == "RX123456"
        assert sample_claim.fill_number == 0
        assert sample_claim.quantity_dispensed == Decimal("30")
        assert sample_claim.days_supply == 30

    def test_claim_has_pricing(self, sample_claim):
        """Claim includes submitted pricing."""
        assert sample_claim.ingredient_cost_submitted == Decimal("100.00")
        assert sample_claim.dispensing_fee_submitted == Decimal("5.00")
        assert sample_claim.gross_amount_due == Decimal("105.00")

    def test_claim_optional_prior_auth(self, sample_claim):
        """Prior auth fields are optional."""
        assert sample_claim.prior_auth_number is None
        assert sample_claim.prior_auth_type is None

    def test_claim_with_prior_auth(self):
        """Claim can have prior authorization."""
        claim = PharmacyClaim(
            claim_id="CLM002",
            transaction_code=TransactionCode.BILLING,
            service_date=date(2025, 1, 15),
            pharmacy_npi="1234567890",
            member_id="MEM001",
            cardholder_id="123456789",
            person_code="01",
            bin="610014",
            pcn="RXTEST",
            group_number="GRP001",
            prescription_number="RX123456",
            fill_number=0,
            ndc="00000000001",
            quantity_dispensed=Decimal("30"),
            days_supply=30,
            daw_code="0",
            prescriber_npi="9876543210",
            ingredient_cost_submitted=Decimal("100.00"),
            dispensing_fee_submitted=Decimal("5.00"),
            usual_customary_charge=Decimal("125.00"),
            gross_amount_due=Decimal("105.00"),
            prior_auth_number="PA123456",
            prior_auth_type="1",
        )
        assert claim.prior_auth_number == "PA123456"


# ============================================================================
# Test RejectCode Model
# ============================================================================

class TestRejectCode:
    """Tests for RejectCode model."""

    def test_create_reject_code(self):
        """Create a reject code."""
        reject = RejectCode(code="70", description="Product/Service Not Covered")
        assert reject.code == "70"
        assert reject.description == "Product/Service Not Covered"

    def test_eligibility_reject_code(self):
        """Create eligibility reject code."""
        reject = RejectCode(code="65", description="Patient Not Covered")
        assert reject.code == "65"


# ============================================================================
# Test DURResponseAlert Model
# ============================================================================

class TestDURResponseAlert:
    """Tests for DURResponseAlert model."""

    def test_create_dur_alert(self):
        """Create a DUR alert."""
        alert = DURResponseAlert(
            reason_for_service="DD",
            clinical_significance="1",
            message="Drug-drug interaction detected",
        )
        assert alert.reason_for_service == "DD"
        assert alert.clinical_significance == "1"
        assert alert.message == "Drug-drug interaction detected"

    def test_dur_alert_optional_fields(self):
        """DUR alert optional fields default to None."""
        alert = DURResponseAlert(
            reason_for_service="DA",
            clinical_significance="2",
        )
        assert alert.other_pharmacy_indicator is None
        assert alert.previous_fill_date is None


# ============================================================================
# Test ClaimResponse Model
# ============================================================================

class TestClaimResponse:
    """Tests for ClaimResponse model."""

    def test_create_approved_response(self):
        """Create an approved claim response."""
        response = ClaimResponse(
            claim_id="CLM001",
            transaction_response_status="A",
            response_status="P",
            authorization_number="AUTH123456789",
            ingredient_cost_paid=Decimal("100.00"),
            dispensing_fee_paid=Decimal("5.00"),
            total_amount_paid=Decimal("75.00"),
            patient_pay_amount=Decimal("30.00"),
            copay_amount=Decimal("30.00"),
        )
        assert response.response_status == "P"
        assert response.authorization_number == "AUTH123456789"
        assert response.total_amount_paid == Decimal("75.00")

    def test_create_rejected_response(self):
        """Create a rejected claim response."""
        response = ClaimResponse(
            claim_id="CLM001",
            transaction_response_status="R",
            response_status="R",
            reject_codes=[
                RejectCode(code="70", description="Product/Service Not Covered"),
            ],
        )
        assert response.response_status == "R"
        assert len(response.reject_codes) == 1
        assert response.reject_codes[0].code == "70"

    def test_response_with_dur_alerts(self):
        """Response can include DUR alerts."""
        response = ClaimResponse(
            claim_id="CLM001",
            transaction_response_status="A",
            response_status="P",
            dur_alerts=[
                DURResponseAlert(
                    reason_for_service="DD",
                    clinical_significance="1",
                    message="Drug interaction warning",
                ),
            ],
        )
        assert len(response.dur_alerts) == 1


# ============================================================================
# Test EligibilityResult
# ============================================================================

class TestEligibilityResult:
    """Tests for EligibilityResult dataclass."""

    def test_eligible_result(self):
        """Create eligible result."""
        result = EligibilityResult(eligible=True, reject_codes=[])
        assert result.eligible is True
        assert len(result.reject_codes) == 0

    def test_ineligible_result(self):
        """Create ineligible result with reject codes."""
        result = EligibilityResult(
            eligible=False,
            reject_codes=[RejectCode(code="65", description="Patient Not Covered")],
        )
        assert result.eligible is False
        assert len(result.reject_codes) == 1


# ============================================================================
# Test PricingResult
# ============================================================================

class TestPricingResult:
    """Tests for PricingResult dataclass."""

    def test_create_pricing_result(self):
        """Create pricing result."""
        result = PricingResult(
            ingredient_cost=Decimal("100.00"),
            dispensing_fee=Decimal("5.00"),
            plan_pays=Decimal("75.00"),
            patient_pays=Decimal("30.00"),
            copay=Decimal("30.00"),
            deductible_applied=Decimal("0.00"),
        )
        assert result.ingredient_cost == Decimal("100.00")
        assert result.plan_pays == Decimal("75.00")
        assert result.patient_pays == Decimal("30.00")


# ============================================================================
# Test AdjudicationEngine
# ============================================================================

class TestAdjudicationEngine:
    """Tests for AdjudicationEngine."""

    def test_create_engine_with_default_formulary(self):
        """Engine creates with default formulary."""
        engine = AdjudicationEngine()
        assert engine.formulary is not None
        assert engine.formulary.formulary_id == "DEFAULT"

    def test_adjudicate_approved_claim(self, sample_claim, sample_member, test_formulary):
        """Adjudicate an approved claim."""
        engine = AdjudicationEngine(formulary=test_formulary)
        response = engine.adjudicate(sample_claim, sample_member)
        
        # Should be approved
        assert response.transaction_response_status == "A"
        assert response.response_status == "P"
        assert response.authorization_number is not None
        assert response.authorization_number.startswith("AUTH")

    def test_adjudicate_ineligible_terminated_member(self, sample_claim):
        """Reject claim for terminated member."""
        # Create terminated member
        member = RxMember(
            member_id="MEM001",
            cardholder_id="123456789",
            person_code="01",
            bin="610014",
            pcn="RXTEST",
            group_number="GRP001",
            demographics=MemberDemographics(
                first_name="John",
                last_name="Smith",
                date_of_birth=date(1980, 5, 15),
                gender="M",
                address_line1="123 Main St",
                city="San Diego",
                state="CA",
                zip_code="92101",
            ),
            effective_date=date(2025, 1, 1),
            termination_date=date(2025, 1, 10),  # Terminated before service date
            accumulators=BenefitAccumulators(
                deductible_total=Decimal("500.00"),
                deductible_remaining=Decimal("500.00"),
                oop_total=Decimal("3000.00"),
                oop_remaining=Decimal("3000.00"),
            ),
        )
        
        engine = AdjudicationEngine()
        response = engine.adjudicate(sample_claim, member)
        
        assert response.response_status == "R"
        assert any(r.code == "65" for r in response.reject_codes)

    def test_adjudicate_bin_mismatch(self, sample_claim, sample_member):
        """Reject claim with mismatched BIN."""
        # Modify claim to have wrong BIN
        wrong_bin_claim = sample_claim.model_copy(update={"bin": "999999"})
        
        engine = AdjudicationEngine()
        response = engine.adjudicate(wrong_bin_claim, sample_member)
        
        assert response.response_status == "R"
        assert any(r.code == "25" for r in response.reject_codes)

    def test_adjudicate_pcn_mismatch(self, sample_claim, sample_member):
        """Reject claim with mismatched PCN."""
        wrong_pcn_claim = sample_claim.model_copy(update={"pcn": "WRONGPCN"})
        
        engine = AdjudicationEngine()
        response = engine.adjudicate(wrong_pcn_claim, sample_member)
        
        assert response.response_status == "R"
        assert any(r.code == "26" for r in response.reject_codes)

    def test_adjudicate_group_mismatch(self, sample_claim, sample_member):
        """Reject claim with mismatched group number."""
        wrong_group_claim = sample_claim.model_copy(update={"group_number": "WRONGGRP"})
        
        engine = AdjudicationEngine()
        response = engine.adjudicate(wrong_group_claim, sample_member)
        
        assert response.response_status == "R"
        assert any(r.code == "64" for r in response.reject_codes)

    def test_adjudicate_service_before_effective(self, sample_claim):
        """Reject claim with service date before effective date."""
        # Member effective Jan 20, but service date is Jan 15
        member = RxMember(
            member_id="MEM001",
            cardholder_id="123456789",
            person_code="01",
            bin="610014",
            pcn="RXTEST",
            group_number="GRP001",
            demographics=MemberDemographics(
                first_name="John",
                last_name="Smith",
                date_of_birth=date(1980, 5, 15),
                gender="M",
                address_line1="123 Main St",
                city="San Diego",
                state="CA",
                zip_code="92101",
            ),
            effective_date=date(2025, 1, 20),  # After service date
            accumulators=BenefitAccumulators(
                deductible_total=Decimal("500.00"),
                deductible_remaining=Decimal("500.00"),
                oop_total=Decimal("3000.00"),
                oop_remaining=Decimal("3000.00"),
            ),
        )
        
        engine = AdjudicationEngine()
        response = engine.adjudicate(sample_claim, member)
        
        assert response.response_status == "R"
        assert any(r.code == "65" for r in response.reject_codes)

    def test_adjudicate_pricing_with_copay(self, sample_claim, sample_member, test_formulary):
        """Pricing includes copay amount."""
        engine = AdjudicationEngine(formulary=test_formulary)
        response = engine.adjudicate(sample_claim, sample_member)
        
        # Approved claim should have copay
        assert response.response_status == "P"
        assert response.copay_amount is not None
        assert response.copay_amount >= Decimal("0")

    def test_adjudicate_deductible_applied(self, sample_claim, sample_member, test_formulary):
        """Deductible is applied when remaining."""
        engine = AdjudicationEngine(formulary=test_formulary)
        response = engine.adjudicate(sample_claim, sample_member)
        
        # Should show deductible info
        assert response.deductible_amount is not None
        assert response.remaining_deductible is not None

    def test_adjudicate_updates_accumulators_display(self, sample_claim, sample_member, test_formulary):
        """Response shows remaining accumulators."""
        engine = AdjudicationEngine(formulary=test_formulary)
        response = engine.adjudicate(sample_claim, sample_member)
        
        # Remaining amounts should be in response
        assert response.remaining_oop is not None


# ============================================================================
# Test Integration Scenarios
# ============================================================================

class TestIntegration:
    """Integration tests for claims processing."""

    def test_full_claim_lifecycle(self, sample_claim, sample_member):
        """Test complete claim submission and response."""
        engine = AdjudicationEngine()
        
        # Submit billing claim
        response = engine.adjudicate(sample_claim, sample_member)
        
        # Verify response completeness
        assert response.claim_id == sample_claim.claim_id
        if response.response_status == "P":
            assert response.authorization_number is not None
            assert response.total_amount_paid is not None
            assert response.patient_pay_amount is not None

    def test_multiple_reject_codes(self, sample_claim):
        """Claim can have multiple reject reasons."""
        # Member with wrong BIN, PCN, and group
        member = RxMember(
            member_id="MEM001",
            cardholder_id="123456789",
            person_code="01",
            bin="WRONGBIN",
            pcn="WRONGPCN",
            group_number="WRONGGRP",
            demographics=MemberDemographics(
                first_name="John",
                last_name="Smith",
                date_of_birth=date(1980, 5, 15),
                gender="M",
                address_line1="123 Main St",
                city="San Diego",
                state="CA",
                zip_code="92101",
            ),
            effective_date=date(2025, 1, 1),
            accumulators=BenefitAccumulators(
                deductible_total=Decimal("500.00"),
                deductible_remaining=Decimal("500.00"),
                oop_total=Decimal("3000.00"),
                oop_remaining=Decimal("3000.00"),
            ),
        )
        
        engine = AdjudicationEngine()
        response = engine.adjudicate(sample_claim, member)
        
        # Should have multiple reject codes
        assert response.response_status == "R"
        assert len(response.reject_codes) >= 3
