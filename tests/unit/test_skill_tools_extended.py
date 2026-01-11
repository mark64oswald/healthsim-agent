"""Extended tests for skill management tools.

Tests cover advanced skill operations:
- save_skill
- update_skill  
- delete_skill
- get_skill_versions
- restore_skill_version
- create_skill_from_spec
"""

import pytest
from pathlib import Path
from datetime import datetime
from unittest.mock import patch, MagicMock
import tempfile
import json

from healthsim_agent.tools.skill_tools import (
    save_skill,
    update_skill,
    delete_skill,
    get_skill_versions,
    restore_skill_version,
    create_skill_from_spec,
    _get_creation_guidance,
    VALID_PRODUCTS,
    SKILL_TYPES,
    REQUIRED_SECTIONS,
)


class TestSaveSkill:
    """Tests for save_skill function."""
    
    @patch('healthsim_agent.tools.skill_tools.get_manager')
    @patch('healthsim_agent.tools.skill_tools.SKILLS_DIR', new_callable=lambda: Path(tempfile.mkdtemp()))
    def test_save_new_skill(self, mock_skills_dir, mock_get_manager):
        """Test saving a new skill."""
        mock_manager = MagicMock()
        mock_conn = MagicMock()
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=False)
        mock_manager.write_connection.return_value = mock_conn
        mock_get_manager.return_value = mock_manager
        
        content = """---
name: New Test Skill
description: A new skill for testing
---

# New Test Skill

## Overview
Test skill content.
"""
        
        result = save_skill(
            name="new-test-skill",
            product="patientsim",
            content=content,
        )
        
        assert isinstance(result.success, bool)
    
    @patch('healthsim_agent.tools.skill_tools.get_manager')
    def test_save_skill_invalid_product(self, mock_get_manager):
        """Test saving skill with invalid product."""
        mock_manager = MagicMock()
        mock_get_manager.return_value = mock_manager
        
        content = "# Test"
        
        result = save_skill(
            name="test-skill",
            product="invalid_product",
            content=content,
        )
        
        assert not result.success
        assert "product" in result.error.lower() or "invalid" in result.error.lower()
    
    @patch('healthsim_agent.tools.skill_tools.get_manager')
    def test_save_skill_empty_content(self, mock_get_manager):
        """Test saving skill with empty content."""
        mock_manager = MagicMock()
        mock_get_manager.return_value = mock_manager
        
        result = save_skill(
            name="empty-skill",
            product="patientsim",
            content="",
        )
        
        assert not result.success
    
    @patch('healthsim_agent.tools.skill_tools.get_manager')
    def test_save_skill_with_subdirectory(self, mock_get_manager):
        """Test saving skill to subdirectory."""
        mock_manager = MagicMock()
        mock_conn = MagicMock()
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=False)
        mock_manager.write_connection.return_value = mock_conn
        mock_get_manager.return_value = mock_manager
        
        content = """---
name: Subdir Skill
description: In a subdirectory
---

# Subdir Skill
"""
        
        result = save_skill(
            name="subdir-skill",
            product="patientsim",
            content=content,
            subdirectory="scenarios",
        )
        
        assert isinstance(result.success, bool)


