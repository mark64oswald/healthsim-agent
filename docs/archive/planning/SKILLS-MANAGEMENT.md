# Skills Management System

This document describes the Skills Management system that enables conversational skill creation, modification, and discovery in HealthSim Agent.

## Overview

Skills are the primary knowledge containers in HealthSim. They define:
- Clinical scenarios (e.g., diabetes management, ED chest pain)
- Generation patterns (e.g., chronic disease journeys)
- Integration mappings (e.g., provider-for-encounter)
- Ready-to-use templates (e.g., Medicare diabetic profile)

The Skills Management system enables users to **create, modify, and discover skills through natural language conversation** without writing Python code.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    User Conversation                         │
│  "Create a skill for post-surgical infection scenarios"      │
└─────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                     Skill Tools API                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │ index_skills│  │search_skills│  │ create_skill_from_  │  │
│  │             │  │             │  │ spec                │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │ save_skill  │  │update_skill │  │ validate_skill      │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                             │
              ┌──────────────┴──────────────┐
              ▼                              ▼
┌──────────────────────┐      ┌─────────────────────────────┐
│   Markdown Files     │      │       DuckDB Index          │
│   skills/{product}/  │      │  - skill_index (search)     │
│   *.md              │      │  - skill_content (full-text)│
│   (git-tracked)      │      │  - skill_versions (history) │
└──────────────────────┘      └─────────────────────────────┘
```

## Skill Types

| Type | Description | Examples |
|------|-------------|----------|
| `scenario` | Clinical or domain scenarios | diabetes-management, ed-chest-pain |
| `pattern` | Reusable generation patterns | tiered-network, hmo-network |
| `template` | Ready-to-use profiles | medicare-diabetic, commercial-family |
| `integration` | Cross-product mappings | provider-for-encounter, formulary-for-rx |
| `query` | Analytics and query skills | provider-search, coverage-analysis |
| `reference` | Reference data skills | code-systems, data-models |
| `workflow` | Multi-step workflows | adt-workflow, care-transition |

## Conversational Workflows

### 1. Discovering Skills

```
User: "What skills do you have for diabetes?"

Agent: [calls search_skills("diabetes")]

Agent: "I found 5 diabetes-related skills:
- patientsim/diabetes-management (scenario) - Comprehensive T2DM cohorts
- generation/templates/profiles/medicare-diabetic (template) - Medicare diabetic profile
- generation/templates/profiles/commercial-diabetic (template) - Commercial diabetic profile  
- generation/templates/journeys/diabetic-first-year (template) - First year journey
- generation/templates/journeys/diabetic-annual (template) - Annual care cycle

Would you like details on any of these?"
```

### 2. Creating a New Skill

```
User: "Create a skill for simulating post-surgical infection scenarios"

Agent: "I'll help you create a post-surgical infection skill. Let me gather some details:

1. Which product should this be for? (PatientSim, MemberSim, etc.)
2. What types of surgeries should be covered?
3. What pathogens/infection types?
4. What's the typical timeline (onset, treatment, resolution)?
5. Any specific complications to model?"

User: "PatientSim. Focus on orthopedic surgeries - hip and knee replacements.
Common pathogens: Staph aureus, Strep, Pseudomonas. 
Timeline: onset 3-14 days post-op, treatment 2-6 weeks antibiotics.
Complications: wound dehiscence, sepsis, prosthetic loosening."

Agent: [builds skill spec from conversation]
       [calls create_skill_from_spec(...)]

Agent: "Created skill 'post-surgical-infection' in PatientSim!

**Summary:**
- Triggers: surgical site infection, post-op infection, SSI, wound infection
- Covers: Hip/knee replacement with Staph, Strep, Pseudomonas infections
- Timeline: 3-14 day onset, 2-6 week treatment
- Complications: dehiscence, sepsis, prosthetic loosening
- Quality score: 92/100

You can now use it: 'Generate 10 patients with post-surgical infections after knee replacement'"
```

### 3. Updating an Existing Skill

```
User: "Add GLP-1 weight loss patterns to the diabetes-management skill"

Agent: [calls get_skill("patientsim/diabetes-management")]
       [identifies medication section]
       [calls update_skill(..., append_section={...})]

Agent: "Updated diabetes-management skill (now version 3):

Added to Medications section:
- GLP-1 weight loss patterns
- Semaglutide/tirzepatide dosing
- Expected weight loss trajectories (5-15% body weight over 6-12 months)
- A1C improvement correlation

The skill now covers GLP-1 medications for both glycemic control and weight management."
```

### 4. Creating from Templates

```
User: "Create a new profile template for Medicaid pregnant members"

Agent: [calls get_skill_template("template")]
       [guides user through customization]

Agent: "I'll create a Medicaid maternity profile template. Key questions:

