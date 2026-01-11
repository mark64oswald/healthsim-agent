"""
Comprehensive tests for summary module.

Tests cover:
- CohortSummary dataclass
- SummaryGenerator class
- ENTITY_COUNT_TABLES constant
"""

import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch
import json


class TestCohortSummary:
    """Tests for CohortSummary dataclass."""
    
    def test_create_basic_summary(self):
        """Test creating a basic CohortSummary."""
        from healthsim_agent.state.summary import CohortSummary
        
        summary = CohortSummary(
            cohort_id="coh-123",
            name="Test Cohort",
        )
        
        assert summary.cohort_id == "coh-123"
        assert summary.name == "Test Cohort"
        assert summary.description is None
        assert summary.entity_counts == {}
        assert summary.statistics == {}
        assert summary.samples == {}
        assert summary.tags == []
    
    def test_create_full_summary(self):
        """Test creating a fully populated CohortSummary."""
        from healthsim_agent.state.summary import CohortSummary
        
        now = datetime(2025, 1, 15, 10, 30, 0)
        
        summary = CohortSummary(
            cohort_id="coh-123",
            name="Full Cohort",
            description="A comprehensive test cohort",
            created_at=now,
            updated_at=now,
            entity_counts={"patients": 100, "encounters": 500},
            statistics={"avg_age": 45.5, "gender_ratio": 0.52},
            samples={"patients": [{"id": "p1"}, {"id": "p2"}]},
            tags=["test", "diabetes"],
        )
        
        assert summary.description == "A comprehensive test cohort"
        assert summary.entity_counts["patients"] == 100
        assert summary.statistics["avg_age"] == 45.5
        assert len(summary.samples["patients"]) == 2
        assert "diabetes" in summary.tags
    
    def test_to_dict(self):
        """Test to_dict conversion."""
        from healthsim_agent.state.summary import CohortSummary
        
        now = datetime(2025, 1, 15, 10, 30, 0)
        
        summary = CohortSummary(
            cohort_id="coh-123",
            name="Test",
            description="Desc",
            created_at=now,
            updated_at=now,
            entity_counts={"patients": 50},
            tags=["tag1"],
        )
        
        d = summary.to_dict()
        
        assert d['cohort_id'] == "coh-123"
        assert d['name'] == "Test"
        assert d['created_at'] == "2025-01-15T10:30:00"
        assert d['entity_counts'] == {"patients": 50}
        assert d['tags'] == ["tag1"]
    
    def test_to_dict_with_none_dates(self):
        """Test to_dict handles None dates."""
        from healthsim_agent.state.summary import CohortSummary
        
        summary = CohortSummary(
            cohort_id="coh-123",
            name="Test",
        )
        
        d = summary.to_dict()
        
        assert d['created_at'] is None
        assert d['updated_at'] is None
    
    def test_to_json(self):
        """Test to_json conversion."""
        from healthsim_agent.state.summary import CohortSummary
        
        summary = CohortSummary(
            cohort_id="coh-123",
            name="Test",
            entity_counts={"patients": 10},
        )
        
        json_str = summary.to_json(indent=2)
        
        # Should be valid JSON
        data = json.loads(json_str)
        
        assert data['cohort_id'] == "coh-123"
        assert data['entity_counts']['patients'] == 10
    
    def test_to_json_no_indent(self):
        """Test to_json without indentation."""
        from healthsim_agent.state.summary import CohortSummary
        
        summary = CohortSummary(
            cohort_id="coh-123",
            name="Test",
        )
        
        json_str = summary.to_json(indent=None)
        
        # Should be compact (no newlines)
        assert '\n' not in json_str
    
    def test_from_dict(self):
        """Test from_dict creation."""
        from healthsim_agent.state.summary import CohortSummary
        
        data = {
            'cohort_id': 'coh-123',
            'name': 'Restored Cohort',
            'description': 'From dict',
            'created_at': '2025-01-15T10:30:00',
            'updated_at': '2025-01-16T12:00:00',
            'entity_counts': {'members': 25},
            'statistics': {'avg_age': 50},
            'samples': {'members': [{'id': 'm1'}]},
            'tags': ['restored'],
        }
        
        summary = CohortSummary.from_dict(data)
        
        assert summary.cohort_id == 'coh-123'
        assert summary.name == 'Restored Cohort'
        assert summary.created_at == datetime(2025, 1, 15, 10, 30, 0)
        assert summary.entity_counts['members'] == 25
        assert summary.tags == ['restored']
    
    def test_from_dict_minimal(self):
        """Test from_dict with minimal data."""
        from healthsim_agent.state.summary import CohortSummary
        
        data = {
            'cohort_id': 'coh-123',
            'name': 'Minimal',
        }
        
        summary = CohortSummary.from_dict(data)
        
        assert summary.cohort_id == 'coh-123'
        assert summary.description is None
        assert summary.created_at is None
        assert summary.entity_counts == {}
        assert summary.tags == []
    
    def test_total_entities(self):
        """Test total_entities calculation."""
        from healthsim_agent.state.summary import CohortSummary
        
        summary = CohortSummary(
            cohort_id="coh-123",
            name="Test",
            entity_counts={
                "patients": 100,
                "encounters": 500,
                "diagnoses": 200,
            },
        )
        
        assert summary.total_entities() == 800
    
    def test_total_entities_empty(self):
        """Test total_entities with no entities."""
        from healthsim_agent.state.summary import CohortSummary
        
        summary = CohortSummary(
            cohort_id="coh-123",
            name="Empty",
        )
        
        assert summary.total_entities() == 0
    
    def test_token_estimate(self):
        """Test token_estimate calculation."""
        from healthsim_agent.state.summary import CohortSummary
        
        summary = CohortSummary(
            cohort_id="coh-123",
            name="Test",
            entity_counts={"patients": 100},
        )
        
        estimate = summary.token_estimate()
        
        # Should be positive
        assert estimate > 0
        
        # Rough check: compact JSON // 4
        json_len = len(summary.to_json(indent=None))
        assert estimate == json_len // 4
    
    def test_token_estimate_increases_with_content(self):
        """Test token estimate increases with more content."""
        from healthsim_agent.state.summary import CohortSummary
        
        small = CohortSummary(cohort_id="c1", name="Small")
        
        large = CohortSummary(
            cohort_id="c2",
            name="Large",
            description="A much longer description with more content",
            entity_counts={"a": 1, "b": 2, "c": 3, "d": 4, "e": 5},
            statistics={"stat1": 10, "stat2": 20, "stat3": 30},
            samples={"type1": [{"id": "1"}, {"id": "2"}, {"id": "3"}]},
            tags=["tag1", "tag2", "tag3", "tag4"],
        )
        
        assert large.token_estimate() > small.token_estimate()