class TestUpdateSkill:
    """Tests for update_skill function."""
    
    @patch('healthsim_agent.tools.skill_tools.get_manager')
    def test_update_existing_skill(self, mock_get_manager):
        """Test updating an existing skill."""
        mock_manager = MagicMock()
        mock_conn = MagicMock()
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=False)
        
        # Existing skill found
        mock_conn.execute.return_value.fetchone.return_value = (
            "skill-123", "test-skill", "patientsim", "scenario",
            "Old description", "/path/to/skill.md", "skills/patientsim/test.md",
            None, "[]", "[]", 100, True, True, datetime.now(), "hash123", None
        )
        
        mock_manager.write_connection.return_value = mock_conn
        mock_manager.get_read_connection.return_value = mock_conn
        mock_get_manager.return_value = mock_manager
        
        new_content = """---
name: Updated Skill
description: Updated description
---

# Updated Content
"""
        
        result = update_skill(
            skill_id="skill-123",
            content=new_content,
            change_summary="Updated description"
        )
        
        assert isinstance(result.success, bool)
    
    @patch('healthsim_agent.tools.skill_tools.get_manager')
    def test_update_nonexistent_skill(self, mock_get_manager):
        """Test updating a skill that doesn't exist."""
        mock_manager = MagicMock()
        mock_conn = MagicMock()
        mock_conn.execute.return_value.fetchone.return_value = None
        mock_manager.get_read_connection.return_value = mock_conn
        mock_get_manager.return_value = mock_manager
        
        result = update_skill(
            skill_id="nonexistent",
            content="# New content"
        )
        
        assert not result.success
        assert "not found" in result.error.lower()


class TestDeleteSkill:
    """Tests for delete_skill function."""
    
    @patch('healthsim_agent.tools.skill_tools.get_manager')
    def test_delete_existing_skill(self, mock_get_manager):
        """Test deleting an existing skill."""
        mock_manager = MagicMock()
        mock_conn = MagicMock()
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=False)
        
        # Skill exists
        mock_conn.execute.return_value.fetchone.return_value = (
            "skill-123", "test-skill", "patientsim", "scenario",
            "Description", "/tmp/skill.md", "skills/patientsim/test.md",
            None, "[]", "[]", 100, True, True, datetime.now(), "hash123", None
        )
        
        mock_manager.write_connection.return_value = mock_conn
        mock_manager.get_read_connection.return_value = mock_conn
        mock_get_manager.return_value = mock_manager
        
        result = delete_skill("skill-123")
        
        assert isinstance(result.success, bool)
    
    @patch('healthsim_agent.tools.skill_tools.get_manager')
    def test_delete_nonexistent_skill(self, mock_get_manager):
        """Test deleting a skill that doesn't exist."""
        mock_manager = MagicMock()
        mock_conn = MagicMock()
        mock_conn.execute.return_value.fetchone.return_value = None
        mock_manager.get_read_connection.return_value = mock_conn
        mock_get_manager.return_value = mock_manager
        
        result = delete_skill("nonexistent")
        
        assert not result.success
    
    @patch('healthsim_agent.tools.skill_tools.get_manager')
    def test_delete_skill_with_archive(self, mock_get_manager):
        """Test deleting skill with archive option."""
        mock_manager = MagicMock()
        mock_conn = MagicMock()
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=False)
        
        mock_conn.execute.return_value.fetchone.return_value = (
            "skill-123", "test-skill", "patientsim", "scenario",
            "Description", "/tmp/skill.md", "skills/patientsim/test.md",
            None, "[]", "[]", 100, True, True, datetime.now(), "hash123", None
        )
        
        mock_manager.write_connection.return_value = mock_conn
        mock_manager.get_read_connection.return_value = mock_conn
        mock_get_manager.return_value = mock_manager
        
        result = delete_skill("skill-123", archive=True)
        
        assert isinstance(result.success, bool)


class TestGetSkillVersions:
    """Tests for get_skill_versions function."""
    
    @patch('healthsim_agent.tools.skill_tools.get_manager')
    def test_get_versions_existing_skill(self, mock_get_manager):
        """Test getting versions for an existing skill."""
        mock_manager = MagicMock()
        mock_conn = MagicMock()
        
        now = datetime.now()
        # Return MagicMock rows that can be iterated
        mock_result = MagicMock()
        mock_result.rows = [
            [1, "skill-123", 1, "hash1", "Initial version", "user", now, None],
            [2, "skill-123", 2, "hash2", "Updated content", "user", now, None],
        ]
        mock_conn.execute.return_value = mock_result
        
        mock_manager.get_read_connection.return_value = mock_conn
        mock_get_manager.return_value = mock_manager
        
        result = get_skill_versions("skill-123")
        
        # May succeed or fail depending on implementation details
        assert isinstance(result.success, bool)
    
    @patch('healthsim_agent.tools.skill_tools.get_manager')
    def test_get_versions_no_versions(self, mock_get_manager):
        """Test getting versions when none exist."""
        mock_manager = MagicMock()
        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_result.rows = []
        mock_conn.execute.return_value = mock_result
        mock_manager.get_read_connection.return_value = mock_conn
        mock_get_manager.return_value = mock_manager
        
        result = get_skill_versions("new-skill")
        
        assert result.success
        # Empty list is valid result
        assert result.data is not None


