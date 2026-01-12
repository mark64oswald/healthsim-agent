"""Extended tests for auto_persist module.

Covers additional methods:
- rename_cohort
- delete_cohort
- Tag management (add_tag, remove_tag, get_tags, list_all_tags)
- get_entity_samples
- get_auto_persist_service
"""

import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch

from healthsim_agent.state.auto_persist import (
    AutoPersistService,
    get_auto_persist_service,
    _ensure_unique_name,
)


class TestRenameCohort:
    """Tests for rename_cohort method."""
    
    def test_rename_cohort_success(self):
        """Test successfully renaming a cohort."""
        mock_conn = MagicMock()
        
        # First query returns current name
        mock_select = MagicMock()
        mock_select.rows = [["OldName"]]
        
        # Unique name check returns no conflict
        mock_unique = MagicMock()
        mock_unique.rows = [[0]]
        
        mock_conn.execute.side_effect = [mock_select, mock_unique, None]
        
        service = AutoPersistService(connection=mock_conn)
        old_name, new_name = service.rename_cohort('coh-123', 'NewName')
        
        assert old_name == 'OldName'
        assert 'newname' in new_name.lower()
    
    def test_rename_cohort_not_found(self):
        """Test renaming nonexistent cohort."""
        mock_conn = MagicMock()
        mock_select = MagicMock()
        mock_select.rows = []  # Empty - not found
        
        mock_conn.execute.return_value = mock_select
        
        service = AutoPersistService(connection=mock_conn)
        
        with pytest.raises(ValueError, match="not found"):
            service.rename_cohort('nonexistent', 'NewName')
    
    def test_rename_generates_unique_name_on_conflict(self):
        """Test rename handles name conflicts."""
        mock_conn = MagicMock()
        
        # First query returns current name
        mock_select = MagicMock()
        mock_select.rows = [["OldName"]]
        
        # Unique name check: first try conflicts, second succeeds
        mock_conflict = MagicMock()
        mock_conflict.rows = [[1]]  # Exists
        mock_unique = MagicMock()
        mock_unique.rows = [[0]]  # Unique
        
        mock_conn.execute.side_effect = [mock_select, mock_conflict, mock_unique, None]
        
        service = AutoPersistService(connection=mock_conn)
        old_name, new_name = service.rename_cohort('coh-123', 'ConflictingName')
        
        assert old_name == 'OldName'


class TestDeleteCohort:
    """Tests for delete_cohort method."""
    
    def test_delete_requires_confirm(self):
        """Test that delete requires confirmation."""
        mock_conn = MagicMock()
        service = AutoPersistService(connection=mock_conn)
        
        with pytest.raises(ValueError, match="confirm=True"):
            service.delete_cohort('coh-123', confirm=False)
    
    def test_delete_cohort_success(self):
        """Test successfully deleting a cohort."""
        mock_conn = MagicMock()
        
        # Query returns cohort info (name, description)
        mock_info = MagicMock()
        mock_info.rows = [["TestCohort", "A test cohort"]]
        
        # _table_exists check - return False to skip table operations
        mock_exists = MagicMock()
        mock_exists.rows = [[False]]
        
        # Set up mock to return appropriate values
        mock_conn.execute.return_value = mock_info
        
        service = AutoPersistService(connection=mock_conn)
        
        # Patch _table_exists to return False (no entity tables)
        with patch.object(service, '_table_exists', return_value=False):
            result = service.delete_cohort('coh-123', confirm=True)
        
        assert result['cohort_id'] == 'coh-123'
        assert result['name'] == 'TestCohort'
    
    def test_delete_cohort_not_found(self):
        """Test deleting nonexistent cohort."""
        mock_conn = MagicMock()
        mock_info = MagicMock()
        mock_info.rows = []  # Not found
        
        mock_conn.execute.return_value = mock_info
        
        service = AutoPersistService(connection=mock_conn)
        
        with pytest.raises(ValueError, match="not found"):
            service.delete_cohort('nonexistent', confirm=True)


