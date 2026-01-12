"""Extended tests for db/connection module."""

import pytest


class TestDatabaseConnection:
    """Tests for DatabaseConnection class."""
    
    def test_database_connection_class(self):
        """Test DatabaseConnection can be imported."""
        from healthsim_agent.db.connection import DatabaseConnection
        
        assert DatabaseConnection is not None
    
    def test_database_connection_methods(self):
        """Test DatabaseConnection has expected methods."""
        from healthsim_agent.db.connection import DatabaseConnection
        
        assert hasattr(DatabaseConnection, 'connect')
        assert hasattr(DatabaseConnection, 'close')
        assert hasattr(DatabaseConnection, 'execute_query')
        assert hasattr(DatabaseConnection, 'execute_raw')
        assert hasattr(DatabaseConnection, 'list_tables')
        assert hasattr(DatabaseConnection, 'table_exists')
        assert hasattr(DatabaseConnection, 'is_connected')


class TestQueryResult:
    """Tests for QueryResult class."""
    
    def test_query_result_class(self):
        """Test QueryResult can be imported."""
        from healthsim_agent.db.connection import QueryResult
        
        assert QueryResult is not None


class TestSchemaOperations:
    """Tests for schema operations."""
    
    def test_schema_functions(self):
        """Test schema module functions."""
        from healthsim_agent.db import schema
        
        # Check module is importable
        assert schema is not None


class TestQueriesModule:
    """Tests for queries module."""
    
    def test_queries_module(self):
        """Test queries module is importable."""
        from healthsim_agent.db import queries
        
        assert queries is not None
