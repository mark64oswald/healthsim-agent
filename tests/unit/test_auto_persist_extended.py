"""Extended tests for auto_persist module.

Covers additional scenarios for tag management, rename, delete, export, and samples.
Uses mocking pattern consistent with existing tests.
"""

import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch

from healthsim_agent.state.auto_persist import (
    AutoPersistService,
    PersistResult,
    QueryResult,
    CohortBrief,
    CloneResult,
    MergeResult,
    ExportResult,
    _validate_query,
    _ensure_unique_name,
)


class TestRenameCohort:
    """Tests for rename_cohort method."""
    
    def test_rename_cohort_success(self):
        """Test successful cohort rename."""
        mock_conn = MagicMock()
        
        # First call returns existing cohort
        mock_select = MagicMock()
        mock_select.rows = [['Old Name']]
        
        # Update returns nothing
        mock_update = MagicMock()
        mock_update.rows = []
        
        # Unique name check
        mock_unique = MagicMock()
        mock_unique.rows = [[0]]  # Name is unique
        
        mock_conn.execute.side_effect = [mock_select, mock_unique, mock_update]
        
        service = AutoPersistService(connection=mock_conn)
        old_name, new_name = service.rename_cohort('cohort-123', 'New Name')
        
        assert old_name == 'Old Name'
        assert 'new-name' in new_name.lower().replace(' ', '-')
    
    def test_rename_cohort_not_found(self):
        """Test rename for nonexistent cohort."""
        mock_conn = MagicMock()
        
        mock_result = MagicMock()
        mock_result.rows = []  # No cohort found
        mock_conn.execute.return_value = mock_result
        
        service = AutoPersistService(connection=mock_conn)
        
        with pytest.raises(ValueError, match="not found"):
            service.rename_cohort('nonexistent-id', 'New Name')


class TestDeleteCohort:
    """Tests for delete_cohort method."""
    
    def test_delete_cohort_requires_confirm(self):
        """Test that delete requires confirmation."""
        mock_conn = MagicMock()
        service = AutoPersistService(connection=mock_conn)
        
        with pytest.raises(ValueError, match="confirm=True"):
            service.delete_cohort('cohort-123', confirm=False)
    
    def test_delete_cohort_not_found(self):
        """Test delete for nonexistent cohort."""
        mock_conn = MagicMock()
        
        mock_result = MagicMock()
        mock_result.rows = []  # No cohort found
        mock_conn.execute.return_value = mock_result
        
        service = AutoPersistService(connection=mock_conn)
        
        with pytest.raises(ValueError, match="not found"):
            service.delete_cohort('nonexistent-id', confirm=True)
    
    def test_delete_cohort_success(self):
        """Test successful cohort deletion."""
        mock_conn = MagicMock()
        
        # Cohort exists
        mock_select = MagicMock()
        mock_select.rows = [['Test Cohort', 'Description']]
        mock_conn.execute.return_value = mock_select
        
        service = AutoPersistService(connection=mock_conn)
        
        with patch.object(service, '_table_exists', return_value=False):
            result = service.delete_cohort('cohort-123', confirm=True)
        
        assert result['cohort_id'] == 'cohort-123'
        assert result['name'] == 'Test Cohort'


