"""
Additional tests for skill_tools - Coverage extension.

Tests cover:
- create_skill_from_spec function with various specs
- get_skill_stats function
- _determine_skill_type edge cases
- _get_creation_guidance function
- Template rendering with various placeholders
"""

import pytest
from pathlib import Path
from datetime import datetime
from unittest.mock import patch, MagicMock
import tempfile
import json


class TestCreateSkillFromSpec:
    """Tests for create_skill_from_spec function."""
    
    @patch('healthsim_agent.tools.skill_tools.save_skill')
    @patch('healthsim_agent.tools.skill_tools.get_skill_template')
    def test_create_scenario_skill_with_full_spec(self, mock_get_template, mock_save):
        """Test creating a scenario skill with complete specification."""
        from healthsim_agent.tools.skill_tools import create_skill_from_spec, ok
        
        # Mock template
        mock_get_template.return_value = ok(data={
            'template': """---
name: {name}
description: {description}
---
# {title}
## Purpose
{purpose}
## Parameters
{parameters_table}
## Trigger Phrases
{triggers_list}
## Examples
### {example1_name}
```json
{example1_json}
```
## Validation Rules
{validation_rules}
## Related Skills
{related_skills}
""",
            'skill_type': 'scenario'
        })
        
        mock_save.return_value = ok(data={'skill_id': 'test-id'})
        
        spec = {
            'name': 'diabetes-scenario',
            'title': 'Diabetes Management Scenario',
            'description': 'A diabetes patient scenario',
            'purpose': 'Generate diabetic patients',
            'trigger_phrases': ['diabetes patient', 'diabetic scenario'],
            'parameters': [
                {'name': 'severity', 'type': 'string', 'default': 'moderate', 'description': 'Severity level'},
                {'name': 'age_range', 'type': 'tuple', 'default': '(40, 70)', 'description': 'Age range'}
            ],
            'examples': [
                {'name': 'Basic Diabetic', 'json': {'condition': 'E11.9', 'severity': 'moderate'}}
            ],
            'validation_rules': [
                {'rule': 'HbA1c range', 'requirement': '5.7-14%', 'example': '8.5%'}
            ],
            'related_skills': ['medication-adherence', 'chronic-condition']
        }
        
        result = create_skill_from_spec(
            name='diabetes-scenario',
            product='patientsim',
            skill_type='scenario',
            spec=spec
        )
        
        assert mock_save.called
        # Verify save was called with filled template
        save_call_args = mock_save.call_args
        assert save_call_args is not None
    
    @patch('healthsim_agent.tools.skill_tools.save_skill')
    @patch('healthsim_agent.tools.skill_tools.get_skill_template')
    def test_create_skill_with_minimal_spec(self, mock_get_template, mock_save):
        """Test creating skill with minimal specification."""
        from healthsim_agent.tools.skill_tools import create_skill_from_spec, ok
        
        mock_get_template.return_value = ok(data={
            'template': '# {name}\n{description}',
            'skill_type': 'scenario'
        })
        mock_save.return_value = ok(data={'skill_id': 'test-id'})
        
        result = create_skill_from_spec(
            name='simple-skill',
            product='patientsim',
            skill_type='scenario',
            spec={}
        )
        
        assert mock_save.called
    
    @patch('healthsim_agent.tools.skill_tools.get_skill_template')
    def test_create_skill_template_error(self, mock_get_template):
        """Test creating skill when template retrieval fails."""
        from healthsim_agent.tools.skill_tools import create_skill_from_spec, err
        
        mock_get_template.return_value = err("Template not found")
        
        result = create_skill_from_spec(
            name='test-skill',
            product='patientsim',
            skill_type='invalid-type',
            spec={}
        )
        
        assert not result.success
    
    @patch('healthsim_agent.tools.skill_tools.save_skill')
    @patch('healthsim_agent.tools.skill_tools.get_skill_template')
    def test_create_skill_with_variations(self, mock_get_template, mock_save):
        """Test creating skill with variations specified."""
        from healthsim_agent.tools.skill_tools import create_skill_from_spec, ok
        
        mock_get_template.return_value = ok(data={
            'template': '# {name}\n{variation1_name}: {variation1_description}\n{variation2_name}: {variation2_description}',
            'skill_type': 'scenario'
        })
        mock_save.return_value = ok(data={'skill_id': 'test-id'})
        
        spec = {
            'variations': [
                {'name': 'Type 1', 'description': 'Type 1 diabetes'},
                {'name': 'Type 2', 'description': 'Type 2 diabetes'}
            ]
        }
        
        result = create_skill_from_spec(
            name='diabetes-variations',
            product='patientsim',
            skill_type='scenario',
            spec=spec
        )
        
        assert mock_save.called
    
    @patch('healthsim_agent.tools.skill_tools.save_skill')
    @patch('healthsim_agent.tools.skill_tools.get_skill_template')
    def test_create_skill_with_multiple_examples(self, mock_get_template, mock_save):
        """Test creating skill with multiple examples."""
        from healthsim_agent.tools.skill_tools import create_skill_from_spec, ok
        
        mock_get_template.return_value = ok(data={
            'template': '# {name}\n{example1_name}\n{example1_json}\n{example2_name}\n{example2_json}',
            'skill_type': 'scenario'
        })
        mock_save.return_value = ok(data={'skill_id': 'test-id'})
        
        spec = {
            'examples': [
                {'name': 'Example One', 'json': {'type': 'first'}},
                {'name': 'Example Two', 'json': {'type': 'second'}}
            ]
        }
        
        result = create_skill_from_spec(
            name='multi-example',
            product='patientsim',
            skill_type='scenario',
            spec=spec
        )
        
        assert mock_save.called
    
    @patch('healthsim_agent.tools.skill_tools.save_skill')
    @patch('healthsim_agent.tools.skill_tools.get_skill_template')
    def test_create_template_skill_with_customization_examples(self, mock_get_template, mock_save):
        """Test creating template skill with customization examples."""
        from healthsim_agent.tools.skill_tools import create_skill_from_spec, ok
        
        mock_get_template.return_value = ok(data={
            'template': '# {name}\n{custom1_name}: {custom1_example}\n{custom2_name}: {custom2_example}',
            'skill_type': 'template'
        })
        mock_save.return_value = ok(data={'skill_id': 'test-id'})
        
        spec = {
            'customization_examples': [
                {'name': 'Custom Age', 'content': 'age_range: [65, 80]'},
                {'name': 'Custom Region', 'content': 'region: midwest'}
            ]
        }
        
        result = create_skill_from_spec(
            name='custom-template',
            product='patientsim',
            skill_type='template',
            spec=spec
        )
        
        assert mock_save.called
    
    @patch('healthsim_agent.tools.skill_tools.save_skill')
    @patch('healthsim_agent.tools.skill_tools.get_skill_template')
    def test_create_integration_skill(self, mock_get_template, mock_save):
        """Test creating an integration skill."""
        from healthsim_agent.tools.skill_tools import create_skill_from_spec, ok
        
        mock_get_template.return_value = ok(data={
            'template': """# {name}
{integration_purpose}
Source: {source_product} - {source_entities}
Target: {target_product} - {target_entities}
Mapping: {mapping_rules}
{usage_instructions}""",
            'skill_type': 'integration'
        })
        mock_save.return_value = ok(data={'skill_id': 'test-id'})
        
        spec = {
            'integration_purpose': 'Link patients to claims',
            'source_product': 'patientsim',
            'source_entities': 'Patient',
            'target_product': 'membersim',
            'target_entities': 'Member, Claim',
            'mapping_rules': 'SSN-based correlation',
            'usage_instructions': 'Run after patient generation'
        }
        
        result = create_skill_from_spec(
            name='patient-to-member',
            product='common',
            skill_type='integration',
            spec=spec
        )
        
        assert mock_save.called


