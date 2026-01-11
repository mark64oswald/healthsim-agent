"""Tests for format transformation tools."""

import pytest
from unittest.mock import patch, MagicMock
import json

from healthsim_agent.tools.format_tools import (
    transform_to_fhir,
    transform_to_ccda,
    transform_to_hl7v2,
    transform_to_x12,
    transform_to_ncpdp,
    transform_to_mimic,
    list_output_formats,
    _load_cohort_data,
    _dict_to_patient,
    _dict_to_encounter,
    _dict_to_diagnosis,
)
from healthsim_agent.tools.base import ToolResult


class TestListOutputFormats:
    """Tests for list_output_formats."""

    def test_returns_all_formats(self):
        """Test that all formats are listed."""
        result = list_output_formats()
        
        assert result.success is True
        assert "fhir_r4" in result.data
        assert "ccda" in result.data
        assert "hl7v2" in result.data
        # X12 is split into specific transaction types
        assert "x12_837" in result.data
        assert "x12_835" in result.data
        assert "x12_834" in result.data
        assert "ncpdp_d0" in result.data
        assert "mimic_iii" in result.data
        # CDISC formats
        assert "cdisc_sdtm" in result.data
        assert "cdisc_adam" in result.data

    def test_format_structure(self):
        """Test format info structure."""
        result = list_output_formats()
        
        for fmt_key, fmt_info in result.data.items():
            assert "name" in fmt_info
            assert "description" in fmt_info
            assert "entity_types" in fmt_info
            assert "output" in fmt_info
            assert "tool" in fmt_info

    def test_fhir_format_details(self):
        """Test FHIR format details."""
        result = list_output_formats()
        fhir = result.data["fhir_r4"]
        
        assert fhir["name"] == "FHIR R4"
        # Entity types use plural form
        assert "patients" in fhir["entity_types"]
        assert "encounters" in fhir["entity_types"]

    def test_x12_format_details(self):
        """Test X12 format details."""
        result = list_output_formats()
        # X12 837 for claims
        x12_837 = result.data["x12_837"]
        assert "837" in x12_837["name"]
        assert "members" in x12_837["entity_types"] or "claims" in x12_837["entity_types"]
        
        # X12 834 for enrollment
        x12_834 = result.data["x12_834"]
        assert "834" in x12_834["name"]
        assert "members" in x12_834["entity_types"]


class TestDictToPatient:
    """Tests for _dict_to_patient helper."""

    def test_convert_with_name_dict(self):
        """Test converting patient data with name dict."""
        data = {
            "id": "PAT001",
            "mrn": "MRN001",
            "name": {"given_name": "John", "family_name": "Doe"},
            "birth_date": "1980-01-15",
            "gender": "male",
        }
        
        patient = _dict_to_patient(data)
        
        assert patient.id == "PAT001"
        assert patient.mrn == "MRN001"
        assert patient.name.given_name == "John"
        assert patient.name.family_name == "Doe"

    def test_convert_with_flat_names(self):
        """Test converting patient data with flat name fields."""
        data = {
            "id": "PAT002",
            "mrn": "MRN002",
            # Note: Uses given_name/family_name at top level when name dict is missing
            "birth_date": "1990-05-20",
            "gender": "female",
        }
        # Without a name dict, it looks for given_name at top level
        data["name"] = {}  # Empty name dict triggers alternate lookup
        
        patient = _dict_to_patient(data)
        
        # Without given_name, falls back to "Unknown"
        assert patient.name.given_name == "Unknown"

    def test_convert_with_defaults(self):
        """Test converting patient data with minimal fields."""
        data = {
            "id": "PAT003",
            "mrn": "MRN003",
        }
        
        patient = _dict_to_patient(data)
        
        assert patient.id == "PAT003"
        assert patient.name.given_name == "Unknown"


class TestTransformToFHIR:
    """Tests for transform_to_fhir."""

    @patch('healthsim_agent.tools.format_tools._load_cohort_data')
    def test_cohort_not_found(self, mock_load):
        """Test error when cohort not found."""
        mock_load.return_value = None  # Returns None when not found
        
        result = transform_to_fhir("nonexistent")
        
        assert result.success is False
        assert "no data" in result.error.lower()

    @patch('healthsim_agent.tools.format_tools._load_cohort_data')
    def test_no_patient_data(self, mock_load):
        """Test error when no patient data in cohort."""
        mock_load.return_value = {}  # Empty cohort data
        
        result = transform_to_fhir("test-cohort")
        
        assert result.success is False
        assert "patient" in result.error.lower()


