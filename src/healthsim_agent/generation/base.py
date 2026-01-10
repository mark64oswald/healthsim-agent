"""Base generator classes.

Provides the foundation for building data generators with
reproducibility and common generation utilities.

Ported from: healthsim-workspace/packages/core/src/healthsim/generation/base.py
"""

import uuid
from datetime import date, datetime, timedelta

from healthsim_agent.generation.distributions import WeightedChoice
from healthsim_agent.generation.reproducibility import SeedManager
from healthsim_agent.person.demographics import (
    Address,
    ContactInfo,
    Gender,
    Person,
    PersonName,
)
from healthsim_agent.temporal.utils import random_date_in_range


class BaseGenerator:
    """Base class for data generators."""

    def __init__(self, seed: int | None = None, locale: str = "en_US") -> None:
        self.seed_manager = SeedManager(seed=seed, locale=locale)
        self.faker = self.seed_manager.faker

    @property
    def rng(self):
        """Get the random number generator."""
        return self.seed_manager.rng

    def reset(self) -> None:
        """Reset the generator to initial seed state."""
        self.seed_manager.reset()
        self.faker = self.seed_manager.faker

    def generate_id(self, prefix: str = "") -> str:
        """Generate a unique identifier."""
        unique_part = uuid.uuid4().hex[:8].upper()
        if prefix:
            return f"{prefix}-{unique_part}"
        return unique_part

    def random_choice(self, options: list) -> any:
        """Select randomly from a list."""
        return self.seed_manager.get_random_choice(options)

    def random_int(self, min_val: int, max_val: int) -> int:
        """Generate random integer in range."""
        return self.seed_manager.get_random_int(min_val, max_val)

    def random_float(self, min_val: float = 0.0, max_val: float = 1.0) -> float:
        """Generate random float in range."""
        return self.seed_manager.get_random_float(min_val, max_val)

    def random_bool(self, probability: float = 0.5) -> bool:
        """Generate random boolean."""
        return self.seed_manager.get_random_bool(probability)

    def weighted_choice(self, options: list[tuple[any, float]]) -> any:
        """Select from weighted options."""
        wc = WeightedChoice(options=options)
        return wc.select(self.rng)

    def random_date_between(self, start: date, end: date) -> date:
        """Generate random date in range."""
        return random_date_in_range(start, end, self.rng)

    def random_datetime_between(self, start: datetime, end: datetime) -> datetime:
        """Generate random datetime in range."""
        delta = end - start
        random_seconds = self.rng.randint(0, int(delta.total_seconds()))
        return start + timedelta(seconds=random_seconds)


class PersonGenerator(BaseGenerator):
    """Generator for Person instances."""

    def generate_person(
        self,
        age_range: tuple[int, int] | None = None,
        gender: Gender | None = None,
        include_address: bool = True,
        include_contact: bool = True,
    ) -> Person:
        """Generate a random person."""
        if age_range is None:
            age_range = (18, 85)

        if gender is None:
            gender = self.random_choice([Gender.MALE, Gender.FEMALE])

        name = self.generate_name(gender)
        birth_date = self.generate_birth_date(age_range)
        address = self.generate_address() if include_address else None
        contact = self.generate_contact() if include_contact else None

        return Person(
            id=self.generate_id("PERSON"),
            name=name,
            birth_date=birth_date,
            gender=gender,
            address=address,
            contact=contact,
        )

    def generate_name(self, gender: Gender | None = None) -> PersonName:
        """Generate a random person name."""
        if gender == Gender.MALE:
            given_name = self.faker.first_name_male()
        elif gender == Gender.FEMALE:
            given_name = self.faker.first_name_female()
        else:
            given_name = self.faker.first_name()

        middle_name = self.faker.first_name() if self.random_bool(0.5) else None

        return PersonName(
            given_name=given_name,
            middle_name=middle_name,
            family_name=self.faker.last_name(),
        )

    def generate_birth_date(self, age_range: tuple[int, int]) -> date:
        """Generate a random birth date within age range."""
        min_age, max_age = age_range
        today = date.today()

        max_birth_date = today - timedelta(days=min_age * 365)
        min_birth_date = today - timedelta(days=max_age * 365)

        return self.random_date_between(min_birth_date, max_birth_date)

    def generate_address(self) -> Address:
        """Generate a random address."""
        return Address(
            street_address=self.faker.street_address(),
            city=self.faker.city(),
            state=self.faker.state_abbr(),
            postal_code=self.faker.postcode(),
            country="US",
        )

    def generate_contact(self) -> ContactInfo:
        """Generate random contact information."""
        return ContactInfo(
            phone=self.faker.phone_number(),
            phone_mobile=self.faker.phone_number() if self.random_bool(0.7) else None,
            email=self.faker.email(),
        )

    def generate_ssn(self) -> str:
        """Generate a random SSN-formatted string."""
        return self.faker.ssn()


__all__ = [
    "BaseGenerator",
    "PersonGenerator",
]
