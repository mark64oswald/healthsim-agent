"""Tests for RxMemberSim X12 835 Pharmacy Remittance format support."""

import pytest
from datetime import date
from decimal import Decimal

from healthsim_agent.products.rxmembersim.formats.x12 import (
    EDI835PharmacyGenerator,
    PharmacyRemittance,
    PharmacyLinePayment,
    ClaimStatus,
    AdjustmentGroup,
    generate_pharmacy_835,
)


class TestClaimStatus:
    """Tests for ClaimStatus enum."""

    def test_claim_status_values(self):
        """Test claim status enum values."""
        assert ClaimStatus.PROCESSED_PRIMARY.value == "1"
        assert ClaimStatus.PROCESSED_SECONDARY.value == "2"
        assert ClaimStatus.DENIED.value == "4"
        assert ClaimStatus.PENDED.value == "20"


class TestAdjustmentGroup:
    """Tests for AdjustmentGroup enum."""

    def test_adjustment_group_values(self):
        """Test adjustment group enum values."""
        assert AdjustmentGroup.CONTRACTUAL.value == "CO"
        assert AdjustmentGroup.PATIENT_RESP.value == "PR"
        assert AdjustmentGroup.PAYER_INITIATED.value == "PI"
        assert AdjustmentGroup.OTHER.value == "OA"


class TestPharmacyLinePayment:
    """Tests for PharmacyLinePayment model."""

    def test_create_line_payment(self):
        """Test creating a pharmacy line payment."""
        line = PharmacyLinePayment(
            prescription_number="RX12345",
            ndc="00378180001",
            drug_name="Lisinopril 10 MG Tablet",
            quantity_dispensed=Decimal("30"),
            days_supply=30,
            ingredient_cost_submitted=Decimal("25.00"),
            dispensing_fee_submitted=Decimal("5.00"),
            total_submitted=Decimal("30.00"),
            ingredient_cost_paid=Decimal("20.00"),
            dispensing_fee_paid=Decimal("3.50"),
            total_paid=Decimal("23.50"),
            copay_amount=Decimal("10.00"),
        )
        
        assert line.prescription_number == "RX12345"
        assert line.ndc == "00378180001"
        assert line.total_paid == Decimal("23.50")

    def test_line_payment_with_adjustments(self):
        """Test line payment with adjustments."""
        line = PharmacyLinePayment(
            prescription_number="RX12346",
            ndc="00591012901",
            drug_name="Metformin 500 MG Tablet",
            quantity_dispensed=Decimal("60"),
            days_supply=30,
            ingredient_cost_submitted=Decimal("15.00"),
            dispensing_fee_submitted=Decimal("5.00"),
            total_submitted=Decimal("20.00"),
            ingredient_cost_paid=Decimal("10.00"),
            dispensing_fee_paid=Decimal("2.50"),
            total_paid=Decimal("12.50"),
            contractual_adjustment=Decimal("5.00"),
            deductible_amount=Decimal("2.50"),
        )
        
        assert line.contractual_adjustment == Decimal("5.00")
        assert line.deductible_amount == Decimal("2.50")


