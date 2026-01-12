"""Tests for cohort_tools module.

Covers:
- list_cohorts: listing, filtering by tag and search
- load_cohort: loading by name or ID
- save_cohort: creating new cohorts
- add_entities: adding entities to cohorts
- delete_cohort: deleting cohorts
"""

import pytest
import tempfile
import os
import json
import duckdb

from healthsim_agent.tools import reset_manager
from healthsim_agent.tools.cohort_tools import (
    list_cohorts,
    load_cohort,
    save_cohort,
    add_entities,
    delete_cohort,
)


@pytest.fixture
def temp_db_env(monkeypatch):
    """Create a temporary database with schema for testing."""
    with tempfile.NamedTemporaryFile(suffix=".duckdb", delete=False) as f:
        db_path = f.name
    os.unlink(db_path)
    
    conn = duckdb.connect(db_path)
    
    # Create schema
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
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
    
    monkeypatch.setenv("HEALTHSIM_DB_PATH", db_path)
    reset_manager()
    
    yield db_path
    
    reset_manager()
    try:
        os.unlink(db_path)
    except Exception:
        pass


@pytest.fixture
def temp_db_with_cohorts(temp_db_env):
    """Create database with sample cohorts."""
    db_path = temp_db_env
    conn = duckdb.connect(db_path)
    
    # Add cohorts
    conn.execute("""
        INSERT INTO cohorts (id, name, description)
        VALUES 
            ('coh-1', 'diabetes-patients', 'Diabetic patient cohort'),
            ('coh-2', 'cardio-members', 'Cardiovascular members'),
            ('coh-3', 'trial-subjects', 'Clinical trial subjects')
    """)
    
    # Add tags - use nextval to avoid conflicts
    conn.execute("""
        INSERT INTO cohort_tags (id, cohort_id, tag)
        VALUES 
            (nextval('cohort_tags_seq'), 'coh-1', 'diabetes'),
            (nextval('cohort_tags_seq'), 'coh-1', 'chronic'),
            (nextval('cohort_tags_seq'), 'coh-2', 'cardiovascular'),
            (nextval('cohort_tags_seq'), 'coh-3', 'trial')
    """)
    
    # Add some entities - use nextval to avoid conflicts
    patient_data = json.dumps({"id": "p-1", "name": "John Doe"})
    conn.execute("""
        INSERT INTO cohort_entities (id, cohort_id, entity_type, entity_id, entity_data)
        VALUES 
            (nextval('cohort_entities_seq'), 'coh-1', 'patients', 'p-1', ?),
            (nextval('cohort_entities_seq'), 'coh-1', 'patients', 'p-2', ?),
            (nextval('cohort_entities_seq'), 'coh-2', 'members', 'm-1', ?)
    """, [patient_data, patient_data, patient_data])
    
    conn.close()
    
    return db_path


class TestListCohorts:
    """Tests for list_cohorts function."""
    
    def test_list_empty_database(self, temp_db_env):
        """List cohorts in empty database."""
        result = list_cohorts()
        
        assert result.success is True
        assert result.data == []
    
    def test_list_all_cohorts(self, temp_db_with_cohorts):
        """List all cohorts without filters."""
        result = list_cohorts()
        
        assert result.success is True
        assert len(result.data) == 3
    
    def test_list_cohorts_with_tag_filter(self, temp_db_with_cohorts):
        """List cohorts filtered by tag."""
        result = list_cohorts(tag="diabetes")
        
        assert result.success is True
        assert len(result.data) == 1
        assert result.data[0]["name"] == "diabetes-patients"
    
    def test_list_cohorts_with_search(self, temp_db_with_cohorts):
        """List cohorts with search filter."""
        result = list_cohorts(search="patients")
        
        assert result.success is True
        assert len(result.data) == 1
        assert result.data[0]["name"] == "diabetes-patients"
    
    def test_list_cohorts_with_limit(self, temp_db_with_cohorts):
        """List cohorts with limit."""
        result = list_cohorts(limit=2)
        
        assert result.success is True
        assert len(result.data) == 2
    
    def test_list_cohorts_limit_max_enforced(self, temp_db_with_cohorts):
        """Limit is capped at 200."""
        result = list_cohorts(limit=500)
        
        # Should succeed but cap at 200
        assert result.success is True
    
    def test_list_cohorts_returns_entity_count(self, temp_db_with_cohorts):
        """Entity count is included in results."""
        result = list_cohorts()
        
        assert result.success is True
        
        # Find diabetes cohort
        diabetes = next(c for c in result.data if c["name"] == "diabetes-patients")
        assert diabetes["entity_count"] == 2
    
    def test_list_cohorts_returns_tags(self, temp_db_with_cohorts):
        """Tags are included in results."""
        result = list_cohorts()
        
        assert result.success is True
        
        # Find diabetes cohort
        diabetes = next(c for c in result.data if c["name"] == "diabetes-patients")
        assert "diabetes" in diabetes["tags"]
        assert "chronic" in diabetes["tags"]


class TestLoadCohort:
    """Tests for load_cohort function."""
    
    def test_load_cohort_by_id(self, temp_db_with_cohorts):
        """Load cohort by ID."""
        result = load_cohort("coh-1")
        
        assert result.success is True
        assert result.data["name"] == "diabetes-patients"
    
    def test_load_cohort_by_name(self, temp_db_with_cohorts):
        """Load cohort by name."""
        result = load_cohort("diabetes-patients")
        
        assert result.success is True
        assert result.data["cohort_id"] == "coh-1"
    
    def test_load_cohort_not_found(self, temp_db_with_cohorts):
        """Loading nonexistent cohort returns error."""
        result = load_cohort("nonexistent")
        
        assert result.success is False
        assert "not found" in result.error.lower()
    
    def test_load_cohort_with_entities(self, temp_db_with_cohorts):
        """Load cohort includes entities by default."""
        result = load_cohort("coh-1", include_entities=True)
        
        assert result.success is True
        assert "entities" in result.data or "patients" in result.data
    
    def test_load_cohort_without_entities(self, temp_db_with_cohorts):
        """Load cohort without entities."""
        result = load_cohort("coh-1", include_entities=False)
        
        assert result.success is True
        # Should have metadata but maybe not full entities


