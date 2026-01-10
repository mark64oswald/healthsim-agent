"""Tests for RxMemberSim NCPDP format support."""

import pytest
from datetime import date, datetime
from decimal import Decimal

from healthsim_agent.products.rxmembersim.formats.ncpdp import (
    NCPDPTelecomGenerator,
    NCPDPScriptGenerator,
    ePAGenerator,
    ePAMessageType,
    SCRIPTMessageType,
    NewRxMessage,
    RxChangeMessage,
    RxChangeType,
    RxRenewalMessage,
    PAInitiationRequest,
    PAInitiationResponse,
    PAResponse,
    QuestionType,
    ePAQuestion,
    ePAQuestionSet,
    ePAAnswer,
    NCPDP_REJECT_CODES,
    get_reject_description,
    get_reject_category,
    is_hard_reject,
    is_dur_reject,
)


class TestRejectCodes:
    """Tests for NCPDP reject code handling."""

    def test_reject_codes_defined(self):
        """Test that reject codes dictionary exists and has entries."""
        assert len(NCPDP_REJECT_CODES) > 0

    def test_get_reject_description(self):
        """Test getting reject code descriptions."""
        desc = get_reject_description("75")  # Prior Auth Required
        assert desc is not None
        assert "auth" in desc.lower() or "prior" in desc.lower()

    def test_get_reject_description_unknown(self):
        """Test getting unknown reject code."""
        desc = get_reject_description("XXXXX")
        assert desc is None or "unknown" in desc.lower()

    def test_get_reject_category(self):
        """Test getting reject code categories."""
        cat = get_reject_category("75")  # Prior Auth Required
        assert cat is not None

    def test_is_hard_reject(self):
        """Test identifying hard rejects."""
        assert isinstance(is_hard_reject("1"), bool)

    def test_is_dur_reject(self):
        """Test identifying DUR rejects."""
        assert isinstance(is_dur_reject("88"), bool)


class TestNCPDPTelecomGenerator:
    """Tests for NCPDP Telecom generator."""

    @pytest.fixture
    def generator(self):
        return NCPDPTelecomGenerator()

    def test_generator_exists(self, generator):
        """Test that telecom generator exists."""
        assert generator is not None


class TestNCPDPScriptGenerator:
    """Tests for NCPDP SCRIPT generator."""

    @pytest.fixture
    def generator(self):
        return NCPDPScriptGenerator()

    @pytest.fixture
    def sample_new_rx(self):
        return NewRxMessage(
            message_id="MSG001",
            prescriber_last_name="Smith",
            prescriber_first_name="John",
            prescriber_npi="1234567890",
            prescriber_dea="AS1234567",
            prescriber_address="100 Medical Plaza",
            prescriber_city="Austin",
            prescriber_state="TX",
            prescriber_zip="78701",
            prescriber_phone="512-555-1234",
            patient_last_name="Doe",
            patient_first_name="Jane",
            patient_dob=date(1975, 3, 20),
            patient_gender="F",
            patient_address="456 Oak St",
            patient_city="Austin",
            patient_state="TX",
            patient_zip="78702",
            drug_description="Lisinopril 10 MG Oral Tablet",
            ndc="00378180001",
            quantity="30",
            quantity_unit="EA",
            days_supply=30,
            directions="Take one tablet by mouth daily",
            refills=5,
            substitutions_allowed=True,
            pharmacy_ncpdp="1234567",
            pharmacy_npi="9876543210",
            pharmacy_name="Main Street Pharmacy",
        )

    @pytest.fixture
    def sample_rx_change(self):
        return RxChangeMessage(
            message_id="MSG002",
            relates_to_message_id="MSG001",
            change_type=RxChangeType.GENERIC_SUBSTITUTION,
            change_reason="Generic available at lower cost",
            original_drug_description="Lisinopril 10 MG Oral Tablet",
            original_ndc="00378180001",
            proposed_drug_description="Lisinopril 10 MG (Generic)",
            proposed_ndc="00591012901",
            pharmacy_ncpdp="1234567",
            pharmacy_npi="9876543210",
        )

    @pytest.fixture
    def sample_rx_renewal(self):
        return RxRenewalMessage(
            message_id="MSG003",
            patient_last_name="Doe",
            patient_first_name="Jane",
            patient_dob=date(1975, 3, 20),
            prescription_number="RX12345",
            drug_description="Lisinopril 10 MG Oral Tablet",
            ndc="00378180001",
            quantity="30",
            days_supply=30,
            last_fill_date=date(2024, 1, 1),
            pharmacy_ncpdp="1234567",
            pharmacy_npi="9876543210",
            pharmacy_name="Main Street Pharmacy",
            prescriber_npi="1234567890",
        )

    def test_generate_new_rx(self, generator, sample_new_rx):
        """Test generating NewRx message."""
        xml = generator.generate_new_rx(sample_new_rx)
        
        assert "<?xml" in xml
        assert "NewRx" in xml or "Message" in xml
        assert "Lisinopril" in xml
        assert "1234567890" in xml  # Prescriber NPI

    def test_generate_rx_change(self, generator, sample_rx_change):
        """Test generating RxChange message."""
        xml = generator.generate_rx_change(sample_rx_change)
        
        assert "<?xml" in xml
        assert "Change" in xml or "Message" in xml
        assert "Generic" in xml

    def test_generate_rx_renewal(self, generator, sample_rx_renewal):
        """Test generating RxRenewal message."""
        xml = generator.generate_rx_renewal(sample_rx_renewal)
        
        assert "<?xml" in xml
        assert "Renewal" in xml or "Message" in xml
        assert "RX12345" in xml

    def test_generate_cancel_rx(self, generator, sample_new_rx):
        """Test generating CancelRx message."""
        xml = generator.generate_cancel_rx(
            message_id="CANCEL001",
            relates_to=sample_new_rx.message_id,
            prescriber_npi=sample_new_rx.prescriber_npi,
            patient_first=sample_new_rx.patient_first_name,
            patient_last=sample_new_rx.patient_last_name,
            patient_dob=sample_new_rx.patient_dob,
            drug_description=sample_new_rx.drug_description,
            cancel_reason="Patient request",
        )
        
        assert "<?xml" in xml
        assert "Cancel" in xml or "Message" in xml


