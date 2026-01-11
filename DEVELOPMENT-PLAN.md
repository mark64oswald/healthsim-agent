# HealthSim Agent Development Plan

**Project**: healthsim-agent  
**Start Date**: January 9, 2026  
**Last Updated**: January 11, 2026  
**Status**: 🟡 In Progress - Phase 6

---

## Overview

Migrating the HealthSim workspace (~20,000 lines of Python) to a standalone Agent SDK application with Rich-based terminal UI.

### Progress Summary

| Phase | Description | Status | Progress |
|-------|-------------|--------|----------|
| Phase 0 | Project Setup | ✅ Complete | 100% |
| Phase 1 | Database & State Layer | ✅ Complete | 100% |
| Phase 2 | Generation Framework | ✅ Complete | 100% |
| Phase 3 | Skills Integration | ✅ Complete | 100% |
| Phase 4 | Agent Tools | ✅ Complete | 100% |
| Phase 5 | UI Enhancements | ✅ Complete | 100% |
| Phase 6 | Testing & Polish | 🟡 In Progress | 50% |
| Phase 7 | Documentation & Release | ⬜ Not Started | 0% |

**Overall Progress**: ~89% (Phases 0-5 complete, Phase 6 ~40%)

---

## Phase 0: Project Setup ✅ COMPLETE

**Completed**: January 9, 2026

### Tasks Completed
- [x] Create repository structure
- [x] Configure pyproject.toml with dependencies
- [x] Create core package structure (src/healthsim_agent/)
- [x] Implement main.py entry point with Click CLI
- [x] Implement agent.py core orchestration
- [x] Implement ui/terminal.py Rich interface
- [x] Implement ui/components.py display widgets
- [x] Implement state/session.py session management
- [x] Implement db/connection.py DuckDB wrapper
- [x] Copy reference documentation
- [x] Create unit tests for SessionState (8 passing)
- [x] Verify package installation and CLI
- [x] Push to GitHub

### Deliverables
- `healthsim` CLI command working
- All module imports verified
- 8 unit tests passing

---

## Phase 1: Database & State Layer ✅ COMPLETE

**Completed**: January 9, 2026  
**Goal**: Port DuckDB integration and state management from healthsim-workspace

### Source Files Ported
From `packages/core/src/healthsim/`:
- `db/schema.py` (700 lines) → Adapted to 443 lines
- `db/queries.py` (170 lines) → Expanded to 414 lines with ReferenceQueries
- `state/manager.py` (900 lines) → Adapted to 451 lines

### Tasks Completed

#### 1.1 Enhanced Database Connection ✅
- [x] Port schema definitions from workspace
- [x] Add table introspection methods
- [x] Implement query result formatting (QueryResult dataclass)
- [x] Add connection context management
- [x] Verify against reference database

**Files**: `src/healthsim_agent/db/connection.py`, `db/schema.py`

#### 1.2 Query Helpers ✅
- [x] Port common query patterns
- [x] Provider search (NPPES)
- [x] Demographics lookup (Census/SVI)
- [x] Health indicators (CDC PLACES)
- [x] Add ReferenceQueries class

**Files**: `src/healthsim_agent/db/queries.py`

#### 1.3 State Manager ✅
- [x] Port StateManager class
- [x] Implement cohort tracking (Cohort dataclass)
- [x] Add entity registry (patients, members, claims)
- [x] Implement state persistence (JSON export/import)
- [x] Add CohortSummary for token efficiency

**Files**: `src/healthsim_agent/state/manager.py`

#### 1.4 Unit Tests ✅
- [x] Test database queries against reference data
- [x] Test state persistence round-trip
- [x] Test cohort tracking operations
- [x] All 38 tests passing

**Files**: `tests/unit/test_database.py`, `test_state_manager.py`

### Verification Criteria ✅
- [x] Can query reference database tables
- [x] State persists across session serialize/deserialize
- [x] All Phase 1 tests passing (38/38)

---

## Phase 2: Generation Framework ✅ COMPLETE

**Completed**: January 9, 2026  
**Goal**: Port the generative data framework

