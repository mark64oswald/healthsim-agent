"""Connection management for HealthSim Agent tools.

Implements the close-before-write pattern required by DuckDB:
- Persistent read-only connection for queries (shared lock, fast repeated reads)
- Write operations close read connection first, then open read-write connection
- Read connection reopens lazily after writes complete

This pattern is required because DuckDB does not allow simultaneous connections
with different read_only configurations to the same database file, even within
the same process.
"""

import atexit
import os
import signal
import sys
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Optional, Generator

import duckdb

# Note: StateManager is in-memory only, not used for DB tools
# from healthsim_agent.state import StateManager


# =============================================================================
# Configuration
# =============================================================================

# Default database path - can be overridden by environment variable
DEFAULT_DB_PATH = Path(
    os.environ.get(
        "HEALTHSIM_DB_PATH",
        "/Users/markoswald/Developer/projects/healthsim-workspace/healthsim.duckdb"
    )
)


def get_db_path() -> Path:
    """Get the database path from environment or default.
    
    Returns:
        Path to the DuckDB database file
    """
    return Path(os.environ.get("HEALTHSIM_DB_PATH", str(DEFAULT_DB_PATH)))


# =============================================================================
# Connection Manager
# =============================================================================

class ConnectionManager:
    """Manages DuckDB connections using close-before-write pattern.
    
    DuckDB Constraint: Cannot have simultaneous connections with different
    read_only configurations to the same database file, even in the same process.
    
    Solution:
    - Read operations: Use persistent read-only connection (shared lock)
    - Write operations: Close read connection first, open read-write connection,
      perform write, close write connection. Read connection reopens lazily.
    
    This allows:
    - Fast repeated reads (connection reuse)
    - Reliable writes (no configuration conflicts)
    - External process access during reads (shared lock)
    
    Example:
        >>> manager = ConnectionManager()
        >>> conn = manager.get_read_connection()
        >>> result = conn.execute("SELECT * FROM cohorts").fetchall()
        >>> 
        >>> with manager.write_connection() as conn:
        ...     conn.execute("INSERT INTO ...")
    """
    
    def __init__(self, db_path: Optional[Path] = None):
        """Initialize the connection manager.
        
        Args:
            db_path: Path to the DuckDB database file.
                     Defaults to HEALTHSIM_DB_PATH env var or built-in default.
        """
        self.db_path = db_path or get_db_path()
        self._read_conn: Optional[duckdb.DuckDBPyConnection] = None
        self._read_manager: Optional[StateManager] = None
    
    def get_read_connection(self) -> duckdb.DuckDBPyConnection:
        """Get persistent read-only connection.
        
        Uses shared lock - allows concurrent readers from other processes.
        Connection is reused across all read operations.
        Will be automatically reopened after write operations.
        
        Includes retry logic in case a previous write lock hasn't fully released.
        
        Returns:
            DuckDB connection in read-only mode
            
        Raises:
            Exception: If connection cannot be established after retries
        """
        if self._read_conn is None:
            max_retries = 3
            retry_delay = 0.1  # 100ms between retries
            
            for attempt in range(max_retries):
                try:
                    self._read_conn = duckdb.connect(
                        str(self.db_path), 
                        read_only=True
                    )
                    break
                except Exception as e:
                    if attempt < max_retries - 1 and "lock" in str(e).lower():
                        time.sleep(retry_delay)
                        retry_delay *= 2  # Exponential backoff
                    else:
                        raise
        
        return self._read_conn
    
    # Note: get_read_manager removed - StateManager is in-memory only
    # Use get_read_connection() directly for DB queries
    
    def _close_read_connection(self) -> None:
        """Close the read connection.
        
        Called before write operations to avoid DuckDB configuration conflicts.
        The read connection will be lazily reopened on the next read operation.
        """
        if self._read_conn is not None:
            self._read_conn.close()
            self._read_conn = None
            self._read_manager = None
    
    @contextmanager
    def write_connection(self) -> Generator[duckdb.DuckDBPyConnection, None, None]:
        """Context manager for write operations.
        
        IMPORTANT: Closes read connection first to avoid DuckDB's constraint
        against mixing read_only=True and read_only=False connections to the
        same database file.
        
        The read connection will be lazily reopened on the next read operation.
        
        Yields:
            DuckDB connection in read-write mode
            
        Example:
            >>> with manager.write_connection() as conn:
            ...     conn.execute("INSERT INTO cohorts VALUES (...)")
        """
        # Close read connection first - DuckDB doesn't allow mixed configurations
        self._close_read_connection()
        
        # Small delay to ensure read connection is fully released
        time.sleep(0.05)
        
        conn = duckdb.connect(str(self.db_path))  # read_only=False (default)
        try:
            yield conn
        finally:
            # Explicit checkpoint to ensure all changes are flushed to disk
            # This helps prevent lock issues when reopening read connection
            try:
                conn.execute("CHECKPOINT")
            except Exception:
                pass  # Checkpoint is best-effort
            
            conn.close()
            # Small delay to ensure write lock is fully released
            time.sleep(0.05)
    
    # Note: write_manager removed - StateManager is in-memory only
    # Use write_connection() directly for DB operations
    
    def close(self) -> None:
        """Close all connections.
        
        Should be called during shutdown to release database locks.
        """
        if self._read_conn:
            self._read_conn.close()
            self._read_conn = None
            self._read_manager = None


# =============================================================================
# Global Connection Manager Singleton
# =============================================================================

_manager: Optional[ConnectionManager] = None


def get_manager() -> ConnectionManager:
    """Get or create the global connection manager.
    
    Returns:
        The singleton ConnectionManager instance
    """
    global _manager
    if _manager is None:
        _manager = ConnectionManager()
    return _manager


def reset_manager() -> None:
    """Reset the global connection manager.
    
    Useful for testing or when database path changes.
    """
    global _manager
    if _manager is not None:
        _manager.close()
        _manager = None


def _cleanup_connections() -> None:
    """Clean up database connections on shutdown."""
    global _manager
    if _manager is not None:
        _manager.close()
        _manager = None


def _signal_handler(signum: int, frame) -> None:
    """Handle termination signals gracefully."""
    _cleanup_connections()
    sys.exit(0)


# Register cleanup handlers
atexit.register(_cleanup_connections)
signal.signal(signal.SIGTERM, _signal_handler)
signal.signal(signal.SIGINT, _signal_handler)
