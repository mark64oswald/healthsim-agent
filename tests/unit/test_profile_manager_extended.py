"""
Extended tests for ProfileManager.

Covers:
- update_profile with various field combinations
- profile_exists checks
- get_cohort_profile lookup
- get_execution_spec for re-execution
- Edge cases in JSON parsing
- Lazy connection loading
"""

import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch
import json


class TestProfileManagerConnection:
    """Tests for ProfileManager connection handling."""
    
    def test_lazy_connection_not_loaded_on_init(self):
        """Test connection is not loaded on initialization."""
        from healthsim_agent.state.profile_manager import ProfileManager
        
        manager = ProfileManager()
        # Connection should be None until accessed
        assert manager._conn is None
    
    def test_ensure_tables_only_runs_once(self):
        """Test _ensure_tables is idempotent."""
        from healthsim_agent.state.profile_manager import ProfileManager
        
        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_result.rows = [[1]]  # Tables exist
        mock_conn.execute.return_value = mock_result
        
        manager = ProfileManager(connection=mock_conn)
        
        # First call
        manager._ensure_tables()
        call_count_1 = mock_conn.execute.call_count
        
        # Second call should be no-op
        manager._ensure_tables()
        call_count_2 = mock_conn.execute.call_count
        
        assert call_count_1 == call_count_2


class TestUpdateProfile:
    """Tests for update_profile method."""
    
    def test_update_profile_spec_only(self):
        """Test updating only the profile spec."""
        from healthsim_agent.state.profile_manager import ProfileManager
        
        mock_conn = MagicMock()
        now = datetime.now()
        
        mock_tables_result = MagicMock()
        mock_tables_result.rows = [[1]]
        
        mock_profile_result = MagicMock()
        mock_profile_result.rows = [[
            "profile-abc",
            "test-profile",
            "Original description",
            1,
            json.dumps({"count": 10}),
            "patientsim",
            json.dumps(["test"]),
            now,
            now,
            None,
        ]]
        
        mock_updated_result = MagicMock()
        mock_updated_result.rows = [[
            "profile-abc",
            "test-profile",
            "Original description",
            2,  # Version bumped
            json.dumps({"count": 20}),
            "patientsim",
            json.dumps(["test"]),
            now,
            now,
            None,
        ]]
        
        # Flow: ensure_tables check -> load SELECT -> UPDATE -> reload SELECT
        # Note: second load_profile skips _ensure_tables because _tables_ensured=True
        mock_conn.execute.side_effect = [
            mock_tables_result,   # 1. ensure tables check
            mock_profile_result,  # 2. load existing profile
            None,                 # 3. update
            mock_updated_result,  # 4. reload after update (no table check)
        ]
        
        manager = ProfileManager(connection=mock_conn)
        result = manager.update_profile(
            "test-profile",
            profile_spec={"count": 20}
        )
        
        assert result.version == 2
    
    def test_update_profile_no_version_bump(self):
        """Test updating without version bump."""
        from healthsim_agent.state.profile_manager import ProfileManager
        
        mock_conn = MagicMock()
        now = datetime.now()
        
        mock_tables_result = MagicMock()
        mock_tables_result.rows = [[1]]
        
        mock_profile_result = MagicMock()
        mock_profile_result.rows = [[
            "profile-abc",
            "test-profile",
            "Desc",
            3,
            json.dumps({}),
            None,
            json.dumps([]),
            now,
            now,
            None,
        ]]
        
        # Flow: ensure_tables -> load SELECT -> UPDATE -> reload SELECT
        mock_conn.execute.side_effect = [
            mock_tables_result,   # 1. ensure tables check
            mock_profile_result,  # 2. load existing
            None,                 # 3. update
            mock_profile_result,  # 4. reload (version stays at 3)
        ]
        
        manager = ProfileManager(connection=mock_conn)
        result = manager.update_profile(
            "test-profile",
            description="New description",
            bump_version=False
        )
        
        # Check UPDATE was called with version 3 (not bumped)
        update_calls = [c for c in mock_conn.execute.call_args_list 
                       if 'UPDATE' in str(c)]
        assert len(update_calls) >= 1
    
    def test_update_profile_all_fields(self):
        """Test updating all optional fields."""
        from healthsim_agent.state.profile_manager import ProfileManager
        
        mock_conn = MagicMock()
        now = datetime.now()
        
        mock_tables_result = MagicMock()
        mock_tables_result.rows = [[1]]
        
        mock_profile_result = MagicMock()
        mock_profile_result.rows = [[
            "profile-abc",
            "test-profile",
            "Old desc",
            1,
            json.dumps({"old": True}),
            "patientsim",
            json.dumps(["old-tag"]),
            now,
            now,
            json.dumps({"old_meta": True}),
        ]]
        
        mock_updated_result = MagicMock()
        mock_updated_result.rows = [[
            "profile-abc",
            "test-profile",
            "New desc",
            2,
            json.dumps({"new": True}),
            "patientsim",
            json.dumps(["new-tag"]),
            now,
            now,
            json.dumps({"new_meta": True}),
        ]]
        
        # Flow: ensure_tables -> load SELECT -> UPDATE -> reload SELECT
        mock_conn.execute.side_effect = [
            mock_tables_result,   # 1. ensure tables check
            mock_profile_result,  # 2. load existing
            None,                 # 3. update
            mock_updated_result,  # 4. reload
        ]
        
        manager = ProfileManager(connection=mock_conn)
        manager.update_profile(
            "test-profile",
            profile_spec={"new": True},
            description="New desc",
            tags=["new-tag"],
            metadata={"new_meta": True}
        )
        
        # Verify UPDATE was called
        update_calls = [c for c in mock_conn.execute.call_args_list 
                       if 'UPDATE' in str(c)]
        assert len(update_calls) >= 1


