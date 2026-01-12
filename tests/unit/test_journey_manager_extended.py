"""
Extended tests for JourneyManager.

Covers:
- update_journey with various field combinations
- journey_exists checks
- get_entity_journeys lookup
- import_builtin_journeys
- _get_builtin_journey_definitions
- Edge cases in JSON parsing
- Lazy connection loading
- List journeys filtering (tags, search, include_builtin)
"""

import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch
import json


class TestJourneyManagerConnection:
    """Tests for JourneyManager connection handling."""
    
    def test_lazy_connection_not_loaded_on_init(self):
        """Test connection is not loaded on initialization."""
        from healthsim_agent.state.journey_manager import JourneyManager
        
        manager = JourneyManager()
        assert manager._conn is None
    
    def test_ensure_tables_only_runs_once(self):
        """Test _ensure_tables is idempotent."""
        from healthsim_agent.state.journey_manager import JourneyManager
        
        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_result.rows = [[1]]
        mock_conn.execute.return_value = mock_result
        
        manager = JourneyManager(connection=mock_conn)
        
        manager._ensure_tables()
        call_count_1 = mock_conn.execute.call_count
        
        manager._ensure_tables()
        call_count_2 = mock_conn.execute.call_count
        
        assert call_count_1 == call_count_2


class TestUpdateJourney:
    """Tests for update_journey method."""
    
    def test_update_journey_steps_only(self):
        """Test updating only the journey steps."""
        from healthsim_agent.state.journey_manager import JourneyManager, JourneyStep, JourneyRecord
        
        mock_conn = MagicMock()
        now = datetime.now()
        
        # Create a mock journey to return from load_journey
        orig_step = JourneyStep(
            id="step-1", name="Old Step", product="patientsim",
            profile_ref=None, profile_spec={}
        )
        mock_journey = JourneyRecord(
            id="journey-abc", name="test-journey", description="Desc",
            version=1, steps=[orig_step], products=["patientsim"],
            tags=[], created_at=now, updated_at=now
        )
        
        manager = JourneyManager(connection=mock_conn)
        manager._tables_ensured = True
        
        new_step = JourneyStep(
            id="step-2", name="New Step", product="membersim",
            profile_ref=None, profile_spec={}
        )
        
        # Patch load_journey to return our mock journey
        with patch.object(manager, 'load_journey', return_value=mock_journey):
            result = manager.update_journey("test-journey", steps=[new_step])
        
        # Verify UPDATE was called
        update_calls = [c for c in mock_conn.execute.call_args_list if 'UPDATE' in str(c)]
        assert len(update_calls) >= 1
    
    def test_update_journey_no_version_bump(self):
        """Test updating without version bump."""
        from healthsim_agent.state.journey_manager import JourneyManager, JourneyStep, JourneyRecord
        
        mock_conn = MagicMock()
        now = datetime.now()
        
        orig_step = JourneyStep(
            id="s1", name="S1", product="patientsim",
            profile_ref=None, profile_spec={}
        )
        mock_journey = JourneyRecord(
            id="journey-abc", name="test", description="Desc",
            version=3, steps=[orig_step], products=["patientsim"],
            tags=[], created_at=now, updated_at=now
        )
        
        manager = JourneyManager(connection=mock_conn)
        manager._tables_ensured = True
        
        with patch.object(manager, 'load_journey', return_value=mock_journey):
            manager.update_journey("test", description="New desc", bump_version=False)
        
        update_calls = [c for c in mock_conn.execute.call_args_list if 'UPDATE' in str(c)]
        assert len(update_calls) >= 1
    
    def test_update_journey_all_fields(self):
        """Test updating all optional fields."""
        from healthsim_agent.state.journey_manager import JourneyManager, JourneyStep, JourneyRecord
        
        mock_conn = MagicMock()
        now = datetime.now()
        
        orig_step = JourneyStep(
            id="s1", name="S1", product="patientsim",
            profile_ref=None, profile_spec={}
        )
        mock_journey = JourneyRecord(
            id="journey-abc", name="test", description="Old desc",
            version=1, steps=[orig_step], products=["patientsim"],
            tags=["old"], created_at=now, updated_at=now,
            metadata={"old": True}
        )
        
        manager = JourneyManager(connection=mock_conn)
        manager._tables_ensured = True
        
        new_step = JourneyStep(
            id="s2", name="S2", product="membersim",
            profile_ref=None, profile_spec={}
        )
        
        with patch.object(manager, 'load_journey', return_value=mock_journey):
            manager.update_journey(
                "test",
                steps=[new_step],
                description="New desc",
                tags=["new"],
                metadata={"new": True}
            )
        
        update_calls = [c for c in mock_conn.execute.call_args_list if 'UPDATE' in str(c)]
        assert len(update_calls) >= 1


