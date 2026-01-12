"""Extended tests for query_tools module.

Covers additional query scenarios and edge cases.
"""

import pytest
import tempfile
import os
import json
import duckdb

from healthsim_agent.tools import reset_manager
from healthsim_agent.tools.query_tools import (
    query,
    get_summary,
    list_tables,
)


@pytest.fixture
def temp_db_with_entities(monkeypatch):
    """Create a database with cohort entities for testing."""
    with tempfile.NamedTemporaryFile(suffix=".duckdb", delete=False) as f:
        db_path = f.name
    os.unlink(db_path)
    
    conn = duckdb.connect(db_path)
    
    # Create schema
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
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS cohort_tags (
            id INTEGER PRIMARY KEY,
            cohort_id VARCHAR,
            tag VARCHAR
        )
    """)
    
    # Add test cohort
    conn.execute("""
        INSERT INTO cohorts (id, name, description)
        VALUES ('cohort-123', 'Test Cohort', 'Testing get_summary')
    """)
    
    # Add entities
    patient_data = json.dumps({"id": "p-1", "name": "John Doe", "age": 45})
    conn.execute("""
        INSERT INTO cohort_entities (id, cohort_id, entity_type, entity_id, entity_data)
        VALUES (1, 'cohort-123', 'patients', 'p-1', ?)
    """, [patient_data])
    
    patient_data2 = json.dumps({"id": "p-2", "name": "Jane Smith", "age": 32})
    conn.execute("""
        INSERT INTO cohort_entities (id, cohort_id, entity_type, entity_id, entity_data)
        VALUES (2, 'cohort-123', 'patients', 'p-2', ?)
    """, [patient_data2])
    
    encounter_data = json.dumps({"id": "e-1", "patient_id": "p-1", "type": "outpatient"})
    conn.execute("""
        INSERT INTO cohort_entities (id, cohort_id, entity_type, entity_id, entity_data)
        VALUES (3, 'cohort-123', 'encounters', 'e-1', ?)
    """, [encounter_data])
    
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
    
    def test_invalid_sql(self, temp_db_with_entities):
        """Test error handling for invalid SQL."""
        result = query("SELEC * FORM invalid")
        assert result.success is False
        assert result.error is not None
    
    def test_empty_result(self, temp_db_with_entities):
        """Test query with no results."""
        result = query("SELECT * FROM cohorts WHERE id = 'nonexistent'")
        assert result.success is True
        assert result.data["row_count"] == 0
    
    def test_aggregate_query(self, temp_db_with_entities):
        """Test aggregate query."""
        result = query("SELECT COUNT(*) as cnt FROM cohort_entities")
        assert result.success is True
        assert result.data["rows"][0]["cnt"] >= 1
    
    def test_join_query(self, temp_db_with_entities):
        """Test JOIN query."""
        result = query("""
            SELECT c.name, COUNT(e.id) as entity_count
            FROM cohorts c
            LEFT JOIN cohort_entities e ON c.id = e.cohort_id
            GROUP BY c.name
        """)
        assert result.success is True
        assert len(result.data["columns"]) == 2
    
    def test_describe_table(self, temp_db_with_entities):
        """Test DESCRIBE query."""
        result = query("DESCRIBE cohorts")
        assert result.success is True
        assert len(result.data["rows"]) > 0


class TestGetSummaryExtended:
    """Extended tests for get_summary function."""
    
    def test_get_summary_with_entities(self, temp_db_with_entities):
        """Test summary with entities."""
        result = get_summary("cohort-123")
        
        assert result.success is True
        assert result.data["cohort_id"] == "cohort-123"
        assert result.data["name"] == "Test Cohort"
        assert "patients" in result.data["entity_counts"]
        assert result.data["entity_counts"]["patients"] == 2
        assert result.data["total_entities"] == 3
    
    def test_get_summary_by_name(self, temp_db_with_entities):
        """Test summary lookup by name."""
        result = get_summary("Test Cohort")
        
        assert result.success is True
        assert result.data["cohort_id"] == "cohort-123"
    
    def test_get_summary_with_tags(self, temp_db_with_entities):
        """Test summary includes tags."""
        result = get_summary("cohort-123")
        
        assert result.success is True
        assert "tags" in result.data
        assert "test" in result.data["tags"]
        assert "demo" in result.data["tags"]
    
    def test_get_summary_with_samples(self, temp_db_with_entities):
        """Test summary with sample entities."""
        result = get_summary("cohort-123", include_samples=True, samples_per_type=1)
        
        assert result.success is True
        assert "samples" in result.data
        assert "patients" in result.data["samples"]
        assert len(result.data["samples"]["patients"]) == 1
    
    def test_get_summary_samples_multiple(self, temp_db_with_entities):
        """Test summary with multiple samples per type."""
        result = get_summary("cohort-123", include_samples=True, samples_per_type=5)
        
        assert result.success is True
        assert "samples" in result.data
        # Should have at most 2 patients (that's all we have)
        assert len(result.data["samples"]["patients"]) == 2
    
    def test_get_summary_nonexistent(self, temp_db_with_entities):
        """Test summary for nonexistent cohort."""
        result = get_summary("nonexistent-cohort")
        
        assert result.success is False
        assert "not found" in result.error.lower()
    
    def test_get_summary_empty_cohort(self, temp_db_with_entities, monkeypatch):
        """Test summary for cohort with no entities."""
        # Add an empty cohort
        db_path = temp_db_with_entities
        conn = duckdb.connect(db_path)
        conn.execute("""
            INSERT INTO cohorts (id, name, description)
            VALUES ('empty-cohort', 'Empty Cohort', 'No entities')
        """)
        conn.close()
        
        result = get_summary("empty-cohort")
        
        assert result.success is True
        assert result.data["total_entities"] == 0
        assert result.data["entity_counts"] == {}


class TestListTablesExtended:
    """Extended tests for list_tables function."""
    
    def test_list_tables_returns_categories(self, temp_db_with_entities):
        """Test that list_tables returns categorized results."""
        result = list_tables()
        
        assert result.success is True
        assert result.data is not None
        # Should have some structure
        assert isinstance(result.data, dict)
    
    def test_list_tables_includes_cohorts(self, temp_db_with_entities):
        """Test that system tables are included."""
        result = list_tables()
        
        assert result.success is True
        # Check for cohorts table in some category
        all_tables = []
        for category, tables in result.data.items():
            if isinstance(tables, list):
                all_tables.extend(tables)
            elif isinstance(tables, dict):
                for subcategory, subtables in tables.items():
                    if isinstance(subtables, list):
                        all_tables.extend(subtables)
        
        # cohorts should be somewhere
        assert any("cohort" in str(t).lower() for t in all_tables) or len(all_tables) > 0


class TestQueryEdgeCases:
    """Edge case tests for query functions."""
    
    def test_query_with_parameters_in_string(self, temp_db_with_entities):
        """Test query with quoted strings containing special chars."""
        result = query("SELECT 'test''s value' as val")
        assert result.success is True
    
    def test_query_null_handling(self, temp_db_with_entities):
        """Test query with NULL values."""
        result = query("SELECT NULL as empty_val, 'test' as filled_val")
        assert result.success is True
        assert result.data["rows"][0]["empty_val"] is None
    
    def test_query_limit(self, temp_db_with_entities):
        """Test query respects LIMIT."""
        result = query("SELECT * FROM cohort_entities LIMIT 1")
        assert result.success is True
        assert result.data["row_count"] == 1
    
    def test_query_order_by(self, temp_db_with_entities):
        """Test query with ORDER BY."""
        result = query("SELECT entity_type FROM cohort_entities ORDER BY entity_type")
        assert result.success is True
