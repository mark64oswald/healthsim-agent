"""Person models for HealthSim.

Provides base person models with demographics, identifiers, and relationships.
These are foundational models that products extend.
"""

from healthsim_agent.person.demographics import (
    Address,
    ContactInfo,
    Gender,
    Person,
    PersonName,
)
from healthsim_agent.person.identifiers import (
    Identifier,
    IdentifierSet,
    IdentifierType,
)
from healthsim_agent.person.relationships import (
    Relationship,
    RelationshipGraph,
    RelationshipType,
)

__all__ = [
    # Demographics
    "Address",
    "ContactInfo",
    "Gender",
    "Person",
    "PersonName",
    # Identifiers
    "Identifier",
    "IdentifierSet",
    "IdentifierType",
    # Relationships
    "Relationship",
    "RelationshipGraph",
    "RelationshipType",
]
