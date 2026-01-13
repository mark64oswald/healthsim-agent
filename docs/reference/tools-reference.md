# Tools Reference

HealthSim Agent provides a comprehensive set of tools for data generation, management, and export. This reference documents all available tools, their parameters, and usage patterns.

## Overview

Tools are organized into categories:

| Category | Purpose | Tools |
|----------|---------|-------|
| **Cohort** | Entity collection management | list_cohorts, load_cohort, save_cohort, add_entities, delete_cohort |
| **Query** | Database operations | query, get_summary, list_tables |
| **Reference** | Real data lookups | query_reference, search_providers |
| **Format** | Output transformations | transform_to_fhir, transform_to_ccda, transform_to_hl7v2, transform_to_x12, transform_to_ncpdp, transform_to_mimic |
| **Validation** | Data quality | validate_data, fix_validation_issues |
| **Skills** | Skills management | search_skills, get_skill, save_skill, validate_skill, index_skills |
| **Generation** | Entity generation | generate_patients, generate_members, generate_claims, generate_prescriptions, generate_trial_subjects |
| **Profile** | Reusable specs | save_profile, load_profile, list_profiles, execute_profile, delete_profile |
| **Journey** | Workflows | create_journey, list_journeys, execute_journey, delete_journey |

## Tool Result Pattern

All tools return a `ToolResult` object:

```python
class ToolResult:
    success: bool      # True if operation succeeded
    data: Any          # Result data on success
    error: str | None  # Error message on failure
```

---

## Cohort Tools

### list_cohorts

List all saved cohorts with summary information.

```python
list_cohorts(
    limit: int = 50,           # Maximum cohorts to return
    include_counts: bool = True # Include entity counts
) -> ToolResult
```

**Returns:** List of cohorts with id, name, description, entity_count, created_at

---

### load_cohort

Load a cohort by ID or name.

```python
load_cohort(
    cohort_id: str,              # Cohort ID or name
    entity_types: list[str] = None  # Filter by entity type
) -> ToolResult
```

**Returns:** Cohort data with all entities grouped by type

---

### save_cohort

Create a new cohort.

```python
save_cohort(
    name: str,                 # Cohort name (unique)
    description: str = None,   # Optional description
    tags: list[str] = None,    # Tags for organization
    metadata: dict = None      # Additional metadata
) -> ToolResult
```

**Returns:** New cohort with generated ID

---

### add_entities

Add entities to an existing cohort.

```python
add_entities(
    cohort_id: str,           # Target cohort ID or name
    entities: list[dict],     # Entity data list
    entity_type: str          # Type: patient, member, claim, etc.
) -> ToolResult
```

**Returns:** Count of added entities

---

### delete_cohort

Delete a cohort and all its entities.

```python
delete_cohort(
    cohort_id: str  # Cohort ID or name
) -> ToolResult
```

**Returns:** Confirmation of deletion

---

## Query Tools

### query

Execute SQL against the database.

```python
query(
    sql: str,           # SQL statement
    params: list = None # Query parameters
) -> ToolResult
```

**Returns:** Query results as list of dicts

**Available schemas:**
- `main` - cohorts, cohort_entities, profiles, journeys
- `network` - providers (NPPES)
- `population` - places_county, places_tract, svi_county

---

### get_summary

Get token-efficient summary of a cohort.

```python
get_summary(
    cohort_id: str  # Cohort ID or name
) -> ToolResult
```

**Returns:** Entity counts, sample records, metadata

---

### list_tables

List available database tables.

```python
list_tables(
    schema: str = None  # Filter by schema
) -> ToolResult
```

**Returns:** Table names with row counts

---

## Reference Tools

### query_reference

Query reference data (population, providers).

```python
query_reference(
    data_type: str,           # Type: places, svi, providers
    filters: dict = None,     # Filter criteria
    limit: int = 100          # Max results
) -> ToolResult
```

**Data types:**
- `places_county` - CDC PLACES county health data
- `places_tract` - CDC PLACES tract level data
- `svi_county` - Social Vulnerability Index
- `providers` - NPPES provider directory

