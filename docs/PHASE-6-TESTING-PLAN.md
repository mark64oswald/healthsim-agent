# HealthSim Agent - Phase 6: Testing & Polish

**Created**: January 11, 2026  
**Current Coverage**: 50%  
**Target Coverage**: >80%  
**Current Tests**: 690 passing

---

## Pre-Flight Checklist

- [x] Run tests with coverage: `pytest tests/ -v --cov=src/healthsim_agent`
- [x] Baseline: 690 tests, 50% coverage
- [x] Identified priority gaps (see below)

---

## Coverage Gap Analysis

### Priority 1: Critical 0% Coverage (High Impact)

| File | Lines | Priority | Reason |
|------|-------|----------|--------|
| `validation/framework.py` | 76 | HIGH | Core validation logic |
| `validation/structural.py` | 44 | HIGH | Entity validation |
| `validation/temporal.py` | 52 | HIGH | Timeline validation |
| `rxmembersim/claims/adjudication.py` | 62 | HIGH | Claim processing |
| `rxmembersim/claims/claim.py` | 39 | HIGH | Claim model |
| `rxmembersim/claims/factory.py` | 46 | HIGH | Claim generation |
| `rxmembersim/claims/response.py` | 37 | HIGH | Response handling |

### Priority 2: Low Coverage Core Modules

| File | Current | Target | Lines to Cover |
|------|---------|--------|----------------|
| `state/auto_naming.py` | 12% | 80% | ~54 |
| `state/auto_persist.py` | 27% | 70% | ~150 |
| `generation/reference_profiles.py` | 25% | 75% | ~120 |
| `generation/journey_validation.py` | 27% | 70% | ~150 |

### Priority 3: Product Format Coverage

| Module | Current | Target |
|--------|---------|--------|
| `trialsim/formats/adam/` | 0% | 60% |
| `trialsim/formats/sdtm/` | 0% | 60% |
| `rxmembersim/dur/` | 0% | 60% |
| `rxmembersim/formulary/` | 0% | 60% |

---

## Implementation Plan

### Task 1: Validation Module Tests (Est: 1 hour)
Create `tests/unit/test_validation.py`:
- Test ValidationResult dataclass
- Test ValidationRule base class
- Test structural validators (required fields, types)
- Test temporal validators (date ranges, sequences)
- Test framework integration

### Task 2: RxMemberSim Claims Tests (Est: 1 hour)
Create `tests/unit/test_rxmembersim_claims.py`:
- Test PBMClaim model
- Test ClaimFactory generation
- Test AdjudicationEngine
- Test ClaimResponse

### Task 3: State Module Tests (Est: 1.5 hours)
Enhance `tests/unit/test_state_*.py`:
- Auto-naming generation patterns
- Auto-persist service lifecycle
- Profile/Journey manager integration

### Task 4: Generation Module Tests (Est: 1.5 hours)
Enhance `tests/unit/test_generation_*.py`:
- Reference profiles loading
- Journey validation rules
- Geography builder patterns

### Task 5: TrialSim Format Tests (Est: 1 hour)
Create `tests/unit/test_trialsim_formats.py`:
- SDTM domain generation
- ADaM dataset transformation
- Export file structure

---

## Test File Structure

```
tests/
├── unit/
│   ├── test_validation.py          # NEW
│   ├── test_rxmembersim_claims.py  # NEW
│   ├── test_trialsim_formats.py    # NEW (expand)
│   ├── test_state_auto_naming.py   # NEW
│   ├── test_state_auto_persist.py  # ENHANCE
│   └── test_generation_reference.py # NEW
└── integration/
    └── test_end_to_end.py          # ENHANCE
```

---

## Success Criteria

- [ ] All existing 690 tests still passing
- [ ] Coverage increased from 50% to >80%
- [ ] No critical modules at 0% coverage
- [ ] All new tests follow existing patterns
- [ ] CHANGELOG.md updated

---

## Post-Flight Checklist

- [ ] Run full test suite: `pytest tests/ -v`
- [ ] Verify coverage: `pytest tests/ --cov=src/healthsim_agent --cov-report=html`
- [ ] Update DEVELOPMENT-PLAN.md Phase 6 section
- [ ] Update CHANGELOG.md
- [ ] Git commit: `[Phase 6] Testing - Coverage increased to >80%`
- [ ] Git push

---

## Notes

- Focus on testing public APIs, not internal implementation details
- Use fixtures for common setup (test data, mock connections)
- Follow existing test patterns in the codebase
- Mark slow integration tests with `@pytest.mark.slow`
