# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added - Phase 6 Testing Improvements (January 11, 2026)
- **Validation Module Tests** - `tests/unit/test_validation_framework.py` (26 tests)
  - ValidationSeverity enum tests
  - ValidationIssue dataclass tests
  - ValidationResult class tests (add_issue, merge, filtering)
  - BaseValidator and CompositeValidator tests
  - StructuralValidator tests
- **Structural Validation Tests** - `tests/unit/test_validation_structural.py` (20 tests)
  - ReferentialIntegrityValidator tests
  - validate_reference, validate_required_reference, validate_unique_ids, validate_foreign_key
  - Entity graph integration tests
- **Temporal Validation Tests** - `tests/unit/test_validation_temporal.py` (31 tests)
  - TemporalValidator tests
  - validate_date_not_future, validate_date_order, validate_duration, validate_age_range
  - Encounter timeline and trial eligibility integration tests
- **Auto Naming Tests** - `tests/unit/test_auto_naming.py` (38 tests)
  - extract_keywords tests (healthcare priority, stop words, entity types)
  - sanitize_name tests (lowercase, hyphens, special chars, max length)
  - ensure_unique_name tests (counters, high counter fallback)
  - generate_cohort_name tests (keywords, context, prefix, date)
  - parse_cohort_name tests (date, counter, keywords extraction)
  - Constants sanity checks (STOP_WORDS, HEALTHCARE_KEYWORDS)
- **Temporal Periods Tests** - `tests/unit/test_temporal_periods.py` (48 tests)
  - Period dataclass tests (creation, duration, contains, overlaps, adjacent)
  - Period merge and iteration tests
  - PeriodCollection tests (add, gaps, overlaps, consolidate, contains)
  - TimePeriod Pydantic model tests (validation, duration, overlaps, merge)
- **Temporal Timeline Tests** - `tests/unit/test_temporal_timeline.py` (56 tests)
  - EventStatus enum tests
  - EventDelay tests (fixed, range, custom RNG)
  - TimelineEvent tests (creation, status marking, comparison)
  - Timeline tests (add, create, schedule, query by type/status/range)
  - Timeline iteration and completion tests
  - Dependency-based scheduling tests
- **RxMemberSim DUR Tests** - `tests/unit/test_rxmembersim_dur.py` (43 tests)
  - DURAlertType, ClinicalSignificance enum tests
  - DURReasonForService, DURProfessionalService, DURResultOfService enum tests
  - DURAlert, DrugDrugInteraction, TherapeuticDuplication, AgeRestriction model tests
  - DURAlertSummary and DUROverride model tests
  - DURAlertFormatter tests (display, NCPDP format, summary creation)
- **TrialSim SDTM Tests** - `tests/unit/test_trialsim_sdtm.py` (40 tests)
  - SDTMDomain enum and SDTMVariable dataclass tests
  - DM_VARIABLES, AE_VARIABLES domain variable tests
  - DOMAIN_VARIABLES mapping tests
  - ExportFormat, ExportConfig, ExportResult model tests
  - SDTMExporter tests (DM, AE, EX, SV domains)
  - File export and filtered domain tests
  - SDTM conversion method tests (USUBJID format, demographics, arm)
- **Coverage milestones:**
  - Total tests: 1031 passing (341 new from baseline 690)
  - Coverage improved from 50% to 57%
  - validation/framework.py: 100%, temporal.py: 100%, structural.py: 95%
  - state/auto_naming.py: 100% (was 12%)
  - temporal/periods.py: 95% (was 32%)
  - temporal/timeline.py: 94% (was 40%)
- Phase 6 Testing Plan documented in `docs/PHASE-6-TESTING-PLAN.md`

### Added - Skills Management System (January 10, 2026)
- `src/healthsim_agent/tools/skill_tools.py` - Comprehensive skill management (1230 lines)
  - **Index & Search**: `index_skills()`, `search_skills()`, `get_skill()`, `list_skill_products()`
  - **CRUD Operations**: `save_skill()`, `update_skill()`, `delete_skill()`
  - **Validation**: `validate_skill()` with quality scoring (0-100)
  - **Versioning**: `get_skill_versions()`, `restore_skill_version()`
  - **Templates**: `get_skill_template()` for guided creation
  - **Spec-based Creation**: `create_skill_from_spec()` for conversational workflow
  - **Statistics**: `get_skill_stats()` for library overview
- Database schema for skill management:
  - `skill_index`: Metadata for fast searching (product, type, triggers, tags)
  - `skill_content`: Full-text content for semantic search
  - `skill_versions`: Version history with content backup
- Four skill templates: scenario, template, pattern, integration
- Validation rules by skill type with required sections
- `docs/SKILLS-MANAGEMENT.md` - Comprehensive documentation (309 lines)
  - Architecture overview
  - Conversational workflow examples
  - API reference
  - Best practices
- `tests/unit/test_skill_tools.py` - 27 tests covering all functionality
- Total tests: 690 passing (27 new)

