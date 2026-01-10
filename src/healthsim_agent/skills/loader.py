"""Skill loader - parses markdown skills with embedded structured data.

This implements the hybrid skill format (Option C) where:
1. YAML frontmatter provides basic metadata
2. Markdown prose goes into system prompt for Claude
3. Embedded YAML/JSON code blocks are parsed for tools

Single file = single source of truth for both AI and tools.
"""
from __future__ import annotations
import re
import yaml
import json
from pathlib import Path
from typing import Any

from .models import ParsedSkill, SkillMetadata, EmbeddedConfig, SkillIndex


class SkillLoader:
    """Load and parse HealthSim skills from markdown files.
    
    The loader scans a skills directory recursively, parsing each
    .md file to extract:
    - YAML frontmatter (name, description, triggers)
    - Full markdown content (for system prompt)
    - Embedded YAML/JSON blocks (for tool configs)
    """
    
    # Regex patterns for parsing
    FRONTMATTER_PATTERN = re.compile(
        r'^---\s*\n(.*?)\n---\s*\n',
        re.DOTALL
    )
    
    # Match ```yaml or ```json blocks, capturing any preceding ## header
    CODE_BLOCK_PATTERN = re.compile(
        r'(?:^#{1,3}\s+([^\n]+)\n\s*)?'  # Optional header (## or ###)
        r'```(yaml|json)\s*\n'           # Code fence with language
        r'(.*?)'                          # Content (non-greedy)
        r'\n```',                         # Closing fence
        re.MULTILINE | re.DOTALL
    )
    
    def __init__(self, skills_dir: Path | str | None = None):
        """Initialize loader with skills directory path.
        
        Args:
            skills_dir: Path to skills directory. Defaults to skills/
                       relative to the package root.
        """
        if skills_dir is None:
            # Default: go up from src/healthsim_agent/skills/ to repo root, then skills/
            skills_dir = Path(__file__).parent.parent.parent.parent / "skills"
        self.skills_dir = Path(skills_dir)
        self._index: SkillIndex | None = None
    
    @property
    def index(self) -> SkillIndex:
        """Get or build the skill index (lazy loading)."""
        if self._index is None:
            self._index = self.load_all()
        return self._index
    
    def reload(self) -> SkillIndex:
        """Force reload all skills."""
        self._index = self.load_all()
        return self._index

    def load_all(self) -> SkillIndex:
        """Load all skills from the skills directory.
        
        Returns:
            SkillIndex with all parsed skills indexed by name,
            triggers, and product.
        """
        index = SkillIndex()
        
        if not self.skills_dir.exists():
            return index
        
        # Find all .md files recursively
        for skill_path in self.skills_dir.rglob("*.md"):
            # Skip README files
            if skill_path.name.lower() == "readme.md":
                continue
            
            try:
                skill = self.load_skill(skill_path)
                if skill and skill.metadata.name:
                    index.add_skill(skill)
            except Exception as e:
                # Log but continue loading other skills
                print(f"Warning: Failed to load {skill_path}: {e}")
        
        return index
    
    def load_skill(self, path: Path) -> ParsedSkill | None:
        """Load and parse a single skill file.
        
        Args:
            path: Path to the skill .md file
            
        Returns:
            ParsedSkill or None if file doesn't exist or lacks frontmatter
        """
        if not path.exists():
            return None
        
        content = path.read_text(encoding="utf-8")
        
        # Extract YAML frontmatter
        metadata = self._parse_frontmatter(content)
        if metadata is None:
            # No valid frontmatter - skip this file
            return None
        
        # Extract embedded configs
        embedded_configs = self._extract_embedded_configs(content)
        
        return ParsedSkill(
            path=path,
            metadata=metadata,
            markdown_content=content,
            embedded_configs=embedded_configs
        )
    
    def _parse_frontmatter(self, content: str) -> SkillMetadata | None:
        """Extract and parse YAML frontmatter from skill content.
        
        Frontmatter must be at the start of the file, delimited by ---.
        """
        match = self.FRONTMATTER_PATTERN.match(content)
        if not match:
            return None
        
        try:
            frontmatter_yaml = match.group(1)
            data = yaml.safe_load(frontmatter_yaml)
            if not isinstance(data, dict):
                return None
            return SkillMetadata.from_frontmatter(data)
        except yaml.YAMLError:
            return None

    def _extract_embedded_configs(self, content: str) -> list[EmbeddedConfig]:
        """Extract YAML/JSON code blocks from markdown content.
        
        Looks for fenced code blocks with yaml or json language specifier.
        Associates each block with the nearest preceding header.
        """
        configs = []
        
        # Track headers to associate with code blocks
        current_header = "config"
        
        for match in self.CODE_BLOCK_PATTERN.finditer(content):
            header = match.group(1) or current_header
            block_type = match.group(2)  # "yaml" or "json"
            block_content = match.group(3)
            
            try:
                if block_type == "yaml":
                    data = yaml.safe_load(block_content)
                else:  # json
                    data = json.loads(block_content)
                
                # Only include dict configs (skip arrays, strings, etc.)
                if isinstance(data, dict):
                    configs.append(EmbeddedConfig(
                        block_type=block_type,
                        section_name=header.strip(),
                        data=data
                    ))
            except (yaml.YAMLError, json.JSONDecodeError):
                # Skip invalid blocks silently
                continue
        
        return configs
    
    def get_skill_context(
        self, 
        products: list[str] | None = None,
        include_generation: bool = True
    ) -> str:
        """Build system prompt context from relevant skills.
        
        Concatenates markdown content from skills for the system prompt.
        
        Args:
            products: List of products to include (e.g., ['patientsim']).
                     If None, includes only common/generation skills.
            include_generation: Whether to include generation framework skills.
        
        Returns:
            Concatenated markdown content for system prompt.
        """
        skills_to_include = []
        
        # Always include common skills
        skills_to_include.extend(self.index.get_by_product("common"))
        
        # Include generation skills (framework knowledge)
        if include_generation:
            skills_to_include.extend(self.index.get_by_product("generation"))
        
        # Include requested product skills
        if products:
            for product in products:
                skills_to_include.extend(self.index.get_by_product(product))
        
        # Deduplicate while preserving order
        seen = set()
        unique_skills = []
        for skill in skills_to_include:
            if skill.metadata.name not in seen:
                seen.add(skill.metadata.name)
                unique_skills.append(skill)
        
        # Build context string
        context_parts = []
        for skill in unique_skills:
            context_parts.append(f"<!-- Skill: {skill.metadata.name} ({skill.product}) -->")
            context_parts.append(skill.markdown_content)
            context_parts.append("")  # Blank line between skills
        
        return "\n".join(context_parts)
    
    def get_configs(self, skill_name: str) -> dict[str, Any]:
        """Get merged configs from a skill's embedded blocks.
        
        Args:
            skill_name: Name of the skill (from frontmatter)
            
        Returns:
            Dict with section names as keys and data as values.
        """
        skill = self.index.skills.get(skill_name)
        if not skill:
            return {}
        
        configs = {}
        for config in skill.embedded_configs:
            configs[config.section_name] = config.data
        
        return configs
    
    def get_all_configs_by_product(self, product: str) -> dict[str, dict[str, Any]]:
        """Get all configs for a product.
        
        Args:
            product: Product name (e.g., 'patientsim')
            
        Returns:
            Dict mapping skill names to their configs.
        """
        result = {}
        for skill in self.index.get_by_product(product):
            configs = self.get_configs(skill.metadata.name)
            if configs:
                result[skill.metadata.name] = configs
        return result
