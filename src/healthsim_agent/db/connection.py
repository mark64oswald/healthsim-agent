"""
HealthSim Agent - Database Connection

DuckDB connection management for reference data queries.

The agent uses two types of database access:
1. Reference Database (read-only): NPPES, CDC PLACES, Census data
2. Session Database (read-write): Generated data during session

This module handles the reference database connection.
"""

from pathlib import Path
from typing import Any

import duckdb

from healthsim_agent.db.queries import QueryResult


class DatabaseConnection:
    """
    Manages DuckDB connection for HealthSim reference data.
    
    The reference database contains:
    - NPPES provider data (~8.9M providers)
    - CDC PLACES health indicators
    - Social Vulnerability Index data
    - Area Deprivation Index data
    - Geographic reference data
    
    Uses read-only access for reference queries.
    """
    
    def __init__(self, db_path: Path | str):
        """
        Initialize database connection.
        
        Args:
            db_path: Path to DuckDB database file
            
        Raises:
            FileNotFoundError: If database file doesn't exist
        """
        self.db_path = Path(db_path)
        self._conn: duckdb.DuckDBPyConnection | None = None
        
        if not self.db_path.exists():
            raise FileNotFoundError(f"Database not found: {self.db_path}")
    
    def connect(self) -> None:
        """Establish database connection."""
        if self._conn is not None:
            return
        
        self._conn = duckdb.connect(str(self.db_path), read_only=True)
    
    def close(self) -> None:
        """Close database connection."""
        if self._conn is not None:
            self._conn.close()
            self._conn = None
    
    @property
    def is_connected(self) -> bool:
        """Check if connection is active."""
        return self._conn is not None
    
    def _ensure_connected(self) -> None:
        """Ensure connection is established."""
        if not self.is_connected:
            self.connect()
    
    def execute_query(
        self,
        query: str,
        params: dict[str, Any] | None = None,
        limit: int = 100,
    ) -> QueryResult:
        """
        Execute a query and return results as QueryResult.
        
        Args:
            query: SQL query string
            params: Optional query parameters
            limit: Maximum rows to return
            
        Returns:
            QueryResult with columns, data, row_count, and optional error
        """
        self._ensure_connected()
        
        try:
            if params:
                result = self._conn.execute(query, params)
            else:
                result = self._conn.execute(query)
            
            columns = [desc[0] for desc in result.description] if result.description else []
            data = result.fetchmany(limit)
            
            return QueryResult(
                columns=columns,
                data=[list(row) for row in data],
                row_count=len(data),
                error=None,
            )
        except Exception as e:
            return QueryResult(
                columns=[],
                data=[],
                row_count=0,
                error=str(e),
            )
    
    def execute_raw(
        self,
        query: str,
        params: dict[str, Any] | None = None,
    ) -> list[tuple]:
        """
        Execute a query and return raw results.
        
        Args:
            query: SQL query string
            params: Optional query parameters
            
        Returns:
            List of row tuples
        """
        self._ensure_connected()
        
        if params:
            return self._conn.execute(query, params).fetchall()
        return self._conn.execute(query).fetchall()
    
    def get_table_info(self, table_name: str) -> QueryResult:
        """
        Get information about a table's columns.
        
        Args:
            table_name: Name of the table
            
        Returns:
            QueryResult with column definitions
        """
        query = f"DESCRIBE {table_name}"
        return self.execute_query(query)
    
    def list_tables(self) -> list[str]:
        """
        List all tables in the database.
        
        Returns:
            List of table names
        """
        self._ensure_connected()
        
        result = self._conn.execute("SHOW TABLES").fetchall()
        return [row[0] for row in result]
    
    def count_rows(self, table_name: str) -> int:
        """
        Get row count for a table.
        
        Args:
            table_name: Name of the table
            
        Returns:
            Number of rows
        """
        result = self.execute_query(f"SELECT COUNT(*) FROM {table_name}")
        if result.data:
            return result.data[0][0]
        return 0
    
    def table_exists(self, table_name: str) -> bool:
        """
        Check if a table exists.
        
        Args:
            table_name: Name of the table
            
        Returns:
            True if table exists
        """
        return table_name.lower() in [t.lower() for t in self.list_tables()]
    
    def get_database_info(self) -> dict[str, Any]:
        """
        Get summary information about the database.
        
        Returns:
            Dict with database metadata
        """
        tables = self.list_tables()
        
        info = {
            "path": str(self.db_path),
            "size_mb": self.db_path.stat().st_size / (1024 * 1024),
            "table_count": len(tables),
            "tables": {},
        }
        
        for table in tables[:20]:  # Limit to first 20 tables
            try:
                count = self.count_rows(table)
                info["tables"][table] = count
            except Exception:
                info["tables"][table] = "error"
        
        return info
    
    def __enter__(self) -> "DatabaseConnection":
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        self.close()
    
    def __repr__(self) -> str:
        status = "connected" if self.is_connected else "disconnected"
        return f"DatabaseConnection({self.db_path}, {status})"