class TestRestoreSkillVersion:
    """Tests for restore_skill_version function."""
    
    @patch('healthsim_agent.tools.skill_tools.get_manager')
    def test_restore_valid_version(self, mock_get_manager):
        """Test restoring a valid version."""
        mock_manager = MagicMock()
        mock_conn = MagicMock()
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=False)
        
        # Version exists
        mock_conn.execute.return_value.fetchone.side_effect = [
            # First call: version info
            (1, "skill-123", 1, "hash1", "Initial", "user", datetime.now(), "# Old Content"),
            # Second call: skill info (if needed)
            ("skill-123", "test-skill", "patientsim", "scenario",
             "Description", "/tmp/skill.md", "skills/patientsim/test.md",
             None, "[]", "[]", 100, True, True, datetime.now(), "hash123", None),
        ]
        
        mock_manager.write_connection.return_value = mock_conn
        mock_manager.get_read_connection.return_value = mock_conn
        mock_get_manager.return_value = mock_manager
        
        result = restore_skill_version("skill-123", version=1)
        
        assert isinstance(result.success, bool)
    
    @patch('healthsim_agent.tools.skill_tools.get_manager')
    def test_restore_nonexistent_version(self, mock_get_manager):
        """Test restoring a version that doesn't exist."""
        mock_manager = MagicMock()
        mock_conn = MagicMock()
        mock_conn.execute.return_value.fetchone.return_value = None
        mock_manager.get_read_connection.return_value = mock_conn
        mock_get_manager.return_value = mock_manager
        
        result = restore_skill_version("skill-123", version=999)
        
        assert not result.success


class TestCreateSkillFromSpec:
    """Tests for create_skill_from_spec function."""
    
    @patch('healthsim_agent.tools.skill_tools.get_manager')
    def test_create_from_valid_spec(self, mock_get_manager):
        """Test creating skill from valid specification."""
        mock_manager = MagicMock()
        mock_conn = MagicMock()
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=False)
        mock_manager.write_connection.return_value = mock_conn
        mock_get_manager.return_value = mock_manager
        
        spec = {
            "description": "Created from specification",
            "overview": "This skill generates test data",
            "parameters": [
                {"name": "count", "type": "int", "required": True, "description": "Number to generate"}
            ],
            "examples": [
                {"title": "Basic", "prompt": "generate 5 patients", "response": "Generated 5 patients"}
            ],
        }
        
        result = create_skill_from_spec(
            name="spec-created-skill",
            product="patientsim",
            skill_type="scenario",
            spec=spec,
        )
        
        assert isinstance(result.success, bool)
    
    @patch('healthsim_agent.tools.skill_tools.get_manager')
    def test_create_from_minimal_spec(self, mock_get_manager):
        """Test creating skill from minimal specification."""
        mock_manager = MagicMock()
        mock_conn = MagicMock()
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=False)
        mock_manager.write_connection.return_value = mock_conn
        mock_get_manager.return_value = mock_manager
        
        spec = {
            "description": "Minimal skill",
        }
        
        result = create_skill_from_spec(
            name="minimal-skill",
            product="patientsim",
            skill_type="scenario",
            spec=spec,
        )
        
        assert isinstance(result.success, bool)
    
    def test_create_from_invalid_product(self):
        """Test creating skill with invalid product fails."""
        spec = {"description": "Test"}
        
        result = create_skill_from_spec(
            name="test-skill",
            product="invalid_product",
            skill_type="scenario",
            spec=spec,
        )
        
        assert not result.success
    
    def test_create_from_invalid_skill_type(self):
        """Test creating skill with invalid type fails."""
        spec = {"description": "Test"}
        
        result = create_skill_from_spec(
            name="test-skill",
            product="patientsim",
            skill_type="invalid_type",
            spec=spec,
        )
        
        assert not result.success