class TestPharmacyRemittance:
    """Tests for PharmacyRemittance model."""

    @pytest.fixture
    def sample_line_payments(self):
        return [
            PharmacyLinePayment(
                prescription_number="RX12345",
                ndc="00378180001",
                drug_name="Lisinopril 10 MG Tablet",
                quantity_dispensed=Decimal("30"),
                days_supply=30,
                ingredient_cost_submitted=Decimal("25.00"),
                dispensing_fee_submitted=Decimal("5.00"),
                total_submitted=Decimal("30.00"),
                ingredient_cost_paid=Decimal("20.00"),
                dispensing_fee_paid=Decimal("3.50"),
                total_paid=Decimal("23.50"),
                copay_amount=Decimal("10.00"),
                fill_date=date(2024, 1, 15),
            ),
            PharmacyLinePayment(
                prescription_number="RX12346",
                ndc="00591012901",
                drug_name="Metformin 500 MG Tablet",
                quantity_dispensed=Decimal("60"),
                days_supply=30,
                ingredient_cost_submitted=Decimal("15.00"),
                dispensing_fee_submitted=Decimal("5.00"),
                total_submitted=Decimal("20.00"),
                ingredient_cost_paid=Decimal("10.00"),
                dispensing_fee_paid=Decimal("2.50"),
                total_paid=Decimal("12.50"),
                deductible_amount=Decimal("5.00"),
                fill_date=date(2024, 1, 15),
            ),
        ]

    def test_create_remittance(self, sample_line_payments):
        """Test creating a pharmacy remittance."""
        remit = PharmacyRemittance(
            remit_id="REM001",
            claim_id="CLM123456",
            pharmacy_npi="1234567890",
            pharmacy_ncpdp="1234567",
            pharmacy_name="Main Street Pharmacy",
            check_number="CHK789",
            payment_method="ACH",
            payment_date=date(2024, 1, 25),
            payer_name="Express Scripts",
            payer_id="ESI001",
            total_submitted=Decimal("50.00"),
            total_paid=Decimal("36.00"),
            total_patient_responsibility=Decimal("15.00"),
            line_payments=sample_line_payments,
        )
        
        assert remit.remit_id == "REM001"
        assert remit.pharmacy_npi == "1234567890"
        assert len(remit.line_payments) == 2
        assert remit.claim_status == ClaimStatus.PROCESSED_PRIMARY

    def test_remittance_denied(self):
        """Test creating a denied remittance."""
        remit = PharmacyRemittance(
            remit_id="REM002",
            claim_id="CLM789",
            pharmacy_npi="1234567890",
            pharmacy_ncpdp="1234567",
            pharmacy_name="Main Street Pharmacy",
            payment_date=date(2024, 1, 25),
            payer_name="Express Scripts",
            payer_id="ESI001",
            total_submitted=Decimal("100.00"),
            total_paid=Decimal("0.00"),
            claim_status=ClaimStatus.DENIED,
        )
        
        assert remit.claim_status == ClaimStatus.DENIED
        assert remit.total_paid == Decimal("0.00")


class TestEDI835PharmacyGenerator:
    """Tests for EDI 835 Pharmacy generator."""

    @pytest.fixture
    def generator(self):
        return EDI835PharmacyGenerator(
            sender_id="PAYER001",
            receiver_id="PHARMACY001",
        )

    @pytest.fixture
    def sample_remittance(self):
        return PharmacyRemittance(
            remit_id="REM001",
            claim_id="CLM123456",
            pharmacy_npi="1234567890",
            pharmacy_ncpdp="1234567",
            pharmacy_name="Main Street Pharmacy",
            check_number="CHK789",
            payment_date=date(2024, 1, 25),
            payer_name="Express Scripts",
            payer_id="ESI001",
            total_submitted=Decimal("50.00"),
            total_paid=Decimal("36.00"),
            total_patient_responsibility=Decimal("15.00"),
            line_payments=[
                PharmacyLinePayment(
                    prescription_number="RX12345",
                    ndc="00378180001",
                    drug_name="Lisinopril 10 MG Tablet",
                    quantity_dispensed=Decimal("30"),
                    days_supply=30,
                    ingredient_cost_submitted=Decimal("25.00"),
                    dispensing_fee_submitted=Decimal("5.00"),
                    total_submitted=Decimal("30.00"),
                    ingredient_cost_paid=Decimal("20.00"),
                    dispensing_fee_paid=Decimal("3.50"),
                    total_paid=Decimal("23.50"),
                    copay_amount=Decimal("10.00"),
                    contractual_adjustment=Decimal("5.00"),
                ),
            ],
        )

    def test_generate_835(self, generator, sample_remittance):
        """Test generating pharmacy 835."""
        edi = generator.generate([sample_remittance])
        
        # Check for required segments
        assert "ISA*" in edi
        assert "GS*HP*" in edi
        assert "ST*835*" in edi
        assert "BPR*" in edi
        assert "TRN*" in edi
        assert "SE*" in edi
        assert "GE*" in edi
        assert "IEA*" in edi

    def test_generate_835_claim_info(self, generator, sample_remittance):
        """Test 835 contains claim information."""
        edi = generator.generate([sample_remittance])
        
        assert "CLP*" in edi  # Claim payment
        assert "CLM123456" in edi
        assert "36" in edi  # Total paid amount

    def test_generate_835_service_lines(self, generator, sample_remittance):
        """Test 835 contains service line information."""
        edi = generator.generate([sample_remittance])
        
        assert "SVC*" in edi  # Service line
        assert "N4:" in edi  # NDC qualifier
        assert "00378180001" in edi  # NDC

    def test_generate_835_adjustments(self, generator, sample_remittance):
        """Test 835 contains adjustment segments."""
        edi = generator.generate([sample_remittance])
        
        # Should have CAS segments for adjustments
        assert "CAS*" in edi
        # Contractual adjustment
        assert "CAS*CO*" in edi
        # Patient responsibility (copay)
        assert "CAS*PR*" in edi

    def test_generate_835_amounts(self, generator, sample_remittance):
        """Test 835 contains amount segments."""
        edi = generator.generate([sample_remittance])
        
        # AMT segments for ingredient cost and dispensing fee
        assert "AMT*" in edi

    def test_generate_835_prescription_ref(self, generator, sample_remittance):
        """Test 835 contains prescription reference."""
        edi = generator.generate([sample_remittance])
        
        # REF segment with prescription number
        assert "REF*XZ*" in edi
        assert "RX12345" in edi

    def test_generate_835_multiple_remittances(self, generator):
        """Test generating 835 with multiple remittances."""
        remittances = [
            PharmacyRemittance(
                remit_id=f"REM00{i}",
                claim_id=f"CLM00{i}",
                pharmacy_npi="1234567890",
                pharmacy_ncpdp="1234567",
                pharmacy_name="Main Street Pharmacy",
                payment_date=date(2024, 1, 25),
                payer_name="Express Scripts",
                payer_id="ESI001",
                total_submitted=Decimal("50.00"),
                total_paid=Decimal("40.00"),
            )
            for i in range(3)
        ]
        
        edi = generator.generate(remittances)
        
        # Should have multiple CLP segments
        assert edi.count("CLP*") == 3
        assert "CLM000" in edi
        assert "CLM001" in edi
        assert "CLM002" in edi

    def test_generate_835_convenience(self, sample_remittance):
        """Test convenience function for pharmacy 835."""
        edi = generate_pharmacy_835([sample_remittance])
        
        assert "ST*835*" in edi
        assert "CLM123456" in edi