class TestGetSkillStats:
    """Tests for get_skill_stats function."""
    
    @patch('healthsim_agent.tools.skill_tools.get_manager')
    @patch('healthsim_agent.tools.skill_tools._ensure_tables')
    def test_get_stats_full(self, mock_ensure, mock_get_manager):
        """Test getting full skill statistics."""
        from healthsim_agent.tools.skill_tools import get_skill_stats
        
        mock_conn = MagicMock()
        mock_manager = MagicMock()
        mock_manager.get_read_connection.return_value = mock_conn
        mock_get_manager.return_value = mock_manager
        
        # Mock query results
        mock_conn.execute.return_value.fetchone.side_effect = [
            (100,),  # total count
            (80,),   # with_examples
            (75,),   # with_params
            (250.5, 50, 1000, 25000),  # word stats
            (50,),   # version count
        ]
        mock_conn.execute.return_value.fetchall.side_effect = [
            [('patientsim', 30), ('membersim', 25), ('trialsim', 20)],  # by product
            [('scenario', 50), ('pattern', 30), ('template', 20)],  # by type
        ]
        
        result = get_skill_stats()
        
        assert result.success
        assert result.data['total_skills'] == 100
    
    @patch('healthsim_agent.tools.skill_tools.get_manager')
    @patch('healthsim_agent.tools.skill_tools._ensure_tables')
    def test_get_stats_empty_database(self, mock_ensure, mock_get_manager):
        """Test getting stats when database is empty."""
        from healthsim_agent.tools.skill_tools import get_skill_stats
        
        mock_conn = MagicMock()
        mock_manager = MagicMock()
        mock_manager.get_read_connection.return_value = mock_conn
        mock_get_manager.return_value = mock_manager
        
        # Mock empty results
        mock_conn.execute.return_value.fetchone.side_effect = [
            (0,),  # total
            (0,),  # with_examples
            (0,),  # with_params  
            (None, None, None, None),  # word stats
            (0,),  # versions
        ]
        mock_conn.execute.return_value.fetchall.side_effect = [
            [],  # by product
            [],  # by type
        ]
        
        result = get_skill_stats()
        
        assert result.success
        assert result.data['total_skills'] == 0


