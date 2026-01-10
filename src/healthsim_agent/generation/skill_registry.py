"""Skill Registry for automatic skill resolution.

This module provides automatic mapping between clinical conditions/domains
and the skills that provide their clinical codes and parameters.
"""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


# =============================================================================
# Skill Capability Declarations
# =============================================================================

class SkillCapability(str, Enum):
    """What a skill can provide for event resolution."""
    
    DIAGNOSIS = "diagnosis"
    MEDICATION = "medication"
    LAB_ORDER = "lab_order"
    LAB_TEST = "lab_test"
    VITAL_SIGN = "vital_sign"
    PROCEDURE = "procedure"
    ENCOUNTER = "encounter"
    REFERRAL = "referral"


class SkillCapabilityDeclaration(BaseModel):
    """Declaration of what a skill provides."""
    
    capability: SkillCapability
    lookup_key: str = ""
    context_keys: list[str] = Field(default_factory=list)
    description: str = ""


class SkillRegistration(BaseModel):
    """A skill's registration in the registry."""
    
    skill_id: str
    skill_path: str = ""
    capabilities: list[SkillCapabilityDeclaration] = Field(default_factory=list)
    condition_mappings: dict[str, list[str]] = Field(default_factory=dict)
    products: list[str] = Field(default_factory=list)
    priority: int = 0


# =============================================================================
# Skill Registry
# =============================================================================

class SkillRegistry:
    """Registry mapping conditions to skills for auto-resolution."""
    
    def __init__(self) -> None:
        self._skills: dict[str, SkillRegistration] = {}
    
    @property
    def skills(self) -> dict[str, SkillRegistration]:
        """Get all registered skills."""
        return self._skills
    
    def register(self, registration: SkillRegistration) -> None:
        """Register a skill with its conditions and capabilities."""
        self._skills[registration.skill_id] = registration
    
    def get_skill(self, skill_id: str) -> SkillRegistration | None:
        """Get a skill registration by ID."""
        return self._skills.get(skill_id)
    
    def find_by_capability(
        self,
        capability: SkillCapability,
    ) -> list[SkillRegistration]:
        """Find skills that provide a specific capability."""
        result = []
        for skill in self._skills.values():
            for cap in skill.capabilities:
                if cap.capability == capability:
                    result.append(skill)
                    break
        return result
    
    def find_by_condition(
        self,
        condition: str,
    ) -> list[SkillRegistration]:
        """Find skills mapped to a specific condition."""
        normalized = self._normalize_condition(condition)
        result = []
        for skill in self._skills.values():
            for cond in skill.condition_mappings.keys():
                if self._normalize_condition(cond) == normalized:
                    result.append(skill)
                    break
        return result
    
    def find_skill_for_condition(
        self,
        condition: str,
        product: str | None = None,
    ) -> SkillRegistration | None:
        """Find the best skill for a given condition."""
        candidates = self.find_by_condition(condition)
        
        if product:
            candidates = [s for s in candidates if product in s.products]
        
        if not candidates:
            return None
        
        return max(candidates, key=lambda s: s.priority)
    
    def _normalize_condition(self, condition: str) -> str:
        """Normalize a condition string for matching."""
        return condition.lower().strip().replace("-", " ").replace("_", " ")


# =============================================================================
# Global Registry
# =============================================================================

_global_registry: SkillRegistry | None = None


def get_skill_registry() -> SkillRegistry:
    """Get the global skill registry singleton."""
    global _global_registry
    if _global_registry is None:
        _global_registry = SkillRegistry()
    return _global_registry


def register_skill(registration: SkillRegistration) -> None:
    """Register a skill in the global registry."""
    get_skill_registry().register(registration)


def auto_resolve_parameters(
    condition: str,
    capability: SkillCapability,
) -> dict[str, Any] | None:
    """Auto-resolve parameters for a condition and capability.
    
    Finds the best skill for the condition and returns the lookup
    for the requested capability.
    """
    registry = get_skill_registry()
    skill = registry.find_skill_for_condition(condition)
    
    if not skill:
        return None
    
    for cap in skill.capabilities:
        if cap.capability == capability:
            return {
                "skill_id": skill.skill_id,
                "lookup_key": cap.lookup_key,
                "context_keys": cap.context_keys,
            }
    
    return None


__all__ = [
    "SkillCapability",
    "SkillCapabilityDeclaration",
    "SkillRegistration",
    "SkillRegistry",
    "get_skill_registry",
    "auto_resolve_parameters",
    "register_skill",
]