class TestPharmacy835Integration:
    """Integration tests for pharmacy 835 generation."""

    def test_complete_pharmacy_remittance_cycle(self):
        """Test complete remittance with multiple prescription types."""
        # Create remittance with various prescription scenarios
        remittance = PharmacyRemittance(
            remit_id="REM100",
            claim_id="CLM100",
            pharmacy_npi="1234567890",
            pharmacy_ncpdp="1234567",
            pharmacy_name="Community Pharmacy",
            payment_date=date(2024, 1, 30),
            payer_name="CVS Caremark",
            payer_id="CVSRX",
            total_submitted=Decimal("275.00"),
            total_paid=Decimal("200.00"),
            total_patient_responsibility=Decimal("50.00"),
            line_payments=[
                # Generic medication - full coverage
                PharmacyLinePayment(
                    prescription_number="RX001",
                    ndc="00378180001",
                    drug_name="Lisinopril 10 MG",
                    quantity_dispensed=Decimal("30"),
                    days_supply=30,
                    ingredient_cost_submitted=Decimal("15.00"),
                    dispensing_fee_submitted=Decimal("5.00"),
                    total_submitted=Decimal("20.00"),
                    ingredient_cost_paid=Decimal("12.00"),
                    dispensing_fee_paid=Decimal("3.00"),
                    total_paid=Decimal("15.00"),
                    copay_amount=Decimal("5.00"),
                ),
                # Brand medication - higher copay
                PharmacyLinePayment(
                    prescription_number="RX002",
                    ndc="00074055402",
                    drug_name="Humira 40 MG Pen",
                    quantity_dispensed=Decimal("2"),
                    days_supply=28,
                    ingredient_cost_submitted=Decimal("2500.00"),
                    dispensing_fee_submitted=Decimal("5.00"),
                    total_submitted=Decimal("2505.00"),
                    ingredient_cost_paid=Decimal("2000.00"),
                    dispensing_fee_paid=Decimal("0.00"),
                    total_paid=Decimal("2000.00"),
                    copay_amount=Decimal("100.00"),
                    coinsurance_amount=Decimal("400.00"),
                ),
                # OTC - denied
                PharmacyLinePayment(
                    prescription_number="RX003",
                    ndc="30045012902",
                    drug_name="Acetaminophen 500 MG",
                    quantity_dispensed=Decimal("100"),
                    days_supply=30,
                    ingredient_cost_submitted=Decimal("10.00"),
                    dispensing_fee_submitted=Decimal("5.00"),
                    total_submitted=Decimal("15.00"),
                    ingredient_cost_paid=Decimal("0.00"),
                    dispensing_fee_paid=Decimal("0.00"),
                    total_paid=Decimal("0.00"),
                    contractual_adjustment=Decimal("15.00"),
                ),
            ],
        )
        
        edi = generate_pharmacy_835([remittance])
        
        # Verify structure
        assert "ST*835*" in edi
        
        # Should have service lines for all prescriptions
        assert edi.count("SVC*") == 3
        
        # Should have prescription references
        assert "RX001" in edi
        assert "RX002" in edi
        assert "RX003" in edi
