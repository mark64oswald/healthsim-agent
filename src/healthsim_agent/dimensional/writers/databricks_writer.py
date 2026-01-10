"""Databricks Dimensional Writer.

Ported from: healthsim-workspace/packages/core/src/healthsim/dimensional/writers/databricks_writer.py
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any

import pandas as pd

try:
    from databricks import sql as databricks_sql
    from databricks.sql.client import Connection
except ImportError:
    databricks_sql = None
    Connection = None

from healthsim_agent.dimensional.writers.base import BaseDimensionalWriter

if TYPE_CHECKING:
    from healthsim_agent.config.dimensional import TargetConfig


class DatabricksDimensionalWriter(BaseDimensionalWriter):
    """Write dimensional model to Databricks Unity Catalog."""

    TARGET_NAME = "databricks"
    REQUIRED_PACKAGES = ["databricks.sql"]

    def __init__(
        self,
        catalog: str = "healthsim",
        schema: str = "gold",
        host: str | None = None,
        http_path: str | None = None,
        access_token: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(schema=schema, **kwargs)
        self.catalog = catalog
        self.host = host or os.environ.get("DATABRICKS_HOST")
        self.http_path = http_path or os.environ.get("DATABRICKS_HTTP_PATH")
        self.access_token = access_token or os.environ.get("DATABRICKS_TOKEN")
        self._validate_config()
        self._conn: Connection | None = None

    def _validate_config(self) -> None:
        """Validate required configuration is present."""
        missing = []
        if not self.host:
            missing.append("host (or DATABRICKS_HOST)")
        if not self.http_path:
            missing.append("http_path (or DATABRICKS_HTTP_PATH)")
        if not self.access_token:
            missing.append("access_token (or DATABRICKS_TOKEN)")

        if missing:
            raise ValueError(f"Missing required Databricks configuration: {', '.join(missing)}")

        self.host = self.host.rstrip("/")
        if not self.host.startswith("https://"):
            self.host = f"https://{self.host}"

    @classmethod
    def from_config(cls, config: TargetConfig) -> DatabricksDimensionalWriter:
        """Create from configuration object."""
        settings = config.settings
        return cls(
            catalog=settings.get("catalog", "healthsim"),
            schema=settings.get("schema", "gold"),
            host=settings.get("host"),
            http_path=settings.get("http_path"),
            access_token=settings.get("access_token"),
        )

    def connect(self) -> None:
        """Establish connection to Databricks."""
        if self._conn is None:
            self._conn = databricks_sql.connect(
                server_hostname=self.host.replace("https://", ""),
                http_path=self.http_path,
                access_token=self.access_token,
            )
            self._ensure_schema()

    def _ensure_schema(self) -> None:
        """Create schema if it doesn't exist."""
        with self._conn.cursor() as cursor:
            cursor.execute(f"USE CATALOG {self.catalog}")
            cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {self.schema}")
            cursor.execute(f"USE SCHEMA {self.schema}")

    def close(self) -> None:
        """Close the database connection."""
        if self._conn is not None:
            self._conn.close()
            self._conn = None

    @property
    def connection(self) -> Connection:
        """Get active connection."""
        if self._conn is None:
            self.connect()
        return self._conn

    def write_table(
        self,
        table_name: str,
        df: pd.DataFrame,
        if_exists: str = "replace",
    ) -> int:
        """Write DataFrame to Databricks Delta table."""
        full_name = f"{self.catalog}.{self.schema}.{table_name}"

        if df.empty:
            return self._create_empty_table(table_name, df)

        with self.connection.cursor() as cursor:
            if if_exists == "replace":
                columns_sql = self._column_definitions(df)
                cursor.execute(f"""
                    CREATE OR REPLACE TABLE {full_name} (
                        {columns_sql}
                    ) USING DELTA
                """)
                self._insert_data(cursor, full_name, df)
            elif if_exists == "append":
                if not self.table_exists(table_name):
                    columns_sql = self._column_definitions(df)
                    cursor.execute(f"""
                        CREATE TABLE {full_name} (
                            {columns_sql}
                        ) USING DELTA
                    """)
                self._insert_data(cursor, full_name, df)
            else:
                raise ValueError("if_exists must be 'replace' or 'append'")

        return len(df)

    def _column_definitions(self, df: pd.DataFrame) -> str:
        """Generate SQL column definitions from DataFrame."""
        type_map = {
            "int64": "BIGINT",
            "int32": "INT",
            "float64": "DOUBLE",
            "float32": "FLOAT",
            "bool": "BOOLEAN",
            "object": "STRING",
            "string": "STRING",
            "datetime64[ns]": "TIMESTAMP",
        }
        cols = []
        for name, dtype in df.dtypes.items():
            sql_type = type_map.get(str(dtype), "STRING")
            cols.append(f"`{name}` {sql_type}")
        return ", ".join(cols)

    def _insert_data(
        self,
        cursor: Any,
        full_name: str,
        df: pd.DataFrame,
        batch_size: int = 1000,
    ) -> None:
        """Insert DataFrame rows in batches."""
        if df.empty:
            return

        columns = ", ".join(f"`{c}`" for c in df.columns)
        placeholders = ", ".join(["%s"] * len(df.columns))
        sql = f"INSERT INTO {full_name} ({columns}) VALUES ({placeholders})"

        rows = [tuple(None if pd.isna(v) else v for v in row) for row in df.values]

        for i in range(0, len(rows), batch_size):
            cursor.executemany(sql, rows[i : i + batch_size])

    def _create_empty_table(self, table_name: str, df: pd.DataFrame) -> int:
        """Create empty table with schema."""
        full_name = f"{self.catalog}.{self.schema}.{table_name}"
        columns_sql = self._column_definitions(df)
        with self.connection.cursor() as cursor:
            cursor.execute(f"""
                CREATE OR REPLACE TABLE {full_name} (
                    {columns_sql}
                ) USING DELTA
            """)
        return 0

    def get_table_list(self) -> list[str]:
        """Get list of tables in schema."""
        with self.connection.cursor() as cursor:
            cursor.execute(f"SHOW TABLES IN {self.catalog}.{self.schema}")
            return [row.tableName for row in cursor.fetchall()]

    def get_table_stats(self) -> pd.DataFrame:
        """Get statistics for all tables."""
        tables = self.get_table_list()
        stats = []
        with self.connection.cursor() as cursor:
            for table in tables:
                full_name = f"{self.catalog}.{self.schema}.{table}"
                cursor.execute(f"SELECT COUNT(*) as cnt FROM {full_name}")
                row_count = cursor.fetchone().cnt
                cursor.execute(f"DESCRIBE TABLE {full_name}")
                col_count = len(cursor.fetchall())
                stats.append({
                    "table_name": table,
                    "row_count": row_count,
                    "column_count": col_count,
                })
        return pd.DataFrame(stats)

    def query(self, sql: str) -> pd.DataFrame:
        """Execute SQL query and return results."""
        with self.connection.cursor() as cursor:
            cursor.execute(sql)
            results = cursor.fetchall()
            if not results:
                columns = [d[0] for d in cursor.description] if cursor.description else []
                return pd.DataFrame(columns=columns)
            columns = [d[0] for d in cursor.description]
            return pd.DataFrame([list(r) for r in results], columns=columns)

    def table_exists(self, table_name: str) -> bool:
        """Check if table exists."""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(f"""
                    SELECT 1 FROM {self.catalog}.information_schema.tables
                    WHERE table_catalog = '{self.catalog}'
                    AND table_schema = '{self.schema}'
                    AND table_name = '{table_name}'
                """)
                return cursor.fetchone() is not None
        except Exception:
            return False

    @property
    def full_table_prefix(self) -> str:
        """Return catalog.schema prefix."""
        return f"{self.catalog}.{self.schema}"

    def drop_table(self, table_name: str) -> bool:
        """Drop a table if it exists."""
        if not self.table_exists(table_name):
            return False
        full_name = f"{self.catalog}.{self.schema}.{table_name}"
        with self.connection.cursor() as cursor:
            cursor.execute(f"DROP TABLE IF EXISTS {full_name}")
        return True


__all__ = ["DatabricksDimensionalWriter"]
