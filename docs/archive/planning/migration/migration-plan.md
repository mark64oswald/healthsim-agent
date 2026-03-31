# HealthSim Agent Migration Plan
## Accurate Assessment Based on Actual Codebase

**Created**: January 2026  
**Purpose**: Migrate working HealthSim workspace to Anthropic Agent SDK  
**Key Insight**: This is a CODE MIGRATION, not a greenfield build

---

## Executive Summary

The HealthSim workspace contains **~20,000+ lines of working, tested Python code** across:
- State Management (cohort persistence, auto-persist, summaries)
- Generation Framework (distributions, profiles, journeys, handlers)
- MCP Server (10 tools, connection management)
- Database Layer (schema, migrations, queries)
- Skills (7 product domains with markdown documentation)

**Migration Strategy**: Port existing Python code to Agent SDK structure, converting MCP tools to Agent tools. This is NOT rebuilding from design documents.

---

## Part 1: Current Implementation Inventory

### 1.1 Python Packages to Migrate

```
packages/core/src/healthsim/
├── state/           # ~5,000 lines - MIGRATE
│   ├── manager.py           (900 lines)  - StateManager class
│   ├── auto_persist.py      (1500 lines) - Token-efficient persistence
│   ├── summary.py           (450 lines)  - CohortSummary
│   ├── serializers.py       (700 lines)  - Canonical table serialization
│   ├── journey_manager.py   (600 lines)  - Journey state
│   ├── profile_manager.py   (500 lines)  - Profile state
│   └── ... (6 more files)
│
├── generation/      # ~10,000 lines - MIGRATE
│   ├── distributions.py     (580 lines)  - 8 distribution types
│   ├── profile_schema.py    (240 lines)  - ProfileSpecification
│   ├── profile_executor.py  (510 lines)  - Execute profiles
│   ├── journey_engine.py    (1400 lines) - Journey execution
│   ├── journey_validation.py (820 lines) - Validation
│   ├── handlers.py          (1300 lines) - Product handlers
│   ├── cross_domain_sync.py (670 lines)  - Cross-product sync
│   ├── triggers.py          (470 lines)  - Event triggers
│   ├── orchestrator.py      (350 lines)  - Profile-Journey orchestration
│   ├── reference_profiles.py (660 lines) - PopulationSim integration
│   ├── networksim_reference.py (690 lines) - NPPES integration
│   ├── skill_registry.py    (550 lines)  - Skill capabilities
│   └── ... (6 more files)
│
├── db/              # ~2,500 lines - MIGRATE
│   ├── schema.py            (700 lines)  - DuckDB schema
│   ├── migrations.py        (500 lines)  - Schema migrations
│   ├── connection.py        (150 lines)  - Connection management
│   └── queries.py           (170 lines)  - Query helpers
│
├── formats/         # ~400 lines - MIGRATE
│   ├── base.py, transformer.py, utils.py
│
├── models/          # Entity models - MIGRATE
├── temporal/        # Time handling - MIGRATE
└── validation/      # Validation rules - MIGRATE
```
