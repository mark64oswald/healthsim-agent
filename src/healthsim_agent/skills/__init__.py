"""Skills integration for HealthSim Agent.

This module provides the skill loading and routing system for the
hybrid skill format:

- SkillLoader: Parses markdown skills with YAML frontmatter and embedded configs
- SkillRouter: Matches user intent to relevant skills
- ParsedSkill: Represents a fully parsed skill
- SkillIndex: Index for efficient skill lookup

Example:
    >>> from healthsim_agent.skills import SkillLoader, SkillRouter
    >>> 
    >>> loader = SkillLoader()
    >>> print(f"Loaded {loader.index.skill_count} skills")
    >>> 
    >>> router = SkillRouter(loader)
    >>> result = router.route("Generate a diabetic patient")
    >>> print(f"Matched: {len(result.matched_skills)} skills")
"""
from .loader import SkillLoader
from .router import SkillRouter, RoutingResult
from .models import (
    ParsedSkill,
    SkillMetadata,
    EmbeddedConfig,
    SkillIndex,
)
from .schema import (
    SkillType,
    ParameterType,
    SkillMetadata as SchemaSkillMetadata,
    SkillParameter,
    SkillVariation,
    Skill,
)

__all__ = [
    # Main classes
    "SkillLoader",
    "SkillRouter",
    "RoutingResult",
    # Data models
    "ParsedSkill",
    "SkillMetadata",
    "EmbeddedConfig",
    "SkillIndex",
    # Schema (Pydantic models)
    "SkillType",
    "ParameterType",
    "SchemaSkillMetadata",
    "SkillParameter",
    "SkillVariation",
    "Skill",
]
