"""Tests for healthsim_agent.tools.base module."""

import pytest
import json

from healthsim_agent.tools.base import (
    ToolResult,
    ok,
    err,
    validate_entity_types,
    normalize_entity_type,
    SCENARIO_ENTITY_TYPES,
    RELATIONSHIP_ENTITY_TYPES,
    REFERENCE_ENTITY_TYPES,
    ALLOWED_ENTITY_TYPES,
)


class TestToolResult:
    """Tests for ToolResult dataclass."""
    
    def test_successful_result(self):
        """Test creating a successful result."""
        result = ToolResult(success=True, data={"key": "value"})
        assert result.success is True
        assert result.data == {"key": "value"}
        assert result.error is None
    
    def test_error_result(self):
        """Test creating an error result."""
        result = ToolResult(success=False, error="Something went wrong")
        assert result.success is False
        assert result.error == "Something went wrong"
        assert result.data is None
    
    def test_result_with_metadata(self):
        """Test result with metadata."""
        result = ToolResult(
            success=True, 
            data=[1, 2, 3],
            metadata={"count": 3, "source": "test"}
        )
        assert result.metadata == {"count": 3, "source": "test"}
    
    def test_to_json_success(self):
        """Test JSON serialization of success result."""
        result = ToolResult(success=True, data={"name": "test"})
        json_str = result.to_json()
        parsed = json.loads(json_str)
        
        assert parsed["status"] == "success"
        assert parsed["data"] == {"name": "test"}
        assert "error" not in parsed
    
    def test_to_json_error(self):
        """Test JSON serialization of error result."""
        result = ToolResult(success=False, error="Test error")
        json_str = result.to_json()
        parsed = json.loads(json_str)
        
        assert parsed["status"] == "error"
        assert parsed["error"] == "Test error"
        assert "data" not in parsed
    
    def test_to_json_with_metadata(self):
        """Test JSON serialization includes metadata."""
        result = ToolResult(
            success=True, 
            data={},
            metadata={"count": 10}
        )
        json_str = result.to_json()
        parsed = json.loads(json_str)
        
        assert parsed["metadata"] == {"count": 10}
    
    def test_to_dict(self):
        """Test dictionary conversion."""
        result = ToolResult(
            success=True,
            data={"x": 1},
            metadata={"y": 2}
        )
        d = result.to_dict()
        
        assert d["success"] is True
        assert d["data"] == {"x": 1}
        assert d["metadata"] == {"y": 2}
        assert d["error"] is None
    
    def test_bool_success(self):
        """Test boolean evaluation for success."""
        result = ToolResult(success=True)
        assert bool(result) is True
        assert result  # Implicit bool check
    
    def test_bool_failure(self):
        """Test boolean evaluation for failure."""
        result = ToolResult(success=False, error="error")
        assert bool(result) is False
        assert not result  # Implicit bool check


class TestOkErr:
    """Tests for ok() and err() helper functions."""
    
    def test_ok_with_data(self):
        """Test ok() creates successful result with data."""
        result = ok({"cohort_id": "123"})
        assert result.success is True
        assert result.data == {"cohort_id": "123"}
        assert result.error is None
    
    def test_ok_with_metadata(self):
        """Test ok() accepts keyword metadata."""
        result = ok(["a", "b"], count=2, source="test")
        assert result.metadata == {"count": 2, "source": "test"}
    
    def test_ok_no_data(self):
        """Test ok() without data."""
        result = ok()
        assert result.success is True
        assert result.data is None
    
    def test_err_with_message(self):
        """Test err() creates error result."""
        result = err("Not found")
        assert result.success is False
        assert result.error == "Not found"
        assert result.data is None
    
    def test_err_with_metadata(self):
        """Test err() accepts keyword metadata."""
        result = err("Invalid input", field="name", code=400)
        assert result.metadata == {"field": "name", "code": 400}


class TestNormalizeEntityType:
    """Tests for normalize_entity_type function."""
    
    def test_lowercase(self):
        """Test converts to lowercase."""
        assert normalize_entity_type("Patient") == "patients"
        assert normalize_entity_type("MEMBER") == "members"
    
    def test_pluralize(self):
        """Test adds 's' if not present."""
        assert normalize_entity_type("patient") == "patients"
        assert normalize_entity_type("claim") == "claims"
    
    def test_already_plural(self):
        """Test doesn't double-pluralize."""
        assert normalize_entity_type("patients") == "patients"
        assert normalize_entity_type("claims") == "claims"


class TestValidateEntityTypes:
    """Tests for validate_entity_types function."""
    
    def test_valid_scenario_types(self):
        """Test valid scenario entity types pass validation."""
        entities = {
            "patients": [{"id": 1}],
            "members": [{"id": 2}],
            "claims": [{"id": 3}],
        }
        assert validate_entity_types(entities) is None
    
    def test_valid_relationship_types(self):
        """Test valid relationship entity types pass validation."""
        entities = {
            "pcp_assignments": [{"member_id": 1, "provider_npi": "123"}],
        }
        assert validate_entity_types(entities) is None
    
    def test_reference_type_rejected_by_default(self):
        """Test reference types are rejected without override."""
        entities = {"providers": [{"npi": "123"}]}
        error = validate_entity_types(entities)
        assert error is not None
        assert "REFERENCE DATA" in error
        assert "providers" in error
    
    def test_reference_type_allowed_with_override(self):
        """Test reference types allowed with allow_reference=True."""
        entities = {"providers": [{"npi": "123"}]}
        assert validate_entity_types(entities, allow_reference=True) is None
    
    def test_unknown_type_rejected(self):
        """Test unknown entity types are rejected."""
        entities = {"unknown_things": [{"id": 1}]}
        error = validate_entity_types(entities)
        assert error is not None
        assert "Unknown entity type" in error
    
    def test_normalizes_type_names(self):
        """Test entity type names are normalized during validation."""
        # Singular should be accepted (normalized to plural)
        entities = {"patient": [{"id": 1}]}
        assert validate_entity_types(entities) is None
        
        # Mixed case should be accepted
        entities = {"Patients": [{"id": 1}]}
        assert validate_entity_types(entities) is None


class TestEntityTypeSets:
    """Tests for entity type set constants."""
    
    def test_scenario_types_defined(self):
        """Test scenario entity types are defined."""
        assert "patients" in SCENARIO_ENTITY_TYPES
        assert "members" in SCENARIO_ENTITY_TYPES
        assert "claims" in SCENARIO_ENTITY_TYPES
        assert "subjects" in SCENARIO_ENTITY_TYPES
    
    def test_relationship_types_defined(self):
        """Test relationship entity types are defined."""
        assert "pcp_assignments" in RELATIONSHIP_ENTITY_TYPES
        assert "network_contracts" in RELATIONSHIP_ENTITY_TYPES
    
    def test_reference_types_defined(self):
        """Test reference entity types are defined."""
        assert "providers" in REFERENCE_ENTITY_TYPES
        assert "facilities" in REFERENCE_ENTITY_TYPES
    
    def test_allowed_types_is_union(self):
        """Test ALLOWED_ENTITY_TYPES is union of scenario + relationship."""
        assert ALLOWED_ENTITY_TYPES == SCENARIO_ENTITY_TYPES | RELATIONSHIP_ENTITY_TYPES
    
    def test_no_overlap_scenario_reference(self):
        """Test scenario and reference types don't overlap."""
        assert SCENARIO_ENTITY_TYPES.isdisjoint(REFERENCE_ENTITY_TYPES)
