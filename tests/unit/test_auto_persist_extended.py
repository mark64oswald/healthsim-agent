"""Extended tests for auto_persist module.

Covers additional methods: delete, rename, tags, clone, merge, export.
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
    get_auto_persist_service,
)


@pytest.fixture
def mock_connection():
    """Create a mock connection."""
    conn = MagicMock()
    conn.execute.return_value = MagicMock(rows=[])
    return conn


@pytest.fixture
def service(mock_connection):
    """Create AutoPersistService with mock connection."""
    return AutoPersistService(mock_connection)


class TestDeleteCohort:
    """Tests for delete_cohort method."""
    
    def test_delete_requires_confirm(self, service):
        """Delete requires confirm=True."""
        with pytest.raises(ValueError, match="confirm=True"):
            service.delete_cohort("coh-test-1", confirm=False)
    
    def test_delete_nonexistent_cohort(self, service, mock_connection):
        """Delete nonexistent cohort raises error."""
        mock_result = MagicMock()
        mock_result.rows = []
        mock_connection.execute.return_value = mock_result
        
        with pytest.raises(ValueError, match="not found"):
            service.delete_cohort("nonexistent-id", confirm=True)
    
    def test_delete_cohort_success(self, service, mock_connection):
        """Successful cohort deletion."""
        # Mock cohort exists
        mock_result = MagicMock()
        mock_result.rows = [("test-cohort", "Test description")]
        mock_connection.execute.return_value = mock_result
        
        # Mock table exists check
        with patch.object(service, '_table_exists', return_value=False):
            result = service.delete_cohort("coh-test-1", confirm=True)
        
        assert result["cohort_id"] == "coh-test-1"
        assert result["name"] == "test-cohort"


class TestRenameCohort:
    """Tests for rename_cohort method."""
    
    def test_rename_cohort_success(self, service, mock_connection):
        """Successful cohort rename."""
        # Mock current name lookup
        mock_result = MagicMock()
        mock_result.rows = [("old-name",)]
        mock_connection.execute.return_value = mock_result
        
        with patch('healthsim_agent.state.auto_persist._ensure_unique_name', return_value="new-name"):
            old_name, new_name = service.rename_cohort("coh-test-1", "new-name")
        
        assert old_name == "old-name"
        assert new_name == "new-name"
    
    def test_rename_nonexistent_cohort(self, service, mock_connection):
        """Rename nonexistent cohort raises error."""
        mock_result = MagicMock()
        mock_result.rows = []
        mock_connection.execute.return_value = mock_result
        
        with pytest.raises(ValueError, match="not found"):
            service.rename_cohort("nonexistent-id", "new-name")


class TestTagManagement:
    """Tests for tag management methods."""
    
    def test_add_tag_success(self, service, mock_connection):
        """Add a new tag successfully."""
        # Mock cohort exists
        mock_cohort_info = MagicMock()
        mock_cohort_info.rows = [("test",)]
        
        # Mock tag check (doesn't exist)
        mock_tag_check = MagicMock()
        mock_tag_check.rows = [[0]]
        
        # Mock get_tags return
        mock_tags = MagicMock()
        mock_tags.rows = [("new-tag",), ("existing-tag",)]
        
        mock_connection.execute.side_effect = [mock_cohort_info, mock_cohort_info, mock_tag_check, MagicMock(), MagicMock(), mock_tags]
        
        with patch.object(service, '_get_cohort_info', return_value={"id": "coh-1"}):
            with patch.object(service, 'get_tags', return_value=["new-tag", "existing-tag"]):
                tags = service.add_tag("coh-test-1", "new-tag")
        
        assert "new-tag" in tags
    
    def test_add_empty_tag(self, service, mock_connection):
        """Empty tag raises error."""
        with patch.object(service, '_get_cohort_info', return_value={"id": "coh-1"}):
            with pytest.raises(ValueError, match="empty"):
                service.add_tag("coh-test-1", "  ")
    
    def test_add_tag_nonexistent_cohort(self, service):
        """Add tag to nonexistent cohort raises error."""
        with patch.object(service, '_get_cohort_info', return_value=None):
            with pytest.raises(ValueError, match="not found"):
                service.add_tag("nonexistent", "tag")
    
    def test_remove_tag_nonexistent_cohort(self, service):
        """Remove tag from nonexistent cohort raises error."""
        with patch.object(service, '_get_cohort_info', return_value=None):
            with pytest.raises(ValueError, match="not found"):
                service.remove_tag("nonexistent", "tag")
    
    def test_remove_tag_success(self, service, mock_connection):
        """Remove tag successfully."""
        with patch.object(service, '_get_cohort_info', return_value={"id": "coh-1"}):
            with patch.object(service, 'get_tags', return_value=["remaining-tag"]):
                with patch.object(service, '_update_cohort_timestamp'):
                    tags = service.remove_tag("coh-test-1", "tag-to-remove")
        
        assert "remaining-tag" in tags
    
    def test_get_tags_returns_list(self, service, mock_connection):
        """Get tags returns a list."""
        mock_result = MagicMock()
        mock_result.rows = [("tag1",), ("tag2",), ("tag3",)]
        mock_connection.execute.return_value = mock_result
        
        tags = service.get_tags("coh-test-1")
        
        assert isinstance(tags, list)
        assert "tag1" in tags
        assert "tag2" in tags
        assert "tag3" in tags
    
    def test_get_tags_empty(self, service, mock_connection):
        """Get tags returns empty list when none exist."""
        mock_result = MagicMock()
        mock_result.rows = []
        mock_connection.execute.return_value = mock_result
        
        tags = service.get_tags("coh-test-1")
        
        assert tags == []
    
    def test_list_all_tags(self, service, mock_connection):
        """List all tags returns list."""
        mock_result = MagicMock()
        mock_result.rows = [("demo", 5), ("test", 3)]
        mock_connection.execute.return_value = mock_result
        
        tags = service.list_all_tags()
        
        assert isinstance(tags, list)


class TestExportResult:
    """Tests for ExportResult dataclass."""
    
    def test_export_result_to_dict(self):
        """ExportResult converts to dict."""
        result = ExportResult(
            cohort_id="coh-123",
            cohort_name="test",
            format="json",
            file_path="/tmp/export.json",
            total_entities=100,
            file_size_bytes=5000,
            entities_exported={"patients": 50, "encounters": 50},
        )
        
        d = result.to_dict()
        
        assert d["cohort_id"] == "coh-123"
        assert d["format"] == "json"
        assert d["total_entities"] == 100
        assert d["entities_exported"]["patients"] == 50
    
    def test_export_result_fields(self):
        """ExportResult has expected fields."""
        result = ExportResult(
            cohort_id="coh-1",
            cohort_name="test",
            format="csv",
            file_path="/tmp/test.csv",
            total_entities=50,
            file_size_bytes=2500,
            entities_exported={"patients": 50},
        )
        
        assert result.cohort_id == "coh-1"
        assert result.format == "csv"
        assert result.file_size_bytes == 2500


class TestGetAutoPersistService:
    """Tests for get_auto_persist_service function."""
    
    def test_get_service_with_connection(self):
        """Get service with explicit connection."""
        mock_conn = MagicMock()
        
        service = get_auto_persist_service(connection=mock_conn)
        
        assert isinstance(service, AutoPersistService)
        assert service.conn is mock_conn


class TestEnsureUniqueName:
    """Tests for _ensure_unique_name function."""
    
    def test_name_already_unique(self):
        """Name that doesn't exist is returned as-is."""
        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_result.rows = [[0]]  # No existing cohort
        mock_conn.execute.return_value = mock_result
        
        result = _ensure_unique_name("brand-new-name", mock_conn)
        
        assert result == "brand-new-name"
    
    def test_name_conflict_adds_suffix(self):
        """Conflicting name gets suffix added."""
        mock_conn = MagicMock()
        
        # First call: name exists
        mock_exists = MagicMock()
        mock_exists.rows = [[1]]
        
        # Second call: name-2 doesn't exist
        mock_unique = MagicMock()
        mock_unique.rows = [[0]]
        
        mock_conn.execute.side_effect = [mock_exists, mock_unique]
        
        result = _ensure_unique_name("test-cohort", mock_conn)
        
        assert result == "test-cohort-2"
    
    def test_multiple_conflicts(self):
        """Multiple conflicts handled."""
        mock_conn = MagicMock()
        
        # name exists, name-2 exists, name-3 doesn't
        mock_exists = MagicMock()
        mock_exists.rows = [[1]]
        
        mock_unique = MagicMock()
        mock_unique.rows = [[0]]
        
        mock_conn.execute.side_effect = [mock_exists, mock_exists, mock_unique]
        
        result = _ensure_unique_name("test-cohort", mock_conn)
        
        assert result == "test-cohort-3"


