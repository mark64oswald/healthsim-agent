"""Base transformer classes for format conversion.

Ported from: healthsim-workspace/packages/core/src/healthsim/formats/base.py
"""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T = TypeVar("T")  # Input type
R = TypeVar("R")  # Output type


class BaseTransformer(ABC, Generic[T, R]):
    """Abstract base class for format transformers."""

    @abstractmethod
    def transform(self, source: T) -> R:
        """Transform a single source object."""
        ...

    def transform_batch(self, sources: list[T]) -> list[R]:
        """Transform multiple source objects."""
        return [self.transform(s) for s in sources]

    def can_transform(self, source: T) -> bool:
        """Check if source can be transformed."""
        return True


class BidirectionalTransformer(ABC, Generic[T, R]):
    """Transformer that can convert in both directions."""

    @abstractmethod
    def forward(self, source: T) -> R:
        """Transform from T to R."""
        ...

    @abstractmethod
    def reverse(self, source: R) -> T:
        """Transform from R to T."""
        ...


class ChainedTransformer(BaseTransformer[T, R]):
    """Transformer that chains multiple transformers together."""

    def __init__(self, transformers: list[BaseTransformer]) -> None:
        if not transformers:
            raise ValueError("Must provide at least one transformer")
        self.transformers = transformers

    def transform(self, source: T) -> R:
        """Transform by applying each transformer in sequence."""
        result = source
        for transformer in self.transformers:
            result = transformer.transform(result)
        return result


__all__ = [
    "BaseTransformer",
    "BidirectionalTransformer",
    "ChainedTransformer",
]
