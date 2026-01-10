"""Unit tests for skill loader."""
import pytest
from pathlib import Path
from healthsim_agent.skills.loader import SkillLoader
from healthsim_agent.skills.models import ParsedSkill, SkillMetadata, EmbeddedConfig


class TestSkillMetadata:
    """Tests for SkillMetadata parsing."""
    
    def test_from_frontmatter_basic(self):
        """Test basic frontmatter parsing."""
        data = {
            "name": "test-skill",
            "description": "A test skill"
        }
        
        metadata = SkillMetadata.from_frontmatter(data)
        
        assert metadata.name == "test-skill"
        assert metadata.description == "A test skill"
        assert metadata.triggers == []
    
    def test_from_frontmatter_with_triggers_in_description(self):
        """Test parsing triggers from description."""
        data = {
            "name": "diabetes-skill",
            "description": "Diabetes management. Triggers: diabetes, diabetic, A1C"
        }
        
        metadata = SkillMetadata.from_frontmatter(data)
        
        assert metadata.name == "diabetes-skill"
        assert "diabetes" in metadata.triggers
        assert "diabetic" in metadata.triggers
        assert "A1C" in metadata.triggers
    
    def test_from_frontmatter_with_explicit_trigger_phrases(self):
        """Test parsing explicit trigger_phrases list."""
        data = {
            "name": "test-skill",
            "description": "A test",
            "trigger_phrases": ["alpha", "beta", "gamma"]
        }
        
        metadata = SkillMetadata.from_frontmatter(data)
        
        assert metadata.triggers == ["alpha", "beta", "gamma"]
    
    def test_from_frontmatter_explicit_overrides_description(self):
        """Test that explicit trigger_phrases takes precedence."""
        data = {
            "name": "test-skill",
            "description": "A test. Triggers: should, be, ignored",
            "trigger_phrases": ["explicit", "triggers"]
        }
        
        metadata = SkillMetadata.from_frontmatter(data)
        
        assert metadata.triggers == ["explicit", "triggers"]
        assert "should" not in metadata.triggers


class TestParsedSkill:
    """Tests for ParsedSkill dataclass."""
    
    def test_product_from_path(self):
        """Test extracting product from skill path."""
        skill = ParsedSkill(
            path=Path("/app/skills/patientsim/diabetes.md"),
            metadata=SkillMetadata(name="test", description="test"),
            markdown_content="# Test"
        )
        
        assert skill.product == "patientsim"
    
    def test_product_from_nested_path(self):
        """Test extracting product from nested skill path."""
        skill = ParsedSkill(
            path=Path("/app/skills/trialsim/domains/ae.md"),
            metadata=SkillMetadata(name="test", description="test"),
            markdown_content="# Test"
        )
        
        assert skill.product == "trialsim"
    
    def test_product_fallback_to_common(self):
        """Test product fallback when skills not in path."""
        skill = ParsedSkill(
            path=Path("/some/other/path/test.md"),
            metadata=SkillMetadata(name="test", description="test"),
            markdown_content="# Test"
        )
        
        assert skill.product == "common"
    
    def test_is_product_skill(self):
        """Test detection of SKILL.md files."""
        product_skill = ParsedSkill(
            path=Path("/app/skills/patientsim/SKILL.md"),
            metadata=SkillMetadata(name="test", description="test"),
            markdown_content="# Test"
        )
        
        regular_skill = ParsedSkill(
            path=Path("/app/skills/patientsim/diabetes.md"),
            metadata=SkillMetadata(name="test", description="test"),
            markdown_content="# Test"
        )
        
        assert product_skill.is_product_skill is True
        assert regular_skill.is_product_skill is False
    
    def test_triggers_property(self):
        """Test triggers property delegates to metadata."""
        skill = ParsedSkill(
            path=Path("/app/skills/test.md"),
            metadata=SkillMetadata(
                name="test", 
                description="test",
                triggers=["alpha", "beta"]
            ),
            markdown_content="# Test"
        )
        
        assert skill.triggers == ["alpha", "beta"]


