"""
HealthSim Agent - State Management Package

Provides session and cohort management:
- SessionState: Conversation history and context
- StateManager: Cohort persistence and entity tracking
- Cohort: Named collection of generated entities
- CohortSummary: Token-efficient cohort overview
"""

from healthsim_agent.state.session import (
    SessionState,
    Message,
    GeneratedItem,
)
from healthsim_agent.state.manager import (
    StateManager,
    Cohort,
    CohortSummary,
    EntityReference,
)

__all__ = [
    # Session management
    "SessionState",
    "Message",
    "GeneratedItem",
    # Cohort management
    "StateManager",
    "Cohort",
    "CohortSummary",
    "EntityReference",
]
