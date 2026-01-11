"""
Comprehensive tests for auto_persist module.

Tests cover:
- Result dataclasses (PersistResult, QueryResult, CohortBrief, CloneResult, MergeResult, ExportResult)
- Query validation (SQL injection protection)
- AutoPersistService class
"""

import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch


class TestPersistResult:
    """Tests for PersistResult dataclass."""
    
    def test_create_basic_result(self):
        """Test creating a basic PersistResult."""
        from healthsim_agent.state.auto_persist import PersistResult
        
        result = PersistResult(
            cohort_id="coh-123",
            cohort_name="test-cohort",
            entity_type="patient",
            entities_persisted=10,
            entity_ids=["p1", "p2", "p3"],
            summary=None,
            is_new_cohort=True,
        )
        
        assert result.cohort_id == "coh-123"
        assert result.cohort_name == "test-cohort"
        assert result.entity_type == "patient"
        assert result.entities_persisted == 10
        assert len(result.entity_ids) == 3
        assert result.is_new_cohort is True
        assert result.batch_number is None
        assert result.total_batches is None
    
    def test_create_result_with_batches(self):
        """Test creating PersistResult with batch information."""
        from healthsim_agent.state.auto_persist import PersistResult
        
        result = PersistResult(
            cohort_id="coh-123",
            cohort_name="test-cohort",
            entity_type="patient",
            entities_persisted=100,
            entity_ids=["p1"],
            summary=None,
            is_new_cohort=False,
            batch_number=2,
            total_batches=5,
        )
        
        assert result.batch_number == 2
        assert result.total_batches == 5
        assert result.is_new_cohort is False
    
    def test_to_dict_without_summary(self):
        """Test to_dict conversion without summary."""
        from healthsim_agent.state.auto_persist import PersistResult
        
        result = PersistResult(
            cohort_id="coh-123",
            cohort_name="test-cohort",
            entity_type="patient",
            entities_persisted=10,
            entity_ids=["p1", "p2"],
            summary=None,
            is_new_cohort=True,
        )
        
        d = result.to_dict()
        
        assert d['cohort_id'] == "coh-123"
        assert d['cohort_name'] == "test-cohort"
        assert d['entity_type'] == "patient"
        assert d['entities_persisted'] == 10
        assert d['entity_ids'] == ["p1", "p2"]
        assert d['summary'] is None
        assert d['is_new_cohort'] is True


class TestQueryResult:
    """Tests for QueryResult dataclass."""
    
    def test_create_query_result(self):
        """Test creating QueryResult."""
        from healthsim_agent.state.auto_persist import QueryResult
        
        result = QueryResult(
            results=[{"id": "1", "name": "Test"}],
            total_count=100,
            page=0,
            page_size=10,
            has_more=True,
            query_executed="SELECT * FROM test",
        )
        
        assert result.results == [{"id": "1", "name": "Test"}]
        assert result.total_count == 100
        assert result.page == 0
        assert result.page_size == 10
        assert result.has_more is True
    
    def test_offset_property(self):
        """Test offset calculation."""
        from healthsim_agent.state.auto_persist import QueryResult
        
        result = QueryResult(
            results=[],
            total_count=100,
            page=3,
            page_size=10,
            has_more=True,
            query_executed="SELECT * FROM test",
        )
        
        assert result.offset == 30
    
    def test_offset_first_page(self):
        """Test offset for first page."""
        from healthsim_agent.state.auto_persist import QueryResult
        
        result = QueryResult(
            results=[],
            total_count=100,
            page=0,
            page_size=25,
            has_more=True,
            query_executed="SELECT * FROM test",
        )
        
        assert result.offset == 0
    
    def test_to_dict(self):
        """Test to_dict conversion."""
        from healthsim_agent.state.auto_persist import QueryResult
        
        result = QueryResult(
            results=[{"id": "1"}],
            total_count=50,
            page=2,
            page_size=20,
            has_more=False,
            query_executed="SELECT id FROM test",
        )
        
        d = result.to_dict()
        
        assert d['results'] == [{"id": "1"}]
        assert d['total_count'] == 50
        assert d['page'] == 2
        assert d['page_size'] == 20
        assert d['has_more'] is False
        assert d['query_executed'] == "SELECT id FROM test"


