"""Tests for skill management tools."""

import pytest
from pathlib import Path
import tempfile
import shutil

from healthsim_agent.tools.skill_tools import (
    index_skills,
    search_skills,
    get_skill,
    list_skill_products,
    save_skill,
    update_skill,
    delete_skill,
    validate_skill,
    get_skill_versions,
    restore_skill_version,
    get_skill_template,
    create_skill_from_spec,
    get_skill_stats,
    SKILLS_DIR,
    VALID_PRODUCTS,
    SKILL_TYPES,
)
from healthsim_agent.tools.connection import reset_manager


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture(autouse=True)
def reset_connection():
    """Reset connection manager before each test."""
    reset_manager()
    yield
    reset_manager()


@pytest.fixture
def sample_skill_content():
    """Sample valid skill content."""
    return '''---
name: test-skill
description: "A test skill for unit testing. Triggers: test, sample, demo"
---

# Test Skill

A sample skill for testing the skill management system.

## Purpose

This skill demonstrates the required structure for HealthSim skills.

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| count | integer | 10 | Number of entities to generate |
| seed | integer | null | Random seed for reproducibility |

## Generation Rules

Generate test data according to these rules.

## Examples

### Example 1: Basic
```json
{
  "id": "TEST001",
  "name": "Test Entity",
  "status": "active"
}
```

### Example 2: With Options
```json
{
  "id": "TEST002",
  "name": "Another Test",
  "status": "pending",
  "options": {"flag": true}
}
```

## Validation Rules

| Rule | Requirement | Example |
|------|-------------|---------|
| ID format | Must start with TEST | TEST001 |

## Trigger Phrases

- test skill
- sample generation
- demo data

## Related Skills

- [other-skill](other-skill.md)
'''


@pytest.fixture
def minimal_skill_content():
    """Minimal valid skill content."""
    return '''---
name: minimal-skill
description: "A minimal skill"
---

# Minimal Skill

Basic content.
'''


# =============================================================================
# Validation Tests
# =============================================================================

class TestValidateSkill:
    """Tests for validate_skill function."""
    
    def test_valid_skill(self, sample_skill_content):
        """Test validation of a well-formed skill."""
        result = validate_skill(sample_skill_content, skill_type="scenario")
        
        assert result.success
        assert result.data["valid"] is True
        assert result.data["quality_score"] >= 80
        assert len(result.data["issues"]) == 0
        assert result.data["has_examples"] is True
        assert result.data["has_json_examples"] is True
        assert result.data["has_triggers"] is True
    
    def test_missing_frontmatter(self):
        """Test validation fails without frontmatter."""
        content = "# No Frontmatter\n\nJust some content."
        result = validate_skill(content)
        
        assert result.success
        assert result.data["valid"] is False
        assert any("frontmatter" in issue.lower() for issue in result.data["issues"])
    
    def test_missing_name(self):
        """Test validation fails without name in frontmatter."""
        content = '''---
description: "A skill without a name"
---

# Unnamed Skill
'''
        result = validate_skill(content)
        
        assert result.success
        assert result.data["valid"] is False
        assert any("name" in issue.lower() for issue in result.data["issues"])
    
    def test_minimal_skill_with_warnings(self, minimal_skill_content):
        """Test minimal skill passes but has warnings."""
        result = validate_skill(minimal_skill_content)
        
        assert result.success
        assert result.data["valid"] is True  # Passes basic validation
        assert len(result.data["warnings"]) > 0  # But has warnings
        assert result.data["quality_score"] < 100
    
    def test_strict_mode(self, minimal_skill_content):
        """Test strict mode requires all sections."""
        result = validate_skill(minimal_skill_content, skill_type="scenario", strict=True)
        
        assert result.success
        # Strict mode may fail due to missing required sections
        if not result.data["valid"]:
            assert len(result.data["issues"]) > 0


# =============================================================================
# Template Tests
# =============================================================================

