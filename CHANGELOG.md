# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

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
