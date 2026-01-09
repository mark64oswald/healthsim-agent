"""
HealthSim Agent - Core Agent Implementation

Orchestrates conversation flow, tool execution, and data generation.
"""
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable

from anthropic import Anthropic

from healthsim_agent.state.session import SessionState
from healthsim_agent.db.connection import DatabaseConnection


class AgentMode(Enum):
    """Operating modes for the agent."""
    INTERACTIVE = "interactive"
    BATCH = "batch"
    DEMO = "demo"


@dataclass
class AgentConfig:
    """Configuration for the HealthSim Agent."""
    model: str = "claude-sonnet-4-20250514"
    max_tokens: int = 4096
    debug: bool = False
    db_path: Path | None = None
    skills_path: Path | None = None
    
    @classmethod
    def from_file(cls, path: Path) -> "AgentConfig":
        """Load configuration from a YAML file."""
        import yaml
        with open(path) as f:
            data = yaml.safe_load(f)
        return cls(**data)


@dataclass
class HealthSimAgent:
    """
    Core agent for HealthSim conversational data generation.
    
    Responsibilities:
    - Manage conversation state and history
    - Route requests to appropriate skills
    - Execute tools for database and file operations
    - Coordinate data generation workflows
    """
    config_path: Path | None = None
    debug: bool = False
    
    # Internal state
    _client: Anthropic = field(default=None, init=False)
    _config: AgentConfig = field(default=None, init=False)
    _session: SessionState = field(default=None, init=False)
    _db: DatabaseConnection = field(default=None, init=False)
    _tools: dict[str, Callable] = field(default_factory=dict, init=False)
    
    def __post_init__(self):
        """Initialize agent components."""
        # Load configuration
        if self.config_path:
            self._config = AgentConfig.from_file(Path(self.config_path))
        else:
            self._config = AgentConfig(debug=self.debug)
        
        # Initialize Anthropic client
        self._client = Anthropic()
        
        # Initialize session state
        self._session = SessionState()
        
        # Register available tools
        self._register_tools()
    
    def _register_tools(self) -> None:
        """Register available tools for the agent."""
        # Tools will be registered here as they're implemented
        # Each tool maps a name to a callable
        self._tools = {
            "query_reference_data": self._tool_query_reference,
            "save_generated_data": self._tool_save_data,
            "load_skill": self._tool_load_skill,
        }
    
    def _tool_query_reference(self, query: str, **kwargs) -> dict[str, Any]:
        """Execute a query against the reference database."""
        if not self._db:
            return {"error": "Database not connected"}
        return self._db.execute_query(query, **kwargs)
    
    def _tool_save_data(self, data: dict, path: str, format: str = "json") -> dict[str, Any]:
        """Save generated data to a file."""
        # Implementation will be added in Phase 1
        return {"status": "not_implemented"}
    
    def _tool_load_skill(self, skill_name: str) -> dict[str, Any]:
        """Load a skill definition for the agent to use."""
        # Implementation will be added in Phase 1
        return {"status": "not_implemented"}
    
    def connect_database(self, db_path: Path | None = None) -> bool:
        """Connect to the reference database."""
        path = db_path or self._config.db_path
        if not path:
            return False
        
        try:
            self._db = DatabaseConnection(path)
            return True
        except Exception as e:
            if self._config.debug:
                raise
            return False
    
    def process_message(self, user_message: str) -> str:
        """
        Process a user message and return the agent's response.
        
        This is the main entry point for conversation turns.
        """
        # Add user message to history
        self._session.add_message("user", user_message)
        
        # Build messages for API call
        messages = self._session.get_messages_for_api()
        
        # Call the Claude API
        response = self._client.messages.create(
            model=self._config.model,
            max_tokens=self._config.max_tokens,
            system=self._build_system_prompt(),
            messages=messages,
        )
        
        # Extract response text
        assistant_message = response.content[0].text
        
        # Add to history
        self._session.add_message("assistant", assistant_message)
        
        return assistant_message
    
    def _build_system_prompt(self) -> str:
        """Build the system prompt with current context."""
        # This will be expanded with skills and context
        return """You are HealthSim, a conversational AI agent specialized in generating 
realistic synthetic healthcare data. You help users create patient records, claims data, 
pharmacy records, clinical trial data, and more.

You have access to reference databases with real demographic and provider information 
to ground your synthetic data generation in realistic patterns.

Be helpful, accurate, and always generate clinically plausible data."""
    
    @property
    def session(self) -> SessionState:
        """Get the current session state."""
        return self._session
    
    @property
    def is_connected(self) -> bool:
        """Check if database is connected."""
        return self._db is not None and self._db.is_connected
