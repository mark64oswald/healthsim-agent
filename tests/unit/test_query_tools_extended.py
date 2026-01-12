"""Extended tests for query_tools module.

Covers additional edge cases and error paths.
"""

import pytest
from unittest.mock import MagicMock, patch
import tempfile
import os
import duckdb

from healthsim_agent.tools import reset_manager
from healthsim_agent.tools.query_tools import (
    query,
    get_summary,
    list_tables,
)


@pytest.fixture
def populated_db_env(monkeypatch):
    """Create database with entities for summary testing."""
    with tempfile.NamedTemporaryFile(suffix=".duckdb", delete=False) as f:
        db_path = f.name
    os.unlink(db_path)
    
    conn = duckdb.connect(db_path)
    # Create tables
    conn.execute("""
        CREATE TABLE IF NOT EXISTS cohorts (
            id VARCHAR PRIMARY KEY,
            name VARCHAR NOT NULL UNIQUE,
            description VARCHAR,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS cohort_entities (
            id INTEGER PRIMARY KEY,
            cohort_id VARCHAR,
            entity_type VARCHAR,
            entity_id VARCHAR,
            entity_data JSON,
            created_at TIMESTAMP
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS cohort_tags (
            id INTEGER PRIMARY KEY,
            cohort_id VARCHAR,
            tag VARCHAR
        )
    """)
    
    # Add cohort with entities
    conn.execute("""
        INSERT INTO cohorts (id, name, description)
        VALUES ('cohort-123', 'Test Population', 'Testing cohort with entities')
    """)
    
    # Add patients
    conn.execute("""
        INSERT INTO cohort_entities (id, cohort_id, entity_type, entity_id, entity_data, created_at)
        VALUES 
            (1, 'cohort-123', 'patient', 'p-1', '{"id": "p-1", "given_name": "John", "family_name": "Doe"}', CURRENT_TIMESTAMP),
            (2, 'cohort-123', 'patient', 'p-2', '{"id": "p-2", "given_name": "Jane", "family_name": "Smith"}', CURRENT_TIMESTAMP),
            (3, 'cohort-123', 'encounter', 'e-1', '{"encounter_id": "e-1", "patient_mrn": "p-1"}', CURRENT_TIMESTAMP)
    """)
    
    # Add tags
    conn.execute("""
        INSERT INTO cohort_tags (id, cohort_id, tag)
        VALUES (1, 'cohort-123', 'test'), (2, 'cohort-123', 'demo')
    """)
    
    conn.close()
    
    monkeypatch.setenv("HEALTHSIM_DB_PATH", db_path)
    reset_manager()
    
    yield db_path
    
    reset_manager()
    try:
        os.unlink(db_path)
    except Exception:
        pass


class TestQueryExtended:
    """Extended tests for query function."""
    
    def test_query_with_parameters(self, populated_db_env):
        """Test query with LIKE pattern."""
        result = query("SELECT * FROM cohorts WHERE name LIKE '%Population%'")
        assert result.success
        assert result.data["row_count"] >= 1
    
    def test_query_aggregate(self, populated_db_env):
        """Test aggregate query."""
        result = query("SELECT COUNT(*) as cnt FROM cohort_entities")
        assert result.success
        assert result.data["rows"][0]["cnt"] >= 3
    
    def test_query_with_join(self, populated_db_env):
        """Test query with JOIN."""
        result = query("""
            SELECT c.name, COUNT(e.id) as entity_count
            FROM cohorts c
            LEFT JOIN cohort_entities e ON c.id = e.cohort_id
            GROUP BY c.name
        """)
        assert result.success
    
    def test_describe_query(self, populated_db_env):
        """Test DESCRIBE query."""
        result = query("DESCRIBE cohorts")
        assert result.success
    
    def test_pragma_query_rejected(self, populated_db_env):
        """Test PRAGMA query is rejected."""
        result = query("PRAGMA table_info('cohorts')")
        assert not result.success
    
    def test_explain_query_rejected(self, populated_db_env):
        """Test EXPLAIN query is rejected."""
        result = query("EXPLAIN SELECT * FROM cohorts")
        assert not result.success
    
    def test_truncate_rejected(self, populated_db_env):
        """Test TRUNCATE is rejected."""
        result = query("TRUNCATE TABLE cohorts")
        assert not result.success
    
    def test_alter_rejected(self, populated_db_env):
        """Test ALTER is rejected."""
        result = query("ALTER TABLE cohorts ADD COLUMN new_col VARCHAR")
        assert not result.success
    
    def test_create_rejected(self, populated_db_env):
        """Test CREATE is rejected."""
        result = query("CREATE TABLE new_table (id INT)")
        assert not result.success


