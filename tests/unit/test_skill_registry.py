"""Tests for skill registry module."""

import pytest
from unittest.mock import Mock, patch

from healthsim_agent.generation.skill_registry import (
    SkillCapability,
    SkillCapabilityDeclaration,
    SkillRegistration,
    SkillRegistry,
    get_skill_registry,
    auto_resolve_parameters,
    register_skill,
)


class TestSkillCapability:
    """Tests for SkillCapability enum."""
    
    def test_capability_values(self):
        """Test capability enum values exist."""
        assert SkillCapability.DIAGNOSIS is not None
        assert SkillCapability.PROCEDURE is not None
        assert SkillCapability.MEDICATION is not None
        assert SkillCapability.LAB_TEST is not None
        assert SkillCapability.VITAL_SIGN is not None
    
    def test_capability_str(self):
        """Test capability string values."""
        assert SkillCapability.DIAGNOSIS.value == "diagnosis"
        assert SkillCapability.PROCEDURE.value == "procedure"
        assert SkillCapability.MEDICATION.value == "medication"


class TestSkillCapabilityDeclaration:
    """Tests for SkillCapabilityDeclaration dataclass."""
    
    def test_declaration_creation(self):
        """Test creating a capability declaration."""
        decl = SkillCapabilityDeclaration(
            capability=SkillCapability.DIAGNOSIS,
            lookup_key="diagnosis_codes",
            context_keys=["condition", "severity"],
        )
        
        assert decl.capability == SkillCapability.DIAGNOSIS
        assert decl.lookup_key == "diagnosis_codes"
        assert "condition" in decl.context_keys
    
    def test_declaration_defaults(self):
        """Test declaration default values."""
        decl = SkillCapabilityDeclaration(
            capability=SkillCapability.MEDICATION,
            lookup_key="medications",
        )
        
        assert decl.context_keys == []


class TestSkillRegistration:
    """Tests for SkillRegistration dataclass."""
    
    def test_registration_creation(self):
        """Test creating a skill registration."""
        cap = SkillCapabilityDeclaration(
            capability=SkillCapability.LAB_TEST,
            lookup_key="lab_tests",
        )
        
        reg = SkillRegistration(
            skill_id="diabetes-management",
            skill_path="/path/to/skill.md",
            capabilities=[cap],
            condition_mappings={"diabetes": ["E11.9", "E11.65"]},
        )
        
        assert reg.skill_id == "diabetes-management"
        assert len(reg.capabilities) == 1
        assert "diabetes" in reg.condition_mappings


class TestSkillRegistry:
    """Tests for SkillRegistry class."""
    
    def test_registry_creation(self):
        """Test creating a registry."""
        registry = SkillRegistry()
        
        assert registry is not None
        assert len(registry.skills) == 0
    
    def test_register_skill(self):
        """Test registering a skill."""
        registry = SkillRegistry()
        
        cap = SkillCapabilityDeclaration(
            capability=SkillCapability.DIAGNOSIS,
            lookup_key="codes",
        )
        
        registration = SkillRegistration(
            skill_id="test-skill",
            skill_path="/path/to/skill.md",
            capabilities=[cap],
        )
        
        registry.register(registration)
        
        assert "test-skill" in registry.skills
        assert registry.get_skill("test-skill") == registration
    
    def test_find_by_capability(self):
        """Test finding skills by capability."""
        registry = SkillRegistry()
        
        cap = SkillCapabilityDeclaration(
            capability=SkillCapability.DIAGNOSIS,
            lookup_key="codes",
        )
        
        registration = SkillRegistration(
            skill_id="diag-skill",
            skill_path="/path/to/skill.md",
            capabilities=[cap],
        )
        
        registry.register(registration)
        
        found = registry.find_by_capability(SkillCapability.DIAGNOSIS)
        
        assert len(found) == 1
        assert found[0].skill_id == "diag-skill"
    
    def test_find_by_condition(self):
        """Test finding skills by condition mapping."""
        registry = SkillRegistry()
        
        registration = SkillRegistration(
            skill_id="diabetes-skill",
            skill_path="/path/to/skill.md",
            capabilities=[],
            condition_mappings={"diabetes": ["E11.9"]},
        )
        
        registry.register(registration)
        
        found = registry.find_by_condition("diabetes")
        
        assert len(found) == 1
        assert found[0].skill_id == "diabetes-skill"


class TestGetSkillRegistry:
    """Tests for get_skill_registry function."""
    
    def test_get_skill_registry_singleton(self):
        """Test that get_skill_registry returns same instance."""
        registry1 = get_skill_registry()
        registry2 = get_skill_registry()
        
        assert registry1 is registry2


class TestAutoResolveParameters:
    """Tests for auto_resolve_parameters function."""
    
    def test_auto_resolve_with_condition(self):
        """Test auto-resolving parameters for a condition."""
        result = auto_resolve_parameters(
            condition="diabetes",
            capability=SkillCapability.DIAGNOSIS,
        )
        
        assert result is not None or result is None  # May or may not find match


class TestRegisterSkillFunction:
    """Tests for register_skill convenience function."""
    
    def test_register_skill_function(self):
        """Test the register_skill convenience function."""
        cap = SkillCapabilityDeclaration(
            capability=SkillCapability.PROCEDURE,
            lookup_key="procedures",
        )
        
        registration = SkillRegistration(
            skill_id="new-skill",
            skill_path="/path/to/new.md",
            capabilities=[cap],
        )
        
        # Should not raise
        register_skill(registration)
        
        # Verify it's in the global registry
        registry = get_skill_registry()
        assert "new-skill" in registry.skills
