"""Tests for healthsim_agent.tools.connection module."""

import pytest
from pathlib import Path
import tempfile
import os

import duckdb

from healthsim_agent.tools.connection import (
    ConnectionManager,
    get_manager,
    reset_manager,
    get_db_path,
    DEFAULT_DB_PATH,
)


class TestConnectionManagerUnit:
    """Unit tests for ConnectionManager (no actual DB required)."""
    
    def test_init_with_default_path(self):
        """Test initialization with default path."""
        manager = ConnectionManager()
        assert manager.db_path is not None
        assert isinstance(manager.db_path, Path)
    
    def test_init_with_custom_path(self):
        """Test initialization with custom path."""
        custom_path = Path("/tmp/test.duckdb")
        manager = ConnectionManager(db_path=custom_path)
        assert manager.db_path == custom_path
    
    def test_initial_state(self):
        """Test initial state has no connections."""
        manager = ConnectionManager()
        assert manager._read_conn is None
        assert manager._read_manager is None


class TestConnectionManagerWithTempDB:
    """Integration tests using a temporary database."""
    
    @pytest.fixture
    def temp_db(self):
        """Create a temporary DuckDB database."""
        # Create temp file path but delete the empty file first
        with tempfile.NamedTemporaryFile(suffix=".duckdb", delete=False) as f:
            db_path = Path(f.name)
        os.unlink(db_path)  # Delete empty file so DuckDB can create fresh
        
        # Initialize with minimal schema
        conn = duckdb.connect(str(db_path))
        conn.execute("""
            CREATE TABLE IF NOT EXISTS cohorts (
                id VARCHAR PRIMARY KEY,
                name VARCHAR NOT NULL,
                description VARCHAR,
                created_at TIMESTAMP,
                updated_at TIMESTAMP
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
                entity_data VARCHAR,
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
        conn.close()
        
        yield db_path
        
        # Cleanup
        try:
            os.unlink(db_path)
        except Exception:
            pass
    
    def test_get_read_connection(self, temp_db):
        """Test getting a read connection."""
        manager = ConnectionManager(db_path=temp_db)
        try:
            conn = manager.get_read_connection()
            assert conn is not None
            
            # Verify it's read-only by checking we can query
            result = conn.execute("SELECT 1").fetchone()
            assert result == (1,)
        finally:
            manager.close()
    
    def test_read_connection_reused(self, temp_db):
        """Test that read connection is reused."""
        manager = ConnectionManager(db_path=temp_db)
        try:
            conn1 = manager.get_read_connection()
            conn2 = manager.get_read_connection()
            assert conn1 is conn2  # Same object
        finally:
            manager.close()
    
    def test_write_connection(self, temp_db):
        """Test write connection context manager."""
        manager = ConnectionManager(db_path=temp_db)
        try:
            # First get a read connection
            read_conn = manager.get_read_connection()
            assert read_conn is not None
            
            # Write operation should work
            with manager.write_connection() as conn:
                conn.execute("""
                    INSERT INTO cohorts (id, name, created_at, updated_at)
                    VALUES ('test1', 'Test Cohort', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                """)
            
            # Read connection should be invalidated during write
            # After write completes, should be able to read again
            new_read_conn = manager.get_read_connection()
            result = new_read_conn.execute(
                "SELECT name FROM cohorts WHERE id = 'test1'"
            ).fetchone()
            assert result == ("Test Cohort",)
        finally:
            manager.close()
    
    def test_write_closes_read(self, temp_db):
        """Test that write operation closes read connection."""
        manager = ConnectionManager(db_path=temp_db)
        try:
            # Get read connection
            manager.get_read_connection()
            assert manager._read_conn is not None
            
            # Write should close it
            with manager.write_connection() as conn:
                assert manager._read_conn is None
            
            # After write, _read_conn is still None until next read
            assert manager._read_conn is None
        finally:
            manager.close()
    
    def test_close(self, temp_db):
        """Test close method."""
        manager = ConnectionManager(db_path=temp_db)
        manager.get_read_connection()
        assert manager._read_conn is not None
        
        manager.close()
        assert manager._read_conn is None
        assert manager._read_manager is None


class TestGlobalManager:
    """Tests for global manager functions."""
    
    def test_get_manager_singleton(self):
        """Test get_manager returns singleton."""
        reset_manager()  # Clear any existing
        
        try:
            manager1 = get_manager()
            manager2 = get_manager()
            assert manager1 is manager2
        finally:
            reset_manager()
    
    def test_reset_manager(self):
        """Test reset_manager clears singleton."""
        manager1 = get_manager()
        reset_manager()
        manager2 = get_manager()
        assert manager1 is not manager2
        reset_manager()
    
    def test_get_db_path(self):
        """Test get_db_path returns Path."""
        path = get_db_path()
        assert isinstance(path, Path)
    
    def test_default_db_path_is_path(self):
        """Test DEFAULT_DB_PATH is a Path."""
        assert isinstance(DEFAULT_DB_PATH, Path)
    
    def test_env_override(self, monkeypatch):
        """Test environment variable override."""
        test_path = "/tmp/override.duckdb"
        monkeypatch.setenv("HEALTHSIM_DB_PATH", test_path)
        
        path = get_db_path()
        assert str(path) == test_path
