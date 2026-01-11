"""
Tests for cohort summary generation.

Tests cover:
- CohortSummary dataclass
- SummaryGenerator class
- Entity count tables constant
- Helper functions
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
            name="test-cohort",
        )
        
        assert summary.cohort_id == "coh-123"
        assert summary.name == "test-cohort"
        assert summary.description is None
        assert summary.entity_counts == {}
        assert summary.statistics == {}
        assert summary.samples == {}
        assert summary.tags == []
    
    def test_create_full_summary(self):
        """Test creating a fully populated CohortSummary."""
        from healthsim_agent.state.summary import CohortSummary
        
        now = datetime.now()
        summary = CohortSummary(
            cohort_id="coh-123",
            name="diabetes-cohort",
            description="Patients with diabetes",
            created_at=now,
            updated_at=now,
            entity_counts={"patients": 100, "encounters": 500},
            statistics={"avg_age": 55.5},
            samples={"patients": [{"id": "p1", "name": "Test"}]},
            tags=["diabetes", "chronic"],
        )
        
        assert summary.description == "Patients with diabetes"
        assert summary.entity_counts["patients"] == 100
        assert summary.statistics["avg_age"] == 55.5
        assert len(summary.samples["patients"]) == 1
        assert "diabetes" in summary.tags
    
    def test_to_dict(self):
        """Test to_dict conversion."""
        from healthsim_agent.state.summary import CohortSummary
        
        now = datetime(2024, 1, 15, 10, 30, 0)
        summary = CohortSummary(
            cohort_id="coh-123",
            name="test-cohort",
            created_at=now,
            entity_counts={"patients": 50},
        )
        
        d = summary.to_dict()
        
        assert d["cohort_id"] == "coh-123"
        assert d["name"] == "test-cohort"
        assert d["created_at"] == "2024-01-15T10:30:00"
        assert d["entity_counts"]["patients"] == 50
    
    def test_to_dict_with_none_dates(self):
        """Test to_dict handles None dates."""
        from healthsim_agent.state.summary import CohortSummary
        
        summary = CohortSummary(
            cohort_id="coh-123",
            name="test-cohort",
        )
        
        d = summary.to_dict()
        
        assert d["created_at"] is None
        assert d["updated_at"] is None
    
    def test_to_json(self):
        """Test JSON serialization."""
        from healthsim_agent.state.summary import CohortSummary
        
        summary = CohortSummary(
            cohort_id="coh-123",
            name="test-cohort",
            entity_counts={"patients": 10},
        )
        
        json_str = summary.to_json()
        parsed = json.loads(json_str)
        
        assert parsed["cohort_id"] == "coh-123"
        assert parsed["entity_counts"]["patients"] == 10
    
    def test_from_dict(self):
        """Test creating from dictionary."""
        from healthsim_agent.state.summary import CohortSummary
        
        data = {
            "cohort_id": "coh-456",
            "name": "loaded-cohort",
            "description": "Loaded from dict",
            "created_at": "2024-01-15T10:30:00",
            "updated_at": "2024-01-16T14:00:00",
            "entity_counts": {"members": 200},
            "statistics": {"avg_premium": 450.0},
            "samples": {},
            "tags": ["payer"],
        }
        
        summary = CohortSummary.from_dict(data)
        
        assert summary.cohort_id == "coh-456"
        assert summary.name == "loaded-cohort"
        assert summary.created_at.year == 2024
        assert summary.entity_counts["members"] == 200
        assert "payer" in summary.tags
    
    def test_from_dict_minimal(self):
        """Test from_dict with minimal data."""
        from healthsim_agent.state.summary import CohortSummary
        
        data = {
            "cohort_id": "coh-789",
            "name": "minimal",
        }
        
        summary = CohortSummary.from_dict(data)
        
        assert summary.cohort_id == "coh-789"
        assert summary.created_at is None
        assert summary.entity_counts == {}
    
    def test_total_entities(self):
        """Test total_entities calculation."""
        from healthsim_agent.state.summary import CohortSummary
        
        summary = CohortSummary(
            cohort_id="coh-123",
            name="test",
            entity_counts={
                "patients": 100,
                "encounters": 500,
                "diagnoses": 1200,
            },
        )
        
        assert summary.total_entities() == 1800
    
    def test_total_entities_empty(self):
        """Test total_entities with no entities."""
        from healthsim_agent.state.summary import CohortSummary
        
        summary = CohortSummary(cohort_id="coh-123", name="empty")
        
        assert summary.total_entities() == 0
    
    def test_token_estimate(self):
        """Test token estimation."""
        from healthsim_agent.state.summary import CohortSummary
        
        summary = CohortSummary(
            cohort_id="coh-123",
            name="test-cohort",
            entity_counts={"patients": 100},
        )
        
        estimate = summary.token_estimate()
        
        # Should be positive and reasonable
        assert estimate > 0
        assert estimate < 1000  # Simple summary should be small


class TestEntityCountTables:
    """Tests for ENTITY_COUNT_TABLES constant."""
    
    def test_tables_dict_exists(self):
        """Test entity count tables dict exists."""
        from healthsim_agent.state.summary import ENTITY_COUNT_TABLES
        
        assert isinstance(ENTITY_COUNT_TABLES, dict)
        assert len(ENTITY_COUNT_TABLES) > 0
    
    def test_includes_patientsim_tables(self):
        """Test PatientSim tables are included."""
        from healthsim_agent.state.summary import ENTITY_COUNT_TABLES
        
        assert "patients" in ENTITY_COUNT_TABLES
        assert "encounters" in ENTITY_COUNT_TABLES
        assert "diagnoses" in ENTITY_COUNT_TABLES
    
    def test_includes_membersim_tables(self):
        """Test MemberSim tables are included."""
        from healthsim_agent.state.summary import ENTITY_COUNT_TABLES
        
        assert "members" in ENTITY_COUNT_TABLES
        assert "claims" in ENTITY_COUNT_TABLES
    
    def test_includes_trialsim_tables(self):
        """Test TrialSim tables are included."""
        from healthsim_agent.state.summary import ENTITY_COUNT_TABLES
        
        assert "subjects" in ENTITY_COUNT_TABLES
        assert "adverse_events" in ENTITY_COUNT_TABLES


class TestSummaryGenerator:
    """Tests for SummaryGenerator class."""
    
    def test_init_with_connection(self):
        """Test initializing with connection."""
        from healthsim_agent.state.summary import SummaryGenerator
        
        mock_conn = MagicMock()
        generator = SummaryGenerator(connection=mock_conn)
        
        assert generator._conn is mock_conn
    
    def test_init_without_connection(self):
        """Test initializing without connection (lazy load)."""
        from healthsim_agent.state.summary import SummaryGenerator
        
        generator = SummaryGenerator()
        
        assert generator._conn is None
    
    def test_get_entity_counts(self):
        """Test getting entity counts."""
        from healthsim_agent.state.summary import SummaryGenerator
        
        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_result.rows = [[50]]
        mock_conn.execute.return_value = mock_result
        
        generator = SummaryGenerator(connection=mock_conn)
        counts = generator.get_entity_counts("coh-123")
        
        # Should have counts for tables that returned > 0
        assert isinstance(counts, dict)
    
    def test_get_entity_counts_handles_errors(self):
        """Test entity counts handles missing tables gracefully."""
        from healthsim_agent.state.summary import SummaryGenerator
        
        mock_conn = MagicMock()
        mock_conn.execute.side_effect = Exception("Table not found")
        
        generator = SummaryGenerator(connection=mock_conn)
        counts = generator.get_entity_counts("coh-123")
        
        # Should return empty dict, not raise
        assert counts == {}
    
    def test_calculate_patient_statistics(self):
        """Test calculating patient statistics."""
        from healthsim_agent.state.summary import SummaryGenerator
        
        mock_conn = MagicMock()
        
        # Age stats result
        mock_age_result = MagicMock()
        mock_age_result.rows = [[25, 75, 50.5]]
        
        # Gender result
        mock_gender_result = MagicMock()
        mock_gender_result.rows = [["M", 30], ["F", 45]]
        
        mock_conn.execute.side_effect = [mock_age_result, mock_gender_result]
        
        generator = SummaryGenerator(connection=mock_conn)
        stats = generator.calculate_patient_statistics("coh-123")
        
        assert "age_range" in stats
        assert stats["age_range"]["min"] == 25
        assert stats["age_range"]["max"] == 75
        assert "gender_distribution" in stats
    
    def test_calculate_patient_statistics_handles_null(self):
        """Test patient statistics handles null results."""
        from healthsim_agent.state.summary import SummaryGenerator
        
        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_result.rows = [[None, None, None]]
        mock_conn.execute.return_value = mock_result
        
        generator = SummaryGenerator(connection=mock_conn)
        stats = generator.calculate_patient_statistics("coh-123")
        
        # Should return without age_range if no data
        assert isinstance(stats, dict)
    
    def test_calculate_encounter_statistics(self):
        """Test calculating encounter statistics."""
        from healthsim_agent.state.summary import SummaryGenerator
        
        mock_conn = MagicMock()
        
        # Date range result
        mock_date_result = MagicMock()
        mock_date_result.rows = [["2024-01-01", "2024-12-31"]]
        
        # Encounter types result
        mock_types_result = MagicMock()
        mock_types_result.rows = [["AMB", 100], ["EMER", 25]]
        
        mock_conn.execute.side_effect = [mock_date_result, mock_types_result]
        
        generator = SummaryGenerator(connection=mock_conn)
        stats = generator.calculate_encounter_statistics("coh-123")
        
        assert "date_range" in stats
        assert "encounter_types" in stats
    
    def test_calculate_claims_statistics(self):
        """Test calculating claims statistics."""
        from healthsim_agent.state.summary import SummaryGenerator
        
        mock_conn = MagicMock()
        
        # Financial stats result
        mock_fin_result = MagicMock()
        mock_fin_result.rows = [[50000.0, 40000.0, 5000.0, 500.0]]
        
        # Claim types result
        mock_types_result = MagicMock()
        mock_types_result.rows = [["P", 80], ["I", 20]]
        
        mock_conn.execute.side_effect = [mock_fin_result, mock_types_result]
        
        generator = SummaryGenerator(connection=mock_conn)
        stats = generator.calculate_claims_statistics("coh-123")
        
        assert "financials" in stats
        assert stats["financials"]["total_billed"] == 50000.0
        assert "claim_types" in stats
    
    def test_calculate_diagnosis_statistics(self):
        """Test calculating diagnosis statistics."""
        from healthsim_agent.state.summary import SummaryGenerator
        
        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_result.rows = [
            ["E11.9", "Type 2 diabetes", 45],
            ["I10", "Essential hypertension", 30],
        ]
        mock_conn.execute.return_value = mock_result
        
        generator = SummaryGenerator(connection=mock_conn)
        stats = generator.calculate_diagnosis_statistics("coh-123")
        
        assert "top_diagnoses" in stats
        assert len(stats["top_diagnoses"]) == 2
        assert stats["top_diagnoses"][0]["code"] == "E11.9"


class TestGenerateSummary:
    """Tests for generate_summary helper function."""
    
    def test_generate_summary_basic(self):
        """Test basic summary generation."""
        from healthsim_agent.state.summary import generate_summary
        
        mock_conn = MagicMock()
        
        # Cohort info query
        mock_cohort_result = MagicMock()
        mock_cohort_result.rows = [[
            "coh-123", "test-cohort", "Description",
            datetime(2024, 1, 1), datetime(2024, 1, 2)
        ]]
        
        # Tags query
        mock_tags_result = MagicMock()
        mock_tags_result.rows = [["diabetes"], ["test"]]
        
        # Entity counts - return 0 for all tables
        mock_count_result = MagicMock()
        mock_count_result.rows = [[0]]
        
        mock_conn.execute.side_effect = [
            mock_cohort_result,
            mock_tags_result,
        ] + [mock_count_result] * 50  # For all entity count queries
        
        summary = generate_summary(
            cohort_id="coh-123",
            include_samples=False,
            connection=mock_conn,
        )
        
        assert summary.cohort_id == "coh-123"
        assert summary.name == "test-cohort"
    
    def test_generate_summary_cohort_not_found(self):
        """Test summary generation when cohort not found."""
        from healthsim_agent.state.summary import generate_summary
        
        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_result.rows = []
        mock_conn.execute.return_value = mock_result
        
        with pytest.raises(ValueError, match="Cohort not found"):
            generate_summary(cohort_id="nonexistent", connection=mock_conn)


class TestGetCohortByName:
    """Tests for get_cohort_by_name helper function."""
    
    def test_exact_match(self):
        """Test finding cohort by exact name."""
        from healthsim_agent.state.summary import get_cohort_by_name
        
        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_result.rows = [["coh-123"]]
        mock_conn.execute.return_value = mock_result
        
        result = get_cohort_by_name("test-cohort", mock_conn)
        
        assert result == "coh-123"
    
    def test_not_found(self):
        """Test cohort not found returns None."""
        from healthsim_agent.state.summary import get_cohort_by_name
        
        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_result.rows = []
        mock_conn.execute.return_value = mock_result
        
        result = get_cohort_by_name("nonexistent", mock_conn)
        
        assert result is None