class TestTagManagement:
    """Tests for tag management methods."""
    
    def test_add_tag(self):
        """Test adding a tag."""
        mock_conn = MagicMock()
        
        # Cohort exists check
        mock_cohort_info = {'id': 'cohort-123', 'name': 'Test'}
        
        # Tag doesn't exist yet
        mock_existing = MagicMock()
        mock_existing.rows = [[0]]
        mock_conn.execute.return_value = mock_existing
        
        service = AutoPersistService(connection=mock_conn)
        
        with patch.object(service, '_get_cohort_info', return_value=mock_cohort_info):
            with patch.object(service, '_update_cohort_timestamp'):
                with patch.object(service, 'get_tags', return_value=['diabetes']):
                    tags = service.add_tag('cohort-123', 'diabetes')
        
        assert 'diabetes' in tags
    
    def test_add_tag_empty_raises(self):
        """Test that empty tag raises error."""
        mock_conn = MagicMock()
        mock_cohort_info = {'id': 'cohort-123', 'name': 'Test'}
        
        service = AutoPersistService(connection=mock_conn)
        
        with patch.object(service, '_get_cohort_info', return_value=mock_cohort_info):
            with pytest.raises(ValueError, match="empty"):
                service.add_tag('cohort-123', '')
    
    def test_add_tag_whitespace_only_raises(self):
        """Test that whitespace-only tag raises error."""
        mock_conn = MagicMock()
        mock_cohort_info = {'id': 'cohort-123', 'name': 'Test'}
        
        service = AutoPersistService(connection=mock_conn)
        
        with patch.object(service, '_get_cohort_info', return_value=mock_cohort_info):
            with pytest.raises(ValueError, match="empty"):
                service.add_tag('cohort-123', '   ')
    
    def test_add_tag_not_found_cohort(self):
        """Test adding tag to nonexistent cohort."""
        mock_conn = MagicMock()
        
        service = AutoPersistService(connection=mock_conn)
        
        with patch.object(service, '_get_cohort_info', return_value=None):
            with pytest.raises(ValueError, match="not found"):
                service.add_tag('nonexistent', 'tag')
    
    def test_add_tag_normalizes(self):
        """Test that tags are normalized to lowercase."""
        mock_conn = MagicMock()
        mock_cohort_info = {'id': 'cohort-123', 'name': 'Test'}
        
        mock_existing = MagicMock()
        mock_existing.rows = [[0]]
        mock_conn.execute.return_value = mock_existing
        
        service = AutoPersistService(connection=mock_conn)
        
        with patch.object(service, '_get_cohort_info', return_value=mock_cohort_info):
            with patch.object(service, '_update_cohort_timestamp'):
                with patch.object(service, 'get_tags', return_value=['uppercase']):
                    tags = service.add_tag('cohort-123', 'UPPERCASE')
        
        assert 'uppercase' in tags
    
    def test_remove_tag(self):
        """Test removing a tag."""
        mock_conn = MagicMock()
        mock_cohort_info = {'id': 'cohort-123', 'name': 'Test'}
        
        service = AutoPersistService(connection=mock_conn)
        
        with patch.object(service, '_get_cohort_info', return_value=mock_cohort_info):
            with patch.object(service, '_update_cohort_timestamp'):
                with patch.object(service, 'get_tags', return_value=[]):
                    tags = service.remove_tag('cohort-123', 'to-remove')
        
        assert 'to-remove' not in tags
    
    def test_remove_tag_not_found_cohort(self):
        """Test removing tag from nonexistent cohort."""
        mock_conn = MagicMock()
        
        service = AutoPersistService(connection=mock_conn)
        
        with patch.object(service, '_get_cohort_info', return_value=None):
            with pytest.raises(ValueError, match="not found"):
                service.remove_tag('nonexistent', 'tag')
    
    def test_get_tags_empty(self):
        """Test getting tags when none exist."""
        mock_conn = MagicMock()
        
        mock_result = MagicMock()
        mock_result.rows = []
        mock_conn.execute.return_value = mock_result
        
        service = AutoPersistService(connection=mock_conn)
        tags = service.get_tags('cohort-123')
        
        assert isinstance(tags, list)
        assert len(tags) == 0
    
    def test_get_tags_multiple(self):
        """Test getting multiple tags."""
        mock_conn = MagicMock()
        
        mock_result = MagicMock()
        mock_result.rows = [['alpha'], ['beta'], ['gamma']]
        mock_conn.execute.return_value = mock_result
        
        service = AutoPersistService(connection=mock_conn)
        tags = service.get_tags('cohort-123')
        
        assert 'alpha' in tags
        assert 'beta' in tags
        assert 'gamma' in tags
    
    def test_list_all_tags_empty(self):
        """Test listing all tags when none exist."""
        mock_conn = MagicMock()
        
        mock_result = MagicMock()
        mock_result.rows = []
        mock_conn.execute.return_value = mock_result
        
        service = AutoPersistService(connection=mock_conn)
        all_tags = service.list_all_tags()
        
        assert isinstance(all_tags, list)
        assert len(all_tags) == 0
    
    def test_list_all_tags_with_counts(self):
        """Test listing all tags with counts."""
        mock_conn = MagicMock()
        
        mock_result = MagicMock()
        mock_result.rows = [['shared-tag', 5], ['unique-tag', 1]]
        mock_conn.execute.return_value = mock_result
        
        service = AutoPersistService(connection=mock_conn)
        all_tags = service.list_all_tags()
        
        assert len(all_tags) == 2
        assert all_tags[0]['tag'] == 'shared-tag'
        assert all_tags[0]['count'] == 5


