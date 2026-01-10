# HealthSim Agent - Comprehensive Gap Analysis

## Executive Summary

**Current State**: ~23,400 lines ported from core package
**Source Total**: ~28,000 lines (core) + ~46,000 lines (product packages) = ~74,000 lines
**Gap Assessment**: Core is ~85% complete; product packages not yet addressed

---

## 1. Core Package Status (packages/core/)

| Directory | Source Lines | Target Status | Notes |
|-----------|-------------|---------------|-------|
| benefits/ | ~900 | ✅ Complete | Accumulator tracking |
| config/ | ~430 | ✅ Complete | Settings, dimensional config |
| db/ | ~400 | ✅ Partial | Connection manager done |
| db/migrate/ | ~8,000 | ❌ Missing | JSON cohort migration |
| db/reference/ | ~12,300 | ❌ Missing | Reference data loaders |
| dimensional/ | ~1,916 | ❌ Missing | Analytics output writers |
| formats/ | ~530 | ✅ Complete | Base transformers, exporters |
| generation/ | ~12,000 | ✅ Complete | All modules ported |
| mcp/ | ~2,000 | ⏭️ Skip | Not needed for Agent SDK |
| person/ | ~700 | ✅ Complete | Demographics, identifiers |
| skills/ | ~300 | ✅ Complete | Schema definitions |
| state/ | ~2,000 | ✅ Complete | Entity, workspace, journey |
| temporal/ | ~500 | ✅ Complete | Timeline, periods, utils |
| validation/ | ~520 | ✅ Complete | Framework, structural, temporal |

**Core Gap**: ~22,000 lines in db/migrate, db/reference, dimensional

---

## 2. Product Packages Status

| Package | Source Lines | Target Status | Key Components |
|---------|-------------|---------------|----------------|
| patientsim/ | ~19,443 | ❌ Not Started | Core models, C-CDA, MIMIC, HL7v2, FHIR |
| membersim/ | ~8,768 | ❌ Not Started | Core models, X12 (834/835/837), quality |
| rxmembersim/ | ~12,805 | ❌ Not Started | Core models, NCPDP D.0, X12 |
| trialsim/ | ~5,008 | ❌ Not Started | Core models, SDTM, journeys |
| **Total** | **~46,024** | | |

### Product Package Contents Detail

**PatientSim** (~19,443 lines):
```
core/           - models.py, generator.py, timeline.py, state.py, reference_data.py
formats/ccda/   - transformer.py, sections.py, narratives.py, entries.py, validators.py
formats/mimic/  - transformer.py, schema.py
formats/hl7v2/  - segments.py, messages.py
formats/fhir/   - transformer.py
```

**MemberSim** (~8,768 lines):
```
core/           - models.py, member.py, subscriber.py, plan.py, provider.py, accumulator.py
formats/x12/    - base.py, edi_834.py, edi_835.py, edi_837.py, edi_270_271.py, edi_278.py
formats/fhir.py
quality/        - measure.py
```

**RxMemberSim** (~12,805 lines):
```
core/           - member.py, drug.py, prescription.py, pharmacy.py, prescriber.py
formats/ncpdp/  - telecom.py, script.py, epa.py, reject_codes.py
formats/x12/    - edi_835.py
```

**TrialSim** (~5,008 lines):
```
core/           - models.py, generator.py
formats/sdtm/   - domains.py, exporter.py
journeys/       - templates.py, handlers.py, compat.py
adverse_events/, exposures/, visits/, subjects/
```

---

## 3. Reference Data Status

### DuckDB Database (healthsim-reference.duckdb) - ✅ Complete
| Schema | Tables | Status |
|--------|--------|--------|
| main/ | 24 entity tables | ✅ Present |
| population/ | 5 CDC/Census tables | ✅ Present |
| network/ | 5 provider/facility tables | ✅ Present |

### Local Reference Files
| Location | Content | Status |
|----------|---------|--------|
| references/ | Clinical domain docs, code systems | 📁 In workspace only |
| formats/ | Format documentation (C-CDA, X12, NCPDP, SDTM) | 📁 In workspace only |
| scenarios/*/data/ | Product-specific data files | 📁 In workspace only |

---

## 4. Decision Matrix: What to Port?

### Must Have (Core Functionality)
| Component | Lines | Rationale |
|-----------|-------|-----------|
| dimensional/ | ~1,916 | Analytics output is core feature |
| db/reference/ (loader.py, populationsim.py) | ~200 | Reference data access |

### Should Have (Full Feature Parity)
| Component | Lines | Rationale |
|-----------|-------|-----------|
| Product core models | ~3,000 | Canonical data structures |
| Product format transformers | ~15,000 | Output format support |

### Could Defer (Specialized Features)
| Component | Lines | Rationale |
|-----------|-------|-----------|
| db/migrate/ (json_cohorts.py) | ~8,000 | Cohort migration utility |
| Quality measures | ~500 | MemberSim-specific |
| MIMIC format | ~500 | Specialized output format |

---

## 5. Architecture Decision: Product Code Strategy

### Option A: Port All Product Packages (~46,000 lines)
**Pros**: Complete feature parity, all formats available
**Cons**: Large effort, may duplicate Skills-based generation

### Option B: Port Core Models Only (~3,000 lines)
**Pros**: Canonical data structures, smaller scope
**Cons**: No format transformers, limited output options

### Option C: Lazy Loading / On-Demand
**Pros**: Start small, add as needed
**Cons**: May need refactoring later

### Recommendation: **Option B + dimensional/**
1. Port dimensional/ (~1,916 lines) - Analytics output
2. Port product core models (~3,000 lines) - Canonical structures
3. Port db/reference/ loaders (~200 lines) - Reference data access
4. Defer format transformers - Skills can guide Claude to generate formats

**Total New Work**: ~5,116 lines
**Resulting Coverage**: Core infrastructure + canonical models + analytics output

---

## 6. PopulationSim & NetworkSim Status

### PopulationSim
- **Data**: ✅ Embedded in DuckDB (population schema)
- **Code**: Uses core generation framework + Skills
- **Python Package**: None (Skills-only product)

### NetworkSim
- **Data**: ✅ Embedded in DuckDB (network schema with 8.9M providers)
- **Code**: Uses networksim_reference.py (already ported)
- **Python Package**: None (Skills-only product)
- **Status**: v2 data infrastructure complete, Skills define queries

---

## 7. Recommended Action Plan

### Phase 1: Complete Core Gaps (This Session)
1. [ ] Port dimensional/ package (~1,916 lines)
   - writers/base.py
   - writers/duckdb_writer.py
   - writers/databricks_writer.py
   - writers/registry.py
   - transformers/base.py
   - generators/dim_date.py

2. [ ] Port db/reference/ loaders (~200 lines)
   - loader.py
   - populationsim.py

### Phase 2: Add Product Core Models (Next Session)
3. [ ] Create products/ directory structure
4. [ ] Port core models from each product:
   - patientsim/core/models.py
   - membersim/core/models.py
   - rxmembersim/core/models.py
   - trialsim/core/models.py

### Phase 3: Integration Testing
5. [ ] End-to-end generation tests
6. [ ] Format output validation
7. [ ] DuckDB analytics output verification

---

## 8. Files Not Needed

| Component | Reason |
|-----------|--------|
| mcp/ | Agent uses Agent SDK, not MCP |
| db/migrate/json_cohorts.py | Cohort migration utility, defer |
| Product format transformers | Skills guide Claude for format generation |
| Product MCP servers | Agent SDK replaces MCP |

---

*Generated: 2026-01-10*
*Source: healthsim-workspace, healthsim-agent comparison*
