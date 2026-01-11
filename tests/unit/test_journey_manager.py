"""
Tests for journey persistence.

Tests cover:
- JourneyStep, JourneyRecord, JourneyExecutionRecord, JourneySummary dataclasses
- JourneyManager CRUD operations
- Journey versioning
- Execution history tracking
"""

import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch
import json


class TestJourneyStep:
    """Tests for JourneyStep dataclass."""
    
    def test_create_basic_step(self):
        """Test creating a basic JourneyStep."""
        from healthsim_agent.state.journey_manager import JourneyStep
        
        step = JourneyStep(
            id="step-1",
            name="Create Patient",
            product="patientsim",
            profile_ref="diabetic-profile",
            profile_spec=None,
        )
        
        assert step.id == "step-1"
        assert step.name == "Create Patient"
        assert step.product == "patientsim"
        assert step.profile_ref == "diabetic-profile"
        assert step.depends_on == []
    
    def test_create_step_with_dependencies(self):
        """Test JourneyStep with dependencies."""
        from healthsim_agent.state.journey_manager import JourneyStep
        
        step = JourneyStep(
            id="step-2",
            name="Generate Claims",
            product="membersim",
            profile_ref=None,
            profile_spec={"count": 5},
            depends_on=["step-1"],
            entity_mapping={"member_id": "patient.id"},
            count_expression="parent.count * 3",
        )
        
        assert step.depends_on == ["step-1"]
        assert step.entity_mapping["member_id"] == "patient.id"
        assert step.count_expression == "parent.count * 3"


class TestJourneyRecord:
    """Tests for JourneyRecord dataclass."""
    
    def test_create_journey_record(self):
        """Test creating a JourneyRecord."""
        from healthsim_agent.state.journey_manager import JourneyRecord, JourneyStep
        
        now = datetime.now()
        step = JourneyStep(
            id="step-1", name="Step 1", product="patientsim",
            profile_ref=None, profile_spec={}
        )
        
        record = JourneyRecord(
            id="journey-abc",
            name="test-journey",
            description="Test journey",
            version=1,
            steps=[step],
            products=["patientsim"],
            tags=["test"],
            created_at=now,
            updated_at=now,
        )
        
        assert record.id == "journey-abc"
        assert record.name == "test-journey"
        assert len(record.steps) == 1
        assert record.products == ["patientsim"]
        assert record.is_builtin is False


class TestJourneyExecutionRecord:
    """Tests for JourneyExecutionRecord dataclass."""
    
    def test_create_execution_record(self):
        """Test creating a JourneyExecutionRecord."""
        from healthsim_agent.state.journey_manager import JourneyExecutionRecord
        
        now = datetime.now()
        record = JourneyExecutionRecord(
            id=1,
            journey_id="journey-abc",
            cohort_id="cohort-xyz",
            executed_at=now,
            seed=42,
            total_entities=500,
            duration_ms=3000,
            status="completed",
            steps_completed=5,
            steps_total=5,
        )
        
        assert record.journey_id == "journey-abc"
        assert record.total_entities == 500
        assert record.status == "completed"
        assert record.steps_completed == record.steps_total
    
    def test_create_failed_execution(self):
        """Test JourneyExecutionRecord for failed execution."""
        from healthsim_agent.state.journey_manager import JourneyExecutionRecord
        
        now = datetime.now()
        record = JourneyExecutionRecord(
            id=2,
            journey_id="journey-abc",
            cohort_id=None,
            executed_at=now,
            seed=None,
            total_entities=100,
            duration_ms=1500,
            status="failed",
            steps_completed=2,
            steps_total=5,
            error_message="Step 3 failed: Invalid profile",
        )
        
        assert record.status == "failed"
        assert record.steps_completed < record.steps_total
        assert "Step 3" in record.error_message


