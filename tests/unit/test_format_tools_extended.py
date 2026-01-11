"""
Tests for format_tools module.

Tests cover:
- Helper functions (_parse_date, _parse_datetime, _parse_gender, _parse_encounter_class)
- Dict to model conversions (_dict_to_patient, _dict_to_encounter, _dict_to_diagnosis)
- Data resolution (_resolve_data)
"""

import pytest
from datetime import date, datetime
from unittest.mock import MagicMock, patch


class TestParseDate:
    """Tests for _parse_date helper function."""
    
    def test_date_passthrough(self):
        """Test date object passes through."""
        from healthsim_agent.tools.format_tools import _parse_date
        
        d = date(2025, 1, 15)
        assert _parse_date(d) == d
    
    def test_datetime_extracts_date(self):
        """Test datetime extracts date portion."""
        from healthsim_agent.tools.format_tools import _parse_date
        
        dt = datetime(2025, 1, 15, 10, 30, 0)
        assert _parse_date(dt) == date(2025, 1, 15)
    
    def test_iso_string(self):
        """Test ISO format string parsing."""
        from healthsim_agent.tools.format_tools import _parse_date
        
        assert _parse_date('2025-01-15') == date(2025, 1, 15)
    
    def test_iso_string_with_z(self):
        """Test ISO format with Z timezone."""
        from healthsim_agent.tools.format_tools import _parse_date
        
        assert _parse_date('2025-01-15T10:30:00Z') == date(2025, 1, 15)
    
    def test_none_returns_none(self):
        """Test None returns None."""
        from healthsim_agent.tools.format_tools import _parse_date
        
        assert _parse_date(None) is None
    
    def test_invalid_returns_none(self):
        """Test invalid string returns None."""
        from healthsim_agent.tools.format_tools import _parse_date
        
        assert _parse_date('not-a-date') is None


class TestParseDatetime:
    """Tests for _parse_datetime helper function."""
    
    def test_datetime_passthrough(self):
        """Test datetime object passes through."""
        from healthsim_agent.tools.format_tools import _parse_datetime
        
        dt = datetime(2025, 1, 15, 10, 30, 0)
        assert _parse_datetime(dt) == dt
    
    def test_date_converts_to_datetime(self):
        """Test date converts to datetime at midnight."""
        from healthsim_agent.tools.format_tools import _parse_datetime
        
        d = date(2025, 1, 15)
        result = _parse_datetime(d)
        
        assert result == datetime(2025, 1, 15, 0, 0, 0)
    
    def test_iso_string(self):
        """Test ISO format string parsing."""
        from healthsim_agent.tools.format_tools import _parse_datetime
        
        result = _parse_datetime('2025-01-15T10:30:00')
        assert result == datetime(2025, 1, 15, 10, 30, 0)
    
    def test_none_returns_none(self):
        """Test None returns None."""
        from healthsim_agent.tools.format_tools import _parse_datetime
        
        assert _parse_datetime(None) is None
    
    def test_invalid_returns_none(self):
        """Test invalid string returns None."""
        from healthsim_agent.tools.format_tools import _parse_datetime
        
        assert _parse_datetime('invalid') is None


class TestParseGender:
    """Tests for _parse_gender helper function."""
    
    def test_gender_enum_passthrough(self):
        """Test Gender enum passes through."""
        from healthsim_agent.tools.format_tools import _parse_gender
        from healthsim_agent.person import Gender
        
        assert _parse_gender(Gender.MALE) == Gender.MALE
        assert _parse_gender(Gender.FEMALE) == Gender.FEMALE
    
    def test_male_string_variants(self):
        """Test male string variants."""
        from healthsim_agent.tools.format_tools import _parse_gender
        from healthsim_agent.person import Gender
        
        assert _parse_gender('M') == Gender.MALE
        assert _parse_gender('m') == Gender.MALE
        assert _parse_gender('MALE') == Gender.MALE
        assert _parse_gender('male') == Gender.MALE
    
    def test_female_string_variants(self):
        """Test female string variants."""
        from healthsim_agent.tools.format_tools import _parse_gender
        from healthsim_agent.person import Gender
        
        assert _parse_gender('F') == Gender.FEMALE
        assert _parse_gender('f') == Gender.FEMALE
        assert _parse_gender('FEMALE') == Gender.FEMALE
    
    def test_other_string_variants(self):
        """Test other gender string variants."""
        from healthsim_agent.tools.format_tools import _parse_gender
        from healthsim_agent.person import Gender
        
        assert _parse_gender('O') == Gender.OTHER
        assert _parse_gender('OTHER') == Gender.OTHER
    
    def test_unknown_default(self):
        """Test unknown defaults to UNKNOWN."""
        from healthsim_agent.tools.format_tools import _parse_gender
        from healthsim_agent.person import Gender
        
        assert _parse_gender('X') == Gender.UNKNOWN
        assert _parse_gender(None) == Gender.UNKNOWN
        assert _parse_gender(123) == Gender.UNKNOWN


