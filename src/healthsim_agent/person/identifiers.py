"""Person identifier management.

Provides classes for managing various types of identifiers
associated with a person.
"""

from datetime import date
from enum import Enum

from pydantic import BaseModel, Field


class IdentifierType(str, Enum):
    """Types of identifiers."""

    SSN = "SSN"
    DRIVERS_LICENSE = "DL"
    PASSPORT = "PASSPORT"
    NATIONAL_ID = "NATIONAL_ID"
    TAX_ID = "TAX_ID"
    CUSTOM = "CUSTOM"


class Identifier(BaseModel):
    """An identifier for a person."""

    type: IdentifierType
    value: str
    system: str | None = None
    issuer: str | None = None
    issue_date: date | None = None
    expiry_date: date | None = None
    is_primary: bool = True

    @property
    def is_expired(self) -> bool:
        """Check if the identifier is expired."""
        if self.expiry_date is None:
            return False
        return date.today() > self.expiry_date

    @property
    def is_valid(self) -> bool:
        """Check if the identifier is currently valid."""
        today = date.today()

        if self.issue_date and self.issue_date > today:
            return False

        if self.expiry_date and self.expiry_date < today:
            return False

        return True


class IdentifierSet(BaseModel):
    """Collection of identifiers for a person."""

    identifiers: list[Identifier] = Field(default_factory=list)

    def add(self, identifier: Identifier) -> None:
        """Add an identifier to the set."""
        self.identifiers.append(identifier)

    def get_by_type(self, id_type: IdentifierType) -> Identifier | None:
        """Get the primary identifier of a specific type."""
        for identifier in self.identifiers:
            if identifier.type == id_type and identifier.is_primary:
                return identifier
        for identifier in self.identifiers:
            if identifier.type == id_type:
                return identifier
        return None

    def get_all_by_type(self, id_type: IdentifierType) -> list[Identifier]:
        """Get all identifiers of a specific type."""
        return [i for i in self.identifiers if i.type == id_type]

    def get_by_system(self, system: str) -> Identifier | None:
        """Get identifier by system/namespace."""
        for identifier in self.identifiers:
            if identifier.system == system:
                return identifier
        return None

    def __len__(self) -> int:
        """Return number of identifiers."""
        return len(self.identifiers)

    def __iter__(self):
        """Iterate over identifiers."""
        return iter(self.identifiers)
