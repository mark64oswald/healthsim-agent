"""
Tests for StateManager cohort and entity management.
"""
import pytest
import json
from healthsim_agent.state import StateManager, Cohort, CohortSummary


class TestCohort:
    """Test Cohort data structure."""
    
    def test_create_cohort(self):
        """Test cohort creation with defaults."""
        cohort = Cohort(id="test-id", name="test-cohort")
        
        assert cohort.id == "test-id"
        assert cohort.name == "test-cohort"
        assert cohort.entities == {}
        assert cohort.total_entities() == 0
    
    def test_add_entities(self):
        """Test adding entities to cohort."""
        cohort = Cohort(id="c1", name="cohort-1")
        
        cohort.add_entity("patients", {"id": "P001", "name": "John"})
        cohort.add_entity("patients", {"id": "P002", "name": "Jane"})
        cohort.add_entity("claims", {"id": "C001", "amount": 100})
        
        assert cohort.total_entities() == 3
        assert cohort.count_by_type() == {"patients": 2, "claims": 1}
    
    def test_serialization(self):
        """Test cohort to/from dict."""
        cohort = Cohort(
            id="c1",
            name="test",
            description="Test cohort",
            tags=["diabetes", "texas"],
        )
        cohort.add_entity("patients", {"id": "P001"})
        
        data = cohort.to_dict()
        restored = Cohort.from_dict(data)
        
        assert restored.id == cohort.id
        assert restored.name == cohort.name
        assert restored.tags == cohort.tags
        assert restored.total_entities() == 1


class TestStateManager:
    """Test StateManager operations."""
    
    def test_create_cohort(self):
        """Test creating a cohort."""
        manager = StateManager()
        
        cohort = manager.create_cohort(
            name="diabetes-study",
            description="Diabetic patients",
            tags=["diabetes"],
        )
        
        assert cohort.name == "diabetes-study"
        assert cohort.id is not None
        assert manager.active_cohort == cohort
    
    def test_duplicate_name_rejected(self):
        """Test that duplicate names are rejected."""
        manager = StateManager()
        manager.create_cohort(name="study-1")
        
        with pytest.raises(ValueError, match="already exists"):
            manager.create_cohort(name="study-1")
    
    def test_get_cohort_by_name(self):
        """Test finding cohort by name."""
        manager = StateManager()
        cohort = manager.create_cohort(name="my-cohort")
        
        found = manager.get_cohort_by_name("my-cohort")
        assert found == cohort
        
        not_found = manager.get_cohort_by_name("nonexistent")
        assert not_found is None
    
    def test_add_entities(self):
        """Test adding entities to cohort."""
        manager = StateManager()
        cohort = manager.create_cohort(name="test")
        
        patients = [
            {"id": "P001", "name": "Alice"},
            {"id": "P002", "name": "Bob"},
        ]
        
        count = manager.add_entities(cohort.id, "patients", patients)
        
        assert count == 2
        assert len(manager.get_entities(cohort.id, "patients")) == 2
    
    def test_add_entity_invalid_cohort(self):
        """Test adding to nonexistent cohort raises error."""
        manager = StateManager()
        
        with pytest.raises(ValueError, match="not found"):
            manager.add_entities("bad-id", "patients", [{"id": "P001"}])
    
    def test_get_summary(self):
        """Test getting token-efficient summary."""
        manager = StateManager()
        cohort = manager.create_cohort(
            name="summary-test",
            description="Test summary"
        )
        
        # Add several entities
        for i in range(10):
            manager.add_entity(cohort.id, "patients", {"id": f"P{i:03d}"})
        for i in range(5):
            manager.add_entity(cohort.id, "claims", {"id": f"C{i:03d}"})
        
        summary = manager.get_summary(cohort.id)
        
        assert isinstance(summary, CohortSummary)
        assert summary.name == "summary-test"
        assert summary.entity_counts == {"patients": 10, "claims": 5}
        assert summary.total_entities() == 15
        
        # Should have samples (default 2 per type)
        assert len(summary.sample_entities.get("patients", [])) == 2
        assert len(summary.sample_entities.get("claims", [])) == 2
    
    def test_summary_without_samples(self):
        """Test summary without sample entities."""
        manager = StateManager()
        cohort = manager.create_cohort(name="no-samples")
        manager.add_entity(cohort.id, "patients", {"id": "P001"})
        
        summary = manager.get_summary(cohort.id, include_samples=False)
        
        assert summary.sample_entities == {}
    
    def test_export_import(self):
        """Test cohort export and import."""
        manager = StateManager()
        cohort = manager.create_cohort(
            name="export-test",
            tags=["tag1", "tag2"],
        )
        manager.add_entity(cohort.id, "patients", {"id": "P001", "name": "Test"})
        
        # Export to JSON
        json_str = manager.export_cohort_json(cohort.id)
        assert json_str is not None
        
        # Clear and reimport
        manager.clear()
        assert len(manager.list_cohorts()) == 0
        
        imported = manager.import_cohort_json(json_str)
        
        assert imported.name == "export-test"
        assert imported.tags == ["tag1", "tag2"]
        assert imported.total_entities() == 1
    
    def test_delete_cohort(self):
        """Test cohort deletion."""
        manager = StateManager()
        cohort = manager.create_cohort(name="to-delete")
        
        assert manager.delete_cohort(cohort.id) is True
        assert manager.get_cohort(cohort.id) is None
        assert manager.active_cohort is None
    
    def test_list_cohorts(self):
        """Test listing all cohorts."""
        manager = StateManager()
        manager.create_cohort(name="cohort-1")
        manager.create_cohort(name="cohort-2")
        manager.create_cohort(name="cohort-3")
        
        cohorts = manager.list_cohorts()
        
        assert len(cohorts) == 3
        names = {c.name for c in cohorts}
        assert names == {"cohort-1", "cohort-2", "cohort-3"}
    
    def test_statistics(self):
        """Test overall statistics."""
        manager = StateManager()
        
        c1 = manager.create_cohort(name="cohort-1")
        manager.add_entities(c1.id, "patients", [{"id": "P1"}, {"id": "P2"}])
        manager.add_entities(c1.id, "claims", [{"id": "C1"}])
        
        c2 = manager.create_cohort(name="cohort-2")
        manager.add_entities(c2.id, "patients", [{"id": "P3"}])
        
        stats = manager.get_statistics()
        
        assert stats["cohort_count"] == 2
        assert stats["total_entities"] == 4
        assert stats["entities_by_type"]["patients"] == 3
        assert stats["entities_by_type"]["claims"] == 1
