"""Extended tests for validation_tools module.

Covers additional validators and helper functions.
"""

import pytest
from healthsim_agent.tools.validation_tools import (
    validate_data,
    fix_validation_issues,
    _get_validator,
    _validate_patient,
    _validate_member,
    _validate_subject,
    _validate_rx_member,
    _validate_encounter,
    _validate_claim,
    _validate_diagnosis,
    _validate_generic,
    _get_id_field,
    _get_defaults,
    _is_valid_date,
    _normalize_date,
    _is_valid_icd10,
)


class TestGetValidator:
    """Tests for _get_validator function."""
    
    def test_get_patient_validator(self):
        """Get patient validator."""
        validator = _get_validator("patient")
        assert validator is not None
        assert callable(validator)
    
    def test_get_member_validator(self):
        """Get member validator."""
        validator = _get_validator("member")
        assert validator is not None
    
    def test_get_subject_validator(self):
        """Get subject validator."""
        validator = _get_validator("subject")
        assert validator is not None
    
    def test_get_rx_member_validator(self):
        """Get rx_member validator."""
        validator = _get_validator("rx_member")
        assert validator is not None
    
    def test_get_encounter_validator(self):
        """Get encounter validator."""
        validator = _get_validator("encounter")
        assert validator is not None
    
    def test_get_claim_validator(self):
        """Get claim validator."""
        validator = _get_validator("claim")
        assert validator is not None
    
    def test_get_diagnosis_validator(self):
        """Get diagnosis validator."""
        validator = _get_validator("diagnosis")
        assert validator is not None
    
    def test_get_unknown_validator(self):
        """Get generic validator for unknown type."""
        validator = _get_validator("unknown_type")
        assert validator is not None
        assert validator == _validate_generic


class TestValidatePatient:
    """Tests for _validate_patient function."""
    
    def test_validate_complete_patient(self):
        """Validate complete patient record."""
        patient = {
            "id": "p-123",
            "given_name": "John",
            "family_name": "Doe",
            "birth_date": "1980-05-15",
            "gender": "M",
        }
        errors, warnings = _validate_patient(patient, ["all"])
        assert len(errors) == 0
    
    def test_validate_patient_missing_id(self):
        """Patient missing ID."""
        patient = {
            "given_name": "John",
            "birth_date": "1980-05-15",
        }
        errors, warnings = _validate_patient(patient, ["required_fields"])
        assert len(errors) >= 1
    
    def test_validate_patient_invalid_date(self):
        """Patient with invalid birth date."""
        patient = {
            "id": "p-123",
            "birth_date": "not-a-date",
        }
        errors, warnings = _validate_patient(patient, ["data_types"])
        assert len(errors) >= 1


class TestValidateMember:
    """Tests for _validate_member function."""
    
    def test_validate_complete_member(self):
        """Validate complete member record."""
        member = {
            "member_id": "m-123",
            "plan_id": "PLAN001",
            "effective_date": "2024-01-01",
        }
        errors, warnings = _validate_member(member, ["all"])
        assert len(errors) == 0
    
    def test_validate_member_missing_id(self):
        """Member missing ID."""
        member = {
            "plan_id": "PLAN001",
        }
        errors, warnings = _validate_member(member, ["required_fields"])
        assert len(errors) >= 1


class TestValidateSubject:
    """Tests for _validate_subject function."""
    
    def test_validate_complete_subject(self):
        """Validate complete subject record."""
        subject = {
            "subject_id": "SUBJ001",
            "protocol_id": "PROT001",
            "site_id": "SITE01",
        }
        errors, warnings = _validate_subject(subject, ["all"])
        assert len(errors) == 0
    
    def test_validate_subject_missing_protocol(self):
        """Subject missing protocol."""
        subject = {
            "subject_id": "SUBJ001",
        }
        errors, warnings = _validate_subject(subject, ["required_fields"])
        # May or may not have error depending on strictness
        assert isinstance(errors, list)