class TestValidateQueryExtended:
    """Extended tests for _validate_query function."""
    
    def test_valid_select_passes(self):
        """Basic SELECT passes validation."""
        assert _validate_query("SELECT * FROM test") is True
    
    def test_valid_with_cte_passes(self):
        """CTE query passes validation."""
        assert _validate_query("WITH cte AS (SELECT 1) SELECT * FROM cte") is True
    
    def test_invalid_show_raises(self):
        """SHOW statement raises ValueError."""
        with pytest.raises(ValueError, match="SELECT"):
            _validate_query("SHOW TABLES")
    
    def test_invalid_alter_raises(self):
        """ALTER statement raises ValueError."""
        with pytest.raises(ValueError, match="SELECT"):
            _validate_query("ALTER TABLE x ADD COLUMN y")
    
    def test_invalid_grant_raises(self):
        """GRANT statement raises ValueError."""
        with pytest.raises(ValueError, match="SELECT"):
            _validate_query("GRANT SELECT ON x TO user")
    
    def test_invalid_exec_raises(self):
        """EXEC statement raises ValueError."""
        with pytest.raises(ValueError, match="SELECT"):
            _validate_query("EXEC sp_something")
    
    def test_nested_select_allowed(self):
        """Nested SELECT is allowed."""
        assert _validate_query("SELECT * FROM (SELECT id FROM test) sub") is True
    
    def test_union_allowed(self):
        """UNION query allowed."""
        assert _validate_query("SELECT id FROM a UNION SELECT id FROM b") is True
    
    def test_select_with_dangerous_keyword_blocked(self):
        """SELECT containing INSERT blocked."""
        with pytest.raises(ValueError):
            _validate_query("SELECT * FROM test; INSERT INTO bad VALUES (1)")


