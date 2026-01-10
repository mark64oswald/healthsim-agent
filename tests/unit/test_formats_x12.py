"""Tests for MemberSim X12 format support."""

import pytest
from datetime import date
from decimal import Decimal

from healthsim_agent.products.membersim.formats.x12 import (
    EDI270Generator,
    EDI271Generator,
    EDI278RequestGenerator,
    EDI278ResponseGenerator,
    EDI834Generator,
    EDI835Generator,
    EDI837PGenerator,
    EDI837IGenerator,
    LinePayment,
    Payment,
    X12Config,
    generate_270,
    generate_271,
    generate_835,
)
from healthsim_agent.products.membersim.core.models import (
    Member,
    Plan,
    Accumulator,
)


class TestX12Config:
    """Tests for X12 configuration."""

    def test_default_config(self):
        """Test default X12 configuration."""
        config = X12Config()
        
        assert config.sender_id == "MEMBERSIM"
        assert config.receiver_id == "RECEIVER"
        assert config.sender_qualifier == "ZZ"

    def test_custom_config(self):
        """Test custom X12 configuration."""
        config = X12Config(
            sender_id="SENDER123",
            receiver_id="RECEIVER456",
        )
        
        assert config.sender_id == "SENDER123"
        assert config.receiver_id == "RECEIVER456"


class TestEDI270Generator:
    """Tests for X12 270 Eligibility Inquiry generation."""

    @pytest.fixture
    def generator(self):
        return EDI270Generator(X12Config())

    @pytest.fixture
    def sample_member(self):
        return Member(
            member_id="MEM123456",
            subscriber_id="SUB123456",
            given_name="John",
            family_name="Doe",
            birth_date=date(1980, 5, 15),
            gender="M",
            street_address="123 Main St",
            city="Austin",
            state="TX",
            postal_code="78701",
            plan_code="PPO-GOLD",
            coverage_start=date(2023, 1, 1),
        )

    def test_generate_270(self, generator, sample_member):
        """Test generating 270 inquiry."""
        edi = generator.generate(sample_member)
        
        # Check for required segments
        assert "ISA*" in edi
        assert "GS*" in edi
        assert "ST*270*" in edi
        assert "BHT*" in edi
        assert "NM1*" in edi
        assert "SE*" in edi
        assert "GE*" in edi
        assert "IEA*" in edi
        
        # Check for subscriber info
        assert "MEM123456" in edi
        assert "Doe" in edi

    def test_generate_270_convenience(self, sample_member):
        """Test convenience function for 270."""
        edi = generate_270(sample_member)
        
        assert "ST*270*" in edi
        assert "MEM123456" in edi


class TestEDI271Generator:
    """Tests for X12 271 Eligibility Response generation."""

    @pytest.fixture
    def generator(self):
        return EDI271Generator(X12Config())

    @pytest.fixture
    def sample_member(self):
        return Member(
            member_id="MEM123456",
            subscriber_id="SUB123456",
            given_name="John",
            family_name="Doe",
            birth_date=date(1980, 5, 15),
            gender="M",
            street_address="123 Main St",
            city="Austin",
            state="TX",
            postal_code="78701",
            plan_code="PPO-GOLD",
            coverage_start=date(2023, 1, 1),
        )

    @pytest.fixture
    def sample_plan(self):
        return Plan(
            plan_code="PPO_GOLD",
            plan_name="Gold PPO Plan",
            plan_type="PPO",
            deductible_individual=Decimal("500.00"),
            deductible_family=Decimal("1500.00"),
            oop_max_individual=Decimal("3000.00"),
            oop_max_family=Decimal("9000.00"),
            copay_pcp=Decimal("25.00"),
            copay_specialist=Decimal("50.00"),
            copay_er=Decimal("150.00"),
            coinsurance=Decimal("0.20"),
        )

    @pytest.fixture
    def sample_accumulator(self, sample_member, sample_plan):
        return Accumulator(
            member_id=sample_member.member_id,
            plan_year=2024,
            deductible_applied=Decimal("250.00"),
            deductible_limit=sample_plan.deductible_individual,
            oop_applied=Decimal("500.00"),
            oop_limit=sample_plan.oop_max_individual,
        )

    def test_generate_271(self, generator, sample_member, sample_plan):
        """Test generating 271 response."""
        edi = generator.generate(sample_member, sample_plan)
        
        assert "ST*271*" in edi
        assert "MEM123456" in edi
        assert "EB*" in edi  # Eligibility benefit segments

    def test_generate_271_with_accumulator(
        self, generator, sample_member, sample_plan, sample_accumulator
    ):
        """Test generating 271 with accumulator data."""
        edi = generator.generate(sample_member, sample_plan, sample_accumulator)
        
        assert "ST*271*" in edi
        assert "EB*" in edi

    def test_generate_271_ineligible(
        self, generator, sample_member, sample_plan
    ):
        """Test generating 271 for ineligible member."""
        edi = generator.generate(sample_member, sample_plan, is_eligible=False)
        
        assert "ST*271*" in edi
        # Should have inactive status
        assert "EB*6" in edi


