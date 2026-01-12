"""Extended tests for auto_persist module.

Covers methods not in the original test file:
- rename_cohort
- delete_cohort
- Tag management (add_tag, remove_tag, get_tags, list_all_tags)
- get_entity_samples
- Additional dataclass tests
"""

import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch, PropertyMock
import tempfile
import os
import duckdb

from healthsim_agent.state.auto_persist import (
    PersistResult,
    QueryResult,
    CohortBrief,
    CloneResult,
    MergeResult,
    ExportResult,
    AutoPersistService,
    _validate_query,
    _ensure_unique_name,
    get_auto_persist_service,
)


class TestCloneResult:
    """Tests for CloneResult dataclass."""
    
    def test_create_clone_result(self):
        """Test creating CloneResult."""
        result = CloneResult(
            source_cohort_id="src-123",
            source_cohort_name="source-cohort",
            new_cohort_id="new-456",
            new_cohort_name="cloned-cohort",
            entities_cloned={"patients": 50, "encounters": 100},
            total_entities=150,
        )
        
        assert result.source_cohort_id == "src-123"
        assert result.source_cohort_name == "source-cohort"
        assert result.new_cohort_id == "new-456"
        assert result.new_cohort_name == "cloned-cohort"
        assert result.entities_cloned == {"patients": 50, "encounters": 100}
        assert result.total_entities == 150
    
    def test_clone_result_to_dict(self):
        """Test CloneResult to_dict."""
        result = CloneResult(
            source_cohort_id="src-123",
            source_cohort_name="source",
            new_cohort_id="new-456",
            new_cohort_name="cloned",
            entities_cloned={"patients": 25},
            total_entities=25,
        )
        
        d = result.to_dict()
        
        assert d['source_cohort_id'] == "src-123"
        assert d['source_cohort_name'] == "source"
        assert d['new_cohort_id'] == "new-456"
        assert d['new_cohort_name'] == "cloned"
        assert d['entities_cloned'] == {"patients": 25}
        assert d['total_entities'] == 25


class TestMergeResult:
    """Tests for MergeResult dataclass."""
    
    def test_create_merge_result(self):
        """Test creating MergeResult."""
        result = MergeResult(
            source_cohort_ids=["coh-1", "coh-2", "coh-3"],
            source_cohort_names=["cohort-1", "cohort-2", "cohort-3"],
            target_cohort_id="merged-123",
            target_cohort_name="merged-cohort",
            entities_merged={"patients": 100, "encounters": 200},
            total_entities=300,
            conflicts_resolved=5,
        )
        
        assert result.source_cohort_ids == ["coh-1", "coh-2", "coh-3"]
        assert result.source_cohort_names == ["cohort-1", "cohort-2", "cohort-3"]
        assert result.target_cohort_id == "merged-123"
        assert result.total_entities == 300
        assert result.conflicts_resolved == 5
    
    def test_merge_result_to_dict(self):
        """Test MergeResult to_dict."""
        result = MergeResult(
            source_cohort_ids=["coh-1", "coh-2"],
            source_cohort_names=["name-1", "name-2"],
            target_cohort_id="merged-123",
            target_cohort_name="merged-cohort",
            entities_merged={"patients": 50},
            total_entities=50,
            conflicts_resolved=0,
        )
        
        d = result.to_dict()
        
        assert d['source_cohort_ids'] == ["coh-1", "coh-2"]
        assert d['source_cohort_names'] == ["name-1", "name-2"]
        assert d['target_cohort_id'] == "merged-123"
        assert d['total_entities'] == 50
        assert d['conflicts_resolved'] == 0


class TestExportResult:
    """Tests for ExportResult dataclass."""
    
    def test_create_export_result(self):
        """Test creating ExportResult."""
        result = ExportResult(
            cohort_id="coh-123",
            cohort_name="test-cohort",
            format="json",
            file_path="/tmp/export.json",
            entities_exported={"patients": 50},
            total_entities=50,
            file_size_bytes=1024,
        )
        
        assert result.cohort_id == "coh-123"
        assert result.cohort_name == "test-cohort"
        assert result.format == "json"
        assert result.file_path == "/tmp/export.json"
        assert result.entities_exported == {"patients": 50}
        assert result.total_entities == 50
        assert result.file_size_bytes == 1024
    
    def test_export_result_to_dict(self):
        """Test ExportResult to_dict."""
        result = ExportResult(
            cohort_id="coh-123",
            cohort_name="test",
            format="csv",
            file_path="/tmp/export.csv",
            entities_exported={"members": 100},
            total_entities=100,
            file_size_bytes=2048,
        )
        
        d = result.to_dict()
        
        assert d['cohort_id'] == "coh-123"
        assert d['cohort_name'] == "test"
        assert d['file_path'] == "/tmp/export.csv"
        assert d['format'] == "csv"
        assert d['entities_exported'] == {"members": 100}
        assert d['total_entities'] == 100
        assert d['file_size_bytes'] == 2048


