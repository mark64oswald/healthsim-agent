"""Person relationship management.

Provides classes for modeling relationships between persons.
"""

from datetime import date
from enum import Enum

from pydantic import BaseModel, Field


class RelationshipType(str, Enum):
    """Types of relationships between persons."""

    SPOUSE = "spouse"
    PARENT = "parent"
    CHILD = "child"
    SIBLING = "sibling"
    GUARDIAN = "guardian"
    DEPENDENT = "dependent"
    EMERGENCY_CONTACT = "emergency_contact"
    EMPLOYER = "employer"
    EMPLOYEE = "employee"
    OTHER = "other"


class Relationship(BaseModel):
    """A relationship between two persons."""

    source_person_id: str
    target_person_id: str
    relationship_type: RelationshipType
    start_date: date | None = None
    end_date: date | None = None
    is_active: bool = True
    notes: str | None = None

    @property
    def is_current(self) -> bool:
        """Check if the relationship is currently active."""
        if not self.is_active:
            return False
        if self.end_date and self.end_date <= date.today():
            return False
        return True

    def get_inverse_type(self) -> RelationshipType:
        """Get the inverse relationship type."""
        inverses = {
            RelationshipType.PARENT: RelationshipType.CHILD,
            RelationshipType.CHILD: RelationshipType.PARENT,
            RelationshipType.SPOUSE: RelationshipType.SPOUSE,
            RelationshipType.SIBLING: RelationshipType.SIBLING,
            RelationshipType.GUARDIAN: RelationshipType.DEPENDENT,
            RelationshipType.DEPENDENT: RelationshipType.GUARDIAN,
            RelationshipType.EMPLOYER: RelationshipType.EMPLOYEE,
            RelationshipType.EMPLOYEE: RelationshipType.EMPLOYER,
            RelationshipType.EMERGENCY_CONTACT: RelationshipType.OTHER,
            RelationshipType.OTHER: RelationshipType.OTHER,
        }
        return inverses.get(self.relationship_type, RelationshipType.OTHER)

    def create_inverse(self) -> "Relationship":
        """Create the inverse relationship."""
        return Relationship(
            source_person_id=self.target_person_id,
            target_person_id=self.source_person_id,
            relationship_type=self.get_inverse_type(),
            start_date=self.start_date,
            end_date=self.end_date,
            is_active=self.is_active,
            notes=self.notes,
        )


class RelationshipGraph(BaseModel):
    """Graph of relationships between persons."""

    relationships: list[Relationship] = Field(default_factory=list)

    def add_relationship(
        self,
        relationship: Relationship,
        create_inverse: bool = False,
    ) -> None:
        """Add a relationship to the graph."""
        self.relationships.append(relationship)
        if create_inverse:
            self.relationships.append(relationship.create_inverse())

    def get_relationships_for_person(
        self,
        person_id: str,
        active_only: bool = True,
    ) -> list[Relationship]:
        """Get all relationships for a person."""
        results = []
        for rel in self.relationships:
            if rel.source_person_id == person_id:
                if not active_only or rel.is_current:
                    results.append(rel)
        return results

    def get_related_persons(
        self,
        person_id: str,
        relationship_type: RelationshipType | None = None,
        active_only: bool = True,
    ) -> list[str]:
        """Get IDs of persons related to a given person."""
        related = []
        for rel in self.get_relationships_for_person(person_id, active_only):
            if relationship_type is None or rel.relationship_type == relationship_type:
                related.append(rel.target_person_id)
        return related

    def has_relationship(
        self,
        source_id: str,
        target_id: str,
        relationship_type: RelationshipType | None = None,
    ) -> bool:
        """Check if a relationship exists between two persons."""
        for rel in self.relationships:
            if rel.source_person_id == source_id and rel.target_person_id == target_id:
                if relationship_type is None or rel.relationship_type == relationship_type:
                    return True
        return False

    def remove_relationship(self, source_id: str, target_id: str) -> bool:
        """Remove a relationship between two persons."""
        for i, rel in enumerate(self.relationships):
            if rel.source_person_id == source_id and rel.target_person_id == target_id:
                del self.relationships[i]
                return True
        return False