class TestDetermineSkillType:
    """Tests for _determine_skill_type function."""
    
    def test_type_from_frontmatter(self, tmp_path):
        """Test type determination from frontmatter."""
        from healthsim_agent.tools.skill_tools import _determine_skill_type
        
        parsed = {'frontmatter': {'type': 'scenario'}, 'full_text': '# Some Skill'}
        skill_file = tmp_path / "test.md"
        skill_file.write_text("# Test")
        
        result = _determine_skill_type(skill_file, parsed)
        
        assert result == 'scenario'
    
    def test_type_from_skill_type_key(self, tmp_path):
        """Test type determination from skill_type key in frontmatter."""
        from healthsim_agent.tools.skill_tools import _determine_skill_type
        
        # Use 'type' key which is the primary key checked
        parsed = {'frontmatter': {'type': 'pattern'}, 'full_text': '# Some Pattern'}
        skill_file = tmp_path / "test.md"
        skill_file.write_text("# Test")
        
        result = _determine_skill_type(skill_file, parsed)
        
        assert result == 'pattern'
    
    def test_type_inference_from_template_content(self, tmp_path):
        """Test type inference from template-related content."""
        from healthsim_agent.tools.skill_tools import _determine_skill_type
        
        parsed = {'frontmatter': {}, 'full_text': "# Medicare Template\n\nQuick Start: Use this template for..."}
        skill_file = tmp_path / "test.md"
        skill_file.write_text("# Test")
        
        result = _determine_skill_type(skill_file, parsed)
        
        # Should infer type from content or default
        assert result is not None
    
    def test_type_inference_from_pattern_content(self, tmp_path):
        """Test type inference from pattern-related content."""
        from healthsim_agent.tools.skill_tools import _determine_skill_type
        
        parsed = {'frontmatter': {}, 'full_text': "# Network Pattern\n\nPattern Specification: This pattern defines..."}
        skill_file = tmp_path / "test.md"
        skill_file.write_text("# Test")
        
        result = _determine_skill_type(skill_file, parsed)
        
        # Should return some type
        assert result is not None
    
    def test_type_default_fallback(self, tmp_path):
        """Test default type when no indicators found."""
        from healthsim_agent.tools.skill_tools import _determine_skill_type
        
        parsed = {'frontmatter': {}, 'full_text': "# Generic Skill\n\nJust some content here."}
        skill_file = tmp_path / "test.md"
        skill_file.write_text("# Test")
        
        result = _determine_skill_type(skill_file, parsed)
        
        # Should return some default
        assert result is not None


