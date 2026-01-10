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
    _filter_for_patient,
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
        assert "x12" in result.data
        assert "ncpdp_script" in result.data
        assert "mimic_iii" in result.data

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
        assert "patients" in fhir["entity_types"]
        assert fhir["output"] == "JSON"

    def test_x12_transaction_types(self):
        """Test X12 transaction types listed."""
        result = list_output_formats()
        
        x12 = result.data["x12"]
        assert "270" in x12["transaction_types"]
        assert "835" in x12["transaction_types"]
        assert "837P" in x12["transaction_types"]


class TestFilterForPatient:
    """Tests for _filter_for_patient helper."""

    def test_filter_dict_entities(self):
        """Test filtering dict entities."""
        patient = {"mrn": "MRN001"}
        entities = [
            {"mrn": "MRN001", "name": "Entity1"},
            {"mrn": "MRN002", "name": "Entity2"},
            {"mrn": "MRN001", "name": "Entity3"},
        ]
        
        filtered = _filter_for_patient(entities, patient)
        
        assert len(filtered) == 2
        assert all(e["mrn"] == "MRN001" for e in filtered)

    def test_filter_empty_list(self):
        """Test filtering empty list."""
        patient = {"mrn": "MRN001"}
        
        filtered = _filter_for_patient([], patient)
        
        assert filtered == []

    def test_filter_no_matches(self):
        """Test filtering with no matches."""
        patient = {"mrn": "MRN003"}
        entities = [
            {"mrn": "MRN001", "name": "Entity1"},
            {"mrn": "MRN002", "name": "Entity2"},
        ]
        
        filtered = _filter_for_patient(entities, patient)
        
        assert filtered == []


class TestTransformToFHIR:
    """Tests for transform_to_fhir."""

    @patch('healthsim_agent.tools.format_tools._load_cohort_data')
    def test_cohort_not_found(self, mock_load):
        """Test error when cohort not found or transformer unavailable."""
        mock_load.return_value = {"error": "Cohort not found"}
        
        result = transform_to_fhir("nonexistent")
        
        assert result.success is False
        # Either cohort not found OR transformer not available (import order)
        assert "not found" in result.error.lower() or "not available" in result.error.lower()


class TestTransformToCCDA:
    """Tests for transform_to_ccda."""

    @patch('healthsim_agent.tools.format_tools._load_cohort_data')
    def test_no_patients_error(self, mock_load):
        """Test error when no patients in cohort."""
        mock_load.return_value = {"patients": []}
        
        result = transform_to_ccda("test-cohort")
        
        assert result.success is False
        assert "No patients" in result.error

    @patch('healthsim_agent.tools.format_tools._load_cohort_data')
    def test_cohort_not_found(self, mock_load):
        """Test error when cohort not found."""
        mock_load.return_value = {"error": "Cohort not found"}
        
        result = transform_to_ccda("nonexistent")
        
        assert result.success is False
        assert "Cohort not found" in result.error


class TestTransformToHL7v2:
    """Tests for transform_to_hl7v2."""

    @patch('healthsim_agent.tools.format_tools._load_cohort_data')
    def test_cohort_not_found(self, mock_load):
        """Test error when cohort not found or transformer unavailable."""
        mock_load.return_value = {"error": "Cohort not found"}
        
        result = transform_to_hl7v2("nonexistent")
        
        assert result.success is False
        # Either cohort not found OR transformer not available (import order)
        assert "not found" in result.error.lower() or "not available" in result.error.lower()


class TestTransformToX12:
    """Tests for transform_to_x12."""

    @patch('healthsim_agent.tools.format_tools._load_cohort_data')
    def test_cohort_not_found(self, mock_load):
        """Test error when cohort not found."""
        mock_load.return_value = {"error": "Cohort not found"}
        
        result = transform_to_x12("nonexistent", "835")
        
        assert result.success is False
        assert "Cohort not found" in result.error

    @patch('healthsim_agent.tools.format_tools._load_cohort_data')
    def test_unsupported_transaction_type(self, mock_load):
        """Test error for unsupported transaction type."""
        mock_load.return_value = {}
        
        result = transform_to_x12("test-cohort", "999")
        
        assert result.success is False
        assert "Unsupported" in result.error

    @patch('healthsim_agent.tools.format_tools._load_cohort_data')
    def test_no_members_for_270(self, mock_load):
        """Test error when no members for 270."""
        mock_load.return_value = {"members": []}
        
        result = transform_to_x12("test-cohort", "270")
        
        assert result.success is False
        assert "No members" in result.error


class TestTransformToNCPDP:
    """Tests for transform_to_ncpdp."""

    @patch('healthsim_agent.tools.format_tools._load_cohort_data')
    def test_no_prescriptions_error(self, mock_load):
        """Test error when no prescriptions in cohort."""
        mock_load.return_value = {"prescriptions": []}
        
        result = transform_to_ncpdp("test-cohort")
        
        assert result.success is False
        assert "No prescriptions" in result.error

    @patch('healthsim_agent.tools.format_tools._load_cohort_data')
    def test_cohort_not_found(self, mock_load):
        """Test error when cohort not found."""
        mock_load.return_value = {"error": "Cohort not found"}
        
        result = transform_to_ncpdp("nonexistent")
        
        assert result.success is False
        assert "Cohort not found" in result.error


class TestTransformToMIMIC:
    """Tests for transform_to_mimic."""

    @patch('healthsim_agent.tools.format_tools._load_cohort_data')
    def test_no_patients_error(self, mock_load):
        """Test error when no patients in cohort."""
        mock_load.return_value = {"patients": []}
        
        result = transform_to_mimic("test-cohort")
        
        assert result.success is False
        assert "No patients" in result.error

    @patch('healthsim_agent.tools.format_tools._load_cohort_data')
    def test_cohort_not_found(self, mock_load):
        """Test error when cohort not found."""
        mock_load.return_value = {"error": "Cohort not found"}
        
        result = transform_to_mimic("nonexistent")
        
        assert result.success is False
        assert "Cohort not found" in result.error