class TestCohortBriefToDict:
    """Additional CohortBrief tests."""
    
    def test_to_dict_with_all_fields(self):
        """Test CohortBrief to_dict with all fields."""
        now = datetime.utcnow()
        
        brief = CohortBrief(
            cohort_id="coh-123",
            name="Test Cohort",
            description="Full cohort brief",
            entity_count=75,
            created_at=now,
            updated_at=now,
            tags=["test", "demo", "v1"],
        )
        
        d = brief.to_dict()
        
        assert d['cohort_id'] == "coh-123"
        assert d['name'] == "Test Cohort"
        assert d['description'] == "Full cohort brief"
        assert d['entity_count'] == 75
        assert d['tags'] == ["test", "demo", "v1"]
        assert 'created_at' in d
        assert 'updated_at' in d


class TestValidateQueryExtended:
    """Extended tests for _validate_query."""
    
    def test_allows_standard_select(self):
        """Valid SELECT queries pass."""
        assert _validate_query("SELECT * FROM patients") is True
        assert _validate_query("SELECT id, name FROM users WHERE age > 18") is True
    
    def test_allows_with_cte(self):
        """WITH (CTE) queries pass."""
        assert _validate_query("WITH cte AS (SELECT 1) SELECT * FROM cte") is True
    
    def test_blocks_update(self):
        """UPDATE queries raise ValueError."""
        with pytest.raises(ValueError):
            _validate_query("UPDATE patients SET name = 'test'")
    
    def test_blocks_insert(self):
        """INSERT queries raise ValueError."""
        with pytest.raises(ValueError):
            _validate_query("INSERT INTO patients VALUES (1, 'test')")
    
    def test_blocks_delete(self):
        """DELETE queries raise ValueError."""
        with pytest.raises(ValueError):
            _validate_query("DELETE FROM patients WHERE id = 1")
    
    def test_blocks_drop(self):
        """DROP queries raise ValueError."""
        with pytest.raises(ValueError):
            _validate_query("DROP TABLE patients")
    
    def test_blocks_truncate(self):
        """TRUNCATE queries raise ValueError."""
        with pytest.raises(ValueError):
            _validate_query("TRUNCATE TABLE patients")
    
    def test_blocks_alter(self):
        """ALTER queries raise ValueError."""
        with pytest.raises(ValueError):
            _validate_query("ALTER TABLE patients ADD COLUMN test VARCHAR")
    
    def test_blocks_create(self):
        """CREATE queries raise ValueError."""
        with pytest.raises(ValueError):
            _validate_query("CREATE TABLE test (id INT)")
    
    def test_case_insensitive(self):
        """Validation is case-insensitive."""
        with pytest.raises(ValueError):
            _validate_query("update patients set name = 'x'")
        with pytest.raises(ValueError):
            _validate_query("drop TABLE patients")


class TestRenameCohort:
    """Tests for rename_cohort method."""
    
    def test_rename_cohort_not_found(self):
        """Renaming nonexistent cohort raises error."""
        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_result.rows = []
        mock_conn.execute.return_value = mock_result
        
        service = AutoPersistService(connection=mock_conn)
        
        with pytest.raises(ValueError, match="not found"):
            service.rename_cohort("nonexistent", "new-name")


class TestDeleteCohort:
    """Tests for delete_cohort method."""
    
    def test_delete_cohort_requires_confirm(self):
        """Deletion without confirm=True raises error."""
        mock_conn = MagicMock()
        service = AutoPersistService(connection=mock_conn)
        
        with pytest.raises(ValueError, match="confirm=True"):
            service.delete_cohort("coh-123", confirm=False)
    
    def test_delete_cohort_not_found(self):
        """Deleting nonexistent cohort raises error."""
        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_result.rows = []
        mock_conn.execute.return_value = mock_result
        
        service = AutoPersistService(connection=mock_conn)
        
        with pytest.raises(ValueError, match="not found"):
            service.delete_cohort("nonexistent", confirm=True)