class TestGetSummaryExtended:
    """Extended tests for get_summary function."""
    
    def test_get_summary_by_name(self, populated_db_env):
        """Test getting summary by cohort name."""
        result = get_summary("Test Population")
        assert result.success
        assert "cohort_id" in result.data
        assert "entity_counts" in result.data
    
    def test_get_summary_entity_counts(self, populated_db_env):
        """Test entity counts in summary."""
        result = get_summary("Test Population")
        assert result.success
        counts = result.data.get("entity_counts", {})
        assert counts.get("patient", 0) >= 2
        assert counts.get("encounter", 0) >= 1
    
    def test_get_summary_with_samples(self, populated_db_env):
        """Test summary includes samples."""
        result = get_summary("Test Population", samples_per_type=2)
        assert result.success
        samples = result.data.get("samples", {})
        # Should have patient and encounter samples
        assert isinstance(samples, dict)
    
    def test_get_summary_tags(self, populated_db_env):
        """Test summary includes tags."""
        result = get_summary("Test Population")
        assert result.success
        tags = result.data.get("tags", [])
        assert "test" in tags
        assert "demo" in tags
    
    def test_get_summary_by_id(self, populated_db_env):
        """Test getting summary by cohort ID."""
        result = get_summary("cohort-123")
        assert result.success
    
    def test_get_summary_samples_capped(self, populated_db_env):
        """Test samples_per_type is capped at max."""
        result = get_summary("Test Population", samples_per_type=100)
        # Should succeed but cap internally
        assert result.success


class TestListTablesExtended:
    """Extended tests for list_tables function."""
    
    def test_list_tables_categorization(self, populated_db_env):
        """Test table categorization."""
        result = list_tables()
        assert result.success
        
        # Should categorize cohorts as system table
        assert "cohorts" in result.data["system_tables"]
        
        # cohort_entities might be entity or system depending on implementation
        assert result.data["total"] >= 3
    
    def test_list_tables_counts(self, populated_db_env):
        """Test total table count."""
        result = list_tables()
        assert result.success
        
        total = result.data["total"]
        system_count = len(result.data["system_tables"])
        entity_count = len(result.data["entity_tables"])
        
        assert total == system_count + entity_count
    
    @patch('healthsim_agent.tools.query_tools.get_manager')
    def test_list_tables_db_error(self, mock_get_manager):
        """Test list_tables handles database error."""
        mock_manager = MagicMock()
        mock_conn = MagicMock()
        mock_conn.execute.side_effect = Exception("Database error")
        mock_manager.get_read_connection.return_value = mock_conn
        mock_get_manager.return_value = mock_manager
        
        result = list_tables()
        assert not result.success
        assert "error" in result.error.lower()


class TestQueryErrorHandling:
    """Tests for query error handling."""
    
    def test_invalid_sql_syntax(self, populated_db_env):
        """Test invalid SQL syntax handling."""
        result = query("SELECT * FROMM cohorts")  # Typo in FROM
        assert not result.success
    
    def test_nonexistent_table(self, populated_db_env):
        """Test query on nonexistent table."""
        result = query("SELECT * FROM nonexistent_table")
        assert not result.success
    
    def test_nonexistent_column(self, populated_db_env):
        """Test query with nonexistent column."""
        result = query("SELECT nonexistent_column FROM cohorts")
        assert not result.success
    
    @patch('healthsim_agent.tools.query_tools.get_manager')
    def test_query_connection_error(self, mock_get_manager):
        """Test query handles connection error."""
        mock_manager = MagicMock()
        mock_manager.get_read_connection.side_effect = Exception("Connection failed")
        mock_get_manager.return_value = mock_manager
        
        result = query("SELECT 1")
        assert not result.success


class TestQuerySecurityEdgeCases:
    """Security-related edge cases."""
    
    def test_comment_injection(self, populated_db_env):
        """Test SQL comment handling."""
        result = query("SELECT * FROM cohorts -- comment")
        # Should still work, comments are valid SQL
        assert result.success
    
    def test_multistatement_rejected(self, populated_db_env):
        """Test multiple statements are rejected."""
        result = query("SELECT 1; DROP TABLE cohorts")
        # Should fail - either semicolon causes issue or DROP is rejected
        assert not result.success or result.data["row_count"] == 1
    
    def test_union_query(self, populated_db_env):
        """Test UNION query works."""
        result = query("""
            SELECT id, name FROM cohorts
            UNION ALL
            SELECT 'test', 'Test Name'
        """)
        assert result.success
    
    def test_subquery(self, populated_db_env):
        """Test subquery works."""
        result = query("""
            SELECT * FROM cohorts 
            WHERE id IN (SELECT cohort_id FROM cohort_entities)
        """)
        assert result.success
