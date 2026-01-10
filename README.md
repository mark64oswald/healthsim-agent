# HealthSim Agent

A conversational AI agent for healthcare data simulation. Generate realistic synthetic healthcare data through natural language conversations.

## Features

- **Conversational Interface** - Generate data through natural language, no complex APIs needed
- **Multiple Data Domains** - Patient records, claims, pharmacy, clinical trials, and more
- **Real Reference Data** - Grounded in actual demographic and provider data (CDC, Census, NPPES)
- **Rich Terminal UI** - Beautiful CLI with syntax highlighting and data previews
- **Format Transformations** - Export to FHIR R4, C-CDA, HL7v2, X12, NCPDP, MIMIC-III

## Installation

### Prerequisites

- Python 3.11 or higher
- An Anthropic API key

### Install from source

```bash
# Clone the repository
git clone https://github.com/mark64oswald/healthsim-agent.git
cd healthsim-agent

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install with dependencies
pip install -e ".[dev]"
```

### Set up API key

```bash
export ANTHROPIC_API_KEY="your-api-key"
```

## Quick Start

```bash
# Start interactive session
healthsim

# Or run as module
python -m healthsim_agent
```

## CLI Commands

### Interactive Chat

```bash
# Start interactive chat (default)
healthsim
healthsim chat
healthsim --debug  # Enable debug mode
```

### Status

```bash
# Show database and configuration status
healthsim status
```

Output shows:
- Database connection status
- Available tables
- Reference data counts (NPPES providers, CDC PLACES)
- Saved cohorts

### Query

```bash
# Execute SQL queries directly
healthsim query "SELECT * FROM cohorts"
healthsim query "SELECT COUNT(*) FROM patients" --format json
healthsim query "SELECT * FROM members" --format csv --limit 50
```

Options:
- `--format, -f`: Output format (table, json, csv). Default: table
- `--limit, -n`: Max rows to return. Default: 100

### Cohorts

```bash
# List all saved cohorts
healthsim cohorts
```

### Export

```bash
# Export cohort data
healthsim export my-cohort                          # Summary
healthsim export my-cohort --format json -o data.json
healthsim export my-cohort --format fhir -o bundle.json
healthsim export my-cohort --format csv -o patients.csv
```

Options:
- `--format, -f`: Export format (summary, json, fhir, csv). Default: summary
- `--output, -o`: Output file path

## In-Session Commands

While in interactive mode:

| Command | Description |
|---------|-------------|
| `/help` | Show help information |
| `/status` | Display session status |
| `/clear` | Clear screen |
| `/sql <query>` | Execute SQL directly |
| `/quit` | Exit HealthSim |

## Example Session

```
healthsim › Generate a 45-year-old diabetic patient in Austin, TX

✓ Added 1 patient

  MRN: PAT-001
  Name: Michael Rodriguez
  Age: 45
  Diagnoses: E11.9 Type 2 diabetes mellitus

healthsim › Create pharmacy claims for their metformin prescription

✓ Added 1 prescription

healthsim › Export to FHIR

✓ Generated FHIR R4 bundle with 1 patient

healthsim › /quit
```

## Data Domains

| Domain | Description | Output Formats |
|--------|-------------|----------------|
| **PatientSim** | Clinical/EMR patient records | FHIR R4, HL7v2, C-CDA, MIMIC-III |
| **MemberSim** | Payer/claims data | X12 837/835/834, JSON |
| **RxMemberSim** | Pharmacy/PBM records | NCPDP SCRIPT, JSON |
| **TrialSim** | Clinical trial data | CDISC SDTM/ADaM |
| **PopulationSim** | Demographics and SDOH | JSON, CSV |
| **NetworkSim** | Provider network data | JSON, CSV |

## Architecture

HealthSim Agent uses a skills-based architecture where domain knowledge is encoded in Skills documents that guide the AI agent in generating realistic data.

```
src/healthsim_agent/
├── main.py         # CLI entry point
├── agent.py        # Core agent orchestration
├── ui/             # Rich terminal interface
├── state/          # Session and context management
├── tools/          # Database and format tools
├── products/       # Domain-specific generators
│   ├── patientsim/ # Patient/clinical data
│   ├── membersim/  # Claims data
│   ├── rxmembersim/# Pharmacy data
│   └── trialsim/   # Clinical trials
├── person/         # Base person models
└── generation/     # Data generation framework
```

## Development

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=healthsim_agent

# Run specific test file
pytest tests/unit/test_tools.py -v

# Run integration tests
pytest tests/integration/ -v
```

### Test Status

- **Unit Tests**: 582 passing
- **Integration Tests**: 7 passing
- **Total**: 589 tests passing

## Configuration

Set environment variables:

```bash
# Required
export ANTHROPIC_API_KEY="your-api-key"

# Optional - custom database path
export HEALTHSIM_DB_PATH="/path/to/healthsim.duckdb"
```

## License

MIT

## Related Projects

- [healthsim-workspace](https://github.com/mark64oswald/healthsim-workspace) - Full healthcare simulation platform
