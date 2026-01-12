"""Tests for db/reference/loader module."""

import pytest


class TestReferenceStatus:
    """Tests for reference data status functions."""
    
    def test_is_reference_data_loaded_with_conn(self):
        """Test checking if reference data is loaded with connection."""
        from healthsim_agent.db.reference.loader import is_reference_data_loaded
        import duckdb
        
        conn = duckdb.connect(":memory:")
        result = is_reference_data_loaded(conn)
        assert isinstance(result, bool)
        conn.close()
    
    def test_get_reference_status_with_conn(self):
        """Test getting reference status with connection."""
        from healthsim_agent.db.reference.loader import get_reference_status
        import duckdb
        
        conn = duckdb.connect(":memory:")
        status = get_reference_status(conn)
        assert status is not None
        conn.close()
    
    def test_reference_tables_constant(self):
        """Test REFERENCE_TABLES constant exists."""
        from healthsim_agent.db.reference.loader import REFERENCE_TABLES
        
        assert REFERENCE_TABLES is not None
        assert isinstance(REFERENCE_TABLES, (list, tuple, dict))


class TestPopulationsimData:
    """Tests for populationsim reference data functions."""
    
    def test_get_default_data_path(self):
        """Test getting default data path."""
        from healthsim_agent.db.reference.populationsim import get_default_data_path
        
        path = get_default_data_path()
        assert path is not None
