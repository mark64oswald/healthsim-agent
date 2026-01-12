"""
Tests for person/relationships module.

Covers:
- RelationshipType enum
- Relationship model (is_current, get_inverse_type, create_inverse)
- RelationshipGraph collection operations
"""

import pytest
from datetime import date, timedelta


class TestRelationshipType:
    """Tests for RelationshipType enum."""
    
    def test_spouse_type(self):
        """Test SPOUSE relationship type."""
        from healthsim_agent.person.relationships import RelationshipType
        
        assert RelationshipType.SPOUSE == "spouse"
    
    def test_parent_child_types(self):
        """Test parent/child types."""
        from healthsim_agent.person.relationships import RelationshipType
        
        assert RelationshipType.PARENT == "parent"
        assert RelationshipType.CHILD == "child"
    
    def test_all_types_exist(self):
        """Test all expected relationship types exist."""
        from healthsim_agent.person.relationships import RelationshipType
        
        expected = ["SPOUSE", "PARENT", "CHILD", "SIBLING", "GUARDIAN", 
                   "DEPENDENT", "EMERGENCY_CONTACT", "EMPLOYER", "EMPLOYEE", "OTHER"]
        for name in expected:
            assert hasattr(RelationshipType, name)


class TestRelationship:
    """Tests for Relationship model."""
    
    def test_create_basic_relationship(self):
        """Test creating a basic relationship."""
        from healthsim_agent.person.relationships import Relationship, RelationshipType
        
        rel = Relationship(
            source_person_id="person-1",
            target_person_id="person-2",
            relationship_type=RelationshipType.SPOUSE
        )
        
        assert rel.source_person_id == "person-1"
        assert rel.target_person_id == "person-2"
        assert rel.relationship_type == RelationshipType.SPOUSE
        assert rel.is_active is True  # default
    
    def test_create_relationship_with_dates(self):
        """Test creating relationship with start/end dates."""
        from healthsim_agent.person.relationships import Relationship, RelationshipType
        
        start = date(2020, 1, 1)
        end = date(2023, 12, 31)
        
        rel = Relationship(
            source_person_id="person-1",
            target_person_id="person-2",
            relationship_type=RelationshipType.EMPLOYER,
            start_date=start,
            end_date=end
        )
        
        assert rel.start_date == start
        assert rel.end_date == end
    
    def test_is_current_active_no_end_date(self):
        """Test is_current returns True when active with no end date."""
        from healthsim_agent.person.relationships import Relationship, RelationshipType
        
        rel = Relationship(
            source_person_id="person-1",
            target_person_id="person-2",
            relationship_type=RelationshipType.SPOUSE,
            is_active=True
        )
        
        assert rel.is_current is True
    
    def test_is_current_inactive(self):
        """Test is_current returns False when inactive."""
        from healthsim_agent.person.relationships import Relationship, RelationshipType
        
        rel = Relationship(
            source_person_id="person-1",
            target_person_id="person-2",
            relationship_type=RelationshipType.SPOUSE,
            is_active=False
        )
        
        assert rel.is_current is False
    
    def test_is_current_ended(self):
        """Test is_current returns False when end date has passed."""
        from healthsim_agent.person.relationships import Relationship, RelationshipType
        
        past = date.today() - timedelta(days=1)
        rel = Relationship(
            source_person_id="person-1",
            target_person_id="person-2",
            relationship_type=RelationshipType.EMPLOYER,
            is_active=True,
            end_date=past
        )
        
        assert rel.is_current is False
    
    def test_is_current_future_end_date(self):
        """Test is_current returns True when end date is future."""
        from healthsim_agent.person.relationships import Relationship, RelationshipType
        
        future = date.today() + timedelta(days=365)
        rel = Relationship(
            source_person_id="person-1",
            target_person_id="person-2",
            relationship_type=RelationshipType.EMPLOYER,
            is_active=True,
            end_date=future
        )
        
        assert rel.is_current is True
    
    def test_get_inverse_type_parent_child(self):
        """Test inverse of parent is child."""
        from healthsim_agent.person.relationships import Relationship, RelationshipType
        
        rel = Relationship(
            source_person_id="parent-1",
            target_person_id="child-1",
            relationship_type=RelationshipType.PARENT
        )
        
        assert rel.get_inverse_type() == RelationshipType.CHILD
    
    def test_get_inverse_type_child_parent(self):
        """Test inverse of child is parent."""
        from healthsim_agent.person.relationships import Relationship, RelationshipType
        
        rel = Relationship(
            source_person_id="child-1",
            target_person_id="parent-1",
            relationship_type=RelationshipType.CHILD
        )
        
        assert rel.get_inverse_type() == RelationshipType.PARENT
    
    def test_get_inverse_type_spouse_symmetric(self):
        """Test spouse is symmetric."""
        from healthsim_agent.person.relationships import Relationship, RelationshipType
        
        rel = Relationship(
            source_person_id="person-1",
            target_person_id="person-2",
            relationship_type=RelationshipType.SPOUSE
        )
        
        assert rel.get_inverse_type() == RelationshipType.SPOUSE
    
    def test_get_inverse_type_sibling_symmetric(self):
        """Test sibling is symmetric."""
        from healthsim_agent.person.relationships import Relationship, RelationshipType
        
        rel = Relationship(
            source_person_id="person-1",
            target_person_id="person-2",
            relationship_type=RelationshipType.SIBLING
        )
        
        assert rel.get_inverse_type() == RelationshipType.SIBLING
    
    def test_get_inverse_type_guardian_dependent(self):
        """Test guardian/dependent inverse."""
        from healthsim_agent.person.relationships import Relationship, RelationshipType
        
        rel = Relationship(
            source_person_id="guardian-1",
            target_person_id="minor-1",
            relationship_type=RelationshipType.GUARDIAN
        )
        
        assert rel.get_inverse_type() == RelationshipType.DEPENDENT
    
    def test_get_inverse_type_employer_employee(self):
        """Test employer/employee inverse."""
        from healthsim_agent.person.relationships import Relationship, RelationshipType
        
        rel = Relationship(
            source_person_id="company-1",
            target_person_id="employee-1",
            relationship_type=RelationshipType.EMPLOYER
        )
        
        assert rel.get_inverse_type() == RelationshipType.EMPLOYEE
    
    def test_get_inverse_type_emergency_contact(self):
        """Test emergency contact inverse is OTHER."""
        from healthsim_agent.person.relationships import Relationship, RelationshipType
        
        rel = Relationship(
            source_person_id="person-1",
            target_person_id="contact-1",
            relationship_type=RelationshipType.EMERGENCY_CONTACT
        )
        
        assert rel.get_inverse_type() == RelationshipType.OTHER
    
    def test_create_inverse(self):
        """Test create_inverse creates correct inverse relationship."""
        from healthsim_agent.person.relationships import Relationship, RelationshipType
        
        start = date(2020, 1, 1)
        
        rel = Relationship(
            source_person_id="parent-1",
            target_person_id="child-1",
            relationship_type=RelationshipType.PARENT,
            start_date=start,
            notes="Birth parent"
        )
        
        inverse = rel.create_inverse()
        
        assert inverse.source_person_id == "child-1"
        assert inverse.target_person_id == "parent-1"
        assert inverse.relationship_type == RelationshipType.CHILD
        assert inverse.start_date == start
        assert inverse.notes == "Birth parent"