---

### search_providers

Search NPPES provider database.

```python
search_providers(
    state: str = None,          # 2-letter state code
    city: str = None,           # City name
    county: str = None,         # County name  
    specialty: str = None,      # Provider specialty
    taxonomy_code: str = None,  # Healthcare taxonomy code
    entity_type: str = None,    # 1=individual, 2=organization
    npi: str = None,            # Specific NPI lookup
    limit: int = 100            # Max results
) -> ToolResult
```

**Returns:** Provider records with NPI, name, address, specialty

---

## Format Tools

### transform_to_fhir

Transform cohort to FHIR R4 Bundle.

```python
transform_to_fhir(
    cohort_id: str,              # Source cohort
    resource_types: list = None  # Filter resources
) -> ToolResult
```

**Returns:** FHIR Bundle with Patient, Encounter, Condition, etc.

---

### transform_to_ccda

Transform to C-CDA document.

```python
transform_to_ccda(
    cohort_id: str,          # Source cohort
    document_type: str = "CCD"  # CCD, Discharge, Referral
) -> ToolResult
```

**Returns:** C-CDA XML document

---

### transform_to_hl7v2

Transform to HL7 v2.x messages.

```python
transform_to_hl7v2(
    cohort_id: str,            # Source cohort
    message_type: str = "ADT"  # ADT, ORU, ORM, etc.
) -> ToolResult
```

**Returns:** HL7v2 messages (pipe-delimited)

---

### transform_to_x12

Transform to X12 EDI format.

```python
transform_to_x12(
    cohort_id: str,            # Source cohort
    transaction_set: str       # 837P, 837I, 835, 834, 270, 271
) -> ToolResult
```

**Returns:** X12 EDI transaction

---

### transform_to_ncpdp

Transform pharmacy data to NCPDP format.

```python
transform_to_ncpdp(
    cohort_id: str,           # Source cohort
    format_type: str = "D0"   # D0 (Telecom), SCRIPT
) -> ToolResult
```

**Returns:** NCPDP formatted data

---

### transform_to_mimic

Transform to MIMIC-style format.

```python
transform_to_mimic(
    cohort_id: str  # Source cohort
) -> ToolResult
```

**Returns:** Data in MIMIC table structure

---

### list_output_formats

List all available output formats.

```python
list_output_formats() -> ToolResult
```

**Returns:** Format names, descriptions, supported entity types

---

## Validation Tools

### validate_data

Validate entity data against schema.

```python
validate_data(
    data: list[dict],    # Entities to validate
    entity_type: str,    # patient, member, claim, etc.
    strict: bool = False # Fail on warnings
) -> ToolResult
```

**Returns:**
```json
{
    "valid": true,
    "errors": [],
    "warnings": [],
    "entity_count": 10,
    "validation_details": {}
}
```

---

### fix_validation_issues

Auto-fix common validation issues.

```python
fix_validation_issues(
    data: list[dict],    # Entities to fix
    entity_type: str,    # patient, member, claim, etc.
    fixes: list = None   # Specific fixes to apply
) -> ToolResult
```

**Auto-fixes:**
- Date format normalization
- Code system formatting
- Missing required fields (with defaults)
- Invalid enum values

---

## Skills Tools

### search_skills

Search skills by keyword or product.

```python
search_skills(
    query: str = None,        # Search query
    product: str = None,      # Filter by product
    tags: list[str] = None,   # Filter by tags
    limit: int = 20           # Max results
) -> ToolResult
```

**Returns:** Matching skills with name, description, path

---

### get_skill

Get a specific skill by name or path.

```python
get_skill(
    skill_name: str,       # Skill name or path
    include_content: bool = True  # Include full content
) -> ToolResult
```

**Returns:** Skill metadata and content

---

### index_skills

Rebuild the skills index.

```python
index_skills(
    force: bool = False  # Force re-index all
) -> ToolResult
```

**Returns:** Index statistics (skill count, products, tags)

---

### validate_skill

Validate a skill file format.

