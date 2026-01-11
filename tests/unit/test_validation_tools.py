"""Tests for validation tools."""

import pytest
from healthsim_agent.tools.validation_tools import validate_data, fix_validation_issues


class TestValidateData:
    """Tests for data validation."""
    
    def test_validate_valid_patient(self):
        """Validate a correctly formed patient."""
        patients = [{"id": "p-1", "birth_date": "1990-01-15", "gender": "M"}]
        result = validate_data(patients, "patient")
        assert result.success is True
        assert result.data["valid"] is True
        assert result.data["error_count"] == 0
    
    def test_validate_missing_required_field(self):
        """Detect missing required field."""
        patients = [{"id": "p-1", "gender": "M"}]  # Missing birth_date
        result = validate_data(patients, "patient")
        assert result.success is True
        assert result.data["valid"] is False
        assert result.data["error_count"] >= 1
    
    def test_validate_multiple_entities(self):
        """Validate multiple entities."""
        patients = [
            {"id": "p-1", "birth_date": "1990-01-15", "gender": "M"},
            {"id": "p-2", "birth_date": "1985-05-20", "gender": "F"},
        ]
        result = validate_data(patients, "patient")
        assert result.success is True
        assert result.data["entity_count"] == 2
    
    def test_validate_empty_list(self):
        """Handle empty entity list."""
        result = validate_data([], "patient")
        assert result.success is False
        assert "No entities" in result.error
    
    def test_validate_member(self):
        """Validate member entity."""
        members = [{"member_id": "m-1"}]
        result = validate_data(members, "member")
        assert result.success is True
        assert result.data["valid"] is True
    
    def test_validate_subject(self):
        """Validate trial subject entity."""
        subjects = [{"subject_id": "s-1", "protocol_id": "P001"}]
        result = validate_data(subjects, "subject")
        assert result.success is True
        assert result.data["valid"] is True
    
    def test_validate_with_specific_rules(self):
        """Validate with specific rules only."""
        patients = [{"id": "p-1"}]  # Missing other fields
        result = validate_data(patients, "patient", rules=["data_types"])
        assert result.success is True
        # Should pass because we only checked data_types, not required_fields


class TestFixValidationIssues:
    """Tests for auto-fixing validation issues."""
    
    def test_fix_missing_id(self):
        """Generate missing ID."""
        patients = [{"birth_date": "1990-01-15", "gender": "M"}]
        result = fix_validation_issues(patients, "patient", auto_fix=["missing_ids"])
        assert result.success is True
        assert "id" in result.data["entities"][0]
        assert result.data["total_changes"] >= 1
    
    def test_fix_null_defaults(self):
        """Apply default values for nulls."""
        patients = [{"id": "p-1"}]
        result = fix_validation_issues(patients, "patient", auto_fix=["null_defaults"])
        assert result.success is True
        # Should have language and deceased defaults
        assert result.data["entities"][0].get("language") == "en"
        assert result.data["entities"][0].get("deceased") is False
    
    def test_fix_preserves_existing_values(self):
        """Don't overwrite existing values."""
        patients = [{"id": "p-1", "language": "es"}]
        result = fix_validation_issues(patients, "patient", auto_fix=["null_defaults"])
        assert result.success is True
        assert result.data["entities"][0]["language"] == "es"
    
    def test_fix_empty_list(self):
        """Handle empty entity list."""
        result = fix_validation_issues([], "patient")
        assert result.success is False
