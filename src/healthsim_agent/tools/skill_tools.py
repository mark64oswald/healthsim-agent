"""Skill Management Tools for HealthSim Agent.

Provides comprehensive skill management:
- Index: Full-text search across all skills
- Create: Guided skill creation with validation
- Update: Modify existing skills with versioning
- Delete: Remove skills (with archive option)
- Validate: Check skill structure and quality

Skills remain as markdown files for human readability and git version control,
but are indexed in DuckDB for fast search and discovery.
"""

from datetime import datetime
from pathlib import Path
from typing import Any
import json
import re
import yaml

from .base import ToolResult, ok, err
from .connection import get_manager


# =============================================================================
# Configuration
# =============================================================================

SKILLS_DIR = Path(__file__).parent.parent.parent.parent / "skills"

VALID_PRODUCTS = [
    "patientsim", "membersim", "rxmembersim", 
    "trialsim", "populationsim", "networksim",
    "common", "generation", "core"
]

SKILL_TYPES = [
    "scenario",      # Clinical/domain scenarios (diabetes-management, ed-chest-pain)
    "pattern",       # Reusable patterns (tiered-network, hmo-network)
    "integration",   # Cross-product integration (provider-for-encounter)
    "template",      # Ready-to-use templates (medicare-diabetic)
    "query",         # Query/analytics skills (provider-search)
    "reference",     # Reference data skills (code-systems)
    "workflow",      # Multi-step workflows (adt-workflow)
]

# Required sections for each skill type
REQUIRED_SECTIONS = {
    "scenario": ["Purpose", "Parameters", "Generation Rules", "Examples"],
    "pattern": ["Purpose", "Pattern Specification", "Examples"],
    "integration": ["Purpose", "Integration Points", "Examples"],
    "template": ["Quick Start", "Template Specification", "Customization Examples"],
    "query": ["Purpose", "Query Patterns", "Examples"],
    "reference": ["Purpose", "Data Structure"],
    "workflow": ["Purpose", "Steps", "Examples"],
}


# =============================================================================
# Table Setup
# =============================================================================

_tables_ensured = False


def _ensure_tables() -> None:
    """Ensure skill index tables exist."""
    global _tables_ensured
    if _tables_ensured:
        return
    
    with get_manager().write_connection() as conn:
        # Main skill index
        conn.execute("""
            CREATE TABLE IF NOT EXISTS skill_index (
                id              VARCHAR PRIMARY KEY,
                name            VARCHAR NOT NULL,
                product         VARCHAR NOT NULL,
                skill_type      VARCHAR,
                description     VARCHAR,
                trigger_phrases JSON,
                file_path       VARCHAR NOT NULL,
                relative_path   VARCHAR NOT NULL,
                subdirectory    VARCHAR,
                tags            JSON,
                related_skills  JSON,
                word_count      INTEGER,
                has_examples    BOOLEAN DEFAULT FALSE,
                has_parameters  BOOLEAN DEFAULT FALSE,
                indexed_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                content_hash    VARCHAR,
                metadata        JSON
            )
        """)
        
        # Full-text search index (skill content for semantic search)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS skill_content (
                skill_id        VARCHAR PRIMARY KEY,
                full_text       VARCHAR,
                sections        JSON,
                code_blocks     JSON,
                indexed_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Version history
        conn.execute("""
            CREATE TABLE IF NOT EXISTS skill_versions (
                id              INTEGER PRIMARY KEY,
                skill_id        VARCHAR NOT NULL,
                version         INTEGER NOT NULL,
                content_hash    VARCHAR,
                change_summary  VARCHAR,
                changed_by      VARCHAR DEFAULT 'user',
                changed_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                content_backup  VARCHAR
            )
        """)
        
        # Create sequence for version IDs
        conn.execute("CREATE SEQUENCE IF NOT EXISTS skill_version_seq START 1")
    
    _tables_ensured = True


# =============================================================================
# Skill Parsing
# =============================================================================

def _parse_skill_file(file_path: Path) -> dict[str, Any] | None:
    """Parse a skill markdown file into structured data."""
    try:
        content = file_path.read_text(encoding='utf-8')
        
        # Extract YAML frontmatter
        frontmatter = {}
        body = content
        
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                try:
                    frontmatter = yaml.safe_load(parts[1]) or {}
                except yaml.YAMLError:
                    frontmatter = {}
                body = parts[2].strip()
        
        # Extract sections
        sections = {}
        current_section = "intro"
        current_content = []
        
        for line in body.split('\n'):
            if line.startswith('## '):
                if current_content:
                    sections[current_section] = '\n'.join(current_content).strip()
                current_section = line[3:].strip()
                current_content = []
            else:
                current_content.append(line)
        
        if current_content:
            sections[current_section] = '\n'.join(current_content).strip()
        
        # Extract code blocks
        code_blocks = re.findall(r'```(\w*)\n(.*?)```', body, re.DOTALL)
        
        # Extract trigger phrases from description or dedicated section
        trigger_phrases = []
        if 'description' in frontmatter:
            desc = frontmatter['description']
            if 'Triggers:' in desc:
                triggers_part = desc.split('Triggers:')[1].strip()
                trigger_phrases = [t.strip() for t in triggers_part.split(',')]
        
        # Also check for Trigger Phrases section
        for section_name, section_content in sections.items():
            if 'trigger' in section_name.lower():
                phrases = [line.strip('- ').strip() for line in section_content.split('\n') 
                          if line.strip() and line.strip().startswith('-')]
                trigger_phrases.extend(phrases)
        
        return {
            "frontmatter": frontmatter,
            "sections": sections,
            "code_blocks": code_blocks,
            "trigger_phrases": list(set(trigger_phrases)),
            "full_text": body,
            "word_count": len(body.split()),
        }
        
    except Exception as e:
        return None


