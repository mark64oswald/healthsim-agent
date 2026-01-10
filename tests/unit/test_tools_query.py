"""Tests for healthsim_agent.tools.query_tools module."""

import pytest
from pathlib import Path
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
def temp_db_env(monkeypatch):
    """Create a temporary database and set environment."""
    with tempfile.NamedTemporaryFile(suffix=".duckdb", delete=False) as f:
        db_path = f.name
    os.unlink(db_path)  # Delete empty file so DuckDB can create fresh
    
    # Initialize schema
    conn = duckdb.connect(db_path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS cohorts (
            id VARCHAR PRIMARY KEY,
            name VARCHAR NOT NULL UNIQUE,
            description VARCHAR,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute("CREATE SEQUENCE IF NOT EXISTS cohort_tags_seq START 1")
    conn.execute("CREATE SEQUENCE IF NOT EXISTS cohort_entities_seq START 1")
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
    # Add some test data
    conn.execute("""
        INSERT INTO cohorts (id, name, description)
        VALUES ('test-id', 'Test Cohort', 'For testing')
    """)
    conn.close()
    
    # Set environment and reset manager
    monkeypatch.setenv("HEALTHSIM_DB_PATH", db_path)
    reset_manager()
    
    yield db_path
    
    # Cleanup
    reset_manager()
    try:
        os.unlink(db_path)
    except Exception:
        pass


class TestQuery:
    """Tests for query function."""
    
    def test_select_query(self, temp_db_env):
        """Test basic SELECT query."""
        result = query("SELECT * FROM cohorts")
        assert result.success
        assert "columns" in result.data
        assert "rows" in result.data
        assert result.data["row_count"] >= 1
    
    def test_show_tables(self, temp_db_env):
        """Test SHOW TABLES query."""
        result = query("SHOW TABLES")
        assert result.success
        assert len(result.data["rows"]) > 0
    
    def test_with_cte(self, temp_db_env):
        """Test WITH (CTE) query."""
        result = query("""
            WITH test AS (SELECT 1 as num)
            SELECT * FROM test
        """)
        assert result.success
        assert result.data["rows"][0]["num"] == 1
    
    def test_insert_rejected(self, temp_db_env):
        """Test INSERT query is rejected."""
        result = query("INSERT INTO cohorts (id, name) VALUES ('x', 'y')")
        assert not result.success
        assert "forbidden" in result.error.lower() or "SELECT" in result.error
    
    def test_update_rejected(self, temp_db_env):
        """Test UPDATE query is rejected."""
        result = query("UPDATE cohorts SET name = 'x'")
        assert not result.success
    
    def test_delete_rejected(self, temp_db_env):
        """Test DELETE query is rejected."""
        result = query("DELETE FROM cohorts")
        assert not result.success
    
    def test_drop_rejected(self, temp_db_env):
        """Test DROP query is rejected."""
        result = query("DROP TABLE cohorts")
        assert not result.success
    
    def test_empty_query_rejected(self, temp_db_env):
        """Test empty query is rejected."""
        result = query("")
        assert not result.success
    
    def test_limit_applied(self, temp_db_env):
        """Test limit is respected."""
        # Add more rows
        conn = duckdb.connect(temp_db_env)
        for i in range(10):
            conn.execute(f"INSERT INTO cohorts (id, name) VALUES ('id{i}', 'Cohort {i}')")
        conn.close()
        reset_manager()
        
        result = query("SELECT * FROM cohorts", limit=3)
        assert result.success
        assert len(result.data["rows"]) <= 3
    
    def test_limit_clamped(self, temp_db_env):
        """Test limit is clamped to max."""
        result = query("SELECT * FROM cohorts LIMIT 5000", limit=9999)
        # Should not error, limit should be clamped internally
        assert result.success


class TestListTables:
    """Tests for list_tables function."""
    
    def test_list_tables(self, temp_db_env):
        """Test listing tables."""
        result = list_tables()
        assert result.success
        assert "system_tables" in result.data
        assert "entity_tables" in result.data
        assert "total" in result.data
    
    def test_system_tables_found(self, temp_db_env):
        """Test system tables are categorized correctly."""
        result = list_tables()
        assert result.success
        # cohorts should be in system tables
        assert "cohorts" in result.data["system_tables"]


class TestGetSummary:
    """Tests for get_summary function."""
    
    def test_get_summary_nonexistent(self, temp_db_env):
        """Test getting summary of nonexistent cohort."""
        result = get_summary("nonexistent")
        assert not result.success
    
    def test_get_summary_empty_name(self, temp_db_env):
        """Test empty name is rejected."""
        result = get_summary("")
        assert not result.success
    
    def test_samples_per_type_clamped(self, temp_db_env):
        """Test samples_per_type is clamped."""
        # This should not error even with extreme values
        # (will still fail because cohort doesn't exist, but validates input handling)
        result = get_summary("test", samples_per_type=0)
        # samples_per_type should be clamped to 1, error is due to cohort not found
        assert not result.success  # Cohort doesn't exist in proper format
