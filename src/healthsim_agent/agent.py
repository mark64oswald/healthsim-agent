"""
HealthSim Agent - Core Agent Implementation

Orchestrates conversation flow, tool execution, and data generation
with full Claude API tool calling support.
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Generator
import json

from anthropic import Anthropic
from anthropic.types import (
    Message, ContentBlock, TextBlock, ToolUseBlock, ToolResultBlockParam
)

from healthsim_agent.state.session import SessionState


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


# ============================================================================
# Tool Definitions for Claude API
# ============================================================================

TOOL_DEFINITIONS = [
    {
        "name": "list_cohorts",
        "description": "List all saved cohorts. Can filter by tag or search term.",
        "input_schema": {
            "type": "object",
            "properties": {
                "tag": {"type": "string", "description": "Filter by tag"},
                "search": {"type": "string", "description": "Search in name/description"},
                "limit": {"type": "integer", "description": "Max results", "default": 50}
            }
        }
    },
    {
        "name": "load_cohort",
        "description": "Load a cohort by ID or name to view its entities.",
        "input_schema": {
            "type": "object",
            "properties": {
                "cohort_id": {"type": "string", "description": "Cohort ID or name"}
            },
            "required": ["cohort_id"]
        }
    },
    {
        "name": "save_cohort",
        "description": "Save a new cohort with entities. For incremental additions, use add_entities instead.",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Cohort name"},
                "description": {"type": "string", "description": "Cohort description"},
                "entities": {
                    "type": "object",
                    "description": "Entities by type, e.g. {'patient': [...], 'encounter': [...]}"
                },
                "tags": {"type": "array", "items": {"type": "string"}, "description": "Tags"}
            },
            "required": ["name", "entities"]
        }
    },
    {
        "name": "add_entities",
        "description": "Add entities to an existing cohort. Creates cohort if it doesn't exist. RECOMMENDED for incremental generation.",
        "input_schema": {
            "type": "object",
            "properties": {
                "cohort_id": {"type": "string", "description": "Cohort ID or name"},
                "entities": {
                    "type": "object",
                    "description": "Entities by type to add"
                }
            },
            "required": ["cohort_id", "entities"]
        }
    },
    {
        "name": "delete_cohort",
        "description": "Delete a cohort and all its entities. Requires confirmation.",
        "input_schema": {
            "type": "object",
            "properties": {
                "cohort_id": {"type": "string", "description": "Cohort ID or name"},
                "confirm": {"type": "boolean", "description": "Must be true to delete"}
            },
            "required": ["cohort_id", "confirm"]
        }
    },
    {
        "name": "query",
        "description": "Execute a read-only SQL query against the database.",
        "input_schema": {
            "type": "object",
            "properties": {
                "sql": {"type": "string", "description": "SQL query (SELECT only)"},
                "limit": {"type": "integer", "description": "Max rows", "default": 100}
            },
            "required": ["sql"]
        }
    },
    {
        "name": "get_summary",
        "description": "Get a token-efficient summary of a cohort.",
        "input_schema": {
            "type": "object",
            "properties": {
                "cohort_id": {"type": "string", "description": "Cohort ID or name"}
            },
            "required": ["cohort_id"]
        }
    },
    {
        "name": "list_tables",
        "description": "List available database tables by category.",
        "input_schema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "query_reference",
        "description": "Query PopulationSim reference data (CDC PLACES, SVI, ADI).",
        "input_schema": {
            "type": "object",
            "properties": {
                "dataset": {
                    "type": "string",
                    "enum": ["places", "svi", "adi", "acs"],
                    "description": "Reference dataset"
                },
                "filters": {
                    "type": "object",
                    "description": "Filter conditions, e.g. {'state': 'TX', 'city': 'Austin'}"
                },
                "limit": {"type": "integer", "default": 100}
            },
            "required": ["dataset"]
        }
    },
    {
        "name": "search_providers",
        "description": "Search NPPES provider registry (8.9M providers).",
        "input_schema": {
            "type": "object",
            "properties": {
                "specialty": {"type": "string", "description": "Specialty keyword or taxonomy code"},
                "city": {"type": "string"},
                "state": {"type": "string", "description": "2-letter state code"},
                "zip_code": {"type": "string"},
                "name": {"type": "string", "description": "Provider name search"},
                "limit": {"type": "integer", "default": 50}
            }
        }
    },
    {
        "name": "transform_to_fhir",
        "description": "Transform cohort to FHIR R4 bundle.",
        "input_schema": {
            "type": "object",
            "properties": {
                "cohort_id": {"type": "string"},
                "bundle_type": {"type": "string", "enum": ["collection", "batch", "transaction"], "default": "collection"}
            },
            "required": ["cohort_id"]
        }
    },
    {
        "name": "transform_to_ccda",
        "description": "Transform cohort to C-CDA XML document.",
        "input_schema": {
            "type": "object",
            "properties": {
                "cohort_id": {"type": "string"},
                "document_type": {"type": "string", "enum": ["ccd", "discharge_summary", "progress_note"], "default": "ccd"}
            },
            "required": ["cohort_id"]
        }
    },
    {
        "name": "transform_to_hl7v2",
        "description": "Transform cohort to HL7v2 messages.",
        "input_schema": {
            "type": "object",
            "properties": {
                "cohort_id": {"type": "string"},
                "message_type": {"type": "string", "enum": ["ADT_A01", "ADT_A03", "ADT_A08"], "default": "ADT_A01"}
            },
            "required": ["cohort_id"]
        }
    },
    {
        "name": "transform_to_x12",
        "description": "Transform cohort to X12 EDI format.",
        "input_schema": {
            "type": "object",
            "properties": {
                "cohort_id": {"type": "string"},
                "transaction_type": {"type": "string", "enum": ["837P", "837I", "835", "834"], "default": "837P"}
            },
            "required": ["cohort_id"]
        }
    },
    {
        "name": "list_output_formats",
        "description": "List all available output formats for data transformation.",
        "input_schema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "transform_to_ncpdp",
        "description": "Transform cohort to NCPDP SCRIPT format for e-prescribing.",
        "input_schema": {
            "type": "object",
            "properties": {
                "cohort_id": {"type": "string"},
                "message_type": {"type": "string", "enum": ["NewRx", "RxRenewal", "RxChange"], "default": "NewRx"}
            },
            "required": ["cohort_id"]
        }
    },
    {
        "name": "transform_to_mimic",
        "description": "Transform cohort to MIMIC-III research format.",
        "input_schema": {
            "type": "object",
            "properties": {
                "cohort_id": {"type": "string"}
            },
            "required": ["cohort_id"]
        }
    }
]


# ============================================================================
# Tool Execution Mapping
# ============================================================================

def _get_tool_executor(tool_name: str) -> Callable | None:
    """Get the executor function for a tool."""
    # Import tools lazily to avoid circular imports
    from healthsim_agent.tools.cohort_tools import (
        list_cohorts, load_cohort, save_cohort, add_entities, delete_cohort
    )
    from healthsim_agent.tools.query_tools import (
        query, get_summary, list_tables
    )
    from healthsim_agent.tools.reference_tools import (
        query_reference, search_providers
    )
    from healthsim_agent.tools.format_tools import (
        transform_to_fhir, transform_to_ccda, transform_to_hl7v2,
        transform_to_x12, transform_to_ncpdp, transform_to_mimic, list_output_formats
    )
    
    executors = {
        "list_cohorts": list_cohorts,
        "load_cohort": load_cohort,
        "save_cohort": save_cohort,
        "add_entities": add_entities,
        "delete_cohort": delete_cohort,
        "query": query,
        "get_summary": get_summary,
        "list_tables": list_tables,
        "query_reference": query_reference,
        "search_providers": search_providers,
        "transform_to_fhir": transform_to_fhir,
        "transform_to_ccda": transform_to_ccda,
        "transform_to_hl7v2": transform_to_hl7v2,
        "transform_to_x12": transform_to_x12,
        "transform_to_ncpdp": transform_to_ncpdp,
        "transform_to_mimic": transform_to_mimic,
        "list_output_formats": list_output_formats,
    }
    
    return executors.get(tool_name)


@dataclass
class HealthSimAgent:
    """
    Core agent for HealthSim conversational data generation.
    
    Features:
    - Full Claude API tool calling support
    - Multi-turn conversation with tool execution
    - Skills-aware system prompts
    - Streaming response support
    """
    config_path: Path | None = None
    debug: bool = False
    
    # Internal state
    _client: Anthropic = field(default=None, init=False)
    _config: AgentConfig = field(default=None, init=False)
    _session: SessionState = field(default=None, init=False)
    _skills_context: str = field(default="", init=False)
    
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
        
        # Load skills context
        self._load_skills_context()
    
    def _load_skills_context(self) -> None:
        """Load skills to inform system prompt."""
        try:
            from healthsim_agent.skills.loader import SkillLoader
            from healthsim_agent.skills.router import SkillRouter
            
            # Find skills directory
            skills_path = Path(__file__).parent / "skills" / "scenarios"
            if skills_path.exists():
                loader = SkillLoader(skills_path)
                index = loader.load_all()
                
                # Build context summary
                products = set()
                triggers = []
                for skill in index.skills.values():
                    if skill.metadata.product:
                        products.add(skill.metadata.product)
                    triggers.extend(skill.metadata.triggers[:3])
                
                self._skills_context = f"""