class TestGetEntitySamples:
    """Tests for get_entity_samples method."""
    
    def test_get_samples_invalid_entity_type(self):
        """Test samples for invalid entity type."""
        mock_conn = MagicMock()
        
        service = AutoPersistService(connection=mock_conn)
        
        with patch('healthsim_agent.state.auto_persist.get_table_info', return_value=None):
            with pytest.raises(ValueError, match="Unknown entity type"):
                service.get_entity_samples(
                    cohort_id='cohort-123',
                    entity_type='invalid_type',
                    count=3,
                )
    
    def test_get_samples_basic(self):
        """Test getting entity samples."""
        mock_conn = MagicMock()
        
        mock_result = MagicMock()
        mock_result.rows = [
            ['{"id": "p1", "name": "Patient 1"}'],
            ['{"id": "p2", "name": "Patient 2"}'],
        ]
        mock_conn.execute.return_value = mock_result
        
        service = AutoPersistService(connection=mock_conn)
        
        with patch('healthsim_agent.state.auto_persist.get_table_info', return_value=('patients', 'id')):
            samples = service.get_entity_samples(
                cohort_id='cohort-123',
                entity_type='patients',
                count=3,
            )
        
        assert isinstance(samples, list)
        assert len(samples) == 2
    
    def test_get_samples_strategies(self):
        """Test different sampling strategies."""
        mock_conn = MagicMock()
        
        mock_result = MagicMock()
        mock_result.rows = [['{"id": "p1"}']]
        mock_conn.execute.return_value = mock_result
        
        service = AutoPersistService(connection=mock_conn)
        
        with patch('healthsim_agent.state.auto_persist.get_table_info', return_value=('patients', 'id')):
            # Test each strategy
            for strategy in ['diverse', 'random', 'recent']:
                samples = service.get_entity_samples(
                    cohort_id='cohort-123',
                    entity_type='patients',
                    count=3,
                    strategy=strategy,
                )
                assert isinstance(samples, list)


class TestExportResult:
    """Tests for ExportResult dataclass."""
    
    def test_create_export_result(self):
        """Test creating ExportResult."""
        result = ExportResult(
            cohort_id='coh-123',
            cohort_name='test-cohort',
            format='json',
            file_path='/tmp/export.json',
            entities_exported=100,
            file_size_bytes=1024,
            total_entities=100,
        )
        
        assert result.cohort_id == 'coh-123'
        assert result.format == 'json'
        assert result.entities_exported == 100
    
    def test_export_result_to_dict(self):
        """Test ExportResult to_dict."""
        result = ExportResult(
            cohort_id='coh-123',
            cohort_name='test-cohort',
            format='csv',
            file_path='/tmp/export.csv',
            entities_exported=50,
            file_size_bytes=512,
            total_entities=50,
        )
        
        d = result.to_dict()
        
        assert d['cohort_id'] == 'coh-123'
        assert d['format'] == 'csv'
        assert d['file_path'] == '/tmp/export.csv'


