"""Tests for PatientSim C-CDA format support."""

import pytest
from dataclasses import dataclass
from datetime import date, datetime
from typing import Any

from healthsim_agent.products.patientsim.formats.ccda import (
    CCDAConfig,
    CCDATransformer,
    CCDAValidator,
    CODE_SYSTEMS,
    CodedValue,
    CodeSystemRegistry,
    DocumentType,
    HeaderBuilder,
    NarrativeBuilder,
    SectionBuilder,
    ValidationResult,
    VITAL_SIGNS_LOINC,
    create_loinc_code,
    create_rxnorm_code,
    create_snomed_code,
    get_code_system,
    get_vital_loinc,
)


# Mock objects for testing (C-CDA builders expect objects with attributes)
@dataclass
class MockDiagnosis:
    code: str
    description: str
    is_active: bool = True
    diagnosed_date: date | None = None


@dataclass
class MockMedication:
    drug_name: str
    dose: str = ""
    unit: str = ""
    frequency: str = ""
    status: str = "active"
    rxnorm_code: str | None = None


@dataclass
class MockVitalSign:
    observation_time: datetime
    systolic_bp: int | None = None
    diastolic_bp: int | None = None
    heart_rate: int | None = None
    respiratory_rate: int | None = None
    temperature: float | None = None


@dataclass 
class MockLab:
    test_name: str
    loinc_code: str
    value: float
    unit: str
    collected_time: datetime


@dataclass
class MockPatient:
    mrn: str
    given_name: str
    family_name: str
    birth_date: date
    gender: str
    address: str | None = None
    city: str | None = None
    state: str | None = None
    postal_code: str | None = None


class TestCodedValue:
    """Tests for CodedValue dataclass."""

    def test_create_coded_value(self):
        """Test creating a coded value."""
        code = CodedValue(
            code="38341003",
            display_name="Hypertension",
            code_system="2.16.840.1.113883.6.96",
            code_system_name="SNOMED CT",
        )
        assert code.code == "38341003"
        assert code.display_name == "Hypertension"
        assert code.code_system == "2.16.840.1.113883.6.96"

    def test_to_xml(self):
        """Test XML generation from coded value."""
        code = CodedValue(
            code="38341003",
            display_name="Hypertension",
            code_system="2.16.840.1.113883.6.96",
            code_system_name="SNOMED CT",
        )
        xml = code.to_xml()
        assert "38341003" in xml
        assert "Hypertension" in xml

    def test_to_code_xml(self):
        """Test code XML element generation."""
        code = CodedValue(
            code="38341003",
            display_name="Hypertension",
            code_system="2.16.840.1.113883.6.96",
            code_system_name="SNOMED CT",
        )
        xml = code.to_code_xml()
        assert "<code" in xml
        assert "38341003" in xml


class TestCodeSystems:
    """Tests for code system constants and helpers."""

    def test_code_systems_defined(self):
        """Test that all expected code systems are defined."""
        expected = ["SNOMED", "RXNORM", "LOINC", "ICD10CM", "CPT", "CVX", "NDC"]
        for system in expected:
            assert system in CODE_SYSTEMS
            oid, name = CODE_SYSTEMS[system]
            assert oid.startswith("2.16.840")

    def test_get_code_system(self):
        """Test getting code system info."""
        oid, name = get_code_system("SNOMED")
        assert oid == "2.16.840.1.113883.6.96"
        assert "SNOMED" in name

    def test_get_code_system_unknown(self):
        """Test getting unknown code system raises KeyError."""
        with pytest.raises(KeyError):
            get_code_system("UNKNOWN")

    def test_create_loinc_code(self):
        """Test creating LOINC coded value."""
        code = create_loinc_code("8480-6", "Systolic BP")
        assert code.code == "8480-6"
        assert "LOINC" in code.code_system_name

    def test_create_snomed_code(self):
        """Test creating SNOMED coded value."""
        code = create_snomed_code("38341003", "Hypertension")
        assert code.code == "38341003"
        assert "SNOMED" in code.code_system_name

    def test_create_rxnorm_code(self):
        """Test creating RxNorm coded value."""
        code = create_rxnorm_code("310965", "Lisinopril 10 MG")
        assert code.code == "310965"
        assert "RxNorm" in code.code_system_name


class TestVitalSignsLOINC:
    """Tests for vital signs LOINC mappings."""

    def test_vital_signs_defined(self):
        """Test that common vital signs are defined."""
        expected = ["systolic_bp", "diastolic_bp", "heart_rate"]
        for vital in expected:
            assert vital in VITAL_SIGNS_LOINC
            code, display, unit = VITAL_SIGNS_LOINC[vital]
            assert code is not None

    def test_get_vital_loinc(self):
        """Test getting vital sign LOINC info."""
        result = get_vital_loinc("systolic_bp")
        assert result is not None
        code, display, unit = result
        assert code == "8480-6"

    def test_get_vital_loinc_unknown(self):
        """Test getting unknown vital returns None."""
        result = get_vital_loinc("unknown_vital")
        assert result is None


