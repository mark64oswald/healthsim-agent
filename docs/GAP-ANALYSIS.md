# HealthSim Agent Gap Analysis
## Comparing Implementation vs. Original Workspace Inventory

**Generated**: January 10, 2026  
**Purpose**: Pre-Phase 6 checkpoint to identify implementation gaps

---

## Executive Summary

Based on the original `healthsim-implementation-inventory.md`, we've successfully ported:
- ✅ **Database Layer** - 100% complete
- ✅ **MCP/Agent Tools** - 100% complete (10 tools)
- ✅ **Skills System** - 100% complete (175 skills, routing)
- ✅ **UI Layer** - 100% complete (enhanced beyond original)
- ⚠️ **State Management** - ~50% complete
- ⚠️ **Generation Framework** - ~30% complete

**Critical Gap**: The Journey Engine and Profile Executor - the core of what makes HealthSim *generate* data from natural language - are NOT implemented.

---

## Detailed Comparison

### 1. Database Layer ✅ COMPLETE

| Workspace File | Lines | Agent File | Lines | Status |
|---------------|-------|------------|-------|--------|
| `db/schema.py` | 700 | `db/schema.py` | 443 | ✅ Adapted |
| `db/queries.py` | 170 | `db/queries.py` | 414 | ✅ Expanded |
| `db/connection.py` | 150 | `db/connection.py` | 164 | ✅ Ported |
| `db/migrations.py` | 500 | (N/A) | - | ⚪ Not needed |

**Notes**: Schema migrations not needed since we're using existing database.

---

### 2. State Management ⚠️ 50% COMPLETE

| Workspace File | Lines | Agent File | Lines | Status |
|---------------|-------|------------|-------|--------|
| `state/manager.py` | 900 | `state/manager.py` | 451 | ⚠️ Partial |
| `state/session.py` | 260 | `state/session.py` | 221 | ✅ Ported |
| `state/summary.py` | 450 | (in manager) | - | ✅ Merged |
| `state/auto_persist.py` | 1500 | - | 0 | ❌ MISSING |
| `state/serializers.py` | 700 | - | 0 | ❌ MISSING |
| `state/journey_manager.py` | 600 | - | 0 | ❌ MISSING |
| `state/profile_manager.py` | 500 | - | 0 | ❌ MISSING |
| `state/provenance.py` | 120 | - | 0 | ❌ MISSING |
| `state/auto_naming.py` | 250 | - | 0 | ❌ MISSING |

**Missing Capabilities**:
- Auto-persistence (token-efficient saving)
- Entity serialization to canonical tables
- Journey state tracking
- Profile state tracking
- Entity provenance
- Auto-generated cohort names

---

### 3. Generation Framework ⚠️ 30% COMPLETE

| Workspace File | Lines | Agent File | Lines | Status |
|---------------|-------|------------|-------|--------|
| `generation/distributions.py` | 580 | `generation/distributions.py` | 411 | ⚠️ 70% |
| `generation/profile_schema.py` | 240 | `generation/profile.py` | 254 | ✅ Ported |
| `generation/profile_executor.py` | 510 | - | 0 | ❌ MISSING |
| `generation/handlers.py` | 1300 | `generation/handlers.py` | 697 | ⚠️ 54% |
| `generation/base.py` | 240 | `generation/generators.py` | 600 | ✅ Merged |
| `generation/journey_engine.py` | 1400 | - | 0 | ❌ MISSING |
| `generation/journey_validation.py` | 820 | - | 0 | ❌ MISSING |
| `generation/cross_domain_sync.py` | 670 | - | 0 | ❌ MISSING |
| `generation/triggers.py` | 470 | - | 0 | ❌ MISSING |
| `generation/orchestrator.py` | 350 | - | 0 | ❌ MISSING |
| `generation/reference_profiles.py` | 660 | - | 0 | ❌ MISSING |
| `generation/networksim_reference.py` | 690 | (in tools) | - | ⚠️ Partial |
| `generation/skill_registry.py` | 550 | - | 0 | ❌ MISSING |
| `generation/skill_reference.py` | 540 | - | 0 | ❌ MISSING |
| `generation/skill_journeys.py` | 420 | - | 0 | ❌ MISSING |
| `generation/auto_journeys.py` | 450 | - | 0 | ❌ MISSING |

**What Works**:
- Basic distributions (8 types)
- ProfileSpecification schema
- PatientGenerator, MemberGenerator, ClaimGenerator, SubjectGenerator
- Basic event handlers for each product

**Missing Critical Capabilities**:
- **Journey Engine** - Timeline-based event execution
- **Profile Executor** - Turn ProfileSpecification → Generated Entities
- **Cross-Domain Sync** - Synchronize entities across products
- **Triggers** - Cross-product event triggering
- **Orchestrator** - Coordinate Profile + Journey execution
- **Skill Integration** - Use skills to drive generation

---

### 4. MCP/Agent Tools ✅ COMPLETE

| Workspace Tool | Agent Tool | Status |
|---------------|------------|--------|
| `healthsim_list_cohorts` | `list_cohorts` | ✅ |
| `healthsim_load_cohort` | `load_cohort` | ✅ |
| `healthsim_save_cohort` | `save_cohort` | ✅ |
| `healthsim_add_entities` | `add_entities` | ✅ |
| `healthsim_delete_cohort` | `delete_cohort` | ✅ |
| `healthsim_query` | `query` | ✅ |
| `healthsim_get_cohort_summary` | `get_summary` | ✅ |
| `healthsim_query_reference` | `query_reference` | ✅ |
| `healthsim_search_providers` | `search_providers` | ✅ |
| `healthsim_tables` | `list_tables` | ✅ |

