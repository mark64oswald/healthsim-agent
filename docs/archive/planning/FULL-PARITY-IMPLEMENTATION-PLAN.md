# Full Parity Implementation Plan
## Completing HealthSim Agent to Match Workspace

**Created**: January 10, 2026  
**Goal**: Port ALL remaining functionality from healthsim-workspace

---

## Summary of Work Required

| Module | Workspace Lines | Agent Lines | Gap |
|--------|----------------|-------------|-----|
| state/ | 6,324 | 672 | 5,652 |
| generation/ | 11,000 | 1,962 | 9,038 |
| formats/ | 531 | 0 | 531 |
| temporal/ | 950 | 0 | 950 |
| validation/ | 705 | 0 | 705 |
| person/ | 675 | 0 | 675 |
| **TOTAL** | **~20,185** | **~2,634** | **~17,551** |

---

## Implementation Order

### Phase A: Foundation Modules (First)

These modules are dependencies for everything else.

#### A1. temporal/ (~950 lines)
Timeline and period handling used by journeys.

| File | Lines | Purpose |
|------|-------|---------|
| `temporal/periods.py` | 295 | Date periods, ranges |
| `temporal/timeline.py` | 300 | Timeline events |
| `temporal/utils.py` | 301 | Date utilities |

#### A2. validation/ (~705 lines)
Validation framework used by journey engine.

| File | Lines | Purpose |
|------|-------|---------|
| `validation/framework.py` | 242 | Base validation |
| `validation/structural.py` | 190 | Structure validation |
| `validation/temporal.py` | 228 | Time validation |

#### A3. person/ (~675 lines)
Person entity with demographics and identifiers.

| File | Lines | Purpose |
|------|-------|---------|
| `person/demographics.py` | 238 | Demographics generation |
| `person/identifiers.py` | 171 | SSN, MRN, etc. |
| `person/relationships.py` | 236 | Family relationships |

---

### Phase B: State Management (~5,652 lines to add)

#### B1. Core State Files

| File | Lines | Purpose | Status |
|------|-------|---------|--------|
| `state/manager.py` | 922 | StateManager class | ⚠️ Partial (451) |
| `state/session.py` | 306 | Session tracking | ✅ Done (221) |
| `state/entity.py` | 64 | Entity base class | ❌ Missing |

#### B2. Persistence & Serialization

| File | Lines | Purpose |
|------|-------|---------|
| `state/auto_persist.py` | 1,596 | Token-efficient persistence |
| `state/serializers.py` | 620 | Canonical table serialization |
| `state/summary.py` | 517 | CohortSummary |

#### B3. Profile & Journey State

| File | Lines | Purpose |
|------|-------|---------|
| `state/profile_manager.py` | 556 | Profile state |
| `state/journey_manager.py` | 644 | Journey state |

#### B4. Utilities

| File | Lines | Purpose |
|------|-------|---------|
| `state/auto_naming.py` | 298 | Auto cohort names |
| `state/provenance.py` | 132 | Entity provenance |
| `state/legacy.py` | 225 | JSON compatibility |
| `state/workspace.py` | 248 | Workspace management |

---

### Phase C: Generation Framework (~9,038 lines to add)

#### C1. Profile Execution

| File | Lines | Purpose | Status |
|------|-------|---------|--------|
| `generation/profile_schema.py` | 306 | ProfileSpecification | ✅ Done (254) |
| `generation/profile_executor.py` | 593 | Execute profiles | ❌ Missing |
| `generation/reference_profiles.py` | 852 | PopulationSim integration | ❌ Missing |

#### C2. Journey Engine

| File | Lines | Purpose |
|------|-------|---------|
| `generation/journey_engine.py` | 1,396 | Timeline execution |
| `generation/journey_validation.py` | 910 | Journey validation |

#### C3. Cross-Product Integration

| File | Lines | Purpose |
|------|-------|---------|
| `generation/cross_domain_sync.py` | 766 | Sync entities |
| `generation/triggers.py` | 468 | Event triggers |
| `generation/orchestrator.py` | 490 | Coordinate execution |

#### C4. Skill Integration

| File | Lines | Purpose |
|------|-------|---------|
| `generation/skill_registry.py` | 564 | Skill capabilities |
| `generation/skill_reference.py` | 576 | Skill parameters |
| `generation/skill_journeys.py` | 426 | Skill journey templates |
| `generation/auto_journeys.py` | 494 | Auto journey templates |

#### C5. Reference Data Integration

| File | Lines | Purpose | Status |
|------|-------|---------|--------|
| `generation/networksim_reference.py` | 793 | NPPES integration | ⚠️ Partial |
| `generation/geography_builder.py` | ~300 | Geography selection | ❌ Missing |

#### C6. Utilities

| File | Lines | Purpose | Status |
|------|-------|---------|--------|
| `generation/distributions.py` | 620 | Distributions | ✅ Done (411) |
| `generation/handlers.py` | 1,236 | Event handlers | ⚠️ Partial (697) |
| `generation/base.py` | 253 | Base generators | ✅ Merged |
| `generation/cohort.py` | 154 | Cohort helpers | ❌ Missing |
| `generation/reproducibility.py` | 132 | Seed management | ❌ Missing |

---

### Phase D: Output Formats (~531 lines)

| File | Lines | Purpose |
|------|-------|---------|
| `formats/base.py` | 143 | Format base classes |
| `formats/transformer.py` | 97 | Transform registry |
| `formats/utils.py` | 255 | Format utilities |

Note: Full FHIR/HL7/X12/CDISC transformers are in separate files not yet identified.

---

## Execution Plan

### Session 1: Foundation (A1-A3)
- Port temporal/ module
- Port validation/ module  
- Port person/ module
- ~2,330 lines

### Session 2: State Management Part 1 (B1-B2)
- Complete state/manager.py
- Port state/entity.py
- Port state/auto_persist.py
- Port state/serializers.py
- Port state/summary.py
- ~3,000 lines

### Session 3: State Management Part 2 (B3-B4)
- Port state/profile_manager.py
- Port state/journey_manager.py
- Port remaining state utilities
- ~2,100 lines

### Session 4: Generation Core (C1-C2)
- Port generation/profile_executor.py
- Port generation/journey_engine.py
- Port generation/journey_validation.py
- ~2,900 lines

### Session 5: Generation Integration (C3-C4)
- Port cross-product sync
- Port triggers and orchestrator
- Port skill integration files
- ~2,800 lines

### Session 6: Generation Completion (C5-C6)
- Complete handlers
- Port reference data integration
- Port utilities
- ~2,000 lines

### Session 7: Formats & Testing (D)
- Port formats module
- Integration testing
- End-to-end validation
- ~1,000 lines + tests

---

## Database Configuration

**Correct Path**: `data/healthsim-reference.duckdb`

Schemas:
- `main` - Entity storage (cohorts, patients, claims, etc.)
- `network` - NPPES providers (8.9M), facilities (77K)
- `population` - CDC PLACES, SVI, ADI

---

## Verification Criteria

After completion:
- [ ] Can execute ProfileSpecification → generated entities
- [ ] Can run journey timelines with events
- [ ] Can sync Patient ↔ Member ↔ RxMember ↔ Subject
- [ ] Can use real NPPES providers
- [ ] Can use PopulationSim demographics
- [ ] Can export to standard formats
- [ ] All products work: PatientSim, MemberSim, RxMemberSim, TrialSim, PopulationSim, NetworkSim
