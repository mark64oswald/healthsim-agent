"""Person demographics models.

Provides models for representing person demographics including
name, address, contact information, and core attributes.
"""

from datetime import date
from enum import Enum

from pydantic import BaseModel, Field, field_validator, model_validator

from healthsim_agent.temporal.utils import calculate_age


class Gender(str, Enum):
    """Gender representation."""

    MALE = "M"
    FEMALE = "F"
    OTHER = "O"
    UNKNOWN = "U"


class PersonName(BaseModel):
    """Name components for a person."""

    given_name: str
    middle_name: str | None = None
    family_name: str
    suffix: str | None = None
    prefix: str | None = None

    @property
    def full_name(self) -> str:
        """Get the complete formatted name."""
        parts = []
        if self.prefix:
            parts.append(self.prefix)
        parts.append(self.given_name)
        if self.middle_name:
            parts.append(self.middle_name)
        parts.append(self.family_name)
        if self.suffix:
            parts.append(self.suffix)
        return " ".join(parts)

    @property
    def formal_name(self) -> str:
        """Get formal name (Family, Given)."""
        return f"{self.family_name}, {self.given_name}"


class Address(BaseModel):
    """Physical address."""

    street_address: str | None = None
    street_address_2: str | None = None
    city: str | None = None
    state: str | None = None
    postal_code: str | None = None
    country: str = "US"

    @property
    def one_line(self) -> str:
        """Get address as a single line."""
        parts = []
        if self.street_address:
            parts.append(self.street_address)
        if self.street_address_2:
            parts.append(self.street_address_2)
        if self.city:
            parts.append(self.city)
        if self.state and self.postal_code:
            parts.append(f"{self.state} {self.postal_code}")
        elif self.state:
            parts.append(self.state)
        elif self.postal_code:
            parts.append(self.postal_code)
        return ", ".join(parts)


class ContactInfo(BaseModel):
    """Contact information for a person."""

    phone: str | None = None
    phone_mobile: str | None = None
    phone_work: str | None = None
    email: str | None = None
    email_work: str | None = None

    @property
    def primary_phone(self) -> str | None:
        """Get primary phone (mobile > phone > work)."""
        return self.phone_mobile or self.phone or self.phone_work

    @property
    def primary_email(self) -> str | None:
        """Get primary email (personal > work)."""
        return self.email or self.email_work


class Person(BaseModel):
    """Base person model with demographics.

    This is the foundational model for representing a person in HealthSim.
    Products should extend this class to add domain-specific fields.
    """

    id: str = Field(..., description="Unique identifier")
    name: PersonName
    birth_date: date
    gender: Gender
    address: Address | None = None
    contact: ContactInfo | None = None
    deceased: bool = False
    death_date: date | None = None

    @field_validator("birth_date")
    @classmethod
    def birth_date_not_future(cls, v: date) -> date:
        """Ensure birth date is not in the future."""
        if v > date.today():
            raise ValueError("birth_date cannot be in the future")
        return v

    @model_validator(mode="after")
    def validate_death_date(self) -> "Person":
        """Validate death date consistency."""
        if self.death_date:
            if not self.deceased:
                raise ValueError("death_date set but deceased is False")
            if self.death_date < self.birth_date:
                raise ValueError("death_date cannot be before birth_date")
            if self.death_date > date.today():
                raise ValueError("death_date cannot be in the future")
        return self

    @property
    def age(self) -> int:
        """Calculate current age in years."""
        as_of = self.death_date if self.deceased and self.death_date else date.today()
        return calculate_age(self.birth_date, as_of)

    @property
    def full_name(self) -> str:
        """Get the person's full name."""
        return self.name.full_name

    @property
    def given_name(self) -> str:
        """Get the person's given/first name."""
        return self.name.given_name

    @property
    def family_name(self) -> str:
        """Get the person's family/last name."""
        return self.name.family_name
