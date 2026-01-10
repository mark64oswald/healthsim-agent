"""Tests for healthsim_agent.tools.cohort_tools module."""

import pytest
from pathlib import Path
import tempfile
import os
from datetime import datetime

import duckdb

from healthsim_agent.tools import reset_manager
from healthsim_agent.tools.connection import ConnectionManager
from healthsim_agent.tools.cohort_tools import (
    list_cohorts,
    load_cohort,
    save_cohort,
    add_entities,
    delete_cohort,
)


@pytest.fixture
def temp_db_env(monkeypatch):
    """Create a temporary database and set environment."""
    with tempfile.NamedTemporaryFile(suffix=".duckdb", delete=False) as f:
        db_path = f.name
    os.unlink(db_path)  # Delete empty file so DuckDB can create fresh
    
    # Initialize schema
    conn = duckdb.connect(db_path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS cohorts (
            id VARCHAR PRIMARY KEY,
            name VARCHAR NOT NULL UNIQUE,
            description VARCHAR,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute("CREATE SEQUENCE IF NOT EXISTS cohort_tags_seq START 1")
    conn.execute("CREATE SEQUENCE IF NOT EXISTS cohort_entities_seq START 1")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS cohort_entities (
            id INTEGER PRIMARY KEY,
            cohort_id VARCHAR,
            entity_type VARCHAR,
            entity_id VARCHAR,
            entity_data JSON,
            created_at TIMESTAMP
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS cohort_tags (
            id INTEGER PRIMARY KEY,
            cohort_id VARCHAR,
            tag VARCHAR
        )
    """)
    conn.close()
    
    # Set environment and reset manager
    monkeypatch.setenv("HEALTHSIM_DB_PATH", db_path)
    reset_manager()
    
    yield db_path
    
    # Cleanup
    reset_manager()
    try:
        os.unlink(db_path)
    except Exception:
        pass


class TestListCohorts:
    """Tests for list_cohorts function."""
    
    def test_list_empty(self, temp_db_env):
        """Test listing when no cohorts exist."""
        result = list_cohorts()
        assert result.success
        assert result.data == []
    
    def test_list_with_cohorts(self, temp_db_env):
        """Test listing after adding cohorts."""
        # Add some test cohorts directly
        conn = duckdb.connect(temp_db_env)
        conn.execute("""
            INSERT INTO cohorts (id, name, description)
            VALUES 
                ('id1', 'Cohort A', 'First cohort'),
                ('id2', 'Cohort B', 'Second cohort')
        """)
        conn.close()
        reset_manager()
        
        result = list_cohorts()
        assert result.success
        assert len(result.data) == 2
        names = [c["name"] for c in result.data]
        assert "Cohort A" in names
        assert "Cohort B" in names
    
    def test_list_with_limit(self, temp_db_env):
        """Test limit parameter."""
        conn = duckdb.connect(temp_db_env)
        for i in range(5):
            conn.execute(f"INSERT INTO cohorts (id, name) VALUES ('id{i}', 'Cohort {i}')")
        conn.close()
        reset_manager()
        
        result = list_cohorts(limit=3)
        assert result.success
        assert len(result.data) <= 3


class TestSaveCohort:
    """Tests for save_cohort function."""
    
    def test_save_basic(self, temp_db_env):
        """Test saving a basic cohort."""
        result = save_cohort(
            name="Test Cohort",
            entities={"patients": [{"patient_id": "P001", "name": "John"}]}
        )
        assert result.success
        assert "cohort_id" in result.data
        assert result.data["name"] == "Test Cohort"
        assert result.data["entity_counts"]["patients"] == 1
    
    def test_save_empty_name_rejected(self, temp_db_env):
        """Test that empty name is rejected."""
        result = save_cohort(name="", entities={"patients": []})
        assert not result.success
        assert "required" in result.error.lower()
    
    def test_save_empty_entities_rejected(self, temp_db_env):
        """Test that empty entities is rejected."""
        result = save_cohort(name="Test", entities={})
        assert not result.success
    
    def test_save_reference_type_rejected(self, temp_db_env):
        """Test that reference types are rejected by default."""
        result = save_cohort(
            name="Test",
            entities={"providers": [{"npi": "123"}]}
        )
        assert not result.success
        assert "REFERENCE DATA" in result.error
    
    def test_save_reference_type_with_override(self, temp_db_env):
        """Test that reference types allowed with override."""
        result = save_cohort(
            name="Test Providers",
            entities={"providers": [{"npi": "123"}]},
            allow_reference_entities=True
        )
        assert result.success


class TestAddEntities:
    """Tests for add_entities function."""
    
    def test_add_creates_new_cohort(self, temp_db_env):
        """Test add_entities creates new cohort."""
        result = add_entities(
            cohort_name="New Cohort",
            entities={"patients": [{"patient_id": "P001"}]}
        )
        assert result.success
        assert result.data["is_new_cohort"] is True
        assert result.data["cohort_name"] == "New Cohort"
    
    def test_add_to_existing(self, temp_db_env):
        """Test add_entities to existing cohort."""
        # First create
        result1 = add_entities(
            cohort_name="Existing",
            entities={"patients": [{"patient_id": "P001"}]}
        )
        cohort_id = result1.data["cohort_id"]
        
        # Then add more
        result2 = add_entities(
            cohort_id=cohort_id,
            entities={"patients": [{"patient_id": "P002"}]}
        )
        assert result2.success
        assert result2.data["is_new_cohort"] is False
        assert result2.data["cohort_totals"]["total_entities"] == 2
    
    def test_add_different_entity_types(self, temp_db_env):
        """Test adding different entity types to same cohort."""
        result1 = add_entities(
            cohort_name="Mixed",
            entities={"patients": [{"patient_id": "P001"}]}
        )
        cohort_id = result1.data["cohort_id"]
        
        result2 = add_entities(
            cohort_id=cohort_id,
            entities={"members": [{"member_id": "M001"}]}
        )
        assert result2.success
        assert "patients" in result2.data["cohort_totals"]["by_type"]
        assert "members" in result2.data["cohort_totals"]["by_type"]
    
    def test_add_requires_identifier(self, temp_db_env):
        """Test that either cohort_id or cohort_name is required."""
        result = add_entities(entities={"patients": []})
        assert not result.success
        assert "cohort_id" in result.error or "cohort_name" in result.error
    
    def test_add_nonexistent_cohort_id(self, temp_db_env):
        """Test adding to nonexistent cohort ID fails."""
        result = add_entities(
            cohort_id="nonexistent-uuid",
            entities={"patients": [{"patient_id": "P001"}]}
        )
        assert not result.success
        assert "not found" in result.error.lower()
    
    def test_add_with_batch_info(self, temp_db_env):
        """Test batch tracking info is included."""
        result = add_entities(
            cohort_name="Batched",
            entities={"patients": [{"patient_id": "P001"}]},
            batch_number=1,
            total_batches=5
        )
        assert result.success
        assert result.data["batch_number"] == 1
        assert result.data["total_batches"] == 5
        assert result.data["batches_remaining"] == 4


class TestLoadCohort:
    """Tests for load_cohort function."""
    
    def test_load_by_name(self, temp_db_env):
        """Test loading cohort by name."""
        # Create first
        add_entities(
            cohort_name="LoadTest",
            entities={"patients": [{"patient_id": "P001", "name": "Test"}]}
        )
        reset_manager()
        
        result = load_cohort("LoadTest")
        assert result.success
        assert result.data["name"] == "LoadTest"
    
    def test_load_nonexistent(self, temp_db_env):
        """Test loading nonexistent cohort fails."""
        result = load_cohort("DoesNotExist")
        assert not result.success
    
    def test_load_empty_name(self, temp_db_env):
        """Test empty name is rejected."""
        result = load_cohort("")
        assert not result.success


class TestDeleteCohort:
    """Tests for delete_cohort function."""
    
    def test_delete_requires_confirm(self, temp_db_env):
        """Test delete requires confirm=True."""
        result = delete_cohort("anything")
        assert not result.success
        assert "confirm" in result.error.lower()
    
    def test_delete_nonexistent(self, temp_db_env):
        """Test deleting nonexistent cohort."""
        result = delete_cohort("nonexistent", confirm=True)
        assert not result.success
    
    def test_delete_existing(self, temp_db_env):
        """Test deleting existing cohort."""
        # Create first
        add_entities(
            cohort_name="ToDelete",
            entities={"patients": [{"patient_id": "P001"}]}
        )
        reset_manager()
        
        # Delete
        result = delete_cohort("ToDelete", confirm=True)
        assert result.success
        
        # Verify gone
        list_result = list_cohorts()
        names = [c["name"] for c in list_result.data]
        assert "ToDelete" not in names
    
    def test_delete_empty_name(self, temp_db_env):
        """Test empty name is rejected."""
        result = delete_cohort("", confirm=True)
        assert not result.success
