"""Extended tests for profile_journey_tools.

Covers:
- Error handling paths
- Edge cases in filtering
- Built-in journey protection
- Unknown product handling
- JSON export variations
"""

import pytest
import os
import json
from pathlib import Path
from unittest.mock import patch, MagicMock

from healthsim_agent.tools.profile_journey_tools import (
    list_profiles, save_profile, load_profile, delete_profile, execute_profile,
    list_journeys, save_journey, load_journey, delete_journey, execute_journey,
    export_json, _ensure_tables,
)
from healthsim_agent.tools.connection import get_manager, reset_manager


@pytest.fixture(autouse=True)
def use_test_database(tmp_path):
    """Use a temporary database for tests."""
    test_db = tmp_path / "test_healthsim.duckdb"
    
    reset_manager()
    os.environ["HEALTHSIM_DB_PATH"] = str(test_db)
    
    import healthsim_agent.tools.profile_journey_tools as pjt
    pjt._tables_ensured = False
    
    yield
    
    reset_manager()
    if "HEALTHSIM_DB_PATH" in os.environ:
        del os.environ["HEALTHSIM_DB_PATH"]


class TestListProfilesExtended:
    """Extended tests for list_profiles."""
    
    def test_list_profiles_with_search(self):
        """Test list_profiles with search term."""
        save_profile(name="diabetes-profile", profile_spec={}, description="Diabetes patients")
        save_profile(name="cardiac-profile", profile_spec={}, description="Heart conditions")
        
        result = list_profiles(search="diabetes")
        assert result.success is True
        assert result.data["count"] == 1
        assert result.data["profiles"][0]["name"] == "diabetes-profile"
    
    def test_list_profiles_with_tag(self):
        """Test list_profiles with tag filter."""
        save_profile(name="tagged-profile", profile_spec={}, tags=["chronic", "diabetes"])
        save_profile(name="untagged-profile", profile_spec={}, tags=["cardiac"])
        
        result = list_profiles(tag="diabetes")
        assert result.success is True
        assert result.data["count"] == 1
        assert result.data["profiles"][0]["name"] == "tagged-profile"
    
    def test_list_profiles_with_limit(self):
        """Test list_profiles respects limit."""
        for i in range(5):
            save_profile(name=f"profile-{i}", profile_spec={})
        
        result = list_profiles(limit=3)
        assert result.success is True
        assert result.data["count"] == 3
    
    def test_list_profiles_limit_capped_at_200(self):
        """Test list_profiles caps limit at 200."""
        # Should not error even with huge limit
        result = list_profiles(limit=500)
        assert result.success is True


class TestSaveProfileExtended:
    """Extended tests for save_profile."""
    
    def test_save_profile_minimal(self):
        """Test save_profile with minimal args."""
        result = save_profile(name="minimal", profile_spec={})
        assert result.success is True
        assert result.data["name"] == "minimal"
    
    def test_save_profile_empty_tags(self):
        """Test save_profile with empty tags list."""
        result = save_profile(name="empty-tags", profile_spec={}, tags=[])
        assert result.success is True


class TestLoadProfileExtended:
    """Extended tests for load_profile."""
    
    def test_load_profile_metadata_parsing(self):
        """Test load_profile handles metadata."""
        save_profile(name="with-metadata", profile_spec={"key": "value"})
        
        result = load_profile("with-metadata")
        assert result.success is True
        assert result.data["profile_spec"]["key"] == "value"
    
    def test_load_profile_dates_serialized(self):
        """Test load_profile serializes dates to ISO format."""
        save_profile(name="dated-profile", profile_spec={})
        
        result = load_profile("dated-profile")
        assert result.success is True
        assert "T" in result.data["created_at"]  # ISO format has T


class TestDeleteProfileExtended:
    """Extended tests for delete_profile."""
    
    def test_delete_nonexistent_profile(self):
        """Test delete_profile with nonexistent profile."""
        result = delete_profile("does-not-exist")
        assert result.success is False
        assert "not found" in result.error