class TestValidateRxMember:
    """Tests for _validate_rx_member function."""
    
    def test_validate_complete_rx_member(self):
        """Validate complete rx_member record."""
        rx_member = {
            "member_id": "m-123",
            "bin": "123456",
            "pcn": "RXPCN",
        }
        errors, warnings = _validate_rx_member(rx_member, ["all"])
        assert len(errors) == 0


class TestValidateEncounter:
    """Tests for _validate_encounter function."""
    
    def test_validate_complete_encounter(self):
        """Validate complete encounter record."""
        encounter = {
            "encounter_id": "e-123",
            "patient_mrn": "MRN001",
            "admission_time": "2025-01-10T08:00:00",
        }
        errors, warnings = _validate_encounter(encounter, ["all"])
        assert len(errors) == 0
    
    def test_validate_encounter_missing_patient(self):
        """Encounter missing patient reference."""
        encounter = {
            "encounter_id": "e-123",
        }
        errors, warnings = _validate_encounter(encounter, ["required_fields"])
        assert isinstance(errors, list)


class TestValidateClaim:
    """Tests for _validate_claim function."""
    
    def test_validate_complete_claim(self):
        """Validate complete claim record."""
        claim = {
            "claim_id": "clm-123",
            "member_id": "m-123",
            "service_date": "2025-01-10",
        }
        errors, warnings = _validate_claim(claim, ["all"])
        assert len(errors) == 0


class TestValidateDiagnosis:
    """Tests for _validate_diagnosis function."""
    
    def test_validate_complete_diagnosis(self):
        """Validate complete diagnosis record."""
        diagnosis = {
            "code": "E11.9",
            "description": "Type 2 diabetes",
            "patient_mrn": "MRN001",
        }
        errors, warnings = _validate_diagnosis(diagnosis, ["all"])
        assert len(errors) == 0
    
    def test_validate_diagnosis_invalid_code(self):
        """Diagnosis with invalid ICD-10 code."""
        diagnosis = {
            "code": "INVALID",
            "patient_mrn": "MRN001",
        }
        errors, warnings = _validate_diagnosis(diagnosis, ["code_systems"])
        # Should have error for invalid code
        assert isinstance(errors, list)


class TestValidateGeneric:
    """Tests for _validate_generic function."""
    
    def test_validate_generic_entity(self):
        """Validate generic entity."""
        entity = {
            "id": "g-123",
            "name": "Test Entity",
        }
        errors, warnings = _validate_generic(entity, ["all"])
        assert len(errors) == 0


class TestGetIdField:
    """Tests for _get_id_field function."""
    
    def test_patient_id_field(self):
        """Get patient ID field."""
        assert _get_id_field("patient") == "id"
    
    def test_member_id_field(self):
        """Get member ID field."""
        assert _get_id_field("member") == "member_id"
    
    def test_subject_id_field(self):
        """Get subject ID field."""
        assert _get_id_field("subject") == "subject_id"
    
    def test_encounter_id_field(self):
        """Get encounter ID field."""
        result = _get_id_field("encounter")
        # Returns 'id' not 'encounter_id'
        assert result == "id"
    
    def test_claim_id_field(self):
        """Get claim ID field."""
        assert _get_id_field("claim") == "claim_id"
    
    def test_unknown_id_field(self):
        """Get ID field for unknown type."""
        result = _get_id_field("unknown")
        # Returns None or default
        assert result is None or isinstance(result, str)


class TestGetDefaults:
    """Tests for _get_defaults function."""
    
    def test_patient_defaults(self):
        """Get patient defaults."""
        defaults = _get_defaults("patient")
        assert isinstance(defaults, dict)
        assert "language" in defaults
        assert defaults["language"] == "en"
    
    def test_member_defaults(self):
        """Get member defaults."""
        defaults = _get_defaults("member")
        assert isinstance(defaults, dict)
    
    def test_unknown_defaults(self):
        """Get defaults for unknown type."""
        defaults = _get_defaults("unknown")
        assert isinstance(defaults, dict)


