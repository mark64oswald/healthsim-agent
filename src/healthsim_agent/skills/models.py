"""Pydantic models for parsed skills.

This module defines the data structures for the hybrid skill format:
- YAML frontmatter for basic metadata
- Markdown prose for Claude's system prompt
- Embedded YAML/JSON blocks for structured tool configs
"""
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class SkillMetadata:
    """YAML frontmatter metadata from a skill file."""
    name: str
    description: str
    triggers: list[str] = field(default_factory=list)
    
    @classmethod
    def from_frontmatter(cls, data: dict[str, Any]) -> "SkillMetadata":
        """Parse frontmatter dict into SkillMetadata.
        
        Extracts triggers from either:
        1. Explicit 'trigger_phrases' list
        2. Text after 'Triggers:' in description
        """
        name = data.get("name", "")
        description = data.get("description", "")
        
        # First check for explicit trigger_phrases
        triggers = data.get("trigger_phrases", [])
        
        # If not found, parse from description after "Triggers:"
        if not triggers and "Triggers:" in description:
            trigger_part = description.split("Triggers:")[-1]
            # Split on commas and clean up
            triggers = [t.strip() for t in trigger_part.split(",") if t.strip()]
        
        return cls(name=name, description=description, triggers=triggers)


@dataclass
class EmbeddedConfig:
    """Structured data extracted from embedded YAML/JSON blocks.
    
    These are code blocks within the skill markdown that contain
    machine-readable configuration for tools.
    """
    block_type: str  # "yaml" or "json"
    section_name: str  # Header before the code block
    data: dict[str, Any]


@dataclass
class ParsedSkill:
    """A fully parsed skill with metadata, content, and configs.
    
    Represents the hybrid skill format where:
    - metadata: From YAML frontmatter (name, description, triggers)
    - markdown_content: Full markdown for system prompt context
    - embedded_configs: Structured data extracted from code blocks
    """
    path: Path
    metadata: SkillMetadata
    markdown_content: str  # Full markdown for system prompt
    embedded_configs: list[EmbeddedConfig] = field(default_factory=list)
    
    @property
    def product(self) -> str:
        """Extract product from path (e.g., 'patientsim', 'membersim').
        
        Looks for the directory immediately after 'skills/' in the path.
        """
        parts = self.path.parts
        if "skills" in parts:
            idx = parts.index("skills")
            if idx + 1 < len(parts):
                return parts[idx + 1]
        return "common"
    
    @property
    def triggers(self) -> list[str]:
        """Get all trigger phrases for this skill."""
        return self.metadata.triggers
    
    @property
    def is_product_skill(self) -> bool:
        """Check if this is a product-level SKILL.md file."""
        return self.path.name == "SKILL.md"


@dataclass 
class SkillIndex:
    """Index of all loaded skills for efficient routing.
    
    Maintains three indexes:
    - skills: name -> ParsedSkill (primary lookup)
    - trigger_map: trigger phrase -> list of skill names
    - product_map: product name -> list of skill names
    """
    skills: dict[str, ParsedSkill] = field(default_factory=dict)  # name -> skill
    trigger_map: dict[str, list[str]] = field(default_factory=dict)  # trigger -> skill names
    product_map: dict[str, list[str]] = field(default_factory=dict)  # product -> skill names
    
    def add_skill(self, skill: ParsedSkill) -> None:
        """Add a skill to the index.
        
        Updates all three indexes (skills, triggers, products).
        """
        self.skills[skill.metadata.name] = skill
        
        # Index by product
        if skill.product not in self.product_map:
            self.product_map[skill.product] = []
        self.product_map[skill.product].append(skill.metadata.name)
        
        # Index by triggers (lowercase for case-insensitive matching)
        for trigger in skill.triggers:
            trigger_lower = trigger.lower().strip()
            if trigger_lower:  # Skip empty triggers
                if trigger_lower not in self.trigger_map:
                    self.trigger_map[trigger_lower] = []
                self.trigger_map[trigger_lower].append(skill.metadata.name)
    
    def get_by_trigger(self, trigger: str) -> list[ParsedSkill]:
        """Get skills matching a trigger phrase (case-insensitive)."""
        trigger_lower = trigger.lower().strip()
        skill_names = self.trigger_map.get(trigger_lower, [])
        return [self.skills[name] for name in skill_names if name in self.skills]
    
    def get_by_product(self, product: str) -> list[ParsedSkill]:
        """Get all skills for a product."""
        skill_names = self.product_map.get(product, [])
        return [self.skills[name] for name in skill_names if name in self.skills]
    
    def get_by_name(self, name: str) -> ParsedSkill | None:
        """Get a skill by its name."""
        return self.skills.get(name)
    
    @property
    def skill_count(self) -> int:
        """Total number of skills in the index."""
        return len(self.skills)
    
    @property
    def products(self) -> list[str]:
        """List of all products with skills."""
        return list(self.product_map.keys())
