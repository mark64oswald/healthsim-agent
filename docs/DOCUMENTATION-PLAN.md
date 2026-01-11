# HealthSim Agent Documentation Plan

**Created**: January 2026  
**Status**: Planning  
**Purpose**: Comprehensive documentation for healthsim-agent release

---

## Executive Summary

This plan outlines the documentation needed for healthsim-agent, adapting and improving upon the excellent healthsim-workspace documentation. The agent architecture is simpler for users (no MCP configuration required), but the documentation must clearly explain the new paradigm.

### Key Differences from Workspace

| Aspect | Workspace (MCP) | Agent (CLI) |
|--------|-----------------|-------------|
| Installation | Clone + MCP config + Claude Desktop | `pip install` + API key |
| Interface | Claude Desktop conversation | Rich CLI (`healthsim` command) |
| Skills | Context files for Claude | Built into agent |
| State | DuckDB via MCP server | DuckDB via agent |
| Tools | MCP tools (10) | Agent tools (15+) |

---

## Current Documentation State

### What Exists

```
docs/
├── FULL-PARITY-IMPLEMENTATION-PLAN.md  # Internal: migration tracking
├── GAP-ANALYSIS.md                      # Internal: comparison with workspace
├── HONEST-ASSESSMENT.md                 # Internal: state assessment
├── ISSUES.md                            # Internal: known issues
├── RELEASE-EVALUATION.md                # Internal: release readiness
├── SKILLS-MANAGEMENT-SYSTEM.md          # Technical: skills architecture
├── SKILLS-MANAGEMENT.md                 # Technical: skills usage
├── design/
│   └── cli-ux-mockup.html              # Design: UI mockup
├── migration/
│   └── migration-plan.md               # Internal: migration from workspace
├── reference/                           # Copied from workspace (needs review)
│   ├── GENERATIVE-FRAMEWORK-*.md       # Generation docs
│   ├── HEALTHSIM-*.md                  # Architecture docs
│   ├── api/                            # API docs (mostly stubs)
│   ├── guides/                         # User guides (empty)
│   ├── mcp/                            # Outdated MCP docs
│   └── skills/                         # Skills reference
└── ux-specification.md                 # Design: UX spec
```

### README.md Assessment

Current README is functional but needs:
- Better "quick start" with actual session example
- Feature highlights with visuals
- More detailed CLI documentation
- Better organization of information

---

## Documentation Structure Plan

### Target Structure

```
healthsim-agent/
├── README.md                           # Primary entry point
├── CHANGELOG.md                        # Version history
├── LICENSE                             # MIT license
│
├── docs/
│   ├── README.md                       # Docs navigation guide
│   │
│   ├── getting-started/               # NEW: User onboarding
│   │   ├── README.md                   # Getting started overview
│   │   ├── installation.md            # Detailed install instructions
│   │   ├── first-session.md           # Your first HealthSim session
│   │   ├── quick-reference.md         # Command cheat sheet
│   │   └── troubleshooting.md         # Common issues & solutions
│   │
│   ├── guides/                        # NEW: Task-focused guides
│   │   ├── README.md                   # Guides overview
│   │   ├── patientsim-guide.md        # Clinical data generation
│   │   ├── membersim-guide.md         # Claims data generation
│   │   ├── rxmembersim-guide.md       # Pharmacy data generation
│   │   ├── trialsim-guide.md          # Clinical trials guide
│   │   ├── populationsim-guide.md     # Demographics & SDOH
│   │   ├── networksim-guide.md        # Provider network data
│   │   ├── cross-product-guide.md     # Multi-product workflows
│   │   ├── analytics-guide.md         # Analytics & star schemas
│   │   └── state-management-guide.md  # Sessions & cohorts
│   │
│   ├── reference/                     # REORGANIZE: Technical reference
│   │   ├── README.md                   # Reference overview
│   │   ├── architecture.md            # System architecture
│   │   ├── cli-reference.md           # Complete CLI documentation
│   │   ├── tools-reference.md         # Agent tools documentation
│   │   ├── generation-framework.md    # Generation system details
│   │   ├── database-schema.md         # DuckDB schema reference
│   │   ├── output-formats.md          # FHIR, X12, NCPDP, etc.
│   │   ├── code-systems.md            # ICD-10, CPT, NDC, etc.
│   │   └── data-models.md             # Canonical data models
│   │
│   ├── skills/                        # Skills documentation
│   │   ├── README.md                   # Skills system overview
│   │   ├── creating-skills.md         # How to create new skills
│   │   ├── skill-format.md            # Skill file format reference
│   │   └── extending-domains.md       # Adding new product domains
│   │
│   ├── contributing/                  # NEW: Contributor docs
│   │   ├── README.md                   # Contributing overview
│   │   ├── development-setup.md       # Dev environment setup
│   │   ├── testing-guide.md           # Running & writing tests
│   │   ├── code-style.md              # Style guidelines
│   │   └── release-process.md         # How releases work
│   │
│   └── internal/                      # MOVE: Internal docs
│       ├── migration-plan.md          # Migration from workspace
│       ├── gap-analysis.md            # Feature comparison
│       └── issues.md                  # Known issues tracking
│
├── examples/                          # NEW: Working examples
│   ├── README.md                       # Examples overview
│   ├── basic/                          # Simple examples
│   │   ├── patient-generation.md
│   │   ├── claims-generation.md
│   │   └── pharmacy-generation.md
│   ├── intermediate/                   # More complex examples
│   │   ├── cross-product-workflow.md
│   │   ├── cohort-analytics.md
│   │   └── format-transformations.md
│   └── advanced/                       # Advanced use cases
│       ├── custom-skills.md
│       ├── batch-generation.md
│       └── integration-testing.md
│
└── skills/                            # Skills (already migrated)
    └── [existing structure]
```

