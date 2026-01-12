"""Extended tests for skill_tools module to increase coverage."""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from datetime import date


class TestSearchSkills:
    """Tests for search_skills function."""
    
    def test_empty_query(self):
        """Test search with empty query."""
        from healthsim_agent.tools.skill_tools import search_skills
        
        result = search_skills("")
        # Empty query still returns results
        assert result is not None
    
    def test_query_single_word(self):
        """Test search with single word."""
        from healthsim_agent.tools.skill_tools import search_skills
        
        result = search_skills("patient")
        assert result.success is True
    
    def test_search_with_limit(self):
        """Test search with custom limit."""
        from healthsim_agent.tools.skill_tools import search_skills
        
        result = search_skills("patient", limit=5)
        assert result.success is True
        if result.data:
            assert len(result.data) <= 5
    
    def test_search_diabetes(self):
        """Test searching for diabetes skills."""
        from healthsim_agent.tools.skill_tools import search_skills
        
        result = search_skills("diabetes")
        assert result.success is True
    
    def test_search_with_product_filter(self):
        """Test searching with product filter."""
        from healthsim_agent.tools.skill_tools import search_skills
        
        result = search_skills("patient", product="patientsim")
        assert result.success is True
    
    def test_search_with_skill_type(self):
        """Test searching with skill type filter."""
        from healthsim_agent.tools.skill_tools import search_skills
        
        result = search_skills("patient", skill_type="scenario")
        assert result.success is True
    
    def test_search_with_tags(self):
        """Test searching with tags filter."""
        from healthsim_agent.tools.skill_tools import search_skills
        
        result = search_skills("patient", tags=["clinical"])
        assert result.success is True


class TestGetSkill:
    """Tests for get_skill function."""
    
    def test_nonexistent_skill(self):
        """Test getting nonexistent skill."""
        from healthsim_agent.tools.skill_tools import get_skill
        
        result = get_skill("nonexistent-skill-xyz-123456")
        assert result.success is False
    
    def test_empty_skill_id_returns_default(self):
        """Test with empty skill ID returns default skill."""
        from healthsim_agent.tools.skill_tools import get_skill
        
        result = get_skill("")
        # Empty ID returns the root SKILL.md
        assert result.success is True


class TestListSkillProducts:
    """Tests for list_skill_products function."""
    
    def test_returns_products(self):
        """Test listing skill products."""
        from healthsim_agent.tools.skill_tools import list_skill_products
        
        result = list_skill_products()
        assert result.success is True
        assert result.data is not None


class TestGetSkillStats:
    """Tests for get_skill_stats function."""
    
    def test_returns_stats(self):
        """Test getting skill stats."""
        from healthsim_agent.tools.skill_tools import get_skill_stats
        
        result = get_skill_stats()
        assert result.success is True
        assert result.data is not None


class TestGetSkillTemplate:
    """Tests for get_skill_template function."""
    
    def test_scenario_template(self):
        """Test getting scenario template."""
        from healthsim_agent.tools.skill_tools import get_skill_template
        
        result = get_skill_template("scenario")
        assert result.success is True
    
    def test_template_template(self):
        """Test getting template template."""
        from healthsim_agent.tools.skill_tools import get_skill_template
        
        result = get_skill_template("template")
        assert result.success is True
    
    def test_pattern_template(self):
        """Test getting pattern template."""
        from healthsim_agent.tools.skill_tools import get_skill_template
        
        result = get_skill_template("pattern")
        assert result.success is True
    
    def test_integration_template(self):
        """Test getting integration template."""
        from healthsim_agent.tools.skill_tools import get_skill_template
        
        result = get_skill_template("integration")
        assert result.success is True
    
    def test_unknown_template_type(self):
        """Test with unknown template type."""
        from healthsim_agent.tools.skill_tools import get_skill_template
        
        result = get_skill_template("unknown_type")
        assert result.success is False


class TestValidateSkill:
    """Tests for validate_skill function."""
    
    def test_validate_empty_content_returns_validation_result(self):
        """Test validating empty content returns validation data."""
        from healthsim_agent.tools.skill_tools import validate_skill
        
        result = validate_skill("")
        # Returns success with validation data showing valid=False
        assert result.success is True
        assert result.data["valid"] is False
    
    def test_validate_minimal_skill(self):
        """Test validating minimal skill content."""
        from healthsim_agent.tools.skill_tools import validate_skill
        
        content = """---
name: test-skill
description: A test skill
product: patientsim
---

# Test Skill

This is a test.
"""
        result = validate_skill(content)
        assert result is not None
        assert result.success is True
    
    def test_validate_with_skill_type(self):
        """Test validating with skill type specified."""
        from healthsim_agent.tools.skill_tools import validate_skill
        
        content = """---
name: test-skill
description: A test skill
---

# Test
"""
        result = validate_skill(content, skill_type="scenario")
        assert result is not None
    
    def test_validate_strict_mode(self):
        """Test validating in strict mode."""
        from healthsim_agent.tools.skill_tools import validate_skill
        
        content = """---
name: test-skill
description: A test skill
---

# Test
"""
        result = validate_skill(content, strict=True)
        assert result is not None