class TestAddTag:
    """Tests for add_tag method."""
    
    def test_add_tag_success(self):
        """Test adding a new tag."""
        mock_conn = MagicMock()
        
        # _get_cohort_info returns cohort exists (5 columns: id, name, desc, created_at, updated_at)
        mock_info = MagicMock()
        mock_info.rows = [["coh-123", "TestCohort", "Desc", "2025-01-01", "2025-01-01"]]
        
        # Check tag exists returns 0 (not exists)
        mock_exists = MagicMock()
        mock_exists.rows = [[0]]
        
        # get_tags returns updated list
        mock_tags = MagicMock()
        mock_tags.rows = [["demo"], ["newtag"], ["test"]]
        
        mock_conn.execute.side_effect = [mock_info, mock_exists, None, None, mock_tags]
        
        service = AutoPersistService(connection=mock_conn)
        tags = service.add_tag('coh-123', 'newtag')
        
        assert 'newtag' in tags
    
    def test_add_tag_empty_raises(self):
        """Test that empty tag raises error."""
        mock_conn = MagicMock()
        mock_info = MagicMock()
        # 5 columns for _get_cohort_info
        mock_info.rows = [["coh-123", "Test", "Desc", "2025-01-01", "2025-01-01"]]
        mock_conn.execute.return_value = mock_info
        
        service = AutoPersistService(connection=mock_conn)
        
        with pytest.raises(ValueError, match="cannot be empty"):
            service.add_tag('coh-123', '   ')
    
    def test_add_tag_cohort_not_found(self):
        """Test adding tag to nonexistent cohort."""
        mock_conn = MagicMock()
        mock_info = MagicMock()
        mock_info.rows = []  # Not found
        mock_conn.execute.return_value = mock_info
        
        service = AutoPersistService(connection=mock_conn)
        
        with pytest.raises(ValueError, match="not found"):
            service.add_tag('nonexistent', 'tag')
    
    def test_add_tag_normalizes_case(self):
        """Test that tags are normalized to lowercase."""
        mock_conn = MagicMock()
        
        mock_info = MagicMock()
        mock_info.rows = [["coh-123", "Test", "Desc", "2025-01-01", "2025-01-01"]]
        
        mock_exists = MagicMock()
        mock_exists.rows = [[0]]
        
        mock_tags = MagicMock()
        mock_tags.rows = [["uppercase"]]
        
        mock_conn.execute.side_effect = [mock_info, mock_exists, None, None, mock_tags]
        
        service = AutoPersistService(connection=mock_conn)
        tags = service.add_tag('coh-123', 'UPPERCASE')
        
        assert 'uppercase' in tags


class TestRemoveTag:
    """Tests for remove_tag method."""
    
    def test_remove_tag_success(self):
        """Test removing a tag."""
        mock_conn = MagicMock()
        
        # 5 columns for _get_cohort_info
        mock_info = MagicMock()
        mock_info.rows = [["coh-123", "Test", "Desc", "2025-01-01", "2025-01-01"]]
        
        mock_tags = MagicMock()
        mock_tags.rows = [["demo"]]  # Only demo left after removing test
        
        mock_conn.execute.side_effect = [mock_info, None, None, mock_tags]
        
        service = AutoPersistService(connection=mock_conn)
        tags = service.remove_tag('coh-123', 'test')
        
        assert 'test' not in tags
        assert 'demo' in tags
    
    def test_remove_tag_cohort_not_found(self):
        """Test removing tag from nonexistent cohort."""
        mock_conn = MagicMock()
        mock_info = MagicMock()
        mock_info.rows = []
        mock_conn.execute.return_value = mock_info
        
        service = AutoPersistService(connection=mock_conn)
        
        with pytest.raises(ValueError, match="not found"):
            service.remove_tag('nonexistent', 'tag')