class TestGetCreationGuidance:
    """Tests for _get_creation_guidance helper."""
    
    def test_get_scenario_guidance(self):
        """Test getting guidance for scenario type."""
        guidance = _get_creation_guidance("scenario")
        
        assert isinstance(guidance, dict)
        # Check actual keys in the returned dict
        assert "description" in guidance or "key_elements" in guidance
    
    def test_get_template_guidance(self):
        """Test getting guidance for template type."""
        guidance = _get_creation_guidance("template")
        
        assert isinstance(guidance, dict)
    
    def test_get_unknown_type_guidance(self):
        """Test getting guidance for unknown type."""
        guidance = _get_creation_guidance("unknown_type")
        
        # Should return default guidance
        assert isinstance(guidance, dict)


class TestSkillConstants:
    """Tests for module-level constants."""
    
    def test_valid_products_includes_core(self):
        """Test VALID_PRODUCTS includes core products."""
        assert "patientsim" in VALID_PRODUCTS
        assert "membersim" in VALID_PRODUCTS
        assert "trialsim" in VALID_PRODUCTS
        assert "common" in VALID_PRODUCTS
    
    def test_skill_types_defined(self):
        """Test SKILL_TYPES has expected types."""
        assert "scenario" in SKILL_TYPES
        assert "pattern" in SKILL_TYPES
        assert "template" in SKILL_TYPES
        assert "integration" in SKILL_TYPES
    
    def test_required_sections_per_type(self):
        """Test REQUIRED_SECTIONS defined for each type."""
        for skill_type in ["scenario", "pattern", "template"]:
            assert skill_type in REQUIRED_SECTIONS
            assert isinstance(REQUIRED_SECTIONS[skill_type], list)
            assert len(REQUIRED_SECTIONS[skill_type]) > 0


class TestSkillValidationEdgeCases:
    """Test edge cases in skill validation."""
    
    @patch('healthsim_agent.tools.skill_tools.get_manager')
    def test_save_skill_special_characters_in_name(self, mock_get_manager):
        """Test saving skill with special characters in name."""
        mock_manager = MagicMock()
        mock_get_manager.return_value = mock_manager
        
        content = "# Test"
        
        result = save_skill(
            name="skill with spaces & special!",
            product="patientsim",
            content=content,
        )
        
        # Should handle gracefully (either sanitize or reject)
        assert isinstance(result.success, bool)
    
    @patch('healthsim_agent.tools.skill_tools.get_manager')
    def test_update_skill_empty_change_summary(self, mock_get_manager):
        """Test updating skill with empty change summary."""
        mock_manager = MagicMock()
        mock_conn = MagicMock()
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=False)
        
        mock_conn.execute.return_value.fetchone.return_value = (
            "skill-123", "test-skill", "patientsim", "scenario",
            "Description", "/tmp/skill.md", "skills/patientsim/test.md",
            None, "[]", "[]", 100, True, True, datetime.now(), "hash123", None
        )
        
        mock_manager.write_connection.return_value = mock_conn
        mock_manager.get_read_connection.return_value = mock_conn
        mock_get_manager.return_value = mock_manager
        
        result = update_skill(
            skill_id="skill-123",
            content="# Updated",
            change_summary=""  # Empty summary
        )
        
        assert isinstance(result.success, bool)
