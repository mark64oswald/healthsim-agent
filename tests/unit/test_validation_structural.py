"""Tests for structural validation utilities.

Tests cover:
- ReferentialIntegrityValidator
- Reference validation
- Required reference validation
- Unique ID validation
- Foreign key validation
"""

import pytest
from dataclasses import dataclass
from typing import Optional

from healthsim_agent.validation.structural import ReferentialIntegrityValidator
from healthsim_agent.validation.framework import ValidationSeverity


@dataclass
class MockEntity:
    """Mock entity for testing."""
    id: str
    name: str
    parent_id: Optional[str] = None


class TestReferentialIntegrityValidator:
    """Tests for ReferentialIntegrityValidator."""

    @pytest.fixture
    def validator(self):
        """Create validator instance."""
        return ReferentialIntegrityValidator()

    def test_generic_validate_returns_valid(self, validator):
        """Test that generic validate returns valid result."""
        result = validator.validate()
        assert result.valid is True

    # validate_reference tests
    class TestValidateReference:
        """Tests for validate_reference method."""

        @pytest.fixture
        def validator(self):
            return ReferentialIntegrityValidator()

        def test_matching_ids_valid(self, validator):
            """Test validation passes when IDs match."""
            result = validator.validate_reference(
                source_id="ABC123",
                target_id="ABC123",
                source_field="patient_id",
                target_field="patient.id",
            )
            assert result.valid is True

        def test_mismatched_ids_invalid(self, validator):
            """Test validation fails when IDs don't match."""
            result = validator.validate_reference(
                source_id="ABC123",
                target_id="XYZ789",
                source_field="patient_id",
                target_field="patient.id",
            )
            assert result.valid is False
            assert any("REF_001" in i.code for i in result.issues)

        def test_none_source_valid(self, validator):
            """Test validation passes when source is None."""
            result = validator.validate_reference(
                source_id=None,
                target_id="ABC123",
                source_field="patient_id",
                target_field="patient.id",
            )
            assert result.valid is True

        def test_none_target_valid(self, validator):
            """Test validation passes when target is None."""
            result = validator.validate_reference(
                source_id="ABC123",
                target_id=None,
                source_field="patient_id",
                target_field="patient.id",
            )
            assert result.valid is True

        def test_both_none_valid(self, validator):
            """Test validation passes when both are None."""
            result = validator.validate_reference(
                source_id=None,
                target_id=None,
                source_field="patient_id",
                target_field="patient.id",
            )
            assert result.valid is True

    # validate_required_reference tests
    class TestValidateRequiredReference:
        """Tests for validate_required_reference method."""

        @pytest.fixture
        def validator(self):
            return ReferentialIntegrityValidator()

        def test_present_reference_valid(self, validator):
            """Test validation passes when reference is present."""
            result = validator.validate_required_reference(
                reference_id="ABC123",
                field_name="patient_id",
            )
            assert result.valid is True

        def test_none_reference_invalid(self, validator):
            """Test validation fails when reference is None."""
            result = validator.validate_required_reference(
                reference_id=None,
                field_name="patient_id",
            )
            assert result.valid is False
            assert any("REF_002" in i.code for i in result.issues)

        def test_empty_reference_invalid(self, validator):
            """Test validation fails when reference is empty string."""
            result = validator.validate_required_reference(
                reference_id="",
                field_name="patient_id",
            )
            assert result.valid is False
            assert any("REF_002" in i.code for i in result.issues)

    # validate_unique_ids tests
    class TestValidateUniqueIds:
        """Tests for validate_unique_ids method."""

        @pytest.fixture
        def validator(self):
            return ReferentialIntegrityValidator()

        def test_unique_ids_valid(self, validator):
            """Test validation passes with unique IDs."""
            items = [
                MockEntity(id="001", name="First"),
                MockEntity(id="002", name="Second"),
                MockEntity(id="003", name="Third"),
            ]
            result = validator.validate_unique_ids(items)
            assert result.valid is True

        def test_duplicate_ids_invalid(self, validator):
            """Test validation fails with duplicate IDs."""
            items = [
                MockEntity(id="001", name="First"),
                MockEntity(id="002", name="Second"),
                MockEntity(id="001", name="Duplicate"),  # duplicate
            ]
            result = validator.validate_unique_ids(items)
            assert result.valid is False
            assert any("REF_004" in i.code for i in result.issues)

        def test_empty_list_valid(self, validator):
            """Test validation passes with empty list."""
            result = validator.validate_unique_ids([])
            assert result.valid is True

        def test_custom_id_getter(self, validator):
            """Test validation with custom ID getter function."""
            items = [
                MockEntity(id="001", name="First"),
                MockEntity(id="002", name="Second"),
            ]
            result = validator.validate_unique_ids(
                items,
                get_id=lambda x: x.name,  # Use name as ID
            )
            assert result.valid is True

        def test_custom_id_getter_duplicate(self, validator):
            """Test validation with custom ID getter detecting duplicates."""
            items = [
                MockEntity(id="001", name="Same"),
                MockEntity(id="002", name="Same"),  # duplicate name
            ]
            result = validator.validate_unique_ids(
                items,
                get_id=lambda x: x.name,
            )
            assert result.valid is False

    # validate_foreign_key tests
    class TestValidateForeignKey:
        """Tests for validate_foreign_key method."""

        @pytest.fixture
        def validator(self):
            return ReferentialIntegrityValidator()

        @pytest.fixture
        def valid_ids(self):
            return {"001", "002", "003"}

        def test_valid_foreign_key(self, validator, valid_ids):
            """Test validation passes with valid foreign key."""
            result = validator.validate_foreign_key(
                reference_id="001",
                valid_ids=valid_ids,
                field_name="patient_id",
            )
            assert result.valid is True

        def test_invalid_foreign_key(self, validator, valid_ids):
            """Test validation fails with invalid foreign key."""
            result = validator.validate_foreign_key(
                reference_id="999",
                valid_ids=valid_ids,
                field_name="patient_id",
            )
            assert result.valid is False
            assert any("REF_006" in i.code for i in result.issues)

        def test_none_allowed_by_default(self, validator, valid_ids):
            """Test that None is allowed by default."""
            result = validator.validate_foreign_key(
                reference_id=None,
                valid_ids=valid_ids,
                field_name="patient_id",
            )
            assert result.valid is True

        def test_none_not_allowed(self, validator, valid_ids):
            """Test validation fails when None is not allowed."""
            result = validator.validate_foreign_key(
                reference_id=None,
                valid_ids=valid_ids,
                field_name="patient_id",
                allow_none=False,
            )
            assert result.valid is False
            assert any("REF_005" in i.code for i in result.issues)

        def test_empty_valid_ids_always_invalid(self, validator):
            """Test that any reference fails with empty valid_ids."""
            result = validator.validate_foreign_key(
                reference_id="001",
                valid_ids=set(),
                field_name="patient_id",
            )
            assert result.valid is False


class TestIntegration:
    """Integration tests for structural validation."""

    def test_validate_entity_graph(self):
        """Test validating a graph of related entities."""
        validator = ReferentialIntegrityValidator()
        
        # Create parent entities
        parents = [
            MockEntity(id="P001", name="Parent 1"),
            MockEntity(id="P002", name="Parent 2"),
        ]
        
        # Create child entities referencing parents
        children = [
            MockEntity(id="C001", name="Child 1", parent_id="P001"),
            MockEntity(id="C002", name="Child 2", parent_id="P002"),
            MockEntity(id="C003", name="Orphan", parent_id="P999"),  # invalid ref
        ]
        
        # Validate unique IDs for parents
        parent_result = validator.validate_unique_ids(parents)
        assert parent_result.valid is True
        
        # Build valid parent ID set
        valid_parent_ids = {p.id for p in parents}
        
        # Validate children foreign keys
        all_valid = True
        for child in children:
            result = validator.validate_foreign_key(
                reference_id=child.parent_id,
                valid_ids=valid_parent_ids,
                field_name="parent_id",
            )
            if not result.valid:
                all_valid = False
        
        assert all_valid is False  # One child has invalid parent


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