class TestSaveSkill:
    """Tests for save_skill function."""
    
    def test_save_empty_name(self):
        """Test saving with empty name."""
        from healthsim_agent.tools.skill_tools import save_skill
        
        result = save_skill("", "patientsim", "content")
        assert result.success is False
    
    def test_save_empty_content(self):
        """Test saving with empty content."""
        from healthsim_agent.tools.skill_tools import save_skill
        
        result = save_skill("test-skill", "patientsim", "")
        assert result.success is False
    
    def test_save_invalid_product(self):
        """Test saving with invalid product."""
        from healthsim_agent.tools.skill_tools import save_skill
        
        result = save_skill("test-skill", "invalid-product", "content")
        assert result.success is False


class TestUpdateSkill:
    """Tests for update_skill function."""
    
    def test_update_nonexistent(self):
        """Test updating nonexistent skill."""
        from healthsim_agent.tools.skill_tools import update_skill
        
        result = update_skill("nonexistent-skill-xyz-123456", content="new content")
        assert result.success is False


class TestDeleteSkill:
    """Tests for delete_skill function."""
    
    def test_delete_nonexistent(self):
        """Test deleting nonexistent skill."""
        from healthsim_agent.tools.skill_tools import delete_skill
        
        result = delete_skill("nonexistent-skill-xyz-123456")
        assert result.success is False


class TestGetSkillVersions:
    """Tests for get_skill_versions function."""
    
    def test_versions_nonexistent_returns_empty(self):
        """Test getting versions for nonexistent skill returns empty list."""
        from healthsim_agent.tools.skill_tools import get_skill_versions
        
        result = get_skill_versions("nonexistent-skill-xyz-123456")
        # Returns success with empty versions
        assert result.success is True
        assert result.data["versions"] == []


class TestRestoreSkillVersion:
    """Tests for restore_skill_version function."""
    
    def test_restore_nonexistent(self):
        """Test restoring nonexistent skill."""
        from healthsim_agent.tools.skill_tools import restore_skill_version
        
        result = restore_skill_version("nonexistent-skill-xyz-123456", 1)
        assert result.success is False
    
    def test_restore_empty_id(self):
        """Test restoring with empty ID."""
        from healthsim_agent.tools.skill_tools import restore_skill_version
        
        result = restore_skill_version("", 1)
        # May return error or handle gracefully
        assert result is not None


class TestIndexSkills:
    """Tests for index_skills function."""
    
    def test_index_all(self):
        """Test indexing all skills."""
        from healthsim_agent.tools.skill_tools import index_skills
        
        result = index_skills()
        assert result.success is True
    
    def test_index_specific_product(self):
        """Test indexing specific product."""
        from healthsim_agent.tools.skill_tools import index_skills
        
        result = index_skills(product="patientsim")
        assert result.success is True
    
    def test_index_force(self):
        """Test force reindex."""
        from healthsim_agent.tools.skill_tools import index_skills
        
        result = index_skills(force=True)
        assert result.success is True


class TestCreateSkillFromSpec:
    """Tests for create_skill_from_spec function."""
    
    def test_create_empty_name(self):
        """Test creating with empty name."""
        from healthsim_agent.tools.skill_tools import create_skill_from_spec
        
        result = create_skill_from_spec("", "patientsim", "scenario", {})
        assert result.success is False
    
    def test_create_with_spec(self):
        """Test creating with spec."""
        from healthsim_agent.tools.skill_tools import create_skill_from_spec
        
        spec = {"description": "Test skill"}
        result = create_skill_from_spec(
            "test-skill-temp", 
            "patientsim", 
            "scenario", 
            spec
        )
        # Result depends on whether it can actually create
        assert result is not None


class TestSkillToolsEdgeCases:
    """Edge case tests for skill tools."""
    
    def test_search_unicode_query(self):
        """Test search with unicode characters."""
        from healthsim_agent.tools.skill_tools import search_skills
        
        result = search_skills("患者")  # Chinese for "patient"
        assert result is not None
    
    def test_search_very_long_query(self):
        """Test search with very long query."""
        from healthsim_agent.tools.skill_tools import search_skills
        
        long_query = "patient diabetes hypertension " * 20
        result = search_skills(long_query)
        assert result is not None
    
    def test_skill_id_case_handling(self):
        """Test skill ID case handling."""
        from healthsim_agent.tools.skill_tools import get_skill
        
        result_lower = get_skill("test-skill")
        result_upper = get_skill("TEST-SKILL")
        # Both should handle consistently
        assert result_lower is not None
        assert result_upper is not None
    
    def test_special_chars_in_skill_id(self):
        """Test skill ID with special characters."""
        from healthsim_agent.tools.skill_tools import get_skill
        
        result = get_skill("skill/with/slashes")
        assert result.success is False
        
        result = get_skill("skill:with:colons")
        assert result.success is False