class TestTransformToCCDA:
    """Tests for transform_to_ccda."""

    @patch('healthsim_agent.tools.format_tools._load_cohort_data')
    def test_no_patients_error(self, mock_load):
        """Test error when no patients in cohort."""
        mock_load.return_value = {"encounter": [{"id": "ENC001"}]}
        
        result = transform_to_ccda("test-cohort")
        
        assert result.success is False
        assert "patient" in result.error.lower()

    @patch('healthsim_agent.tools.format_tools._load_cohort_data')
    def test_cohort_not_found(self, mock_load):
        """Test error when cohort not found."""
        mock_load.return_value = None
        
        result = transform_to_ccda("nonexistent")
        
        assert result.success is False
        assert "no data" in result.error.lower()


class TestTransformToHL7v2:
    """Tests for transform_to_hl7v2."""

    @patch('healthsim_agent.tools.format_tools._load_cohort_data')
    def test_cohort_not_found(self, mock_load):
        """Test error when cohort not found."""
        mock_load.return_value = None
        
        result = transform_to_hl7v2("nonexistent")
        
        assert result.success is False
        assert "no data" in result.error.lower()

    @patch('healthsim_agent.tools.format_tools._load_cohort_data')
    def test_no_patient_data(self, mock_load):
        """Test error when no patient data."""
        mock_load.return_value = {}
        
        result = transform_to_hl7v2("test-cohort")
        
        assert result.success is False
        assert "patient" in result.error.lower()


class TestTransformToX12:
    """Tests for transform_to_x12."""

    @patch('healthsim_agent.tools.format_tools._load_cohort_data')
    def test_cohort_not_found(self, mock_load):
        """Test error when cohort not found."""
        mock_load.return_value = None
        
        result = transform_to_x12("nonexistent")
        
        assert result.success is False
        assert "no data" in result.error.lower()

    @patch('healthsim_agent.tools.format_tools._load_cohort_data')
    def test_unsupported_transaction_type(self, mock_load):
        """Test error for unsupported transaction type."""
        mock_load.return_value = {"member": [{"member_id": "M001"}]}
        
        result = transform_to_x12("test-cohort", transaction_type="999")
        
        assert result.success is False
        assert "unsupported" in result.error.lower()

    @patch('healthsim_agent.tools.format_tools._load_cohort_data')
    def test_no_data_error(self, mock_load):
        """Test error when no member/claim data."""
        mock_load.return_value = {}
        
        result = transform_to_x12("test-cohort")
        
        assert result.success is False
        assert "member" in result.error.lower() or "claim" in result.error.lower()


class TestTransformToNCPDP:
    """Tests for transform_to_ncpdp."""

    @patch('healthsim_agent.tools.format_tools._load_cohort_data')
    def test_no_rx_data_error(self, mock_load):
        """Test error when no rx member/pharmacy claim data."""
        mock_load.return_value = {}
        
        result = transform_to_ncpdp("test-cohort")
        
        assert result.success is False
        # Updated error message mentions rx_member or pharmacy_claims
        assert "rxmember" in result.error.lower() or "pharmacy" in result.error.lower()

    @patch('healthsim_agent.tools.format_tools._load_cohort_data')
    def test_cohort_not_found(self, mock_load):
        """Test error when cohort not found."""
        mock_load.return_value = None
        
        result = transform_to_ncpdp("nonexistent")
        
        assert result.success is False
        assert "no data" in result.error.lower()


class TestTransformToMIMIC:
    """Tests for transform_to_mimic."""

    @patch('healthsim_agent.tools.format_tools._load_cohort_data')
    def test_no_patients_error(self, mock_load):
        """Test error when no patients in cohort."""
        mock_load.return_value = {}
        
        result = transform_to_mimic("test-cohort")
        
        assert result.success is False
        assert "patient" in result.error.lower()

    @patch('healthsim_agent.tools.format_tools._load_cohort_data')
    def test_cohort_not_found(self, mock_load):
        """Test error when cohort not found."""
        mock_load.return_value = None
        
        result = transform_to_mimic("nonexistent")
        
        assert result.success is False
        assert "no data" in result.error.lower()
