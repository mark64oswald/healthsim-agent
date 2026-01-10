# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added - Phase 3: Skills Integration (January 10, 2026)
- `src/healthsim_agent/skills/models.py` - Data models for parsed skills
  - SkillMetadata: YAML frontmatter parsing with trigger extraction
  - ParsedSkill: Full skill representation with path, content, configs
  - EmbeddedConfig: Structured data from YAML/JSON code blocks
  - SkillIndex: Efficient indexing by name, trigger, and product
- `src/healthsim_agent/skills/loader.py` - Hybrid skill parser
  - YAML frontmatter parsing
  - Embedded YAML/JSON block extraction
  - Recursive skill discovery
  - get_skill_context() for system prompts
  - get_configs() for tool configurations
- `src/healthsim_agent/skills/router.py` - Intent-to-skill routing
  - Product keyword detection (6 products)
  - Trigger phrase matching (557 triggers)
  - Confidence scoring algorithm
  - get_skill_for_generation() helper
  - find_related_skills() discovery
- Copied 175 skill files from healthsim-workspace
  - patientsim: 18 skills (diabetes, oncology, pediatrics, etc.)
  - membersim: 10 skills (claims, enrollment, benefits)
  - rxmembersim: 10 skills (pharmacy, formulary, PA)
  - trialsim: 19 skills (CDISC domains, phases, therapeutic areas)
  - populationsim: 42 skills (demographics, SDOH, geographic)
  - networksim: 45 skills (providers, networks, adequacy)
  - common: 5 skills (DuckDB, identity, state)
  - generation: 26 skills (profiles, journeys, distributions)
- Unit tests: 62 new tests for skills module
  - test_skill_loader.py: 22 tests
  - test_skill_router.py: 40 tests

### Added - Phase 2: Generation Framework (January 9, 2026)
- `src/healthsim_agent/generation/distributions.py` - Statistical distributions
- `src/healthsim_agent/generation/generators.py` - Data generators
- `src/healthsim_agent/generation/handlers.py` - Event handlers
- `src/healthsim_agent/generation/profile.py` - Profile builder
- Unit tests: 60 tests for generation module

### Added - Phase 1: Database & State Layer (January 9, 2026)
- `src/healthsim_agent/db/schema.py` - DuckDB schema definitions
- `src/healthsim_agent/db/queries.py` - Reference data queries
- `src/healthsim_agent/state/manager.py` - Cohort state management
- Unit tests: 30 tests for db and state modules

### Added - Phase 0: Project Setup (January 9, 2026)
- Initial project structure
- CLI entry point with Click
- Rich terminal UI foundation
- Session state management
- DuckDB connection wrapper
- Unit tests: 8 tests for session module
