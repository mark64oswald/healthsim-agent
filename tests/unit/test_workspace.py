"""
Tests for workspace management.

Tests cover:
- WorkspaceMetadata dataclass
- Workspace class (create, load, save)
- Workspace operations (add/remove cohorts, profiles, journeys)
- Static methods (list_all, delete)
"""

import pytest
from datetime import datetime
from pathlib import Path
import tempfile
import shutil
import json


class TestWorkspaceMetadata:
    """Tests for WorkspaceMetadata dataclass."""
    
    def test_create_basic_metadata(self):
        """Test creating basic metadata."""
        from healthsim_agent.state.workspace import WorkspaceMetadata
        
        now = datetime.now()
        meta = WorkspaceMetadata(
            id="ws-test",
            name="test-workspace",
            description="Test workspace",
            created_at=now,
            updated_at=now,
        )
        
        assert meta.id == "ws-test"
        assert meta.name == "test-workspace"
        assert meta.description == "Test workspace"
        assert meta.cohort_ids == []
        assert meta.profile_ids == []
        assert meta.journey_ids == []
        assert meta.tags == []
        assert meta.config == {}
    
    def test_create_with_all_fields(self):
        """Test creating metadata with all fields."""
        from healthsim_agent.state.workspace import WorkspaceMetadata
        
        now = datetime.now()
        meta = WorkspaceMetadata(
            id="ws-full",
            name="full-workspace",
            description="Full workspace",
            created_at=now,
            updated_at=now,
            cohort_ids=["coh-1", "coh-2"],
            profile_ids=["prof-1"],
            journey_ids=["jour-1"],
            tags=["diabetes", "test"],
            config={"key": "value"},
        )
        
        assert len(meta.cohort_ids) == 2
        assert len(meta.profile_ids) == 1
        assert "diabetes" in meta.tags
        assert meta.config["key"] == "value"


