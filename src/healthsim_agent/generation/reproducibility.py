"""Seed management for reproducible generation.

Provides utilities for managing random seeds to ensure reproducibility
across generation runs.

Ported from: healthsim-workspace/packages/core/src/healthsim/generation/reproducibility.py
"""

import random
from typing import Any

from faker import Faker


class SeedManager:
    """Manages random seeds for reproducible data generation."""

    def __init__(self, seed: int | None = None, locale: str = "en_US") -> None:
        self.seed = seed
        self.locale = locale
        self.rng = random.Random(seed)
        self.faker = Faker(locale)

        if seed is not None:
            Faker.seed(seed)
            self.faker.seed_instance(seed)

    def reset(self) -> None:
        """Reset the random state to the original seed."""
        if self.seed is not None:
            self.rng = random.Random(self.seed)
            Faker.seed(self.seed)
            self.faker = Faker(self.locale)
            self.faker.seed_instance(self.seed)

    def get_child_seed(self) -> int:
        """Get a deterministic child seed for sub-generators."""
        return self.rng.randint(0, 2**31 - 1)

    def get_random_int(self, min_val: int, max_val: int) -> int:
        """Get a random integer in range."""
        return self.rng.randint(min_val, max_val)

    def get_random_float(self, min_val: float = 0.0, max_val: float = 1.0) -> float:
        """Get a random float in range."""
        return self.rng.uniform(min_val, max_val)

    def get_random_choice(self, options: list[Any]) -> Any:
        """Get a random choice from a list."""
        return self.rng.choice(options)

    def get_random_sample(self, options: list[Any], k: int) -> list[Any]:
        """Get a random sample from a list."""
        return self.rng.sample(options, min(k, len(options)))

    def shuffle(self, items: list[Any]) -> list[Any]:
        """Shuffle a list in place and return it."""
        self.rng.shuffle(items)
        return items

    def get_random_bool(self, probability: float = 0.5) -> bool:
        """Get a random boolean with given probability of True."""
        return self.rng.random() < probability


__all__ = ["SeedManager"]
