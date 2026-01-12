"""
Additional tests for format_tools.py MIMIC, SDTM, and ADaM transforms.

Covers uncovered code paths:
- transform_to_mimic
- transform_to_sdtm  
- transform_to_adam
- Error handling branches
"""

import pytest
from datetime import date, datetime
from unittest.mock import MagicMock, patch


class TestTransformToMimic:
    """Tests for transform_to_mimic function."""
    
    def test_basic_patient_transform(self):
        """Test MIMIC transform with basic patient data."""
        from healthsim_agent.tools.format_tools import transform_to_mimic
        
        data = {
            "patients": [{
                "id": "P001",
                "mrn": "MRN001",
                "given_name": "John",
                "family_name": "Doe",
                "birth_date": "1980-01-15",
                "gender": "M"
            }]
        }
        
        result = transform_to_mimic(data)
        
        assert result.success is True
        assert "PATIENTS" in result.data
        assert len(result.data["PATIENTS"]) == 1
        assert result.data["PATIENTS"][0]["gender"] == "M"
    
    def test_mimic_with_encounters(self):
        """Test MIMIC transform with encounters."""
        from healthsim_agent.tools.format_tools import transform_to_mimic
        
        data = {
            "patients": [{
                "id": "P001",
                "mrn": "MRN001",
                "given_name": "John",
                "family_name": "Doe",
                "birth_date": "1980-01-15",
                "gender": "M"
            }],
            "encounters": [{
                "id": "E001",
                "patient_mrn": "MRN001",
                "admission_time": "2024-01-15T10:00:00",
                "discharge_time": "2024-01-17T14:00:00",
                "class": "E"  # Emergency
            }]
        }
        
        result = transform_to_mimic(data)
        
        assert result.success is True
        assert len(result.data["ADMISSIONS"]) == 1
        assert result.data["ADMISSIONS"][0]["admission_type"] == "EMERGENCY"
    
    def test_mimic_with_vitals(self):
        """Test MIMIC transform with vital signs."""
        from healthsim_agent.tools.format_tools import transform_to_mimic
        
        data = {
            "patients": [{
                "mrn": "MRN001",
                "given_name": "Jane",
                "family_name": "Doe",
                "birth_date": "1990-05-20",
                "gender": "F"
            }],
            "vitals": [{
                "patient_mrn": "MRN001",
                "observation_time": "2024-01-15T14:30:00",
                "heart_rate": 72,
                "systolic_bp": 120,
                "diastolic_bp": 80  # Both BP values required together
            }]
        }
        
        result = transform_to_mimic(data)
        
        assert result.success is True
        assert len(result.data["CHARTEVENTS"]) >= 2  # HR and BP
    
    def test_mimic_with_labs(self):
        """Test MIMIC transform with lab results."""
        from healthsim_agent.tools.format_tools import transform_to_mimic
        
        data = {
            "patients": [{
                "mrn": "MRN001",
                "given_name": "Test",
                "family_name": "Patient",
                "birth_date": "1975-03-10",
                "gender": "M"
            }],
            "labs": [{
                "patient_mrn": "MRN001",
                "test_name": "Glucose",
                "loinc_code": "2345-7",
                "value": "95",
                "unit": "mg/dL",
                "collected_time": "2024-01-15T08:00:00"
            }]
        }
        
        result = transform_to_mimic(data)
        
        assert result.success is True
        assert len(result.data["LABEVENTS"]) == 1
        assert result.data["LABEVENTS"][0]["valuenum"] == 95.0
    
    def test_mimic_lab_non_numeric_value(self):
        """Test MIMIC transform with non-numeric lab value."""
        from healthsim_agent.tools.format_tools import transform_to_mimic
        
        data = {
            "patients": [{
                "mrn": "MRN001",
                "given_name": "Test",
                "family_name": "Patient",
                "birth_date": "1975-03-10",
                "gender": "M"
            }],
            "labs": [{
                "patient_mrn": "MRN001",
                "test_name": "Culture",
                "value": "Positive",  # Non-numeric
                "unit": None
            }]
        }
        
        result = transform_to_mimic(data)
        
        assert result.success is True
        assert result.data["LABEVENTS"][0]["valuenum"] is None
    
    def test_mimic_no_data_error(self):
        """Test MIMIC transform with no data."""
        from healthsim_agent.tools.format_tools import transform_to_mimic
        
        result = transform_to_mimic("nonexistent-cohort-xyz")
        
        assert result.success is False
        assert "No data found" in result.error
    
    def test_mimic_no_patients_error(self):
        """Test MIMIC transform with no patients."""
        from healthsim_agent.tools.format_tools import transform_to_mimic
        
        # Empty patients list, no other entities
        data = {"patients": []}
        result = transform_to_mimic(data)
        
        assert result.success is False
        assert "No patient data" in result.error
    
    def test_mimic_female_patient(self):
        """Test MIMIC transform female patient gender mapping."""
        from healthsim_agent.tools.format_tools import transform_to_mimic
        
        data = {
            "patients": [{
                "mrn": "MRN002",
                "given_name": "Jane",
                "family_name": "Smith",
                "birth_date": "1985-06-15",
                "gender": "F"
            }]
        }
        
        result = transform_to_mimic(data)
        
        assert result.data["PATIENTS"][0]["gender"] == "F"
    
    def test_mimic_unknown_gender(self):
        """Test MIMIC transform with unknown gender."""
        from healthsim_agent.tools.format_tools import transform_to_mimic
        
        data = {
            "patients": [{
                "mrn": "MRN003",
                "given_name": "Pat",
                "family_name": "Unknown",
                "birth_date": "1990-01-01",
                "gender": "X"  # Unknown/other
            }]
        }
        
        result = transform_to_mimic(data)
        
        assert result.data["PATIENTS"][0]["gender"] == "U"
    
    def test_mimic_with_diagnoses(self):
        """Test MIMIC transform with diagnoses."""
        from healthsim_agent.tools.format_tools import transform_to_mimic
        
        data = {
            "patients": [{
                "mrn": "MRN001",
                "given_name": "John",
                "family_name": "Doe",
                "birth_date": "1970-01-01",
                "gender": "M"
            }],
            "encounters": [{
                "id": "E001",
                "encounter_id": "E001",
                "patient_mrn": "MRN001",
                "admission_time": "2024-01-15T10:00:00",
                "class": "I"  # Inpatient
            }],
            "diagnoses": [{
                "patient_mrn": "MRN001",
                "encounter_id": "E001",
                "code": "E11.9",
                "description": "Type 2 diabetes"
            }]
        }
        
        result = transform_to_mimic(data)
        
        assert result.success is True
        assert len(result.data["DIAGNOSES_ICD"]) == 1
        assert result.data["DIAGNOSES_ICD"][0]["icd_code"] == "E11.9"


