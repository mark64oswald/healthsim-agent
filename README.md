# HealthSim Agent

<p align="center">
  <strong>Generate realistic synthetic healthcare data through natural conversation.</strong>
</p>

<p align="center">
  <a href="#quick-start">Quick Start</a> •
  <a href="#features">Features</a> •
  <a href="#installation">Installation</a> •
  <a href="docs/getting-started/">Getting Started</a> •
  <a href="#data-domains">Data Domains</a> •
  <a href="docs/">Documentation</a>
</p>

---

## What is HealthSim Agent?

HealthSim Agent is a conversational AI that generates realistic synthetic healthcare data. Describe what you need in plain English, and HealthSim creates clinically plausible patient records, insurance claims, pharmacy transactions, clinical trial data, and more—all without exposing real PHI.

```
healthsim › Generate a 65-year-old diabetic patient with hypertension in Houston, TX

✓ Added 1 patient to current session

  ID:        PAT-001
  Name:      Robert Johnson  
  Age:       65
  Location:  Houston, TX
  
  Diagnoses:
    • E11.9  Type 2 diabetes mellitus
    • I10    Essential hypertension
  
  Medications:
    • Metformin 1000mg BID
    • Lisinopril 20mg daily
    • Atorvastatin 40mg daily

healthsim › Create a professional claim for their recent office visit

✓ Added 1 claim

  Claim:     CLM-2026-000001
  Type:      Professional (837P)
  Service:   99214 - Office visit, established patient
  Charges:   $185.00
  Allowed:   $142.50
  Status:    Paid

healthsim › Export as FHIR R4

✓ Generated FHIR R4 Bundle → patient-bundle.json

healthsim ›
```

**No coding required.** Just describe what you need.

---

## Quick Start

```bash
# Install
pip install healthsim-agent

# Set your API key
export ANTHROPIC_API_KEY="your-key-here"

# Start generating
healthsim
```

That's it! You're ready to generate healthcare data.

---

## Features

### 🗣️ Conversation-First

Generate data through natural language. No complex APIs, no configuration files—just describe what you need.

### 🏥 Six Healthcare Domains

| Domain | Data Types | Output Formats |
|--------|------------|----------------|
| **PatientSim** | Patients, encounters, diagnoses, medications, labs | FHIR R4, HL7v2, C-CDA, MIMIC-III |
| **MemberSim** | Members, enrollment, professional & facility claims | X12 837/835/834, JSON |
| **RxMemberSim** | Prescriptions, pharmacy claims, DUR, prior auth | NCPDP SCRIPT, D.0, JSON |
| **TrialSim** | Trials, subjects, adverse events, efficacy | CDISC SDTM, ADaM |
| **PopulationSim** | Demographics, SDOH, health indicators | JSON, CSV, SQL |
| **NetworkSim** | Providers, facilities, pharmacies, networks | JSON, CSV |

### 📊 Real Reference Data

PopulationSim and NetworkSim include **real data** embedded in DuckDB:
- **CDC PLACES** - Health indicators for every US county and census tract
- **Social Vulnerability Index** - SDOH metrics at tract level
- **NPPES Registry** - 8.9 million real US healthcare providers

Your synthetic data is grounded in actual population statistics.

### 🎨 Rich Terminal Interface

Beautiful CLI with syntax highlighting, data previews, and helpful suggestions:

- Color-coded output for easy reading
- Inline data tables and summaries
- Contextual suggestions based on your session
- Progress indicators for long operations

### 💾 Persistent State

Save your work, come back later, explore alternatives:

```
healthsim › save as diabetes-cohort

✓ Saved session to 'diabetes-cohort'

healthsim › /quit

# Later...

healthsim › load diabetes-cohort

✓ Loaded 15 patients, 47 encounters, 23 claims

healthsim ›
```

### 🔄 Cross-Product Integration

Generate complete patient journeys that span multiple domains:

```
Generate a diabetic patient with their recent office visit claims 
and pharmacy fills for their medications
```

HealthSim creates linked data across PatientSim, MemberSim, and RxMemberSim with consistent identifiers.

---

## Installation

### Requirements