class TestJourneyExists:
    """Tests for journey_exists method."""
    
    def test_journey_exists_true(self):
        """Test journey_exists returns True when journey exists."""
        from healthsim_agent.state.journey_manager import JourneyManager
        
        mock_conn = MagicMock()
        mock_tables_result = MagicMock()
        mock_tables_result.rows = [[1]]
        
        mock_exists_result = MagicMock()
        mock_exists_result.rows = [[1]]
        
        mock_conn.execute.side_effect = [mock_tables_result, mock_exists_result]
        
        manager = JourneyManager(connection=mock_conn)
        assert manager.journey_exists("test-journey") is True
    
    def test_journey_exists_false(self):
        """Test journey_exists returns False when journey doesn't exist."""
        from healthsim_agent.state.journey_manager import JourneyManager
        
        mock_conn = MagicMock()
        mock_tables_result = MagicMock()
        mock_tables_result.rows = [[1]]
        
        mock_exists_result = MagicMock()
        mock_exists_result.rows = [[0]]
        
        mock_conn.execute.side_effect = [mock_tables_result, mock_exists_result]
        
        manager = JourneyManager(connection=mock_conn)
        assert manager.journey_exists("nonexistent") is False
    
    def test_journey_exists_empty_rows(self):
        """Test journey_exists handles empty rows."""
        from healthsim_agent.state.journey_manager import JourneyManager
        
        mock_conn = MagicMock()
        mock_tables_result = MagicMock()
        mock_tables_result.rows = [[1]]
        
        mock_exists_result = MagicMock()
        mock_exists_result.rows = []
        
        mock_conn.execute.side_effect = [mock_tables_result, mock_exists_result]
        
        manager = JourneyManager(connection=mock_conn)
        assert manager.journey_exists("test") is False