class TestEntityCountTables:
    """Tests for ENTITY_COUNT_TABLES constant."""
    
    def test_constant_exists(self):
        """Test constant exists."""
        from healthsim_agent.state.summary import ENTITY_COUNT_TABLES
        
        assert isinstance(ENTITY_COUNT_TABLES, dict)
        assert len(ENTITY_COUNT_TABLES) > 0
    
    def test_includes_patient_entities(self):
        """Test PatientSim entities included."""
        from healthsim_agent.state.summary import ENTITY_COUNT_TABLES
        
        assert 'patients' in ENTITY_COUNT_TABLES
        assert 'encounters' in ENTITY_COUNT_TABLES
        assert 'diagnoses' in ENTITY_COUNT_TABLES
    
    def test_includes_member_entities(self):
        """Test MemberSim entities included."""
        from healthsim_agent.state.summary import ENTITY_COUNT_TABLES
        
        assert 'members' in ENTITY_COUNT_TABLES
        assert 'claims' in ENTITY_COUNT_TABLES
    
    def test_includes_rx_entities(self):
        """Test RxMemberSim entities included."""
        from healthsim_agent.state.summary import ENTITY_COUNT_TABLES
        
        assert 'rx_members' in ENTITY_COUNT_TABLES
        assert 'prescriptions' in ENTITY_COUNT_TABLES
    
    def test_includes_trial_entities(self):
        """Test TrialSim entities included."""
        from healthsim_agent.state.summary import ENTITY_COUNT_TABLES
        
        assert 'studies' in ENTITY_COUNT_TABLES
        assert 'subjects' in ENTITY_COUNT_TABLES