- Python 3.11 or higher
- An [Anthropic API key](https://console.anthropic.com/)

### Install with pip

```bash
pip install healthsim-agent
```

### Install from source

```bash
git clone https://github.com/mark64oswald/healthsim-agent.git
cd healthsim-agent
pip install -e ".[dev]"
```

### Configure API Key

```bash
# Set for current session
export ANTHROPIC_API_KEY="your-key-here"

# Or add to your shell profile (~/.zshrc, ~/.bashrc)
echo 'export ANTHROPIC_API_KEY="your-key-here"' >> ~/.zshrc
```

### Verify Installation

```bash
healthsim status
```

You should see database status and reference data counts.

---

## Data Domains

### PatientSim — Clinical/EMR Data

Generate patients with clinically plausible medical histories.

```
Generate a 45-year-old with heart failure and recent hospitalization
```

**Capabilities:**
- Demographics and identifiers
- Diagnoses (ICD-10) with onset dates
- Medications with dosing
- Lab results with reference ranges
- Encounters (inpatient, outpatient, ED)
- Oncology staging and biomarkers

**Formats:** FHIR R4, HL7v2 ADT, C-CDA, MIMIC-III

### MemberSim — Claims/Payer Data

Generate health plan members with enrollment and claims history.

```
Generate a family of 4 with commercial PPO coverage and 12 months of claims
```

**Capabilities:**
- Member enrollment and eligibility
- Professional claims (837P)
- Facility claims (837I) with DRG
- Remittance advice (835)
- Adjudication with CARC/RARC codes
- Prior authorization workflows

**Formats:** X12 837P, 837I, 835, 834, JSON

### RxMemberSim — Pharmacy/PBM Data

Generate prescription and pharmacy benefit data.

```
Generate a specialty pharmacy claim for Humira with prior authorization
```

**Capabilities:**
- Prescriptions (NCPDP SCRIPT)
- Pharmacy claims with pricing
- Drug Utilization Review (DUR) alerts
- Formulary and tier structures
- Prior authorization workflows
- Specialty pharmacy programs

**Formats:** NCPDP SCRIPT, D.0, JSON

### TrialSim — Clinical Trials Data

Generate clinical trial data for testing regulatory systems.

```
Generate a Phase 3 breast cancer trial with 200 subjects and SDTM output
```

**Capabilities:**
- Trial design (phases, arms, endpoints)
- Subject demographics and disposition
- Adverse events with MedDRA coding
- Efficacy endpoints (RECIST, biomarkers)
- Laboratory and vital signs

**Formats:** CDISC SDTM, ADaM, JSON

### PopulationSim — Demographics & SDOH

Access real population data and create evidence-based cohort specifications.

```
Profile Maricopa County for diabetes prevalence and social vulnerability
```

**Capabilities:**
- County and tract-level health indicators
- CDC PLACES chronic disease data
- Social Vulnerability Index (SVI)
- Area Deprivation Index (ADI)
- Cohort specifications for generation

**Data Sources:** Real CDC, Census, and HHS data embedded in DuckDB

### NetworkSim — Provider Networks

Query real providers or generate synthetic ones.

```
Find all cardiologists in Harris County, Texas
```

**Capabilities:**
- Query NPPES registry (8.9M providers)
- Provider search by specialty, location
- Network adequacy analysis
- Synthetic provider generation
- Facility and pharmacy data

**Data Sources:** Real NPPES data for queries; synthetic generation available

---

## CLI Reference

### Commands

| Command | Description |
|---------|-------------|
| `healthsim` | Start interactive session |
| `healthsim status` | Show database and session status |
| `healthsim query SQL` | Execute SQL query directly |
| `healthsim cohorts` | List saved cohorts |
| `healthsim export NAME` | Export a saved cohort |

### Interactive Commands

While in a session, use slash commands:

| Command | Description |
|---------|-------------|
| `/help` | Show available commands |
| `/status` | Display session status |
| `/sql QUERY` | Execute SQL query |
| `/clear` | Clear the screen |
| `/quit` | Exit HealthSim |

### Command Options

```bash
# Enable debug mode
healthsim --debug

# Query with specific format
healthsim query "SELECT * FROM patients" --format json

# Export with format and output file
healthsim export my-cohort --format fhir --output bundle.json
```

---

## Example Session

```
healthsim › Generate 10 diabetic patients in Texas with varying A1C levels

✓ Added 10 patients

  Summary:
    Patients:    10
    Avg Age:     58.3
    A1C Range:   6.2 - 11.4
    Location:    TX (Houston: 4, Dallas: 3, Austin: 2, San Antonio: 1)

healthsim › Add office visit claims for each patient

✓ Added 10 claims

  Claims generated for E&M services (99213, 99214)
  Total charges: $1,650.00

healthsim › Generate pharmacy claims for their metformin prescriptions

✓ Added 10 pharmacy claims

  All patients on Metformin 500-1000mg
  Average copay: $8.50

healthsim › Export the patients as FHIR R4

✓ Generated FHIR R4 Bundle → output/patients-bundle.json

  Bundle contains:
    10 Patient resources
    10 Condition resources (diabetes)
    32 MedicationRequest resources

healthsim › save as texas-diabetes-cohort

✓ Saved session 'texas-diabetes-cohort'

healthsim › /quit
```

---

## Development

### Setup

```bash
git clone https://github.com/mark64oswald/healthsim-agent.git
cd healthsim-agent
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### Run Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=healthsim_agent

# Specific test file
pytest tests/unit/test_tools.py -v
```

### Test Status

- **Unit Tests:** 582 passing
- **Integration Tests:** 7 passing
- **Total:** 589 tests passing ✓

---

## Architecture

```
healthsim-agent/
├── src/healthsim_agent/
│   ├── agent.py            # Core agent orchestration
│   ├── main.py             # CLI entry point
│   ├── ui/                 # Rich terminal interface
│   ├── state/              # Session & context management
│   ├── tools/              # Agent tool implementations
│   ├── products/           # Domain-specific generators
│   │   ├── patientsim/
│   │   ├── membersim/
│   │   ├── rxmembersim/
│   │   └── trialsim/
│   ├── generation/         # Generation framework
│   └── db/                 # Database layer
├── skills/                 # Domain knowledge (markdown)
├── data/                   # Reference data (DuckDB)
└── tests/                  # Test suite
```

---

## Documentation

- **[Getting Started](docs/getting-started/)** - Installation and first steps
- **[User Guides](docs/guides/)** - Product-specific guides
- **[Reference](docs/reference/)** - Technical documentation
- **[Examples](examples/)** - Working examples
- **[Contributing](docs/contributing/)** - Development guide

---

## License

MIT License - see [LICENSE](LICENSE)

---

## Related Projects

- [healthsim-workspace](https://github.com/mark64oswald/healthsim-workspace) - MCP-based platform (predecessor)

---

## Disclaimer

HealthSim generates **synthetic test data only**. It is not a clinical decision support system and does not provide medical advice, diagnosis, or treatment guidance. Generated data reflects general healthcare patterns for software testing, development, and demonstration purposes.

**Never use HealthSim output for actual patient care decisions.**