class TestCohortBrief:
    """Tests for CohortBrief dataclass."""
    
    def test_create_cohort_brief(self):
        """Test creating CohortBrief."""
        from healthsim_agent.state.auto_persist import CohortBrief
        
        now = datetime.utcnow()
        brief = CohortBrief(
            cohort_id="coh-123",
            name="Test Cohort",
            description="A test cohort",
            entity_count=50,
            created_at=now,
            updated_at=now,
            tags=["test", "demo"],
        )
        
        assert brief.cohort_id == "coh-123"
        assert brief.name == "Test Cohort"
        assert brief.entity_count == 50
        assert brief.tags == ["test", "demo"]
    
    def test_create_minimal_brief(self):
        """Test creating CohortBrief with minimal fields."""
        from healthsim_agent.state.auto_persist import CohortBrief
        
        brief = CohortBrief(
            cohort_id="coh-123",
            name="Minimal",
            description=None,
            entity_count=0,
            created_at=None,
            updated_at=None,
        )
        
        assert brief.description is None
        assert brief.created_at is None
        assert brief.tags == []  # default factory
    
    def test_to_dict(self):
        """Test to_dict conversion."""
        from healthsim_agent.state.auto_persist import CohortBrief
        
        now = datetime(2025, 1, 15, 10, 30, 0)
        brief = CohortBrief(
            cohort_id="coh-123",
            name="Test",
            description="Desc",
            entity_count=25,
            created_at=now,
            updated_at=now,
            tags=["tag1"],
        )
        
        d = brief.to_dict()
        
        assert d['cohort_id'] == "coh-123"
        assert d['name'] == "Test"
        assert d['description'] == "Desc"
        assert d['entity_count'] == 25
        assert d['created_at'] == "2025-01-15T10:30:00"
        assert d['tags'] == ["tag1"]
    
    def test_to_dict_with_none_dates(self):
        """Test to_dict handles None dates."""
        from healthsim_agent.state.auto_persist import CohortBrief
        
        brief = CohortBrief(
            cohort_id="coh-123",
            name="Test",
            description=None,
            entity_count=0,
            created_at=None,
            updated_at=None,
        )
        
        d = brief.to_dict()
        
        assert d['created_at'] is None
        assert d['updated_at'] is None


class TestCloneResult:
    """Tests for CloneResult dataclass."""
    
    def test_create_clone_result(self):
        """Test creating CloneResult."""
        from healthsim_agent.state.auto_persist import CloneResult
        
        result = CloneResult(
            source_cohort_id="src-123",
            source_cohort_name="Source",
            new_cohort_id="new-456",
            new_cohort_name="Source-copy",
            entities_cloned={"patient": 10, "encounter": 50},
            total_entities=60,
        )
        
        assert result.source_cohort_id == "src-123"
        assert result.new_cohort_id == "new-456"
        assert result.entities_cloned["patient"] == 10
        assert result.total_entities == 60
    
    def test_to_dict(self):
        """Test to_dict conversion."""
        from healthsim_agent.state.auto_persist import CloneResult
        
        result = CloneResult(
            source_cohort_id="src-123",
            source_cohort_name="Source",
            new_cohort_id="new-456",
            new_cohort_name="Cloned",
            entities_cloned={"member": 5},
            total_entities=5,
        )
        
        d = result.to_dict()
        
        assert d['source_cohort_id'] == "src-123"
        assert d['new_cohort_id'] == "new-456"
        assert d['entities_cloned'] == {"member": 5}


class TestMergeResult:
    """Tests for MergeResult dataclass."""
    
    def test_create_merge_result(self):
        """Test creating MergeResult."""
        from healthsim_agent.state.auto_persist import MergeResult
        
        result = MergeResult(
            source_cohort_ids=["coh-1", "coh-2"],
            source_cohort_names=["Cohort A", "Cohort B"],
            target_cohort_id="merged-123",
            target_cohort_name="Merged Cohort",
            entities_merged={"patient": 20, "encounter": 100},
            total_entities=120,
            conflicts_resolved=5,
        )
        
        assert len(result.source_cohort_ids) == 2
        assert result.target_cohort_id == "merged-123"
        assert result.conflicts_resolved == 5
    
    def test_to_dict(self):
        """Test to_dict conversion."""
        from healthsim_agent.state.auto_persist import MergeResult
        
        result = MergeResult(
            source_cohort_ids=["a"],
            source_cohort_names=["A"],
            target_cohort_id="t",
            target_cohort_name="Target",
            entities_merged={},
            total_entities=0,
            conflicts_resolved=0,
        )
        
        d = result.to_dict()
        
        assert 'source_cohort_ids' in d
        assert 'conflicts_resolved' in d


