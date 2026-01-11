# HealthSim Agent - Claude Project Instructions

*Condensed guardrails for Phase 6-7 development*

---

## Project Overview

**healthsim-agent** is a standalone CLI agent using the Anthropic Agent SDK that generates synthetic healthcare data across 4 products (PatientSim, MemberSim, RxMemberSim, TrialSim) and transforms to 12 industry formats.

**Repository**: https://github.com/mark64oswald/healthsim-agent  
**Local Path**: `/Users/markoswald/Developer/projects/healthsim-agent`

---

## Current Status

- **Phase 6**: Testing & Polish - **NEXT**
- **Phase 7**: Documentation & Release - Pending
- **Tests**: 663 passing
- **Issues**: No critical/high priority remaining

---

## Session Protocol

### Starting Every Session

1. **Read `CURRENT-WORK.md`** - Live state tracker
2. **Verify git state**:
   ```bash
   cd /Users/markoswald/Developer/projects/healthsim-agent
   git log --oneline -3
   ```
3. **Run tests** to confirm clean state:
   ```bash
   source .venv/bin/activate
   pytest tests/ -v --tb=short
   ```

### During a Session

- Commit frequently after major changes
- Update `CURRENT-WORK.md` if significant progress
- If context feels heavy, suggest continuing in new session

### Ending Every Session

1. Run tests: `pytest tests/ -v`
2. Commit with descriptive message: `[Component] Brief description`
3. Update `CURRENT-WORK.md` with progress
4. Push: `git push`

---

## Key Documents

| Document | Purpose |
|----------|---------|
| `CURRENT-WORK.md` | Live session state |
| `DEVELOPMENT-PLAN.md` | Full phase breakdown |
| `docs/ISSUES.md` | Issue tracker |
| `docs/RELEASE-EVALUATION.md` | Release readiness |
| `docs/ux-specification.md` | UI requirements |

---

## Architecture Quick Reference

```
healthsim-agent/
├── src/healthsim_agent/
│   ├── agent.py           # Core orchestration
│   ├── main.py            # CLI entry point
│   ├── db/                # DuckDB connection, queries
│   ├── generation/        # Distributions, generators, handlers
│   ├── skills/            # Loader, router, models
│   ├── tools/             # Cohort, query, reference, format tools
│   └── ui/                # Terminal, components, formatters
├── skills/                # 175 skill files (6 products)
├── tests/                 # 663 tests
└── docs/                  # Design docs, specs
```

---

## Test Failure Policy

When tests fail:
1. **STOP and diagnose** before changes
2. **Never modify assertions** just to pass
3. **Ask if uncertain** - test vs implementation fault
4. Fix root cause, not symptoms

---

## Phase 6 Tasks (Testing & Polish)

- [ ] Unit test coverage >80%
- [ ] Edge case tests
- [ ] Integration tests (end-to-end, database, export)
- [ ] Performance profiling
- [ ] Bug fixes and polish

## Phase 7 Tasks (Documentation & Release)

- [ ] README with examples
- [ ] Quick-start guide
- [ ] API reference
- [ ] Version bump and changelog
- [ ] Tag release

---

## Quick Commands

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src/healthsim_agent --cov-report=html

# Run CLI
healthsim

# Debug mode
healthsim --debug
```

---

*See DEVELOPMENT-PLAN.md for complete phase details*
