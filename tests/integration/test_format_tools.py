"""Integration tests for HealthSim Agent core functionality.

These tests verify database connectivity and basic tool operations.
Format transformation tests are in unit tests with proper mocking.

Note: Write connection tests may fail if the HealthSim agent/MCP server
is running, as DuckDB only allows one write connection at a time.
"""

import pytest
import json
import uuid
import duckdb

from healthsim_agent.tools.connection import get_manager
from healthsim_agent.tools.format_tools import list_output_formats
from healthsim_agent.tools.base import ok, err


def db_write_available():
    """Check if database write connection is available."""
    try:
        manager = get_manager()
        with manager.write_connection() as conn:
            conn.execute("SELECT 1")
        return True
    except duckdb.IOException:
        return False


# Skip write tests if another process holds the DB lock
skip_if_db_locked = pytest.mark.skipif(
    not db_write_available(),
    reason="Database write lock held by another process (agent/MCP server running)"
)


class TestDatabaseConnection:
    """Test database connectivity."""
    
    def test_read_connection(self):
        """Should establish read connection."""
        manager = get_manager()
        conn = manager.get_read_connection()
        
        assert conn is not None
        
        # Should be able to query
        result = conn.execute("SELECT 1 as test").fetchone()
        assert result[0] == 1
    
    @skip_if_db_locked
    def test_write_connection(self):
        """Should establish write connection via context manager."""
        manager = get_manager()
        
        with manager.write_connection() as conn:
            # Should be able to create temp table
            conn.execute("CREATE TEMP TABLE test_write (id INTEGER)")
            conn.execute("INSERT INTO test_write VALUES (42)")
            result = conn.execute("SELECT * FROM test_write").fetchone()
            assert result[0] == 42


class TestCohortOperations:
    """Test cohort creation and querying."""
    
    @skip_if_db_locked
    def test_create_and_query_cohort(self):
        """Should create and query a cohort."""
        manager = get_manager()
        cohort_id = f"test-{uuid.uuid4().hex[:8]}"
        
        try:
            with manager.write_connection() as conn:
                conn.execute(
                    "INSERT INTO cohorts (id, name, description) VALUES (?, ?, ?)",
                    [cohort_id, f"Test {cohort_id}", "Integration test"]
                )
            
            # Query it back
            conn = manager.get_read_connection()
            result = conn.execute(
                "SELECT id, name FROM cohorts WHERE id = ?", [cohort_id]
            ).fetchone()
            
            assert result is not None
            assert result[0] == cohort_id
            
        finally:
            # Cleanup
            with manager.write_connection() as conn:
                conn.execute("DELETE FROM cohorts WHERE id = ?", [cohort_id])


class TestFormatListing:
    """Test format listing functionality."""
    
    def test_list_output_formats(self):
        """Should list all output formats."""
        result = list_output_formats()
        
        assert result.success is True
        assert len(result.data) == 12  # 12 formats total
        
        # Verify all formats present
        formats = result.data
        assert "fhir_r4" in formats
        assert "ccda" in formats
        assert "hl7v2" in formats
        # X12 is split by transaction type
        assert "x12_837" in formats
        assert "x12_835" in formats
        assert "x12_834" in formats
        assert "x12_270" in formats
        assert "x12_271" in formats
        assert "ncpdp_d0" in formats
        assert "mimic_iii" in formats
        # CDISC formats
        assert "cdisc_sdtm" in formats
        assert "cdisc_adam" in formats
    
    def test_format_metadata_complete(self):
        """Each format should have complete metadata."""
        result = list_output_formats()
        
        for fmt_name, fmt_info in result.data.items():
            assert "name" in fmt_info, f"{fmt_name} missing name"
            assert "description" in fmt_info, f"{fmt_name} missing description"
            assert "entity_types" in fmt_info, f"{fmt_name} missing entity_types"
            assert "output" in fmt_info, f"{fmt_name} missing output"
            assert "tool" in fmt_info, f"{fmt_name} missing tool"


class TestToolResultHelpers:
    """Test tool result helper functions."""
    
    def test_ok_result(self):
        """ok() should create successful result."""
        result = ok(data={"test": 123}, message="Success")
        
        assert result.success is True
        assert result.data == {"test": 123}
        assert result.error is None
    
    def test_err_result(self):
        """err() should create error result."""
        result = err("Something went wrong")
        
        assert result.success is False
        assert result.data is None
        assert result.error == "Something went wrong"
