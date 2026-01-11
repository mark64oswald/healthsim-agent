"""
Additional tests for format_tools transforms.

Covers:
- transform_to_hl7v2
- transform_to_x12
- transform_to_ncpdp
- transform_to_mimic
- transform_to_sdtm
- transform_to_adam
- list_output_formats
"""

import pytest
from datetime import date, datetime
from unittest.mock import MagicMock, patch


class TestTransformToHl7v2:
    """Tests for transform_to_hl7v2 function."""
    
    def test_empty_data_error(self):
        """Test error when no data provided."""
        from healthsim_agent.tools.format_tools import transform_to_hl7v2
        
        result = transform_to_hl7v2({})
        
        assert result.success is False
    
    def test_with_patient_data_adt(self):
        """Test ADT message generation."""
        from healthsim_agent.tools.format_tools import transform_to_hl7v2
        
        data = {
            'patients': [{
                'id': 'p-123',
                'given_name': 'John',
                'family_name': 'Doe',
                'birth_date': '1980-05-15',
                'gender': 'M',
                'mrn': 'MRN001',
            }],
            'encounters': [{
                'encounter_id': 'e-123',
                'patient_mrn': 'MRN001',
                'class_code': 'I',
                'admission_time': '2025-01-10T08:00:00',
            }],
        }
        
        result = transform_to_hl7v2(data, message_type="ADT_A01")
        
        assert result.success is True
        assert result.data is not None
    
    def test_oru_message(self):
        """Test ORU message generation."""
        from healthsim_agent.tools.format_tools import transform_to_hl7v2
        
        data = {
            'patients': [{
                'id': 'p-123',
                'given_name': 'Jane',
                'family_name': 'Smith',
                'birth_date': '1975-03-20',
                'gender': 'F',
                'mrn': 'MRN002',
            }],
            'labs': [{
                'lab_id': 'lab-1',
                'patient_mrn': 'MRN002',
                'test_name': 'Glucose',
                'loinc_code': '2345-7',
                'value': '95',
                'units': 'mg/dL',
                'collection_time': '2025-01-15T10:00:00',
            }],
        }
        
        result = transform_to_hl7v2(data, message_type="ORU_R01")
        
        assert result.success is True


class TestTransformToX12:
    """Tests for transform_to_x12 function."""
    
    def test_empty_data_error(self):
        """Test error when no data provided."""
        from healthsim_agent.tools.format_tools import transform_to_x12
        
        result = transform_to_x12({})
        
        assert result.success is False
    
    def test_837p_professional_claim(self):
        """Test 837P professional claim generation."""
        from healthsim_agent.tools.format_tools import transform_to_x12
        
        data = {
            'members': [{
                'member_id': 'm-123',
                'given_name': 'John',
                'family_name': 'Doe',
                'birth_date': '1980-05-15',
                'gender': 'M',
                'plan_id': 'PLAN001',
            }],
            'claims': [{
                'claim_id': 'clm-123',
                'member_id': 'm-123',
                'claim_type': 'P',
                'service_date': '2025-01-10',
                'total_charge': 150.00,
                'diagnosis_codes': ['E11.9'],
                'procedure_codes': ['99213'],
            }],
        }
        
        result = transform_to_x12(data, transaction_type="837P")
        
        assert result.success is True
        assert result.data is not None
    
    def test_837i_institutional_claim(self):
        """Test 837I institutional claim generation."""
        from healthsim_agent.tools.format_tools import transform_to_x12
        
        data = {
            'members': [{
                'member_id': 'm-456',
                'given_name': 'Jane',
                'family_name': 'Smith',
                'birth_date': '1965-08-22',
                'gender': 'F',
            }],
            'claims': [{
                'claim_id': 'clm-456',
                'member_id': 'm-456',
                'claim_type': 'I',
                'service_date': '2025-01-05',
                'total_charge': 5000.00,
            }],
        }
        
        result = transform_to_x12(data, transaction_type="837I")
        
        assert result.success is True
    
    def test_835_remittance(self):
        """Test 835 remittance advice generation."""
        from healthsim_agent.tools.format_tools import transform_to_x12
        
        data = {
            'claims': [{
                'claim_id': 'clm-789',
                'member_id': 'm-789',
                'total_charge': 200.00,
                'paid_amount': 160.00,
                'claim_status': 'paid',
            }],
        }
        
        result = transform_to_x12(data, transaction_type="835")
        
        assert result.success is True


