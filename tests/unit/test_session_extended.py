"""
Extended tests for SessionState management.

Covers additional edge cases and methods:
- Message.text_content property
- get_recent_messages
- get_messages_for_api with content blocks
- Metadata handling
"""
import pytest
from datetime import datetime
from healthsim_agent.state import SessionState, Message, GeneratedItem


class TestMessage:
    """Tests for Message dataclass."""
    
    def test_create_message(self):
        """Test basic message creation."""
        msg = Message(role="user", content="Hello!")
        
        assert msg.role == "user"
        assert msg.content == "Hello!"
        assert isinstance(msg.timestamp, datetime)
        assert msg.metadata == {}
    
    def test_create_message_with_metadata(self):
        """Test message with metadata."""
        msg = Message(
            role="assistant",
            content="Response here",
            metadata={"tool_used": "generate_patient"}
        )
        
        assert msg.metadata["tool_used"] == "generate_patient"
    
    def test_text_content_string(self):
        """Test text_content with string content."""
        msg = Message(role="user", content="Simple text")
        
        assert msg.text_content == "Simple text"
    
    def test_text_content_list_with_text_attr(self):
        """Test text_content with list containing text attribute."""
        class TextBlock:
            def __init__(self, text):
                self.text = text
        
        msg = Message(
            role="assistant",
            content=[TextBlock("Hello"), TextBlock("World")]
        )
        
        assert "Hello" in msg.text_content
        assert "World" in msg.text_content
    
    def test_text_content_list_with_dicts(self):
        """Test text_content with list of dicts."""
        msg = Message(
            role="assistant",
            content=[
                {"text": "First block"},
                {"text": "Second block"}
            ]
        )
        
        assert "First block" in msg.text_content
        assert "Second block" in msg.text_content
    
    def test_text_content_empty_list(self):
        """Test text_content with empty list."""
        msg = Message(role="user", content=[])
        
        assert msg.text_content == ""


class TestGeneratedItem:
    """Tests for GeneratedItem dataclass."""
    
    def test_create_generated_item(self):
        """Test basic generated item creation."""
        item = GeneratedItem(
            item_type="patient",
            data={"id": "P001", "name": "John"}
        )
        
        assert item.item_type == "patient"
        assert item.data["id"] == "P001"
        assert item.skill_used is None
        assert isinstance(item.timestamp, datetime)
    
    def test_create_with_skill(self):
        """Test generated item with skill reference."""
        item = GeneratedItem(
            item_type="claim",
            data={"amount": 150.00},
            skill_used="membersim/claims"
        )
        
        assert item.skill_used == "membersim/claims"