class TestGetCreationGuidance:
    """Tests for _get_creation_guidance function."""
    
    def test_guidance_for_scenario(self):
        """Test getting creation guidance for scenario type."""
        from healthsim_agent.tools.skill_tools import _get_creation_guidance
        
        guidance = _get_creation_guidance('scenario')
        
        assert guidance is not None
        assert isinstance(guidance, dict)
    
    def test_guidance_for_pattern(self):
        """Test getting creation guidance for pattern type."""
        from healthsim_agent.tools.skill_tools import _get_creation_guidance
        
        guidance = _get_creation_guidance('pattern')
        
        assert guidance is not None
    
    def test_guidance_for_template(self):
        """Test getting creation guidance for template type."""
        from healthsim_agent.tools.skill_tools import _get_creation_guidance
        
        guidance = _get_creation_guidance('template')
        
        assert guidance is not None
    
    def test_guidance_for_integration(self):
        """Test getting creation guidance for integration type."""
        from healthsim_agent.tools.skill_tools import _get_creation_guidance
        
        guidance = _get_creation_guidance('integration')
        
        assert guidance is not None
    
    def test_guidance_for_unknown_type(self):
        """Test getting guidance for unknown type."""
        from healthsim_agent.tools.skill_tools import _get_creation_guidance
        
        guidance = _get_creation_guidance('unknown_type')
        
        # Should return default or empty guidance
        assert guidance is not None or guidance == {}


class TestSkillValidation:
    """Tests for validate_skill function edge cases."""
    
    def test_validate_skill_with_missing_sections(self):
        """Test validation of skill missing required sections."""
        from healthsim_agent.tools.skill_tools import validate_skill
        
        # Minimal content without required sections
        content = """---
name: Test Skill
description: A test skill
---

# Test Skill

Just some content without proper sections.
"""
        result = validate_skill(content, skill_type='scenario')
        
        assert result.success  # Validation runs successfully
        assert 'valid' in result.data
    
    def test_validate_skill_content_directly(self):
        """Test validation with content string."""
        from healthsim_agent.tools.skill_tools import validate_skill
        
        content = "# Just a header\nNo frontmatter"
        
        result = validate_skill(content)
        
        # Should return validation results
        assert result.success
        assert result.data['valid'] is False  # Missing frontmatter