---

## Documentation Deliverables

### Priority 1: Core User Documentation (Week 1)

#### 1.1 README.md Enhancement

Improve the main README with:
- [ ] Hero section with clear value proposition
- [ ] Installation quickstart (3 commands to running)
- [ ] Visual session example (terminal screenshot or code block)
- [ ] Feature matrix with domain coverage
- [ ] Quick reference card (inline)
- [ ] Link architecture to rest of docs

#### 1.2 Getting Started Guide

Create `docs/getting-started/`:

**README.md** - Getting started overview
- Prerequisites
- Installation paths (pip, source, dev)
- Next steps navigation

**installation.md** - Detailed installation
- System requirements
- Python version considerations
- Virtual environment setup
- API key configuration
- Verification steps
- Common installation issues

**first-session.md** - Your first session
- Starting the CLI
- Understanding the interface
- Your first generation request
- Saving your work
- Exiting properly

**quick-reference.md** - Command cheat sheet
- CLI commands table
- In-session slash commands
- Common generation patterns
- Format export options

**troubleshooting.md** - Common issues
- Installation problems
- API key issues
- Database errors
- Generation problems
- Format issues
- Performance optimization

### Priority 2: Product Guides (Week 1-2)

#### 2.1 Product-Specific Guides

Create comprehensive guides for each domain:

**patientsim-guide.md**
- Clinical data overview
- Patient generation patterns
- Chronic disease scenarios
- Oncology scenarios
- Format options (FHIR, HL7v2, C-CDA, MIMIC-III)
- Examples with expected outputs

**membersim-guide.md**
- Claims domain overview
- Professional claims generation
- Facility claims with DRG
- Adjudication scenarios
- Format options (X12 837/835)
- Examples with expected outputs

**rxmembersim-guide.md**
- Pharmacy domain overview
- Prescription generation
- PBM claims workflows
- DUR alerts
- Prior authorization
- Format options (NCPDP)
- Examples with expected outputs

**trialsim-guide.md**
- Clinical trials overview
- Phase 1/2/3 scenarios
- Subject enrollment
- Adverse events
- SDTM/ADaM outputs
- Examples with expected outputs

**populationsim-guide.md**
- Demographics & SDOH overview
- Geographic profiling
- Real data integration (CDC, SVI)
- Cohort specification
- Examples with expected outputs

**networksim-guide.md**
- Provider network overview
- Real provider queries (NPPES)
- Synthetic provider generation
- Facility and pharmacy generation
- Examples with expected outputs

### Priority 3: Reference Documentation (Week 2)

#### 3.1 Technical Reference

**architecture.md**
- System architecture diagram
- Component overview
- Data flow diagrams
- Skills system
- Tool layer

**cli-reference.md**
- Complete CLI documentation
- All commands with options
- Environment variables
- Configuration files

**tools-reference.md**
- All agent tools documented
- Parameters and return values
- Error handling
- Examples for each tool

**generation-framework.md**
- Generation system overview
- Profile specifications
- Journey engine
- Handlers and triggers
- Cross-product sync

**database-schema.md**
- DuckDB schema documentation
- Table descriptions
- Relationships
- Query examples

**output-formats.md**
- All supported formats
- Format selection guide
- Validation requirements
- Transformation examples

### Priority 4: Examples (Week 2-3)

#### 4.1 Example Library