class TestGetEntityJourneys:
    """Tests for get_entity_journeys method."""
    
    def test_get_entity_journeys_found(self):
        """Test get_entity_journeys returns journeys when found."""
        from healthsim_agent.state.journey_manager import JourneyManager, JourneyRecord, JourneyStep
        
        mock_conn = MagicMock()
        now = datetime.now()
        
        # Mock the search result
        mock_search_result = MagicMock()
        mock_search_result.rows = [["journey-abc"]]
        mock_conn.execute.return_value = mock_search_result
        
        # Create mock journey
        mock_journey = JourneyRecord(
            id="journey-abc", name="test", description="Desc",
            version=1, steps=[JourneyStep(id="s1", name="S1", product="patientsim", profile_ref=None, profile_spec={})],
            products=["patientsim"], tags=[], created_at=now, updated_at=now
        )
        
        manager = JourneyManager(connection=mock_conn)
        manager._tables_ensured = True
        
        with patch.object(manager, 'load_journey', return_value=mock_journey):
            journeys = manager.get_entity_journeys("entity-123")
        
        assert len(journeys) == 1
        assert journeys[0].name == "test"
    
    def test_get_entity_journeys_not_found(self):
        """Test get_entity_journeys returns empty list when no journeys found."""
        from healthsim_agent.state.journey_manager import JourneyManager
        
        mock_conn = MagicMock()
        mock_search_result = MagicMock()
        mock_search_result.rows = []
        mock_conn.execute.return_value = mock_search_result
        
        manager = JourneyManager(connection=mock_conn)
        manager._tables_ensured = True
        
        journeys = manager.get_entity_journeys("nonexistent-entity")
        
        assert journeys == []
    
    def test_get_entity_journeys_handles_load_error(self):
        """Test get_entity_journeys handles errors when loading journeys."""
        from healthsim_agent.state.journey_manager import JourneyManager, JourneyRecord, JourneyStep
        
        mock_conn = MagicMock()
        now = datetime.now()
        
        # Mock search returns two results
        mock_search_result = MagicMock()
        mock_search_result.rows = [["journey-abc"], ["journey-xyz"]]
        mock_conn.execute.return_value = mock_search_result
        
        mock_journey = JourneyRecord(
            id="journey-abc", name="test", description="Desc",
            version=1, steps=[JourneyStep(id="s1", name="S1", product="patientsim", profile_ref=None, profile_spec={})],
            products=["patientsim"], tags=[], created_at=now, updated_at=now
        )
        
        manager = JourneyManager(connection=mock_conn)
        manager._tables_ensured = True
        
        # First load succeeds, second raises ValueError
        def load_side_effect(journey_id):
            if journey_id == "journey-abc":
                return mock_journey
            else:
                raise ValueError("Journey not found")
        
        with patch.object(manager, 'load_journey', side_effect=load_side_effect):
            journeys = manager.get_entity_journeys("entity-123")
        
        # Should return only the one that loaded successfully
        assert len(journeys) == 1


class TestImportBuiltinJourneys:
    """Tests for import_builtin_journeys method."""
    
    def test_import_builtin_journeys_all_new(self):
        """Test importing all built-in journeys when none exist."""
        from healthsim_agent.state.journey_manager import JourneyManager
        
        mock_conn = MagicMock()
        mock_tables_result = MagicMock()
        mock_tables_result.rows = [[1]]
        
        # journey_exists returns False for all
        mock_not_exists = MagicMock()
        mock_not_exists.rows = [[0]]
        
        # save_journey - check for existing returns empty
        mock_no_existing = MagicMock()
        mock_no_existing.rows = []
        
        mock_conn.execute.return_value = mock_tables_result
        
        manager = JourneyManager(connection=mock_conn)
        
        # Patch journey_exists to return False
        with patch.object(manager, 'journey_exists', return_value=False):
            with patch.object(manager, 'save_journey', return_value="journey-123"):
                imported = manager.import_builtin_journeys()
        
        # Should import 4 built-in journeys
        assert imported == 4
    
    def test_import_builtin_journeys_some_exist(self):
        """Test importing built-in journeys when some already exist."""
        from healthsim_agent.state.journey_manager import JourneyManager
        
        mock_conn = MagicMock()
        mock_tables_result = MagicMock()
        mock_tables_result.rows = [[1]]
        mock_conn.execute.return_value = mock_tables_result
        
        manager = JourneyManager(connection=mock_conn)
        
        # First two exist, last two don't
        exists_results = [True, True, False, False]
        
        with patch.object(manager, 'journey_exists', side_effect=exists_results):
            with patch.object(manager, 'save_journey', return_value="journey-123"):
                imported = manager.import_builtin_journeys()
        
        assert imported == 2
    
    def test_import_builtin_journeys_all_exist(self):
        """Test importing when all built-in journeys already exist."""
        from healthsim_agent.state.journey_manager import JourneyManager
        
        mock_conn = MagicMock()
        mock_tables_result = MagicMock()
        mock_tables_result.rows = [[1]]
        mock_conn.execute.return_value = mock_tables_result
        
        manager = JourneyManager(connection=mock_conn)
        
        with patch.object(manager, 'journey_exists', return_value=True):
            imported = manager.import_builtin_journeys()
        
        assert imported == 0