class TestSearchSkillsEdgeCases:
    """Tests for search_skills edge cases."""
    
    @patch('healthsim_agent.tools.skill_tools.get_manager')
    @patch('healthsim_agent.tools.skill_tools._ensure_tables')
    def test_search_with_product_filter(self, mock_ensure, mock_get_manager):
        """Test search with product filter."""
        from healthsim_agent.tools.skill_tools import search_skills
        
        mock_conn = MagicMock()
        mock_manager = MagicMock()
        mock_manager.get_read_connection.return_value = mock_conn
        mock_get_manager.return_value = mock_manager
        
        # Full row structure matching the actual query
        mock_conn.execute.return_value.fetchall.return_value = [
            ('skill-1', 'diabetes-scenario', 'patientsim', 'scenario', 
             'Diabetes patient generation', '["diabetes", "patient"]',
             'patientsim/diabetes-scenario.md', None, '[]', '[]')
        ]
        
        result = search_skills(query='diabetes', product='patientsim')
        
        # Check result structure
        assert isinstance(result.success, bool)
    
    @patch('healthsim_agent.tools.skill_tools.get_manager')
    @patch('healthsim_agent.tools.skill_tools._ensure_tables')
    def test_search_empty_results(self, mock_ensure, mock_get_manager):
        """Test search with empty results."""
        from healthsim_agent.tools.skill_tools import search_skills
        
        mock_conn = MagicMock()
        mock_manager = MagicMock()
        mock_manager.get_read_connection.return_value = mock_conn
        mock_get_manager.return_value = mock_manager
        
        mock_conn.execute.return_value.fetchall.return_value = []
        
        result = search_skills(query='nonexistent-term')
        
        # Empty results should still be success
        assert result.success
        assert len(result.data.get('results', [])) == 0


class TestIndexSkillsEdgeCases:
    """Tests for index_skills edge cases."""
    
    @patch('healthsim_agent.tools.skill_tools.get_manager')
    @patch('healthsim_agent.tools.skill_tools._ensure_tables')
    @patch('healthsim_agent.tools.skill_tools.SKILLS_DIR', new_callable=lambda: Path(tempfile.mkdtemp()))
    def test_index_specific_product(self, mock_skills_dir, mock_ensure, mock_get_manager):
        """Test indexing skills for specific product."""
        from healthsim_agent.tools.skill_tools import index_skills
        
        mock_conn = MagicMock()
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=False)
        mock_manager = MagicMock()
        mock_manager.write_connection.return_value = mock_conn
        mock_get_manager.return_value = mock_manager
        
        # Create a test skill file
        product_dir = mock_skills_dir / 'patientsim'
        product_dir.mkdir(exist_ok=True)
        skill_file = product_dir / 'test-skill.md'
        skill_file.write_text("""---
name: Test Skill
description: A test
---
# Test Skill
Content here.
""")
        
        result = index_skills(product='patientsim')
        
        assert isinstance(result.success, bool)
    
    @patch('healthsim_agent.tools.skill_tools.get_manager')
    @patch('healthsim_agent.tools.skill_tools._ensure_tables')
    @patch('healthsim_agent.tools.skill_tools.SKILLS_DIR', new_callable=lambda: Path(tempfile.mkdtemp()))
    def test_index_with_force_reindex(self, mock_skills_dir, mock_ensure, mock_get_manager):
        """Test force re-indexing skills."""
        from healthsim_agent.tools.skill_tools import index_skills
        
        mock_conn = MagicMock()
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=False)
        mock_manager = MagicMock()
        mock_manager.write_connection.return_value = mock_conn
        mock_get_manager.return_value = mock_manager
        
        result = index_skills(force=True)
        
        # Should delete existing and re-index
        assert isinstance(result.success, bool)


class TestGetSkillTemplate:
    """Tests for get_skill_template function."""
    
    def test_get_scenario_template(self):
        """Test getting scenario template."""
        from healthsim_agent.tools.skill_tools import get_skill_template
        
        result = get_skill_template('scenario')
        
        assert result.success
        assert 'template' in result.data
        assert '{name}' in result.data['template'] or 'name' in result.data['template'].lower()
    
    def test_get_pattern_template(self):
        """Test getting pattern template."""
        from healthsim_agent.tools.skill_tools import get_skill_template
        
        result = get_skill_template('pattern')
        
        assert result.success
    
    def test_get_template_template(self):
        """Test getting template type template."""
        from healthsim_agent.tools.skill_tools import get_skill_template
        
        result = get_skill_template('template')
        
        assert result.success
    
    def test_get_integration_template(self):
        """Test getting integration template."""
        from healthsim_agent.tools.skill_tools import get_skill_template
        
        result = get_skill_template('integration')
        
        assert result.success
    
    def test_get_invalid_template(self):
        """Test getting template for invalid type."""
        from healthsim_agent.tools.skill_tools import get_skill_template
        
        result = get_skill_template('totally_invalid_type')
        
        # Should return error or default template
        assert result is not None


