# HealthSim Agent Development Plan

**Project**: healthsim-agent  
**Start Date**: January 9, 2026  
**Last Updated**: January 9, 2026  
**Status**: 🟡 In Progress - Phase 1

---

## Overview

Migrating the HealthSim workspace (~20,000 lines of Python) to a standalone Agent SDK application with Rich-based terminal UI.

### Progress Summary

| Phase | Description | Status | Progress |
|-------|-------------|--------|----------|
| Phase 0 | Project Setup | ✅ Complete | 100% |
| Phase 1 | Database & State Layer | ✅ Complete | 100% |
| Phase 2 | Generation Framework | ⬜ Not Started | 0% |
| Phase 3 | Skills Integration | ⬜ Not Started | 0% |
| Phase 4 | Agent Tools | ⬜ Not Started | 0% |
| Phase 5 | UI Enhancements | ⬜ Not Started | 0% |
| Phase 6 | Testing & Polish | ⬜ Not Started | 0% |
| Phase 7 | Documentation & Release | ⬜ Not Started | 0% |

**Overall Progress**: ~28% (Phases 0-1 complete)

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

## Phase 2: Generation Framework ⬜ NOT STARTED

**Estimated Duration**: 8-10 hours  
**Goal**: Port the generative data framework

### Source Files to Port
- `generation/distributions.py` (580 lines) - 8 distribution types
- `generation/profile_schema.py` (240 lines) - ProfileSpecification
- `generation/profile_executor.py` (510 lines) - Profile execution
- `generation/journey_engine.py` (1400 lines) - Journey execution
- `generation/handlers.py` (1300 lines) - Product handlers

### Tasks

#### 2.1 Distribution System
- [ ] Port distribution types (normal, uniform, categorical, etc.)
- [ ] Implement distribution sampling
- [ ] Add seed management for reproducibility

#### 2.2 Profile Framework
- [ ] Port ProfileSpecification schema
- [ ] Implement profile executor
- [ ] Add profile validation

#### 2.3 Journey Engine
- [ ] Port journey engine core
- [ ] Implement state transitions
- [ ] Add event generation

#### 2.4 Product Handlers
- [ ] Port PatientSim handler
- [ ] Port MemberSim handler
- [ ] Port RxMemberSim handler
- [ ] Port TrialSim handler
- [ ] Port NetworkSim handler

### Verification Criteria
- [ ] Can generate patient with realistic demographics
- [ ] Can generate claims with proper coding
- [ ] Journey engine produces temporal sequences
- [ ] All handlers produce valid canonical JSON

---

## Phase 3: Skills Integration ⬜ NOT STARTED

**Estimated Duration**: 4-6 hours  
**Goal**: Load and route Skills from the skills/ directory

### Tasks

#### 3.1 Skill Loader
- [ ] Implement skill discovery (scan skills/ directory)
- [ ] Parse YAML frontmatter
- [ ] Extract trigger phrases
- [ ] Build skill index

#### 3.2 Skill Router
- [ ] Match user intent to skills
- [ ] Extract parameters from natural language
- [ ] Route to appropriate handler

#### 3.3 Skill Integration
- [ ] Copy skills from healthsim-workspace
- [ ] Validate skill format
- [ ] Test routing for each product domain

### Verification Criteria
- [ ] Skills load from directory
- [ ] Trigger phrases route correctly
- [ ] Parameters extracted from user messages

---

## Phase 4: Agent Tools ⬜ NOT STARTED

**Estimated Duration**: 6-8 hours  
**Goal**: Convert MCP tools to Agent SDK tools

### Tools to Implement
1. `query_reference_data` - Database queries
2. `generate_patient` - Patient generation
3. `generate_claims` - Claims generation
4. `generate_prescription` - Rx generation
5. `save_cohort` - Persist generated data
6. `export_data` - Export to files
7. `search_providers` - NPPES search
8. `get_demographics` - Census/SDOH data

### Tasks

#### 4.1 Tool Framework
- [ ] Define tool interface/protocol
- [ ] Implement tool registry
- [ ] Add tool result formatting

#### 4.2 Query Tools
- [ ] Implement query_reference_data
- [ ] Implement search_providers
- [ ] Implement get_demographics

#### 4.3 Generation Tools
- [ ] Implement generate_patient
- [ ] Implement generate_claims
- [ ] Implement generate_prescription

#### 4.4 Persistence Tools
- [ ] Implement save_cohort
- [ ] Implement export_data

### Verification Criteria
- [ ] Tools callable from agent
- [ ] Results formatted for display
- [ ] Error handling working

---

## Phase 5: UI Enhancements ⬜ NOT STARTED

**Estimated Duration**: 4-5 hours  
**Goal**: Polish terminal interface per UX spec

### Tasks

#### 5.1 Streaming Responses
- [ ] Implement token streaming display
- [ ] Add typing indicator
- [ ] Handle partial responses

#### 5.2 Data Visualization
- [ ] Enhance table formatting
- [ ] Add chart/sparkline support
- [ ] Implement data previews

#### 5.3 Suggestions System
- [ ] Implement contextual suggestions
- [ ] Add quick-action shortcuts
- [ ] Show related commands

#### 5.4 Session Management
- [ ] Add session save/restore
- [ ] Implement history browsing
- [ ] Add export options

### Verification Criteria
- [ ] Responses stream smoothly
- [ ] Data displays are readable
- [ ] Suggestions are contextually relevant

---

## Phase 6: Testing & Polish ⬜ NOT STARTED

**Estimated Duration**: 4-5 hours  
**Goal**: Comprehensive testing and bug fixes

### Tasks

#### 6.1 Unit Test Coverage
- [ ] Achieve >80% coverage on core modules
- [ ] Add edge case tests
- [ ] Test error conditions

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
- [ ] All tests passing
- [ ] Coverage >80%
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

**Next Session**: Begin Phase 2 (Generation Framework)

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