class TestGetBuiltinJourneyDefinitions:
    """Tests for _get_builtin_journey_definitions method."""
    
    def test_get_builtin_journey_definitions_structure(self):
        """Test built-in journey definitions have correct structure."""
        from healthsim_agent.state.journey_manager import JourneyManager
        
        manager = JourneyManager()
        definitions = manager._get_builtin_journey_definitions()
        
        assert len(definitions) >= 4
        
        for journey_def in definitions:
            assert "name" in journey_def
            assert "steps" in journey_def
            assert len(journey_def["steps"]) > 0
            
            for step in journey_def["steps"]:
                assert "id" in step
                assert "name" in step
                assert "product" in step
    
    def test_get_builtin_journey_definitions_products(self):
        """Test built-in journeys cover expected products."""
        from healthsim_agent.state.journey_manager import JourneyManager
        
        manager = JourneyManager()
        definitions = manager._get_builtin_journey_definitions()
        
        all_products = set()
        for journey_def in definitions:
            for step in journey_def["steps"]:
                all_products.add(step["product"])
        
        # Should include key products
        assert "patientsim" in all_products
        assert "membersim" in all_products
    
    def test_get_builtin_journey_definitions_dependencies(self):
        """Test built-in journeys have valid dependencies."""
        from healthsim_agent.state.journey_manager import JourneyManager
        
        manager = JourneyManager()
        definitions = manager._get_builtin_journey_definitions()
        
        for journey_def in definitions:
            step_ids = {step["id"] for step in journey_def["steps"]}
            
            for step in journey_def["steps"]:
                depends_on = step.get("depends_on", [])
                for dep in depends_on:
                    assert dep in step_ids, f"Invalid dependency {dep} in {journey_def['name']}"


class TestDeleteJourney:
    """Tests for delete_journey method."""
    
    def test_delete_journey_not_found(self):
        """Test delete_journey returns False when not found."""
        from healthsim_agent.state.journey_manager import JourneyManager
        
        mock_conn = MagicMock()
        mock_tables_result = MagicMock()
        mock_tables_result.rows = [[1]]
        
        mock_find_result = MagicMock()
        mock_find_result.rows = []
        
        mock_conn.execute.side_effect = [mock_tables_result, mock_find_result]
        
        manager = JourneyManager(connection=mock_conn)
        result = manager.delete_journey("nonexistent")
        
        assert result is False
    
    def test_delete_journey_without_executions(self):
        """Test delete_journey without deleting executions."""
        from healthsim_agent.state.journey_manager import JourneyManager
        
        mock_conn = MagicMock()
        mock_tables_result = MagicMock()
        mock_tables_result.rows = [[1]]
        
        mock_find_result = MagicMock()
        mock_find_result.rows = [["journey-abc"]]
        
        mock_conn.execute.side_effect = [
            mock_tables_result,
            mock_find_result,
            None,  # DELETE journeys only
        ]
        
        manager = JourneyManager(connection=mock_conn)
        result = manager.delete_journey("journey-abc", delete_executions=False)
        
        assert result is True
        
        delete_calls = [str(c) for c in mock_conn.execute.call_args_list if 'DELETE' in str(c)]
        execution_deletes = [c for c in delete_calls if 'execution' in c.lower()]
        assert len(execution_deletes) == 0


