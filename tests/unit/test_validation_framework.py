"""Tests for the validation framework module.

Tests cover:
- ValidationSeverity enum
- ValidationIssue dataclass
- ValidationResult class
- BaseValidator and subclasses
- CompositeValidator
- StructuralValidator
"""

import pytest
from dataclasses import dataclass
from datetime import date, datetime, timedelta

from healthsim_agent.validation.framework import (
    ValidationSeverity,
    ValidationIssue,
    ValidationResult,
    BaseValidator,
    CompositeValidator,
    StructuralValidator,
)


class TestValidationSeverity:
    """Tests for ValidationSeverity enum."""

    def test_severity_values(self):
        """Test that severity values are correct."""
        assert ValidationSeverity.ERROR.value == "error"
        assert ValidationSeverity.WARNING.value == "warning"
        assert ValidationSeverity.INFO.value == "info"

    def test_severity_is_string_enum(self):
        """Test that severity inherits from str."""
        assert isinstance(ValidationSeverity.ERROR, str)
        assert ValidationSeverity.ERROR == "error"


class TestValidationIssue:
    """Tests for ValidationIssue dataclass."""

    def test_create_basic_issue(self):
        """Test creating a basic issue."""
        issue = ValidationIssue(
            code="TEST_001",
            message="Test message",
            severity=ValidationSeverity.ERROR,
        )
        assert issue.code == "TEST_001"
        assert issue.message == "Test message"
        assert issue.severity == ValidationSeverity.ERROR
        assert issue.field_path is None
        assert issue.context == {}

    def test_create_issue_with_all_fields(self):
        """Test creating an issue with all fields."""
        issue = ValidationIssue(
            code="TEST_002",
            message="Field error",
            severity=ValidationSeverity.WARNING,
            field_path="person.name",
            context={"expected": "string", "actual": "int"},
        )
        assert issue.field_path == "person.name"
        assert issue.context == {"expected": "string", "actual": "int"}

    def test_issue_str_representation(self):
        """Test string representation of issue."""
        issue = ValidationIssue(
            code="TEST_003",
            message="Some error",
            severity=ValidationSeverity.ERROR,
            field_path="field.name",
        )
        result = str(issue)
        assert "[ERROR]" in result
        assert "TEST_003" in result
        assert "field.name" in result
        assert "Some error" in result

    def test_issue_str_without_field_path(self):
        """Test string representation without field path."""
        issue = ValidationIssue(
            code="TEST_004",
            message="General error",
            severity=ValidationSeverity.INFO,
        )
        result = str(issue)
        assert "[INFO]" in result
        assert " at " not in result


class TestValidationResult:
    """Tests for ValidationResult class."""

    def test_create_valid_result(self):
        """Test creating an empty valid result."""
        result = ValidationResult()
        assert result.valid is True
        assert result.issues == []

    def test_add_error_makes_invalid(self):
        """Test that adding an error makes result invalid."""
        result = ValidationResult()
        result.add_issue(
            code="ERR_001",
            message="Error occurred",
            severity=ValidationSeverity.ERROR,
        )
        assert result.valid is False
        assert len(result.issues) == 1

    def test_add_warning_keeps_valid(self):
        """Test that adding a warning keeps result valid."""
        result = ValidationResult()
        result.add_issue(
            code="WARN_001",
            message="Warning",
            severity=ValidationSeverity.WARNING,
        )
        assert result.valid is True
        assert len(result.issues) == 1

    def test_add_info_keeps_valid(self):
        """Test that adding info keeps result valid."""
        result = ValidationResult()
        result.add_issue(
            code="INFO_001",
            message="Information",
            severity=ValidationSeverity.INFO,
        )
        assert result.valid is True
        assert len(result.issues) == 1

    def test_errors_property(self):
        """Test filtering errors."""
        result = ValidationResult()
        result.add_issue("ERR_001", "Error 1", ValidationSeverity.ERROR)
        result.add_issue("WARN_001", "Warning 1", ValidationSeverity.WARNING)
        result.add_issue("ERR_002", "Error 2", ValidationSeverity.ERROR)
        
        errors = result.errors
        assert len(errors) == 2
        assert all(e.severity == ValidationSeverity.ERROR for e in errors)

    def test_warnings_property(self):
        """Test filtering warnings."""
        result = ValidationResult()
        result.add_issue("ERR_001", "Error", ValidationSeverity.ERROR)
        result.add_issue("WARN_001", "Warning 1", ValidationSeverity.WARNING)
        result.add_issue("WARN_002", "Warning 2", ValidationSeverity.WARNING)
        
        warnings = result.warnings
        assert len(warnings) == 2
        assert all(w.severity == ValidationSeverity.WARNING for w in warnings)

    def test_infos_property(self):
        """Test filtering info messages."""
        result = ValidationResult()
        result.add_issue("INFO_001", "Info 1", ValidationSeverity.INFO)
        result.add_issue("INFO_002", "Info 2", ValidationSeverity.INFO)
        result.add_issue("WARN_001", "Warning", ValidationSeverity.WARNING)
        
        infos = result.infos
        assert len(infos) == 2
        assert all(i.severity == ValidationSeverity.INFO for i in infos)

    def test_merge_results(self):
        """Test merging two results."""
        result1 = ValidationResult()
        result1.add_issue("ERR_001", "Error 1", ValidationSeverity.ERROR)
        
        result2 = ValidationResult()
        result2.add_issue("WARN_001", "Warning 1", ValidationSeverity.WARNING)
        
        result1.merge(result2)
        assert len(result1.issues) == 2
        assert result1.valid is False  # Because of error in result1

    def test_merge_propagates_invalid(self):
        """Test that merging invalid result propagates invalid status."""
        result1 = ValidationResult()  # valid
        result2 = ValidationResult()
        result2.add_issue("ERR_001", "Error", ValidationSeverity.ERROR)  # invalid
        
        result1.merge(result2)
        assert result1.valid is False

    def test_str_representation(self):
        """Test string representation of result."""
        result = ValidationResult()
        result.add_issue("ERR_001", "Error", ValidationSeverity.ERROR)
        result.add_issue("WARN_001", "Warning", ValidationSeverity.WARNING)
        result.add_issue("INFO_001", "Info", ValidationSeverity.INFO)
        
        text = str(result)
        assert "INVALID" in text
        assert "1 errors" in text
        assert "1 warnings" in text
        assert "1 info" in text

    def test_str_representation_valid(self):
        """Test string representation of valid result."""
        result = ValidationResult()
        text = str(result)
        assert "VALID" in text
        assert "0 errors" in text


