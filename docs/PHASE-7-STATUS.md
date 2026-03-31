# Phase 7 Documentation Status

**Last Updated:** 2026-01-13T05:45:00Z
**Session:** Fixing GitHub sync issues

---

## Current Problem

Files exist locally but were NOT pushed to GitHub. The commit `52cd5613` is ahead of origin/main by 1 commit.

---

## What's on GitHub (source of truth)

### docs/guides/ (3 files only)
- [x] README.md
- [x] patientsim-guide.md  
- [x] membersim-guide.md
- [ ] rxmembersim-guide.md - EXISTS LOCALLY, NOT PUSHED
- [ ] trialsim-guide.md - EXISTS LOCALLY, NOT PUSHED
- [ ] populationsim-guide.md - EXISTS LOCALLY, NOT PUSHED
- [ ] networksim-guide.md - EXISTS LOCALLY, NOT PUSHED
- [ ] cross-product-guide.md - EXISTS LOCALLY, NOT PUSHED
- [ ] state-management-guide.md - EXISTS LOCALLY, NOT PUSHED

### examples/ (1 file only)
- [x] README.md
- [x] basic/patient-generation.md
- [ ] basic/claims-generation.md - EXISTS LOCALLY, NOT PUSHED
- [ ] basic/pharmacy-generation.md - EXISTS LOCALLY, NOT PUSHED
- [ ] basic/provider-search.md - EXISTS LOCALLY, NOT PUSHED
- [ ] intermediate/* - EXISTS LOCALLY, NOT PUSHED
- [ ] advanced/* - EXISTS LOCALLY, NOT PUSHED

---

## Files That Exist Locally (need push)

### docs/guides/
```
cross-product-guide.md    (12K)
networksim-guide.md       (10K)
populationsim-guide.md    (9.5K)
rxmembersim-guide.md      (11K)
state-management-guide.md (9K)
trialsim-guide.md         (10K)
```

### examples/basic/
```
claims-generation.md
pharmacy-claims.md
pharmacy-generation.md
provider-search.md
```

### examples/intermediate/
```
cohort-analytics.md
cross-product-workflow.md
denial-scenarios.md
format-transformations.md
oncology-scenarios.md
```

### examples/advanced/
```
clinical-trial-protocol.md
full-data-pipeline.md
population-study.md
```

---

## Action Required

1. Stage all untracked/modified files
2. Commit changes
3. Push to origin/main
4. Verify on GitHub

---

## Session Notes

The bash_tool runs in a container that is NOT the same as the filesystem MCP server.
- filesystem:* tools → access real local files
- bash_tool → runs in isolated container
- git:* tools → access real local git repo

Must use git:* tools for git operations, NOT bash_tool.