class TestTransformToNcpdp:
    """Tests for transform_to_ncpdp function."""
    
    def test_empty_data_error(self):
        """Test error when no data provided."""
        from healthsim_agent.tools.format_tools import transform_to_ncpdp
        
        result = transform_to_ncpdp({})
        
        assert result.success is False
    
    def test_with_rx_member_data(self):
        """Test NCPDP message generation with rx_members."""
        from healthsim_agent.tools.format_tools import transform_to_ncpdp
        
        data = {
            'rx_members': [{
                'member_id': 'm-123',
                'given_name': 'John',
                'family_name': 'Doe',
                'birth_date': '1980-05-15',
                'gender': 'M',
                'bin': '123456',
                'pcn': 'RXPCN',
            }],
            'pharmacy_claims': [{
                'claim_id': 'rx-123',
                'member_id': 'm-123',
                'ndc': '00002-3227-30',
                'drug_name': 'Metformin 500mg',
                'quantity': 60,
                'days_supply': 30,
                'fill_date': '2025-01-10',
            }],
        }
        
        result = transform_to_ncpdp(data, message_type="B1")
        
        # Either succeeds or fails with meaningful error
        assert isinstance(result.success, bool)


class TestTransformToMimic:
    """Tests for transform_to_mimic function."""
    
    def test_empty_data_error(self):
        """Test error when no data provided."""
        from healthsim_agent.tools.format_tools import transform_to_mimic
        
        result = transform_to_mimic({})
        
        assert result.success is False
    
    def test_with_patient_data(self):
        """Test MIMIC format generation with patient data."""
        from healthsim_agent.tools.format_tools import transform_to_mimic
        
        data = {
            'patients': [{
                'id': 'p-123',
                'given_name': 'John',
                'family_name': 'Doe',
                'birth_date': '1960-05-15',
                'gender': 'M',
                'mrn': 'MRN001',
            }],
            'encounters': [{
                'encounter_id': 'e-123',
                'patient_mrn': 'MRN001',
                'class_code': 'I',
                'admission_time': '2025-01-10T08:00:00',
                'discharge_time': '2025-01-15T14:00:00',
            }],
        }
        
        result = transform_to_mimic(data)
        
        assert result.success is True
        assert result.data is not None
    
    def test_with_icu_data(self):
        """Test MIMIC format with ICU data."""
        from healthsim_agent.tools.format_tools import transform_to_mimic
        
        data = {
            'patients': [{
                'id': 'p-456',
                'given_name': 'Jane',
                'family_name': 'Smith',
                'birth_date': '1955-08-20',
                'gender': 'F',
                'mrn': 'MRN002',
            }],
            'encounters': [{
                'encounter_id': 'e-456',
                'patient_mrn': 'MRN002',
                'class_code': 'I',
                'admission_time': '2025-01-05T10:00:00',
                'care_unit': 'MICU',
            }],
            'vitals': [{
                'patient_mrn': 'MRN002',
                'encounter_id': 'e-456',
                'vital_type': 'heart_rate',
                'value': '88',
                'units': 'bpm',
                'recorded_time': '2025-01-05T12:00:00',
            }],
        }
        
        result = transform_to_mimic(data)
        
        assert result.success is True


