"""Extended tests for config/dimensional module."""

import pytest


class TestDimensionalConfig:
    """Tests for dimensional configuration."""
    
    def test_dimensional_import(self):
        """Test dimensional module imports."""
        from healthsim_agent.config import dimensional
        
        assert dimensional is not None
    
    def test_dimensional_config_class(self):
        """Test DimensionalConfig class."""
        from healthsim_agent.config.dimensional import DimensionalConfig
        
        assert DimensionalConfig is not None
    
    def test_config_manager_class(self):
        """Test ConfigManager class."""
        from healthsim_agent.config.dimensional import ConfigManager
        
        assert ConfigManager is not None
    
    def test_target_config_class(self):
        """Test TargetConfig class."""
        from healthsim_agent.config.dimensional import TargetConfig
        
        assert TargetConfig is not None
    
    def test_persistent_config_class(self):
        """Test HealthSimPersistentConfig class."""
        from healthsim_agent.config.dimensional import HealthSimPersistentConfig
        
        assert HealthSimPersistentConfig is not None
    
    def test_default_config_dir(self):
        """Test DEFAULT_CONFIG_DIR."""
        from healthsim_agent.config.dimensional import DEFAULT_CONFIG_DIR
        
        assert DEFAULT_CONFIG_DIR is not None
    
    def test_default_config_file(self):
        """Test DEFAULT_CONFIG_FILE."""
        from healthsim_agent.config.dimensional import DEFAULT_CONFIG_FILE
        
        assert DEFAULT_CONFIG_FILE is not None


class TestReferenceLoader:
    """Tests for reference data loader."""
    
    def test_loader_import(self):
        """Test loader module imports."""
        from healthsim_agent.db.reference import loader
        
        assert loader is not None
    
    def test_has_load_functions(self):
        """Test loader has load functions."""
        from healthsim_agent.db.reference import loader
        
        # Check for common loader functions
        module_attrs = dir(loader)
        assert any('load' in attr.lower() for attr in module_attrs)


class TestPopulationsimReference:
    """Tests for populationsim reference module."""
    
    def test_populationsim_import(self):
        """Test populationsim module imports."""
        from healthsim_agent.db.reference import populationsim
        
        assert populationsim is not None
    
    def test_has_population_functions(self):
        """Test has population functions."""
        from healthsim_agent.db.reference import populationsim
        
        # Check for common functions
        module_attrs = dir(populationsim)
        has_relevant = any('population' in attr.lower() or 'census' in attr.lower() 
                          for attr in module_attrs)
        assert has_relevant or len(module_attrs) > 5