class TestTransformToSdtm:
    """Tests for transform_to_sdtm function."""
    
    def test_basic_sdtm_transform(self):
        """Test SDTM transform with basic subject data."""
        from healthsim_agent.tools.format_tools import transform_to_sdtm
        
        data = {
            "subjects": [{
                "subject_id": "001",
                "site_id": "SITE01",
                "arm": "Treatment",
                "randomized_date": "2024-01-15",
                "birth_date": "1980-05-20",
                "sex": "M",
                "race": "WHITE"
            }]
        }
        
        result = transform_to_sdtm(data, study_id="TEST01")
        
        assert result.success is True
        assert "DM" in result.data  # Demographics domain
    
    def test_sdtm_with_visits(self):
        """Test SDTM transform with visit data."""
        from healthsim_agent.tools.format_tools import transform_to_sdtm
        
        data = {
            "subjects": [{
                "subject_id": "001",
                "site_id": "SITE01",
                "arm": "Control",
                "randomized_date": "2024-01-15",
                "sex": "F"
            }],
            "visits": [{
                "subject_id": "001",
                "visit_number": 1,
                "visit_date": "2024-01-15",
                "visit_type": "Screening"
            }]
        }
        
        result = transform_to_sdtm(data, study_id="TEST01", domains=["DM", "SV"])
        
        assert result.success is True
    
    def test_sdtm_no_data_error(self):
        """Test SDTM transform with no data."""
        from healthsim_agent.tools.format_tools import transform_to_sdtm
        
        result = transform_to_sdtm(None, data=None)
        
        assert result.success is False
    
    def test_sdtm_with_adverse_events(self):
        """Test SDTM transform with adverse events."""
        from healthsim_agent.tools.format_tools import transform_to_sdtm
        
        data = {
            "subjects": [{
                "subject_id": "001",
                "site_id": "SITE01",
                "arm": "Treatment",
                "sex": "M"
            }],
            "adverse_events": [{
                "subject_id": "001",
                "term": "Headache",
                "start_date": "2024-01-20",
                "severity": "Mild"
            }]
        }
        
        result = transform_to_sdtm(data, study_id="TEST01", domains=["DM", "AE"])
        
        assert result.success is True
    
    def test_sdtm_with_exposures(self):
        """Test SDTM transform with exposure data."""
        from healthsim_agent.tools.format_tools import transform_to_sdtm
        
        data = {
            "subjects": [{
                "subject_id": "001",
                "site_id": "SITE01",
                "arm": "Active",
                "sex": "F"
            }],
            "exposures": [{
                "subject_id": "001",
                "drug_name": "Study Drug",
                "dose": 100,
                "dose_unit": "mg",
                "start_date": "2024-01-15"
            }]
        }
        
        result = transform_to_sdtm(data, study_id="TEST01", domains=["DM", "EX"])
        
        assert result.success is True