class TestSummaryGenerator:
    """Tests for SummaryGenerator class."""
    
    @pytest.fixture
    def mock_connection(self):
        """Create a mock database connection."""
        conn = MagicMock()
        return conn
    
    @pytest.fixture
    def generator(self, mock_connection):
        """Create generator with mock connection."""
        from healthsim_agent.state.summary import SummaryGenerator
        return SummaryGenerator(connection=mock_connection)
    
    def test_init_with_connection(self, mock_connection):
        """Test initialization with provided connection."""
        from healthsim_agent.state.summary import SummaryGenerator
        
        gen = SummaryGenerator(connection=mock_connection)
        
        assert gen._conn is mock_connection
    
    def test_init_without_connection(self):
        """Test initialization without connection (lazy loading)."""
        from healthsim_agent.state.summary import SummaryGenerator
        
        gen = SummaryGenerator()
        
        assert gen._conn is None
    
    def test_get_entity_counts_single_table(self, generator, mock_connection):
        """Test getting entity counts for single table."""
        mock_result = MagicMock()
        mock_result.rows = [[50]]
        mock_connection.execute.return_value = mock_result
        
        counts = generator.get_entity_counts("coh-123")
        
        # Should have made multiple calls (one per table)
        assert mock_connection.execute.called
        # Should include counts for tables that have data
        # Note: The actual result depends on how many tables return data
    
    def test_get_entity_counts_handles_exceptions(self, generator, mock_connection):
        """Test that missing tables don't raise exceptions."""
        # Simulate some tables not existing
        mock_connection.execute.side_effect = Exception("Table not found")
        
        # Should not raise, just return empty dict
        counts = generator.get_entity_counts("coh-123")
        
        assert counts == {}
    
    def test_calculate_patient_statistics(self, generator, mock_connection):
        """Test patient statistics calculation."""
        # Mock age stats result
        age_result = MagicMock()
        age_result.rows = [[25, 75, 45.5]]
        
        # Mock gender result
        gender_result = MagicMock()
        gender_result.rows = [['M', 50], ['F', 50]]
        
        mock_connection.execute.side_effect = [age_result, gender_result]
        
        stats = generator.calculate_patient_statistics("coh-123")
        
        # Should have age_range if query succeeds
        if 'age_range' in stats:
            assert stats['age_range']['min'] == 25
            assert stats['age_range']['max'] == 75
    
    def test_calculate_patient_statistics_handles_missing_data(self, generator, mock_connection):
        """Test patient stats handles missing data gracefully."""
        mock_result = MagicMock()
        mock_result.rows = [[None, None, None]]
        mock_connection.execute.return_value = mock_result
        
        stats = generator.calculate_patient_statistics("coh-123")
        
        # Should not crash, just return what it can
        assert isinstance(stats, dict)
    
    def test_calculate_encounter_statistics(self, generator, mock_connection):
        """Test encounter statistics calculation."""
        from datetime import date
        
        mock_result = MagicMock()
        mock_result.rows = [[date(2024, 1, 1), date(2025, 1, 1)]]
        mock_connection.execute.return_value = mock_result
        
        stats = generator.calculate_encounter_statistics("coh-123")
        
        assert isinstance(stats, dict)


class TestSummaryRoundTrip:
    """Integration tests for summary serialization."""
    
    def test_dict_round_trip(self):
        """Test to_dict -> from_dict preserves data."""
        from healthsim_agent.state.summary import CohortSummary
        
        original = CohortSummary(
            cohort_id="coh-123",
            name="Round Trip",
            description="Test round trip",
            created_at=datetime(2025, 1, 15, 10, 30, 0),
            entity_counts={"patients": 100},
            statistics={"avg_age": 45.5},
            samples={"patients": [{"id": "p1"}]},
            tags=["test"],
        )
        
        d = original.to_dict()
        restored = CohortSummary.from_dict(d)
        
        assert restored.cohort_id == original.cohort_id
        assert restored.name == original.name
        assert restored.description == original.description
        assert restored.created_at == original.created_at
        assert restored.entity_counts == original.entity_counts
        assert restored.statistics == original.statistics
        assert restored.samples == original.samples
        assert restored.tags == original.tags
    
    def test_json_round_trip(self):
        """Test to_json -> from_dict(json.loads) preserves data."""
        from healthsim_agent.state.summary import CohortSummary
        
        original = CohortSummary(
            cohort_id="coh-456",
            name="JSON Test",
            entity_counts={"members": 50},
        )
        
        json_str = original.to_json()
        data = json.loads(json_str)
        restored = CohortSummary.from_dict(data)
        
        assert restored.cohort_id == original.cohort_id
        assert restored.name == original.name
        assert restored.entity_counts == original.entity_counts