### Source Files Ported
- `generation/distributions.py` (580→411 lines) - 8 distribution types
- `generation/profile_schema.py` (240→254 lines) - ProfileSpecification  
- `generation/generators.py` (NEW - 600 lines) - Entity generators
- `generation/handlers.py` (1300→697 lines) - Product event handlers

### Tasks Completed

#### 2.1 Distribution System ✅
- [x] Port distribution types (Normal, Uniform, Categorical, LogNormal, etc.)
- [x] Implement distribution sampling with seeded RNG
- [x] Add create_distribution() factory function
- [x] WeightedChoice for weighted selection

**Files**: `src/healthsim_agent/generation/distributions.py`

#### 2.2 Profile Framework ✅
- [x] Port ProfileSpecification schema with Pydantic
- [x] Demographics, Clinical, Coverage specs
- [x] Profile templates (medicare-diabetic, commercial-healthy, medicaid-pediatric)
- [x] JSON serialization/deserialization

**Files**: `src/healthsim_agent/generation/profile.py`

#### 2.3 Entity Generators ✅
- [x] PatientGenerator - realistic patient demographics
- [x] MemberGenerator - insurance member data
- [x] ClaimGenerator - claims with line items
- [x] SubjectGenerator - clinical trial subjects
- [x] Batch generation with distributions
- [x] Reproducibility via seeding

**Files**: `src/healthsim_agent/generation/generators.py`

#### 2.4 Product Handlers ✅
- [x] PatientSimHandlers - encounters, diagnoses, labs
- [x] MemberSimHandlers - enrollment, claims
- [x] RxMemberSimHandlers - prescriptions, fills
- [x] TrialSimHandlers - screening, randomization, AEs
- [x] HandlerRegistry for event routing

**Files**: `src/healthsim_agent/generation/handlers.py`

#### 2.5 Unit Tests ✅
- [x] Distribution tests (17 tests)
- [x] Generator tests (25 tests)
- [x] Handler tests (18 tests)
- [x] All 98 tests passing

### Verification Criteria ✅
- [x] Can generate patient with realistic demographics
- [x] Can generate claims with proper coding
- [x] Event handlers produce valid canonical JSON
- [x] All Phase 2 tests passing (98/98)

---

## Phase 3: Skills Integration ✅ COMPLETE

**Completed**: January 10, 2026  
**Goal**: Load and route Skills from the skills/ directory

### Tasks Completed

#### 3.1 Skill Models ✅
- [x] SkillMetadata dataclass for frontmatter
- [x] ParsedSkill dataclass for parsed skills
- [x] EmbeddedConfig for YAML/JSON code blocks
- [x] SkillIndex for efficient routing

**Files**: `src/healthsim_agent/skills/models.py`

#### 3.2 Skill Loader ✅
- [x] Recursive skill discovery (213 .md files)
- [x] YAML frontmatter parsing
- [x] Trigger phrase extraction from description
- [x] Embedded YAML/JSON block extraction
- [x] get_skill_context() for system prompts
- [x] get_configs() for tool configs

**Files**: `src/healthsim_agent/skills/loader.py`

#### 3.3 Skill Router ✅
- [x] Product keyword detection (6 products)
- [x] Trigger phrase matching (557 triggers indexed)
- [x] Confidence scoring algorithm
- [x] get_skill_for_generation() helper
- [x] find_related_skills() for discovery

**Files**: `src/healthsim_agent/skills/router.py`

#### 3.4 Skills Content ✅
- [x] Copied 175 skill files from workspace
- [x] All 6 products: patientsim, membersim, rxmembersim, trialsim, populationsim, networksim
- [x] Common and generation framework skills
- [x] Master SKILL.md for routing

#### 3.5 Unit Tests ✅
- [x] test_skill_loader.py (22 tests)
- [x] test_skill_router.py (40 tests)
- [x] All 62 skill tests passing
- [x] Total: 160 tests passing

