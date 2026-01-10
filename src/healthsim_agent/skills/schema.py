"""Skill schema definitions.

Defines the data structures for skill definitions that guide
Claude in generating domain-specific data.

Ported from: healthsim-workspace/packages/core/src/healthsim/skills/schema.py
"""

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class SkillType(str, Enum):
    """Type of skill."""
    
    DOMAIN_KNOWLEDGE = "domain-knowledge"
    COHORT_TEMPLATE = "cohort-template"
    FORMAT_SPEC = "format-spec"
    VALIDATION_RULES = "validation-rules"
    GENERATION_GUIDE = "generation-guide"


class ParameterType(str, Enum):
    """Type of skill parameter."""
    
    RANGE = "range"
    ENUM = "enum"
    BOOLEAN = "boolean"
    INTEGER = "integer"
    FLOAT = "float"
    STRING = "string"
    LIST = "list"
    OBJECT = "object"


class SkillMetadata(BaseModel):
    """Metadata for a skill."""
    
    type: SkillType = SkillType.COHORT_TEMPLATE
    version: str = "1.0"
    author: str | None = None
    tags: list[str] = Field(default_factory=list)
    requires_version: str | None = None


class SkillParameter(BaseModel):
    """A configurable parameter for a skill."""
    
    name: str
    type: ParameterType
    default: Any = None
    description: str = ""
    required: bool = False
    options: list[Any] | None = None
    min_value: float | None = None
    max_value: float | None = None
    
    def validate_value(self, value: Any) -> bool:
        """Validate a value against this parameter's constraints."""
        if value is None:
            return not self.required
        
        if self.type == ParameterType.ENUM:
            return self.options is None or value in self.options
        
        if self.type == ParameterType.BOOLEAN:
            return isinstance(value, bool)
        
        if self.type in (ParameterType.INTEGER, ParameterType.FLOAT):
            if not isinstance(value, (int, float)):
                return False
            if self.min_value is not None and value < self.min_value:
                return False
            if self.max_value is not None and value > self.max_value:
                return False
        
        if self.type == ParameterType.RANGE:
            if not isinstance(value, (list, tuple)) or len(value) != 2:
                return False
            if value[0] > value[1]:
                return False
        
        return True


class SkillVariation(BaseModel):
    """A variation/modifier for a skill."""
    
    name: str
    description: str = ""
    parameter_overrides: dict[str, Any] = Field(default_factory=dict)


class Skill(BaseModel):
    """A complete skill definition."""
    
    name: str
    description: str = ""
    metadata: SkillMetadata = Field(default_factory=SkillMetadata)
    purpose: str = ""
    parameters: list[SkillParameter] = Field(default_factory=list)
    knowledge: dict[str, str] = Field(default_factory=dict)
    variations: list[SkillVariation] = Field(default_factory=list)
    examples: list[str] = Field(default_factory=list)
    references: list[str] = Field(default_factory=list)
    dependencies: list[str] = Field(default_factory=list)
    raw_text: str = ""
    content: dict[str, Any] = Field(default_factory=dict)
    
    for_claude: str | None = None
    when_to_use: str | None = None
    
    def get_parameter(self, name: str) -> SkillParameter | None:
        """Get a parameter by name."""
        for param in self.parameters:
            if param.name == name:
                return param
        return None
    
    def get_parameter_value(self, name: str, overrides: dict[str, Any] | None = None) -> Any:
        """Get parameter value with optional override."""
        if overrides and name in overrides:
            return overrides[name]
        
        param = self.get_parameter(name)
        return param.default if param else None
    
    def apply_variation(self, variation_name: str) -> "Skill":
        """Apply a variation to create a modified skill."""
        variation = None
        for v in self.variations:
            if v.name == variation_name:
                variation = v
                break
        
        if variation is None:
            raise ValueError(f"Variation '{variation_name}' not found")
        
        new_params = []
        for param in self.parameters:
            if param.name in variation.parameter_overrides:
                new_param = param.model_copy(
                    update={"default": variation.parameter_overrides[param.name]}
                )
                new_params.append(new_param)
            else:
                new_params.append(param)
        
        return self.model_copy(
            update={
                "name": f"{self.name} ({variation.name})",
                "parameters": new_params,
            }
        )


__all__ = [
    "SkillType",
    "ParameterType",
    "SkillMetadata",
    "SkillParameter",
    "SkillVariation",
    "Skill",
]
