"""DuckDB writer for dimensional model data.

Ported from: healthsim-workspace/packages/core/src/healthsim/dimensional/writers/duckdb_writer.py
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

import duckdb
import pandas as pd

from healthsim_agent.dimensional.writers.base import BaseDimensionalWriter

if TYPE_CHECKING:
    from healthsim_agent.config.dimensional import TargetConfig


class DuckDBDimensionalWriter(BaseDimensionalWriter):
    """Write dimensional model to DuckDB database."""

    TARGET_NAME = "duckdb"
    REQUIRED_PACKAGES = ["duckdb"]

    def __init__(
        self,
        db_path: str | Path = ":memory:",
        schema: str = "analytics",
        read_only: bool = False,
        **kwargs: Any,
    ) -> None:
        super().__init__(schema=schema, **kwargs)
        self.db_path = str(db_path)
        self.read_only = read_only
        self._connection: duckdb.DuckDBPyConnection | None = None
        self._schema_created = False

        if self.db_path != ":memory:":
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

    @classmethod
    def from_config(cls, config: TargetConfig) -> DuckDBDimensionalWriter:
        """Create from configuration object."""
        settings = config.settings
        return cls(
            db_path=settings.get("db_path", ":memory:"),
            schema=settings.get("schema", "analytics"),
            read_only=settings.get("read_only", False),
        )

    def _ensure_connection(self) -> duckdb.DuckDBPyConnection:
        """Ensure database connection is open and schema exists."""
        if self._connection is None:
            self._connection = duckdb.connect(self.db_path, read_only=self.read_only)

        if not self._schema_created and not self.read_only:
            self._connection.execute(f"CREATE SCHEMA IF NOT EXISTS {self.schema}")
            self._schema_created = True

        return self._connection

    def connect(self) -> None:
        """Establish connection to DuckDB."""
        self._ensure_connection()

    def close(self) -> None:
        """Close the database connection."""
        if self._connection is not None:
            self._connection.close()
            self._connection = None
            self._schema_created = False

    def write_table(
        self,
        table_name: str,
        df: pd.DataFrame,
        if_exists: str = "replace",
    ) -> int:
        """Write a single DataFrame to a table."""
        if if_exists not in ("replace", "append"):
            raise ValueError(f"if_exists must be 'replace' or 'append', got '{if_exists}'")

        conn = self._ensure_connection()
        full_table_name = f"{self.schema}.{table_name}"

        if if_exists == "replace":
            conn.execute(f"DROP TABLE IF EXISTS {full_table_name}")

        conn.register("_temp_df", df)

        if if_exists == "replace":
            conn.execute(f"CREATE TABLE {full_table_name} AS SELECT * FROM _temp_df")
        else:
            if self.table_exists(table_name):
                conn.execute(f"INSERT INTO {full_table_name} SELECT * FROM _temp_df")
            else:
                conn.execute(f"CREATE TABLE {full_table_name} AS SELECT * FROM _temp_df")

        conn.unregister("_temp_df")
        return len(df)

    def get_table_list(self) -> list[str]:
        """Get list of tables in the schema."""
        conn = self._ensure_connection()
        result = conn.execute(f"""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = '{self.schema}'
            ORDER BY table_name
        """).fetchall()
        return [row[0] for row in result]

    def get_table_stats(self) -> pd.DataFrame:
        """Get statistics for all tables in schema."""
        conn = self._ensure_connection()
        tables = self.get_table_list()

        stats = []
        for table_name in tables:
            full_name = f"{self.schema}.{table_name}"
            row_count = conn.execute(f"SELECT COUNT(*) FROM {full_name}").fetchone()[0]
            col_result = conn.execute(f"""
                SELECT COUNT(*) FROM information_schema.columns
                WHERE table_schema = '{self.schema}' AND table_name = '{table_name}'
            """).fetchone()
            col_count = col_result[0] if col_result else 0

            stats.append({
                "table_name": table_name,
                "row_count": row_count,
                "column_count": col_count,
            })

        return pd.DataFrame(stats)

    def query(self, sql: str) -> pd.DataFrame:
        """Execute SQL query and return results as DataFrame."""
        conn = self._ensure_connection()
        return conn.execute(sql).df()

    def table_exists(self, table_name: str) -> bool:
        """Check if a table exists in the schema."""
        conn = self._ensure_connection()
        result = conn.execute(f"""
            SELECT COUNT(*) as cnt FROM information_schema.tables
            WHERE table_schema = '{self.schema}' AND table_name = '{table_name}'
        """).fetchone()
        return result is not None and result[0] > 0

    @property
    def full_table_prefix(self) -> str:
        """Return fully qualified schema name."""
        return self.schema

    def drop_table(self, table_name: str) -> bool:
        """Drop a table if it exists."""
        if not self.table_exists(table_name):
            return False
        conn = self._ensure_connection()
        full_name = f"{self.schema}.{table_name}"
        conn.execute(f"DROP TABLE {full_name}")
        return True

    @property
    def full_schema_name(self) -> str:
        """Return fully qualified schema name (legacy)."""
        return self.schema


__all__ = ["DuckDBDimensionalWriter"]
