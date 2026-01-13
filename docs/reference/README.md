# Reference Documentation

Technical reference documentation for HealthSim Agent developers and advanced users.

## Contents

### Architecture & Design

| Document | Description |
|----------|-------------|
| [Architecture Guide](HEALTHSIM-ARCHITECTURE-GUIDE.md) | System architecture, components, and design decisions |
| [Data Architecture](data-architecture.md) | Database schema and data relationships |
| [DuckDB Schema](healthsim-duckdb-schema.md) | Complete database schema reference |

### Commands & Tools

| Document | Description |
|----------|-------------|
| [CLI Reference](cli-reference.md) | Command-line interface commands |
| [Tools Reference](tools-reference.md) | Agent tool functions and parameters |

### Formats & Standards

| Document | Description |
|----------|-------------|
| [Output Formats](output-formats.md) | Supported export formats (FHIR, HL7v2, X12, etc.) |
| [Code Systems](code-systems.md) | Healthcare code systems (ICD-10, CPT, NDC, etc.) |

### Generation Framework

| Document | Description |
|----------|-------------|
| [Generation Framework](GENERATIVE-FRAMEWORK-USER-GUIDE.md) | Generative framework concepts and usage |
| [Integration Guide](integration-guide.md) | External system integration patterns |

### API Documentation

| Document | Description |
|----------|-------------|
| [Generation API](api/generation.md) | Entity generation functions |
| [Profile Schema](api/profile-schema.md) | Profile specification format |
| [Journey Engine](api/journey-engine.md) | Multi-step workflow system |

### Skills System

| Document | Description |
|----------|-------------|
| [Skills Overview](skills/README.md) | Skills system introduction |
| [Creating Skills](skills/creating-skills.md) | How to create new skills |
| [Format Specification](skills/format-specification-v2.md) | Skill file format reference |

## Quick Links

- [Back to Documentation Home](../README.md)
- [Getting Started](../getting-started/README.md)
- [User Guides](../guides/README.md)
- [Contributing](../contributing/README.md)

## Database Quick Reference

HealthSim Agent uses a unified DuckDB database with three schemas:

```
healthsim.duckdb
├── main (HealthSim entities)
│   ├── cohorts
│   ├── cohort_entities
│   ├── profiles
│   └── journeys
├── population (CDC/Census data)
│   ├── places_county
│   ├── places_tract
│   └── svi_county
└── network (Provider data)
    └── providers (8.9M NPPES records)
```

## Tool Categories

| Category | Tools | Purpose |
|----------|-------|---------|
| **Cohort** | list, load, save, add, delete | Manage entity collections |
| **Query** | query, summary, tables | Database queries |
| **Reference** | query_reference, search_providers | Provider/population lookups |
| **Format** | transform_to_fhir, transform_to_x12, etc. | Output format conversion |
| **Validation** | validate_data, fix_validation_issues | Data quality checks |
| **Skills** | search, get, save, validate | Skills management |
| **Generation** | generate_patients, generate_members, etc. | Entity generation |
| **Profile** | save_profile, load_profile, execute_profile | Reusable specifications |
| **Journey** | create_journey, execute_journey | Multi-step workflows |