class TestSkillLoader:
    """Tests for SkillLoader."""
    
    @pytest.fixture
    def loader(self):
        """Create loader pointing to actual skills directory."""
        return SkillLoader()
    
    @pytest.fixture
    def sample_skill_content(self) -> str:
        """Sample skill markdown for testing parsing."""
        return '''---
name: test-skill
description: "A test skill for diabetes. Triggers: diabetes, diabetic, T2DM"
---

# Test Skill

## Overview

This is a test skill for parsing.

## Generation Parameters

```yaml
name: Test Diabetes
trigger_phrases:
  - diabetes
  - diabetic

icd10_codes:
  primary: [E11.9, E11.65]
  
prevalence:
  base_rate: 0.10
```

## Example Output

```json
{
  "patient": {
    "name": "Test Patient"
  }
}
```
'''
    
    def test_loader_initializes(self, loader):
        """Test loader initializes with correct path."""
        assert loader.skills_dir is not None
    
    def test_parse_frontmatter(self, loader, sample_skill_content):
        """Test YAML frontmatter parsing."""
        metadata = loader._parse_frontmatter(sample_skill_content)
        
        assert metadata is not None
        assert metadata.name == "test-skill"
        assert "diabetes" in metadata.description.lower()
    
    def test_parse_frontmatter_extracts_triggers(self, loader, sample_skill_content):
        """Test trigger extraction from frontmatter description."""
        metadata = loader._parse_frontmatter(sample_skill_content)
        
        assert len(metadata.triggers) > 0
        assert "diabetes" in metadata.triggers
    
    def test_parse_frontmatter_returns_none_for_invalid(self, loader):
        """Test that invalid content returns None."""
        invalid_content = "# No frontmatter here\n\nJust markdown."
        
        metadata = loader._parse_frontmatter(invalid_content)
        
        assert metadata is None
    
    def test_extract_embedded_configs(self, loader, sample_skill_content):
        """Test embedded YAML/JSON extraction."""
        configs = loader._extract_embedded_configs(sample_skill_content)
        
        assert len(configs) >= 1
        
        # Find the YAML config
        yaml_configs = [c for c in configs if c.block_type == "yaml"]
        assert len(yaml_configs) >= 1
        
        yaml_config = yaml_configs[0]
        assert "icd10_codes" in yaml_config.data or "name" in yaml_config.data
    
    def test_extract_embedded_json(self, loader, sample_skill_content):
        """Test embedded JSON extraction."""
        configs = loader._extract_embedded_configs(sample_skill_content)
        
        json_configs = [c for c in configs if c.block_type == "json"]
        assert len(json_configs) >= 1
        
        json_config = json_configs[0]
        assert "patient" in json_config.data
    
    def test_load_all_builds_index(self, loader):
        """Test load_all creates skill index."""
        index = loader.load_all()
        
        assert index is not None
        assert isinstance(index.skills, dict)
        # Should have loaded many skills
        assert index.skill_count > 100
    
    def test_index_property_lazy_loads(self, loader):
        """Test index property triggers lazy loading."""
        # Access index property
        index = loader.index
        
        assert index is not None
        assert index.skill_count > 0
    
    def test_get_skill_context(self, loader):
        """Test building system prompt context."""
        context = loader.get_skill_context(products=["patientsim"])
        
        assert isinstance(context, str)
        assert len(context) > 0
        # Should contain skill markers
        assert "Skill:" in context
    
    def test_get_skill_context_no_products(self, loader):
        """Test context with no products specified."""
        context = loader.get_skill_context(products=None)
        
        assert isinstance(context, str)
        # Should still include common and generation skills
        assert len(context) > 0
    
    def test_get_configs(self, loader):
        """Test getting configs from a skill."""
        # First load skills
        loader.load_all()
        
        # Find a skill with configs
        for name, skill in loader.index.skills.items():
            if skill.embedded_configs:
                configs = loader.get_configs(name)
                assert len(configs) > 0
                break
    
    def test_get_configs_nonexistent_skill(self, loader):
        """Test getting configs for non-existent skill."""
        configs = loader.get_configs("nonexistent-skill-xyz")
        
        assert configs == {}


class TestSkillIndex:
    """Tests for SkillIndex."""
    
    @pytest.fixture
    def loader(self):
        return SkillLoader()
    
    def test_products_list(self, loader):
        """Test products property returns list of products."""
        products = loader.index.products
        
        assert "patientsim" in products
        assert "membersim" in products
        assert "trialsim" in products
    
    def test_get_by_product(self, loader):
        """Test getting skills by product."""
        patientsim_skills = loader.index.get_by_product("patientsim")
        
        assert len(patientsim_skills) > 0
        for skill in patientsim_skills:
            assert skill.product == "patientsim"
    
    def test_get_by_trigger(self, loader):
        """Test getting skills by trigger phrase."""
        diabetes_skills = loader.index.get_by_trigger("diabetes")
        
        assert len(diabetes_skills) > 0
    
    def test_get_by_trigger_case_insensitive(self, loader):
        """Test trigger matching is case-insensitive."""
        lower_skills = loader.index.get_by_trigger("diabetes")
        upper_skills = loader.index.get_by_trigger("DIABETES")
        
        # Should find same skills
        assert len(lower_skills) == len(upper_skills)
    
    def test_get_by_name(self, loader):
        """Test getting skill by name."""
        skill = loader.index.get_by_name("diabetes-management")
        
        # May or may not exist depending on loaded skills
        if skill:
            assert skill.metadata.name == "diabetes-management"
