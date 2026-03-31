# HealthSim Skills Management System

## Project Document

**Version:** 1.0  
**Date:** January 2026  
**Status:** Implemented  

---

## Executive Summary

The Skills Management System enables users to extend HealthSim Agent's knowledge and capabilities through natural language conversation, without writing Python code. Skills are markdown files containing domain knowledge, generation patterns, and examples that guide Claude in generating synthetic healthcare data.

### Key Capabilities

| Capability | Description |
|------------|-------------|
| **Conversational Creation** | Users describe what they need, Claude builds the skill |
| **Version Control** | Full version history with restore capability |
| **Cross-Product Integration** | Skills can reference and integrate with other products |
| **Validation** | Automatic structure and quality validation |
| **Fast Search** | DuckDB-indexed full-text search across all skills |

---

## Design Philosophy

### Why Skills?

Skills solve a fundamental problem: **How do users extend an AI system's domain knowledge without programming?**

Traditional approaches require:
- Writing Python code to add new generators
- Modifying configuration files
- Understanding internal APIs

HealthSim's approach:
- **Markdown files** that humans can read and write
- **Natural language conversations** to create and modify
- **Structured templates** that ensure consistency
- **Automatic indexing** for discovery and search

### The Skill as Knowledge Container

A skill is a self-contained unit of domain knowledge:

```
┌─────────────────────────────────────────────────────────┐
│ YAML Frontmatter                                        │
│   name, description, trigger phrases                    │
├─────────────────────────────────────────────────────────┤
│ For Claude                                              │
│   When to apply, what it enables                        │
├─────────────────────────────────────────────────────────┤
│ Parameters                                              │
│   Input specifications                                  │
├─────────────────────────────────────────────────────────┤
│ Generation Rules                                        │
│   Domain-specific logic, codes, patterns                │
├─────────────────────────────────────────────────────────┤
│ Examples                                                │
│   JSON output examples (at least 2)                     │
├─────────────────────────────────────────────────────────┤
│ Validation Rules                                        │
│   Quality constraints                                   │
├─────────────────────────────────────────────────────────┤
│ Related Skills                                          │
│   Cross-references to other skills                      │
└─────────────────────────────────────────────────────────┘
```

---

## Architecture

### Component Overview

```
┌──────────────────────────────────────────────────────────────┐
│                     User Conversation                         │
│                                                              │
│  "I want to create a skill for post-surgical infections"    │
└──────────────────────────────┬───────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────┐
│                    Skill Management Tools                     │
│                                                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐   │
│  │   Search    │  │   CRUD      │  │  Version Control    │   │
│  │   & Index   │  │   Ops       │  │  & Templates        │   │
│  └─────────────┘  └─────────────┘  └─────────────────────┘   │
└──────────────────────────────┬───────────────────────────────┘
                               │
           ┌───────────────────┼───────────────────┐
           │                   │                   │
           ▼                   ▼                   ▼
    ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
    │  DuckDB     │     │  Markdown   │     │   Git       │
    │  Index      │     │  Files      │     │  History    │
    │             │     │             │     │             │
    │ - Full-text │     │ skills/     │     │ Version     │
    │ - Metadata  │     │  patientsim/│     │ tracking    │
    │ - Triggers  │     │  membersim/ │     │ via backup  │
    └─────────────┘     │  trialsim/  │     └─────────────┘
                        │  ...        │
                        └─────────────┘
```

### File Organization

```
skills/
├── patientsim/           # Clinical/EMR scenarios
│   ├── SKILL.md          # Product overview
│   ├── diabetes-management.md
│   ├── ed-chest-pain.md
│   ├── oncology/         # Subdomain
│   │   ├── breast-cancer.md
│   │   └── lung-cancer.md
│   └── pediatrics/       # Subdomain
│       ├── childhood-asthma.md
│       └── acute-otitis-media.md
├── membersim/            # Claims/Payer scenarios
├── trialsim/             # Clinical trials
├── rxmembersim/          # Pharmacy
├── populationsim/        # Demographics
├── networksim/           # Provider networks
├── common/               # Shared patterns
└── generation/           # Generation patterns
```