def _compute_content_hash(content: str) -> str:
    """Compute a hash of skill content for change detection."""
    import hashlib
    return hashlib.md5(content.encode()).hexdigest()[:12]


def _determine_skill_type(file_path: Path, parsed: dict) -> str:
    """Determine skill type from path and content."""
    path_str = str(file_path).lower()
    
    # Check path for type hints
    if '/patterns/' in path_str:
        return 'pattern'
    if '/integration/' in path_str:
        return 'integration'
    if '/templates/' in path_str:
        return 'template'
    if '/query/' in path_str:
        return 'query'
    if '/reference/' in path_str:
        return 'reference'
    
    # Check frontmatter
    if parsed.get('frontmatter', {}).get('type'):
        fm_type = parsed['frontmatter']['type'].lower()
        if 'template' in fm_type:
            return 'template'
        if 'pattern' in fm_type:
            return 'pattern'
    
    # Default to scenario for clinical content
    return 'scenario'


# =============================================================================
# Index Tools
# =============================================================================

def index_skills(product: str | None = None, force: bool = False) -> ToolResult:
    """Index all skills into the database for search.
    
    Args:
        product: Only index skills for this product (default: all)
        force: Re-index even if content hasn't changed
    
    Returns:
        ToolResult with indexing summary
    """
    try:
        _ensure_tables()
        
        if not SKILLS_DIR.exists():
            return err(f"Skills directory not found: {SKILLS_DIR}")
        
        indexed = 0
        skipped = 0
        errors = []
        
        # Find all skill files
        pattern = f"{product}/**/*.md" if product else "**/*.md"
        skill_files = list(SKILLS_DIR.glob(pattern))
        
        conn = get_manager().get_read_connection()
        
        for file_path in skill_files:
            # Skip README files and main SKILL.md files
            if file_path.name in ['README.md']:
                skipped += 1
                continue
            
            try:
                # Parse the skill
                parsed = _parse_skill_file(file_path)
                if not parsed:
                    errors.append(f"Failed to parse: {file_path.name}")
                    continue
                
                # Compute content hash
                content_hash = _compute_content_hash(parsed['full_text'])
                
                # Check if already indexed with same hash
                if not force:
                    existing = conn.execute("""
                        SELECT content_hash FROM skill_index WHERE file_path = ?
                    """, [str(file_path)]).fetchone()
                    
                    if existing and existing[0] == content_hash:
                        skipped += 1
                        continue
                
                # Determine product from path
                rel_path = file_path.relative_to(SKILLS_DIR)
                parts = rel_path.parts
                skill_product = parts[0] if parts else 'common'
                subdirectory = '/'.join(parts[1:-1]) if len(parts) > 2 else None
                
                # Build skill ID
                skill_id = f"{skill_product}/{rel_path.stem}"
                if subdirectory:
                    skill_id = f"{skill_product}/{subdirectory}/{rel_path.stem}"
                
                # Extract metadata
                frontmatter = parsed.get('frontmatter', {})
                name = frontmatter.get('name', rel_path.stem)
                description = frontmatter.get('description', '')
                skill_type = _determine_skill_type(file_path, parsed)
                
                # Check for examples and parameters
                sections = parsed.get('sections', {})
                has_examples = any('example' in s.lower() for s in sections.keys())
                has_parameters = any('parameter' in s.lower() for s in sections.keys())
                
                # Extract tags
                tags = frontmatter.get('tags', [])
                if isinstance(tags, str):
                    tags = [t.strip() for t in tags.split(',')]
                
                # Extract related skills
                related_skills = []
                for section_name, section_content in sections.items():
                    if 'related' in section_name.lower():
                        # Find markdown links
                        links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', section_content)
                        for text, href in links:
                            if href.endswith('.md'):
                                related_skills.append(href)
                
                # Insert or update index
                with get_manager().write_connection() as wconn:
                    wconn.execute("""
                        INSERT OR REPLACE INTO skill_index 
                        (id, name, product, skill_type, description, trigger_phrases,
                         file_path, relative_path, subdirectory, tags, related_skills,
                         word_count, has_examples, has_parameters, indexed_at, content_hash)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, [
                        skill_id, name, skill_product, skill_type, description,
                        json.dumps(parsed.get('trigger_phrases', [])),
                        str(file_path), str(rel_path), subdirectory,
                        json.dumps(tags), json.dumps(related_skills),
                        parsed.get('word_count', 0), has_examples, has_parameters,
                        datetime.now(), content_hash
                    ])
                    
                    # Store full content for search
                    wconn.execute("""
                        INSERT OR REPLACE INTO skill_content
                        (skill_id, full_text, sections, code_blocks, indexed_at)
                        VALUES (?, ?, ?, ?, ?)
                    """, [
                        skill_id,
                        parsed['full_text'],
                        json.dumps(parsed['sections']),
                        json.dumps([{'lang': cb[0], 'code': cb[1]} for cb in parsed.get('code_blocks', [])]),
                        datetime.now()
                    ])
                
                indexed += 1
                
            except Exception as e:
                errors.append(f"{file_path.name}: {str(e)}")
        
        return ok(
            data={
                "indexed": indexed,
                "skipped": skipped,
                "errors": errors[:10],  # Limit error list
                "total_files": len(skill_files),
            },
            message=f"Indexed {indexed} skills, skipped {skipped}, {len(errors)} errors"
        )
        
    except Exception as e:
        return err(f"Failed to index skills: {str(e)}")


def search_skills(
    query: str,
    product: str | None = None,
    skill_type: str | None = None,
    tags: list[str] | None = None,
    limit: int = 20,
) -> ToolResult:
    """Search skills by keyword, trigger phrase, or content.
    
    Args:
        query: Search query (matches name, description, triggers, content)
        product: Filter by product
        skill_type: Filter by skill type
        tags: Filter by tags (any match)
        limit: Maximum results
    
    Returns:
        ToolResult with matching skills
    """
    try:
        _ensure_tables()
        conn = get_manager().get_read_connection()
        
        # Build search query
        sql = """
            SELECT DISTINCT
                si.id,
                si.name,
                si.product,
                si.skill_type,
                si.description,
                si.trigger_phrases,
                si.subdirectory,
                si.tags,
                si.word_count,
                si.has_examples,
                si.relative_path
            FROM skill_index si
            LEFT JOIN skill_content sc ON si.id = sc.skill_id
            WHERE 1=1
        """
        params = []
        
        # Search across multiple fields
        if query:
            sql += """ AND (
                si.name ILIKE ? 
                OR si.description ILIKE ?
                OR si.trigger_phrases::VARCHAR ILIKE ?
                OR sc.full_text ILIKE ?
            )"""
            search_pattern = f"%{query}%"
            params.extend([search_pattern] * 4)
        
        if product:
            sql += " AND si.product = ?"
            params.append(product)
        
        if skill_type:
            sql += " AND si.skill_type = ?"
            params.append(skill_type)
        
        if tags:
            # Match any tag
            tag_conditions = []
            for tag in tags:
                tag_conditions.append("si.tags::VARCHAR ILIKE ?")
                params.append(f'%"{tag}"%')
            sql += f" AND ({' OR '.join(tag_conditions)})"
        
        sql += " ORDER BY si.product, si.name LIMIT ?"
        params.append(limit)
        
        rows = conn.execute(sql, params).fetchall()
        
        results = []
        for row in rows:
            results.append({
                "id": row[0],
                "name": row[1],
                "product": row[2],
                "skill_type": row[3],
                "description": row[4][:200] + "..." if row[4] and len(row[4]) > 200 else row[4],
                "trigger_phrases": json.loads(row[5]) if row[5] else [],
                "subdirectory": row[6],
                "tags": json.loads(row[7]) if row[7] else [],
                "word_count": row[8],
                "has_examples": row[9],
                "path": row[10],
            })
        
        return ok(
            data={"skills": results, "count": len(results), "query": query},
            message=f"Found {len(results)} skills matching '{query}'"
        )
        
    except Exception as e:
        return err(f"Search failed: {str(e)}")


def get_skill(skill_id: str) -> ToolResult:
    """Get full skill content by ID.
    
    Args:
        skill_id: Skill ID (e.g., "patientsim/diabetes-management")
    
    Returns:
        ToolResult with skill content and metadata
    """
    try:
        _ensure_tables()
        conn = get_manager().get_read_connection()
        
        # First try exact match
        row = conn.execute("""
            SELECT 
                si.id, si.name, si.product, si.skill_type, si.description,
                si.trigger_phrases, si.file_path, si.relative_path, si.subdirectory,
                si.tags, si.related_skills, si.word_count, si.has_examples,
                si.has_parameters, si.content_hash, sc.full_text, sc.sections
            FROM skill_index si
            LEFT JOIN skill_content sc ON si.id = sc.skill_id
            WHERE si.id = ? OR si.name = ? OR si.relative_path LIKE ?
        """, [skill_id, skill_id, f"%{skill_id}%"]).fetchone()
        
        if not row:
            return err(f"Skill not found: {skill_id}")
        
        return ok(
            data={
                "id": row[0],
                "name": row[1],
                "product": row[2],
                "skill_type": row[3],
                "description": row[4],
                "trigger_phrases": json.loads(row[5]) if row[5] else [],
                "file_path": row[6],
                "relative_path": row[7],
                "subdirectory": row[8],
                "tags": json.loads(row[9]) if row[9] else [],
                "related_skills": json.loads(row[10]) if row[10] else [],
                "word_count": row[11],
                "has_examples": row[12],
                "has_parameters": row[13],
                "content_hash": row[14],
                "content": row[15],
                "sections": json.loads(row[16]) if row[16] else {},
            },
            message=f"Loaded skill: {row[1]}"
        )
        
    except Exception as e:
        return err(f"Failed to get skill: {str(e)}")


def list_skill_products() -> ToolResult:
    """List all products and their skill counts.
    
    Returns:
        ToolResult with product summary
    """
    try:
        _ensure_tables()
        conn = get_manager().get_read_connection()
        
        rows = conn.execute("""
            SELECT 
                product,
                COUNT(*) as skill_count,
                COUNT(DISTINCT skill_type) as type_count,
                COUNT(DISTINCT subdirectory) as subdir_count
            FROM skill_index
            GROUP BY product
            ORDER BY product
        """).fetchall()
        
        products = []
        for row in rows:
            products.append({
                "product": row[0],
                "skill_count": row[1],
                "type_count": row[2],
                "subdirectory_count": row[3],
            })
        
        return ok(
            data={"products": products},
            message=f"Found {len(products)} products with skills"
        )
        
    except Exception as e:
        return err(f"Failed to list products: {str(e)}")


# =============================================================================
# Skill Templates
# =============================================================================

SKILL_TEMPLATES = {
    "scenario": '''---
name: {name}
description: "{description}"
---

# {title}

{overview}

## For Claude

Use this skill when the user requests {use_cases}.

**When to apply this skill:**
{triggers_list}

## Purpose

{purpose}

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
{parameters_table}

## Generation Rules

### Demographics
{demographics}

### Conditions
{conditions}

### Medications
{medications}

## Variations

### Variation 1: {variation1_name}
{variation1_description}

### Variation 2: {variation2_name}
{variation2_description}

## Examples

### Example 1: {example1_name}
```json
{example1_json}
```

### Example 2: {example2_name}
```json
{example2_json}
```

## Validation Rules

| Rule | Requirement | Example |
|------|-------------|---------|
{validation_rules}

## Trigger Phrases

{trigger_phrases}

## Related Skills

{related_skills}
''',

    "template": '''---
name: {name}-template
description: Pre-built profile for {description}
type: profile_template
---

# {title} Template

Ready-to-use profile for generating {description}.

## Quick Start

```
User: "{example_prompt}"

Claude: "Using template '{name}' with defaults:
{defaults_summary}

Generate now or customize?"
```

## Template Specification

```json
{template_spec}
```

## Customization Examples

### Example 1: {custom1_name}
```
{custom1_example}
```

### Example 2: {custom2_name}
```
{custom2_example}
```

## Expected Outputs

| Product | Entity Types | Formats |
|---------|--------------|---------|
{output_table}

## Related Templates

{related_templates}

---

*Part of the HealthSim Skills Library*
''',

    "pattern": '''---
name: {name}-pattern
description: "{description}"
type: pattern
---

# {title} Pattern

{overview}

## Purpose

{purpose}

## Pattern Specification

{pattern_spec}

## When to Use

Apply this pattern when:
{when_to_use}

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
{parameters_table}

## Examples

### Example 1: {example1_name}
{example1_content}

### Example 2: {example2_name}
{example2_content}

## Integration Points

{integration_points}

## Related Patterns

{related_patterns}
''',

    "integration": '''---
name: {name}
description: "{description}"
type: integration
---

# {title}

Cross-product integration skill for {integration_purpose}.

## Purpose

{purpose}

## Integration Points

### Source Product: {source_product}
{source_entities}

### Target Product: {target_product}
{target_entities}

## Mapping Rules

{mapping_rules}

## Examples

### Example 1: {example1_name}
```json
{example1_json}
```

## Usage

{usage_instructions}

## Related Skills

{related_skills}
'''
}


def get_skill_template(skill_type: str) -> ToolResult:
    """Get the template for creating a new skill of a given type.
    
    Args:
        skill_type: Type of skill (scenario, template, pattern, integration)
    
    Returns:
        ToolResult with template structure and guidance
    """
    if skill_type not in SKILL_TEMPLATES:
        return err(f"Unknown skill type: {skill_type}. Valid types: {list(SKILL_TEMPLATES.keys())}")
    
    template = SKILL_TEMPLATES[skill_type]
    
    # Extract placeholder fields
    placeholders = set(re.findall(r'\{(\w+)\}', template))
    
    required_sections = REQUIRED_SECTIONS.get(skill_type, [])
    
    return ok(
        data={
            "skill_type": skill_type,
            "template": template,
            "placeholders": sorted(placeholders),
            "required_sections": required_sections,
            "guidance": _get_creation_guidance(skill_type),
        },
        message=f"Template for {skill_type} skill"
    )


def _get_creation_guidance(skill_type: str) -> dict:
    """Get guidance for creating a skill of the given type."""
    guidance = {
        "scenario": {
            "description": "Clinical or domain scenarios that guide generation",
            "key_elements": [
                "Clear trigger phrases for when to use",
                "Specific generation rules (demographics, conditions, medications)",
                "At least 2 complete JSON examples",
                "Validation rules for data quality",
            ],
            "examples": ["diabetes-management", "ed-chest-pain", "chronic-kidney-disease"],
        },
        "template": {
            "description": "Ready-to-use profile specifications",
            "key_elements": [
                "Complete JSON template specification",
                "Customization examples",
                "Expected outputs by product",
            ],
            "examples": ["medicare-diabetic", "commercial-family"],
        },
        "pattern": {
            "description": "Reusable patterns for generation or integration",
            "key_elements": [
                "Clear pattern specification",
                "When to use guidance",
                "Integration points",
            ],
            "examples": ["tiered-network-pattern", "hmo-network-pattern"],
        },
        "integration": {
            "description": "Cross-product integration mappings",
            "key_elements": [
                "Source and target products",
                "Entity mapping rules",
                "Transformation examples",
            ],
            "examples": ["provider-for-encounter", "formulary-for-rx"],
        },
    }
    return guidance.get(skill_type, {})


# =============================================================================
# Skill Validation
# =============================================================================

def validate_skill(
    content: str,
    skill_type: str | None = None,
    strict: bool = False,
) -> ToolResult:
    """Validate skill content structure and quality.
    
    Args:
        content: Markdown content to validate
        skill_type: Expected skill type (for type-specific validation)
        strict: If True, require all recommended sections
    
    Returns:
        ToolResult with validation results and suggestions
    """
    issues = []
    warnings = []
    
    # Check YAML frontmatter
    if not content.startswith('---'):
        issues.append("Missing YAML frontmatter (must start with ---)")
    else:
        parts = content.split('---', 2)
        if len(parts) < 3:
            issues.append("Invalid YAML frontmatter format")
        else:
            try:
                frontmatter = yaml.safe_load(parts[1]) or {}
                
                if 'name' not in frontmatter:
                    issues.append("Missing 'name' in frontmatter")
                
                if 'description' not in frontmatter:
                    issues.append("Missing 'description' in frontmatter")
                elif len(frontmatter.get('description', '')) < 20:
                    warnings.append("Description is very short - consider adding trigger phrases")
                    
            except yaml.YAMLError as e:
                issues.append(f"Invalid YAML in frontmatter: {str(e)}")
    
    # Parse sections
    parsed = _parse_skill_file_from_content(content)
    sections = parsed.get('sections', {}) if parsed else {}
    section_names_lower = [s.lower() for s in sections.keys()]
    
    # Check for required sections based on skill type
    if skill_type:
        required = REQUIRED_SECTIONS.get(skill_type, [])
        for req in required:
            if not any(req.lower() in s for s in section_names_lower):
                if strict:
                    issues.append(f"Missing required section: {req}")
                else:
                    warnings.append(f"Recommended section missing: {req}")
    
    # Check for examples
    has_examples = any('example' in s for s in section_names_lower)
    has_json_examples = '```json' in content
    
    if not has_examples:
        warnings.append("No Examples section found - examples help Claude understand output format")
    elif not has_json_examples and skill_type in ['scenario', 'template', 'integration']:
        warnings.append("No JSON code blocks in examples - structured examples improve generation quality")
    
    # Check for trigger phrases
    has_triggers = (
        'Triggers:' in content or 
        any('trigger' in s for s in section_names_lower) or
        'trigger_phrases' in str(parsed.get('frontmatter', {}))
    )
    
    if not has_triggers:
        warnings.append("No trigger phrases defined - these help Claude know when to use this skill")
    
    # Check for related skills
    has_related = any('related' in s for s in section_names_lower)
    if not has_related:
        warnings.append("No Related Skills section - cross-product links improve integration")
    
    # Word count check
    word_count = len(content.split())
    if word_count < 200:
        warnings.append(f"Skill is quite short ({word_count} words) - consider adding more detail")
    
    # Quality score (0-100)
    quality_score = 100
    quality_score -= len(issues) * 15
    quality_score -= len(warnings) * 5
    quality_score = max(0, min(100, quality_score))
    
    is_valid = len(issues) == 0
    
    return ok(
        data={
            "valid": is_valid,
            "quality_score": quality_score,
            "issues": issues,
            "warnings": warnings,
            "sections_found": list(sections.keys()),
            "word_count": word_count,
            "has_examples": has_examples,
            "has_json_examples": has_json_examples,
            "has_triggers": has_triggers,
        },
        message=f"Validation {'passed' if is_valid else 'failed'} with score {quality_score}/100"
    )


def _parse_skill_file_from_content(content: str) -> dict[str, Any]:
    """Parse skill content string (same as _parse_skill_file but from string)."""
    try:
        frontmatter = {}
        body = content
        
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                try:
                    frontmatter = yaml.safe_load(parts[1]) or {}
                except yaml.YAMLError:
                    pass
                body = parts[2].strip()
        
        sections = {}
        current_section = "intro"
        current_content = []
        
        for line in body.split('\n'):
            if line.startswith('## '):
                if current_content:
                    sections[current_section] = '\n'.join(current_content).strip()
                current_section = line[3:].strip()
                current_content = []
            else:
                current_content.append(line)
        
        if current_content:
            sections[current_section] = '\n'.join(current_content).strip()
        
        return {
            "frontmatter": frontmatter,
            "sections": sections,
            "full_text": body,
        }
    except Exception:
        return {}


# =============================================================================
# Skill CRUD Operations
# =============================================================================

def save_skill(
    name: str,
    product: str,
    content: str,
    skill_type: str = "scenario",
    subdirectory: str | None = None,
    validate: bool = True,
    overwrite: bool = False,
) -> ToolResult:
    """Save a new skill to the skills directory.
    
    Creates a properly formatted markdown file in the appropriate location.
    
    Args:
        name: Skill name (used for filename, e.g., "post-surgical-infection")
        product: Product this skill belongs to (patientsim, membersim, etc.)
        content: Full markdown content of the skill
        skill_type: Type of skill (scenario, template, pattern, integration)
        subdirectory: Optional subdirectory within product folder
        validate: Validate content before saving (default True)
        overwrite: Allow overwriting existing skill (default False)
    
    Returns:
        ToolResult with saved skill path and validation results
    """
    try:
        _ensure_tables()
        
        # Validate product
        if product not in VALID_PRODUCTS:
            return err(f"Invalid product: {product}. Valid: {VALID_PRODUCTS}")
        
        # Validate skill type
        if skill_type not in SKILL_TYPES:
            return err(f"Invalid skill type: {skill_type}. Valid: {SKILL_TYPES}")
        
        # Normalize name
        safe_name = re.sub(r'[^a-z0-9-]', '-', name.lower())
        safe_name = re.sub(r'-+', '-', safe_name).strip('-')
        
        if not safe_name:
            return err("Invalid skill name - must contain alphanumeric characters")
        
        # Build file path
        skill_dir = SKILLS_DIR / product
        if subdirectory:
            skill_dir = skill_dir / subdirectory
        
        file_path = skill_dir / f"{safe_name}.md"
        
        # Check if exists
        if file_path.exists() and not overwrite:
            return err(f"Skill already exists: {file_path.relative_to(SKILLS_DIR)}. Use overwrite=True to replace.")
        
        # Validate content if requested
        validation_result = None
        if validate:
            validation_result = validate_skill(content, skill_type)
            if not validation_result.data.get('valid'):
                return err(
                    f"Skill validation failed: {validation_result.data.get('issues')}",
                    validation=validation_result.data
                )
        
        # Ensure directory exists
        skill_dir.mkdir(parents=True, exist_ok=True)
        
        # Save version backup if overwriting
        if file_path.exists():
            old_content = file_path.read_text(encoding='utf-8')
            old_hash = _compute_content_hash(old_content)
            
            skill_id = f"{product}/{safe_name}"
            if subdirectory:
                skill_id = f"{product}/{subdirectory}/{safe_name}"
            
            with get_manager().write_connection() as conn:
                # Get current version
                row = conn.execute("""
                    SELECT COALESCE(MAX(version), 0) FROM skill_versions WHERE skill_id = ?
                """, [skill_id]).fetchone()
                
                next_version = (row[0] if row else 0) + 1
                
                conn.execute("""
                    INSERT INTO skill_versions 
                    (id, skill_id, version, content_hash, change_summary, content_backup)
                    VALUES (nextval('skill_version_seq'), ?, ?, ?, 'Updated via save_skill', ?)
                """, [skill_id, next_version, old_hash, old_content])
        
        # Write the skill file
        file_path.write_text(content, encoding='utf-8')
        
        # Re-index this skill
        index_result = index_skills(product=product, force=True)
        
        return ok(
            data={
                "skill_name": safe_name,
                "product": product,
                "skill_type": skill_type,
                "file_path": str(file_path),
                "relative_path": str(file_path.relative_to(SKILLS_DIR)),
                "validation": validation_result.data if validation_result else None,
                "indexed": index_result.success,
            },
            message=f"Saved skill '{safe_name}' to {product}{'/' + subdirectory if subdirectory else ''}"
        )
        
    except Exception as e:
        return err(f"Failed to save skill: {str(e)}")


def update_skill(
    skill_id: str,
    content: str | None = None,
    append_section: dict | None = None,
    update_frontmatter: dict | None = None,
    change_summary: str | None = None,
) -> ToolResult:
    """Update an existing skill.
    
    Args:
        skill_id: Skill ID (e.g., "patientsim/diabetes-management")
        content: New full content (replaces entire skill)
        append_section: Dict with section_name and content to append
        update_frontmatter: Dict of frontmatter fields to update
        change_summary: Description of changes for version history
    
    Returns:
        ToolResult with update confirmation
    """
    try:
        _ensure_tables()
        
        # Load current skill
        skill_result = get_skill(skill_id)
        if not skill_result.success:
            return skill_result
        
        skill = skill_result.data
        file_path = Path(skill['file_path'])
        
        if not file_path.exists():
            return err(f"Skill file not found: {file_path}")
        
        # Read current content
        current_content = file_path.read_text(encoding='utf-8')
        
        # Determine new content
        if content:
            # Full replacement
            new_content = content
        elif append_section:
            # Append a section
            section_name = append_section.get('section_name', 'Additional Content')
            section_content = append_section.get('content', '')
            new_content = current_content.rstrip() + f"\n\n## {section_name}\n\n{section_content}\n"
        elif update_frontmatter:
            # Update frontmatter only
            parsed = _parse_skill_file_from_content(current_content)
            current_fm = parsed.get('frontmatter', {})
            current_fm.update(update_frontmatter)
            
            # Rebuild content with new frontmatter
            if current_content.startswith('---'):
                parts = current_content.split('---', 2)
                body = parts[2] if len(parts) >= 3 else ''
            else:
                body = current_content
            
            new_content = f"---\n{yaml.dump(current_fm, default_flow_style=False)}---{body}"
        else:
            return err("Must provide content, append_section, or update_frontmatter")
        
        # Validate new content
        validation_result = validate_skill(new_content, skill.get('skill_type'))
        
        # Save version backup
        old_hash = _compute_content_hash(current_content)
        with get_manager().write_connection() as conn:
            row = conn.execute("""
                SELECT COALESCE(MAX(version), 0) FROM skill_versions WHERE skill_id = ?
            """, [skill_id]).fetchone()
            
            next_version = (row[0] if row else 0) + 1
            
            conn.execute("""
                INSERT INTO skill_versions 
                (id, skill_id, version, content_hash, change_summary, content_backup)
                VALUES (nextval('skill_version_seq'), ?, ?, ?, ?, ?)
            """, [skill_id, next_version, old_hash, change_summary or 'Updated', current_content])
        
        # Write updated content
        file_path.write_text(new_content, encoding='utf-8')
        
        # Re-index
        index_skills(product=skill['product'], force=True)
        
        return ok(
            data={
                "skill_id": skill_id,
                "version": next_version,
                "validation": validation_result.data,
            },
            message=f"Updated skill '{skill['name']}' to version {next_version}"
        )
        
    except Exception as e:
        return err(f"Failed to update skill: {str(e)}")


def delete_skill(
    skill_id: str,
    archive: bool = True,
) -> ToolResult:
    """Delete a skill from the skills directory.
    
    Args:
        skill_id: Skill ID to delete
        archive: If True, save content to versions before deleting (default True)
    
    Returns:
        ToolResult confirming deletion
    """
    try:
        _ensure_tables()
        
        # Load current skill
        skill_result = get_skill(skill_id)
        if not skill_result.success:
            return skill_result
        
        skill = skill_result.data
        file_path = Path(skill['file_path'])
        
        if not file_path.exists():
            return err(f"Skill file not found: {file_path}")
        
        # Archive if requested
        if archive:
            current_content = file_path.read_text(encoding='utf-8')
            old_hash = _compute_content_hash(current_content)
            
            with get_manager().write_connection() as conn:
                row = conn.execute("""
                    SELECT COALESCE(MAX(version), 0) FROM skill_versions WHERE skill_id = ?
                """, [skill_id]).fetchone()
                
                next_version = (row[0] if row else 0) + 1
                
                conn.execute("""
                    INSERT INTO skill_versions 
                    (id, skill_id, version, content_hash, change_summary, content_backup)
                    VALUES (nextval('skill_version_seq'), ?, ?, ?, 'Deleted (archived)', ?)
                """, [skill_id, next_version, old_hash, current_content])
        
        # Delete file
        file_path.unlink()
        
        # Remove from index
        with get_manager().write_connection() as conn:
            conn.execute("DELETE FROM skill_content WHERE skill_id = ?", [skill_id])
            conn.execute("DELETE FROM skill_index WHERE id = ?", [skill_id])
        
        return ok(
            data={
                "skill_id": skill_id,
                "archived": archive,
                "file_path": str(file_path),
            },
            message=f"Deleted skill '{skill['name']}'" + (" (archived)" if archive else "")
        )
        
    except Exception as e:
        return err(f"Failed to delete skill: {str(e)}")


def get_skill_versions(skill_id: str) -> ToolResult:
    """Get version history for a skill.
    
    Args:
        skill_id: Skill ID to get history for
    
    Returns:
        ToolResult with version history
    """
    try:
        _ensure_tables()
        conn = get_manager().get_read_connection()
        
        rows = conn.execute("""
            SELECT version, content_hash, change_summary, changed_by, changed_at
            FROM skill_versions
            WHERE skill_id = ?
            ORDER BY version DESC
        """, [skill_id]).fetchall()
        
        versions = []
        for row in rows:
            versions.append({
                "version": row[0],
                "content_hash": row[1],
                "change_summary": row[2],
                "changed_by": row[3],
                "changed_at": row[4].isoformat() if row[4] else None,
            })
        
        return ok(
            data={"skill_id": skill_id, "versions": versions, "count": len(versions)},
            message=f"Found {len(versions)} versions for {skill_id}"
        )
        
    except Exception as e:
        return err(f"Failed to get versions: {str(e)}")


def restore_skill_version(skill_id: str, version: int) -> ToolResult:
    """Restore a skill to a previous version.
    
    Args:
        skill_id: Skill ID to restore
        version: Version number to restore to
    
    Returns:
        ToolResult confirming restoration
    """
    try:
        _ensure_tables()
        conn = get_manager().get_read_connection()
        
        # Get the version content
        row = conn.execute("""
            SELECT content_backup FROM skill_versions
            WHERE skill_id = ? AND version = ?
        """, [skill_id, version]).fetchone()
        
        if not row or not row[0]:
            return err(f"Version {version} not found or has no content backup")
        
        old_content = row[0]
        
        # Update the skill with old content
        result = update_skill(
            skill_id,
            content=old_content,
            change_summary=f"Restored to version {version}"
        )
        
        if result.success:
            result.message = f"Restored skill to version {version}"
        
        return result
        
    except Exception as e:
        return err(f"Failed to restore version: {str(e)}")


# =============================================================================
# Guided Skill Creation
# =============================================================================

def create_skill_from_spec(
    name: str,
    product: str,
    skill_type: str,
    spec: dict[str, Any],
    subdirectory: str | None = None,
) -> ToolResult:
    """Create a skill from a structured specification.
    
    This is the primary function for conversational skill creation.
    Claude builds the spec through conversation, then this function
    generates the formatted markdown.
    
    Args:
        name: Skill name
        product: Target product
        skill_type: Type of skill
        spec: Structured specification with content for template placeholders
        subdirectory: Optional subdirectory
    
    Returns:
        ToolResult with created skill
    """
    try:
        # Get template
        template_result = get_skill_template(skill_type)
        if not template_result.success:
            return template_result
        
        template = template_result.data['template']
        
        # Apply spec to template
        # Fill in known fields
        filled = template
        
        # Standard fields
        filled = filled.replace('{name}', spec.get('name', name))
        filled = filled.replace('{title}', spec.get('title', name.replace('-', ' ').title()))
        filled = filled.replace('{description}', spec.get('description', ''))
        filled = filled.replace('{overview}', spec.get('overview', ''))
        filled = filled.replace('{purpose}', spec.get('purpose', ''))
        
        # Build trigger list
        triggers = spec.get('trigger_phrases', [])
        triggers_list = '\n'.join([f'- {t}' for t in triggers]) if triggers else '- (add trigger phrases)'
        filled = filled.replace('{triggers_list}', triggers_list)
        filled = filled.replace('{trigger_phrases}', '\n'.join([f'- {t}' for t in triggers]))
        filled = filled.replace('{use_cases}', ', '.join(triggers[:3]) if triggers else '(specify use cases)')
        
        # Parameters table
        params = spec.get('parameters', [])
        if params:
            params_table = '\n'.join([
                f"| {p.get('name', '')} | {p.get('type', 'string')} | {p.get('default', '')} | {p.get('description', '')} |"
                for p in params
            ])
        else:
            params_table = "| (add parameters) | | | |"
        filled = filled.replace('{parameters_table}', params_table)
        
        # Clinical details (for scenarios)
        filled = filled.replace('{demographics}', spec.get('demographics', '(add demographics rules)'))
        filled = filled.replace('{conditions}', spec.get('conditions', '(add condition codes)'))
        filled = filled.replace('{medications}', spec.get('medications', '(add medication patterns)'))
        
        # Variations
        variations = spec.get('variations', [])
        if len(variations) >= 2:
            filled = filled.replace('{variation1_name}', variations[0].get('name', 'Variation 1'))
            filled = filled.replace('{variation1_description}', variations[0].get('description', ''))
            filled = filled.replace('{variation2_name}', variations[1].get('name', 'Variation 2'))
            filled = filled.replace('{variation2_description}', variations[1].get('description', ''))
        
        # Examples
        examples = spec.get('examples', [])
        if len(examples) >= 1:
            filled = filled.replace('{example1_name}', examples[0].get('name', 'Example'))
            ex1_json = examples[0].get('json', {})
            filled = filled.replace('{example1_json}', json.dumps(ex1_json, indent=2) if ex1_json else '{}')
        if len(examples) >= 2:
            filled = filled.replace('{example2_name}', examples[1].get('name', 'Example 2'))
            ex2_json = examples[1].get('json', {})
            filled = filled.replace('{example2_json}', json.dumps(ex2_json, indent=2) if ex2_json else '{}')
        
        # Validation rules
        validation_rules = spec.get('validation_rules', [])
        if validation_rules:
            rules_table = '\n'.join([
                f"| {r.get('rule', '')} | {r.get('requirement', '')} | {r.get('example', '')} |"
                for r in validation_rules
            ])
        else:
            rules_table = "| (add rules) | | |"
        filled = filled.replace('{validation_rules}', rules_table)
        
        # Related skills
        related = spec.get('related_skills', [])
        if related:
            related_text = '\n'.join([f"- [{r}]({r}.md)" for r in related])
        else:
            related_text = "- (add related skills)"
        filled = filled.replace('{related_skills}', related_text)
        
        # Template-specific fields
        filled = filled.replace('{template_spec}', json.dumps(spec.get('template_spec', {}), indent=2))
        filled = filled.replace('{example_prompt}', spec.get('example_prompt', 'Use this template'))
        filled = filled.replace('{defaults_summary}', spec.get('defaults_summary', '(defaults)'))
        
        # Custom examples for templates
        custom_examples = spec.get('customization_examples', [])
        if len(custom_examples) >= 2:
            filled = filled.replace('{custom1_name}', custom_examples[0].get('name', 'Custom 1'))
            filled = filled.replace('{custom1_example}', custom_examples[0].get('content', ''))
            filled = filled.replace('{custom2_name}', custom_examples[1].get('name', 'Custom 2'))
            filled = filled.replace('{custom2_example}', custom_examples[1].get('content', ''))
        
        filled = filled.replace('{output_table}', spec.get('output_table', '| | | |'))
        filled = filled.replace('{related_templates}', spec.get('related_templates', ''))
        
        # Pattern-specific
        filled = filled.replace('{pattern_spec}', spec.get('pattern_spec', ''))
        filled = filled.replace('{when_to_use}', spec.get('when_to_use', ''))
        filled = filled.replace('{integration_points}', spec.get('integration_points', ''))
        filled = filled.replace('{related_patterns}', spec.get('related_patterns', ''))
        
        # Integration-specific
        filled = filled.replace('{integration_purpose}', spec.get('integration_purpose', ''))
        filled = filled.replace('{source_product}', spec.get('source_product', ''))
        filled = filled.replace('{source_entities}', spec.get('source_entities', ''))
        filled = filled.replace('{target_product}', spec.get('target_product', ''))
        filled = filled.replace('{target_entities}', spec.get('target_entities', ''))
        filled = filled.replace('{mapping_rules}', spec.get('mapping_rules', ''))
        filled = filled.replace('{usage_instructions}', spec.get('usage_instructions', ''))
        
        # Clean up any remaining placeholders
        filled = re.sub(r'\{[a-z_0-9]+\}', '', filled)
        
        # Save the skill
        return save_skill(
            name=name,
            product=product,
            content=filled,
            skill_type=skill_type,
            subdirectory=subdirectory,
            validate=True,
        )
        
    except Exception as e:
        return err(f"Failed to create skill from spec: {str(e)}")


# =============================================================================
# Skill Statistics
# =============================================================================

def get_skill_stats() -> ToolResult:
    """Get statistics about the skill library.
    
    Returns:
        ToolResult with skill statistics
    """
    try:
        _ensure_tables()
        conn = get_manager().get_read_connection()
        
        # Overall stats
        total = conn.execute("SELECT COUNT(*) FROM skill_index").fetchone()[0]
        
        # By product
        by_product = conn.execute("""
            SELECT product, COUNT(*) as count
            FROM skill_index
            GROUP BY product
            ORDER BY count DESC
        """).fetchall()
        
        # By type
        by_type = conn.execute("""
            SELECT skill_type, COUNT(*) as count
            FROM skill_index
            GROUP BY skill_type
            ORDER BY count DESC
        """).fetchall()
        
        # Quality metrics
        with_examples = conn.execute("""
            SELECT COUNT(*) FROM skill_index WHERE has_examples = TRUE
        """).fetchone()[0]
        
        with_params = conn.execute("""
            SELECT COUNT(*) FROM skill_index WHERE has_parameters = TRUE
        """).fetchone()[0]
        
        # Word count stats
        word_stats = conn.execute("""
            SELECT 
                AVG(word_count) as avg,
                MIN(word_count) as min,
                MAX(word_count) as max,
                SUM(word_count) as total
            FROM skill_index
        """).fetchone()
        
        # Version count
        version_count = conn.execute("""
            SELECT COUNT(*) FROM skill_versions
        """).fetchone()[0]
        
        return ok(
            data={
                "total_skills": total,
                "by_product": [{"product": r[0], "count": r[1]} for r in by_product],
                "by_type": [{"type": r[0], "count": r[1]} for r in by_type],
                "with_examples": with_examples,
                "with_parameters": with_params,
                "word_count": {
                    "average": int(word_stats[0]) if word_stats[0] else 0,
                    "min": word_stats[1],
                    "max": word_stats[2],
                    "total": word_stats[3],
                },
                "version_count": version_count,
            },
            message=f"Skill library: {total} skills across {len(by_product)} products"
        )
        
    except Exception as e:
        return err(f"Failed to get stats: {str(e)}")