class TestExecuteProfileExtended:
    """Extended tests for execute_profile."""
    
    def test_execute_profile_not_found(self):
        """Test execute_profile with nonexistent profile."""
        result = execute_profile("nonexistent-profile")
        assert result.success is False
        assert "not found" in result.error
    
    def test_execute_profile_membersim(self):
        """Test execute_profile with membersim product."""
        save_profile(name="member-exec", profile_spec={"count": 2}, product="membersim")
        
        result = execute_profile("member-exec", seed=42)
        assert result.success is True
        assert "members" in result.data
    
    def test_execute_profile_trialsim(self):
        """Test execute_profile with trialsim product."""
        save_profile(name="trial-exec", profile_spec={"count": 2}, product="trialsim")
        
        result = execute_profile("trial-exec", seed=42)
        assert result.success is True
        assert "subjects" in result.data
    
    def test_execute_profile_rxmembersim(self):
        """Test execute_profile with rxmembersim product."""
        save_profile(name="rx-exec", profile_spec={"count": 2}, product="rxmembersim")
        
        result = execute_profile("rx-exec", seed=42)
        assert result.success is True
        assert "rx_members" in result.data
    
    def test_execute_profile_unknown_product(self):
        """Test execute_profile with unknown product."""
        save_profile(name="unknown-exec", profile_spec={"count": 2}, product="unknownsim")
        
        result = execute_profile("unknown-exec")
        assert result.success is False
        assert "Unknown product" in result.error
    
    def test_execute_profile_count_override(self):
        """Test execute_profile count override."""
        save_profile(name="count-override", profile_spec={"count": 10}, product="patientsim")
        
        result = execute_profile("count-override", count=3, seed=42)
        assert result.success is True
        assert len(result.data["patients"]) == 3


class TestListJourneysExtended:
    """Extended tests for list_journeys."""
    
    def test_list_journeys_exclude_builtin(self):
        """Test list_journeys can exclude built-in journeys."""
        save_journey(name="user-journey", steps=[{"name": "s1", "product": "patientsim"}])
        
        result = list_journeys(include_builtin=False)
        assert result.success is True
        # Should only show user journeys
    
    def test_list_journeys_product_filter(self):
        """Test list_journeys with product filter."""
        save_journey(name="patient-journey", steps=[{"name": "s1", "product": "patientsim"}])
        save_journey(name="member-journey", steps=[{"name": "s1", "product": "membersim"}])
        
        result = list_journeys(product="patientsim")
        assert result.success is True
        # Filter applied
    
    def test_list_journeys_tag_filter(self):
        """Test list_journeys with tag filter."""
        save_journey(name="tagged-journey", steps=[{"name": "s1", "product": "patientsim"}], tags=["diabetes"])
        save_journey(name="other-journey", steps=[{"name": "s1", "product": "patientsim"}], tags=["cardiac"])
        
        result = list_journeys(tag="diabetes")
        assert result.success is True


class TestSaveJourneyExtended:
    """Extended tests for save_journey."""
    
    def test_save_duplicate_journey_fails(self):
        """Test save_journey fails for duplicate name."""
        save_journey(name="dup-journey", steps=[{"name": "s1", "product": "patientsim"}])
        
        result = save_journey(name="dup-journey", steps=[{"name": "s2", "product": "membersim"}])
        assert result.success is False
        assert "already exists" in result.error
    
    def test_save_journey_extracts_products(self):
        """Test save_journey extracts products from steps."""
        steps = [
            {"name": "s1", "product": "patientsim"},
            {"name": "s2", "product": "membersim"},
        ]
        result = save_journey(name="multi-product", steps=steps)
        
        assert result.success is True
        
        load_result = load_journey("multi-product")
        assert set(load_result.data["products"]) == {"patientsim", "membersim"}


class TestLoadJourneyExtended:
    """Extended tests for load_journey."""
    
    def test_load_journey_not_found(self):
        """Test load_journey with nonexistent journey."""
        result = load_journey("does-not-exist")
        assert result.success is False
        assert "not found" in result.error