### Database Schema

```sql
-- Main skill index for fast search
CREATE TABLE skill_index (
    id              VARCHAR PRIMARY KEY,    -- e.g., "patientsim/diabetes-management"
    name            VARCHAR NOT NULL,
    product         VARCHAR NOT NULL,
    skill_type      VARCHAR,                -- scenario, pattern, template, integration
    description     VARCHAR,
    trigger_phrases JSON,                   -- ["diabetes", "T2DM", "blood sugar"]
    file_path       VARCHAR NOT NULL,
    relative_path   VARCHAR NOT NULL,
    subdirectory    VARCHAR,
    tags            JSON,
    related_skills  JSON,
    word_count      INTEGER,
    has_examples    BOOLEAN DEFAULT FALSE,
    has_parameters  BOOLEAN DEFAULT FALSE,
    indexed_at      TIMESTAMP,
    content_hash    VARCHAR                 -- For change detection
);

-- Full content for semantic search
CREATE TABLE skill_content (
    skill_id        VARCHAR PRIMARY KEY,
    full_text       VARCHAR,
    sections        JSON,                   -- Parsed markdown sections
    code_blocks     JSON,                   -- Extracted examples
    indexed_at      TIMESTAMP
);

-- Version history
CREATE TABLE skill_versions (
    id              INTEGER PRIMARY KEY,
    skill_id        VARCHAR NOT NULL,
    version         INTEGER NOT NULL,
    content_hash    VARCHAR,
    change_summary  VARCHAR,
    changed_by      VARCHAR DEFAULT 'user',
    changed_at      TIMESTAMP,
    content_backup  VARCHAR                 -- Full content for restore
);
```

---

## API Reference

### Index & Search

#### `index_skills(product, force)`
Indexes all skills into DuckDB for fast search.

```python
# Index all skills
result = index_skills()
# {"indexed": 213, "skipped": 0, "errors": []}

# Force re-index for one product
result = index_skills(product="patientsim", force=True)
```

#### `search_skills(query, product, skill_type, tags, limit)`
Search skills by keyword across name, description, triggers, and content.

```python
# Search for diabetes-related skills
result = search_skills("diabetes")
# Returns matching skills with relevance ranking

# Filter by product and type
result = search_skills("claims", product="membersim", skill_type="scenario")
```

#### `get_skill(skill_id)`
Get full skill content and metadata.

```python
result = get_skill("patientsim/diabetes-management")
# Returns complete skill with content, sections, metadata
```

### CRUD Operations

#### `save_skill(name, product, content, skill_type, subdirectory, validate, overwrite)`
Create a new skill from markdown content.

```python
content = '''---
name: post-surgical-infection
description: "Post-operative surgical site infections. Triggers: SSI, wound infection, post-op infection"
---

# Post-Surgical Infection

## For Claude
Use this skill when generating patients with surgical site infections...
'''

result = save_skill(
    name="post-surgical-infection",
    product="patientsim",
    content=content,
    skill_type="scenario"
)
```

#### `update_skill(skill_id, content, append_section, update_frontmatter, change_summary)`
Update an existing skill with version tracking.

```python
# Full content replacement
result = update_skill("patientsim/diabetes-management", content=new_content)

# Append a new section
result = update_skill(
    "patientsim/diabetes-management",
    append_section={
        "section_name": "GLP-1 Medications",
        "content": "New content about semaglutide..."
    },
    change_summary="Added GLP-1 medication section"
)

# Update frontmatter only
result = update_skill(
    "patientsim/diabetes-management",
    update_frontmatter={"description": "Updated description..."}
)
```

#### `delete_skill(skill_id, archive)`
Delete a skill with optional archiving.

```python
# Delete and archive (default)
result = delete_skill("patientsim/old-skill")

# Delete without archive
result = delete_skill("patientsim/old-skill", archive=False)
```

### Version Control

#### `get_skill_versions(skill_id)`
Get version history for a skill.

```python
result = get_skill_versions("patientsim/diabetes-management")
# Returns list of versions with timestamps, hashes, change summaries
```