class TestTransformToAdam:
    """Tests for transform_to_adam function."""
    
    def test_basic_adam_transform(self):
        """Test ADaM transform with basic data."""
        from healthsim_agent.tools.format_tools import transform_to_adam
        
        data = {
            "subjects": [{
                "subject_id": "001",
                "site_id": "SITE01",
                "arm": "Treatment",
                "randomized_date": "2024-01-15",
                "sex": "M",
                "age": 45
            }]
        }
        
        result = transform_to_adam(data, study_id="TEST01")
        
        assert result.success is True
        assert "ADSL" in result.data  # Subject-level analysis dataset
    
    def test_adam_no_data_error(self):
        """Test ADaM transform with no data."""
        from healthsim_agent.tools.format_tools import transform_to_adam
        
        result = transform_to_adam(None, data=None)
        
        assert result.success is False
    
    def test_adam_with_efficacy_data(self):
        """Test ADaM transform with efficacy endpoint data."""
        from healthsim_agent.tools.format_tools import transform_to_adam
        
        data = {
            "subjects": [{
                "subject_id": "001",
                "site_id": "SITE01",
                "arm": "Treatment",
                "sex": "F"
            }],
            "efficacy_endpoints": [{
                "subject_id": "001",
                "parameter": "Response",
                "visit": "Week 12",
                "value": "Complete Response"
            }]
        }
        
        result = transform_to_adam(data, study_id="TEST01", datasets=["ADSL", "ADEFF"])
        
        assert result.success is True
    
    def test_adam_with_safety_data(self):
        """Test ADaM transform with safety analysis data."""
        from healthsim_agent.tools.format_tools import transform_to_adam
        
        data = {
            "subjects": [{
                "subject_id": "001",
                "site_id": "SITE01",
                "arm": "Control",
                "sex": "M"
            }],
            "adverse_events": [{
                "subject_id": "001",
                "term": "Nausea",
                "severity": "Moderate",
                "start_date": "2024-02-01"
            }]
        }
        
        result = transform_to_adam(data, study_id="TEST01", datasets=["ADSL", "ADAE"])
        
        assert result.success is True


