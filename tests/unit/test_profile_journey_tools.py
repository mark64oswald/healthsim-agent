"""Tests for profile and journey tools.

These tests verify profile and journey management functionality.
Uses a separate test database to avoid affecting production data.
"""

import pytest
import os
import tempfile
from pathlib import Path

from healthsim_agent.tools.profile_journey_tools import (
    list_profiles, save_profile, load_profile, delete_profile, execute_profile,
    list_journeys, save_journey, load_journey, delete_journey, execute_journey,
    export_json, _ensure_tables,
)
from healthsim_agent.tools.connection import get_manager, reset_manager


@pytest.fixture(autouse=True)
def use_test_database(tmp_path):
    """Use a temporary database for tests."""
    # Create temp database path
    test_db = tmp_path / "test_healthsim.duckdb"
    
    # Reset and configure to use test database
    reset_manager()
    os.environ["HEALTHSIM_DB_PATH"] = str(test_db)
    
    # Reset the tables_ensured flag
    import healthsim_agent.tools.profile_journey_tools as pjt
    pjt._tables_ensured = False
    
    yield
    
    # Cleanup
    reset_manager()
    if "HEALTHSIM_DB_PATH" in os.environ:
        del os.environ["HEALTHSIM_DB_PATH"]


class TestProfileTools:
    """Tests for profile management."""
    
    def test_list_profiles_empty(self):
        """List profiles when none exist."""
        result = list_profiles()
        assert result.success is True
        assert result.data["count"] == 0
        assert result.data["profiles"] == []
    
    def test_save_profile(self):
        """Save a new profile."""
        result = save_profile(
            name="test-profile",
            profile_spec={"count": 10, "product": "patientsim"},
            description="Test profile",
            product="patientsim",
            tags=["test", "diabetes"],
        )
        assert result.success is True
        assert "profile_id" in result.data
        assert result.data["name"] == "test-profile"
    
    def test_save_duplicate_profile_fails(self):
        """Cannot save profile with same name."""
        save_profile(name="duplicate-test", profile_spec={"count": 5})
        result = save_profile(name="duplicate-test", profile_spec={"count": 10})
        assert result.success is False
        assert "already exists" in result.error
    
    def test_load_profile_by_name(self):
        """Load profile by name."""
        save_profile(
            name="load-test",
            profile_spec={"count": 20, "age_range": [30, 50]},
            description="Profile for load test",
            product="membersim",
        )
        
        result = load_profile("load-test")
        assert result.success is True
        assert result.data["name"] == "load-test"
        assert result.data["profile_spec"]["count"] == 20
        assert result.data["product"] == "membersim"
    
    def test_load_profile_by_id(self):
        """Load profile by ID."""
        save_result = save_profile(name="id-test", profile_spec={"count": 5})
        profile_id = save_result.data["profile_id"]
        
        result = load_profile(profile_id)
        assert result.success is True
        assert result.data["id"] == profile_id
    
    def test_load_nonexistent_profile(self):
        """Load profile that doesn't exist."""
        result = load_profile("nonexistent-profile")
        assert result.success is False
        assert "not found" in result.error
    
    def test_delete_profile(self):
        """Delete a profile."""
        save_profile(name="delete-me", profile_spec={"count": 1})
        
        result = delete_profile("delete-me")
        assert result.success is True
        
        # Verify deleted
        load_result = load_profile("delete-me")
        assert load_result.success is False
    
    def test_list_profiles_with_filter(self):
        """List profiles with product filter."""
        save_profile(name="patient-profile", profile_spec={}, product="patientsim")
        save_profile(name="member-profile", profile_spec={}, product="membersim")
        
        result = list_profiles(product="patientsim")
        assert result.success is True
        assert result.data["count"] == 1
        assert result.data["profiles"][0]["name"] == "patient-profile"
    
    def test_execute_profile(self):
        """Execute a saved profile."""
        save_profile(
            name="exec-test",
            profile_spec={"count": 3},
            product="patientsim",
        )
        
        result = execute_profile("exec-test", count=2, seed=42)
        assert result.success is True
        assert "patients" in result.data
        assert result.metadata.get("profile_name") == "exec-test"


class TestJourneyTools:
    """Tests for journey management."""
    
    def test_list_journeys_empty(self):
        """List journeys when none exist."""
        result = list_journeys()
        assert result.success is True
        assert result.data["count"] == 0
    
    def test_save_journey(self):
        """Save a new journey."""
        steps = [
            {"name": "create_patients", "product": "patientsim", "profile_spec": {"count": 5}},
            {"name": "create_claims", "product": "membersim", "profile_spec": {"count": 10}},
        ]
        
        result = save_journey(
            name="test-journey",
            steps=steps,
            description="Test journey",
            tags=["test"],
        )
        assert result.success is True
        assert "journey_id" in result.data
        assert result.data["steps_count"] == 2
    
    def test_load_journey(self):
        """Load a saved journey."""
        steps = [
            {"name": "step1", "product": "patientsim", "profile_spec": {"count": 3}},
        ]
        save_journey(name="load-journey-test", steps=steps)
        
        result = load_journey("load-journey-test")
        assert result.success is True
        assert result.data["name"] == "load-journey-test"
        assert len(result.data["steps"]) == 1
    
    def test_delete_journey(self):
        """Delete a journey."""
        save_journey(name="delete-journey", steps=[{"name": "s1", "product": "patientsim"}])
        
        result = delete_journey("delete-journey")
        assert result.success is True
        
        # Verify deleted
        load_result = load_journey("delete-journey")
        assert load_result.success is False
    
    def test_execute_journey(self):
        """Execute a saved journey."""
        steps = [
            {"name": "patients", "product": "patientsim", "profile_spec": {"count": 2}},
            {"name": "members", "product": "membersim", "profile_spec": {"count": 3}},
        ]
        save_journey(name="exec-journey-test", steps=steps)
        
        result = execute_journey("exec-journey-test", seed=42)
        assert result.success is True
        assert result.data["steps_completed"] == 2
        assert result.data["steps_total"] == 2
        assert "patients" in result.data["entities"]
        assert "members" in result.data["entities"]


class TestExportJson:
    """Tests for JSON export."""
    
    def test_export_json_to_string(self):
        """Export entities to JSON string."""
        entities = {"patients": [{"id": "p1", "name": "Test"}]}
        
        result = export_json(entities)
        assert result.success is True
        assert "json" in result.data
        assert '"patients"' in result.data["json"]
    
    def test_export_json_to_file(self, tmp_path):
        """Export entities to JSON file."""
        entities = {"patients": [{"id": "p1"}, {"id": "p2"}]}
        output_path = tmp_path / "export.json"
        
        result = export_json(entities, output_path=str(output_path))
        assert result.success is True
        assert output_path.exists()
        
        import json
        with open(output_path) as f:
            data = json.load(f)
        assert len(data["patients"]) == 2