class TestSessionStateExtended:
    """Extended tests for SessionState."""
    
    def test_get_recent_messages_all(self):
        """Test getting recent messages when fewer than n."""
        session = SessionState()
        session.add_message("user", "Msg 1")
        session.add_message("assistant", "Msg 2")
        
        recent = session.get_recent_messages(10)
        
        assert len(recent) == 2
        assert recent[0].content == "Msg 1"
        assert recent[1].content == "Msg 2"
    
    def test_get_recent_messages_truncated(self):
        """Test getting recent messages with truncation."""
        session = SessionState()
        for i in range(20):
            session.add_message("user", f"Message {i}")
        
        recent = session.get_recent_messages(5)
        
        assert len(recent) == 5
        assert recent[0].content == "Message 15"
        assert recent[4].content == "Message 19"
    
    def test_get_messages_for_api_with_content_blocks(self):
        """Test API formatting with complex content."""
        session = SessionState()
        
        # Add message with dict content blocks
        msg = Message(
            role="assistant",
            content=[
                {"type": "text", "text": "Hello"},
                {"type": "text", "text": "World"}
            ]
        )
        session.messages.append(msg)
        
        api_msgs = session.get_messages_for_api()
        
        assert len(api_msgs) == 1
        assert api_msgs[0]["role"] == "assistant"
        assert len(api_msgs[0]["content"]) == 2
    
    def test_add_message_with_metadata(self):
        """Test adding message with extra metadata."""
        session = SessionState()
        
        msg = session.add_message(
            "assistant",
            "Generated patient",
            tool="generate_patient",
            duration_ms=250
        )
        
        assert msg.metadata["tool"] == "generate_patient"
        assert msg.metadata["duration_ms"] == 250
    
    def test_multiple_items_same_type(self):
        """Test tracking multiple items of same type."""
        session = SessionState()
        
        session.add_generated_item("patient", {"id": "P001"})
        session.add_generated_item("patient", {"id": "P002"})
        session.add_generated_item("patient", {"id": "P003"})
        
        patients = session.get_items_by_type("patient")
        
        assert len(patients) == 3
        assert session.generated_count == 3
    
    def test_get_items_empty_type(self):
        """Test getting items of type that doesn't exist."""
        session = SessionState()
        session.add_generated_item("patient", {"id": "P001"})
        
        claims = session.get_items_by_type("claim")
        
        assert claims == []
    
    def test_session_preserves_id_on_clear(self):
        """Test that session_id persists through clear."""
        session = SessionState()
        original_id = session.session_id
        
        session.add_message("user", "Test")
        session.clear()
        
        assert session.session_id == original_id
    
    def test_context_overwrite(self):
        """Test overwriting context values."""
        session = SessionState()
        
        session.set_context("patient", {"id": "P001"})
        session.set_context("patient", {"id": "P002"})
        
        assert session.get_context("patient")["id"] == "P002"
    
    def test_to_dict_includes_all_fields(self):
        """Test serialization includes all fields."""
        session = SessionState()
        session.add_message("user", "Hello")
        session.add_generated_item("patient", {"id": "P001"})
        session.set_context("key", "value")
        
        data = session.to_dict()
        
        assert "session_id" in data
        assert "created_at" in data
        assert "messages" in data
        assert "generated_items" in data
        assert "context" in data


class TestSessionContentBlocks:
    """Tests for handling various content block formats."""
    
    def test_messages_with_model_dump(self):
        """Test handling objects with model_dump method."""
        class MockPydantic:
            def model_dump(self):
                return {"type": "text", "text": "pydantic content"}
        
        session = SessionState()
        msg = Message(role="assistant", content=[MockPydantic()])
        session.messages.append(msg)
        
        api_msgs = session.get_messages_for_api()
        
        assert api_msgs[0]["content"][0]["type"] == "text"
    
    def test_messages_with_to_dict(self):
        """Test handling objects with to_dict method."""
        class MockObject:
            def to_dict(self):
                return {"type": "text", "text": "dict content"}
        
        session = SessionState()
        msg = Message(role="assistant", content=[MockObject()])
        session.messages.append(msg)
        
        api_msgs = session.get_messages_for_api()
        
        assert api_msgs[0]["content"][0]["type"] == "text"
    
    def test_messages_with_text_attr(self):
        """Test handling objects with text attribute."""
        class TextBlock:
            def __init__(self):
                self.text = "plain text"
        
        session = SessionState()
        msg = Message(role="assistant", content=[TextBlock()])
        session.messages.append(msg)
        
        api_msgs = session.get_messages_for_api()
        
        assert api_msgs[0]["content"][0]["text"] == "plain text"
    
    def test_messages_with_tool_use(self):
        """Test handling tool use blocks."""
        class ToolUse:
            def __init__(self):
                self.id = "tool-123"
                self.name = "generate_patient"
                self.input = {"count": 5}
        
        session = SessionState()
        msg = Message(role="assistant", content=[ToolUse()])
        session.messages.append(msg)
        
        api_msgs = session.get_messages_for_api()
        
        assert api_msgs[0]["content"][0]["type"] == "tool_use"
        assert api_msgs[0]["content"][0]["name"] == "generate_patient"