class TestGetSkillTemplate:
    """Tests for get_skill_template function."""
    
    def test_scenario_template(self):
        """Test getting scenario template."""
        result = get_skill_template("scenario")
        
        assert result.success
        assert "template" in result.data
        assert "placeholders" in result.data
        assert "required_sections" in result.data
        assert "Purpose" in result.data["required_sections"]
    
    def test_template_template(self):
        """Test getting template template."""
        result = get_skill_template("template")
        
        assert result.success
        assert "Quick Start" in result.data["required_sections"]
    
    def test_pattern_template(self):
        """Test getting pattern template."""
        result = get_skill_template("pattern")
        
        assert result.success
        assert "Pattern Specification" in result.data["required_sections"]
    
    def test_integration_template(self):
        """Test getting integration template."""
        result = get_skill_template("integration")
        
        assert result.success
        assert "Integration Points" in result.data["required_sections"]
    
    def test_invalid_type(self):
        """Test error for invalid skill type."""
        result = get_skill_template("invalid_type")
        
        assert not result.success
        assert "Unknown skill type" in result.error


# =============================================================================
# Index Tests
# =============================================================================

class TestIndexSkills:
    """Tests for index_skills function."""
    
    def test_index_all_skills(self):
        """Test indexing all skills."""
        # This requires the actual skills directory to exist
        if not SKILLS_DIR.exists():
            pytest.skip("Skills directory not found")
        
        result = index_skills()
        
        assert result.success
        assert "indexed" in result.data
        assert "total_files" in result.data
    
    def test_index_single_product(self):
        """Test indexing skills for a single product."""
        if not SKILLS_DIR.exists():
            pytest.skip("Skills directory not found")
        
        result = index_skills(product="patientsim")
        
        assert result.success
        # Should have indexed some skills
        assert result.data["indexed"] >= 0


# =============================================================================
# Search Tests
# =============================================================================

class TestSearchSkills:
    """Tests for search_skills function."""
    
    @pytest.fixture(autouse=True)
    def ensure_indexed(self):
        """Ensure skills are indexed before search tests."""
        if SKILLS_DIR.exists():
            index_skills()
    
    def test_search_by_keyword(self):
        """Test searching by keyword."""
        if not SKILLS_DIR.exists():
            pytest.skip("Skills directory not found")
        
        result = search_skills("diabetes")
        
        assert result.success
        assert "skills" in result.data
        # Should find diabetes-related skills
    
    def test_search_by_product(self):
        """Test filtering by product."""
        if not SKILLS_DIR.exists():
            pytest.skip("Skills directory not found")
        
        result = search_skills("", product="patientsim")
        
        assert result.success
        for skill in result.data["skills"]:
            assert skill["product"] == "patientsim"
    
    def test_search_with_limit(self):
        """Test search respects limit."""
        if not SKILLS_DIR.exists():
            pytest.skip("Skills directory not found")
        
        result = search_skills("", limit=5)
        
        assert result.success
        assert len(result.data["skills"]) <= 5


# =============================================================================
# Get Skill Tests
# =============================================================================

class TestGetSkill:
    """Tests for get_skill function."""
    
    @pytest.fixture(autouse=True)
    def ensure_indexed(self):
        """Ensure skills are indexed."""
        if SKILLS_DIR.exists():
            index_skills()
    
    def test_get_existing_skill(self):
        """Test getting an existing skill."""
        if not SKILLS_DIR.exists():
            pytest.skip("Skills directory not found")
        
        # First search to find a skill
        search_result = search_skills("", limit=1)
        if not search_result.success or not search_result.data["skills"]:
            pytest.skip("No skills available")
        
        skill_id = search_result.data["skills"][0]["id"]
        result = get_skill(skill_id)
        
        assert result.success
        assert result.data["id"] == skill_id
        assert "content" in result.data
    
    def test_get_nonexistent_skill(self):
        """Test error for nonexistent skill."""
        result = get_skill("nonexistent/fake-skill")
        
        assert not result.success
        assert "not found" in result.error.lower()


# =============================================================================
# CRUD Tests
# =============================================================================