class TestQueryResultExtended:
    """Extended tests for QueryResult."""
    
    def test_large_page_offset(self):
        """Large page number calculates correct offset."""
        result = QueryResult(
            results=[],
            total_count=10000,
            page=99,
            page_size=100,
            has_more=True,
            query_executed="SELECT * FROM test",
        )
        
        assert result.offset == 9900
    
    def test_to_dict_all_fields(self):
        """All fields included in to_dict."""
        result = QueryResult(
            results=[{"a": 1}, {"a": 2}],
            total_count=1000,
            page=5,
            page_size=50,
            has_more=True,
            query_executed="SELECT a FROM test LIMIT 50 OFFSET 250",
        )
        
        d = result.to_dict()
        
        assert len(d["results"]) == 2
        assert d["total_count"] == 1000
        assert d["page"] == 5
        assert d["page_size"] == 50
        assert d["has_more"] is True
        assert "SELECT" in d["query_executed"]


class TestCohortBriefExtended:
    """Extended tests for CohortBrief."""
    
    def test_to_dict_with_tags(self):
        """Tags included in to_dict."""
        brief = CohortBrief(
            cohort_id="coh-1",
            name="test",
            description="Test cohort",
            entity_count=100,
            created_at=datetime(2025, 1, 15, 10, 30),
            updated_at=datetime(2025, 1, 15, 11, 0),
            tags=["demo", "test", "v1"],
        )
        
        d = brief.to_dict()
        
        assert d["tags"] == ["demo", "test", "v1"]
        assert "2025-01-15" in d["created_at"]
        assert "2025-01-15" in d["updated_at"]
    
    def test_to_dict_with_none_values(self):
        """None values handled in to_dict."""
        brief = CohortBrief(
            cohort_id="coh-1",
            name="test",
            description=None,
            entity_count=0,
            created_at=None,
            updated_at=None,
        )
        
        d = brief.to_dict()
        
        assert d["description"] is None
        assert d["created_at"] is None
        assert d["updated_at"] is None


class TestCloneResultExtended:
    """Extended tests for CloneResult."""
    
    def test_clone_result_to_dict(self):
        """CloneResult converts to dict."""
        result = CloneResult(
            source_cohort_id="coh-1",
            source_cohort_name="original",
            new_cohort_id="coh-2",
            new_cohort_name="copy",
            entities_cloned={"patients": 10, "encounters": 20},
            total_entities=30,
        )
        
        d = result.to_dict()
        
        assert d["source_cohort_id"] == "coh-1"
        assert d["new_cohort_id"] == "coh-2"
        assert d["total_entities"] == 30
        assert d["entities_cloned"]["patients"] == 10


class TestMergeResultExtended:
    """Extended tests for MergeResult."""
    
    def test_merge_result_to_dict(self):
        """MergeResult converts to dict."""
        result = MergeResult(
            source_cohort_ids=["coh-1", "coh-2"],
            source_cohort_names=["first", "second"],
            target_cohort_id="coh-merged",
            target_cohort_name="merged",
            entities_merged={"patients": 50},
            total_entities=50,
            conflicts_resolved=5,
        )
        
        d = result.to_dict()
        
        assert len(d["source_cohort_ids"]) == 2
        assert d["target_cohort_id"] == "coh-merged"
        assert d["conflicts_resolved"] == 5


class TestPersistResultExtended:
    """Extended tests for PersistResult."""
    
    def test_persist_result_with_summary(self):
        """PersistResult with summary."""
        mock_summary = MagicMock()
        mock_summary.to_dict.return_value = {"cohort_id": "coh-1", "entity_counts": {"patients": 5}}
        
        result = PersistResult(
            cohort_id="coh-1",
            cohort_name="test",
            entity_type="patient",
            entities_persisted=5,
            entity_ids=["p1", "p2", "p3", "p4", "p5"],
            summary=mock_summary,
            is_new_cohort=True,
        )
        
        d = result.to_dict()
        
        assert d["summary"] is not None
        assert d["summary"]["cohort_id"] == "coh-1"
