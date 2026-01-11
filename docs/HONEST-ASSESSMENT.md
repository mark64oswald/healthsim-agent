# HealthSim-Agent vs HealthSim-Workspace: Honest Assessment

**Date**: 2026-01-11
**Tests Passing**: 663
**Tools Defined**: 39

---

## 1. WHAT'S ACTUALLY WORKING

### Tools That Execute Successfully

| Category | Tools | Status |
|----------|-------|--------|
| **Cohort Management** | list_cohorts, load_cohort, save_cohort, add_entities, delete_cohort | ✅ Working |
| **Query** | query, get_summary, list_tables | ✅ Working |
| **Reference Data** | query_reference, search_providers | ✅ Working |
| **Generation** | generate_patients, generate_members, generate_subjects, generate_rx_members | ✅ Working |
| **Skills** | list_skills, describe_skill, check_formulary | ✅ Working |
| **Validation** | validate_data, fix_validation_issues | ✅ Working |
| **Profile/Journey** | save/load/list/delete/execute_profile, save/load/list/delete/execute_journey | ✅ Working (16 tests) |
| **Export** | export_json, export_csv, export_ndjson | ✅ Working |
| **Transform** | transform_to_fhir, transform_to_ccda, transform_to_hl7v2, transform_to_x12, transform_to_ncpdp, transform_to_mimic, list_output_formats | ⚠️ Defined but untested with real data |

**Working Tools**: 32/39 (82%)
**Defined/Partially Working**: 7/39 (18% - transform tools)

---

## 2. FEATURE PARITY GAPS

### What healthsim-workspace HAS that healthsim-agent LACKS

| Feature | Workspace | Agent | Gap |
|---------|-----------|-------|-----|
| **MCP Protocol** | Native MCP server | Agent SDK | Different paradigm - intentional |
| **Conversational Generation** | Full profile→conversation→entities | Basic generate_* tools | **MAJOR GAP** |
| **Journey Execution Engine** | Full multi-step with dependencies | Simple sequential execution | **SIGNIFICANT GAP** |
| **X12 EDI Generation** | Full 837/835/834/270/271/278 | Basic transform_to_x12 | **GAP** |
| **NCPDP D.0 Claims** | Full pharmacy claims | Just member structure | **GAP** |
| **SDTM/ADaM Export** | Full CDISC domains | Not implemented | **GAP** |
| **Dimensional Analytics** | DuckDB star schema writers | Only schema definitions | **GAP** |
| **Quality Measures** | HEDIS gap calculation | Not implemented | **GAP** |
| **Value-Based Care** | VBC contract modeling | Not implemented | **GAP** |
| **Prior Authorization** | Full PA workflow | Not implemented | **GAP** |
| **DUR Alerts** | Drug utilization review | Not implemented | **GAP** |

### What's EQUIVALENT

| Feature | Status |
|---------|--------|
| Cohort persistence (DuckDB) | ✅ Same |
| Skills system (markdown files) | ✅ Same (214 vs 213 skills) |
| Close-before-write pattern | ✅ Same |
| Entity generation structure | ✅ Similar |
| Reference data (CDC, Census, NPPES) | ✅ Same database |

---

## 3. PRODUCT CONSISTENCY ANALYSIS

### Code Structure Comparison

| Product | Workspace Structure | Agent Structure | Consistent? |
|---------|---------------------|-----------------|-------------|
| **PatientSim** | packages/patientsim/src/patientsim/ | src/healthsim_agent/products/patientsim/ | ⚠️ Partially |
| **MemberSim** | packages/membersim/src/membersim/ | src/healthsim_agent/products/membersim/ | ⚠️ Partially |
| **RxMemberSim** | packages/rxmembersim/src/rxmembersim/ | src/healthsim_agent/products/rxmembersim/ | ⚠️ Partially |
| **TrialSim** | packages/trialsim/src/trialsim/ | src/healthsim_agent/products/trialsim/ | ⚠️ Partially |

### What Each Product Generates

| Product | Entities Generated | Consistent Pattern? |
|---------|-------------------|---------------------|
| **PatientSim** | patients, encounters, diagnoses, vitals, labs, meds | ✅ Yes |
| **MemberSim** | members, enrollments, claims | ✅ Yes |
| **TrialSim** | subjects, visits, adverse_events, exposures | ✅ Yes |
| **RxMemberSim** | rx_members only (no pharmacy_claims) | ⚠️ Incomplete |