### Verification Criteria ✅
- [x] Skills load from directory (175 skills)
- [x] Trigger phrases route correctly (557 indexed)
- [x] Embedded configs extracted
- [x] Product detection working for all 6 products
- [x] All tests passing (160/160)

---

## Phase 4: Agent Tools ✅ COMPLETE

**Completed**: January 10, 2026  
**Goal**: Convert MCP tools to Agent SDK tools

### Source Files Created
- `src/healthsim_agent/tools/base.py` (115 lines) - ToolResult, entity validation
- `src/healthsim_agent/tools/connection.py` (180 lines) - ConnectionManager
- `src/healthsim_agent/tools/cohort_tools.py` (489 lines) - Cohort CRUD operations
- `src/healthsim_agent/tools/query_tools.py` (200 lines) - SQL queries, summaries
- `src/healthsim_agent/tools/reference_tools.py` (350 lines) - Reference data, provider search

### Tasks Completed

#### 4.1 Tool Framework ✅
- [x] ToolResult dataclass for standard responses
- [x] ok() and err() helper functions
- [x] Entity type taxonomy (SCENARIO/RELATIONSHIP/REFERENCE)
- [x] validate_entity_types() for cohort validation

**Files**: `src/healthsim_agent/tools/base.py`

#### 4.2 Connection Management ✅
- [x] ConnectionManager with close-before-write pattern
- [x] Persistent read connection with retry logic
- [x] Write connection context manager
- [x] Global manager singleton with reset capability

**Files**: `src/healthsim_agent/tools/connection.py`

#### 4.3 Cohort Tools ✅
- [x] list_cohorts - List saved cohorts with filtering
- [x] load_cohort - Load cohort by name or ID
- [x] save_cohort - Save new cohort (full replacement)
- [x] add_entities - Incremental upsert (RECOMMENDED)
- [x] delete_cohort - Delete with confirmation

**Files**: `src/healthsim_agent/tools/cohort_tools.py`

#### 4.4 Query Tools ✅
- [x] query - Execute read-only SQL
- [x] get_summary - Token-efficient cohort summary
- [x] list_tables - Categorized table listing

**Files**: `src/healthsim_agent/tools/query_tools.py`

#### 4.5 Reference Tools ✅
- [x] query_reference - PopulationSim data (CDC PLACES, SVI, ADI)
- [x] search_providers - NPPES search (8.9M providers)
- [x] Specialty keyword to taxonomy mapping

**Files**: `src/healthsim_agent/tools/reference_tools.py`

#### 4.6 Unit Tests ✅
- [x] test_tools_connection.py (14 tests)
- [x] test_tools_cohort.py (35 tests)
- [x] test_tools_query.py (15 tests)
- [x] test_tools_reference.py (32 tests)
- [x] All 96 tool tests passing
- [x] Total: 256 tests passing

### Verification Criteria ✅
- [x] 10 MCP tools converted to standalone functions
- [x] ConnectionManager handles close-before-write pattern
- [x] Entity type validation working
- [x] All tools return ToolResult
- [x] All 256 tests passing

---

## Phase 5: UI Enhancements ✅ COMPLETE

**Completed**: January 10, 2026  
**Goal**: Polish terminal interface per UX spec

### Source Files Created
- `src/healthsim_agent/ui/theme.py` (119 lines) - GitHub Dark color palette
- `src/healthsim_agent/ui/formatters.py` (359 lines) - Data → Rich renderables
- `src/healthsim_agent/ui/suggestions.py` (270 lines) - Contextual suggestions
- `src/healthsim_agent/ui/components.py` (470 lines) - Enhanced Rich components
- `src/healthsim_agent/ui/terminal.py` (443 lines) - Main UI with streaming

### Tasks Completed

#### 5.1 Theme & Colors ✅
- [x] GitHub Dark color palette from UX spec
- [x] Rich Theme object for consistent styling
- [x] Status icons (✓ ✗ ⚠ → •)
- [x] Braille spinner animation frames

**Files**: `src/healthsim_agent/ui/theme.py`

