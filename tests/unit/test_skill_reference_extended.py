"""Extended tests for generation/skill_reference module."""

import pytest
from pathlib import Path


class TestGetSkillsRoot:
    """Tests for get_skills_root function."""
    
    def test_returns_path(self):
        """Test returns a Path object."""
        from healthsim_agent.generation.skill_reference import get_skills_root
        
        result = get_skills_root()
        assert isinstance(result, Path)
    
    def test_path_exists(self):
        """Test returned path exists."""
        from healthsim_agent.generation.skill_reference import get_skills_root
        
        result = get_skills_root()
        assert result.exists()


class TestGetParameterResolver:
    """Tests for get_parameter_resolver function."""
    
    def test_returns_resolver(self):
        """Test returns a ParameterResolver."""
        from healthsim_agent.generation.skill_reference import get_parameter_resolver
        
        result = get_parameter_resolver()
        assert result is not None
    
    def test_resolver_singleton(self):
        """Test returns same resolver instance."""
        from healthsim_agent.generation.skill_reference import get_parameter_resolver
        
        r1 = get_parameter_resolver()
        r2 = get_parameter_resolver()
        assert r1 is r2


class TestGetSkillResolver:
    """Tests for get_skill_resolver function."""
    
    def test_returns_resolver(self):
        """Test returns a SkillResolver."""
        from healthsim_agent.generation.skill_reference import get_skill_resolver
        
        result = get_skill_resolver()
        assert result is not None
    
    def test_resolver_singleton(self):
        """Test returns same resolver instance."""
        from healthsim_agent.generation.skill_reference import get_skill_resolver
        
        r1 = get_skill_resolver()
        r2 = get_skill_resolver()
        assert r1 is r2


class TestResolveSkillRef:
    """Tests for resolve_skill_ref function."""
    
    def test_resolve_basic(self):
        """Test basic skill resolution."""
        from healthsim_agent.generation.skill_reference import resolve_skill_ref
        
        result = resolve_skill_ref("patientsim", "condition.diabetes")
        assert result is not None
    
    def test_resolve_with_context(self):
        """Test resolution with context."""
        from healthsim_agent.generation.skill_reference import resolve_skill_ref
        
        context = {"severity": "moderate"}
        result = resolve_skill_ref("patientsim", "condition.diabetes", context=context)
        assert result is not None
    
    def test_resolve_unknown_skill(self):
        """Test resolving unknown skill."""
        from healthsim_agent.generation.skill_reference import resolve_skill_ref
        
        result = resolve_skill_ref("unknown_product", "unknown.lookup")
        assert isinstance(result, dict)


class TestSkillLoader:
    """Tests for SkillLoader class."""
    
    def test_create_loader(self):
        """Test creating a SkillLoader."""
        from healthsim_agent.generation.skill_reference import SkillLoader
        
        loader = SkillLoader()
        assert loader is not None


class TestParsedSkill:
    """Tests for ParsedSkill model."""
    
    def test_parsed_skill_exists(self):
        """Test ParsedSkill can be imported."""
        from healthsim_agent.generation.skill_reference import ParsedSkill
        
        assert ParsedSkill is not None


class TestSkillReference:
    """Tests for SkillReference model."""
    
    def test_create_reference(self):
        """Test creating a SkillReference."""
        from healthsim_agent.generation.skill_reference import SkillReference
        
        ref = SkillReference(
            skill="patientsim",
            lookup="condition.diabetes"
        )
        assert ref.skill == "patientsim"
        assert ref.lookup == "condition.diabetes"


class TestResolvedParameters:
    """Tests for ResolvedParameters model."""
    
    def test_create_resolved(self):
        """Test creating ResolvedParameters."""
        from healthsim_agent.generation.skill_reference import ResolvedParameters
        
        params = ResolvedParameters(parameters={"key": "value"})
        assert params.parameters["key"] == "value"


class TestParameterResolver:
    """Tests for ParameterResolver class."""
    
    def test_resolver_instance(self):
        """Test ParameterResolver instance."""
        from healthsim_agent.generation.skill_reference import ParameterResolver
        
        resolver = ParameterResolver()
        assert resolver is not None


class TestSkillResolver:
    """Tests for SkillResolver class."""
    
    def test_resolver_instance(self):
        """Test SkillResolver instance."""
        from healthsim_agent.generation.skill_reference import SkillResolver
        
        resolver = SkillResolver()
        assert resolver is not None
