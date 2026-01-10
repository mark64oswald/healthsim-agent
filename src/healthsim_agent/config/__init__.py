"""Configuration management for HealthSim applications.

This package provides configuration management including:
- Base settings class for application configuration
- Dimensional output configuration for analytics targets
- Persistent configuration storage in ~/.healthsim/config.yaml
"""

from healthsim_agent.config.settings import HealthSimSettings

from healthsim_agent.config.dimensional import (
    DEFAULT_CONFIG_DIR,
    DEFAULT_CONFIG_FILE,
    TargetConfig,
    DimensionalConfig,
    HealthSimPersistentConfig,
    ConfigManager,
)


__all__ = [
    # Settings
    "HealthSimSettings",
    # Dimensional config
    "DEFAULT_CONFIG_DIR",
    "DEFAULT_CONFIG_FILE",
    "TargetConfig",
    "DimensionalConfig",
    "HealthSimPersistentConfig",
    "ConfigManager",
]