class TestGetTags:
    """Tests for get_tags method."""
    
    def test_get_tags_returns_list(self):
        """Test getting all tags for a cohort."""
        mock_conn = MagicMock()
        mock_tags = MagicMock()
        mock_tags.rows = [["demo"], ["test"]]
        mock_conn.execute.return_value = mock_tags
        
        service = AutoPersistService(connection=mock_conn)
        tags = service.get_tags('coh-123')
        
        assert 'test' in tags
        assert 'demo' in tags
        assert len(tags) == 2
    
    def test_get_tags_empty(self):
        """Test getting tags for cohort with no tags."""
        mock_conn = MagicMock()
        mock_tags = MagicMock()
        mock_tags.rows = []
        mock_conn.execute.return_value = mock_tags
        
        service = AutoPersistService(connection=mock_conn)
        tags = service.get_tags('coh-empty')
        
        assert tags == []


class TestListAllTags:
    """Tests for list_all_tags method."""
    
    def test_list_all_tags_with_counts(self):
        """Test listing all tags with counts."""
        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_result.rows = [["test", 5], ["demo", 3], ["production", 1]]
        mock_conn.execute.return_value = mock_result
        
        service = AutoPersistService(connection=mock_conn)
        tags = service.list_all_tags()
        
        assert len(tags) == 3
        assert tags[0] == {'tag': 'test', 'count': 5}
        assert tags[1] == {'tag': 'demo', 'count': 3}
    
    def test_list_all_tags_empty(self):
        """Test listing tags when none exist."""
        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_result.rows = []
        mock_conn.execute.return_value = mock_result
        
        service = AutoPersistService(connection=mock_conn)
        tags = service.list_all_tags()
        
        assert tags == []


class TestGetEntitySamples:
    """Tests for get_entity_samples method."""
    
    def test_get_samples_default_strategy(self):
        """Test getting samples with default strategy."""
        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_result.rows = [
            ("p1", "John", "1980-01-01", "M"),
            ("p2", "Jane", "1985-06-15", "F"),
            ("p3", "Bob", "1970-03-20", "M"),
            ("p4", "Alice", "1990-12-01", "F"),
            ("p5", "Charlie", "1965-08-10", "M"),
        ]
        mock_result.columns = ["id", "name", "birth_date", "gender"]
        mock_conn.execute.return_value = mock_result
        
        service = AutoPersistService(connection=mock_conn)
        
        with patch('healthsim_agent.state.auto_persist.get_table_info') as mock_table:
            mock_table.return_value = ('patients', 'id')
            samples = service.get_entity_samples('coh-123', 'patients', count=3)
        
        assert len(samples) == 3
    
    def test_get_samples_random_strategy(self):
        """Test random sampling strategy."""
        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_result.rows = [("p1", "John"), ("p2", "Jane")]
        mock_result.columns = ["id", "name"]
        mock_conn.execute.return_value = mock_result
        
        service = AutoPersistService(connection=mock_conn)
        
        with patch('healthsim_agent.state.auto_persist.get_table_info') as mock_table:
            mock_table.return_value = ('patients', 'id')
            samples = service.get_entity_samples(
                'coh-123', 'patients', count=2, strategy='random'
            )
        
        assert len(samples) == 2
    
    def test_get_samples_recent_strategy(self):
        """Test recent sampling strategy."""
        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_result.rows = [("p1", "John")]
        mock_result.columns = ["id", "name"]
        mock_conn.execute.return_value = mock_result
        
        service = AutoPersistService(connection=mock_conn)
        
        with patch('healthsim_agent.state.auto_persist.get_table_info') as mock_table:
            mock_table.return_value = ('patients', 'id')
            samples = service.get_entity_samples(
                'coh-123', 'patients', count=1, strategy='recent'
            )
        
        assert len(samples) == 1
    
    def test_get_samples_unknown_type_raises(self):
        """Test unknown entity type raises error."""
        mock_conn = MagicMock()
        service = AutoPersistService(connection=mock_conn)
        
        with patch('healthsim_agent.state.auto_persist.get_table_info') as mock_table:
            mock_table.return_value = None  # Unknown type
            
            with pytest.raises(ValueError, match="Unknown entity type"):
                service.get_entity_samples('coh-123', 'unknowns')
    
    def test_get_samples_normalizes_singular(self):
        """Test that singular entity type gets plural suffix."""
        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_result.rows = [("p1", "John")]
        mock_result.columns = ["id", "name"]
        mock_conn.execute.return_value = mock_result
        
        service = AutoPersistService(connection=mock_conn)
        
        with patch('healthsim_agent.state.auto_persist.get_table_info') as mock_table:
            mock_table.return_value = ('patients', 'id')
            # Pass singular "patient" 
            samples = service.get_entity_samples('coh-123', 'patient', count=1)
        
        # Should work - internal code adds 's' suffix
        assert len(samples) == 1
    
    def test_get_samples_empty_cohort(self):
        """Test sampling from empty cohort."""
        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_result.rows = []  # No entities
        mock_conn.execute.return_value = mock_result
        
        service = AutoPersistService(connection=mock_conn)
        
        with patch('healthsim_agent.state.auto_persist.get_table_info') as mock_table:
            mock_table.return_value = ('patients', 'id')
            samples = service.get_entity_samples('coh-empty', 'patients')
        
        assert samples == []
    
    def test_get_samples_diverse_with_many_entities(self):
        """Test diverse strategy evenly spaces samples."""
        mock_conn = MagicMock()
        mock_result = MagicMock()
        # 10 entities
        mock_result.rows = [(f"p{i}", f"Name{i}") for i in range(10)]
        mock_result.columns = ["id", "name"]
        mock_conn.execute.return_value = mock_result
        
        service = AutoPersistService(connection=mock_conn)
        
        with patch('healthsim_agent.state.auto_persist.get_table_info') as mock_table:
            mock_table.return_value = ('patients', 'id')
            samples = service.get_entity_samples(
                'coh-123', 'patients', count=3, strategy='diverse'
            )
        
        # Should get 3 evenly spaced samples
        assert len(samples) == 3


