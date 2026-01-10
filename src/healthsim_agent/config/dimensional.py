"""Persistent configuration for HealthSim dimensional output.

Stores user preferences including default dimensional output target.
Configuration is stored in ~/.healthsim/config.yaml

Ported from: healthsim-workspace/packages/core/src/healthsim/config/dimensional.py
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import yaml

DEFAULT_CONFIG_DIR = Path.home() / ".healthsim"
DEFAULT_CONFIG_FILE = DEFAULT_CONFIG_DIR / "config.yaml"


@dataclass
class TargetConfig:
    """Configuration for a dimensional output target."""

    target_type: str  # e.g., 'duckdb', 'databricks'
    settings: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TargetConfig:
        return cls(
            target_type=data["target_type"],
            settings=data.get("settings", {}),
        )


@dataclass
class DimensionalConfig:
    """Configuration for dimensional output."""

    default_target: str = "duckdb"
    targets: dict[str, TargetConfig] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Ensure default DuckDB config exists."""
        if "duckdb" not in self.targets:
            self.targets["duckdb"] = TargetConfig(
                target_type="duckdb",
                settings={
                    "db_path": str(DEFAULT_CONFIG_DIR / "data" / "analytics.duckdb"),
                    "schema": "analytics",
                },
            )

    def get_target_config(self, target_name: str | None = None) -> TargetConfig:
        """Get config for specified target, or default target."""
        name = target_name or self.default_target
        if name not in self.targets:
            raise ValueError(f"No configuration for target '{name}'")
        return self.targets[name]

    def set_target_config(
        self,
        target_name: str,
        target_type: str,
        settings: dict[str, Any],
        set_as_default: bool = False,
    ) -> None:
        """Add or update a target configuration."""
        self.targets[target_name] = TargetConfig(
            target_type=target_type,
            settings=settings,
        )
        if set_as_default:
            self.default_target = target_name

    def to_dict(self) -> dict[str, Any]:
        return {
            "default_target": self.default_target,
            "targets": {name: config.to_dict() for name, config in self.targets.items()},
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DimensionalConfig:
        targets = {}
        for name, config_data in data.get("targets", {}).items():
            targets[name] = TargetConfig.from_dict(config_data)
        return cls(
            default_target=data.get("default_target", "duckdb"),
            targets=targets,
        )


@dataclass
class HealthSimPersistentConfig:
    """Root configuration for HealthSim."""

    dimensional: DimensionalConfig = field(default_factory=DimensionalConfig)

    def to_dict(self) -> dict[str, Any]:
        return {"dimensional": self.dimensional.to_dict()}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> HealthSimPersistentConfig:
        dimensional = DimensionalConfig.from_dict(data.get("dimensional", {}))
        return cls(dimensional=dimensional)


class ConfigManager:
    """Manages persistent configuration."""

    _config_path: Path = DEFAULT_CONFIG_FILE
    _cached_config: HealthSimPersistentConfig | None = None

    @classmethod
    def set_config_path(cls, path: Path) -> None:
        """Override config file path (useful for testing)."""
        cls._config_path = path
        cls._cached_config = None

    @classmethod
    def load(cls, force_reload: bool = False) -> HealthSimPersistentConfig:
        """Load configuration from file."""
        if cls._cached_config is not None and not force_reload:
            return cls._cached_config

        if cls._config_path.exists():
            with open(cls._config_path) as f:
                data = yaml.safe_load(f) or {}
            config = HealthSimPersistentConfig.from_dict(data)
        else:
            config = HealthSimPersistentConfig()

        cls._cached_config = config
        return config

    @classmethod
    def save(cls, config: HealthSimPersistentConfig) -> None:
        """Save configuration to file."""
        cls._config_path.parent.mkdir(parents=True, exist_ok=True)

        with open(cls._config_path, "w") as f:
            yaml.dump(config.to_dict(), f, default_flow_style=False, sort_keys=False)

        cls._cached_config = config

    @classmethod
    def get_dimensional_config(cls) -> DimensionalConfig:
        """Convenience method to get dimensional config."""
        return cls.load().dimensional

    @classmethod
    def set_default_target(
        cls,
        target_name: str,
        target_type: str | None = None,
        settings: dict[str, Any] | None = None,
    ) -> None:
        """Set the default dimensional output target."""
        config = cls.load()

        if target_name not in config.dimensional.targets:
            if target_type is None or settings is None:
                raise ValueError(f"Target '{target_name}' not configured")
            config.dimensional.set_target_config(
                target_name, target_type, settings, set_as_default=True
            )
        else:
            config.dimensional.default_target = target_name

        cls.save(config)

    @classmethod
    def configure_target(
        cls,
        target_name: str,
        target_type: str,
        settings: dict[str, Any],
        set_as_default: bool = False,
    ) -> None:
        """Add or update a target configuration."""
        config = cls.load()
        config.dimensional.set_target_config(target_name, target_type, settings, set_as_default)
        cls.save(config)


__all__ = [
    "DEFAULT_CONFIG_DIR",
    "DEFAULT_CONFIG_FILE",
    "TargetConfig",
    "DimensionalConfig",
    "HealthSimPersistentConfig",
    "ConfigManager",
]