class TestCCDAConfig:
    """Tests for CCDAConfig dataclass."""

    def test_minimal_config(self):
        """Test minimal configuration with required fields."""
        config = CCDAConfig(
            document_type=DocumentType.CCD,
            organization_name="Test Hospital",
            organization_oid="2.16.840.1.113883.3.123",
        )
        assert config.document_type == DocumentType.CCD
        assert config.organization_name == "Test Hospital"

    def test_full_config(self):
        """Test full configuration."""
        config = CCDAConfig(
            document_type=DocumentType.DISCHARGE_SUMMARY,
            organization_name="Test Hospital",
            organization_oid="2.16.840.1.113883.3.123",
            author_name="Dr. Smith",
            author_npi="1234567890",
        )
        assert config.document_type == DocumentType.DISCHARGE_SUMMARY
        assert config.organization_name == "Test Hospital"
        assert config.author_npi == "1234567890"


class TestDocumentType:
    """Tests for DocumentType enum."""

    def test_document_types(self):
        """Test document type values."""
        assert DocumentType.CCD is not None
        assert DocumentType.DISCHARGE_SUMMARY is not None
        assert DocumentType.REFERRAL_NOTE is not None

    def test_document_type_properties(self):
        """Test document type properties."""
        ccd = DocumentType.CCD
        assert ccd.template_oid is not None
        assert ccd.loinc_code is not None
        assert ccd.display_name is not None


class TestCCDAValidator:
    """Tests for CCDAValidator."""

    @pytest.fixture
    def validator(self):
        return CCDAValidator()

    def test_validate_oid_valid(self, validator):
        """Test validating valid OIDs."""
        assert validator.validate_oid("2.16.840.1.113883.6.96") is True
        assert validator.validate_oid("1.2.3.4.5") is True

    def test_validate_oid_invalid(self, validator):
        """Test validating invalid OIDs."""
        assert validator.validate_oid("") is False
        assert validator.validate_oid("abc") is False
        assert validator.validate_oid(None) is False

    def test_validate_date_valid(self, validator):
        """Test validating valid CDA dates."""
        assert validator.validate_date("20240115") is True
        assert validator.validate_date("20240115143025") is True

    def test_validate_date_invalid(self, validator):
        """Test validating invalid CDA dates."""
        assert validator.validate_date("") is False
        assert validator.validate_date("2024-01-15") is False
        assert validator.validate_date("abc") is False

    def test_validate_document_minimal(self, validator):
        """Test validating minimal C-CDA document."""
        xml = '''<?xml version="1.0"?>
        <ClinicalDocument xmlns="urn:hl7-org:v3">
            <realmCode code="US"/>
            <typeId root="2.16.840.1.113883.1.3"/>
            <templateId root="2.16.840.1.113883.10.20.22.1.1"/>
            <component><structuredBody></structuredBody></component>
        </ClinicalDocument>'''
        
        result = validator.validate_document(xml)
        assert result.is_valid is True

    def test_validate_document_missing_root(self, validator):
        """Test validating document without ClinicalDocument."""
        xml = '<?xml version="1.0"?><Document></Document>'
        
        result = validator.validate_document(xml)
        assert result.is_valid is False
        assert len(result.errors) > 0


class TestNarrativeBuilder:
    """Tests for NarrativeBuilder."""

    @pytest.fixture
    def builder(self):
        return NarrativeBuilder()

    def test_build_problems_narrative(self, builder):
        """Test building problems narrative."""
        problems = [
            MockDiagnosis(code="I10", description="Hypertension", diagnosed_date=date(2020, 1, 15)),
            MockDiagnosis(code="E11.9", description="Diabetes Type 2", diagnosed_date=date(2019, 6, 1)),
        ]
        
        html = builder.build_problems_narrative(problems)
        
        assert "<table" in html.lower()
        assert "Hypertension" in html

    def test_build_problems_narrative_empty(self, builder):
        """Test building problems narrative with no problems."""
        html = builder.build_problems_narrative([])
        assert "No known problems" in html

    def test_build_medications_narrative(self, builder):
        """Test building medications narrative."""
        meds = [
            MockMedication(drug_name="Lisinopril", dose="10", unit="mg", frequency="daily"),
        ]
        
        html = builder.build_medications_narrative(meds)
        
        assert "Lisinopril" in html
        assert "table" in html.lower()

    def test_build_medications_narrative_empty(self, builder):
        """Test building medications narrative with no meds."""
        html = builder.build_medications_narrative([])
        assert "No known medications" in html

    def test_build_vital_signs_narrative(self, builder):
        """Test building vital signs narrative."""
        vitals = [
            MockVitalSign(
                observation_time=datetime.now(),
                systolic_bp=120,
                diastolic_bp=80,
                heart_rate=72,
            )
        ]
        
        html = builder.build_vital_signs_narrative(vitals)
        
        assert "120" in html or "table" in html.lower()