class TestRelationshipGraph:
    """Tests for RelationshipGraph collection."""
    
    def test_create_empty_graph(self):
        """Test creating an empty relationship graph."""
        from healthsim_agent.person.relationships import RelationshipGraph
        
        graph = RelationshipGraph()
        
        assert len(graph.relationships) == 0
    
    def test_add_relationship(self):
        """Test adding a relationship to the graph."""
        from healthsim_agent.person.relationships import (
            RelationshipGraph, Relationship, RelationshipType
        )
        
        graph = RelationshipGraph()
        rel = Relationship(
            source_person_id="person-1",
            target_person_id="person-2",
            relationship_type=RelationshipType.SPOUSE
        )
        
        graph.add_relationship(rel)
        
        assert len(graph.relationships) == 1
    
    def test_add_relationship_with_inverse(self):
        """Test adding relationship with automatic inverse."""
        from healthsim_agent.person.relationships import (
            RelationshipGraph, Relationship, RelationshipType
        )
        
        graph = RelationshipGraph()
        rel = Relationship(
            source_person_id="parent-1",
            target_person_id="child-1",
            relationship_type=RelationshipType.PARENT
        )
        
        graph.add_relationship(rel, create_inverse=True)
        
        assert len(graph.relationships) == 2
        # Check inverse was created
        inverse = graph.relationships[1]
        assert inverse.source_person_id == "child-1"
        assert inverse.target_person_id == "parent-1"
        assert inverse.relationship_type == RelationshipType.CHILD
    
    def test_get_relationships_for_person(self):
        """Test getting relationships for a person."""
        from healthsim_agent.person.relationships import (
            RelationshipGraph, Relationship, RelationshipType
        )
        
        graph = RelationshipGraph()
        graph.add_relationship(Relationship(
            source_person_id="person-1",
            target_person_id="spouse-1",
            relationship_type=RelationshipType.SPOUSE
        ))
        graph.add_relationship(Relationship(
            source_person_id="person-1",
            target_person_id="child-1",
            relationship_type=RelationshipType.PARENT
        ))
        graph.add_relationship(Relationship(
            source_person_id="other-1",
            target_person_id="person-1",
            relationship_type=RelationshipType.SIBLING
        ))
        
        results = graph.get_relationships_for_person("person-1")
        
        assert len(results) == 2  # Only where person-1 is source
    
    def test_get_relationships_for_person_active_only(self):
        """Test filtering by active relationships."""
        from healthsim_agent.person.relationships import (
            RelationshipGraph, Relationship, RelationshipType
        )
        
        graph = RelationshipGraph()
        graph.add_relationship(Relationship(
            source_person_id="person-1",
            target_person_id="employer-1",
            relationship_type=RelationshipType.EMPLOYEE,
            is_active=True
        ))
        graph.add_relationship(Relationship(
            source_person_id="person-1",
            target_person_id="employer-2",
            relationship_type=RelationshipType.EMPLOYEE,
            is_active=False
        ))
        
        active = graph.get_relationships_for_person("person-1", active_only=True)
        all_rels = graph.get_relationships_for_person("person-1", active_only=False)
        
        assert len(active) == 1
        assert len(all_rels) == 2
    
    def test_get_related_persons(self):
        """Test getting related person IDs."""
        from healthsim_agent.person.relationships import (
            RelationshipGraph, Relationship, RelationshipType
        )
        
        graph = RelationshipGraph()
        graph.add_relationship(Relationship(
            source_person_id="person-1",
            target_person_id="spouse-1",
            relationship_type=RelationshipType.SPOUSE
        ))
        graph.add_relationship(Relationship(
            source_person_id="person-1",
            target_person_id="child-1",
            relationship_type=RelationshipType.PARENT
        ))
        
        related = graph.get_related_persons("person-1")
        
        assert set(related) == {"spouse-1", "child-1"}
    
    def test_get_related_persons_by_type(self):
        """Test filtering related persons by relationship type."""
        from healthsim_agent.person.relationships import (
            RelationshipGraph, Relationship, RelationshipType
        )
        
        graph = RelationshipGraph()
        graph.add_relationship(Relationship(
            source_person_id="person-1",
            target_person_id="child-1",
            relationship_type=RelationshipType.PARENT
        ))
        graph.add_relationship(Relationship(
            source_person_id="person-1",
            target_person_id="child-2",
            relationship_type=RelationshipType.PARENT
        ))
        graph.add_relationship(Relationship(
            source_person_id="person-1",
            target_person_id="spouse-1",
            relationship_type=RelationshipType.SPOUSE
        ))
        
        children = graph.get_related_persons("person-1", RelationshipType.PARENT)
        
        assert set(children) == {"child-1", "child-2"}
    
    def test_has_relationship_true(self):
        """Test has_relationship returns True when exists."""
        from healthsim_agent.person.relationships import (
            RelationshipGraph, Relationship, RelationshipType
        )
        
        graph = RelationshipGraph()
        graph.add_relationship(Relationship(
            source_person_id="person-1",
            target_person_id="person-2",
            relationship_type=RelationshipType.SPOUSE
        ))
        
        assert graph.has_relationship("person-1", "person-2") is True
    
    def test_has_relationship_false(self):
        """Test has_relationship returns False when not exists."""
        from healthsim_agent.person.relationships import (
            RelationshipGraph, Relationship, RelationshipType
        )
        
        graph = RelationshipGraph()
        graph.add_relationship(Relationship(
            source_person_id="person-1",
            target_person_id="person-2",
            relationship_type=RelationshipType.SPOUSE
        ))
        
        # Wrong direction
        assert graph.has_relationship("person-2", "person-1") is False
        # Different target
        assert graph.has_relationship("person-1", "person-3") is False
    
    def test_has_relationship_with_type(self):
        """Test has_relationship with type filter."""
        from healthsim_agent.person.relationships import (
            RelationshipGraph, Relationship, RelationshipType
        )
        
        graph = RelationshipGraph()
        graph.add_relationship(Relationship(
            source_person_id="person-1",
            target_person_id="person-2",
            relationship_type=RelationshipType.SIBLING
        ))
        
        assert graph.has_relationship("person-1", "person-2", RelationshipType.SIBLING) is True
        assert graph.has_relationship("person-1", "person-2", RelationshipType.SPOUSE) is False
    
    def test_remove_relationship_success(self):
        """Test removing an existing relationship."""
        from healthsim_agent.person.relationships import (
            RelationshipGraph, Relationship, RelationshipType
        )
        
        graph = RelationshipGraph()
        graph.add_relationship(Relationship(
            source_person_id="person-1",
            target_person_id="person-2",
            relationship_type=RelationshipType.SPOUSE
        ))
        
        result = graph.remove_relationship("person-1", "person-2")
        
        assert result is True
        assert len(graph.relationships) == 0
    
    def test_remove_relationship_not_found(self):
        """Test removing a non-existent relationship."""
        from healthsim_agent.person.relationships import (
            RelationshipGraph, Relationship, RelationshipType
        )
        
        graph = RelationshipGraph()
        
        result = graph.remove_relationship("person-1", "person-2")
        
        assert result is False
    
    def test_create_with_initial_relationships(self):
        """Test creating graph with initial relationships."""
        from healthsim_agent.person.relationships import (
            RelationshipGraph, Relationship, RelationshipType
        )
        
        relationships = [
            Relationship(
                source_person_id="person-1",
                target_person_id="spouse-1",
                relationship_type=RelationshipType.SPOUSE
            ),
            Relationship(
                source_person_id="person-1",
                target_person_id="child-1",
                relationship_type=RelationshipType.PARENT
            ),
        ]
        
        graph = RelationshipGraph(relationships=relationships)
        
        assert len(graph.relationships) == 2
