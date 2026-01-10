"""Base class for dimensional model writers.

Ported from: healthsim-workspace/packages/core/src/healthsim/dimensional/writers/base.py
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

import pandas as pd

if TYPE_CHECKING:
    from healthsim_agent.config.dimensional import TargetConfig


class BaseDimensionalWriter(ABC):
    """Abstract base class for all dimensional writers."""

    TARGET_NAME: str = ""
    REQUIRED_PACKAGES: list[str] = []

    def __init__(self, schema: str = "analytics", **kwargs: Any) -> None:
        self.schema = schema
        self._config = kwargs

    @classmethod
    def from_config(cls, config: TargetConfig) -> BaseDimensionalWriter:
        """Create writer from configuration object."""
        return cls(**config.settings)

    @classmethod
    def is_available(cls) -> bool:
        """Check if required packages are installed."""
        for package in cls.REQUIRED_PACKAGES:
            try:
                __import__(package)
            except ImportError:
                return False
        return True

    @abstractmethod
    def connect(self) -> None:
        """Establish connection to the target database."""
        pass

    @abstractmethod
    def close(self) -> None:
        """Close the database connection."""
        pass

    def __enter__(self) -> BaseDimensionalWriter:
        self.connect()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object,
    ) -> None:
        self.close()

    @abstractmethod
    def write_table(
        self,
        table_name: str,
        df: pd.DataFrame,
        if_exists: str = "replace",
    ) -> int:
        """Write a single DataFrame to a table."""
        pass

    def write_dimensional_model(
        self,
        dimensions: dict[str, pd.DataFrame],
        facts: dict[str, pd.DataFrame],
    ) -> dict[str, int]:
        """Write complete dimensional model (dimensions and facts)."""
        results: dict[str, int] = {}
        for name, df in dimensions.items():
            results[name] = self.write_table(name, df)
        for name, df in facts.items():
            results[name] = self.write_table(name, df)
        return results

    @abstractmethod
    def get_table_list(self) -> list[str]:
        """Get list of tables in the schema."""
        pass

    @abstractmethod
    def get_table_stats(self) -> pd.DataFrame:
        """Get statistics for all tables in schema."""
        pass

    @abstractmethod
    def query(self, sql: str) -> pd.DataFrame:
        """Execute SQL query and return results as DataFrame."""
        pass

    @abstractmethod
    def table_exists(self, table_name: str) -> bool:
        """Check if a table exists in the schema."""
        pass

    @property
    @abstractmethod
    def full_table_prefix(self) -> str:
        """Return the fully qualified table name prefix."""
        pass

    @abstractmethod
    def drop_table(self, table_name: str) -> bool:
        """Drop a table if it exists."""
        pass

    def drop_all_tables(self) -> int:
        """Drop all tables in schema."""
        tables = self.get_table_list()
        for table in tables:
            self.drop_table(table)
        return len(tables)

    def health_check(self) -> dict[str, Any]:
        """Verify connection and return status."""
        try:
            self.connect()
            tables = self.get_table_list()
            return {
                "healthy": True,
                "message": "Connected successfully",
                "target": self.TARGET_NAME,
                "table_count": len(tables),
            }
        except Exception as e:
            return {
                "healthy": False,
                "message": str(e),
                "target": self.TARGET_NAME,
            }
        finally:
            self.close()


__all__ = ["BaseDimensionalWriter"]