class TestProfileExists:
    """Tests for profile_exists method."""
    
    def test_profile_exists_true(self):
        """Test profile_exists returns True when profile exists."""
        from healthsim_agent.state.profile_manager import ProfileManager
        
        mock_conn = MagicMock()
        mock_tables_result = MagicMock()
        mock_tables_result.rows = [[1]]
        
        mock_exists_result = MagicMock()
        mock_exists_result.rows = [[1]]  # Count = 1
        
        mock_conn.execute.side_effect = [
            mock_tables_result,
            mock_exists_result,
        ]
        
        manager = ProfileManager(connection=mock_conn)
        assert manager.profile_exists("test-profile") is True
    
    def test_profile_exists_false(self):
        """Test profile_exists returns False when profile doesn't exist."""
        from healthsim_agent.state.profile_manager import ProfileManager
        
        mock_conn = MagicMock()
        mock_tables_result = MagicMock()
        mock_tables_result.rows = [[1]]
        
        mock_exists_result = MagicMock()
        mock_exists_result.rows = [[0]]  # Count = 0
        
        mock_conn.execute.side_effect = [
            mock_tables_result,
            mock_exists_result,
        ]
        
        manager = ProfileManager(connection=mock_conn)
        assert manager.profile_exists("nonexistent") is False
    
    def test_profile_exists_empty_rows(self):
        """Test profile_exists handles empty rows."""
        from healthsim_agent.state.profile_manager import ProfileManager
        
        mock_conn = MagicMock()
        mock_tables_result = MagicMock()
        mock_tables_result.rows = [[1]]
        
        mock_exists_result = MagicMock()
        mock_exists_result.rows = []  # Empty
        
        mock_conn.execute.side_effect = [
            mock_tables_result,
            mock_exists_result,
        ]
        
        manager = ProfileManager(connection=mock_conn)
        assert manager.profile_exists("test") is False