### Format Exporters per Product

| Format | PatientSim | MemberSim | TrialSim | RxMemberSim |
|--------|------------|-----------|----------|-------------|
| FHIR R4 | ✅ | ❌ | ❌ | ❌ |
| C-CDA | ✅ | ❌ | ❌ | ❌ |
| HL7v2 | ✅ | ❌ | ❌ | ❌ |
| X12 837/835 | ❌ | ⚠️ Basic | ❌ | ❌ |
| NCPDP D.0 | ❌ | ❌ | ❌ | ⚠️ Basic |
| SDTM | ❌ | ❌ | ❌ | ❌ |
| ADaM | ❌ | ❌ | ❌ | ❌ |
| MIMIC | ✅ | ❌ | ❌ | ❌ |

**Consistency Score: 60%** - Basic generation is consistent, but format exports are PatientSim-heavy.

---

## 4. ARCHITECTURAL DIFFERENCES

### healthsim-workspace (MCP)
```
User → Claude → MCP Server → Tools → DuckDB
                    ↓
              Skills (Markdown)
```
- Claude interprets skills
- MCP server provides database I/O only
- Generation happens in conversation

### healthsim-agent (Agent SDK)
```
User → Agent → Tools → Generation Logic → DuckDB
                  ↓
            Skills (Python)
```
- Python code does generation
- Tools wrap generation logic
- Skills inform but don't control

**This is a fundamental difference** - the workspace is "conversation-first" where Claude interprets skills and generates data. The agent has generation logic hardcoded in Python.

---

## 5. PATH TO PARITY

### Critical Gaps (Must Fix)

1. **RxMemberSim pharmacy claims** - Add pharmacy_claims generation
2. **TrialSim SDTM export** - Implement CDISC domains
3. **MemberSim X12 full implementation** - Complete EDI generation
4. **Transform tools testing** - Verify they actually work

### Important Gaps (Should Fix)

5. **Journey execution with dependencies** - Current is too simple
6. **Dimensional analytics writers** - DuckDB writer needs completion
7. **Quality measures** - HEDIS gap calculations
8. **DUR alerts for RxMemberSim** - Drug interaction checking

### Nice to Have

9. **Value-based care modeling**
10. **Prior authorization workflows**
11. **Population health analytics**

---

## 6. RECOMMENDATIONS

### Immediate Actions

1. **Verify transform tools** - Run actual end-to-end tests with real data
2. **Add RxMemberSim pharmacy_claims** - Match the generate_* pattern
3. **Create consistency tests** - Ensure all products have same test patterns

### Short-term (1-2 weeks)

4. **Implement SDTM export for TrialSim**
5. **Complete X12 generation for MemberSim**
6. **Add journey dependency resolution**

### Medium-term (1 month)

7. **Dimensional analytics writers**
8. **Quality measures**
9. **Documentation alignment**

---

## 7. FILE LOCATIONS

### Agent Product Code
```
/src/healthsim_agent/products/
├── patientsim/     (9 .py files)
├── membersim/      (14 .py files)
├── rxmembersim/    (16 .py files)
├── trialsim/       (4 .py files)
```

### Agent Tools
```
/src/healthsim_agent/tools/
├── generation_tools.py     (7 tools)
├── format_tools.py         (7 tools)
├── cohort_tools.py         (5 tools)
├── query_tools.py          (3 tools)
├── reference_tools.py      (2 tools)
├── validation_tools.py     (2 tools)
├── profile_journey_tools.py (10 tools)
├── export_tools.py         (3 tools)
```

### Skills (Both Repositories)
```
/skills/
├── patientsim/     (~40 scenarios)
├── membersim/      (~35 scenarios)
├── rxmembersim/    (~25 scenarios)
├── trialsim/       (~20 scenarios)
├── populationsim/  (~10 skills)
├── networksim/     (~10 skills)
├── common/         (shared patterns)
├── generation/     (builders, executors)
```

---

## SUMMARY

**What Works**: Basic generation, cohort management, skills listing, validation, profile/journey persistence

**What's Missing**: Advanced format exports, journey dependencies, quality measures, complete RxMemberSim

**Biggest Risk**: Transform tools are defined but may not work with real data - need verification

**Consistency**: Products follow similar patterns for generation but diverge significantly for format exports