class TestWorkspace:
    """Tests for Workspace class."""
    
    @pytest.fixture
    def temp_workspace_dir(self):
        """Create a temporary directory for workspace tests."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_create_new_workspace(self, temp_workspace_dir):
        """Test creating a new workspace."""
        from healthsim_agent.state.workspace import Workspace
        
        ws = Workspace("test-project", base_dir=temp_workspace_dir)
        
        assert ws.name == "test-project"
        assert ws.path.exists()
        assert (ws.path / "workspace.json").exists()
        assert ws.cohorts_dir.exists()
        assert ws.profiles_dir.exists()
        assert ws.journeys_dir.exists()
        assert ws.outputs_dir.exists()
    
    def test_load_existing_workspace(self, temp_workspace_dir):
        """Test loading an existing workspace."""
        from healthsim_agent.state.workspace import Workspace
        
        # Create first
        ws1 = Workspace("load-test", base_dir=temp_workspace_dir)
        ws1.add_cohort("coh-123")
        
        # Load again
        ws2 = Workspace("load-test", base_dir=temp_workspace_dir)
        
        assert ws2.name == "load-test"
        assert "coh-123" in ws2.list_cohorts()
    
    def test_workspace_not_found_raises(self, temp_workspace_dir):
        """Test loading non-existent workspace with auto_create=False."""
        from healthsim_agent.state.workspace import Workspace
        
        with pytest.raises(FileNotFoundError):
            Workspace("nonexistent", base_dir=temp_workspace_dir, auto_create=False)
    
    def test_add_cohort(self, temp_workspace_dir):
        """Test adding cohort to workspace."""
        from healthsim_agent.state.workspace import Workspace
        
        ws = Workspace("cohort-test", base_dir=temp_workspace_dir)
        ws.add_cohort("coh-001")
        ws.add_cohort("coh-002")
        
        cohorts = ws.list_cohorts()
        assert "coh-001" in cohorts
        assert "coh-002" in cohorts
        assert len(cohorts) == 2
    
    def test_add_duplicate_cohort_ignored(self, temp_workspace_dir):
        """Test adding same cohort twice is idempotent."""
        from healthsim_agent.state.workspace import Workspace
        
        ws = Workspace("dup-test", base_dir=temp_workspace_dir)
        ws.add_cohort("coh-001")
        ws.add_cohort("coh-001")
        
        assert ws.list_cohorts().count("coh-001") == 1
    
    def test_remove_cohort(self, temp_workspace_dir):
        """Test removing cohort from workspace."""
        from healthsim_agent.state.workspace import Workspace
        
        ws = Workspace("remove-test", base_dir=temp_workspace_dir)
        ws.add_cohort("coh-001")
        ws.add_cohort("coh-002")
        result = ws.remove_cohort("coh-001")
        
        assert result is True
        cohorts = ws.list_cohorts()
        assert "coh-001" not in cohorts
        assert "coh-002" in cohorts
    
    def test_remove_nonexistent_cohort_returns_false(self, temp_workspace_dir):
        """Test removing non-existent cohort returns False."""
        from healthsim_agent.state.workspace import Workspace
        
        ws = Workspace("remove-safe", base_dir=temp_workspace_dir)
        result = ws.remove_cohort("nonexistent")
        
        assert result is False
    
    def test_add_profile(self, temp_workspace_dir):
        """Test adding profile to workspace."""
        from healthsim_agent.state.workspace import Workspace
        
        ws = Workspace("profile-test", base_dir=temp_workspace_dir)
        ws.add_profile("prof-001")
        
        assert "prof-001" in ws.list_profiles()
    
    def test_remove_profile(self, temp_workspace_dir):
        """Test removing profile from workspace."""
        from healthsim_agent.state.workspace import Workspace
        
        ws = Workspace("profile-rm", base_dir=temp_workspace_dir)
        ws.add_profile("prof-001")
        result = ws.remove_profile("prof-001")
        
        assert result is True
        assert "prof-001" not in ws.list_profiles()
    
    def test_add_journey(self, temp_workspace_dir):
        """Test adding journey to workspace."""
        from healthsim_agent.state.workspace import Workspace
        
        ws = Workspace("journey-test", base_dir=temp_workspace_dir)
        ws.add_journey("jour-001")
        
        assert "jour-001" in ws.list_journeys()
    
    def test_remove_journey(self, temp_workspace_dir):
        """Test removing journey from workspace."""
        from healthsim_agent.state.workspace import Workspace
        
        ws = Workspace("journey-rm", base_dir=temp_workspace_dir)
        ws.add_journey("jour-001")
        result = ws.remove_journey("jour-001")
        
        assert result is True
        assert "jour-001" not in ws.list_journeys()
    
    def test_add_tag(self, temp_workspace_dir):
        """Test adding tag to workspace."""
        from healthsim_agent.state.workspace import Workspace
        
        ws = Workspace("tag-test", base_dir=temp_workspace_dir)
        ws.add_tag("diabetes")
        ws.add_tag("chronic")
        
        assert "diabetes" in ws.metadata.tags
        assert "chronic" in ws.metadata.tags
    
    def test_remove_tag(self, temp_workspace_dir):
        """Test removing tag from workspace."""
        from healthsim_agent.state.workspace import Workspace
        
        ws = Workspace("tag-rm", base_dir=temp_workspace_dir)
        ws.add_tag("diabetes")
        result = ws.remove_tag("diabetes")
        
        assert result is True
        assert "diabetes" not in ws.metadata.tags
    
    def test_update_description(self, temp_workspace_dir):
        """Test updating workspace description."""
        from healthsim_agent.state.workspace import Workspace
        
        ws = Workspace("desc-test", base_dir=temp_workspace_dir)
        ws.update_description("Test description")
        
        # Reload and verify
        ws2 = Workspace("desc-test", base_dir=temp_workspace_dir)
        assert ws2.metadata.description == "Test description"
    
    def test_set_and_get_config(self, temp_workspace_dir):
        """Test setting and getting workspace config."""
        from healthsim_agent.state.workspace import Workspace
        
        ws = Workspace("config-test", base_dir=temp_workspace_dir)
        ws.set_config("key1", "value1")
        ws.set_config("key2", {"nested": True})
        
        assert ws.get_config("key1") == "value1"
        assert ws.get_config("key2")["nested"] is True
    
    def test_get_config_default(self, temp_workspace_dir):
        """Test getting config with default."""
        from healthsim_agent.state.workspace import Workspace
        
        ws = Workspace("config-default", base_dir=temp_workspace_dir)
        
        assert ws.get_config("missing") is None
        assert ws.get_config("missing", "default") == "default"
    
    def test_metadata_property(self, temp_workspace_dir):
        """Test metadata property returns WorkspaceMetadata."""
        from healthsim_agent.state.workspace import Workspace, WorkspaceMetadata
        
        ws = Workspace("meta-test", base_dir=temp_workspace_dir)
        
        assert isinstance(ws.metadata, WorkspaceMetadata)
        assert ws.metadata.name == "meta-test"
    
    def test_path_property(self, temp_workspace_dir):
        """Test path property returns correct path."""
        from healthsim_agent.state.workspace import Workspace
        
        ws = Workspace("path-test", base_dir=temp_workspace_dir)
        
        assert ws.path == temp_workspace_dir / "path-test"
        assert ws.path.exists()


class TestWorkspaceStaticMethods:
    """Tests for Workspace static/class methods."""
    
    @pytest.fixture
    def temp_workspace_dir(self):
        """Create a temporary directory for workspace tests."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_list_all_empty(self, temp_workspace_dir):
        """Test listing workspaces when none exist."""
        from healthsim_agent.state.workspace import Workspace
        
        result = Workspace.list_all(base_dir=temp_workspace_dir)
        
        assert result == []
    
    def test_list_all_with_workspaces(self, temp_workspace_dir):
        """Test listing multiple workspaces."""
        from healthsim_agent.state.workspace import Workspace
        
        Workspace("project-a", base_dir=temp_workspace_dir)
        Workspace("project-b", base_dir=temp_workspace_dir)
        
        result = Workspace.list_all(base_dir=temp_workspace_dir)
        
        names = [ws.name for ws in result]
        assert "project-a" in names
        assert "project-b" in names
    
    def test_delete_workspace(self, temp_workspace_dir):
        """Test deleting a workspace."""
        from healthsim_agent.state.workspace import Workspace
        
        ws = Workspace("delete-me", base_dir=temp_workspace_dir)
        ws_path = ws.path
        
        assert ws_path.exists()
        
        Workspace.delete("delete-me", base_dir=temp_workspace_dir)
        
        assert not ws_path.exists()
    
    def test_delete_nonexistent_workspace(self, temp_workspace_dir):
        """Test deleting non-existent workspace is safe."""
        from healthsim_agent.state.workspace import Workspace
        
        # Should not raise
        Workspace.delete("nonexistent", base_dir=temp_workspace_dir)
    
    def test_exists(self, temp_workspace_dir):
        """Test checking if workspace exists."""
        from healthsim_agent.state.workspace import Workspace
        
        assert not Workspace.exists("maybe", base_dir=temp_workspace_dir)
        
        Workspace("maybe", base_dir=temp_workspace_dir)
        
        assert Workspace.exists("maybe", base_dir=temp_workspace_dir)