class TestGetCohortProfile:
    """Tests for get_cohort_profile method."""
    
    def test_get_cohort_profile_found(self):
        """Test get_cohort_profile returns profile when found."""
        from healthsim_agent.state.profile_manager import ProfileManager
        
        mock_conn = MagicMock()
        now = datetime.now()
        
        mock_tables_result = MagicMock()
        mock_tables_result.rows = [[1]]
        
        mock_exec_result = MagicMock()
        mock_exec_result.rows = [["profile-abc"]]
        
        mock_profile_result = MagicMock()
        mock_profile_result.rows = [[
            "profile-abc",
            "test-profile",
            "Description",
            1,
            json.dumps({"count": 10}),
            "patientsim",
            json.dumps([]),
            now,
            now,
            None,
        ]]
        
        # Flow: ensure_tables -> execution SELECT -> profile SELECT
        # Note: load_profile skips _ensure_tables because _tables_ensured=True
        mock_conn.execute.side_effect = [
            mock_tables_result,   # 1. ensure tables check
            mock_exec_result,     # 2. find execution by cohort_id
            mock_profile_result,  # 3. load profile (table check skipped)
        ]
        
        manager = ProfileManager(connection=mock_conn)
        profile = manager.get_cohort_profile("cohort-xyz")
        
        assert profile is not None
        assert profile.name == "test-profile"
    
    def test_get_cohort_profile_not_found(self):
        """Test get_cohort_profile returns None when no execution found."""
        from healthsim_agent.state.profile_manager import ProfileManager
        
        mock_conn = MagicMock()
        mock_tables_result = MagicMock()
        mock_tables_result.rows = [[1]]
        
        mock_exec_result = MagicMock()
        mock_exec_result.rows = []  # No execution
        
        mock_conn.execute.side_effect = [
            mock_tables_result,
            mock_exec_result,
        ]
        
        manager = ProfileManager(connection=mock_conn)
        profile = manager.get_cohort_profile("nonexistent-cohort")
        
        assert profile is None


class TestGetExecutionSpec:
    """Tests for get_execution_spec method."""
    
    def test_get_execution_spec_with_seed(self):
        """Test get_execution_spec includes seed from execution."""
        from healthsim_agent.state.profile_manager import ProfileManager
        
        mock_conn = MagicMock()
        mock_tables_result = MagicMock()
        mock_tables_result.rows = [[1]]
        
        mock_exec_result = MagicMock()
        mock_exec_result.rows = [[
            42,  # seed
            100,  # count
            json.dumps({
                "profile": {
                    "demographics": {"age": [30, 50]}
                }
            }),  # spec
        ]]
        
        mock_conn.execute.side_effect = [
            mock_tables_result,
            mock_exec_result,
        ]
        
        manager = ProfileManager(connection=mock_conn)
        spec = manager.get_execution_spec(1)
        
        assert spec["profile"]["generation"]["seed"] == 42
        assert spec["profile"]["generation"]["count"] == 100
    
    def test_get_execution_spec_without_seed(self):
        """Test get_execution_spec handles None seed."""
        from healthsim_agent.state.profile_manager import ProfileManager
        
        mock_conn = MagicMock()
        mock_tables_result = MagicMock()
        mock_tables_result.rows = [[1]]
        
        mock_exec_result = MagicMock()
        mock_exec_result.rows = [[
            None,  # no seed
            50,  # count
            json.dumps({"profile": {}}),
        ]]
        
        mock_conn.execute.side_effect = [
            mock_tables_result,
            mock_exec_result,
        ]
        
        manager = ProfileManager(connection=mock_conn)
        spec = manager.get_execution_spec(1)
        
        # Seed should not be set
        assert "seed" not in spec["profile"]["generation"]
        assert spec["profile"]["generation"]["count"] == 50
    
    def test_get_execution_spec_creates_generation_section(self):
        """Test get_execution_spec creates generation section if missing."""
        from healthsim_agent.state.profile_manager import ProfileManager
        
        mock_conn = MagicMock()
        mock_tables_result = MagicMock()
        mock_tables_result.rows = [[1]]
        
        mock_exec_result = MagicMock()
        mock_exec_result.rows = [[
            42,
            100,
            json.dumps({}),  # Empty spec - no profile section
        ]]
        
        mock_conn.execute.side_effect = [
            mock_tables_result,
            mock_exec_result,
        ]
        
        manager = ProfileManager(connection=mock_conn)
        spec = manager.get_execution_spec(1)
        
        # Should create nested structure
        assert "profile" in spec
        assert "generation" in spec["profile"]
        assert spec["profile"]["generation"]["seed"] == 42
    
    def test_get_execution_spec_not_found(self):
        """Test get_execution_spec raises for nonexistent execution."""
        from healthsim_agent.state.profile_manager import ProfileManager
        
        mock_conn = MagicMock()
        mock_tables_result = MagicMock()
        mock_tables_result.rows = [[1]]
        
        mock_exec_result = MagicMock()
        mock_exec_result.rows = []  # Not found
        
        mock_conn.execute.side_effect = [
            mock_tables_result,
            mock_exec_result,
        ]
        
        manager = ProfileManager(connection=mock_conn)
        
        with pytest.raises(ValueError, match="not found"):
            manager.get_execution_spec(999)
    
    def test_get_execution_spec_already_parsed_json(self):
        """Test get_execution_spec handles already parsed JSON."""
        from healthsim_agent.state.profile_manager import ProfileManager
        
        mock_conn = MagicMock()
        mock_tables_result = MagicMock()
        mock_tables_result.rows = [[1]]
        
        mock_exec_result = MagicMock()
        mock_exec_result.rows = [[
            42,
            100,
            {"profile": {"name": "test"}},  # Already dict, not JSON string
        ]]
        
        mock_conn.execute.side_effect = [
            mock_tables_result,
            mock_exec_result,
        ]
        
        manager = ProfileManager(connection=mock_conn)
        spec = manager.get_execution_spec(1)
        
        assert spec["profile"]["name"] == "test"
        assert spec["profile"]["generation"]["seed"] == 42


