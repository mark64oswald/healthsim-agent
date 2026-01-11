# HealthSim Agent - Outstanding Issues Tracker

*Last Updated: 2026-01-11 (Session 30)*

## Critical (Blocking)

| Issue | Product | Identified | Status |
|-------|---------|------------|--------|
| *None* | - | - | - |

## High Priority (Product Gaps)

| Issue | Product | Identified | Status |
|-------|---------|------------|--------|
| No X12 270/271 (eligibility) | MemberSim | Session 28 | 🔴 Open |

## Medium Priority (Consistency)

| Issue | Product | Identified | Status |
|-------|---------|------------|--------|
| Format exports PatientSim-heavy | All | Session 28 | 🟡 Improved |
| Product code varies (4-16 files) | All | Session 28 | 🟡 Observation |

## Low Priority (Nice to Have)

| Issue | Product | Identified | Status |
|-------|---------|------------|--------|
| MIMIC export only for PatientSim | PatientSim | Session 28 | 🟡 Observation |

---

## Session 30 Summary

### Completed ✅
- Fixed 11 test failures (updated test expectations for new signatures)
- Added `generate_pharmacy_claims()` to RxMemberSim
- Created `PharmacyClaimFactory` for pharmacy claim generation
- Created ADaM exporter for TrialSim
- Added `transform_to_sdtm()` tool for CDISC SDTM export
- Added `transform_to_adam()` tool for CDISC ADaM export
- Added dict-to-model converters for trialsim entities (Subject, Visit, AdverseEvent, Exposure)
- Updated `list_output_formats()` to include 10 formats across 4 products
- All 663 tests passing

### Format Support Matrix (Current)

| Product | Formats |
|---------|---------|
| PatientSim | FHIR R4, C-CDA, HL7v2, MIMIC-III |
| MemberSim | X12 837, X12 835, X12 834 |
| RxMemberSim | NCPDP D.0 |
| TrialSim | CDISC SDTM, CDISC ADaM |

### Not Completed (Carried Forward)
- MemberSim X12 270/271 (eligibility inquiry/response)

---

## Resolution Log

| Date | Issue | Resolution |
|------|-------|------------|
| 2026-01-11 | Transform tools only accept cohort_id | Added Union[str, dict] support |
| 2026-01-11 | X12 835 needs Payment objects | Added claim-to-payment conversion |
| 2026-01-11 | C-CDA needs config | Added default CCDAConfig |
| 2026-01-11 | 11 format tool tests failing | Updated test expectations |
| 2026-01-11 | RxMemberSim lacks pharmacy_claims | Added generate_pharmacy_claims() |
| 2026-01-11 | TrialSim lacks SDTM export | Added transform_to_sdtm() |
| 2026-01-11 | TrialSim lacks ADaM export | Added transform_to_adam() |