1. Age range for the pregnant population?
2. What comorbidities should be modeled? (GDM, preeclampsia, etc.)
3. What coverage details? (Medicaid expansion, CHIP pregnancy coverage)
4. Trimester distribution at generation time?"

User: "Age 18-40, weight toward 20-30. 
Comorbidities: 15% gestational diabetes, 8% preeclampsia, 20% anemia.
Medicaid expansion states. Generate across all trimesters equally."

Agent: [calls create_skill_from_spec(..., skill_type="template")]

Agent: "Created 'medicaid-maternity' template in generation/templates/profiles!

Quick start: 'Use the Medicaid maternity template for 50 members'"
```

## API Reference

### Index and Search

```python
# Index all skills (run after adding/modifying skills)
index_skills(product=None, force=False)

# Search skills by keyword, product, type, or tags
search_skills(query, product=None, skill_type=None, tags=None, limit=20)

# Get full skill content
get_skill(skill_id)

# List products with skill counts
list_skill_products()
```

### CRUD Operations

```python
# Save a new skill
save_skill(name, product, content, skill_type="scenario", subdirectory=None, validate=True)

# Update existing skill
update_skill(skill_id, content=None, append_section=None, update_frontmatter=None)

# Delete a skill (archives by default)
delete_skill(skill_id, archive=True)
```

### Validation

```python
# Validate skill content
validate_skill(content, skill_type=None, strict=False)
```

### Versioning

```python
# Get version history
get_skill_versions(skill_id)

# Restore to previous version
restore_skill_version(skill_id, version)
```

### Templates and Creation

```python
# Get template for skill type
get_skill_template(skill_type)  # scenario, template, pattern, integration

# Create skill from structured spec (used by Claude)
create_skill_from_spec(name, product, skill_type, spec, subdirectory=None)
```

### Statistics

```python
# Get skill library statistics
get_skill_stats()
```

## Skill Structure Requirements

### Required YAML Frontmatter

```yaml
---
name: skill-name
description: "Brief description. Triggers: keyword1, keyword2, keyword3"
---
```

### Required Sections by Type

| Type | Required Sections |
|------|-------------------|
| scenario | Purpose, Parameters, Generation Rules, Examples |
| template | Quick Start, Template Specification, Customization Examples |
| pattern | Purpose, Pattern Specification, Examples |
| integration | Purpose, Integration Points, Examples |

### Quality Indicators

- **Examples**: At least 2 complete JSON examples
- **Trigger Phrases**: Clear keywords for skill activation
- **Parameters Table**: Documented customization options
- **Related Skills**: Cross-product links

## Best Practices

### For Users Creating Skills

1. **Be specific about trigger phrases** - These determine when the skill activates
2. **Provide complete examples** - JSON examples teach the generation pattern
3. **Document variations** - Different scenarios within the skill
4. **Link related skills** - Enable cross-product workflows

### For the Agent

1. **Always index after changes** - Keep the search index current
2. **Validate before saving** - Ensure quality standards
3. **Archive before deleting** - Maintain version history
4. **Guide users through creation** - Ask clarifying questions

## Database Schema

### skill_index
Primary skill metadata for fast searching.

| Column | Type | Description |
|--------|------|-------------|
| id | VARCHAR | Unique skill ID (product/name) |
| name | VARCHAR | Skill name |
| product | VARCHAR | Product (patientsim, membersim, etc.) |
| skill_type | VARCHAR | Type (scenario, template, pattern, etc.) |
| description | VARCHAR | Brief description |
| trigger_phrases | JSON | List of trigger keywords |
| file_path | VARCHAR | Absolute file path |
| relative_path | VARCHAR | Path relative to skills/ |
| subdirectory | VARCHAR | Subdirectory within product |
| tags | JSON | List of tags |
| related_skills | JSON | Links to related skills |
| word_count | INTEGER | Content word count |
| has_examples | BOOLEAN | Has Examples section |
| has_parameters | BOOLEAN | Has Parameters table |
| content_hash | VARCHAR | MD5 hash for change detection |

### skill_content
Full-text content for semantic search.

| Column | Type | Description |
|--------|------|-------------|
| skill_id | VARCHAR | Foreign key to skill_index |
| full_text | VARCHAR | Complete markdown content |
| sections | JSON | Parsed section map |
| code_blocks | JSON | Extracted code blocks |

### skill_versions
Version history for rollback.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Version record ID |
| skill_id | VARCHAR | Skill being versioned |
| version | INTEGER | Version number |
| content_hash | VARCHAR | Hash of this version |
| change_summary | VARCHAR | Description of changes |
| changed_by | VARCHAR | Who made the change |
| changed_at | TIMESTAMP | When changed |
| content_backup | VARCHAR | Full content backup |
