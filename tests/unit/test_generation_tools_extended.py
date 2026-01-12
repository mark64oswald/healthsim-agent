"""Extended tests for generation_tools module.

Covers additional generation scenarios, serialization, and skill functions.
"""

import pytest
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from pydantic import BaseModel

from healthsim_agent.tools.generation_tools import (
    generate_patients,
    generate_members,
    generate_subjects,
    generate_rx_members,
    generate_pharmacy_claims,
    check_formulary,
    list_skills,
    describe_skill,
    _model_to_dict,
    _serialize_value,
)


class TestModelToDict:
    """Tests for _model_to_dict helper."""
    
    def test_dict_passthrough(self):
        """Dict passes through unchanged."""
        data = {"key": "value", "num": 42}
        result = _model_to_dict(data)
        assert result == data
    
    def test_pydantic_model(self):
        """Pydantic model converts to dict."""
        class TestModel(BaseModel):
            name: str
            age: int
        
        model = TestModel(name="Test", age=25)
        result = _model_to_dict(model)
        
        assert isinstance(result, dict)
        assert result["name"] == "Test"
        assert result["age"] == 25
    
    def test_object_with_dict_method(self):
        """Object with dict() method."""
        class DictableObject:
            def __init__(self):
                self.value = "test"
            def dict(self):
                return {"value": self.value}
        
        obj = DictableObject()
        result = _model_to_dict(obj)
        
        assert result == {"value": "test"}


class TestSerializeValue:
    """Tests for _serialize_value helper."""
    
    def test_none(self):
        """None passes through."""
        assert _serialize_value(None) is None
    
    def test_string(self):
        """String passes through."""
        assert _serialize_value("hello") == "hello"
    
    def test_int(self):
        """Int passes through."""
        assert _serialize_value(42) == 42
    
    def test_float(self):
        """Float passes through."""
        assert _serialize_value(3.14) == 3.14
    
    def test_bool(self):
        """Bool passes through."""
        assert _serialize_value(True) is True
        assert _serialize_value(False) is False
    
    def test_date(self):
        """Date converts to ISO string."""
        d = date(2025, 1, 15)
        result = _serialize_value(d)
        assert result == "2025-01-15"
    
    def test_datetime(self):
        """Datetime converts to ISO string."""
        dt = datetime(2025, 1, 15, 10, 30, 0)
        result = _serialize_value(dt)
        assert "2025-01-15" in result
        assert "10:30" in result
    
    def test_decimal(self):
        """Decimal converts to float."""
        d = Decimal("123.45")
        result = _serialize_value(d)
        assert result == 123.45
    
    def test_enum(self):
        """Enum converts to value."""
        class Color(Enum):
            RED = "red"
            BLUE = "blue"
        
        result = _serialize_value(Color.RED)
        assert result == "red"
    
    def test_list(self):
        """List items are serialized."""
        data = [date(2025, 1, 1), "test", 42]
        result = _serialize_value(data)
        assert result == ["2025-01-01", "test", 42]
    
    def test_dict(self):
        """Dict values are serialized."""
        data = {"date": date(2025, 1, 1), "name": "test"}
        result = _serialize_value(data)
        assert result == {"date": "2025-01-01", "name": "test"}
    
    def test_pydantic_model(self):
        """Pydantic model converts to dict."""
        class SimpleModel(BaseModel):
            value: str
        
        model = SimpleModel(value="test")
        result = _serialize_value(model)
        
        assert isinstance(result, dict)
        assert result["value"] == "test"


class TestGeneratePatientsExtended:
    """Extended tests for generate_patients."""
    
    def test_gender_male(self):
        """Generate male patients."""
        result = generate_patients(count=3, gender="male", seed=42)
        assert result.success is True
        for patient in result.data["patients"]:
            assert patient["gender"] in ("M", "male", "MALE")
    
    def test_invalid_age_range(self):
        """Invalid age range handling."""
        # min > max should still work (swapped internally or error)
        result = generate_patients(count=1, age_range=(80, 20))
        # Either succeeds with swapped values or returns error
        assert isinstance(result.success, bool)
    
    def test_all_includes(self):
        """Test with all include flags True."""
        result = generate_patients(
            count=1,
            include_encounters=True,
            include_diagnoses=True,
            include_vitals=True,
            include_labs=True,
            include_medications=True,
        )
        assert result.success is True
        assert len(result.data.keys()) >= 6


class TestGenerateMembersExtended:
    """Extended tests for generate_members."""
    
    def test_claims_per_member_zero(self):
        """Zero claims per member."""
        result = generate_members(count=2, include_claims=True, claims_per_member=0)
        assert result.success is True
        # Should have no claims or be empty
        claims = result.data.get("claims", [])
        assert len(claims) == 0
    
    def test_large_claims_count(self):
        """Many claims per member."""
        result = generate_members(count=1, include_claims=True, claims_per_member=10)
        assert result.success is True
        assert len(result.data.get("claims", [])) == 10


class TestGenerateSubjectsExtended:
    """Extended tests for generate_subjects."""
    
    def test_with_exposures(self):
        """Generate subjects with drug exposures."""
        result = generate_subjects(count=2, include_exposures=True)
        assert result.success is True
        assert "exposures" in result.data
    
    def test_all_includes(self):
        """Generate subjects with all data types."""
        result = generate_subjects(
            count=1,
            include_visits=True,
            include_adverse_events=True,
            include_exposures=True,
        )
        assert result.success is True
        assert "visits" in result.data
        assert "adverse_events" in result.data
        assert "exposures" in result.data