#### `restore_skill_version(skill_id, version)`
Restore a skill to a previous version.

```python
result = restore_skill_version("patientsim/diabetes-management", version=2)
```

### Templates & Creation

#### `get_skill_template(skill_type)`
Get a template for creating a new skill.

```python
result = get_skill_template("scenario")
# Returns template with placeholders and guidance
```

#### `create_skill_from_spec(name, product, skill_type, spec, subdirectory)`
Create a skill from a structured specification (primary for conversational creation).

```python
spec = {
    "name": "post-surgical-infection",
    "title": "Post-Surgical Infection",
    "description": "Surgical site infections following procedures",
    "trigger_phrases": ["SSI", "wound infection", "post-op infection"],
    "parameters": [
        {"name": "surgery_type", "type": "string", "description": "Type of surgery"},
        {"name": "days_post_op", "type": "integer", "description": "Days since surgery"}
    ],
    "demographics": "Adults 30-80, surgery patients",
    "conditions": "T81.4 - Infection following procedure",
    "medications": "Antibiotics: vancomycin, piperacillin-tazobactam",
    "examples": [
        {"name": "Superficial SSI", "json": {...}},
        {"name": "Deep SSI with Sepsis", "json": {...}}
    ],
    "validation_rules": [
        {"rule": "days_post_op", "requirement": "1-30 days", "example": "5"}
    ]
}

result = create_skill_from_spec(
    name="post-surgical-infection",
    product="patientsim",
    skill_type="scenario",
    spec=spec
)
```

### Statistics

#### `get_skill_stats()`
Get library-wide statistics.

```python
result = get_skill_stats()
# {
#   "total_skills": 213,
#   "by_product": [{"product": "patientsim", "count": 40}, ...],
#   "by_type": [{"type": "scenario", "count": 120}, ...],
#   "with_examples": 200,
#   "word_count": {"average": 450, "total": 95000},
#   "version_count": 47
# }
```

---

## Skill Types

| Type | Purpose | Example |
|------|---------|---------|
| **scenario** | Clinical/domain scenarios for generation | `diabetes-management.md` |
| **pattern** | Reusable generation patterns | `tiered-network-pattern.md` |
| **template** | Ready-to-use profile specifications | `medicare-diabetic-template.md` |
| **integration** | Cross-product mappings | `provider-for-encounter.md` |
| **query** | Analytics/query patterns | `provider-search.md` |
| **reference** | Reference data documentation | `code-systems.md` |
| **workflow** | Multi-step workflows | `adt-workflow.md` |

---

## Conversational Workflow

### Creating a New Skill

```
User: "I want to create a skill for simulating post-surgical infections"

Claude: "I'll help you create that skill. Let me ask a few questions:

1. What types of surgeries should trigger this? (orthopedic, cardiac, abdominal, etc.)
2. What's the typical timeline for infection onset?
3. What pathogens are most common?
4. What complications should we model?"

User: "Focus on orthopedic surgeries like hip and knee replacements. 
Infections usually appear 3-14 days post-op. 
Common pathogens are Staph aureus and MRSA.
Complications include sepsis and return to OR."

Claude: "I'll create this skill with:
- Trigger phrases: SSI, post-op infection, wound infection, surgical infection
- Parameters: surgery_type, days_post_op, pathogen
- Conditions: T81.4 series codes
- Common scenarios: superficial SSI, deep SSI, sepsis

Creating skill..."

[Claude calls create_skill_from_spec()]

Claude: "Created skill 'post-surgical-infection' in patientsim.
Quality score: 85/100.

You can now generate infected patients with:
'Generate 5 patients with post-surgical knee replacement infections'"
```

### Updating an Existing Skill

```
User: "Add information about antibiotic resistance patterns to the 
diabetes-management skill"

Claude: "I'll append a new section about antibiotic resistance for diabetic patients.
This is relevant since diabetic foot infections often involve resistant organisms."

[Claude calls update_skill() with append_section]

Claude: "Updated diabetes-management skill to version 4.
Added 'Antibiotic Resistance Patterns' section covering:
- MRSA prevalence in diabetic wounds
- Pseudomonas in chronic wounds
- Empiric coverage recommendations"
```