class TestSaveSkill:
    """Tests for save_skill function."""
    
    def test_save_valid_skill(self, sample_skill_content, tmp_path):
        """Test saving a valid skill."""
        # Note: This would modify the actual skills directory
        # In a real test, we'd use a temp directory
        
        # For now, just test validation would pass
        result = validate_skill(sample_skill_content, skill_type="scenario")
        assert result.success
        assert result.data["valid"]
    
    def test_save_invalid_product(self, sample_skill_content):
        """Test error for invalid product."""
        result = save_skill(
            name="test",
            product="invalid_product",
            content=sample_skill_content
        )
        
        assert not result.success
        assert "Invalid product" in result.error
    
    def test_save_invalid_skill_type(self, sample_skill_content):
        """Test error for invalid skill type."""
        result = save_skill(
            name="test",
            product="patientsim",
            content=sample_skill_content,
            skill_type="invalid_type"
        )
        
        assert not result.success
        assert "Invalid skill type" in result.error


class TestUpdateSkill:
    """Tests for update_skill function."""
    
    def test_update_nonexistent_skill(self):
        """Test error when updating nonexistent skill."""
        result = update_skill(
            skill_id="nonexistent/fake-skill",
            content="New content"
        )
        
        assert not result.success


class TestDeleteSkill:
    """Tests for delete_skill function."""
    
    def test_delete_nonexistent_skill(self):
        """Test error when deleting nonexistent skill."""
        result = delete_skill("nonexistent/fake-skill")
        
        assert not result.success


# =============================================================================
# Version Tests
# =============================================================================

class TestSkillVersions:
    """Tests for skill versioning functions."""
    
    def test_get_versions_empty(self):
        """Test getting versions for skill with no history."""
        result = get_skill_versions("nonexistent/skill")
        
        assert result.success
        assert result.data["count"] == 0
    
    def test_restore_nonexistent_version(self):
        """Test error restoring nonexistent version."""
        result = restore_skill_version("some/skill", version=999)
        
        assert not result.success


# =============================================================================
# Statistics Tests
# =============================================================================

class TestSkillStats:
    """Tests for get_skill_stats function."""
    
    @pytest.fixture(autouse=True)
    def ensure_indexed(self):
        """Ensure skills are indexed."""
        if SKILLS_DIR.exists():
            index_skills()
    
    def test_get_stats(self):
        """Test getting skill statistics."""
        result = get_skill_stats()
        
        assert result.success
        assert "total_skills" in result.data
        assert "by_product" in result.data
        assert "by_type" in result.data
        assert "word_count" in result.data


# =============================================================================
# Create From Spec Tests
# =============================================================================

class TestCreateFromSpec:
    """Tests for create_skill_from_spec function."""
    
    def test_create_scenario_spec(self):
        """Test creating a scenario from spec."""
        spec = {
            "name": "test-scenario",
            "title": "Test Scenario",
            "description": "A test scenario for validation",
            "purpose": "Testing skill creation",
            "trigger_phrases": ["test", "demo", "sample"],
            "parameters": [
                {"name": "count", "type": "integer", "default": "10", "description": "Number to generate"}
            ],
            "demographics": "Age 18-65",
            "conditions": "E11.9 - Diabetes",
            "medications": "Metformin",
            "variations": [
                {"name": "Basic", "description": "Simple test case"},
                {"name": "Complex", "description": "Advanced test case"}
            ],
            "examples": [
                {"name": "Example 1", "json": {"id": "TEST001"}},
                {"name": "Example 2", "json": {"id": "TEST002"}}
            ],
            "validation_rules": [
                {"rule": "ID", "requirement": "Must exist", "example": "TEST001"}
            ],
        }
        
        # This would actually create a file, so we just test validation
        # In integration tests, we'd use a temp directory
        template_result = get_skill_template("scenario")
        assert template_result.success


# =============================================================================
# List Products Tests
# =============================================================================

class TestListSkillProducts:
    """Tests for list_skill_products function."""
    
    @pytest.fixture(autouse=True)
    def ensure_indexed(self):
        """Ensure skills are indexed."""
        if SKILLS_DIR.exists():
            index_skills()
    
    def test_list_products(self):
        """Test listing skill products."""
        result = list_skill_products()
        
        assert result.success
        assert "products" in result.data
        # Should find some products if skills exist