class TestEDI278Generators:
    """Tests for X12 278 Prior Authorization generators."""

    @pytest.fixture
    def request_generator(self):
        return EDI278RequestGenerator(X12Config())

    @pytest.fixture
    def response_generator(self):
        return EDI278ResponseGenerator(X12Config())

    def test_request_generator_exists(self, request_generator):
        """Test that 278 request generator exists."""
        assert request_generator is not None
        assert hasattr(request_generator, 'generate')

    def test_response_generator_exists(self, response_generator):
        """Test that 278 response generator exists."""
        assert response_generator is not None
        assert hasattr(response_generator, 'generate')


class TestEDI835Generator:
    """Tests for X12 835 Remittance generation."""

    @pytest.fixture
    def generator(self):
        return EDI835Generator(X12Config())

    @pytest.fixture
    def sample_payment(self):
        return Payment(
            payment_id="PMT001",
            claim_id="CLM123456",
            check_number="CHK789",
            payment_date=date(2024, 1, 25),
            total_charged=Decimal("500.00"),
            total_allowed=Decimal("400.00"),
            total_paid=Decimal("320.00"),
            total_patient_responsibility=Decimal("80.00"),
            line_payments=[
                LinePayment(
                    line_number=1,
                    charged_amount=Decimal("300.00"),
                    allowed_amount=Decimal("250.00"),
                    paid_amount=Decimal("200.00"),
                    deductible_amount=Decimal("25.00"),
                    coinsurance_amount=Decimal("25.00"),
                ),
                LinePayment(
                    line_number=2,
                    charged_amount=Decimal("200.00"),
                    allowed_amount=Decimal("150.00"),
                    paid_amount=Decimal("120.00"),
                    copay_amount=Decimal("30.00"),
                ),
            ],
        )

    def test_generate_835(self, generator, sample_payment):
        """Test generating 835 remittance."""
        edi = generator.generate([sample_payment])
        
        assert "ST*835*" in edi
        assert "BPR*" in edi  # Financial info
        assert "CLP*" in edi  # Claim payment
        assert "CLM123456" in edi

    def test_generate_835_convenience(self, sample_payment):
        """Test convenience function for 835."""
        edi = generate_835([sample_payment])
        
        assert "ST*835*" in edi
        assert "CLM123456" in edi

    def test_generate_835_with_adjustments(self, generator, sample_payment):
        """Test 835 includes adjustment segments."""
        edi = generator.generate([sample_payment])
        
        # Should have CAS segments for adjustments
        assert "CAS*" in edi
        # Should have SVC segments for service lines
        assert "SVC*" in edi

    def test_generate_835_multiple_payments(self, generator):
        """Test 835 with multiple payments."""
        payments = [
            Payment(
                payment_id=f"PMT00{i}",
                claim_id=f"CLM00{i}",
                payment_date=date(2024, 1, 25),
                total_charged=Decimal("100.00"),
                total_allowed=Decimal("80.00"),
                total_paid=Decimal("80.00"),
            )
            for i in range(3)
        ]
        
        edi = generator.generate(payments)
        
        assert "CLM000" in edi
        assert "CLM001" in edi
        assert "CLM002" in edi


class TestEDI837Generators:
    """Tests for X12 837 Claim generators."""

    @pytest.fixture
    def professional_generator(self):
        return EDI837PGenerator(X12Config())

    @pytest.fixture
    def institutional_generator(self):
        return EDI837IGenerator(X12Config())

    def test_professional_generator_exists(self, professional_generator):
        """Test that 837P generator exists."""
        assert professional_generator is not None
        assert hasattr(professional_generator, 'generate')

    def test_institutional_generator_exists(self, institutional_generator):
        """Test that 837I generator exists."""
        assert institutional_generator is not None
        assert hasattr(institutional_generator, 'generate')


class TestEDI834Generator:
    """Tests for X12 834 Enrollment generation."""

    @pytest.fixture
    def generator(self):
        return EDI834Generator(X12Config())

    def test_generator_exists(self, generator):
        """Test that 834 generator exists."""
        assert generator is not None
        assert hasattr(generator, 'generate')
