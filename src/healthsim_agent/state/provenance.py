"""Provenance tracking for entity lineage.

Tracks how entities were created across all HealthSim products.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from healthsim_agent.state.entity import EntityWithProvenance


class SourceType(str, Enum):
    """How an entity was created."""

    LOADED = "loaded"
    GENERATED = "generated"
    DERIVED = "derived"


class Provenance(BaseModel):
    """Tracks how an entity was created."""

    source_type: SourceType
    source_system: str | None = None
    skill_used: str | None = None
    derived_from: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    generation_params: dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def generated(cls, skill_used: str | None = None, **params: Any) -> Provenance:
        """Create provenance for a generated entity."""
        return cls(
            source_type=SourceType.GENERATED,
            skill_used=skill_used,
            generation_params=params,
        )

    @classmethod
    def loaded(cls, source_system: str) -> Provenance:
        """Create provenance for a loaded entity."""
        return cls(source_type=SourceType.LOADED, source_system=source_system)

    @classmethod
    def derived(cls, derived_from: list[str]) -> Provenance:
        """Create provenance for a derived entity."""
        return cls(source_type=SourceType.DERIVED, derived_from=derived_from)


class ProvenanceSummary(BaseModel):
    """Aggregate provenance statistics for a workspace."""

    total_entities: int = 0
    by_source_type: dict[str, int] = Field(default_factory=dict)
    source_systems: list[str] = Field(default_factory=list)
    skills_used: list[str] = Field(default_factory=list)

    @classmethod
    def from_entities(cls, entities: dict[str, list[EntityWithProvenance]]) -> ProvenanceSummary:
        """Build summary from entity collections."""
        from healthsim_agent.state.entity import EntityWithProvenance

        total = 0
        by_type: dict[str, int] = {}
        systems: set[str] = set()
        skills: set[str] = set()

        for entity_list in entities.values():
            for entity in entity_list:
                if not isinstance(entity, EntityWithProvenance):
                    continue
                total += 1
                source = entity.provenance.source_type.value
                by_type[source] = by_type.get(source, 0) + 1
                if entity.provenance.source_system:
                    systems.add(entity.provenance.source_system)
                if entity.provenance.skill_used:
                    skills.add(entity.provenance.skill_used)

        return cls(
            total_entities=total,
            by_source_type=by_type,
            source_systems=sorted(systems),
            skills_used=sorted(skills),
        )