class TestListJourneysFiltering:
    """Tests for list_journeys filtering options."""
    
    def test_list_journeys_exclude_builtin(self):
        """Test list_journeys can exclude built-in journeys."""
        from healthsim_agent.state.journey_manager import JourneyManager
        
        mock_conn = MagicMock()
        mock_list_result = MagicMock()
        mock_list_result.rows = []
        
        mock_conn.execute.return_value = mock_list_result
        
        manager = JourneyManager(connection=mock_conn)
        manager._tables_ensured = True
        manager.list_journeys(include_builtin=False)
        
        query_call = mock_conn.execute.call_args_list[-1]
        query_str = str(query_call)
        assert "is_builtin" in query_str.lower() or "FALSE" in query_str
    
    def test_list_journeys_with_search(self):
        """Test list_journeys with search term."""
        from healthsim_agent.state.journey_manager import JourneyManager
        
        mock_conn = MagicMock()
        mock_list_result = MagicMock()
        mock_list_result.rows = []
        
        mock_conn.execute.return_value = mock_list_result
        
        manager = JourneyManager(connection=mock_conn)
        manager._tables_ensured = True
        manager.list_journeys(search="diabetes")
        
        query_call = mock_conn.execute.call_args_list[-1]
        query_str = str(query_call)
        assert "ILIKE" in query_str or "diabetes" in query_str
    
    def test_list_journeys_tag_filter_excludes(self):
        """Test list_journeys tag filter excludes non-matching."""
        from healthsim_agent.state.journey_manager import JourneyManager
        
        mock_conn = MagicMock()
        now = datetime.now()
        
        steps = json.dumps([{"id": "s1"}])
        
        mock_list_result = MagicMock()
        mock_list_result.rows = [
            ["j1", "journey-one", "Desc", 1, json.dumps(["patientsim"]),
             json.dumps(["cardiac"]), steps, False, now, 0, None],
            ["j2", "journey-two", "Desc", 1, json.dumps(["patientsim"]),
             json.dumps(["diabetes"]), steps, False, now, 0, None],
        ]
        
        mock_conn.execute.return_value = mock_list_result
        
        manager = JourneyManager(connection=mock_conn)
        manager._tables_ensured = True
        journeys = manager.list_journeys(tags=["diabetes"])
        
        assert len(journeys) == 1
        assert journeys[0].name == "journey-two"
    
    def test_list_journeys_product_filter_excludes(self):
        """Test list_journeys product filter excludes non-matching."""
        from healthsim_agent.state.journey_manager import JourneyManager
        
        mock_conn = MagicMock()
        now = datetime.now()
        
        steps = json.dumps([{"id": "s1"}])
        
        mock_list_result = MagicMock()
        mock_list_result.rows = [
            ["j1", "journey-one", "Desc", 1, json.dumps(["patientsim"]),
             json.dumps([]), steps, False, now, 0, None],
            ["j2", "journey-two", "Desc", 1, json.dumps(["membersim"]),
             json.dumps([]), steps, False, now, 0, None],
        ]
        
        mock_conn.execute.return_value = mock_list_result
        
        manager = JourneyManager(connection=mock_conn)
        manager._tables_ensured = True
        journeys = manager.list_journeys(products=["membersim"])
        
        assert len(journeys) == 1
        assert journeys[0].name == "journey-two"


class TestRecordExecutionEdgeCases:
    """Tests for record_execution edge cases."""
    
    def test_record_execution_with_step_results(self):
        """Test recording execution with step results."""
        from healthsim_agent.state.journey_manager import JourneyManager
        
        mock_conn = MagicMock()
        mock_insert_result = MagicMock()
        mock_insert_result.rows = [[123]]
        
        mock_conn.execute.return_value = mock_insert_result
        
        manager = JourneyManager(connection=mock_conn)
        manager._tables_ensured = True
        
        exec_id = manager.record_execution(
            journey_id="journey-abc",
            step_results={
                "step-1": {"entities": 10, "duration_ms": 500},
                "step-2": {"entities": 50, "duration_ms": 1000}
            }
        )
        
        assert exec_id == 123
    
    def test_record_execution_with_error(self):
        """Test recording a failed execution with error message."""
        from healthsim_agent.state.journey_manager import JourneyManager
        
        mock_conn = MagicMock()
        mock_insert_result = MagicMock()
        mock_insert_result.rows = [[456]]
        
        mock_conn.execute.return_value = mock_insert_result
        
        manager = JourneyManager(connection=mock_conn)
        manager._tables_ensured = True
        
        exec_id = manager.record_execution(
            journey_id="journey-abc",
            status="failed",
            steps_completed=2,
            steps_total=5,
            error_message="Step 3 failed: Profile not found"
        )
        
        assert exec_id == 456