class TestCloneResult:
    """Tests for CloneResult dataclass."""
    
    def test_clone_result_to_dict(self):
        """Test CloneResult to_dict."""
        result = CloneResult(
            source_cohort_id='src-123',
            source_cohort_name='source',
            new_cohort_id='new-456',
            new_cohort_name='clone',
            entities_cloned={'patients': 10, 'encounters': 20},
            total_entities=30,
        )
        
        d = result.to_dict()
        
        assert d['source_cohort_id'] == 'src-123'
        assert d['new_cohort_id'] == 'new-456'
        assert d['total_entities'] == 30


class TestMergeResult:
    """Tests for MergeResult dataclass."""
    
    def test_merge_result_to_dict(self):
        """Test MergeResult to_dict."""
        result = MergeResult(
            source_cohort_ids=['s1', 's2'],
            source_cohort_names=['source1', 'source2'],
            target_cohort_id='target-123',
            target_cohort_name='merged',
            entities_merged={'patients': 15},
            total_entities=15,
            conflicts_resolved=2,
        )
        
        d = result.to_dict()
        
        assert d['source_cohort_ids'] == ['s1', 's2']
        assert d['conflicts_resolved'] == 2


class TestCohortBrief:
    """Tests for CohortBrief dataclass."""
    
    def test_cohort_brief_to_dict_with_datetime(self):
        """Test CohortBrief to_dict with datetime objects."""
        now = datetime.utcnow()
        
        brief = CohortBrief(
            cohort_id='coh-123',
            name='test',
            description='desc',
            entity_count=10,
            created_at=now,
            updated_at=now,
            tags=['tag1', 'tag2'],
        )
        
        d = brief.to_dict()
        
        assert d['cohort_id'] == 'coh-123'
        assert d['created_at'] is not None
        assert 'tag1' in d['tags']
    
    def test_cohort_brief_to_dict_none_dates(self):
        """Test CohortBrief to_dict with None dates."""
        brief = CohortBrief(
            cohort_id='coh-123',
            name='test',
            description=None,
            entity_count=0,
            created_at=None,
            updated_at=None,
        )
        
        d = brief.to_dict()
        
        assert d['created_at'] is None
        assert d['updated_at'] is None


class TestQueryResultExtended:
    """Extended tests for QueryResult dataclass."""
    
    def test_query_result_last_page(self):
        """Test QueryResult when on last page."""
        result = QueryResult(
            results=[{"id": "1"}],
            total_count=25,
            page=2,
            page_size=10,
            has_more=False,
            query_executed="SELECT * FROM test",
        )
        
        assert result.has_more is False
        assert result.offset == 20
    
    def test_query_result_large_page_size(self):
        """Test QueryResult with large page size."""
        result = QueryResult(
            results=[],
            total_count=5,
            page=0,
            page_size=100,
            has_more=False,
            query_executed="SELECT * FROM test",
        )
        
        assert result.offset == 0


class TestValidateQueryExtended:
    """Extended tests for _validate_query."""
    
    def test_valid_select_with_subquery(self):
        """Test SELECT with subquery."""
        assert _validate_query("SELECT * FROM (SELECT 1)") is True
    
    def test_valid_select_with_cte(self):
        """Test SELECT with CTE."""
        assert _validate_query("WITH cte AS (SELECT 1) SELECT * FROM cte") is True
    
    def test_invalid_multiple_statements(self):
        """Test multiple statements are rejected."""
        # Multiple statements should raise ValueError
        with pytest.raises(ValueError, match="disallowed pattern"):
            _validate_query("SELECT 1; SELECT 2")


class TestPersistResultExtended:
    """Extended tests for PersistResult."""
    
    def test_persist_result_with_summary(self):
        """Test PersistResult with summary object."""
        from healthsim_agent.state.summary import CohortSummary
        
        summary = CohortSummary(
            cohort_id='coh-123',
            name='test',
            description='test desc',
            entity_counts={'patients': 10},
            samples={},
        )
        
        result = PersistResult(
            cohort_id='coh-123',
            cohort_name='test',
            entity_type='patients',
            entities_persisted=10,
            entity_ids=['p1'],
            summary=summary,
            is_new_cohort=True,
        )
        
        d = result.to_dict()
        assert d['summary'] is not None
        assert d['summary']['cohort_id'] == 'coh-123'
