"""Extended tests for state/summary.py module.

Covers additional scenarios for CohortSummary, SummaryGenerator, and utility functions.
"""

import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch

from healthsim_agent.state.summary import (
    CohortSummary,
    SummaryGenerator,
    generate_summary,
    get_cohort_by_name,
)


class TestCohortSummaryExtended:
    """Extended tests for CohortSummary dataclass."""
    
    def test_to_dict_full(self):
        """Test to_dict with all fields populated."""
        now = datetime.utcnow()
        
        summary = CohortSummary(
            cohort_id='coh-123',
            name='Test Cohort',
            description='A test cohort',
            created_at=now,
            updated_at=now,
            entity_counts={'patients': 10, 'encounters': 25},
            statistics={'avg_age': 45.5},
            samples={'patients': [{'id': 'p1'}]},
            tags=['diabetes', 'test'],
        )
        
        d = summary.to_dict()
        
        assert d['cohort_id'] == 'coh-123'
        assert d['name'] == 'Test Cohort'
        assert d['entity_counts']['patients'] == 10
        assert d['statistics']['avg_age'] == 45.5
        assert len(d['samples']['patients']) == 1
        assert 'diabetes' in d['tags']
    
    def test_to_dict_minimal(self):
        """Test to_dict with minimal fields."""
        summary = CohortSummary(
            cohort_id='coh-minimal',
            name='Minimal',
        )
        
        d = summary.to_dict()
        
        assert d['cohort_id'] == 'coh-minimal'
        assert d['description'] is None
        assert d['entity_counts'] == {}
        assert d['samples'] == {}
    
    def test_to_json(self):
        """Test to_json method."""
        summary = CohortSummary(
            cohort_id='coh-123',
            name='Test Cohort',
            entity_counts={'patients': 10},
        )
        
        json_str = summary.to_json()
        
        assert '"cohort_id": "coh-123"' in json_str
        assert '"patients": 10' in json_str
    
    def test_from_dict(self):
        """Test from_dict classmethod."""
        data = {
            'cohort_id': 'coh-123',
            'name': 'Test',
            'description': 'Desc',
            'entity_counts': {'patients': 5},
            'statistics': {},
            'samples': {},
            'tags': ['tag1'],
        }
        
        summary = CohortSummary.from_dict(data)
        
        assert summary.cohort_id == 'coh-123'
        assert summary.name == 'Test'
        assert summary.entity_counts['patients'] == 5
    
    def test_total_entities_property(self):
        """Test total_entities method."""
        summary = CohortSummary(
            cohort_id='coh-123',
            name='Test',
            entity_counts={'patients': 10, 'encounters': 20, 'diagnoses': 30},
        )
        
        total = summary.total_entities()
        
        assert total == 60
    
    def test_total_entities_empty(self):
        """Test total_entities with empty counts."""
        summary = CohortSummary(
            cohort_id='coh-123',
            name='Test',
        )
        
        total = summary.total_entities()
        
        assert total == 0
    
    def test_token_estimate_property(self):
        """Test token_estimate method."""
        summary = CohortSummary(
            cohort_id='coh-123',
            name='Test',
            entity_counts={'patients': 5},
            samples={'patients': [{'id': 'p1'}]},
        )
        
        estimate = summary.token_estimate()
        
        # token_estimate is based on len(to_json()) / 4
        assert estimate > 0