class TestTagManagement:
    """Tests for tag management methods."""
    
    def test_add_tag_cohort_not_found(self):
        """Adding tag to nonexistent cohort raises error."""
        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_result.rows = []
        mock_conn.execute.return_value = mock_result
        
        service = AutoPersistService(connection=mock_conn)
        
        with pytest.raises(ValueError, match="not found"):
            service.add_tag("nonexistent", "tag")
    
    def test_add_tag_empty_raises(self):
        """Adding empty tag raises error."""
        mock_conn = MagicMock()
        cohort_info_result = MagicMock()
        cohort_info_result.rows = [("coh-123", "Test", "desc", None, None)]
        mock_conn.execute.return_value = cohort_info_result
        
        service = AutoPersistService(connection=mock_conn)
        
        with pytest.raises(ValueError, match="empty"):
            service.add_tag("coh-123", "   ")
    
    def test_remove_tag_cohort_not_found(self):
        """Removing tag from nonexistent cohort raises error."""
        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_result.rows = []
        mock_conn.execute.return_value = mock_result
        
        service = AutoPersistService(connection=mock_conn)
        
        with pytest.raises(ValueError, match="not found"):
            service.remove_tag("nonexistent", "tag")
    
    def test_get_tags_empty(self):
        """Getting tags for cohort with none returns empty list."""
        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_result.rows = []
        mock_conn.execute.return_value = mock_result
        
        service = AutoPersistService(connection=mock_conn)
        result = service.get_tags("coh-123")
        
        assert result == []
    
    def test_get_tags_with_tags(self):
        """Getting tags returns list of tags."""
        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_result.rows = [("alpha",), ("beta",), ("gamma",)]
        mock_conn.execute.return_value = mock_result
        
        service = AutoPersistService(connection=mock_conn)
        result = service.get_tags("coh-123")
        
        assert result == ["alpha", "beta", "gamma"]
    
    def test_list_all_tags_empty(self):
        """list_all_tags with no tags returns empty list."""
        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_result.rows = []
        mock_conn.execute.return_value = mock_result
        
        service = AutoPersistService(connection=mock_conn)
        result = service.list_all_tags()
        
        assert result == []
    
    def test_list_all_tags_with_counts(self):
        """list_all_tags returns tags with counts."""
        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_result.rows = [("test", 5), ("demo", 3), ("v1", 1)]
        mock_conn.execute.return_value = mock_result
        
        service = AutoPersistService(connection=mock_conn)
        result = service.list_all_tags()
        
        assert len(result) == 3
        assert result[0] == {'tag': 'test', 'count': 5}
        assert result[1] == {'tag': 'demo', 'count': 3}


class TestGetAutoPersistService:
    """Tests for get_auto_persist_service factory function."""
    
    def test_get_service_with_connection(self):
        """Get service with provided connection."""
        mock_conn = MagicMock()
        service = get_auto_persist_service(connection=mock_conn)
        
        assert isinstance(service, AutoPersistService)


class TestPersistResultWithSummary:
    """Test PersistResult with summary object."""
    
    def test_to_dict_with_summary(self):
        """Test to_dict when summary is present."""
        from healthsim_agent.state.summary import CohortSummary
        
        mock_summary = MagicMock(spec=CohortSummary)
        mock_summary.to_dict.return_value = {
            'cohort_id': 'coh-123',
            'name': 'Test',
            'total_entities': 10,
        }
        
        result = PersistResult(
            cohort_id="coh-123",
            cohort_name="test-cohort",
            entity_type="patient",
            entities_persisted=10,
            entity_ids=["p1"],
            summary=mock_summary,
            is_new_cohort=True,
        )
        
        d = result.to_dict()
        
        assert d['summary'] is not None
        assert d['summary']['cohort_id'] == 'coh-123'


class TestQueryResultEdgeCases:
    """Edge cases for QueryResult."""
    
    def test_empty_results(self):
        """QueryResult with empty results."""
        result = QueryResult(
            results=[],
            total_count=0,
            page=0,
            page_size=10,
            has_more=False,
            query_executed="SELECT * FROM empty_table",
        )
        
        assert result.results == []
        assert result.total_count == 0
        assert result.has_more is False
    
    def test_large_page_offset(self):
        """QueryResult with large page number."""
        result = QueryResult(
            results=[],
            total_count=10000,
            page=99,
            page_size=100,
            has_more=False,
            query_executed="SELECT * FROM big_table LIMIT 100 OFFSET 9900",
        )
        
        assert result.offset == 9900


class TestEnsureUniqueName:
    """Tests for _ensure_unique_name helper."""
    
    def test_unique_name_returned_directly(self):
        """Name that doesn't exist is returned directly."""
        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_result.rows = [(0,)]
        mock_conn.execute.return_value = mock_result
        
        result = _ensure_unique_name("test-cohort", mock_conn)
        
        assert result == "test-cohort"
    
    def test_unique_name_with_suffix(self):
        """Name collision gets suffix starting at -2."""
        mock_conn = MagicMock()
        
        # First call: base name exists, second call: suffixed name doesn't exist
        # The function starts counter at 1, increments to 2, so first suffix is -2
        mock_result_exists = MagicMock()
        mock_result_exists.rows = [(1,)]
        mock_result_not_exists = MagicMock()
        mock_result_not_exists.rows = [(0,)]
        
        mock_conn.execute.side_effect = [mock_result_exists, mock_result_not_exists]
        
        result = _ensure_unique_name("test-cohort", mock_conn)
        
        assert result == "test-cohort-2"
