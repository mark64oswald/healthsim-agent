"""
HealthSim Agent - Database Connection

DuckDB connection management for reference data queries.
"""
from pathlib import Path
from typing import Any

import duckdb


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
    
    def execute_query(
        self,
        query: str,
        params: dict[str, Any] | None = None,
        limit: int = 100,
    ) -> dict[str, Any]:
        """
        Execute a query and return results.
        
        Returns dict with:
        - columns: list of column names
        - data: list of row tuples
        - row_count: number of rows returned
        """
        if not self.is_connected:
            self.connect()
        
        try:
            if params:
                result = self._conn.execute(query, params)
            else:
                result = self._conn.execute(query)
            
            columns = [desc[0] for desc in result.description]
            data = result.fetchmany(limit)
            
            return {
                "columns": columns,
                "data": [list(row) for row in data],
                "row_count": len(data),
            }
        except Exception as e:
            return {
                "error": str(e),
                "columns": [],
                "data": [],
                "row_count": 0,
            }
    
    def get_table_info(self, table_name: str) -> dict[str, Any]:
        """Get information about a table."""
        query = f"DESCRIBE {table_name}"
        return self.execute_query(query)
    
    def list_tables(self) -> list[str]:
        """List all tables in the database."""
        result = self.execute_query("SHOW TABLES")
        if "error" in result:
            return []
        return [row[0] for row in result["data"]]
    
    def count_rows(self, table_name: str) -> int:
        """Get row count for a table."""
        result = self.execute_query(f"SELECT COUNT(*) FROM {table_name}")
        if result["data"]:
            return result["data"][0][0]
        return 0
    
    # Convenience methods for common reference queries
    
    def query_providers(
        self,
        specialty: str | None = None,
        state: str | None = None,
        city: str | None = None,
        limit: int = 10,
    ) -> dict[str, Any]:
        """Query NPPES provider data."""
        conditions = []
        if specialty:
            conditions.append(f"primary_taxonomy_desc ILIKE '%{specialty}%'")
        if state:
            conditions.append(f"state = '{state.upper()}'")
        if city:
            conditions.append(f"city ILIKE '%{city}%'")
        
        where = " AND ".join(conditions) if conditions else "1=1"
        
        query = f"""
        SELECT npi, provider_name, primary_taxonomy_desc, 
               address, city, state, zip
        FROM nppes_providers
        WHERE {where}
        LIMIT {limit}
        """
        return self.execute_query(query)
    
    def query_demographics(
        self,
        state: str | None = None,
        county: str | None = None,
        limit: int = 10,
    ) -> dict[str, Any]:
        """Query demographic/SDOH data."""
        conditions = []
        if state:
            conditions.append(f"state_abbr = '{state.upper()}'")
        if county:
            conditions.append(f"county_name ILIKE '%{county}%'")
        
        where = " AND ".join(conditions) if conditions else "1=1"
        
        query = f"""
        SELECT state_abbr, county_name, population,
               median_income, poverty_rate
        FROM demographic_reference
        WHERE {where}
        LIMIT {limit}
        """
        return self.execute_query(query)
    
    def query_health_indicators(
        self,
        state: str | None = None,
        measure: str | None = None,
        limit: int = 10,
    ) -> dict[str, Any]:
        """Query CDC PLACES health indicators."""
        conditions = []
        if state:
            conditions.append(f"state_abbr = '{state.upper()}'")
        if measure:
            conditions.append(f"measure ILIKE '%{measure}%'")
        
        where = " AND ".join(conditions) if conditions else "1=1"
        
        query = f"""
        SELECT state_abbr, county_name, measure, 
               data_value, data_value_type
        FROM cdc_places
        WHERE {where}
        LIMIT {limit}
        """
        return self.execute_query(query)
    
    def __enter__(self) -> "DatabaseConnection":
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        self.close()