class TestJourneySummary:
    """Tests for JourneySummary dataclass."""
    
    def test_create_summary(self):
        """Test creating a JourneySummary."""
        from healthsim_agent.state.journey_manager import JourneySummary
        
        now = datetime.now()
        summary = JourneySummary(
            id="journey-abc",
            name="diabetes-journey",
            description="Complete diabetes workflow",
            version=2,
            products=["patientsim", "membersim"],
            tags=["diabetes"],
            steps_count=3,
            created_at=now,
            is_builtin=False,
            execution_count=10,
            last_executed=now,
        )
        
        assert summary.name == "diabetes-journey"
        assert len(summary.products) == 2
        assert summary.steps_count == 3
        assert summary.execution_count == 10


class TestJourneyManager:
    """Tests for JourneyManager class."""
    
    def test_init_with_connection(self):
        """Test initializing with connection."""
        from healthsim_agent.state.journey_manager import JourneyManager
        
        mock_conn = MagicMock()
        manager = JourneyManager(connection=mock_conn)
        
        assert manager._conn is mock_conn
        assert manager._tables_ensured is False
    
    def test_init_without_connection(self):
        """Test initializing without connection (lazy load)."""
        from healthsim_agent.state.journey_manager import JourneyManager
        
        manager = JourneyManager()
        
        assert manager._conn is None
    
    def test_ensure_tables_creates_tables(self):
        """Test _ensure_tables creates necessary tables."""
        from healthsim_agent.state.journey_manager import JourneyManager
        
        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_result.rows = [[0]]  # Tables don't exist
        mock_conn.execute.return_value = mock_result
        
        manager = JourneyManager(connection=mock_conn)
        manager._ensure_tables()
        
        assert manager._tables_ensured is True
        assert mock_conn.execute.call_count >= 2
    
    def test_save_journey_new(self):
        """Test saving a new journey."""
        from healthsim_agent.state.journey_manager import JourneyManager, JourneyStep
        
        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_result.rows = [[1]]
        mock_existing = MagicMock()
        mock_existing.rows = []
        
        mock_conn.execute.side_effect = [mock_result, mock_existing, None]
        
        step = JourneyStep(
            id="step-1", name="Create Patient", product="patientsim",
            profile_ref=None, profile_spec={"count": 10}
        )
        
        manager = JourneyManager(connection=mock_conn)
        journey_id = manager.save_journey(
            name="test-journey",
            steps=[step],
            description="Test journey",
            tags=["test"],
        )
        
        assert journey_id.startswith("journey-")
    
    def test_save_journey_duplicate_raises(self):
        """Test saving duplicate journey name raises error."""
        from healthsim_agent.state.journey_manager import JourneyManager, JourneyStep
        
        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_result.rows = [[1]]
        mock_existing = MagicMock()
        mock_existing.rows = [["existing-id"]]
        
        mock_conn.execute.side_effect = [mock_result, mock_existing]
        
        step = JourneyStep(
            id="step-1", name="Step", product="patientsim",
            profile_ref=None, profile_spec={}
        )
        
        manager = JourneyManager(connection=mock_conn)
        
        with pytest.raises(ValueError, match="already exists"):
            manager.save_journey(name="duplicate", steps=[step])
    
    def test_load_journey_by_name(self):
        """Test loading journey by name."""
        from healthsim_agent.state.journey_manager import JourneyManager
        
        mock_conn = MagicMock()
        now = datetime.now()
        
        mock_tables_result = MagicMock()
        mock_tables_result.rows = [[1]]
        
        steps_json = json.dumps([{
            "id": "step-1",
            "name": "Create Patient",
            "product": "patientsim",
            "profile_ref": None,
            "profile_spec": {"count": 10},
            "depends_on": [],
            "entity_mapping": None,
            "count_expression": None,
            "condition": None,
            "metadata": None,
        }])
        
        mock_journey_result = MagicMock()
        mock_journey_result.rows = [[
            "journey-abc",
            "test-journey",
            "Description",
            1,
            steps_json,
            json.dumps(["patientsim"]),
            json.dumps(["test"]),
            now,
            now,
            False,
            None,
        ]]
        
        mock_conn.execute.side_effect = [mock_tables_result, mock_journey_result]
        
        manager = JourneyManager(connection=mock_conn)
        record = manager.load_journey("test-journey")
        
        assert record.name == "test-journey"
        assert len(record.steps) == 1
        assert record.steps[0].product == "patientsim"
    
    def test_load_journey_not_found(self):
        """Test loading non-existent journey raises error."""
        from healthsim_agent.state.journey_manager import JourneyManager
        
        mock_conn = MagicMock()
        mock_tables_result = MagicMock()
        mock_tables_result.rows = [[1]]
        mock_journey_result = MagicMock()
        mock_journey_result.rows = []
        
        mock_conn.execute.side_effect = [mock_tables_result, mock_journey_result]
        
        manager = JourneyManager(connection=mock_conn)
        
        with pytest.raises(ValueError, match="not found"):
            manager.load_journey("nonexistent")
    
    def test_delete_journey(self):
        """Test deleting a journey."""
        from healthsim_agent.state.journey_manager import JourneyManager
        
        mock_conn = MagicMock()
        mock_conn.execute.return_value = MagicMock(rows=[[1]])
        
        manager = JourneyManager(connection=mock_conn)
        manager._tables_ensured = True
        manager.delete_journey("journey-abc")
        
        delete_calls = [c for c in mock_conn.execute.call_args_list
                       if 'DELETE' in str(c)]
        assert len(delete_calls) >= 1
    
    def test_list_journeys_empty(self):
        """Test listing journeys when none exist."""
        from healthsim_agent.state.journey_manager import JourneyManager
        
        mock_conn = MagicMock()
        mock_tables_result = MagicMock()
        mock_tables_result.rows = [[1]]
        mock_list_result = MagicMock()
        mock_list_result.rows = []
        
        mock_conn.execute.side_effect = [mock_tables_result, mock_list_result]
        
        manager = JourneyManager(connection=mock_conn)
        journeys = manager.list_journeys()
        
        assert journeys == []
    
    def test_list_journeys_with_results(self):
        """Test listing journeys with results."""
        from healthsim_agent.state.journey_manager import JourneyManager
        
        mock_conn = MagicMock()
        now = datetime.now()
        
        # Row format: id, name, desc, version, products, tags, steps, is_builtin, created_at, exec_count, last_exec
        steps1 = json.dumps([{"id": "s1"}, {"id": "s2"}])
        steps2 = json.dumps([{"id": "s1"}, {"id": "s2"}, {"id": "s3"}])
        
        mock_list_result = MagicMock()
        mock_list_result.rows = [
            ["journey-1", "journey-one", "Desc 1", 1, json.dumps(["patientsim"]),
             json.dumps(["test"]), steps1, False, now, 5, now],
            ["journey-2", "journey-two", "Desc 2", 1, json.dumps(["membersim"]),
             json.dumps([]), steps2, True, now, 0, None],
        ]
        
        mock_conn.execute.return_value = mock_list_result
        
        manager = JourneyManager(connection=mock_conn)
        manager._tables_ensured = True
        journeys = manager.list_journeys()
        
        assert len(journeys) == 2
        assert journeys[0].name == "journey-one"
        assert journeys[0].steps_count == 2
        assert journeys[1].is_builtin is True
        assert journeys[1].steps_count == 3
    
    def test_list_journeys_with_product_filter(self):
        """Test listing journeys filtered by product."""
        from healthsim_agent.state.journey_manager import JourneyManager
        
        mock_conn = MagicMock()
        mock_list_result = MagicMock()
        mock_list_result.rows = []
        
        mock_conn.execute.return_value = mock_list_result
        
        manager = JourneyManager(connection=mock_conn)
        manager._tables_ensured = True
        manager.list_journeys(products=["patientsim"])
        
        call_args = mock_conn.execute.call_args_list[-1]
        assert "patientsim" in str(call_args) or "products" in str(call_args).lower()
    
    def test_record_execution(self):
        """Test recording a journey execution."""
        from healthsim_agent.state.journey_manager import JourneyManager
        
        mock_conn = MagicMock()
        mock_conn.execute.return_value = MagicMock(rows=[[1]])
        
        manager = JourneyManager(connection=mock_conn)
        manager._tables_ensured = True
        manager.record_execution(
            journey_id="journey-abc",
            cohort_id="cohort-xyz",
            seed=42,
            total_entities=500,
            duration_ms=3000,
            steps_completed=5,
            steps_total=5,
        )
        
        insert_calls = [c for c in mock_conn.execute.call_args_list
                       if 'INSERT' in str(c)]
        assert len(insert_calls) >= 1
    
    def test_get_executions(self):
        """Test getting executions for a journey."""
        from healthsim_agent.state.journey_manager import JourneyManager, JourneyRecord, JourneyStep
        
        mock_conn = MagicMock()
        now = datetime.now()
        
        # Mock the load_journey call
        mock_journey = JourneyRecord(
            id="journey-abc",
            name="test",
            description=None,
            version=1,
            steps=[JourneyStep(id="s1", name="S1", product="patientsim", profile_ref=None, profile_spec={})],
            products=["patientsim"],
            tags=[],
            created_at=now,
            updated_at=now,
        )
        
        mock_history_result = MagicMock()
        mock_history_result.rows = [
            [1, "journey-abc", "cohort-1", now, 42, 500, 3000,
             "completed", 5, 5, None, None, None],
            [2, "journey-abc", "cohort-2", now, 43, 250, 1500,
             "completed", 5, 5, None, None, None],
        ]
        
        mock_conn.execute.return_value = mock_history_result
        
        manager = JourneyManager(connection=mock_conn)
        manager._tables_ensured = True
        
        # Patch load_journey to avoid the complex mock setup
        with patch.object(manager, 'load_journey', return_value=mock_journey):
            history = manager.get_executions("journey-abc")
        
        assert len(history) == 2
        assert history[0].total_entities == 500
        assert history[1].seed == 43