---

### 5. Skills System ✅ COMPLETE

| Component | Status |
|-----------|--------|
| SkillLoader (YAML parsing) | ✅ |
| SkillRouter (trigger matching) | ✅ |
| 175 skill files | ✅ Copied |
| Trigger index (557 phrases) | ✅ |

---

### 6. UI Layer ✅ COMPLETE (Enhanced)

| Workspace | Agent | Status |
|-----------|-------|--------|
| Basic terminal | Rich terminal | ✅ Enhanced |
| - | GitHub Dark theme | ✅ New |
| - | Streaming support | ✅ New |
| - | Contextual suggestions | ✅ New |
| - | Status bar | ✅ New |

---

### 7. Formats/Output ❌ NOT IMPLEMENTED

| Format | Status |
|--------|--------|
| FHIR R4 | ❌ Not ported |
| HL7v2 | ❌ Not ported |
| X12 837/835/834 | ❌ Not ported |
| CDISC SDTM/ADaM | ❌ Not ported |
| Canonical JSON | ✅ (via generators) |

---

## Impact Assessment

### What Currently Works

1. **Cohort Storage & Retrieval** ✅
   - Save cohorts to DuckDB
   - Load cohorts
   - Query cohort data
   - List/delete cohorts

2. **Reference Data Access** ✅
   - Search NPPES providers
   - Query CDC PLACES, SVI, ADI
   - Geographic population data

3. **Basic Entity Generation** ✅
   - PatientGenerator can create patients
   - MemberGenerator can create members
   - ClaimGenerator can create claims
   - SubjectGenerator can create subjects

4. **Skill Discovery** ✅
   - Load and parse skills
   - Route by trigger phrase
   - Find related skills

### What Does NOT Work

1. **Profile-Driven Generation** ❌
   - Cannot execute a ProfileSpecification to generate entities
   - Cannot use demographic references from PopulationSim
   - Cannot use real providers from NPPES

2. **Journey-Based Events** ❌
   - Cannot create timeline-based patient journeys
   - Cannot generate encounters, claims over time
   - Cannot simulate treatment progressions

3. **Cross-Product Integration** ❌
   - Cannot sync Patient → Member → RxMember
   - Cannot trigger claims from encounters
   - Cannot maintain SSN as universal correlator

4. **Format Export** ❌
   - Cannot export to FHIR bundles
   - Cannot create HL7 messages
   - Cannot generate X12 claims

---

## Recommendations

### Option A: Minimal Viable Product (MVP)

Port only what's needed for basic generation:
- `profile_executor.py` - Execute profiles
- Link generators to real reference data

**Effort**: ~4-6 hours
**Result**: Can generate entities from profiles, no journeys

### Option B: Core Generation Complete

Port full generation engine:
- `profile_executor.py`
- `journey_engine.py`
- `journey_validation.py`
- `orchestrator.py`

**Effort**: ~12-16 hours
**Result**: Full profile + journey generation working

### Option C: Feature Parity

Port everything from workspace:
- All generation files
- All state management
- Format transformers (FHIR, HL7, X12, CDISC)

**Effort**: ~30-40 hours
**Result**: Complete parity with workspace

### Recommended Path

**Option B** - Core Generation Complete is the right balance:

1. We already have the building blocks (distributions, generators, handlers)
2. Profile Executor + Journey Engine are the "brain" that orchestrates generation
3. Cross-product sync can come later
4. Format export can come later

---

## Test Coverage Analysis

| Module | Tests | Status |
|--------|-------|--------|
| Database | 27 | ✅ |
| State | 24 | ✅ |
| Tools | 96 | ✅ |
| Skills | 62 | ✅ |
| UI | 168 | ✅ |
| Generation | 47 | ⚠️ Basic only |

**Missing Tests**:
- Profile execution tests
- Journey engine tests
- End-to-end generation integration tests

---

## Line Count Summary

| Category | Workspace | Agent | Ported |
|----------|-----------|-------|--------|
| Database | ~1,520 | ~1,021 | 67% |
| State | ~5,760 | ~672 | 12% |
| Generation | ~10,920 | ~1,962 | 18% |
| Tools | ~1,600 | ~1,334 | 83% |
| Skills | ~500 | ~621 | 124% |
| UI | ~200 | ~1,722 | 861% |
| **Total** | **~20,500** | **~7,332** | **36%** |

**Note**: UI is enhanced beyond original. Skills system rebuilt (not ported).

---

## Conclusion

We've built a solid foundation but are missing the core generation engine:
- ✅ Can store and query data
- ✅ Can access reference data
- ✅ Can discover skills
- ❌ Cannot execute profiles to generate realistic multi-entity scenarios
- ❌ Cannot run journey-based event timelines
- ❌ Cannot coordinate cross-product generation

**Recommendation**: Before Phase 6 Testing, implement at minimum:
1. `profile_executor.py` - Turn specs into entities
2. `journey_engine.py` - Timeline event execution
3. Integration with reference data (PopulationSim demographics)

This will enable the core value proposition: "Generate synthetic healthcare data through conversation."