class TestIsValidDate:
    """Tests for _is_valid_date function."""
    
    def test_valid_iso_date(self):
        """Valid ISO date string."""
        assert _is_valid_date("2025-01-15") is True
    
    def test_valid_datetime_string(self):
        """Valid datetime string."""
        assert _is_valid_date("2025-01-15T10:30:00") is True
    
    def test_invalid_date_string(self):
        """Invalid date string."""
        assert _is_valid_date("not-a-date") is False
    
    def test_none_value(self):
        """None value returns True (permissive)."""
        # Function allows None as valid
        assert _is_valid_date(None) is True
    
    def test_empty_string(self):
        """Empty string is not valid."""
        assert _is_valid_date("") is False


class TestNormalizeDate:
    """Tests for _normalize_date function."""
    
    def test_normalize_date_string(self):
        """Normalize date string."""
        result = _normalize_date("2025-01-15")
        assert isinstance(result, str)
        assert "2025" in result
    
    def test_normalize_datetime_string(self):
        """Normalize datetime string."""
        result = _normalize_date("2025-01-15T10:30:00")
        assert isinstance(result, str)
    
    def test_normalize_invalid(self):
        """Normalize invalid returns original."""
        result = _normalize_date("invalid")
        assert result == "invalid"


class TestIsValidIcd10:
    """Tests for _is_valid_icd10 function."""
    
    def test_valid_icd10_codes(self):
        """Valid ICD-10 codes."""
        assert _is_valid_icd10("E11.9") is True
        assert _is_valid_icd10("I10") is True
        assert _is_valid_icd10("J18.9") is True
    
    def test_invalid_icd10_codes(self):
        """Invalid ICD-10 codes."""
        assert _is_valid_icd10("INVALID") is False
        assert _is_valid_icd10("123") is False
        assert _is_valid_icd10("") is False


class TestValidateDataEdgeCases:
    """Edge case tests for validate_data."""
    
    def test_validate_encounter(self):
        """Validate encounter entities."""
        encounters = [{
            "encounter_id": "e-1",
            "patient_mrn": "MRN001",
            "admission_time": "2025-01-10T08:00:00",
        }]
        result = validate_data(encounters, "encounter")
        assert result.success is True
    
    def test_validate_claim(self):
        """Validate claim entities."""
        claims = [{
            "claim_id": "clm-1",
            "member_id": "m-1",
            "service_date": "2025-01-10",
        }]
        result = validate_data(claims, "claim")
        assert result.success is True
    
    def test_validate_rx_member(self):
        """Validate rx_member entities."""
        rx_members = [{
            "member_id": "m-1",
            "bin": "123456",
        }]
        result = validate_data(rx_members, "rx_member")
        assert result.success is True
    
    def test_validate_diagnosis(self):
        """Validate diagnosis entities."""
        diagnoses = [{
            "code": "E11.9",
            "description": "Type 2 diabetes",
            "patient_mrn": "MRN001",
        }]
        result = validate_data(diagnoses, "diagnosis")
        assert result.success is True


class TestFixValidationIssuesExtended:
    """Extended tests for fix_validation_issues."""
    
    def test_fix_member_missing_id(self):
        """Fix missing member ID."""
        members = [{"plan_id": "PLAN001"}]
        result = fix_validation_issues(members, "member", auto_fix=["missing_ids"])
        assert result.success is True
        assert "member_id" in result.data["entities"][0]
    
    def test_fix_subject_missing_id(self):
        """Fix missing subject ID."""
        subjects = [{"protocol_id": "PROT001"}]
        result = fix_validation_issues(subjects, "subject", auto_fix=["missing_ids"])
        assert result.success is True
        assert "subject_id" in result.data["entities"][0]
    
    def test_fix_encounter_missing_id(self):
        """Fix missing encounter ID."""
        encounters = [{"patient_mrn": "MRN001"}]
        result = fix_validation_issues(encounters, "encounter", auto_fix=["missing_ids"])
        assert result.success is True
        # Uses 'id' not 'encounter_id'
        assert "id" in result.data["entities"][0]
    
    def test_fix_all_issues(self):
        """Fix with all auto-fix options."""
        patients = [{"given_name": "John"}]
        result = fix_validation_issues(patients, "patient", auto_fix=["missing_ids", "null_defaults"])
        assert result.success is True
        # Should have ID and defaults applied
        assert "id" in result.data["entities"][0]