**basic/**
- Simple patient generation
- Basic claims generation
- Pharmacy claim example

**intermediate/**
- Cross-product patient journey
- Cohort with analytics
- Multiple format exports

**advanced/**
- Custom skill creation
- Batch generation script
- Integration test scenario

### Priority 5: Contributing & Skills (Week 3)

#### 5.1 Contributor Documentation

**development-setup.md**
- Clone and setup
- Running tests
- Development workflow
- PR process

**testing-guide.md**
- Test structure
- Running tests
- Writing new tests
- CI/CD integration

**creating-skills.md**
- Skills architecture
- Skill file format
- YAML specification
- Adding to a product
- Testing new skills

---

## Migration from Workspace Documentation

### Content to Adapt

| Workspace File | Agent Destination | Notes |
|----------------|-------------------|-------|
| `hello-healthsim/README.md` | `docs/getting-started/first-session.md` | Adapt for CLI |
| `hello-healthsim/TROUBLESHOOTING.md` | `docs/getting-started/troubleshooting.md` | Remove MCP issues |
| `hello-healthsim/CLAUDE-*.md` | Remove | Not applicable |
| `hello-healthsim/EXTENDING.md` | `docs/skills/creating-skills.md` | Adapt for agent |
| `docs/HEALTHSIM-ARCHITECTURE-GUIDE.md` | `docs/reference/architecture.md` | Update for agent |
| `docs/data-architecture.md` | `docs/reference/database-schema.md` | Already similar |
| `docs/integration-guide.md` | `docs/guides/cross-product-guide.md` | Update for agent |
| `docs/contributing.md` | `docs/contributing/README.md` | Update for agent |
| `formats/*.md` | `docs/reference/output-formats.md` | Consolidate |

### Content to Remove

- All MCP-specific documentation
- Claude Desktop configuration
- Claude Code project setup
- MCP server troubleshooting

### Content to Create New

- CLI reference documentation
- Agent tools documentation
- Rich UI feature documentation
- In-session commands documentation

---

## Writing Standards

### Voice & Tone

- Friendly, practical, outcome-focused for users
- Clear, technical, comprehensive for developers
- Lead with examples, follow with explanation
- Use "you" for user-facing docs

### Formatting Standards

- Headers: Sentence case ("Getting started" not "Getting Started")
- Code blocks: Always specify language
- Tables: Use for comparisons and reference data
- Lists: Use sparingly, prefer prose for explanation
- Links: Use relative links within docs

### Example Format

Every guide should include:

1. **Overview** - What this feature/domain does
2. **Quick Start** - Get something working in <2 minutes
3. **Examples** - Multiple real examples with outputs
4. **Reference** - Detailed parameter/option documentation
5. **Troubleshooting** - Common issues specific to this area
6. **Next Steps** - Links to related documentation

---

## Implementation Plan

### Week 1: Core Documentation

- [ ] Enhance README.md
- [ ] Create docs/getting-started/ structure
- [ ] Write installation.md
- [ ] Write first-session.md
- [ ] Write quick-reference.md
- [ ] Adapt troubleshooting.md from workspace
- [ ] Begin product guides (PatientSim, MemberSim)

### Week 2: Product & Reference

- [ ] Complete all product guides
- [ ] Write cross-product-guide.md
- [ ] Write state-management-guide.md
- [ ] Write architecture.md
- [ ] Write cli-reference.md
- [ ] Write tools-reference.md
- [ ] Consolidate output-formats.md

### Week 3: Examples & Contributing

- [ ] Create basic/ examples
- [ ] Create intermediate/ examples
- [ ] Write development-setup.md
- [ ] Write testing-guide.md
- [ ] Write creating-skills.md
- [ ] Final review and link verification

---

## Success Criteria

### User Experience

- [ ] New user can install and run first command in <5 minutes
- [ ] All CLI commands documented with examples
- [ ] Every product domain has comprehensive guide
- [ ] Common issues have documented solutions

### Content Quality

- [ ] No broken links
- [ ] All code examples tested and working
- [ ] Consistent formatting throughout
- [ ] Clear navigation between sections

### Completeness

- [ ] README serves as effective landing page
- [ ] Getting started covers all installation scenarios
- [ ] Reference covers all tools and commands
- [ ] Examples cover basic through advanced usage

---

## Appendix: Quick Reference Card (for README)

```
## Quick Reference

### CLI Commands
healthsim              # Start interactive session
healthsim status       # Show database status
healthsim query SQL    # Execute SQL query
healthsim cohorts      # List saved cohorts
healthsim export NAME  # Export cohort data

### In-Session Commands
/help                  # Show help
/status                # Session status
/sql QUERY             # Execute SQL
/clear                 # Clear screen
/quit                  # Exit

### Generation Patterns
"Generate a diabetic patient"
"Create a professional claim for an office visit"
"Generate pharmacy claims for metformin"
"Create a Phase 3 oncology trial with 50 subjects"
"Profile Harris County, Texas"
"Find cardiologists in Houston"

### Format Exports
"Export as FHIR R4"
"Generate as X12 837P"
"Export in NCPDP format"
"Generate as CDISC SDTM"
```

---

*This plan will be updated as implementation progresses.*
