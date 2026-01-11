"""
Tests for profile persistence.

Tests cover:
- ProfileRecord, ExecutionRecord, ProfileSummary dataclasses
- ProfileManager CRUD operations
- Profile versioning
- Execution history tracking
"""

import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch
import json


class TestProfileRecord:
    """Tests for ProfileRecord dataclass."""
    
    def test_create_basic_record(self):
        """Test creating a basic ProfileRecord."""
        from healthsim_agent.state.profile_manager import ProfileRecord
        
        now = datetime.now()
        record = ProfileRecord(
            id="profile-abc123",
            name="test-profile",
            description="Test description",
            version=1,
            profile_spec={"count": 10},
            product="patientsim",
            tags=["test"],
            created_at=now,
            updated_at=now,
        )
        
        assert record.id == "profile-abc123"
        assert record.name == "test-profile"
        assert record.version == 1
        assert record.profile_spec["count"] == 10
        assert "test" in record.tags
    
    def test_create_with_metadata(self):
        """Test ProfileRecord with metadata."""
        from healthsim_agent.state.profile_manager import ProfileRecord
        
        now = datetime.now()
        record = ProfileRecord(
            id="profile-abc123",
            name="test-profile",
            description=None,
            version=2,
            profile_spec={},
            product=None,
            tags=[],
            created_at=now,
            updated_at=now,
            metadata={"author": "test-user"},
        )
        
        assert record.metadata["author"] == "test-user"


class TestExecutionRecord:
    """Tests for ExecutionRecord dataclass."""
    
    def test_create_execution_record(self):
        """Test creating an ExecutionRecord."""
        from healthsim_agent.state.profile_manager import ExecutionRecord
        
        now = datetime.now()
        record = ExecutionRecord(
            id=1,
            profile_id="profile-abc123",
            cohort_id="cohort-xyz",
            executed_at=now,
            seed=42,
            count=100,
            duration_ms=1500,
            status="completed",
        )
        
        assert record.id == 1
        assert record.profile_id == "profile-abc123"
        assert record.cohort_id == "cohort-xyz"
        assert record.seed == 42
        assert record.count == 100
        assert record.status == "completed"
    
    def test_create_failed_execution(self):
        """Test ExecutionRecord for failed execution."""
        from healthsim_agent.state.profile_manager import ExecutionRecord
        
        now = datetime.now()
        record = ExecutionRecord(
            id=2,
            profile_id="profile-abc123",
            cohort_id=None,
            executed_at=now,
            seed=None,
            count=0,
            duration_ms=500,
            status="failed",
            error_message="Database connection error",
        )
        
        assert record.status == "failed"
        assert record.error_message == "Database connection error"
        assert record.cohort_id is None


class TestProfileSummary:
    """Tests for ProfileSummary dataclass."""
    
    def test_create_summary(self):
        """Test creating a ProfileSummary."""
        from healthsim_agent.state.profile_manager import ProfileSummary
        
        now = datetime.now()
        summary = ProfileSummary(
            id="profile-abc123",
            name="diabetes-profile",
            description="Diabetic patient profile",
            version=3,
            product="patientsim",
            tags=["diabetes", "chronic"],
            created_at=now,
            execution_count=5,
            last_executed=now,
        )
        
        assert summary.name == "diabetes-profile"
        assert summary.version == 3
        assert summary.execution_count == 5
        assert "diabetes" in summary.tags
    
    def test_create_summary_defaults(self):
        """Test ProfileSummary with default values."""
        from healthsim_agent.state.profile_manager import ProfileSummary
        
        now = datetime.now()
        summary = ProfileSummary(
            id="profile-new",
            name="new-profile",
            description=None,
            version=1,
            product=None,
            tags=[],
            created_at=now,
        )
        
        assert summary.execution_count == 0
        assert summary.last_executed is None