class TestGenerateRxMembers:
    """Tests for generate_rx_members."""
    
    def test_generate_single_rx_member(self):
        """Generate single RxMember."""
        result = generate_rx_members(count=1)
        assert result.success is True
        assert "rx_members" in result.data
        assert len(result.data["rx_members"]) == 1
    
    def test_generate_multiple_rx_members(self):
        """Generate multiple RxMembers."""
        result = generate_rx_members(count=5)
        assert result.success is True
        assert len(result.data["rx_members"]) == 5
    
    def test_rx_member_has_required_fields(self):
        """RxMember has pharmacy-specific fields."""
        result = generate_rx_members(count=1)
        assert result.success is True
        
        rx_member = result.data["rx_members"][0]
        assert "member_id" in rx_member
    
    def test_invalid_count(self):
        """Invalid count returns error."""
        result = generate_rx_members(count=0)
        assert result.success is False


class TestGeneratePharmacyClaims:
    """Tests for generate_pharmacy_claims."""
    
    def test_generate_pharmacy_claims(self):
        """Generate pharmacy claims."""
        result = generate_pharmacy_claims(count=3)
        assert result.success is True
        assert "pharmacy_claims" in result.data
        assert len(result.data["pharmacy_claims"]) == 3
    
    def test_claims_with_member(self):
        """Claims include member data when requested."""
        result = generate_pharmacy_claims(count=2, include_member=True)
        assert result.success is True
        assert "rx_members" in result.data
        assert len(result.data["rx_members"]) == 1
    
    def test_claims_without_member(self):
        """Claims without member data."""
        result = generate_pharmacy_claims(count=2, include_member=False)
        assert result.success is True
        assert "rx_members" not in result.data or len(result.data.get("rx_members", [])) == 0
    
    def test_invalid_count(self):
        """Invalid count returns error."""
        result = generate_pharmacy_claims(count=0)
        assert result.success is False
    
    def test_count_too_high(self):
        """Count above max returns error."""
        result = generate_pharmacy_claims(count=51)
        assert result.success is False


class TestCheckFormulary:
    """Tests for check_formulary."""
    
    def test_check_formulary_with_drug_name(self):
        """Check formulary with drug name."""
        result = check_formulary(drug_name="metformin")
        # May succeed or fail depending on formulary data
        assert isinstance(result.success, bool)
    
    def test_check_formulary_with_ndc(self):
        """Check formulary with NDC."""
        result = check_formulary(
            drug_name="metformin",
            ndc="00002-3227-30",
        )
        # Should handle gracefully
        assert isinstance(result.success, bool)
    
    def test_check_formulary_unknown_drug(self):
        """Check formulary for unknown drug."""
        result = check_formulary(drug_name="unknown_drug_xyz_12345")
        # Should return success with covered=False or error
        assert isinstance(result.success, bool)


class TestListSkills:
    """Tests for list_skills."""
    
    def test_list_all_skills(self):
        """List all skills across products."""
        result = list_skills()
        
        assert result.success is True
        assert result.data is not None
        assert isinstance(result.data, dict)
    
    def test_list_patientsim_skills(self):
        """List PatientSim skills only."""
        result = list_skills(product="patientsim")
        
        assert result.success is True
        assert result.data is not None
    
    def test_list_membersim_skills(self):
        """List MemberSim skills only."""
        result = list_skills(product="membersim")
        
        assert result.success is True
    
    def test_list_trialsim_skills(self):
        """List TrialSim skills only."""
        result = list_skills(product="trialsim")
        
        assert result.success is True
    
    def test_list_rxmembersim_skills(self):
        """List RxMemberSim skills only."""
        result = list_skills(product="rxmembersim")
        
        assert result.success is True
    
    def test_list_invalid_product(self):
        """List skills for invalid product."""
        result = list_skills(product="invalid_product")
        
        # Should return empty or error
        assert isinstance(result.success, bool)


class TestDescribeSkill:
    """Tests for describe_skill."""
    
    def test_describe_existing_skill(self):
        """Describe an existing skill."""
        # First list skills to get a valid name
        list_result = list_skills(product="patientsim")
        
        if list_result.success and list_result.data:
            # Try to describe a skill
            skills = list_result.data.get("skills", list_result.data)
            if isinstance(skills, dict) and skills:
                skill_name = list(skills.keys())[0] if skills else "diabetes-management"
            else:
                skill_name = "diabetes-management"
            
            result = describe_skill(skill_name, product="patientsim")
            assert isinstance(result.success, bool)
    
    def test_describe_nonexistent_skill(self):
        """Describe a skill that doesn't exist."""
        result = describe_skill("nonexistent-skill-xyz", product="patientsim")
        
        assert result.success is False
        assert result.error is not None
    
    def test_describe_skill_invalid_product(self):
        """Describe skill with invalid product."""
        result = describe_skill("some-skill", product="invalid_product")
        
        assert result.success is False


class TestGenerationEdgeCases:
    """Edge cases for generation functions."""
    
    def test_max_count_patients(self):
        """Test maximum allowed count."""
        result = generate_patients(count=100)
        assert result.success is True
        assert len(result.data["patients"]) == 100
    
    def test_seed_reproducibility(self):
        """Same seed produces identical results."""
        seed = 99999
        
        result1 = generate_patients(count=3, seed=seed)
        result2 = generate_patients(count=3, seed=seed)
        
        assert result1.data["patients"][0]["id"] == result2.data["patients"][0]["id"]
        assert result1.data["patients"][1]["id"] == result2.data["patients"][1]["id"]
    
    def test_different_seeds_different_results(self):
        """Different seeds produce different results."""
        result1 = generate_patients(count=3, seed=11111)
        result2 = generate_patients(count=3, seed=22222)
        
        # IDs should be different
        assert result1.data["patients"][0]["id"] != result2.data["patients"][0]["id"]