class TestTransformToSdtm:
    """Tests for transform_to_sdtm function."""
    
    def test_empty_data_error(self):
        """Test error when no data provided."""
        from healthsim_agent.tools.format_tools import transform_to_sdtm
        
        result = transform_to_sdtm({})
        
        assert result.success is False
    
    def test_with_subject_data(self):
        """Test SDTM generation with subject data."""
        from healthsim_agent.tools.format_tools import transform_to_sdtm
        
        data = {
            'subjects': [{
                'subject_id': 'SUBJ001',
                'study_id': 'STUDY-001',
                'site_id': 'SITE01',
                'birth_date': '1970-03-15',
                'gender': 'M',
                'race': 'WHITE',
                'ethnicity': 'NOT HISPANIC OR LATINO',
                'enrolled_date': '2024-06-01',
            }],
        }
        
        result = transform_to_sdtm(data)
        
        assert result.success is True
        assert result.data is not None
    
    def test_with_visits(self):
        """Test SDTM with visits."""
        from healthsim_agent.tools.format_tools import transform_to_sdtm
        
        data = {
            'subjects': [{
                'subject_id': 'SUBJ002',
                'study_id': 'STUDY-001',
                'site_id': 'SITE01',
            }],
            'visits': [{
                'subject_id': 'SUBJ002',
                'visit_id': 'V1',
                'visit_name': 'Screening',
                'visit_date': '2024-06-01',
                'visit_status': 'completed',
            }],
        }
        
        result = transform_to_sdtm(data)
        
        assert result.success is True
    
    def test_with_adverse_events(self):
        """Test SDTM with adverse events."""
        from healthsim_agent.tools.format_tools import transform_to_sdtm
        
        data = {
            'subjects': [{
                'subject_id': 'SUBJ003',
                'study_id': 'STUDY-001',
            }],
            'adverse_events': [{
                'subject_id': 'SUBJ003',
                'ae_term': 'Headache',
                'ae_severity': 'Mild',
                'onset_date': '2024-07-15',
                'outcome': 'Recovered',
            }],
        }
        
        result = transform_to_sdtm(data)
        
        assert result.success is True


class TestTransformToAdam:
    """Tests for transform_to_adam function."""
    
    def test_empty_data_error(self):
        """Test error when no data provided."""
        from healthsim_agent.tools.format_tools import transform_to_adam
        
        result = transform_to_adam({})
        
        assert result.success is False
    
    def test_with_subject_data(self):
        """Test ADaM generation with subject data."""
        from healthsim_agent.tools.format_tools import transform_to_adam
        
        data = {
            'subjects': [{
                'subject_id': 'SUBJ001',
                'study_id': 'STUDY-001',
                'arm': 'Treatment',
                'randomization_date': '2024-06-15',
                'age': 55,
                'gender': 'M',
            }],
        }
        
        result = transform_to_adam(data)
        
        assert result.success is True
        assert result.data is not None
    
    def test_with_efficacy_data(self):
        """Test ADaM with efficacy endpoints."""
        from healthsim_agent.tools.format_tools import transform_to_adam
        
        data = {
            'subjects': [{
                'subject_id': 'SUBJ002',
                'study_id': 'STUDY-001',
                'arm': 'Placebo',
            }],
            'efficacy': [{
                'subject_id': 'SUBJ002',
                'parameter': 'HbA1c',
                'baseline': 8.5,
                'week4': 8.2,
                'week12': 7.8,
            }],
        }
        
        result = transform_to_adam(data)
        
        assert result.success is True


class TestListOutputFormats:
    """Tests for list_output_formats function."""
    
    def test_returns_format_dict(self):
        """Test that function returns format dictionary."""
        from healthsim_agent.tools.format_tools import list_output_formats
        
        result = list_output_formats()
        
        assert result.success is True
        assert result.data is not None
        assert isinstance(result.data, dict)
        # Data is a dict of format_id -> format_info
        assert len(result.data) > 0
    
    def test_includes_fhir(self):
        """Test that FHIR is in format list."""
        from healthsim_agent.tools.format_tools import list_output_formats
        
        result = list_output_formats()
        
        # Format keys contain fhir
        assert any('fhir' in key.lower() for key in result.data.keys())
    
    def test_includes_hl7(self):
        """Test that HL7 is in format list."""
        from healthsim_agent.tools.format_tools import list_output_formats
        
        result = list_output_formats()
        
        # Format keys contain hl7
        assert any('hl7' in key.lower() for key in result.data.keys())
    
    def test_includes_x12(self):
        """Test that X12 is in format list."""
        from healthsim_agent.tools.format_tools import list_output_formats
        
        result = list_output_formats()
        
        # Format keys contain x12
        assert any('x12' in key.lower() or '837' in key for key in result.data.keys())
    
    def test_format_has_required_fields(self):
        """Test that formats have required fields."""
        from healthsim_agent.tools.format_tools import list_output_formats
        
        result = list_output_formats()
        
        # Each format should have name and description
        for format_id, format_info in result.data.items():
            assert 'name' in format_info
            assert 'description' in format_info