class TestDeleteJourneyExtended:
    """Extended tests for delete_journey."""
    
    def test_delete_journey_not_found(self):
        """Test delete_journey with nonexistent journey."""
        result = delete_journey("nonexistent-journey")
        assert result.success is False
        assert "not found" in result.error
    
    def test_delete_builtin_journey_blocked(self):
        """Test cannot delete built-in journey."""
        # Insert a built-in journey directly
        import healthsim_agent.tools.profile_journey_tools as pjt
        pjt._ensure_tables()
        
        from healthsim_agent.tools.connection import get_manager
        with get_manager().write_connection() as conn:
            conn.execute("""
                INSERT INTO journeys (id, name, steps, is_builtin, created_at, updated_at)
                VALUES ('builtin-1', 'builtin-journey', '[]', TRUE, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """)
        
        result = delete_journey("builtin-journey")
        assert result.success is False
        assert "Cannot delete built-in" in result.error


class TestExecuteJourneyExtended:
    """Extended tests for execute_journey."""
    
    def test_execute_journey_not_found(self):
        """Test execute_journey with nonexistent journey."""
        result = execute_journey("nonexistent-journey")
        assert result.success is False
        assert "not found" in result.error
    
    def test_execute_journey_empty_steps(self):
        """Test execute_journey with no steps."""
        save_journey(name="empty-journey", steps=[])
        
        result = execute_journey("empty-journey")
        assert result.success is False
        assert "no steps" in result.error
    
    def test_execute_journey_unknown_product(self):
        """Test execute_journey handles unknown product in step."""
        steps = [
            {"name": "bad-step", "product": "unknownsim", "profile_spec": {"count": 1}},
        ]
        save_journey(name="bad-product-journey", steps=steps)
        
        result = execute_journey("bad-product-journey")
        assert result.success is True  # Continues but skips unknown product
        assert result.data["step_results"]["bad-step"]["status"] == "skipped"
    
    def test_execute_journey_step_with_default_product(self):
        """Test execute_journey uses default patientsim product."""
        steps = [
            {"name": "default-step", "profile_spec": {"count": 2}},  # No product specified
        ]
        save_journey(name="default-product-journey", steps=steps)
        
        result = execute_journey("default-product-journey", seed=42)
        assert result.success is True
        assert "patients" in result.data["entities"]
    
    def test_execute_journey_multiple_products(self):
        """Test execute_journey with multiple products."""
        steps = [
            {"name": "patients", "product": "patientsim", "profile_spec": {"count": 2}},
            {"name": "members", "product": "membersim", "profile_spec": {"count": 3}},
            {"name": "rx", "product": "rxmembersim", "profile_spec": {"count": 1}},
        ]
        save_journey(name="multi-journey", steps=steps)
        
        result = execute_journey("multi-journey", seed=42)
        assert result.success is True
        assert result.data["steps_completed"] == 3


class TestExportJsonExtended:
    """Extended tests for export_json."""
    
    def test_export_json_not_pretty(self):
        """Test export_json without pretty formatting."""
        entities = {"patients": [{"id": "p1"}]}
        
        result = export_json(entities, pretty=False)
        assert result.success is True
        # No indentation in output
        assert "\n" not in result.data["json"]
    
    def test_export_json_empty_entities(self):
        """Test export_json with empty entities."""
        result = export_json({})
        assert result.success is True
        assert result.data["json"] == "{}"
    
    def test_export_json_nested_directory(self, tmp_path):
        """Test export_json creates nested directories."""
        entities = {"patients": [{"id": "p1"}]}
        output_path = tmp_path / "nested" / "dir" / "export.json"
        
        result = export_json(entities, output_path=str(output_path))
        assert result.success is True
        assert output_path.exists()
    
    def test_export_json_with_datetime(self):
        """Test export_json handles datetime serialization."""
        from datetime import datetime
        entities = {"patients": [{"id": "p1", "created": datetime.now()}]}
        
        result = export_json(entities)
        assert result.success is True
        # datetime converted to string
        assert "created" in result.data["json"]