class TestSCRIPTMessageType:
    """Tests for SCRIPT message type enum."""

    def test_message_types_defined(self):
        """Test that all message types are defined."""
        assert SCRIPTMessageType.NEW_RX is not None
        assert SCRIPTMessageType.RX_CHANGE is not None
        assert SCRIPTMessageType.RX_RENEWAL is not None
        assert SCRIPTMessageType.CANCEL_RX is not None


class TestRxChangeType:
    """Tests for RxChange type enum."""

    def test_change_types_defined(self):
        """Test that change types are defined."""
        assert RxChangeType.GENERIC_SUBSTITUTION is not None
        assert RxChangeType.THERAPEUTIC_SUBSTITUTION is not None
        assert RxChangeType.PRIOR_AUTHORIZATION is not None
        assert RxChangeType.FORMULARY is not None


class TestePAGenerator:
    """Tests for ePA generator."""

    @pytest.fixture
    def generator(self):
        return ePAGenerator()

    def test_generate_initiation_request(self, generator):
        """Test generating PA initiation request."""
        request = generator.generate_initiation_request(
            member_id="MEM123456",
            patient_first="Jane",
            patient_last="Doe",
            patient_dob="1975-03-20",
            patient_gender="F",
            prescriber_npi="1234567890",
            prescriber_name="Dr. John Smith",
            drug_description="Humira 40 MG/0.4 ML Pen Injector",
            ndc="00074055402",
            quantity="2",
            days_supply=28,
            diagnosis_codes=["M06.9"],
            urgency="routine",
        )
        
        assert request is not None
        assert isinstance(request, PAInitiationRequest)
        assert request.member_id == "MEM123456"
        assert request.drug_description == "Humira 40 MG/0.4 ML Pen Injector"

    def test_generate_approval_response(self, generator):
        """Test generating approval response."""
        response = generator.generate_approval_response(
            request_message_id="EPA001",
            pa_number="PA123456",
            quantity_approved="24",
            refills_approved=11,
        )
        
        assert response is not None
        assert isinstance(response, PAResponse)
        assert response.determination == "Approved"
        assert response.pa_number == "PA123456"

    def test_generate_denial_response(self, generator):
        """Test generating denial response."""
        response = generator.generate_denial_response(
            request_message_id="EPA002",
            denial_reason="Step therapy required",
            alternatives=["adalimumab biosimilar"],
        )
        
        assert response is not None
        assert isinstance(response, PAResponse)
        assert response.determination == "Denied"
        assert response.denial_reason == "Step therapy required"

    def test_generate_question_response(self, generator):
        """Test generating response with questions."""
        questions = ePAQuestionSet(
            question_set_id="QS001",
            drug_name="Humira",
            description="Prior Authorization Questions",
            questions=[
                ePAQuestion(
                    question_id="Q1",
                    question_text="Has patient tried methotrexate?",
                    question_type=QuestionType.BOOLEAN,
                    required=True,
                ),
                ePAQuestion(
                    question_id="Q2",
                    question_text="Duration of disease (years)?",
                    question_type=QuestionType.NUMERIC,
                    required=True,
                    min_value=0,
                    max_value=50,
                ),
            ],
        )
        
        response = generator.generate_question_response(
            request_message_id="EPA003",
            questions=questions,
        )
        
        assert response is not None
        assert isinstance(response, PAInitiationResponse)
        assert response.response_type == "Question"
        assert response.question_set is not None

    def test_to_xml(self, generator):
        """Test converting ePA message to XML."""
        request = generator.generate_initiation_request(
            member_id="MEM123456",
            patient_first="Jane",
            patient_last="Doe",
            patient_dob="1975-03-20",
            patient_gender="F",
            prescriber_npi="1234567890",
            prescriber_name="Dr. John Smith",
            drug_description="Humira",
            ndc="00074055402",
            quantity="2",
            days_supply=28,
        )
        
        xml = generator.to_xml(request)
        
        assert "<?xml" in xml or "<Message" in xml
        assert "Humira" in xml


