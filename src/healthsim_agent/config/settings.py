"""Settings management for HealthSim applications.

Ported from: healthsim-workspace/packages/core/src/healthsim/config/settings.py
"""

from pydantic import BaseModel, Field


class HealthSimSettings(BaseModel):
    """Base settings for HealthSim applications."""

    app_name: str = Field(default="healthsim", description="Application name")
    debug: bool = Field(default=False, description="Enable debug mode")
    log_level: str = Field(default="INFO", description="Logging level")
    random_seed: int | None = Field(default=None, description="Random seed for reproducibility")
    locale: str = Field(default="en_US", description="Locale for data generation")

    model_config = {"extra": "allow"}


__all__ = ["HealthSimSettings"]