class TestExportResult:
    """Tests for ExportResult dataclass."""
    
    def test_create_export_result(self):
        """Test creating ExportResult."""
        from healthsim_agent.state.auto_persist import ExportResult
        
        result = ExportResult(
            cohort_id="coh-123",
            cohort_name="Test",
            format="parquet",
            file_path="/tmp/export.parquet",
            entities_exported={"patient": 100},
            total_entities=100,
            file_size_bytes=1024000,
        )
        
        assert result.format == "parquet"
        assert result.file_size_bytes == 1024000
    
    def test_to_dict(self):
        """Test to_dict conversion."""
        from healthsim_agent.state.auto_persist import ExportResult
        
        result = ExportResult(
            cohort_id="coh-123",
            cohort_name="Test",
            format="csv",
            file_path="/tmp/test.csv",
            entities_exported={},
            total_entities=0,
            file_size_bytes=0,
        )
        
        d = result.to_dict()
        
        assert d['format'] == "csv"
        assert d['file_path'] == "/tmp/test.csv"


class TestValidateQuery:
    """Tests for _validate_query function."""
    
    def test_valid_select(self):
        """Test valid SELECT query."""
        from healthsim_agent.state.auto_persist import _validate_query
        
        assert _validate_query("SELECT * FROM patients") is True
    
    def test_valid_select_with_where(self):
        """Test valid SELECT with WHERE clause."""
        from healthsim_agent.state.auto_persist import _validate_query
        
        query = "SELECT id, name FROM patients WHERE age > 18"
        assert _validate_query(query) is True
    
    def test_valid_cte(self):
        """Test valid WITH (CTE) query."""
        from healthsim_agent.state.auto_persist import _validate_query
        
        query = "WITH active AS (SELECT * FROM patients) SELECT * FROM active"
        assert _validate_query(query) is True
    
    def test_invalid_insert(self):
        """Test INSERT query is rejected (fails SELECT check first)."""
        from healthsim_agent.state.auto_persist import _validate_query
        
        with pytest.raises(ValueError, match="must be a SELECT"):
            _validate_query("INSERT INTO patients VALUES (1, 'Test')")
    
    def test_invalid_update(self):
        """Test UPDATE query is rejected (fails SELECT check first)."""
        from healthsim_agent.state.auto_persist import _validate_query
        
        with pytest.raises(ValueError, match="must be a SELECT"):
            _validate_query("UPDATE patients SET name = 'Test'")
    
    def test_invalid_delete(self):
        """Test DELETE query is rejected (fails SELECT check first)."""
        from healthsim_agent.state.auto_persist import _validate_query
        
        with pytest.raises(ValueError, match="must be a SELECT"):
            _validate_query("DELETE FROM patients WHERE id = 1")
    
    def test_invalid_drop(self):
        """Test DROP query is rejected (fails SELECT check first)."""
        from healthsim_agent.state.auto_persist import _validate_query
        
        with pytest.raises(ValueError, match="must be a SELECT"):
            _validate_query("DROP TABLE patients")
    
    def test_invalid_create(self):
        """Test CREATE query is rejected (fails SELECT check first)."""
        from healthsim_agent.state.auto_persist import _validate_query
        
        with pytest.raises(ValueError, match="must be a SELECT"):
            _validate_query("CREATE TABLE test (id INT)")
    
    def test_invalid_truncate(self):
        """Test TRUNCATE query is rejected (fails SELECT check first)."""
        from healthsim_agent.state.auto_persist import _validate_query
        
        with pytest.raises(ValueError, match="must be a SELECT"):
            _validate_query("TRUNCATE TABLE patients")
    
    def test_select_with_insert_subquery_blocked(self):
        """Test pattern matching catches INSERT inside SELECT."""
        from healthsim_agent.state.auto_persist import _validate_query
        
        # This starts with SELECT but has INSERT in a subquery - disallowed pattern
        with pytest.raises(ValueError, match="disallowed pattern"):
            _validate_query("SELECT * FROM (INSERT INTO x VALUES (1))")
    
    def test_select_with_update_subquery_blocked(self):
        """Test pattern matching catches UPDATE inside SELECT."""
        from healthsim_agent.state.auto_persist import _validate_query
        
        with pytest.raises(ValueError, match="disallowed pattern"):
            _validate_query("SELECT * FROM patients WHERE 1=1 UPDATE x SET y=1")
    
    def test_invalid_sql_comment(self):
        """Test SQL comments are rejected."""
        from healthsim_agent.state.auto_persist import _validate_query
        
        with pytest.raises(ValueError, match="disallowed pattern"):
            _validate_query("SELECT * FROM patients -- comment")
    
    def test_invalid_multiple_statements(self):
        """Test multiple statements are rejected."""
        from healthsim_agent.state.auto_persist import _validate_query
        
        with pytest.raises(ValueError, match="disallowed pattern"):
            _validate_query("SELECT * FROM patients; DROP TABLE patients")
    
    def test_must_start_with_select_or_with(self):
        """Test query must start with SELECT or WITH."""
        from healthsim_agent.state.auto_persist import _validate_query
        
        with pytest.raises(ValueError, match="must be a SELECT"):
            _validate_query("EXPLAIN SELECT * FROM patients")
    
    def test_case_insensitive_validation(self):
        """Test validation is case insensitive."""
        from healthsim_agent.state.auto_persist import _validate_query
        
        assert _validate_query("select * from patients") is True
        
        with pytest.raises(ValueError):
            _validate_query("select * from patients; drop table x")