class TestGetExecutions:
    """Tests for get_executions method."""
    
    def test_get_executions_with_step_results(self):
        """Test get_executions parses step_results correctly."""
        from healthsim_agent.state.journey_manager import JourneyManager, JourneyRecord, JourneyStep
        
        mock_conn = MagicMock()
        now = datetime.now()
        
        mock_journey = JourneyRecord(
            id="journey-abc", name="test", description=None, version=1,
            steps=[JourneyStep(id="s1", name="S1", product="patientsim", profile_ref=None, profile_spec={})],
            products=["patientsim"], tags=[], created_at=now, updated_at=now
        )
        
        mock_exec_result = MagicMock()
        mock_exec_result.rows = [[
            1, "journey-abc", "cohort-1", now, 42, 500, 3000,
            "completed", 5, 5, None,
            json.dumps({"step-1": {"count": 100}}),  # step_results
            json.dumps({"triggered_by": "api"})  # metadata
        ]]
        
        mock_conn.execute.return_value = mock_exec_result
        
        manager = JourneyManager(connection=mock_conn)
        manager._tables_ensured = True
        
        with patch.object(manager, 'load_journey', return_value=mock_journey):
            execs = manager.get_executions("journey-abc")
        
        assert len(execs) == 1
        assert execs[0].step_results["step-1"]["count"] == 100
        assert execs[0].metadata["triggered_by"] == "api"
    
    def test_get_executions_already_parsed_json(self):
        """Test get_executions handles already parsed JSON."""
        from healthsim_agent.state.journey_manager import JourneyManager, JourneyRecord, JourneyStep
        
        mock_conn = MagicMock()
        now = datetime.now()
        
        mock_journey = JourneyRecord(
            id="journey-abc", name="test", description=None, version=1,
            steps=[JourneyStep(id="s1", name="S1", product="patientsim", profile_ref=None, profile_spec={})],
            products=["patientsim"], tags=[], created_at=now, updated_at=now
        )
        
        mock_exec_result = MagicMock()
        mock_exec_result.rows = [[
            1, "journey-abc", None, now, None, 50, 800,
            "completed", 3, 3, None,
            {"already": "parsed"},  # Already dict
            None
        ]]
        
        mock_conn.execute.return_value = mock_exec_result
        
        manager = JourneyManager(connection=mock_conn)
        manager._tables_ensured = True
        
        with patch.object(manager, 'load_journey', return_value=mock_journey):
            execs = manager.get_executions("journey-abc")
        
        assert execs[0].step_results["already"] == "parsed"