class TestJourneyValidation:
    """Tests for journey validation logic."""
    
    def test_validate_steps_empty_raises(self):
        """Test that empty steps list raises error."""
        from healthsim_agent.state.journey_manager import JourneyManager
        
        mock_conn = MagicMock()
        mock_conn.execute.return_value = MagicMock(rows=[[1], []])
        
        manager = JourneyManager(connection=mock_conn)
        
        with pytest.raises((ValueError, TypeError)):
            manager.save_journey(name="empty-journey", steps=[])
    
    def test_step_serialization(self):
        """Test that steps serialize to JSON correctly."""
        from healthsim_agent.state.journey_manager import JourneyStep
        
        step = JourneyStep(
            id="step-1",
            name="Test Step",
            product="patientsim",
            profile_ref="test-profile",
            profile_spec=None,
            depends_on=["step-0"],
            entity_mapping={"patient_id": "previous.id"},
        )
        
        # Convert to dict for serialization
        step_dict = {
            "id": step.id,
            "name": step.name,
            "product": step.product,
            "profile_ref": step.profile_ref,
            "profile_spec": step.profile_spec,
            "depends_on": step.depends_on,
            "entity_mapping": step.entity_mapping,
            "count_expression": step.count_expression,
            "condition": step.condition,
            "metadata": step.metadata,
        }
        
        json_str = json.dumps(step_dict)
        parsed = json.loads(json_str)
        
        assert parsed["id"] == "step-1"
        assert parsed["depends_on"] == ["step-0"]
        assert parsed["entity_mapping"]["patient_id"] == "previous.id"
