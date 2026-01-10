"""Skill reference system for journey events.

This module enables journey templates to reference skills for parameter
values instead of hardcoding clinical codes.

Ported from: healthsim-workspace/packages/core/src/healthsim/generation/skill_reference.py
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from healthsim_agent.skills.loader import SkillLoader
from healthsim_agent.skills.models import ParsedSkill


# =============================================================================
# Skill Reference Schema
# =============================================================================

class SkillReference(BaseModel):
    """Reference to a skill for parameter resolution."""
    
    skill: str = Field(..., description="Skill name to reference")
    lookup: str = Field(..., description="What to look up in the skill")
    context: dict[str, Any] = Field(default_factory=dict, description="Context for resolution")
    fallback: Any = Field(default=None, description="Fallback if lookup fails")


class ResolvedParameters(BaseModel):
    """Result of resolving skill references in parameters."""
    
    parameters: dict[str, Any] = Field(default_factory=dict)
    skill_used: str | None = None
    lookup_path: str | None = None
    resolved_from: str = "direct"


# =============================================================================
# Skills Directory Configuration
# =============================================================================

def get_skills_root() -> Path:
    """Get the root directory for skills."""
    import os
    
    if env_path := os.environ.get("HEALTHSIM_SKILLS_PATH"):
        return Path(env_path)
    
    current = Path.cwd()
    for parent in [current] + list(current.parents):
        if (parent / "pyproject.toml").exists() and (parent / "skills").exists():
            return parent / "skills"
    
    return current / "skills"


# =============================================================================
# Skill Resolver
# =============================================================================

class SkillResolver:
    """Resolves skill references to concrete parameter values."""
    
    LOOKUP_MAPPINGS = {
        "diagnosis_code": {
            "sections": ["conditions", "generation rules"],
            "pattern": r"(E\d{2}\.\d+)\s*[-–]\s*(.+)",
            "fields": ["icd10", "description"],
        },
        "diagnosis_by_stage": {
            "sections": ["disease progression stages"],
            "context_key": "stage",
        },
        "medication": {
            "sections": ["medication patterns", "medications"],
            "json_key": "code",
            "fields": ["rxnorm", "name", "dose", "frequency"],
        },
        "first_line_medication": {
            "sections": ["medication patterns"],
            "subsection": "first-line therapy",
        },
        "lab_order": {
            "sections": ["lab patterns by control status"],
            "context_key": "control_status",
            "fields": ["loinc", "test_name", "range"],
        },
        "icd10": {
            "sections": ["conditions", "comorbidities"],
            "pattern": r"(E\d{2}\.\d+|I\d{2}(?:\.\d+)?|N\d{2}\.\d+)",
        },
        "loinc": {
            "sections": ["labs", "lab patterns"],
            "pattern": r"(\d{4,5}-\d)",
        },
        "rxnorm": {
            "sections": ["medications", "medication patterns"],
            "pattern": r'"code":\s*"(\d+)"',
        },
    }
    
    def __init__(self, skills_root: Path | None = None):
        self.skills_root = skills_root or get_skills_root()
        self.loader = SkillLoader(self.skills_root)
        self._cache: dict[str, ParsedSkill] = {}
    
    def load_skill(self, skill_name: str) -> ParsedSkill | None:
        """Load a skill by name."""
        if skill_name in self._cache:
            return self._cache[skill_name]
        
        skill_path = self._find_skill_file(skill_name)
        if not skill_path:
            return None
        
        try:
            skill = self.loader.load_skill(skill_path)
            if skill:
                self._cache[skill_name] = skill
            return skill
        except Exception:
            return None
    
    def _find_skill_file(self, skill_name: str) -> Path | None:
        """Find skill file by name."""
        normalized = skill_name.lower().replace("_", "-")
        
        for product in ["patientsim", "membersim", "rxmembersim", "trialsim", "common", "networksim", "populationsim"]:
            path = self.skills_root / product / f"{normalized}.md"
            if path.exists():
                return path
        
        for md_file in self.skills_root.rglob("*.md"):
            if md_file.stem.lower() == normalized:
                return md_file
        
        return None
    
    def resolve(
        self,
        ref: SkillReference,
        entity_context: dict[str, Any] | None = None,
    ) -> ResolvedParameters:
        """Resolve a skill reference to concrete parameters."""
        skill = self.load_skill(ref.skill)
        if not skill:
            return ResolvedParameters(
                parameters={"value": ref.fallback} if ref.fallback else {},
                resolved_from="fallback",
            )
        
        resolved_context = self._resolve_context(ref.context, entity_context or {})
        result = self._lookup_value(skill, ref.lookup, resolved_context)
        
        if result:
            return ResolvedParameters(
                parameters=result,
                skill_used=ref.skill,
                lookup_path=ref.lookup,
                resolved_from="skill",
            )
        
        return ResolvedParameters(
            parameters={"value": ref.fallback} if ref.fallback else {},
            resolved_from="fallback",
        )
    
    def _resolve_context(
        self,
        context: dict[str, Any],
        entity_context: dict[str, Any],
    ) -> dict[str, Any]:
        """Resolve ${entity.x} references in context."""
        resolved = {}
        
        for key, value in context.items():
            if isinstance(value, str) and value.startswith("${entity."):
                attr_name = value[9:-1]
                resolved[key] = entity_context.get(attr_name, value)
            else:
                resolved[key] = value
        
        return resolved
    
    def _lookup_value(
        self,
        skill: ParsedSkill,
        lookup: str,
        context: dict[str, Any],
    ) -> dict[str, Any] | None:
        """Look up a value in the skill."""
        mapping = self.LOOKUP_MAPPINGS.get(lookup)
        
        if not mapping:
            return self._direct_lookup(skill, lookup, context)
        
        sections = mapping.get("sections", [])
        content = self._get_sections_content(skill, sections)
        
        if not content:
            return None
        
        if context_key := mapping.get("context_key"):
            context_value = context.get(context_key, "").lower().replace("_", "-")
            return self._context_lookup(content, context_value, mapping)
        
        if pattern := mapping.get("pattern"):
            return self._pattern_lookup(content, pattern, mapping.get("fields"))
        
        if json_key := mapping.get("json_key"):
            return self._json_lookup(content, json_key)
        
        return None
    
    def _direct_lookup(
        self,
        skill: ParsedSkill,
        lookup: str,
        context: dict[str, Any],
    ) -> dict[str, Any] | None:
        """Direct lookup in skill content."""
        # Check embedded configs
        for config in skill.embedded_configs:
            if lookup in config.data:
                return {"value": config.data[lookup]}
        
        return None
    
    def _get_sections_content(self, skill: ParsedSkill, sections: list[str]) -> str:
        """Get combined content from specified sections."""
        content_parts = []
        
        # Check embedded configs for matching sections
        for config in skill.embedded_configs:
            section_name = config.section_name.lower()
            for target_section in sections:
                if target_section.lower() in section_name:
                    import json
                    content_parts.append(json.dumps(config.data))
        
        # Include raw markdown if no structured content found
        if not content_parts:
            content_parts.append(skill.markdown_content)
        
        return "\n".join(content_parts)
    
    def _context_lookup(
        self,
        content: str,
        context_value: str,
        mapping: dict,
    ) -> dict[str, Any] | None:
        """Look up based on context value."""
        section_pattern = rf"###\s*{re.escape(context_value)}.*?\n(.*?)(?=###|\Z)"
        match = re.search(section_pattern, content, re.IGNORECASE | re.DOTALL)
        
        if match:
            section_content = match.group(1)
            json_match = re.search(r"\{[^}]+\}", section_content, re.DOTALL)
            if json_match:
                import json
                try:
                    return json.loads(json_match.group())
                except json.JSONDecodeError:
                    pass
        
        return None
    
    def _pattern_lookup(
        self,
        content: str,
        pattern: str,
        fields: list[str] | None,
    ) -> dict[str, Any] | None:
        """Look up using regex pattern."""
        match = re.search(pattern, content)
        if match:
            groups = match.groups()
            if fields and len(groups) >= len(fields):
                return dict(zip(fields, groups))
            return {"value": groups[0] if groups else match.group()}
        return None
    
    def _json_lookup(self, content: str, json_key: str) -> dict[str, Any] | None:
        """Look up a key from JSON in content."""
        import json
        
        json_pattern = r"```json\s*([\s\S]*?)```"
        for match in re.finditer(json_pattern, content):
            try:
                data = json.loads(match.group(1))
                if isinstance(data, dict) and json_key in data:
                    return data
            except json.JSONDecodeError:
                continue
        
        return None
    
    def list_skills(self) -> list[str]:
        """List available skills."""
        skills = []
        if self.skills_root.exists():
            for md_file in self.skills_root.rglob("*.md"):
                if md_file.stem not in ("README", "SKILL"):
                    skills.append(md_file.stem)
        return sorted(set(skills))


# =============================================================================
# Parameter Resolver for Journey Events
# =============================================================================

class ParameterResolver:
    """Resolves parameters in journey events, handling skill references."""
    
    def __init__(self, skill_resolver: SkillResolver | None = None):
        self.skill_resolver = skill_resolver or SkillResolver()
    
    def resolve_event_parameters(
        self,
        parameters: dict[str, Any],
        entity: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Resolve all parameters for an event."""
        entity = entity or {}
        resolved = {}
        
        for key, value in parameters.items():
            if key == "skill_ref":
                ref = SkillReference.model_validate(value) if isinstance(value, dict) else value
                result = self.skill_resolver.resolve(ref, entity)
                resolved.update(result.parameters)
            elif isinstance(value, str) and "${entity." in value:
                resolved[key] = self._resolve_entity_var(value, entity)
            elif isinstance(value, dict):
                resolved[key] = self.resolve_event_parameters(value, entity)
            else:
                resolved[key] = value
        
        return resolved
    
    def _resolve_entity_var(self, value: str, entity: dict[str, Any]) -> Any:
        """Resolve ${entity.x} variables."""
        pattern = r"\$\{entity\.(\w+)\}"
        
        def replacer(match):
            attr = match.group(1)
            return str(entity.get(attr, match.group(0)))
        
        result = re.sub(pattern, replacer, value)
        
        if value.startswith("${entity.") and value.endswith("}"):
            attr = value[9:-1]
            return entity.get(attr, value)
        
        return result


# =============================================================================
# Convenience Functions
# =============================================================================

_default_skill_resolver: SkillResolver | None = None
_default_parameter_resolver: ParameterResolver | None = None


def get_skill_resolver() -> SkillResolver:
    """Get the default skill resolver (singleton)."""
    global _default_skill_resolver
    if _default_skill_resolver is None:
        _default_skill_resolver = SkillResolver()
    return _default_skill_resolver


def get_parameter_resolver() -> ParameterResolver:
    """Get the default parameter resolver (singleton)."""
    global _default_parameter_resolver
    if _default_parameter_resolver is None:
        _default_parameter_resolver = ParameterResolver(get_skill_resolver())
    return _default_parameter_resolver


def resolve_skill_ref(
    skill: str,
    lookup: str,
    context: dict[str, Any] | None = None,
    entity: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Convenience function to resolve a skill reference."""
    ref = SkillReference(skill=skill, lookup=lookup, context=context or {})
    result = get_skill_resolver().resolve(ref, entity)
    return result.parameters


__all__ = [
    "SkillReference",
    "ResolvedParameters",
    "SkillResolver",
    "ParameterResolver",
    "get_skill_resolver",
    "get_parameter_resolver",
    "resolve_skill_ref",
    "get_skills_root",
]