#### 5.2 Formatters ✅
- [x] format_tool_indicator() - "→ tool_name"
- [x] format_result_headline() - "✓ Success message"
- [x] format_data_panel() - Bordered data panels
- [x] format_data_table() - Formatted tables with pagination
- [x] format_suggestions() - Contextual next actions
- [x] format_error() - Actionable error display
- [x] format_cohort_summary() - Token-efficient summary
- [x] format_provider_results() - Provider search display

**Files**: `src/healthsim_agent/ui/formatters.py`

#### 5.3 Components ✅
- [x] WelcomePanel - ASCII banner with quick start
- [x] ToolIndicator - "→ tool_name" during execution
- [x] ResultHeadline - Success/error/warning with icons
- [x] SuggestionBox - Contextual next actions
- [x] StatusBar - Session info at bottom
- [x] ThinkingSpinner - Animated thinking indicator
- [x] ProgressDisplay - Progress bar for batch operations
- [x] HelpDisplay - Categorized help

**Files**: `src/healthsim_agent/ui/components.py`

#### 5.4 Suggestions System ✅
- [x] SuggestionGenerator class
- [x] Context tracking (last tool, entity type)
- [x] Tool-specific suggestion rules
- [x] Max 3 suggestions per response

**Files**: `src/healthsim_agent/ui/suggestions.py`

#### 5.5 Terminal UI ✅
- [x] TerminalUI class with all components
- [x] Streaming response support
- [x] StreamingCallback for progressive display
- [x] Command handling (/help, /status, /clear, /quit)
- [x] Session state tracking (cohort, entities, messages)

**Files**: `src/healthsim_agent/ui/terminal.py`

#### 5.6 Unit Tests ✅
- [x] test_ui_theme.py (25 tests)
- [x] test_ui_formatters.py (32 tests)
- [x] test_ui_suggestions.py (18 tests)
- [x] test_ui_components.py (51 tests)
- [x] test_ui_terminal.py (42 tests)
- [x] All 168 UI tests passing
- [x] Total: 424 tests passing

### Verification Criteria ✅
- [x] GitHub Dark theme applied throughout
- [x] Welcome screen matches UX spec
- [x] Tool indicators display during execution
- [x] Result headlines with appropriate icons
- [x] Streaming response support ready
- [x] Suggestions appear after substantive responses
- [x] Status bar shows session context
- [x] All 424 tests passing

---

## Phase 6: Testing & Polish 🟡 IN PROGRESS

**Started**: January 11, 2026  
**Estimated Duration**: 4-5 hours  
**Goal**: Comprehensive testing and bug fixes

### Progress
- [x] Baseline assessment: 690 tests, 50% coverage
- [x] Phase 6 Testing Plan documented (`docs/PHASE-6-TESTING-PLAN.md`)
- [x] Validation module tests (77 tests) - 95-100% coverage
- [x] RxMemberSim DUR tests (43 tests) - covering alerts/rules modules
- [x] TrialSim SDTM tests (40 tests) - 93-94% coverage
- [x] RxMemberSim claims tests (27 tests) - covering adjudication module
- [x] Auto naming tests (38 tests) - 100% coverage
- [x] Temporal utils tests (44 tests) - 100% coverage
- [x] Entity/provenance tests (25 tests) - 100% coverage
- [x] Skills schema tests (35 tests) - improved coverage
- **Current**: 1317 tests, 60% coverage

### Remaining Tasks

#### 6.1 Unit Test Coverage
- [x] temporal/utils.py tests (100% coverage ✅)
- [x] state/provenance.py tests (100% coverage ✅)
- [x] skills/schema.py tests (improved coverage)
- [ ] State module tests (auto_persist 38%, journey_manager 42%)
- [ ] Format tools tests (39% coverage)
- [ ] Skill tools tests (50% coverage)

#### 6.2 Integration Tests
- [ ] End-to-end conversation tests
- [ ] Database integration tests
- [ ] File export tests

#### 6.3 Performance
- [ ] Profile slow operations
- [ ] Optimize database queries
- [ ] Reduce startup time

#### 6.4 Bug Fixes
- [ ] Address discovered issues
- [ ] Fix edge cases
- [ ] Polish error messages