```python
validate_skill(
    content: str  # Skill markdown content
) -> ToolResult
```

**Returns:** Validation result with errors/warnings

---

### get_skill_stats

Get statistics about loaded skills.

```python
get_skill_stats() -> ToolResult
```

**Returns:**
```json
{
    "total_skills": 175,
    "by_product": {
        "patientsim": 45,
        "membersim": 38,
        ...
    },
    "by_category": {...}
}
```

---

## Generation Tools

### generate_patients

Generate synthetic patient data.

```python
generate_patients(
    count: int = 1,                      # Number to generate (1-100)
    age_range: tuple[int, int] = None,   # (min, max) age
    gender: str = None,                  # male, female, or random
    include_encounters: bool = False,    # Add encounters
    include_diagnoses: bool = False,     # Add conditions
    include_vitals: bool = False,        # Add vital signs
    include_labs: bool = False,          # Add lab results
    include_medications: bool = False,   # Add medications
    diagnosis_categories: list = None,   # Filter diagnoses
    seed: int = None                     # Reproducibility
) -> ToolResult
```

---

### generate_members

Generate member/subscriber data.

```python
generate_members(
    count: int = 1,
    plan_type: str = None,    # HMO, PPO, etc.
    coverage_type: str = None, # Individual, Family
    age_range: tuple = None,
    seed: int = None
) -> ToolResult
```

---

### generate_claims

Generate healthcare claims.

```python
generate_claims(
    member_id: str = None,      # Link to member
    claim_type: str = "professional",  # professional, institutional, pharmacy
    count: int = 1,
    date_range: tuple = None,   # (start, end) dates
    diagnosis_codes: list = None,
    seed: int = None
) -> ToolResult
```

---

### generate_prescriptions

Generate pharmacy prescriptions.

```python
generate_prescriptions(
    member_id: str = None,
    count: int = 1,
    drug_categories: list = None,
    include_dur: bool = False,   # Drug utilization review
    include_pricing: bool = True,
    seed: int = None
) -> ToolResult
```

---

### generate_trial_subjects

Generate clinical trial subjects.

```python
generate_trial_subjects(
    protocol_id: str = None,
    count: int = 1,
    include_visits: bool = True,
    include_ae: bool = True,      # Adverse events
    include_labs: bool = True,
    randomization_ratio: tuple = (1, 1),  # Treatment:Control
    seed: int = None
) -> ToolResult
```

---

## Profile Tools

### save_profile

Save a generation profile.

```python
save_profile(
    name: str,                # Profile name (unique)
    spec: dict,               # Generation specification
    description: str = None,
    product: str = None,      # patientsim, membersim, etc.
    tags: list[str] = None
) -> ToolResult
```

---

### load_profile

Load a profile by name.

```python
load_profile(
    name: str  # Profile name
) -> ToolResult
```

---

### execute_profile

Execute a profile to generate data.

```python
execute_profile(
    name: str,              # Profile name
    count: int = 1,         # Override count
    cohort_name: str = None, # Target cohort
    seed: int = None        # Reproducibility
) -> ToolResult
```

---

## Journey Tools

### create_journey

Create a multi-step journey.

```python
create_journey(
    name: str,           # Journey name (unique)
    steps: list[dict],   # Step definitions
    description: str = None,
    tags: list[str] = None
) -> ToolResult
```

**Step format:**
```json
{
    "name": "step-name",
    "action": "generate_patients",
    "params": {...},
    "depends_on": ["previous-step"]
}
```

---

### execute_journey

Execute a journey workflow.

```python
execute_journey(
    name: str,               # Journey name
    params: dict = None,     # Override parameters
    cohort_name: str = None, # Target cohort
    seed: int = None
) -> ToolResult
```

**Returns:** Step-by-step execution results

---

## Related Documentation

- [CLI Reference](cli-reference.md) - Command-line interface
- [Output Formats](output-formats.md) - Format specifications
- [Generation Framework](GENERATIVE-FRAMEWORK-USER-GUIDE.md) - Generation concepts