class TestParseEncounterClass:
    """Tests for _parse_encounter_class helper function."""
    
    def test_enum_passthrough(self):
        """Test enum passes through."""
        from healthsim_agent.tools.format_tools import _parse_encounter_class
        from healthsim_agent.products.patientsim.core.models import EncounterClass
        
        assert _parse_encounter_class(EncounterClass.INPATIENT) == EncounterClass.INPATIENT
    
    def test_inpatient_variants(self):
        """Test inpatient string variants."""
        from healthsim_agent.tools.format_tools import _parse_encounter_class
        from healthsim_agent.products.patientsim.core.models import EncounterClass
        
        assert _parse_encounter_class('I') == EncounterClass.INPATIENT
        assert _parse_encounter_class('IMP') == EncounterClass.INPATIENT
        assert _parse_encounter_class('INPATIENT') == EncounterClass.INPATIENT
    
    def test_emergency_variants(self):
        """Test emergency string variants."""
        from healthsim_agent.tools.format_tools import _parse_encounter_class
        from healthsim_agent.products.patientsim.core.models import EncounterClass
        
        assert _parse_encounter_class('E') == EncounterClass.EMERGENCY
        assert _parse_encounter_class('EMER') == EncounterClass.EMERGENCY
        assert _parse_encounter_class('EMERGENCY') == EncounterClass.EMERGENCY
    
    def test_urgent_care_variants(self):
        """Test urgent care string variants."""
        from healthsim_agent.tools.format_tools import _parse_encounter_class
        from healthsim_agent.products.patientsim.core.models import EncounterClass
        
        assert _parse_encounter_class('U') == EncounterClass.URGENT_CARE
        assert _parse_encounter_class('URGENT') == EncounterClass.URGENT_CARE
    
    def test_default_to_outpatient(self):
        """Test unknown defaults to outpatient."""
        from healthsim_agent.tools.format_tools import _parse_encounter_class
        from healthsim_agent.products.patientsim.core.models import EncounterClass
        
        assert _parse_encounter_class('O') == EncounterClass.OUTPATIENT
        assert _parse_encounter_class('UNKNOWN') == EncounterClass.OUTPATIENT


class TestDictToPatient:
    """Tests for _dict_to_patient helper function."""
    
    def test_basic_patient(self):
        """Test converting basic patient dict."""
        from healthsim_agent.tools.format_tools import _dict_to_patient
        
        data = {
            'id': 'p-123',
            'given_name': 'John',
            'family_name': 'Doe',
            'birth_date': '1980-05-15',
            'gender': 'M',
            'mrn': 'MRN001',
        }
        
        patient = _dict_to_patient(data)
        
        assert patient.id == 'p-123'
        assert patient.name.given_name == 'John'
        assert patient.name.family_name == 'Doe'
        assert patient.birth_date == date(1980, 5, 15)
        assert patient.mrn == 'MRN001'
    
    def test_nested_name(self):
        """Test patient with nested name dict."""
        from healthsim_agent.tools.format_tools import _dict_to_patient
        
        data = {
            'id': 'p-456',
            'name': {
                'given': 'Jane',
                'family': 'Smith',
                'middle_name': 'Marie',
            },
            'birth_date': '1990-03-20',
            'gender': 'F',
        }
        
        patient = _dict_to_patient(data)
        
        assert patient.name.given_name == 'Jane'
        assert patient.name.family_name == 'Smith'
        assert patient.name.middle_name == 'Marie'
    
    def test_alternative_field_names(self):
        """Test alternative field names."""
        from healthsim_agent.tools.format_tools import _dict_to_patient
        
        data = {
            'patient_id': 'p-789',
            'first_name': 'Bob',
            'last_name': 'Jones',
            'dob': '1975-08-10',
            'sex': 'M',
        }
        
        patient = _dict_to_patient(data)
        
        assert patient.id == 'p-789'
        assert patient.name.given_name == 'Bob'
        assert patient.name.family_name == 'Jones'
    
    def test_with_address(self):
        """Test patient with address."""
        from healthsim_agent.tools.format_tools import _dict_to_patient
        
        data = {
            'id': 'p-111',
            'given_name': 'Test',
            'family_name': 'User',
            'birth_date': '2000-01-01',
            'address': {
                'street': '123 Main St',
                'city': 'Boston',
                'state': 'MA',
                'postal_code': '02101',
            },
        }
        
        patient = _dict_to_patient(data)
        
        assert patient.address is not None
        assert patient.address.city == 'Boston'
        assert patient.address.state == 'MA'