class TestSummaryGenerator:
    """Tests for SummaryGenerator class."""
    
    def test_get_entity_counts(self):
        """Test getting entity counts."""
        mock_conn = MagicMock()
        
        # Simulate different count results for different tables
        mock_count = MagicMock()
        mock_count.rows = [[10]]
        mock_conn.execute.return_value = mock_count
        
        generator = SummaryGenerator(connection=mock_conn)
        counts = generator.get_entity_counts('cohort-123')
        
        assert isinstance(counts, dict)
    
    def test_get_diverse_samples_empty(self):
        """Test getting samples from empty table."""
        mock_conn = MagicMock()
        
        mock_result = MagicMock()
        mock_result.rows = []
        mock_result.columns = ['id', 'name']
        mock_conn.execute.return_value = mock_result
        
        generator = SummaryGenerator(connection=mock_conn)
        samples = generator.get_diverse_samples('cohort-123', 'patients', 3)
        
        assert samples == []
    
    def test_get_diverse_samples_few_records(self):
        """Test samples when fewer records than requested."""
        mock_conn = MagicMock()
        
        mock_result = MagicMock()
        mock_result.rows = [['p1', 'John'], ['p2', 'Jane']]
        mock_result.columns = ['id', 'name']
        mock_conn.execute.return_value = mock_result
        
        generator = SummaryGenerator(connection=mock_conn)
        samples = generator.get_diverse_samples('cohort-123', 'patients', 5)
        
        assert len(samples) == 2
    
    def test_get_diverse_samples_excludes_internal_columns(self):
        """Test that internal columns are excluded from samples."""
        mock_conn = MagicMock()
        
        mock_result = MagicMock()
        mock_result.rows = [['p1', 'John', 'cohort-123', datetime.utcnow()]]
        mock_result.columns = ['id', 'name', 'cohort_id', 'created_at']
        mock_conn.execute.return_value = mock_result
        
        generator = SummaryGenerator(connection=mock_conn)
        samples = generator.get_diverse_samples('cohort-123', 'patients', 1)
        
        assert len(samples) == 1
        # cohort_id and created_at should be excluded
        assert 'cohort_id' not in samples[0]
        assert 'created_at' not in samples[0]
    
    def test_generate_not_found(self):
        """Test generate for nonexistent cohort."""
        mock_conn = MagicMock()
        
        mock_result = MagicMock()
        mock_result.rows = []  # No cohort found
        mock_conn.execute.return_value = mock_result
        
        generator = SummaryGenerator(connection=mock_conn)
        
        with pytest.raises(ValueError, match="not found"):
            generator.generate('nonexistent')
    
    def test_generate_basic(self):
        """Test basic summary generation."""
        mock_conn = MagicMock()
        
        # Cohort metadata
        mock_cohort = MagicMock()
        mock_cohort.rows = [['coh-123', 'Test', 'Desc', datetime.utcnow(), datetime.utcnow()]]
        
        # Tags
        mock_tags = MagicMock()
        mock_tags.rows = [['tag1']]
        
        mock_conn.execute.side_effect = [mock_cohort, mock_tags]
        
        generator = SummaryGenerator(connection=mock_conn)
        
        with patch.object(generator, 'get_entity_counts', return_value={'patients': 5}):
            with patch.object(generator, 'get_diverse_samples', return_value=[]):
                summary = generator.generate('coh-123', include_samples=False)
        
        assert summary.cohort_id == 'coh-123'
        assert summary.name == 'Test'
    
    def test_calculate_patient_statistics(self):
        """Test patient statistics calculation."""
        mock_conn = MagicMock()
        
        mock_result = MagicMock()
        mock_result.rows = [[40, 50, 60, 45.5]]  # min, max, count, avg
        mock_conn.execute.return_value = mock_result
        
        generator = SummaryGenerator(connection=mock_conn)
        stats = generator.calculate_patient_statistics('cohort-123')
        
        assert isinstance(stats, dict)
    
    def test_calculate_encounter_statistics(self):
        """Test encounter statistics calculation."""
        mock_conn = MagicMock()
        
        # Mock encounter type counts
        mock_result = MagicMock()
        mock_result.rows = [['outpatient', 10], ['inpatient', 5]]
        mock_conn.execute.return_value = mock_result
        
        generator = SummaryGenerator(connection=mock_conn)
        stats = generator.calculate_encounter_statistics('cohort-123')
        
        assert isinstance(stats, dict)
    
    def test_calculate_diagnosis_statistics(self):
        """Test diagnosis statistics calculation."""
        mock_conn = MagicMock()
        
        mock_result = MagicMock()
        mock_result.rows = [['E11.9', 'Type 2 diabetes', 15]]
        mock_conn.execute.return_value = mock_result
        
        generator = SummaryGenerator(connection=mock_conn)
        stats = generator.calculate_diagnosis_statistics('cohort-123')
        
        assert isinstance(stats, dict)
    
    def test_calculate_claims_statistics(self):
        """Test claims statistics calculation."""
        mock_conn = MagicMock()
        
        mock_result = MagicMock()
        mock_result.rows = [[100.00, 5000.00, 1500.50, 50]]
        mock_conn.execute.return_value = mock_result
        
        generator = SummaryGenerator(connection=mock_conn)
        stats = generator.calculate_claims_statistics('cohort-123')
        
        assert isinstance(stats, dict)


class TestGenerateSummaryFunction:
    """Tests for generate_summary function."""
    
    def test_generate_summary_with_connection(self):
        """Test generate_summary with custom connection."""
        mock_conn = MagicMock()
        
        # Setup mock responses
        mock_cohort = MagicMock()
        mock_cohort.rows = [['coh-123', 'Test', 'Desc', datetime.utcnow(), datetime.utcnow()]]
        mock_tags = MagicMock()
        mock_tags.rows = []
        
        mock_conn.execute.side_effect = [mock_cohort, mock_tags]
        
        with patch('healthsim_agent.state.summary.SummaryGenerator') as MockGenerator:
            mock_generator = MagicMock()
            mock_generator.generate.return_value = CohortSummary(
                cohort_id='coh-123',
                name='Test',
            )
            MockGenerator.return_value = mock_generator
            
            summary = generate_summary('coh-123', connection=mock_conn)
        
        assert summary is not None


class TestGetCohortByName:
    """Tests for get_cohort_by_name function."""
    
    def test_get_cohort_by_name_found(self):
        """Test finding cohort by name."""
        mock_conn = MagicMock()
        
        mock_result = MagicMock()
        mock_result.rows = [['coh-123']]
        mock_conn.execute.return_value = mock_result
        
        result = get_cohort_by_name('Test Cohort', connection=mock_conn)
        
        assert result == 'coh-123'
    
    def test_get_cohort_by_name_not_found(self):
        """Test cohort not found by name."""
        mock_conn = MagicMock()
        
        mock_result = MagicMock()
        mock_result.rows = []
        mock_conn.execute.return_value = mock_result
        
        result = get_cohort_by_name('Nonexistent', connection=mock_conn)
        
        assert result is None