class TestBaseValidator:
    """Tests for BaseValidator abstract class."""

    def test_validator_call(self):
        """Test that validator is callable."""
        
        class SimpleValidator(BaseValidator):
            def validate(self, value: int) -> ValidationResult:
                result = ValidationResult()
                if value < 0:
                    result.add_issue(
                        code="NEG_001",
                        message="Value cannot be negative",
                        severity=ValidationSeverity.ERROR,
                    )
                return result
        
        validator = SimpleValidator()
        result = validator(10)
        assert result.valid is True
        
        result = validator(-5)
        assert result.valid is False


class TestCompositeValidator:
    """Tests for CompositeValidator class."""

    def test_empty_composite_is_valid(self):
        """Test that empty composite returns valid result."""
        composite = CompositeValidator()
        result = composite.validate()
        assert result.valid is True
        assert len(result.issues) == 0

    def test_composite_runs_all_validators(self):
        """Test that composite runs all validators."""
        
        class AlwaysWarnValidator(BaseValidator):
            def __init__(self, code: str):
                self.code = code
                
            def validate(self) -> ValidationResult:
                result = ValidationResult()
                result.add_issue(self.code, "Warning", ValidationSeverity.WARNING)
                return result
        
        composite = CompositeValidator([
            AlwaysWarnValidator("WARN_001"),
            AlwaysWarnValidator("WARN_002"),
        ])
        
        result = composite.validate()
        assert len(result.issues) == 2

    def test_composite_add_validator(self):
        """Test adding validators to composite."""
        composite = CompositeValidator()
        
        class SimpleValidator(BaseValidator):
            def validate(self) -> ValidationResult:
                result = ValidationResult()
                result.add_issue("INFO_001", "Info", ValidationSeverity.INFO)
                return result
        
        composite.add(SimpleValidator())
        result = composite.validate()
        assert len(result.issues) == 1


class TestStructuralValidator:
    """Tests for StructuralValidator class."""

    @dataclass
    class SampleEntity:
        """Test entity for validation."""
        name: str
        age: int
        email: str | None = None

    def test_required_fields_present(self):
        """Test validation passes when required fields are present."""
        validator = StructuralValidator(required_fields=["name", "age"])
        entity = self.SampleEntity(name="John", age=30)
        
        result = validator.validate(entity)
        assert result.valid is True

    def test_required_field_missing(self):
        """Test validation fails when required field is missing."""
        validator = StructuralValidator(required_fields=["name", "missing_field"])
        entity = self.SampleEntity(name="John", age=30)
        
        result = validator.validate(entity)
        assert result.valid is False
        assert any("STRUCT_001" in i.code for i in result.issues)

    def test_required_field_empty(self):
        """Test validation fails when required field is empty."""
        validator = StructuralValidator(required_fields=["name", "email"])
        entity = self.SampleEntity(name="", age=30, email="test@example.com")
        
        result = validator.validate(entity)
        assert result.valid is False
        assert any("STRUCT_002" in i.code for i in result.issues)

    def test_required_field_none(self):
        """Test validation fails when required field is None."""
        validator = StructuralValidator(required_fields=["email"])
        entity = self.SampleEntity(name="John", age=30, email=None)
        
        result = validator.validate(entity)
        assert result.valid is False
        assert any("STRUCT_002" in i.code for i in result.issues)

    def test_no_required_fields(self):
        """Test validation with no required fields."""
        validator = StructuralValidator()
        entity = self.SampleEntity(name="John", age=30)
        
        result = validator.validate(entity)
        assert result.valid is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
