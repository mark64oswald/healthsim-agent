# HealthSim Agent - Outstanding Issues Tracker

*Last Updated: 2026-01-11 (Session 30 - Complete)*

## Critical (Blocking)

| Issue | Product | Identified | Status |
|-------|---------|------------|--------|
| *(none)* | - | - | - |

## High Priority (Product Gaps)

| Issue | Product | Identified | Status |
|-------|---------|------------|--------|
| *(none - all resolved)* | - | - | - |

## Medium Priority (Consistency)

| Issue | Product | Identified | Status |
|-------|---------|------------|--------|
| Generator/Factory naming inconsistent | All | Session 30 | 🟡 Cosmetic |
| TrialSim lacks clinical depth (vitals, labs for subjects) | TrialSim | Session 30 | 🟡 Observation |

## Low Priority (Nice to Have)

| Issue | Product | Identified | Status |
|-------|---------|------------|--------|
| MemberSim could integrate NPPES | MemberSim | Session 30 | 🔵 Future |

---

## Session 30 Summary

### Completed This Session
- ✅ Fixed all 11 test failures (663 tests now passing)
- ✅ Added `generate_pharmacy_claims()` function to RxMemberSim
- ✅ Added `PharmacyClaimFactory` class
- ✅ Verified SDTM/ADaM transform tools work correctly
- ✅ Added X12 270 (eligibility inquiry) support
- ✅ Added X12 271 (eligibility response) support
- ✅ Comprehensive consistency analysis completed
- ✅ Updated format catalog to 12 formats across 4 products

### All Product Gaps Resolved
| Gap | Resolution |
|-----|------------|
| RxMemberSim pharmacy_claims | Added `generate_pharmacy_claims()` |
| TrialSim SDTM export | Verified working - `transform_to_sdtm()` |
| TrialSim ADaM export | Verified working - `transform_to_adam()` |
| MemberSim X12 270/271 | Added to `transform_to_x12()` |

---

## Current State Summary

### Test Coverage
- **663 tests passing**
- All products have unit tests
- All formats have unit tests

### Generation Tools (5 total)
| Tool | Product | Status |
|------|---------|--------|
| `generate_patients()` | PatientSim | ✅ Working |
| `generate_members()` | MemberSim | ✅ Working |
| `generate_subjects()` | TrialSim | ✅ Working |
| `generate_rx_members()` | RxMemberSim | ✅ Working |
| `generate_pharmacy_claims()` | RxMemberSim | ✅ Working |

### Transform Tools (12 formats)
| Format | Tool | Product | Status |
|--------|------|---------|--------|
| FHIR R4 | `transform_to_fhir()` | PatientSim | ✅ |
| C-CDA | `transform_to_ccda()` | PatientSim | ✅ |
| HL7v2 | `transform_to_hl7v2()` | PatientSim | ✅ |
| X12 837P/I | `transform_to_x12(type='837P')` | MemberSim | ✅ |
| X12 835 | `transform_to_x12(type='835')` | MemberSim | ✅ |
| X12 834 | `transform_to_x12(type='834')` | MemberSim | ✅ |
| X12 270 | `transform_to_x12(type='270')` | MemberSim | ✅ |
| X12 271 | `transform_to_x12(type='271')` | MemberSim | ✅ |
| NCPDP D.0 | `transform_to_ncpdp()` | RxMemberSim | ✅ |
| MIMIC-III | `transform_to_mimic()` | PatientSim | ✅ |
| CDISC SDTM | `transform_to_sdtm()` | TrialSim | ✅ |
| CDISC ADaM | `transform_to_adam()` | TrialSim | ✅ |

---

## Consistency Assessment

### Appropriately Consistent ✅
- All products have `core/` and `formats/` directories
- All products use Pydantic models
- All products have generation tools
- All products have transform tools
- All transform tools accept both cohort_id and direct data dict

### Appropriately Different ✅
- RxMemberSim has `dur/`, `formulary/` (pharmacy-specific)
- TrialSim has SDTM/ADaM (clinical trials-specific)
- PatientSim has FHIR/C-CDA/HL7v2 (clinical exchange-specific)
- MemberSim has X12 (claims-specific)

### Minor Inconsistencies 🟡
- Generator naming: some use `Generator`, others use `Factory`
- TrialSim has fewer clinical detail models than PatientSim

---

## Resolution Log

| Date | Issue | Resolution |
|------|-------|------------|
| 2026-01-11 | Transform tools only accept cohort_id | Added Union[str, dict] support |
| 2026-01-11 | X12 835 needs Payment objects | Added claim-to-payment conversion |
| 2026-01-11 | C-CDA needs config | Added default CCDAConfig |
| 2026-01-11 | RxMemberSim no pharmacy_claims | Added PharmacyClaimFactory + generate_pharmacy_claims() |
| 2026-01-11 | Test assertions outdated | Updated tests to match new implementations |
| 2026-01-11 | Format exports PatientSim-heavy | Confirmed appropriate domain separation |
| 2026-01-11 | TrialSim SDTM/ADaM missing | Verified already implemented and working |
| 2026-01-11 | MemberSim X12 270/271 missing | Added to transform_to_x12() |