class TestSectionBuilder:
    """Tests for SectionBuilder."""

    @pytest.fixture
    def builder(self):
        return SectionBuilder()

    def test_build_problem_entry(self, builder):
        """Test building problem entry XML."""
        problem = MockDiagnosis(
            code="38341003",
            description="Hypertension",
            diagnosed_date=date(2020, 1, 15),
        )
        
        xml = builder.build_problem_entry(problem)
        
        assert "38341003" in xml or "entry" in xml.lower()

    def test_build_medication_entry(self, builder):
        """Test building medication entry XML."""
        med = MockMedication(
            drug_name="Lisinopril 10 MG",
            rxnorm_code="310965",
            dose="10",
            unit="mg",
        )
        
        xml = builder.build_medication_entry(med)
        
        assert "310965" in xml or "entry" in xml.lower()

    def test_build_vital_sign_entry(self, builder):
        """Test building vital signs entry XML."""
        vitals = MockVitalSign(
            observation_time=datetime.now(),
            systolic_bp=120,
            diastolic_bp=80,
            heart_rate=72,
        )
        
        xml = builder.build_vital_sign_entry(vitals)
        
        assert "120" in xml or "entry" in xml.lower()


class TestHeaderBuilder:
    """Tests for HeaderBuilder."""

    @pytest.fixture
    def config(self):
        return CCDAConfig(
            document_type=DocumentType.CCD,
            organization_name="Test Hospital",
            organization_oid="2.16.840.1.113883.3.123",
            author_name="Dr. Smith",
            author_npi="1234567890",
        )

    @pytest.fixture
    def builder(self, config):
        return HeaderBuilder(config)

    def test_build_header(self, builder):
        """Test building complete header."""
        patient = MockPatient(
            mrn="MRN001",
            given_name="John",
            family_name="Doe",
            birth_date=date(1960, 5, 15),
            gender="M",
            address="123 Main St",
            city="Austin",
            state="TX",
            postal_code="78701",
        )
        
        xml = builder.build_header(patient)
        
        assert "<recordTarget>" in xml
        assert "John" in xml
        assert "Doe" in xml


class TestCCDATransformer:
    """Tests for CCDATransformer."""

    @pytest.fixture
    def config(self):
        return CCDAConfig(
            document_type=DocumentType.CCD,
            organization_name="Test Hospital",
            organization_oid="2.16.840.1.113883.3.123",
            author_name="Dr. Smith",
            author_npi="1234567890",
        )

    @pytest.fixture
    def transformer(self, config):
        return CCDATransformer(config)

    @pytest.fixture
    def sample_patient(self):
        return MockPatient(
            mrn="MRN001",
            given_name="John",
            family_name="Doe",
            birth_date=date(1960, 5, 15),
            gender="M",
            address="123 Main St",
            city="Austin",
            state="TX",
            postal_code="78701",
        )

    @pytest.fixture
    def sample_diagnoses(self):
        return [
            MockDiagnosis(code="I10", description="Essential hypertension", diagnosed_date=date(2020, 1, 15)),
            MockDiagnosis(code="E11.9", description="Type 2 diabetes mellitus", diagnosed_date=date(2019, 6, 1)),
        ]

    @pytest.fixture
    def sample_medications(self):
        return [
            MockMedication(
                drug_name="Lisinopril 10 MG Oral Tablet",
                rxnorm_code="310965",
                dose="10",
                unit="mg",
                frequency="daily",
                status="active",
            ),
        ]

    def test_transform_basic(self, transformer, sample_patient):
        """Test basic transformation with patient only."""
        xml = transformer.transform(patient=sample_patient)
        
        assert '<?xml version="1.0"' in xml
        assert "<ClinicalDocument" in xml
        assert "John" in xml
        assert "Doe" in xml

    def test_transform_with_diagnoses(
        self, transformer, sample_patient, sample_diagnoses
    ):
        """Test transformation with diagnoses."""
        xml = transformer.transform(
            patient=sample_patient,
            diagnoses=sample_diagnoses,
        )
        
        assert "<ClinicalDocument" in xml
        assert "I10" in xml or "hypertension" in xml.lower()

    def test_transform_with_medications(
        self, transformer, sample_patient, sample_medications
    ):
        """Test transformation with medications."""
        xml = transformer.transform(
            patient=sample_patient,
            medications=sample_medications,
        )
        
        assert "<ClinicalDocument" in xml
        assert "310965" in xml or "Lisinopril" in xml

    def test_transform_complete(
        self, transformer, sample_patient, sample_diagnoses, sample_medications
    ):
        """Test complete transformation."""
        vitals = [
            MockVitalSign(
                observation_time=datetime.now(),
                systolic_bp=120,
                diastolic_bp=80,
                heart_rate=72,
                respiratory_rate=16,
                temperature=98.6,
            )
        ]
        
        labs = [
            MockLab(
                test_name="Hemoglobin A1c",
                loinc_code="4548-4",
                value=7.2,
                unit="%",
                collected_time=datetime.now(),
            )
        ]
        
        xml = transformer.transform(
            patient=sample_patient,
            diagnoses=sample_diagnoses,
            medications=sample_medications,
            vitals=vitals,
            labs=labs,
        )
        
        assert "<ClinicalDocument" in xml
        assert "structuredBody" in xml