class TestAutoPersistService:
    """Tests for AutoPersistService class."""
    
    @pytest.fixture
    def mock_connection(self):
        """Create a mock database connection."""
        conn = MagicMock()
        return conn
    
    @pytest.fixture
    def service(self, mock_connection):
        """Create service with mock connection."""
        from healthsim_agent.state.auto_persist import AutoPersistService
        return AutoPersistService(connection=mock_connection)
    
    def test_init_with_connection(self, mock_connection):
        """Test initialization with provided connection."""
        from healthsim_agent.state.auto_persist import AutoPersistService
        
        service = AutoPersistService(connection=mock_connection)
        
        assert service._conn is mock_connection
    
    def test_init_without_connection(self):
        """Test initialization without connection (lazy loading)."""
        from healthsim_agent.state.auto_persist import AutoPersistService
        
        service = AutoPersistService()
        
        assert service._conn is None
    
    def test_create_cohort(self, service, mock_connection):
        """Test cohort creation."""
        mock_connection.execute.return_value = None
        
        cohort_id = service._create_cohort(
            name="Test Cohort",
            description="A test cohort",
            tags=["test", "demo"],
        )
        
        assert cohort_id is not None
        assert len(cohort_id) == 36  # UUID length
        
        # Should have called execute for cohort insert and each tag
        assert mock_connection.execute.call_count == 3
    
    def test_create_cohort_without_tags(self, service, mock_connection):
        """Test cohort creation without tags."""
        mock_connection.execute.return_value = None
        
        cohort_id = service._create_cohort(
            name="Simple Cohort",
        )
        
        assert cohort_id is not None
        # Only one call for cohort insert
        assert mock_connection.execute.call_count == 1
    
    def test_update_cohort_timestamp(self, service, mock_connection):
        """Test updating cohort timestamp."""
        service._update_cohort_timestamp("coh-123")
        
        mock_connection.execute.assert_called_once()
        call_args = mock_connection.execute.call_args
        assert "UPDATE cohorts" in call_args[0][0]
        assert "coh-123" in call_args[0][1]
    
    def test_get_cohort_info_found(self, service, mock_connection):
        """Test getting cohort info when found."""
        from datetime import datetime
        
        mock_result = MagicMock()
        mock_result.rows = [
            ("coh-123", "Test", "Description", datetime(2025, 1, 1), datetime(2025, 1, 2))
        ]
        mock_connection.execute.return_value = mock_result
        
        info = service._get_cohort_info("coh-123")
        
        assert info is not None
        # Note: Full assertion depends on the actual return structure
    
    def test_get_cohort_info_not_found(self, service, mock_connection):
        """Test getting cohort info when not found."""
        mock_result = MagicMock()
        mock_result.rows = []
        mock_connection.execute.return_value = mock_result
        
        info = service._get_cohort_info("nonexistent")
        
        assert info is None