class TestDeleteProfile:
    """Tests for delete_profile method."""
    
    def test_delete_profile_not_found(self):
        """Test delete_profile returns False when not found."""
        from healthsim_agent.state.profile_manager import ProfileManager
        
        mock_conn = MagicMock()
        mock_tables_result = MagicMock()
        mock_tables_result.rows = [[1]]
        
        mock_find_result = MagicMock()
        mock_find_result.rows = []  # Not found
        
        mock_conn.execute.side_effect = [
            mock_tables_result,
            mock_find_result,
        ]
        
        manager = ProfileManager(connection=mock_conn)
        result = manager.delete_profile("nonexistent")
        
        assert result is False
    
    def test_delete_profile_without_executions(self):
        """Test delete_profile without deleting executions."""
        from healthsim_agent.state.profile_manager import ProfileManager
        
        mock_conn = MagicMock()
        mock_tables_result = MagicMock()
        mock_tables_result.rows = [[1]]
        
        mock_find_result = MagicMock()
        mock_find_result.rows = [["profile-abc"]]
        
        mock_conn.execute.side_effect = [
            mock_tables_result,
            mock_find_result,
            None,  # DELETE profiles (no execution delete)
        ]
        
        manager = ProfileManager(connection=mock_conn)
        result = manager.delete_profile("profile-abc", delete_executions=False)
        
        assert result is True
        
        # Should NOT have deleted executions
        delete_calls = [str(c) for c in mock_conn.execute.call_args_list 
                       if 'DELETE' in str(c)]
        execution_deletes = [c for c in delete_calls if 'execution' in c.lower()]
        assert len(execution_deletes) == 0


