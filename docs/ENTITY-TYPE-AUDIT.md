# Entity Type Gap Analysis

**Date**: January 11, 2026  
**Status**: ✅ RESOLVED  
**Purpose**: Comprehensive audit of entity types across all HealthSim products

## Summary - Post-Fix Status

| Product | Database Tables | In SCENARIO_ENTITY_TYPES | In SERIALIZERS | In ENTITY_TABLE_MAP | Status |
|---------|-----------------|-------------------------|----------------|---------------------|--------|
| **PatientSim** |
| patients | ✅ | ✅ | ✅ | ✅ | ✅ Complete |
| encounters | ✅ | ✅ + aliases | ✅ + aliases | ✅ + aliases | ✅ Complete |
| diagnoses | ✅ | ✅ + aliases | ✅ + aliases | ✅ + aliases | ✅ Complete |
| medications | ✅ | ✅ + aliases | ✅ + aliases | ✅ + aliases | ✅ Complete |
| lab_results | ✅ | ✅ + aliases | ✅ + aliases | ✅ + aliases | ✅ Complete |
| **MemberSim** |
| members | ✅ | ✅ + aliases | ✅ + aliases | ✅ + aliases | ✅ Complete |
| claims | ✅ | ✅ | ✅ | ✅ | ✅ Complete |
| claim_lines | ✅ | ✅ | ✅ (NEW) | ✅ | ✅ Complete |
| **RxMemberSim** |
| prescriptions | ✅ | ✅ + aliases | ✅ + aliases | ✅ + aliases | ✅ Complete |
| pharmacy_claims | ✅ | ✅ + aliases (NEW) | ✅ (NEW) | ✅ (NEW) | ✅ Complete |
| **TrialSim** |
| subjects | ✅ | ✅ + aliases | ✅ + aliases | ✅ + aliases | ✅ Complete |
| adverse_events | ✅ | ✅ + aliases (NEW) | ✅ (NEW) | ✅ (NEW) | ✅ Complete |

## Gaps Identified (Now Resolved)

### Critical Gaps (Tables exist but not registered) - FIXED

1. **pharmacy_claims** (RxMemberSim) ✅
   - Added serializer, table mapping, and aliases

2. **adverse_events** (TrialSim) ✅
   - Added serializer, table mapping, and aliases

3. **claim_lines** serializer ✅
   - Added serialize_claim_line function

### Semantic Aliases Added

| LLM Term | Maps To | Product |
|----------|---------|---------|
| visit, visits | encounters | PatientSim |
| appointment, appointments | encounters | PatientSim |
| condition, conditions | diagnoses | PatientSim |
| lab, labs, test, tests | lab_results | PatientSim |
| drug, drugs | medications | PatientSim |
| subscriber, subscribers | members | MemberSim |
| dependent, dependents | members | MemberSim |
| coverage, coverages | members | MemberSim |
| enrollment, enrollments | members | MemberSim |
| rx, rxs | prescriptions | RxMemberSim |
| fill, fills | pharmacy_claims | RxMemberSim |
| refill, refills | pharmacy_claims | RxMemberSim |
| rx_claim, rx_claims | pharmacy_claims | RxMemberSim |
| participant, participants | subjects | TrialSim |
| trial_subject, trial_subjects | subjects | TrialSim |
| ae, aes | adverse_events | TrialSim |
| side_effect, side_effects | adverse_events | TrialSim |

## Files Modified

- `src/healthsim_agent/tools/base.py` - SCENARIO_ENTITY_TYPES (expanded with aliases)
- `src/healthsim_agent/state/serializers.py`:
  - Added serialize_claim_line, serialize_pharmacy_claim, serialize_adverse_event
  - Expanded SERIALIZERS registry with all aliases
  - Expanded ENTITY_TABLE_MAP with all aliases