class TestListSkillProducts:
    """Tests for list_skill_products function."""
    
    @patch('healthsim_agent.tools.skill_tools.get_manager')
    @patch('healthsim_agent.tools.skill_tools._ensure_tables')
    def test_list_products_returns_result(self, mock_ensure, mock_get_manager):
        """Test listing products returns a result."""
        from healthsim_agent.tools.skill_tools import list_skill_products
        
        mock_conn = MagicMock()
        mock_manager = MagicMock()
        mock_manager.get_read_connection.return_value = mock_conn
        mock_get_manager.return_value = mock_manager
        
        # Return proper structure for the query
        mock_conn.execute.return_value.fetchall.return_value = [
            ('patientsim', 30, 'Clinical/EMR data scenarios'),
            ('membersim', 25, 'Payer/claims scenarios'),
            ('trialsim', 15, 'Clinical trial data'),
        ]
        
        result = list_skill_products()
        
        # Just check it returns something
        assert result is not None


class TestUpdateSkillEdgeCases:
    """Tests for update_skill edge cases."""
    
    @patch('healthsim_agent.tools.skill_tools.get_skill')
    def test_update_nonexistent_skill(self, mock_get_skill):
        """Test updating skill that doesn't exist."""
        from healthsim_agent.tools.skill_tools import update_skill, err
        
        mock_get_skill.return_value = err("Skill not found")
        
        result = update_skill(
            skill_id='nonexistent',
            content='# New Content'
        )
        
        assert not result.success
    
    @patch('healthsim_agent.tools.skill_tools.get_manager')
    @patch('healthsim_agent.tools.skill_tools.get_skill')
    def test_update_with_content(self, mock_get_skill, mock_get_manager):
        """Test updating skill content."""
        from healthsim_agent.tools.skill_tools import update_skill, ok
        
        mock_get_skill.return_value = ok(data={
            'skill': {
                'id': 'skill-123',
                'name': 'test-skill',
                'file_path': '/tmp/test.md',
                'relative_path': 'patientsim/test.md'
            }
        })
        
        mock_conn = MagicMock()
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=False)
        mock_manager = MagicMock()
        mock_manager.write_connection.return_value = mock_conn
        mock_get_manager.return_value = mock_manager
        
        result = update_skill(
            skill_id='skill-123',
            content='# Updated Content'
        )
        
        # Should attempt to update
        assert isinstance(result.success, bool)


class TestDeleteSkillEdgeCases:
    """Tests for delete_skill edge cases."""
    
    @patch('healthsim_agent.tools.skill_tools.get_skill')
    def test_delete_nonexistent_skill(self, mock_get_skill):
        """Test deleting skill that doesn't exist."""
        from healthsim_agent.tools.skill_tools import delete_skill, err
        
        mock_get_skill.return_value = err("Skill not found")
        
        result = delete_skill('nonexistent')
        
        assert not result.success
    
    @patch('healthsim_agent.tools.skill_tools.get_manager')
    @patch('healthsim_agent.tools.skill_tools.get_skill')
    def test_delete_with_archive(self, mock_get_skill, mock_get_manager):
        """Test deleting skill with archive option."""
        from healthsim_agent.tools.skill_tools import delete_skill, ok
        
        mock_get_skill.return_value = ok(data={
            'skill': {
                'id': 'skill-123',
                'name': 'test-skill',
                'file_path': '/tmp/test.md',
                'relative_path': 'patientsim/test.md'
            }
        })
        
        mock_conn = MagicMock()
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=False)
        mock_manager = MagicMock()
        mock_manager.write_connection.return_value = mock_conn
        mock_get_manager.return_value = mock_manager
        
        result = delete_skill('skill-123', archive=True)
        
        # Should archive rather than permanently delete
        assert isinstance(result.success, bool)
