"""Plugin registry for dimensional writers.

Ported from: healthsim-workspace/packages/core/src/healthsim/dimensional/writers/registry.py
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from healthsim_agent.config.dimensional import TargetConfig
    from healthsim_agent.dimensional.writers.base import BaseDimensionalWriter

logger = logging.getLogger(__name__)


class WriterRegistry:
    """Registry for dimensional writer plugins."""

    _writers: dict[str, type[BaseDimensionalWriter]] = {}

    @classmethod
    def register(cls, writer_class: type[BaseDimensionalWriter]) -> None:
        """Register a writer class."""
        name = writer_class.TARGET_NAME
        if not name:
            raise ValueError(f"Writer {writer_class} must define TARGET_NAME")
        cls._writers[name] = writer_class
        logger.debug(f"Registered writer: {name}")

    @classmethod
    def get(cls, target_name: str) -> type[BaseDimensionalWriter]:
        """Get a writer class by target name."""
        if target_name not in cls._writers:
            available = cls.list_available()
            raise ValueError(f"Unknown target '{target_name}'. Available: {available}")

        writer_class = cls._writers[target_name]

        if not writer_class.is_available():
            raise ValueError(
                f"Target '{target_name}' requires packages: "
                f"{writer_class.REQUIRED_PACKAGES}. "
                f"Install with: pip install healthsim-agent[{target_name}]"
            )

        return writer_class

    @classmethod
    def list_registered(cls) -> list[str]:
        """List all registered writer names."""
        return list(cls._writers.keys())

    @classmethod
    def list_available(cls) -> list[str]:
        """List writer names that are installed and available."""
        return [name for name, writer_class in cls._writers.items() if writer_class.is_available()]

    @classmethod
    def create(cls, target_name: str, **kwargs) -> BaseDimensionalWriter:
        """Create a writer instance."""
        writer_class = cls.get(target_name)
        return writer_class(**kwargs)

    @classmethod
    def create_from_config(cls, config: TargetConfig) -> BaseDimensionalWriter:
        """Create a writer from a configuration object."""
        writer_class = cls.get(config.target_type)
        return writer_class.from_config(config)

    @classmethod
    def get_status(cls) -> dict[str, dict]:
        """Get status of all registered writers."""
        status = {}
        for name, writer_class in cls._writers.items():
            status[name] = {
                "registered": True,
                "available": writer_class.is_available(),
                "required_packages": writer_class.REQUIRED_PACKAGES,
            }
        return status


def _auto_register_writers() -> None:
    """Auto-register available writers on module import."""
    from healthsim_agent.dimensional.writers.duckdb_writer import DuckDBDimensionalWriter
    WriterRegistry.register(DuckDBDimensionalWriter)

    try:
        from healthsim_agent.dimensional.writers.databricks_writer import DatabricksDimensionalWriter
        WriterRegistry.register(DatabricksDimensionalWriter)
    except ImportError:
        logger.debug("Databricks writer not available (package not installed)")


_auto_register_writers()


__all__ = ["WriterRegistry"]
