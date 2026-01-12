"""Tests for config/dimensional module."""

import pytest
from pathlib import Path


class TestDimensionalConfig:
    """Tests for DimensionalConfig dataclass."""
    
    def test_create_default(self):
        """Test creating default config."""
        from healthsim_agent.config.dimensional import DimensionalConfig
        
        config = DimensionalConfig()
        assert config is not None
    
    def test_config_fields(self):
        """Test config has expected fields."""
        from healthsim_agent.config.dimensional import DimensionalConfig
        
        config = DimensionalConfig()
        # Check it's a dataclass with some fields
        assert hasattr(config, '__dataclass_fields__')


class TestTargetConfig:
    """Tests for TargetConfig dataclass."""
    
    def test_create_with_type(self):
        """Test creating target config with required arg."""
        from healthsim_agent.config.dimensional import TargetConfig
        
        config = TargetConfig(target_type="duckdb")
        assert config is not None


class TestHealthSimPersistentConfig:
    """Tests for HealthSimPersistentConfig dataclass."""
    
    def test_create_default(self):
        """Test creating default persistent config."""
        from healthsim_agent.config.dimensional import HealthSimPersistentConfig
        
        config = HealthSimPersistentConfig()
        assert config is not None


class TestConfigManager:
    """Tests for ConfigManager class."""
    
    def test_create_manager(self):
        """Test creating config manager."""
        from healthsim_agent.config.dimensional import ConfigManager
        
        manager = ConfigManager()
        assert manager is not None
    
    def test_default_config_dir(self):
        """Test default config directory constant."""
        from healthsim_agent.config.dimensional import DEFAULT_CONFIG_DIR
        
        assert DEFAULT_CONFIG_DIR is not None
    
    def test_default_config_file(self):
        """Test default config file constant."""
        from healthsim_agent.config.dimensional import DEFAULT_CONFIG_FILE
        
        assert DEFAULT_CONFIG_FILE is not None