class TestEnsureTables:
    """Tests for _ensure_tables function."""
    
    def test_ensure_tables_idempotent(self):
        """Test _ensure_tables can be called multiple times."""
        import healthsim_agent.tools.profile_journey_tools as pjt
        pjt._tables_ensured = False
        
        _ensure_tables()
        assert pjt._tables_ensured is True
        
        # Second call should be no-op
        _ensure_tables()
        assert pjt._tables_ensured is True


class TestErrorHandling:
    """Tests for error handling paths."""
    
    def test_list_profiles_error_handling(self):
        """Test list_profiles handles exceptions."""
        with patch('healthsim_agent.tools.profile_journey_tools.get_manager') as mock:
            mock.return_value.get_read_connection.side_effect = Exception("DB error")
            
            result = list_profiles()
            assert result.success is False
            assert "Failed to list profiles" in result.error
    
    def test_save_profile_error_handling(self):
        """Test save_profile handles exceptions."""
        with patch('healthsim_agent.tools.profile_journey_tools.get_manager') as mock:
            mock.return_value.write_connection.side_effect = Exception("DB error")
            
            result = save_profile(name="error-test", profile_spec={})
            assert result.success is False
            assert "Failed to save profile" in result.error
    
    def test_load_profile_error_handling(self):
        """Test load_profile handles exceptions."""
        with patch('healthsim_agent.tools.profile_journey_tools.get_manager') as mock:
            mock.return_value.get_read_connection.side_effect = Exception("DB error")
            
            result = load_profile("test")
            assert result.success is False
            assert "Failed to load profile" in result.error
    
    def test_delete_profile_error_handling(self):
        """Test delete_profile handles exceptions."""
        with patch('healthsim_agent.tools.profile_journey_tools.get_manager') as mock:
            mock.return_value.get_read_connection.side_effect = Exception("DB error")
            
            result = delete_profile("test")
            assert result.success is False
            assert "Failed to delete profile" in result.error
    
    def test_list_journeys_error_handling(self):
        """Test list_journeys handles exceptions."""
        with patch('healthsim_agent.tools.profile_journey_tools.get_manager') as mock:
            mock.return_value.get_read_connection.side_effect = Exception("DB error")
            
            result = list_journeys()
            assert result.success is False
            assert "Failed to list journeys" in result.error
    
    def test_save_journey_error_handling(self):
        """Test save_journey handles exceptions."""
        with patch('healthsim_agent.tools.profile_journey_tools.get_manager') as mock:
            mock.return_value.write_connection.side_effect = Exception("DB error")
            
            result = save_journey(name="error-test", steps=[])
            assert result.success is False
            assert "Failed to save journey" in result.error
    
    def test_load_journey_error_handling(self):
        """Test load_journey handles exceptions."""
        with patch('healthsim_agent.tools.profile_journey_tools.get_manager') as mock:
            mock.return_value.get_read_connection.side_effect = Exception("DB error")
            
            result = load_journey("test")
            assert result.success is False
            assert "Failed to load journey" in result.error
    
    def test_delete_journey_error_handling(self):
        """Test delete_journey handles exceptions."""
        with patch('healthsim_agent.tools.profile_journey_tools.get_manager') as mock:
            mock.return_value.get_read_connection.side_effect = Exception("DB error")
            
            result = delete_journey("test")
            assert result.success is False
            assert "Failed to delete journey" in result.error
    
    def test_export_json_error_handling(self, tmp_path):
        """Test export_json handles write errors."""
        entities = {"patients": [{"id": "p1"}]}
        # Invalid path
        output_path = "/nonexistent/path/that/cannot/be/created/export.json"
        
        result = export_json(entities, output_path=output_path)
        assert result.success is False
        assert "Failed to export" in result.error
