"""Tests for agent module."""

import pytest


class TestAgentMode:
    """Tests for AgentMode enum."""
    
    def test_agent_modes_exist(self):
        """Test AgentMode enum exists."""
        from healthsim_agent.agent import AgentMode
        
        assert AgentMode is not None
    
    def test_mode_values(self):
        """Test AgentMode has expected values."""
        from healthsim_agent.agent import AgentMode
        
        # Check it's an Enum
        assert hasattr(AgentMode, '__members__')


class TestAgentConfig:
    """Tests for AgentConfig dataclass."""
    
    def test_create_default(self):
        """Test creating default config."""
        from healthsim_agent.agent import AgentConfig
        
        config = AgentConfig()
        assert config is not None
    
    def test_config_is_dataclass(self):
        """Test config is a dataclass."""
        from healthsim_agent.agent import AgentConfig
        
        config = AgentConfig()
        assert hasattr(config, '__dataclass_fields__')


class TestSessionState:
    """Tests for SessionState dataclass."""
    
    def test_create_default(self):
        """Test creating default session state."""
        from healthsim_agent.agent import SessionState
        
        state = SessionState()
        assert state is not None
    
    def test_state_is_dataclass(self):
        """Test state is a dataclass."""
        from healthsim_agent.agent import SessionState
        
        state = SessionState()
        assert hasattr(state, '__dataclass_fields__')


class TestToolDefinitions:
    """Tests for TOOL_DEFINITIONS constant."""
    
    def test_tool_definitions_exist(self):
        """Test tool definitions exist."""
        from healthsim_agent.agent import TOOL_DEFINITIONS
        
        assert TOOL_DEFINITIONS is not None
    
    def test_tool_definitions_is_list(self):
        """Test tool definitions is a list."""
        from healthsim_agent.agent import TOOL_DEFINITIONS
        
        assert isinstance(TOOL_DEFINITIONS, list)
    
    def test_tool_definitions_not_empty(self):
        """Test tool definitions is not empty."""
        from healthsim_agent.agent import TOOL_DEFINITIONS
        
        assert len(TOOL_DEFINITIONS) > 0


class TestHealthSimAgentCreation:
    """Tests for HealthSimAgent class creation."""
    
    def test_agent_class_exists(self):
        """Test HealthSimAgent class exists."""
        from healthsim_agent.agent import HealthSimAgent
        
        assert HealthSimAgent is not None