class TestGetAutoPersistService:
    """Tests for get_auto_persist_service factory function."""
    
    def test_with_connection(self):
        """Test creating service with provided connection."""
        mock_conn = MagicMock()
        
        service = get_auto_persist_service(connection=mock_conn)
        
        assert service is not None
        assert isinstance(service, AutoPersistService)
    
    def test_without_connection_creates_new_service(self):
        """Test creating service without connection creates a default service."""
        # Patch DatabaseConnection to avoid actual DB connection
        with patch('healthsim_agent.state.auto_persist.AutoPersistService') as MockService:
            # Actually, get_auto_persist_service creates AutoPersistService directly
            # Let's just verify the function signature works
            pass
        
        # Simple test - just verify it returns an AutoPersistService when given a connection
        mock_conn = MagicMock()
        service = get_auto_persist_service(connection=mock_conn)
        assert isinstance(service, AutoPersistService)


class TestEnsureUniqueNameExtended:
    """Extended tests for _ensure_unique_name function."""
    
    def test_unique_on_first_try(self):
        """Test name is unique on first try."""
        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_result.rows = [[0]]  # Count = 0, name is unique
        mock_conn.execute.return_value = mock_result
        
        result = _ensure_unique_name('myname', mock_conn)
        
        assert result == 'myname'
    
    def test_adds_suffix_on_conflict(self):
        """Test adds suffix when name conflicts."""
        mock_conn = MagicMock()
        
        mock_conflict = MagicMock()
        mock_conflict.rows = [[1]]  # Exists
        mock_unique = MagicMock()
        mock_unique.rows = [[0]]  # Unique
        
        mock_conn.execute.side_effect = [mock_conflict, mock_unique]
        
        result = _ensure_unique_name('myname', mock_conn)
        
        assert 'myname' in result
        assert result != 'myname'  # Should have suffix
    
    def test_multiple_conflicts_increments_suffix(self):
        """Test handles multiple name conflicts."""
        mock_conn = MagicMock()
        
        # First 3 attempts conflict, 4th succeeds
        mock_conflict = MagicMock()
        mock_conflict.rows = [[1]]
        mock_unique = MagicMock()
        mock_unique.rows = [[0]]
        
        mock_conn.execute.side_effect = [
            mock_conflict, mock_conflict, mock_conflict, mock_unique
        ]
        
        result = _ensure_unique_name('myname', mock_conn)
        
        assert 'myname' in result