### Added - Phase 6: CLI & Integration (January 10, 2026)
- Enhanced CLI with subcommands (`main.py`)
  - `healthsim chat` - Interactive chat session (default)
  - `healthsim status` - Database and configuration status
  - `healthsim query` - Direct SQL execution with format options
  - `healthsim cohorts` - List all saved cohorts
  - `healthsim export` - Export cohorts to JSON, FHIR, CSV
- `src/healthsim_agent/__main__.py` - Module entry point
  - Enables `python -m healthsim_agent`
- `src/healthsim_agent/tools/format_tools.py` - Format transformations (810 lines)
  - transform_to_fhir: Convert to FHIR R4 bundles
  - transform_to_ccda: Convert to C-CDA XML documents
  - transform_to_hl7v2: Convert to HL7v2 messages
  - transform_to_x12: Convert to X12 EDI (270/271/834/835/837)
  - transform_to_ncpdp: Convert to NCPDP SCRIPT XML
  - transform_to_mimic: Convert to MIMIC-III format
  - list_output_formats: List available formats
  - Helper functions for model conversion
- Full agent integration (`agent.py` rewrite)
  - 17 tools registered with Claude API tool calling
  - Tool execution loop with multi-turn support
  - Streaming response support with callbacks
  - Skills context loading for system prompt
  - Session save/load for persistence
- Session state enhancements (`state/session.py`)
  - Support for complex content blocks (tool use)
  - Proper serialization for API messages
  - Text extraction helpers
- Integration tests: 7 new tests
  - test_format_tools.py: Database connectivity, cohort operations, format listing
- Total tests: 591 passing
- Updated README with comprehensive CLI documentation

### Added - Phase 5: UI Enhancements (January 10, 2026)
- `src/healthsim_agent/ui/theme.py` - GitHub Dark theme
  - COLORS: Full palette from UX specification
  - HEALTHSIM_THEME: Rich Theme for consistent styling
  - ICONS: Status indicators (✓ ✗ ⚠ → •)
  - SPINNER_FRAMES: Braille animation sequence
- `src/healthsim_agent/ui/formatters.py` - Data formatters
  - format_tool_indicator: "→ tool_name" display
  - format_result_headline: Success/error/warning with icons
  - format_data_panel: Bordered data panels
  - format_data_table: Tables with pagination hints
  - format_suggestions: Next action suggestions
  - format_error: Actionable error display
  - format_cohort_summary: Token-efficient summary
  - format_provider_results: Provider search results
- `src/healthsim_agent/ui/suggestions.py` - Contextual suggestions
  - SuggestionGenerator: Context-aware suggestion engine
  - Tool-specific suggestion rules for all 10 tools
  - Entity type tracking for relevant follow-ups
- `src/healthsim_agent/ui/components.py` - Enhanced Rich components
  - WelcomePanel: ASCII banner with quick start
  - ToolIndicator: Tool invocation display
  - ResultHeadline: Status with icons
  - SuggestionBox: Next action suggestions
  - StatusBar: Session info display
  - ThinkingSpinner: Animated indicator
  - ProgressDisplay: Progress bar for batch operations
  - HelpDisplay: Categorized help
- `src/healthsim_agent/ui/terminal.py` - Enhanced terminal UI
  - Streaming response display support
  - StreamingCallback for progressive text
  - Tool indicator during execution
  - Suggestion display after responses
  - Session state tracking
- Unit tests: 168 new UI tests
  - test_ui_theme.py: 25 tests
  - test_ui_formatters.py: 32 tests
  - test_ui_suggestions.py: 18 tests
  - test_ui_components.py: 51 tests
  - test_ui_terminal.py: 42 tests
- Total tests: 424 passing (up from 256)

### Added - Phase 4: Agent Tools (January 10, 2026)
- `src/healthsim_agent/tools/base.py` - Tool result container and validation
  - ToolResult: Standard response format with success/error handling
  - ok() and err() helper functions
  - Entity type taxonomy (SCENARIO/RELATIONSHIP/REFERENCE)
  - validate_entity_types() for cohort validation
- `src/healthsim_agent/tools/connection.py` - Database connection management
  - ConnectionManager: Close-before-write pattern for DuckDB
  - Persistent read connection with retry logic
  - Write connection context manager with checkpointing
  - Global singleton with reset capability
- `src/healthsim_agent/tools/cohort_tools.py` - Cohort CRUD operations
  - list_cohorts: List saved cohorts with tag/search filtering
  - load_cohort: Load cohort by name or ID
  - save_cohort: Save new cohort (full replacement)
  - add_entities: Incremental upsert with batch support (RECOMMENDED)
  - delete_cohort: Delete with confirmation requirement
- `src/healthsim_agent/tools/query_tools.py` - Database query tools
  - query: Execute read-only SQL with validation
  - get_summary: Token-efficient cohort summary
  - list_tables: Categorized table listing
- `src/healthsim_agent/tools/reference_tools.py` - Reference data tools
  - query_reference: PopulationSim data (CDC PLACES, SVI, ADI)
  - search_providers: NPPES provider search (8.9M records)
  - Specialty keyword to taxonomy code mapping
- Unit tests: 96 new tests for tools module
  - test_tools_connection.py: 14 tests
  - test_tools_cohort.py: 35 tests
  - test_tools_query.py: 15 tests
  - test_tools_reference.py: 32 tests

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