### Restoring a Previous Version

```
User: "The last update to the heart-failure skill broke something.
Can you restore the previous version?"

[Claude calls get_skill_versions()]

Claude: "Found 3 versions of heart-failure skill:
- v3 (current): Added SGLT2i section - Jan 10, 2026
- v2: Updated EF ranges - Jan 8, 2026  
- v1: Initial creation - Jan 5, 2026

Which version would you like to restore?"

User: "Version 2"

[Claude calls restore_skill_version()]

Claude: "Restored heart-failure skill to version 2.
Current version is now 4 (restoration creates new version)."
```

---

## Validation

### Required Elements

| Element | Location | Purpose |
|---------|----------|---------|
| `name` | YAML frontmatter | Unique identifier |
| `description` | YAML frontmatter | Brief description with trigger phrases |

### Recommended Sections

| Section | Purpose |
|---------|---------|
| `For Claude` | AI guidance on when and how to use |
| `Parameters` | Input specification table |
| `Generation Rules` | Domain-specific rules and codes |
| `Examples` | At least 2 JSON examples |
| `Validation Rules` | Quality constraints |
| `Related Skills` | Cross-references |

### Quality Score

Skills are scored 0-100 based on:
- Required fields present (-15 per missing)
- Recommended sections present (-5 per missing)
- Has JSON examples
- Has trigger phrases
- Word count (minimum 200 words)

---

## Integration with Generation

When Claude generates data, it:

1. **Matches trigger phrases** from the user's request
2. **Loads relevant skills** via `search_skills()`
3. **Applies generation rules** from the skill
4. **Follows examples** for output format
5. **Validates output** against validation rules

### Example Flow

```
User: "Generate a diabetic patient with CKD"

Claude's internal process:
1. search_skills("diabetes CKD") → finds diabetes-management.md, chronic-kidney-disease.md
2. Loads both skills
3. Combines rules:
   - A1C patterns from diabetes skill
   - eGFR/creatinine from CKD skill
   - Comorbidity rules (75% overlap expected)
4. Generates patient with both conditions
5. Validates against both skill's rules
```

---

## Best Practices

### Writing Effective Skills

1. **Clear trigger phrases** - Be specific about when to use
2. **Complete examples** - Show realistic output
3. **Domain accuracy** - Use correct codes (ICD-10, LOINC, etc.)
4. **Cross-references** - Link to related skills
5. **Validation rules** - Define quality constraints

### Organizing Skills

1. **Use subdirectories** for specialty areas (oncology/, pediatrics/)
2. **Keep skills focused** - One scenario per skill
3. **Maintain consistency** - Follow the product's existing patterns
4. **Version thoughtfully** - Include meaningful change summaries

### Performance

1. **Run `index_skills()`** after bulk changes
2. **Use specific products** in searches when possible
3. **Archive rather than delete** to preserve history

---

## Current Statistics

As of January 2026:

| Product | Skills | With Examples |
|---------|--------|---------------|
| PatientSim | ~40 | 38 |
| MemberSim | ~35 | 33 |
| RxMemberSim | ~25 | 24 |
| TrialSim | ~20 | 19 |
| PopulationSim | ~17 | 16 |
| NetworkSim | ~12 | 11 |
| Common | 7 | 7 |
| Generation | 9 | 9 |
| **Total** | **~213** | **~200** |

---

## Future Enhancements

| Enhancement | Priority | Description |
|-------------|----------|-------------|
| Semantic search | Medium | Use embeddings for better skill matching |
| Skill dependencies | Medium | Automatic loading of prerequisite skills |
| Skill marketplace | Low | Share skills between HealthSim instances |
| Visual editor | Low | Web UI for skill editing |

---

## Conclusion

The Skills Management System transforms HealthSim from a static tool into a **continuously extensible platform**. Users can:

1. **Discover** existing knowledge through search
2. **Create** new scenarios through conversation
3. **Evolve** skills over time with version control
4. **Integrate** knowledge across products

This enables the "conversation-first" philosophy: users describe what they need, and the system adapts its knowledge base accordingly.