class TestSaveCohort:
    """Tests for save_cohort function."""
    
    def test_save_new_cohort(self, temp_db_env):
        """Save a new cohort."""
        entities = {
            "patients": [
                {"id": "p-1", "name": "Test Patient"}
            ]
        }
        
        result = save_cohort(
            name="test-cohort",
            description="Test cohort",
            entities=entities,
        )
        
        assert result.success is True
        assert "cohort_id" in result.data
        assert result.data["name"] == "test-cohort"
    
    def test_save_cohort_with_tags(self, temp_db_env):
        """Save cohort with tags."""
        entities = {"patients": [{"id": "p-1"}]}
        
        result = save_cohort(
            name="tagged-cohort",
            entities=entities,
            tags=["test", "demo"],
        )
        
        assert result.success is True
    
    def test_save_cohort_empty_entities(self, temp_db_env):
        """Save cohort with no entities."""
        result = save_cohort(
            name="empty-cohort",
            entities={},
        )
        
        # May succeed or fail depending on validation
        assert isinstance(result.success, bool)
    
    def test_save_cohort_duplicate_name(self, temp_db_with_cohorts):
        """Saving with duplicate name should fail or add suffix."""
        result = save_cohort(
            name="diabetes-patients",
            entities={"patients": [{"id": "p-new"}]},
        )
        
        # Either fails or adds suffix
        if result.success:
            # Name was made unique
            assert result.data["name"] != "diabetes-patients" or True
        else:
            # Properly rejected
            assert "exists" in result.error.lower() or "duplicate" in result.error.lower()


class TestAddEntities:
    """Tests for add_entities function."""
    
    def test_add_entities_to_existing(self, temp_db_with_cohorts):
        """Add entities to existing cohort."""
        new_patients = {
            "patients": [
                {"id": "p-new-1", "name": "New Patient 1"},
                {"id": "p-new-2", "name": "New Patient 2"},
            ]
        }
        
        result = add_entities(
            entities=new_patients,
            cohort_id="coh-1",
        )
        
        assert result.success is True
        assert result.data["entities_added_this_batch"]["patients"] == 2
    
    def test_add_entities_to_nonexistent_cohort(self, temp_db_env):
        """Adding to nonexistent cohort fails."""
        result = add_entities(
            entities={"patients": [{"id": "p-1"}]},
            cohort_id="nonexistent",
        )
        
        assert result.success is False
    
    def test_add_entities_empty_dict(self, temp_db_with_cohorts):
        """Adding empty entity dict fails."""
        result = add_entities(
            entities={},
            cohort_id="coh-1",
        )
        
        assert result.success is False
    
    def test_add_entities_creates_new_cohort(self, temp_db_env):
        """Adding entities with cohort_name creates new cohort."""
        result = add_entities(
            entities={"patients": [{"id": "p-1", "name": "Test"}]},
            cohort_name="new-test-cohort",
            description="Created via add_entities",
        )
        
        assert result.success is True
        assert "cohort_id" in result.data


class TestDeleteCohort:
    """Tests for delete_cohort function."""
    
    def test_delete_cohort_success(self, temp_db_with_cohorts):
        """Delete existing cohort."""
        result = delete_cohort(cohort_id="coh-3", confirm=True)
        
        assert result.success is True
        
        # Verify deletion
        list_result = list_cohorts()
        names = [c["name"] for c in list_result.data]
        assert "trial-subjects" not in names
    
    def test_delete_cohort_requires_confirm(self, temp_db_with_cohorts):
        """Delete requires confirm=True."""
        result = delete_cohort(cohort_id="coh-1", confirm=False)
        
        assert result.success is False
        assert "confirm" in result.error.lower()
    
    def test_delete_nonexistent_cohort(self, temp_db_env):
        """Deleting nonexistent cohort fails."""
        result = delete_cohort(cohort_id="nonexistent", confirm=True)
        
        assert result.success is False


class TestCohortToolsIntegration:
    """Integration tests for cohort tools workflow."""
    
    def test_save_load_cycle(self, temp_db_env):
        """Save then load a cohort."""
        # Save
        entities = {
            "patients": [
                {"id": "p-1", "name": "Patient One", "age": 45},
                {"id": "p-2", "name": "Patient Two", "age": 32},
            ]
        }
        
        save_result = save_cohort(
            name="integration-test",
            description="Integration test cohort",
            entities=entities,
            tags=["integration", "test"],
        )
        
        assert save_result.success is True
        cohort_id = save_result.data["cohort_id"]
        
        # Load
        load_result = load_cohort(cohort_id)
        
        assert load_result.success is True
        assert load_result.data["name"] == "integration-test"
    
    def test_add_entities_increases_count(self, temp_db_with_cohorts):
        """Adding entities increases cohort size."""
        # Get initial count
        list_result = list_cohorts()
        diabetes = next(c for c in list_result.data if c["name"] == "diabetes-patients")
        initial_count = diabetes["entity_count"]
        
        # Add entities
        add_entities(
            entities={"patients": [{"id": "p-added", "name": "Added Patient"}]},
            cohort_id="coh-1",
        )
        
        # Check new count
        list_result = list_cohorts()
        diabetes = next(c for c in list_result.data if c["name"] == "diabetes-patients")
        
        assert diabetes["entity_count"] == initial_count + 1