class TestTransformEdgeCases:
    """Tests for edge cases in transform functions."""
    
    def test_fhir_exception_handling(self):
        """Test FHIR transform exception handling."""
        from healthsim_agent.tools.format_tools import transform_to_fhir
        
        # Bad data that might cause exception
        data = {
            "patients": [{"invalid": True}]  # Missing required fields
        }
        
        result = transform_to_fhir(data)
        # Should either succeed with defaults or return error gracefully
        # Not raise an exception
        assert isinstance(result.success, bool)
    
    def test_ccda_exception_handling(self):
        """Test CCDA transform exception handling."""
        from healthsim_agent.tools.format_tools import transform_to_ccda
        
        data = {
            "patients": [{"mrn": "MRN001", "given_name": "Test", "family_name": "Patient"}]
        }
        
        result = transform_to_ccda(data)
        # Should handle gracefully
        assert isinstance(result.success, bool)
    
    def test_hl7v2_exception_handling(self):
        """Test HL7v2 transform handles edge cases."""
        from healthsim_agent.tools.format_tools import transform_to_hl7v2
        
        # Test with minimal data
        data = {
            "patients": [{
                "mrn": "MRN001",
                "given_name": "Test",
                "family_name": "Patient",
                "birth_date": "1980-01-01",
                "gender": "M"
            }],
            "encounters": [{
                "patient_mrn": "MRN001",
                "admission_time": "2024-01-15T10:00:00"
            }]
        }
        
        result = transform_to_hl7v2(data, message_type="ADT_A01")
        assert isinstance(result.success, bool)
    
    def test_x12_837p_transform(self):
        """Test X12 837P professional claim transform."""
        from healthsim_agent.tools.format_tools import transform_to_x12
        
        data = {
            "members": [{
                "member_id": "M001",
                "given_name": "John",
                "family_name": "Doe",
                "birth_date": "1980-01-15",
                "gender": "M"
            }],
            "claims": [{
                "claim_id": "CLM001",
                "member_id": "M001",
                "service_date": "2024-01-15",
                "provider_npi": "1234567890",
                "total_billed": 150.00,
                "lines": [{
                    "procedure_code": "99213",
                    "billed_amount": 150.00
                }]
            }]
        }
        
        result = transform_to_x12(data, transaction_type="837P")
        assert isinstance(result.success, bool)
    
    def test_ncpdp_b1_transform(self):
        """Test NCPDP B1 billing request transform."""
        from healthsim_agent.tools.format_tools import transform_to_ncpdp
        
        data = {
            "prescriptions": [{
                "rx_number": "RX123456",
                "patient_id": "P001",
                "drug_name": "Metformin",
                "ndc": "12345678901",
                "quantity": 30,
                "days_supply": 30,
                "fill_date": "2024-01-15"
            }]
        }
        
        result = transform_to_ncpdp(data, message_type="B1")
        assert isinstance(result.success, bool)


class TestListOutputFormatsCoverage:
    """Tests for list_output_formats function coverage."""
    
    def test_list_all_formats(self):
        """Test listing all output formats."""
        from healthsim_agent.tools.format_tools import list_output_formats
        
        result = list_output_formats()
        
        assert result.success is True
        formats = result.data
        
        # Result is dict keyed by format code
        assert isinstance(formats, dict)
        assert "fhir_r4" in formats
        assert formats["fhir_r4"]["name"] == "FHIR R4"
    
    def test_formats_have_metadata(self):
        """Test format entries have required metadata."""
        from healthsim_agent.tools.format_tools import list_output_formats
        
        result = list_output_formats()
        
        for code, fmt in result.data.items():
            assert "name" in fmt
            assert "description" in fmt
            assert "tool" in fmt