### Verification Criteria
- [x] All tests passing (✅ 1317 passing)
- [ ] Coverage >80% (60% achieved, target 80%)
- [ ] No critical bugs

---

## Phase 7: Documentation & Release ⬜ NOT STARTED

**Estimated Duration**: 3-4 hours  
**Goal**: Complete documentation and prepare for distribution

### Tasks

#### 7.1 User Documentation
- [ ] Write README with examples
- [ ] Create quick-start guide
- [ ] Document all commands

#### 7.2 Developer Documentation
- [ ] API reference
- [ ] Architecture overview
- [ ] Contributing guide

#### 7.3 Release Preparation
- [ ] Version bump
- [ ] Create changelog
- [ ] Tag release
- [ ] Build distribution package

### Verification Criteria
- [ ] Documentation complete
- [ ] Package installable via pip
- [ ] Release tagged on GitHub

---

## Time Estimates Summary

| Phase | Estimated Hours | Cumulative |
|-------|-----------------|------------|
| Phase 0 | 4 | 4 |
| Phase 1 | 5 | 9 |
| Phase 2 | 9 | 18 |
| Phase 3 | 5 | 23 |
| Phase 4 | 7 | 30 |
| Phase 5 | 4.5 | 34.5 |
| Phase 6 | 4.5 | 39 |
| Phase 7 | 3.5 | 42.5 |

**Total Estimated**: ~42-45 hours

---

## Session Log

### Session 1: January 9, 2026
**Duration**: ~2 hours  
**Completed**:
- Phase 0 complete
- Repository scaffolded
- Core modules created
- Tests passing
- Pushed to GitHub

### Session 2: January 9, 2026
**Duration**: ~1 hour  
**Completed**:
- Phase 1 complete
- Database schema (443 lines)
- Query helpers with ReferenceQueries (414 lines)
- StateManager with Cohort/CohortSummary (451 lines)
- 38 unit tests passing

### Session 3: January 9, 2026
**Duration**: ~1.5 hours  
**Completed**:
- Phase 2 complete (Generation Framework)
- distributions.py (411 lines) - Statistical distributions
- profile.py (254 lines) - Profile specifications
- generators.py (600 lines) - Entity generators (Patient, Member, Claim, Subject)
- handlers.py (697 lines) - Event handlers for all products
- 60 new unit tests (98 total, all passing)

**Next Session**: Begin Phase 3 (Skills Integration)

### Session 4: January 10, 2026
**Duration**: ~2 hours  
**Completed**:
- Phase 3 complete (Skills Integration)
- models.py (120 lines) - SkillMetadata, ParsedSkill, EmbeddedConfig
- loader.py (280 lines) - Hybrid skill parser
- router.py (350 lines) - Intent-to-skill routing
- 175 skills copied from workspace
- 62 new unit tests (160 total, all passing)

### Session 5: January 10, 2026
**Duration**: ~2 hours  
**Completed**:
- Phase 4 complete (Agent Tools)
- base.py (115 lines) - ToolResult, entity validation
- connection.py (180 lines) - ConnectionManager
- cohort_tools.py (489 lines) - Cohort CRUD
- query_tools.py (200 lines) - SQL queries
- reference_tools.py (350 lines) - Reference data, providers
- 96 new unit tests (256 total, all passing)

**Next Session**: Begin Phase 5 (UI Enhancements)

---

## Notes & Decisions

1. **Technology Stack**: Python 3.11+, Rich, Click, DuckDB, Anthropic SDK
2. **Database Strategy**: Read-only connection to reference data, separate from state
3. **State Persistence**: JSON-based for portability
4. **Skills Location**: Local skills/ directory (not loaded from workspace)

---

## Quick Reference

**Run Tests**: `pytest tests/ -v`  
**Run CLI**: `healthsim`  
**Debug Mode**: `healthsim --debug`  
**Project Path**: `/Users/markoswald/Developer/projects/healthsim-agent`  
**Source Workspace**: `/Users/markoswald/Developer/projects/healthsim-workspace`