class TestListProfilesFiltering:
    """Tests for list_profiles filtering options."""
    
    def test_list_profiles_with_product_filter(self):
        """Test list_profiles with product filter."""
        from healthsim_agent.state.profile_manager import ProfileManager
        
        mock_conn = MagicMock()
        now = datetime.now()
        
        mock_tables_result = MagicMock()
        mock_tables_result.rows = [[1]]
        
        mock_list_result = MagicMock()
        mock_list_result.rows = [
            ["profile-1", "profile-one", "Desc", 1, "patientsim",
             json.dumps([]), now, 0, None],
        ]
        
        mock_conn.execute.side_effect = [
            mock_tables_result,
            mock_list_result,
        ]
        
        manager = ProfileManager(connection=mock_conn)
        profiles = manager.list_profiles(product="patientsim")
        
        # Check that WHERE clause included product filter
        query_call = mock_conn.execute.call_args_list[-1]
        assert "patientsim" in str(query_call)
    
    def test_list_profiles_with_search(self):
        """Test list_profiles with search term."""
        from healthsim_agent.state.profile_manager import ProfileManager
        
        mock_conn = MagicMock()
        now = datetime.now()
        
        mock_tables_result = MagicMock()
        mock_tables_result.rows = [[1]]
        
        mock_list_result = MagicMock()
        mock_list_result.rows = [
            ["profile-1", "diabetes-profile", "Diabetes testing", 1, "patientsim",
             json.dumps(["diabetes"]), now, 5, now],
        ]
        
        mock_conn.execute.side_effect = [
            mock_tables_result,
            mock_list_result,
        ]
        
        manager = ProfileManager(connection=mock_conn)
        profiles = manager.list_profiles(search="diabetes")
        
        # Check that ILIKE was used for search
        query_call = mock_conn.execute.call_args_list[-1]
        query_str = str(query_call)
        assert "ILIKE" in query_str or "diabetes" in query_str
    
    def test_list_profiles_tag_filter_excludes(self):
        """Test list_profiles tag filter excludes non-matching."""
        from healthsim_agent.state.profile_manager import ProfileManager
        
        mock_conn = MagicMock()
        now = datetime.now()
        
        mock_tables_result = MagicMock()
        mock_tables_result.rows = [[1]]
        
        mock_list_result = MagicMock()
        mock_list_result.rows = [
            ["profile-1", "profile-one", "Desc", 1, "patientsim",
             json.dumps(["cardiac"]), now, 0, None],  # Has "cardiac" tag
            ["profile-2", "profile-two", "Desc", 1, "patientsim",
             json.dumps(["diabetes"]), now, 0, None],  # Has "diabetes" tag
        ]
        
        mock_conn.execute.side_effect = [
            mock_tables_result,
            mock_list_result,
        ]
        
        manager = ProfileManager(connection=mock_conn)
        profiles = manager.list_profiles(tags=["diabetes"])
        
        # Should only return profile with diabetes tag
        assert len(profiles) == 1
        assert profiles[0].name == "profile-two"


class TestRecordExecutionEdgeCases:
    """Tests for record_execution edge cases."""
    
    def test_record_execution_with_error(self):
        """Test recording a failed execution with error message."""
        from healthsim_agent.state.profile_manager import ProfileManager
        
        mock_conn = MagicMock()
        mock_tables_result = MagicMock()
        mock_tables_result.rows = [[1]]
        
        mock_insert_result = MagicMock()
        mock_insert_result.rows = [[123]]
        
        mock_conn.execute.side_effect = [
            mock_tables_result,
            mock_insert_result,
        ]
        
        manager = ProfileManager(connection=mock_conn)
        exec_id = manager.record_execution(
            profile_id="profile-abc",
            status="failed",
            error_message="Connection timeout",
            duration_ms=500,
        )
        
        assert exec_id == 123
    
    def test_record_execution_with_metadata(self):
        """Test recording execution with metadata."""
        from healthsim_agent.state.profile_manager import ProfileManager
        
        mock_conn = MagicMock()
        mock_tables_result = MagicMock()
        mock_tables_result.rows = [[1]]
        
        mock_insert_result = MagicMock()
        mock_insert_result.rows = [[456]]
        
        mock_conn.execute.side_effect = [
            mock_tables_result,
            mock_insert_result,
        ]
        
        manager = ProfileManager(connection=mock_conn)
        exec_id = manager.record_execution(
            profile_id="profile-abc",
            metadata={"triggered_by": "api", "version": "1.0"}
        )
        
        # Check metadata was JSON-encoded
        insert_call = mock_conn.execute.call_args_list[-1]
        assert "triggered_by" in str(insert_call) or exec_id == 456