class TestDictToEncounter:
    """Tests for _dict_to_encounter helper function."""
    
    def test_basic_encounter(self):
        """Test converting basic encounter dict."""
        from healthsim_agent.tools.format_tools import _dict_to_encounter
        
        data = {
            'encounter_id': 'e-123',
            'patient_mrn': 'MRN001',
            'class_code': 'IMP',
            'status': 'finished',
            'admission_time': '2025-01-10T08:00:00',
            'discharge_time': '2025-01-15T14:00:00',
        }
        
        encounter = _dict_to_encounter(data)
        
        assert encounter.encounter_id == 'e-123'
        assert encounter.patient_mrn == 'MRN001'
        assert encounter.admission_time == datetime(2025, 1, 10, 8, 0, 0)
    
    def test_alternative_field_names(self):
        """Test alternative field names."""
        from healthsim_agent.tools.format_tools import _dict_to_encounter
        
        data = {
            'id': 'e-456',
            'patient_id': 'P001',
            'encounter_class': 'E',
            'start_time': '2025-01-20T09:30:00',
            'reason': 'Chest pain',
        }
        
        encounter = _dict_to_encounter(data)
        
        assert encounter.encounter_id == 'e-456'
        assert encounter.patient_mrn == 'P001'
        assert encounter.chief_complaint == 'Chest pain'


class TestDictToDiagnosis:
    """Tests for _dict_to_diagnosis helper function."""
    
    def test_basic_diagnosis(self):
        """Test converting basic diagnosis dict."""
        from healthsim_agent.tools.format_tools import _dict_to_diagnosis
        
        data = {
            'code': 'E11.9',
            'description': 'Type 2 diabetes mellitus without complications',
            'type': 'final',
            'patient_mrn': 'MRN001',
            'diagnosed_date': '2024-06-15',
        }
        
        diagnosis = _dict_to_diagnosis(data)
        
        assert diagnosis.code == 'E11.9'
        assert diagnosis.description == 'Type 2 diabetes mellitus without complications'
        assert diagnosis.diagnosed_date == date(2024, 6, 15)
    
    def test_alternative_field_names(self):
        """Test alternative field names."""
        from healthsim_agent.tools.format_tools import _dict_to_diagnosis
        
        data = {
            'icd_code': 'I10',
            'diagnosis_description': 'Essential hypertension',
            'diagnosis_type': 'final',
            'patient_id': 'P001',
            'onset_date': '2023-01-01',
        }
        
        diagnosis = _dict_to_diagnosis(data)
        
        assert diagnosis.code == 'I10'
        assert diagnosis.description == 'Essential hypertension'
        assert diagnosis.patient_mrn == 'P001'


class TestResolveData:
    """Tests for _resolve_data helper function."""
    
    def test_dict_passthrough(self):
        """Test dict data passes through."""
        from healthsim_agent.tools.format_tools import _resolve_data
        
        data = {'patients': [{'id': '1'}]}
        result = _resolve_data(data)
        
        assert result == data
    
    def test_invalid_type_returns_none(self):
        """Test invalid type returns None."""
        from healthsim_agent.tools.format_tools import _resolve_data
        
        assert _resolve_data(123) is None
        assert _resolve_data([]) is None


class TestTransformToFhir:
    """Tests for transform_to_fhir function."""
    
    def test_empty_data_error(self):
        """Test error when no data provided."""
        from healthsim_agent.tools.format_tools import transform_to_fhir
        
        result = transform_to_fhir({})
        
        assert result.success is False
        assert 'No patient data' in result.error
    
    def test_with_patient_data(self):
        """Test with patient data."""
        from healthsim_agent.tools.format_tools import transform_to_fhir
        
        data = {
            'patients': [{
                'id': 'p-123',
                'given_name': 'John',
                'family_name': 'Doe',
                'birth_date': '1980-05-15',
                'gender': 'M',
            }],
            'encounters': [{
                'encounter_id': 'e-123',
                'patient_mrn': 'p-123',
                'class_code': 'O',
                'admission_time': '2025-01-10T08:00:00',
            }],
        }
        
        result = transform_to_fhir(data)
        
        assert result.success is True
        assert result.data is not None
        assert 'resourceType' in result.data
        assert result.data['resourceType'] == 'Bundle'


class TestTransformToCcda:
    """Tests for transform_to_ccda function."""
    
    def test_empty_data_error(self):
        """Test error when no data provided."""
        from healthsim_agent.tools.format_tools import transform_to_ccda
        
        result = transform_to_ccda({})
        
        assert result.success is False
        assert 'No patient data' in result.error
    
    def test_with_patient_data(self):
        """Test with patient data."""
        from healthsim_agent.tools.format_tools import transform_to_ccda
        
        data = {
            'patients': [{
                'id': 'p-123',
                'given_name': 'John',
                'family_name': 'Doe',
                'birth_date': '1980-05-15',
                'gender': 'M',
                'mrn': 'MRN001',
            }],
        }
        
        result = transform_to_ccda(data)
        
        assert result.success is True
        assert result.data is not None
        assert 'xml' in result.data
        assert '<?xml' in result.data['xml']
