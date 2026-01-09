"""
Tests for SessionState management.
"""
import pytest
from healthsim_agent.state import SessionState, Message, GeneratedItem


class TestSessionState:
    """Test session state management."""
    
    def test_create_session(self):
        """Test session creation with default values."""
        session = SessionState()
        
        assert session.session_id is not None
        assert session.message_count == 0
        assert session.generated_count == 0
        assert session.messages == []
        assert session.context == {}
    
    def test_add_message(self):
        """Test adding messages to session."""
        session = SessionState()
        
        msg = session.add_message("user", "Hello!")
        
        assert isinstance(msg, Message)
        assert msg.role == "user"
        assert msg.content == "Hello!"
        assert session.message_count == 1
    
    def test_add_multiple_messages(self):
        """Test conversation flow with multiple messages."""
        session = SessionState()
        
        session.add_message("user", "Generate a patient")
        session.add_message("assistant", "Here's a patient record...")
        session.add_message("user", "Add diabetes")
        
        assert session.message_count == 3
        
        api_messages = session.get_messages_for_api()
        assert len(api_messages) == 3
        assert api_messages[0]["role"] == "user"
        assert api_messages[1]["role"] == "assistant"
    
    def test_add_generated_item(self):
        """Test tracking generated data items."""
        session = SessionState()
        
        item = session.add_generated_item(
            item_type="patient",
            data={"name": "John Doe", "age": 45},
            skill_used="patientsim"
        )
        
        assert isinstance(item, GeneratedItem)
        assert item.item_type == "patient"
        assert item.skill_used == "patientsim"
        assert session.generated_count == 1
    
    def test_context_management(self):
        """Test context key-value storage."""
        session = SessionState()
        
        session.set_context("current_patient", {"id": "P001"})
        session.set_context("location", "Austin, TX")
        
        assert session.get_context("current_patient") == {"id": "P001"}
        assert session.get_context("location") == "Austin, TX"
        assert session.get_context("missing", "default") == "default"
    
    def test_clear_session(self):
        """Test clearing session state."""
        session = SessionState()
        
        session.add_message("user", "Hello")
        session.add_generated_item("patient", {"id": "P001"})
        session.set_context("key", "value")
        
        session.clear()
        
        assert session.message_count == 0
        assert session.generated_count == 0
        assert session.context == {}
        # Session ID should be preserved
        assert session.session_id is not None
    
    def test_serialization(self):
        """Test session serialization to/from dict."""
        session = SessionState()
        session.add_message("user", "Test")
        session.add_generated_item("claim", {"amount": 100})
        
        data = session.to_dict()
        
        restored = SessionState.from_dict(data)
        
        assert restored.session_id == session.session_id
        assert restored.message_count == 1
        assert restored.generated_count == 1
    
    def test_get_items_by_type(self):
        """Test filtering generated items by type."""
        session = SessionState()
        
        session.add_generated_item("patient", {"id": "P001"})
        session.add_generated_item("claim", {"id": "C001"})
        session.add_generated_item("patient", {"id": "P002"})
        
        patients = session.get_items_by_type("patient")
        claims = session.get_items_by_type("claim")
        
        assert len(patients) == 2
        assert len(claims) == 1
