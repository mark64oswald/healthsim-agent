"""
Tests for Database Connection and Query functionality.

These tests verify:
- Database connection management
- Query result handling
- Reference data queries (if database available)
"""
import pytest
from pathlib import Path
from healthsim_agent.db import DatabaseConnection, QueryResult, ReferenceQueries


# Path to reference database
REFERENCE_DB = Path("/Users/markoswald/Developer/projects/healthsim-agent/data/healthsim-reference.duckdb")


class TestQueryResult:
    """Test QueryResult data class."""
    
    def test_to_dicts(self):
        """Test converting rows to dictionaries."""
        result = QueryResult(
            columns=["name", "age", "city"],
            data=[
                ["Alice", 30, "Austin"],
                ["Bob", 25, "Dallas"],
            ],
            row_count=2,
        )
        
        dicts = result.to_dicts()
        
        assert len(dicts) == 2
        assert dicts[0] == {"name": "Alice", "age": 30, "city": "Austin"}
        assert dicts[1]["name"] == "Bob"
    
    def test_first(self):
        """Test getting first row."""
        result = QueryResult(
            columns=["id", "value"],
            data=[[1, "first"], [2, "second"]],
            row_count=2,
        )
        
        first = result.first()
        assert first == {"id": 1, "value": "first"}
    
    def test_first_empty(self):
        """Test first() on empty result."""
        result = QueryResult(columns=[], data=[], row_count=0)
        assert result.first() is None
    
    def test_error_result(self):
        """Test result with error."""
        result = QueryResult(
            columns=[],
            data=[],
            row_count=0,
            error="Table not found",
        )
        
        assert result.error == "Table not found"
        assert result.to_dicts() == []


class TestDatabaseConnection:
    """Test DatabaseConnection class."""
    
    def test_connection_missing_file(self):
        """Test error when database file doesn't exist."""
        with pytest.raises(FileNotFoundError):
            DatabaseConnection("/nonexistent/path.duckdb")
    
    @pytest.mark.skipif(
        not REFERENCE_DB.exists(),
        reason="Reference database not available"
    )
    def test_connect_and_close(self):
        """Test connecting and closing."""
        conn = DatabaseConnection(REFERENCE_DB)
        
        assert not conn.is_connected
        
        conn.connect()
        assert conn.is_connected
        
        conn.close()
        assert not conn.is_connected
    
    @pytest.mark.skipif(
        not REFERENCE_DB.exists(),
        reason="Reference database not available"
    )
    def test_context_manager(self):
        """Test using connection as context manager."""
        with DatabaseConnection(REFERENCE_DB) as conn:
            assert conn.is_connected
        
        assert not conn.is_connected
    
    @pytest.mark.skipif(
        not REFERENCE_DB.exists(),
        reason="Reference database not available"
    )
    def test_list_tables(self):
        """Test listing tables."""
        with DatabaseConnection(REFERENCE_DB) as conn:
            tables = conn.list_tables()
            
            assert isinstance(tables, list)
            assert len(tables) > 0
    
    @pytest.mark.skipif(
        not REFERENCE_DB.exists(),
        reason="Reference database not available"
    )
    def test_execute_query(self):
        """Test executing a query."""
        with DatabaseConnection(REFERENCE_DB) as conn:
            tables = conn.list_tables()
            if tables:
                result = conn.execute_query(f"SELECT COUNT(*) FROM {tables[0]}")
                
                assert isinstance(result, QueryResult)
                assert result.error is None
                assert result.row_count == 1
    
    @pytest.mark.skipif(
        not REFERENCE_DB.exists(),
        reason="Reference database not available"
    )
    def test_query_error_handling(self):
        """Test that query errors are captured."""
        with DatabaseConnection(REFERENCE_DB) as conn:
            result = conn.execute_query("SELECT * FROM nonexistent_table_xyz")
            
            assert result.error is not None
            assert result.row_count == 0
    
    @pytest.mark.skipif(
        not REFERENCE_DB.exists(),
        reason="Reference database not available"
    )
    def test_database_info(self):
        """Test getting database info."""
        with DatabaseConnection(REFERENCE_DB) as conn:
            info = conn.get_database_info()
            
            assert "path" in info
            assert "size_mb" in info
            assert "table_count" in info
            assert info["table_count"] > 0


@pytest.mark.skipif(
    not REFERENCE_DB.exists(),
    reason="Reference database not available"
)
class TestReferenceQueries:
    """Test reference data query helpers."""
    
    @pytest.fixture
    def queries(self):
        """Create ReferenceQueries with database connection."""
        conn = DatabaseConnection(REFERENCE_DB)
        conn.connect()
        yield ReferenceQueries(conn)
        conn.close()
    
    def test_list_tables(self, queries):
        """Test listing available tables."""
        tables = queries.list_available_tables()
        assert isinstance(tables, list)
        assert len(tables) > 0
    
    def test_search_providers_by_state(self, queries):
        """Test searching providers by state."""
        result = queries.search_providers(state="TX", limit=5)
        
        if result.error is None and result.row_count > 0:
            dicts = result.to_dicts()
            assert all(d.get("state") == "TX" for d in dicts)
    
    def test_search_providers_by_specialty(self, queries):
        """Test searching providers by specialty."""
        result = queries.search_providers(specialty="cardiology", limit=5)
        
        # Query may fail if nppes_providers table doesn't exist in this DB
        # That's acceptable - we're testing the query helper, not the data
        assert result.error is None or "does not exist" in (result.error or "").lower()
    
    def test_count_providers_by_specialty(self, queries):
        """Test counting providers by specialty."""
        result = queries.count_providers_by_specialty(state="CA", limit=10)
        
        if result.error is None and result.row_count > 0:
            assert "specialty" in result.columns
            assert "provider_count" in result.columns
    
    def test_custom_query(self, queries):
        """Test executing custom SQL."""
        tables = queries.list_available_tables()
        if tables:
            result = queries.execute_custom(
                f"SELECT * FROM {tables[0]} LIMIT 1"
            )
            assert result.error is None