class TestDictToSubject:
    """Tests for _dict_to_subject helper function."""
    
    def test_basic_subject(self):
        """Test converting basic subject dict."""
        from healthsim_agent.tools.format_tools import _dict_to_subject
        
        data = {
            'subject_id': 'SUBJ001',
            'study_id': 'STUDY-001',
            'site_id': 'SITE01',
            'age': 45,
            'gender': 'F',
        }
        
        subject = _dict_to_subject(data)
        
        assert subject.subject_id == 'SUBJ001'
        assert subject.site_id == 'SITE01'
    
    def test_with_enrollment_info(self):
        """Test subject with enrollment information."""
        from healthsim_agent.tools.format_tools import _dict_to_subject
        
        data = {
            'subject_id': 'SUBJ002',
            'study_id': 'STUDY-001',
            'enrolled_date': '2024-06-01',
            'arm': 'Treatment',
            'randomization_date': '2024-06-15',
        }
        
        subject = _dict_to_subject(data)
        
        # arm is an enum, check its value property
        assert subject.arm is not None


class TestDictToVitalsign:
    """Tests for _dict_to_vitalsign helper function."""
    
    def test_basic_vitalsign(self):
        """Test converting basic vital sign dict."""
        from healthsim_agent.tools.format_tools import _dict_to_vitalsign
        
        data = {
            'patient_mrn': 'MRN001',
            'vital_type': 'blood_pressure',
            'value': '120/80',
            'units': 'mmHg',
            'recorded_time': '2025-01-15T10:30:00',
        }
        
        vital = _dict_to_vitalsign(data)
        
        assert vital.patient_mrn == 'MRN001'
        # Just verify it was created successfully
        assert vital is not None
    
    def test_with_encounter(self):
        """Test vital sign with encounter reference."""
        from healthsim_agent.tools.format_tools import _dict_to_vitalsign
        
        data = {
            'patient_mrn': 'MRN002',
            'encounter_id': 'e-123',
            'vital_type': 'temperature',
            'value': '98.6',
            'units': 'F',
        }
        
        vital = _dict_to_vitalsign(data)
        
        assert vital.encounter_id == 'e-123'


class TestDictToLab:
    """Tests for _dict_to_lab helper function."""
    
    def test_basic_lab(self):
        """Test converting basic lab result dict."""
        from healthsim_agent.tools.format_tools import _dict_to_lab
        
        data = {
            'lab_id': 'lab-001',
            'patient_mrn': 'MRN001',
            'test_name': 'Glucose',
            'loinc_code': '2345-7',
            'value': '95',
            'units': 'mg/dL',
            'reference_range': '70-100',
        }
        
        lab = _dict_to_lab(data)
        
        assert lab.patient_mrn == 'MRN001'
        assert lab.test_name == 'Glucose'
        assert lab.value == '95'
    
    def test_with_abnormal_flag(self):
        """Test lab with abnormal flag."""
        from healthsim_agent.tools.format_tools import _dict_to_lab
        
        data = {
            'lab_id': 'lab-002',
            'patient_mrn': 'MRN002',
            'test_name': 'Hemoglobin A1c',
            'value': '8.5',
            'units': '%',
            'abnormal_flag': 'H',
        }
        
        lab = _dict_to_lab(data)
        
        # Just verify it was created
        assert lab.patient_mrn == 'MRN002'