class TestEnsureUniqueName:
    """Tests for _ensure_unique_name function."""
    
    def test_unique_name_first_try(self):
        """Test name is unique on first try."""
        from healthsim_agent.state.auto_persist import _ensure_unique_name
        
        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_result.rows = [[0]]  # No existing cohort
        mock_conn.execute.return_value = mock_result
        
        result = _ensure_unique_name("my-cohort", mock_conn)
        
        assert result == "my-cohort"
    
    def test_unique_name_with_suffix(self):
        """Test name gets suffix when collision exists."""
        from healthsim_agent.state.auto_persist import _ensure_unique_name
        
        mock_conn = MagicMock()
        
        # First call: name exists (count = 1)
        # Second call: name-2 doesn't exist (count = 0)
        mock_result_exists = MagicMock()
        mock_result_exists.rows = [[1]]
        
        mock_result_unique = MagicMock()
        mock_result_unique.rows = [[0]]
        
        mock_conn.execute.side_effect = [mock_result_exists, mock_result_unique]
        
        result = _ensure_unique_name("my-cohort", mock_conn)
        
        assert result == "my-cohort-2"


class TestDisallowedPatterns:
    """Tests for DISALLOWED_SQL_PATTERNS constant."""
    
    def test_patterns_list_exists(self):
        """Test disallowed patterns list exists."""
        from healthsim_agent.state.auto_persist import DISALLOWED_SQL_PATTERNS
        
        assert isinstance(DISALLOWED_SQL_PATTERNS, list)
        assert len(DISALLOWED_SQL_PATTERNS) > 0
    
    def test_patterns_include_dangerous_keywords(self):
        """Test patterns include dangerous SQL keywords."""
        from healthsim_agent.state.auto_persist import DISALLOWED_SQL_PATTERNS
        import re
        
        # These dangerous keywords should be blocked
        dangerous_keywords = ['INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE', 'ALTER', 'TRUNCATE']
        
        for keyword in dangerous_keywords:
            found = any(
                re.search(pattern, keyword, re.IGNORECASE)
                for pattern in DISALLOWED_SQL_PATTERNS
            )
            assert found, f"Pattern for {keyword} should be in disallowed list"


class TestCanonicalTables:
    """Tests for CANONICAL_TABLES constant."""
    
    def test_canonical_tables_list_exists(self):
        """Test canonical tables list exists."""
        from healthsim_agent.state.auto_persist import CANONICAL_TABLES
        
        assert isinstance(CANONICAL_TABLES, list)
        assert len(CANONICAL_TABLES) > 0
    
    def test_canonical_tables_have_id_columns(self):
        """Test all canonical tables have ID column specification."""
        from healthsim_agent.state.auto_persist import CANONICAL_TABLES
        
        for table in CANONICAL_TABLES:
            assert isinstance(table, tuple)
            assert len(table) == 2
            table_name, id_column = table
            assert isinstance(table_name, str)
            assert isinstance(id_column, str)
            assert 'id' in id_column.lower()
    
    def test_includes_core_tables(self):
        """Test core tables are included."""
        from healthsim_agent.state.auto_persist import CANONICAL_TABLES
        
        table_names = [t[0] for t in CANONICAL_TABLES]
        
        assert 'persons' in table_names
        assert 'providers' in table_names
        assert 'facilities' in table_names
    
    def test_includes_product_tables(self):
        """Test product-specific tables are included."""
        from healthsim_agent.state.auto_persist import CANONICAL_TABLES
        
        table_names = [t[0] for t in CANONICAL_TABLES]
        
        # PatientSim
        assert 'patients' in table_names
        assert 'encounters' in table_names
        
        # MemberSim  
        assert 'members' in table_names
        assert 'claims' in table_names
        
        # RxMemberSim
        assert 'rx_members' in table_names
        assert 'prescriptions' in table_names
        
        # TrialSim
        assert 'studies' in table_names
        assert 'subjects' in table_names
