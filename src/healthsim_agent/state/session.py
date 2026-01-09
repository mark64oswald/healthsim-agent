"""
HealthSim Agent - Session State Management

Manages conversation history, context, and generated data tracking.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import uuid4


@dataclass
class Message:
    """A single message in the conversation."""
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class GeneratedItem:
    """Track a piece of generated data."""
    item_type: str  # "patient", "claim", "provider", etc.
    data: dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    skill_used: str | None = None


@dataclass 
class SessionState:
    """
    Manages the state of a HealthSim conversation session.
    
    Tracks:
    - Conversation history
    - Generated data items
    - Active context (current patient, scenario, etc.)
    - Session metadata
    """
    session_id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=datetime.now)
    messages: list[Message] = field(default_factory=list)
    generated_items: list[GeneratedItem] = field(default_factory=list)
    context: dict[str, Any] = field(default_factory=dict)
    
    def add_message(self, role: str, content: str, **metadata) -> Message:
        """Add a message to the conversation history."""
        msg = Message(role=role, content=content, metadata=metadata)
        self.messages.append(msg)
        return msg
    
    def add_generated_item(
        self,
        item_type: str,
        data: dict[str, Any],
        skill_used: str | None = None,
    ) -> GeneratedItem:
        """Track a newly generated data item."""
        item = GeneratedItem(
            item_type=item_type,
            data=data,
            skill_used=skill_used,
        )
        self.generated_items.append(item)
        return item
    
    def get_messages_for_api(self) -> list[dict[str, str]]:
        """Get messages formatted for the Anthropic API."""
        return [
            {"role": msg.role, "content": msg.content}
            for msg in self.messages
        ]
    
    def get_recent_messages(self, n: int = 10) -> list[Message]:
        """Get the n most recent messages."""
        return self.messages[-n:]
    
    def set_context(self, key: str, value: Any) -> None:
        """Set a context value."""
        self.context[key] = value
    
    def get_context(self, key: str, default: Any = None) -> Any:
        """Get a context value."""
        return self.context.get(key, default)
    
    def clear(self) -> None:
        """Clear conversation history but preserve session."""
        self.messages.clear()
        self.generated_items.clear()
        self.context.clear()
    
    @property
    def message_count(self) -> int:
        """Get total message count."""
        return len(self.messages)
    
    @property
    def generated_count(self) -> int:
        """Get count of generated items."""
        return len(self.generated_items)
    
    def get_items_by_type(self, item_type: str) -> list[GeneratedItem]:
        """Get all generated items of a specific type."""
        return [
            item for item in self.generated_items
            if item.item_type == item_type
        ]
    
    def to_dict(self) -> dict[str, Any]:
        """Serialize session state to dictionary."""
        return {
            "session_id": self.session_id,
            "created_at": self.created_at.isoformat(),
            "messages": [
                {
                    "role": m.role,
                    "content": m.content,
                    "timestamp": m.timestamp.isoformat(),
                    "metadata": m.metadata,
                }
                for m in self.messages
            ],
            "generated_items": [
                {
                    "item_type": g.item_type,
                    "data": g.data,
                    "timestamp": g.timestamp.isoformat(),
                    "skill_used": g.skill_used,
                }
                for g in self.generated_items
            ],
            "context": self.context,
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SessionState":
        """Deserialize session state from dictionary."""
        session = cls(
            session_id=data["session_id"],
            created_at=datetime.fromisoformat(data["created_at"]),
            context=data.get("context", {}),
        )
        
        for m in data.get("messages", []):
            msg = Message(
                role=m["role"],
                content=m["content"],
                timestamp=datetime.fromisoformat(m["timestamp"]),
                metadata=m.get("metadata", {}),
            )
            session.messages.append(msg)
        
        for g in data.get("generated_items", []):
            item = GeneratedItem(
                item_type=g["item_type"],
                data=g["data"],
                timestamp=datetime.fromisoformat(g["timestamp"]),
                skill_used=g.get("skill_used"),
            )
            session.generated_items.append(item)
        
        return session