Available products: {', '.join(sorted(products))}
Sample capabilities: {', '.join(triggers[:15])}
"""
        except Exception as e:
            if self._config.debug:
                print(f"Skills loading warning: {e}")
            self._skills_context = ""
    
    def _build_system_prompt(self) -> str:
        """Build the system prompt with skills context."""
        base_prompt = """You are HealthSim, a conversational AI agent specialized in generating 
realistic synthetic healthcare data. You help users create:

- Patient records (demographics, encounters, diagnoses, labs, vitals)
- Payer/claims data (members, claims, benefits)
- Pharmacy records (prescriptions, pharmacy claims)
- Clinical trial data (subjects, visits, adverse events)

You have access to tools for:
1. **Cohort Management**: Create, load, save, and manage cohorts of generated entities
2. **Data Generation**: Generate realistic healthcare data based on user requests
3. **Reference Data**: Query real demographic data (CDC, Census) and provider registry (NPPES)
4. **Format Transformation**: Export to FHIR, C-CDA, HL7v2, X12, and other standards

Guidelines:
- Generate clinically plausible data with realistic values
- Use real geographic and demographic patterns from reference data
- Maintain consistency within cohorts (patient IDs, dates, relationships)
- Explain what you're generating and why
- Use add_entities to incrementally build cohorts (recommended over save_cohort)
"""
        
        if self._skills_context:
            base_prompt += f"\n{self._skills_context}"
        
        return base_prompt
    
    def process_message(self, user_message: str) -> str:
        """
        Process a user message and return the agent's response.
        
        Handles multi-turn tool calling automatically.
        """
        # Add user message to history
        self._session.add_message("user", user_message)
        
        # Build messages for API call
        messages = self._session.get_messages_for_api()
        
        # Call Claude with tools
        response = self._client.messages.create(
            model=self._config.model,
            max_tokens=self._config.max_tokens,
            system=self._build_system_prompt(),
            messages=messages,
            tools=TOOL_DEFINITIONS,
        )
        
        # Handle tool calls in a loop
        while response.stop_reason == "tool_use":
            # Extract tool calls and execute them
            tool_results = self._execute_tool_calls(response)
            
            # Add assistant message and tool results to conversation
            self._session.add_message("assistant", response.content)
            
            # Build tool result messages
            messages = self._session.get_messages_for_api()
            messages.append({
                "role": "user",
                "content": tool_results
            })
            
            # Continue conversation
            response = self._client.messages.create(
                model=self._config.model,
                max_tokens=self._config.max_tokens,
                system=self._build_system_prompt(),
                messages=messages,
                tools=TOOL_DEFINITIONS,
            )
        
        # Extract final text response
        assistant_message = self._extract_text(response)
        
        # Add to history
        self._session.add_message("assistant", assistant_message)
        
        return assistant_message
    
    def _execute_tool_calls(self, response: Message) -> list[ToolResultBlockParam]:
        """Execute all tool calls in a response."""
        results = []
        
        for block in response.content:
            if isinstance(block, ToolUseBlock):
                tool_name = block.name
                tool_input = block.input
                tool_id = block.id
                
                if self._config.debug:
                    print(f"Executing tool: {tool_name}")
                    print(f"Input: {json.dumps(tool_input, indent=2)}")
                
                # Execute the tool
                result = self._execute_single_tool(tool_name, tool_input)
                
                results.append({
                    "type": "tool_result",
                    "tool_use_id": tool_id,
                    "content": json.dumps(result, default=str),
                })
        
        return results
    
    def _execute_single_tool(self, tool_name: str, tool_input: dict) -> dict:
        """Execute a single tool and return result."""
        executor = _get_tool_executor(tool_name)
        
        if executor is None:
            return {"error": f"Unknown tool: {tool_name}"}
        
        try:
            result = executor(**tool_input)
            
            # Convert ToolResult to dict
            if hasattr(result, 'success'):
                return {
                    "success": result.success,
                    "data": result.data,
                    "error": result.error,
                }
            return result
            
        except Exception as e:
            if self._config.debug:
                import traceback
                traceback.print_exc()
            return {"error": str(e)}
    
    def _extract_text(self, response: Message) -> str:
        """Extract text content from response."""
        text_parts = []
        for block in response.content:
            if isinstance(block, TextBlock):
                text_parts.append(block.text)
        return "\n".join(text_parts)

    
    def process_message_streaming(
        self, 
        user_message: str,
        on_text: Callable[[str], None] | None = None,
        on_tool_start: Callable[[str, dict], None] | None = None,
        on_tool_end: Callable[[str, dict], None] | None = None,
    ) -> str:
        """
        Process a user message with streaming response.
        
        Callbacks:
            on_text: Called with each text chunk
            on_tool_start: Called when a tool starts (name, input)
            on_tool_end: Called when a tool completes (name, result)
        """
        # Add user message to history
        self._session.add_message("user", user_message)
        
        # Build messages for API call
        messages = self._session.get_messages_for_api()
        
        full_response = ""
        
        # Stream the response
        with self._client.messages.stream(
            model=self._config.model,
            max_tokens=self._config.max_tokens,
            system=self._build_system_prompt(),
            messages=messages,
            tools=TOOL_DEFINITIONS,
        ) as stream:
            # Collect the full message
            response = stream.get_final_message()
            
            # Stream text as it arrives
            for text in stream.text_stream:
                if on_text:
                    on_text(text)
                full_response += text
        
        # Handle tool calls
        while response.stop_reason == "tool_use":
            tool_results = []
            
            for block in response.content:
                if isinstance(block, ToolUseBlock):
                    if on_tool_start:
                        on_tool_start(block.name, block.input)
                    
                    result = self._execute_single_tool(block.name, block.input)
                    
                    if on_tool_end:
                        on_tool_end(block.name, result)
                    
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": json.dumps(result, default=str),
                    })
            
            # Add to conversation and continue
            self._session.add_message("assistant", response.content)
            messages = self._session.get_messages_for_api()
            messages.append({"role": "user", "content": tool_results})
            
            # Stream continuation
            with self._client.messages.stream(
                model=self._config.model,
                max_tokens=self._config.max_tokens,
                system=self._build_system_prompt(),
                messages=messages,
                tools=TOOL_DEFINITIONS,
            ) as stream:
                response = stream.get_final_message()
                for text in stream.text_stream:
                    if on_text:
                        on_text(text)
                    full_response += text
        
        # Final text extraction
        final_text = self._extract_text(response)
        self._session.add_message("assistant", final_text)
        
        return final_text
    
    def save_session(self, path: Path | str) -> None:
        """Save session state to a file."""
        path = Path(path)
        session_data = self._session.to_dict()
        session_data["metadata"] = {
            "model": self._config.model,
            "saved_at": datetime.now().isoformat(),
        }
        
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w') as f:
            json.dump(session_data, f, indent=2, default=str)
    
    def load_session(self, path: Path | str) -> bool:
        """Load session state from a file."""
        path = Path(path)
        if not path.exists():
            return False
        
        try:
            with open(path) as f:
                session_data = json.load(f)
            
            self._session = SessionState.from_dict(session_data)
            return True
        except Exception as e:
            if self._config.debug:
                print(f"Failed to load session: {e}")
            return False
    
    def clear_session(self) -> None:
        """Clear the current session."""
        self._session = SessionState()
    
    @property
    def session(self) -> SessionState:
        """Get the current session state."""
        return self._session
    
    @property
    def is_connected(self) -> bool:
        """Check if database is accessible."""
        try:
            from healthsim_agent.tools.connection import get_manager
            manager = get_manager()
            conn = manager.get_read_connection()
            return conn is not None
        except:
            return False
    
    @property
    def message_count(self) -> int:
        """Get number of messages in session."""
        return len(self._session.messages)