class TestePAMessageType:
    """Tests for ePA message type enum."""

    def test_message_types_defined(self):
        """Test that all ePA message types are defined."""
        assert ePAMessageType.PA_INITIATION_REQUEST is not None
        assert ePAMessageType.PA_INITIATION_RESPONSE is not None
        assert ePAMessageType.PA_REQUEST is not None
        assert ePAMessageType.PA_RESPONSE is not None


class TestQuestionType:
    """Tests for ePA question type enum."""

    def test_question_types_defined(self):
        """Test that question types are defined."""
        assert QuestionType.BOOLEAN is not None
        assert QuestionType.TEXT is not None
        assert QuestionType.SINGLE_SELECT is not None
        assert QuestionType.MULTI_SELECT is not None
        assert QuestionType.NUMERIC is not None
        assert QuestionType.DATE is not None


class TestePAQuestion:
    """Tests for ePA question model."""

    def test_create_boolean_question(self):
        """Test creating boolean question."""
        q = ePAQuestion(
            question_id="Q1",
            question_text="Has patient tried methotrexate?",
            question_type=QuestionType.BOOLEAN,
            required=True,
        )
        
        assert q.question_type == QuestionType.BOOLEAN
        assert q.required is True

    def test_create_select_question(self):
        """Test creating select question with options."""
        q = ePAQuestion(
            question_id="Q2",
            question_text="Select diagnosis",
            question_type=QuestionType.SINGLE_SELECT,
            required=True,
            options=["Rheumatoid Arthritis", "Psoriatic Arthritis", "Crohn's Disease"],
        )
        
        assert len(q.options) == 3


class TestePAAnswer:
    """Tests for ePA answer model."""

    def test_create_boolean_answer(self):
        """Test creating boolean answer."""
        a = ePAAnswer(
            question_id="Q1",
            answer_type=QuestionType.BOOLEAN,
            boolean_answer=True,
        )
        
        assert a.boolean_answer is True

    def test_create_numeric_answer(self):
        """Test creating numeric answer."""
        a = ePAAnswer(
            question_id="Q2",
            answer_type=QuestionType.NUMERIC,
            numeric_answer=5.5,
        )
        
        assert a.numeric_answer == 5.5

    def test_create_text_answer(self):
        """Test creating text answer."""
        a = ePAAnswer(
            question_id="Q3",
            answer_type=QuestionType.TEXT,
            text_answer="Patient has been on MTX for 6 months with inadequate response",
        )
        
        assert "MTX" in a.text_answer