class TestLoadJourneyJsonParsing:
    """Tests for load_journey JSON parsing edge cases."""
    
    def test_load_journey_already_parsed_json(self):
        """Test load_journey handles already parsed JSON fields."""
        from healthsim_agent.state.journey_manager import JourneyManager
        
        mock_conn = MagicMock()
        now = datetime.now()
        
        mock_tables_result = MagicMock()
        mock_tables_result.rows = [[1]]
        
        mock_journey_result = MagicMock()
        mock_journey_result.rows = [[
            "journey-abc",
            "test",
            "Desc",
            1,
            [{  # Already list
                "id": "s1", "name": "S1", "product": "patientsim",
                "profile_ref": None, "profile_spec": {}, "depends_on": [],
                "entity_mapping": None, "count_expression": None, "condition": None, "metadata": None
            }],
            ["patientsim"],  # Already list
            ["tag1"],  # Already list
            False,
            now,
            now,
            {"meta": "data"}  # Already dict
        ]]
        
        mock_conn.execute.side_effect = [mock_tables_result, mock_journey_result]
        
        manager = JourneyManager(connection=mock_conn)
        record = manager.load_journey("test")
        
        assert len(record.steps) == 1
        assert "patientsim" in record.products
        assert "tag1" in record.tags
        assert record.metadata["meta"] == "data"
    
    def test_load_journey_null_tags(self):
        """Test load_journey handles null tags."""
        from healthsim_agent.state.journey_manager import JourneyManager
        
        mock_conn = MagicMock()
        now = datetime.now()
        
        mock_tables_result = MagicMock()
        mock_tables_result.rows = [[1]]
        
        steps_json = json.dumps([{
            "id": "s1", "name": "S1", "product": "patientsim",
            "profile_ref": None, "profile_spec": {}, "depends_on": [],
            "entity_mapping": None, "count_expression": None, "condition": None, "metadata": None
        }])
        
        mock_journey_result = MagicMock()
        mock_journey_result.rows = [[
            "journey-abc", "test", None, 1, steps_json,
            json.dumps(["patientsim"]),
            None,  # Null tags
            False, now, now, None
        ]]
        
        mock_conn.execute.side_effect = [mock_tables_result, mock_journey_result]
        
        manager = JourneyManager(connection=mock_conn)
        record = manager.load_journey("test")
        
        assert record.tags == []


class TestStepConversion:
    """Tests for _step_to_dict and _dict_to_step methods."""
    
    def test_step_to_dict_complete(self):
        """Test _step_to_dict converts all fields."""
        from healthsim_agent.state.journey_manager import JourneyManager, JourneyStep
        
        manager = JourneyManager()
        
        step = JourneyStep(
            id="step-1",
            name="Test Step",
            product="patientsim",
            profile_ref="test-profile",
            profile_spec={"count": 10},
            depends_on=["step-0"],
            entity_mapping={"patient_id": "prev.id"},
            count_expression="parent.count * 2",
            condition="age >= 18",
            metadata={"custom": "data"}
        )
        
        d = manager._step_to_dict(step)
        
        assert d["id"] == "step-1"
        assert d["name"] == "Test Step"
        assert d["product"] == "patientsim"
        assert d["profile_ref"] == "test-profile"
        assert d["profile_spec"]["count"] == 10
        assert d["depends_on"] == ["step-0"]
        assert d["entity_mapping"]["patient_id"] == "prev.id"
        assert d["count_expression"] == "parent.count * 2"
        assert d["condition"] == "age >= 18"
        assert d["metadata"]["custom"] == "data"
    
    def test_dict_to_step_minimal(self):
        """Test _dict_to_step handles minimal dict."""
        from healthsim_agent.state.journey_manager import JourneyManager
        
        manager = JourneyManager()
        
        d = {
            "id": "step-1",
            "name": "Minimal Step",
            "product": "patientsim"
        }
        
        step = manager._dict_to_step(d)
        
        assert step.id == "step-1"
        assert step.name == "Minimal Step"
        assert step.product == "patientsim"
        assert step.profile_ref is None
        assert step.profile_spec is None
        assert step.depends_on == []
        assert step.entity_mapping is None
        assert step.count_expression is None
        assert step.condition is None
        assert step.metadata is None


class TestGetJourneyManager:
    """Tests for get_journey_manager factory function."""
    
    def test_get_journey_manager_with_connection(self):
        """Test get_journey_manager with provided connection."""
        from healthsim_agent.state.journey_manager import get_journey_manager
        
        mock_conn = MagicMock()
        manager = get_journey_manager(mock_conn)
        
        assert manager._conn is mock_conn
    
    def test_get_journey_manager_without_connection(self):
        """Test get_journey_manager without connection."""
        from healthsim_agent.state.journey_manager import get_journey_manager
        
        manager = get_journey_manager()
        
        assert manager._conn is None