class TestProfileManager:
    """Tests for ProfileManager class."""
    
    def test_init_with_connection(self):
        """Test initializing with connection."""
        from healthsim_agent.state.profile_manager import ProfileManager
        
        mock_conn = MagicMock()
        manager = ProfileManager(connection=mock_conn)
        
        assert manager._conn is mock_conn
        assert manager._tables_ensured is False
    
    def test_init_without_connection(self):
        """Test initializing without connection (lazy load)."""
        from healthsim_agent.state.profile_manager import ProfileManager
        
        manager = ProfileManager()
        
        assert manager._conn is None
    
    def test_ensure_tables_creates_tables(self):
        """Test _ensure_tables creates necessary tables."""
        from healthsim_agent.state.profile_manager import ProfileManager
        
        mock_conn = MagicMock()
        # First check returns 0 (tables don't exist)
        mock_result = MagicMock()
        mock_result.rows = [[0]]
        mock_conn.execute.return_value = mock_result
        
        manager = ProfileManager(connection=mock_conn)
        manager._ensure_tables()
        
        assert manager._tables_ensured is True
        # Should have called execute multiple times for CREATE statements
        assert mock_conn.execute.call_count >= 3
    
    def test_ensure_tables_skips_if_exists(self):
        """Test _ensure_tables skips if tables exist."""
        from healthsim_agent.state.profile_manager import ProfileManager
        
        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_result.rows = [[1]]  # Tables exist
        mock_conn.execute.return_value = mock_result
        
        manager = ProfileManager(connection=mock_conn)
        manager._ensure_tables()
        
        # Should only call execute once for the check
        assert mock_conn.execute.call_count == 1
    
    def test_save_profile_new(self):
        """Test saving a new profile."""
        from healthsim_agent.state.profile_manager import ProfileManager
        
        mock_conn = MagicMock()
        # Tables exist
        mock_tables_result = MagicMock()
        mock_tables_result.rows = [[1]]
        # No existing profile
        mock_existing_result = MagicMock()
        mock_existing_result.rows = []
        
        mock_conn.execute.side_effect = [
            mock_tables_result,  # table check
            mock_existing_result,  # existing check
            None,  # insert
        ]
        
        manager = ProfileManager(connection=mock_conn)
        profile_id = manager.save_profile(
            name="test-profile",
            profile_spec={"count": 10},
            description="Test profile",
            product="patientsim",
            tags=["test"],
        )
        
        assert profile_id.startswith("profile-")
    
    def test_save_profile_duplicate_raises(self):
        """Test saving duplicate profile name raises error."""
        from healthsim_agent.state.profile_manager import ProfileManager
        
        mock_conn = MagicMock()
        mock_tables_result = MagicMock()
        mock_tables_result.rows = [[1]]
        mock_existing_result = MagicMock()
        mock_existing_result.rows = [["existing-id"]]  # Profile exists
        
        mock_conn.execute.side_effect = [
            mock_tables_result,
            mock_existing_result,
        ]
        
        manager = ProfileManager(connection=mock_conn)
        
        with pytest.raises(ValueError, match="already exists"):
            manager.save_profile(name="duplicate", profile_spec={})
    
    def test_load_profile_by_name(self):
        """Test loading profile by name."""
        from healthsim_agent.state.profile_manager import ProfileManager
        
        mock_conn = MagicMock()
        now = datetime.now()
        
        mock_tables_result = MagicMock()
        mock_tables_result.rows = [[1]]
        
        mock_profile_result = MagicMock()
        mock_profile_result.rows = [[
            "profile-abc",
            "test-profile",
            "Description",
            1,
            json.dumps({"count": 10}),
            "patientsim",
            json.dumps(["test"]),
            now,
            now,
            None,
        ]]
        
        mock_conn.execute.side_effect = [
            mock_tables_result,
            mock_profile_result,
        ]
        
        manager = ProfileManager(connection=mock_conn)
        record = manager.load_profile("test-profile")
        
        assert record.name == "test-profile"
        assert record.profile_spec["count"] == 10
        assert "test" in record.tags
    
    def test_load_profile_not_found(self):
        """Test loading non-existent profile raises error."""
        from healthsim_agent.state.profile_manager import ProfileManager
        
        mock_conn = MagicMock()
        mock_tables_result = MagicMock()
        mock_tables_result.rows = [[1]]
        mock_profile_result = MagicMock()
        mock_profile_result.rows = []
        
        mock_conn.execute.side_effect = [
            mock_tables_result,
            mock_profile_result,
        ]
        
        manager = ProfileManager(connection=mock_conn)
        
        with pytest.raises(ValueError, match="not found"):
            manager.load_profile("nonexistent")
    
    def test_delete_profile(self):
        """Test deleting a profile."""
        from healthsim_agent.state.profile_manager import ProfileManager
        
        mock_conn = MagicMock()
        mock_tables_result = MagicMock()
        mock_tables_result.rows = [[1]]
        
        mock_conn.execute.return_value = mock_tables_result
        
        manager = ProfileManager(connection=mock_conn)
        result = manager.delete_profile("profile-abc")
        
        # Should have called DELETE
        delete_calls = [c for c in mock_conn.execute.call_args_list 
                       if 'DELETE' in str(c)]
        assert len(delete_calls) >= 1
    
    def test_list_profiles_empty(self):
        """Test listing profiles when none exist."""
        from healthsim_agent.state.profile_manager import ProfileManager
        
        mock_conn = MagicMock()
        mock_tables_result = MagicMock()
        mock_tables_result.rows = [[1]]
        mock_list_result = MagicMock()
        mock_list_result.rows = []
        
        mock_conn.execute.side_effect = [
            mock_tables_result,
            mock_list_result,
        ]
        
        manager = ProfileManager(connection=mock_conn)
        profiles = manager.list_profiles()
        
        assert profiles == []
    
    def test_list_profiles_with_results(self):
        """Test listing profiles with results."""
        from healthsim_agent.state.profile_manager import ProfileManager
        
        mock_conn = MagicMock()
        now = datetime.now()
        
        mock_tables_result = MagicMock()
        mock_tables_result.rows = [[1]]
        
        mock_list_result = MagicMock()
        mock_list_result.rows = [
            ["profile-1", "profile-one", "Desc 1", 1, "patientsim", 
             json.dumps(["test"]), now, 5, now],
            ["profile-2", "profile-two", "Desc 2", 2, "membersim",
             json.dumps([]), now, 0, None],
        ]
        
        mock_conn.execute.side_effect = [
            mock_tables_result,
            mock_list_result,
        ]
        
        manager = ProfileManager(connection=mock_conn)
        profiles = manager.list_profiles()
        
        assert len(profiles) == 2
        assert profiles[0].name == "profile-one"
        assert profiles[0].execution_count == 5
        assert profiles[1].name == "profile-two"
    
    def test_list_profiles_with_tag_filter(self):
        """Test listing profiles filtered by tag."""
        from healthsim_agent.state.profile_manager import ProfileManager
        
        mock_conn = MagicMock()
        mock_tables_result = MagicMock()
        mock_tables_result.rows = [[1]]
        mock_list_result = MagicMock()
        mock_list_result.rows = []
        
        mock_conn.execute.side_effect = [
            mock_tables_result,
            mock_list_result,
        ]
        
        manager = ProfileManager(connection=mock_conn)
        manager.list_profiles(tags=["diabetes"])
        
        # Check that the query included tag filtering
        call_args = mock_conn.execute.call_args_list[-1]
        assert "tags" in str(call_args).lower() or "diabetes" in str(call_args)
    
    def test_record_execution(self):
        """Test recording a profile execution."""
        from healthsim_agent.state.profile_manager import ProfileManager
        
        mock_conn = MagicMock()
        mock_tables_result = MagicMock()
        mock_tables_result.rows = [[1]]
        
        mock_conn.execute.return_value = mock_tables_result
        
        manager = ProfileManager(connection=mock_conn)
        manager.record_execution(
            profile_id="profile-abc",
            cohort_id="cohort-xyz",
            seed=42,
            count=100,
            duration_ms=1500,
        )
        
        # Should have called INSERT for execution
        insert_calls = [c for c in mock_conn.execute.call_args_list
                       if 'INSERT' in str(c) and 'execution' in str(c).lower()]
        assert len(insert_calls) >= 1
    
    def test_get_executions(self):
        """Test getting executions for a profile."""
        from healthsim_agent.state.profile_manager import ProfileManager
        
        mock_conn = MagicMock()
        now = datetime.now()
        
        mock_history_result = MagicMock()
        mock_history_result.rows = [
            [1, "profile-abc", "cohort-1", now, 42, 100, 1500, "completed", None, None],
            [2, "profile-abc", "cohort-2", now, 43, 50, 800, "completed", None, None],
        ]
        
        mock_conn.execute.return_value = mock_history_result
        
        manager = ProfileManager(connection=mock_conn)
        manager._tables_ensured = True  # Skip table check
        history = manager.get_executions("profile-abc")
        
        assert len(history) == 2
        assert history[0].seed == 42
        assert history[1].count == 50