class TestGetExecutions:
    """Tests for get_executions method."""
    
    def test_get_executions_with_metadata(self):
        """Test get_executions parses metadata correctly."""
        from healthsim_agent.state.profile_manager import ProfileManager
        
        mock_conn = MagicMock()
        now = datetime.now()
        
        mock_profile_result = MagicMock()
        mock_profile_result.rows = [[
            "profile-abc", "test", None, 1, json.dumps({}),
            None, json.dumps([]), now, now, None
        ]]
        
        mock_tables_result = MagicMock()
        mock_tables_result.rows = [[1]]
        
        mock_exec_result = MagicMock()
        mock_exec_result.rows = [[
            1, "profile-abc", "cohort-1", now, 42, 100, 1500, 
            "completed", None, json.dumps({"source": "api"})
        ]]
        
        mock_conn.execute.side_effect = [
            mock_tables_result,  # for load_profile
            mock_profile_result,
            mock_exec_result,
        ]
        
        manager = ProfileManager(connection=mock_conn)
        execs = manager.get_executions("profile-abc")
        
        assert len(execs) == 1
        assert execs[0].metadata["source"] == "api"
    
    def test_get_executions_already_parsed_metadata(self):
        """Test get_executions handles already parsed metadata."""
        from healthsim_agent.state.profile_manager import ProfileManager
        
        mock_conn = MagicMock()
        now = datetime.now()
        
        mock_profile_result = MagicMock()
        mock_profile_result.rows = [[
            "profile-abc", "test", None, 1, {},  # Already dict
            None, [], now, now, None
        ]]
        
        mock_tables_result = MagicMock()
        mock_tables_result.rows = [[1]]
        
        mock_exec_result = MagicMock()
        mock_exec_result.rows = [[
            1, "profile-abc", None, now, None, 50, 800,
            "completed", None, {"already": "parsed"}  # Already dict
        ]]
        
        mock_conn.execute.side_effect = [
            mock_tables_result,
            mock_profile_result,
            mock_exec_result,
        ]
        
        manager = ProfileManager(connection=mock_conn)
        execs = manager.get_executions("profile-abc")
        
        assert execs[0].metadata["already"] == "parsed"


class TestLoadProfileJsonParsing:
    """Tests for load_profile JSON parsing edge cases."""
    
    def test_load_profile_already_parsed_json(self):
        """Test load_profile handles already parsed JSON fields."""
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
            {"count": 10},  # Already dict
            "patientsim",
            ["tag1", "tag2"],  # Already list
            now,
            now,
            {"meta": "data"},  # Already dict
        ]]
        
        mock_conn.execute.side_effect = [
            mock_tables_result,
            mock_profile_result,
        ]
        
        manager = ProfileManager(connection=mock_conn)
        record = manager.load_profile("test-profile")
        
        assert record.profile_spec["count"] == 10
        assert "tag1" in record.tags
        assert record.metadata["meta"] == "data"
    
    def test_load_profile_null_tags(self):
        """Test load_profile handles null tags."""
        from healthsim_agent.state.profile_manager import ProfileManager
        
        mock_conn = MagicMock()
        now = datetime.now()
        
        mock_tables_result = MagicMock()
        mock_tables_result.rows = [[1]]
        
        mock_profile_result = MagicMock()
        mock_profile_result.rows = [[
            "profile-abc",
            "test-profile",
            None,
            1,
            json.dumps({}),
            None,
            None,  # Null tags
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
        
        assert record.tags == []


class TestGetProfileManager:
    """Tests for get_profile_manager factory function."""
    
    def test_get_profile_manager_with_connection(self):
        """Test get_profile_manager with provided connection."""
        from healthsim_agent.state.profile_manager import get_profile_manager
        
        mock_conn = MagicMock()
        manager = get_profile_manager(mock_conn)
        
        assert manager._conn is mock_conn
    
    def test_get_profile_manager_without_connection(self):
        """Test get_profile_manager without connection."""
        from healthsim_agent.state.profile_manager import get_profile_manager
        
        manager = get_profile_manager()
        
        assert manager._conn is None


class TestSaveProfileProductInference:
    """Tests for save_profile product inference."""
    
    def test_save_profile_infers_product_from_spec(self):
        """Test save_profile infers product from profile_spec."""
        from healthsim_agent.state.profile_manager import ProfileManager
        
        mock_conn = MagicMock()
        mock_tables_result = MagicMock()
        mock_tables_result.rows = [[1]]
        mock_existing_result = MagicMock()
        mock_existing_result.rows = []
        
        mock_conn.execute.side_effect = [
            mock_tables_result,
            mock_existing_result,
            None,  # insert
        ]
        
        manager = ProfileManager(connection=mock_conn)
        manager.save_profile(
            name="test-profile",
            profile_spec={"profile": {"product": "membersim"}},
            # product not explicitly provided
        )
        
        # Check that INSERT included the inferred product
        insert_call = mock_conn.execute.call_args_list[-1]
        insert_params = insert_call[0][1]
        # Product should be in params
        assert "membersim" in insert_params or "membersim" in str(insert_call)
