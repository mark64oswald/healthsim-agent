# HealthSim Agent

A conversational AI agent for healthcare data simulation. Generate realistic synthetic healthcare data through natural language conversations.

## Features

- **Conversational Interface** - Generate data through natural language, no complex APIs needed
- **Multiple Data Domains** - Patient records, claims, pharmacy, clinical trials, and more
- **Real Reference Data** - Grounded in actual demographic and provider data (CDC, Census, NPPES)
- **Rich Terminal UI** - Beautiful CLI with syntax highlighting and data previews

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

# Or run with options
healthsim --debug
```

### Example Interactions

```
healthsim › Generate a 45-year-old diabetic patient in Austin, TX

healthsim › Create pharmacy claims for their metformin prescription

healthsim › Show me providers near this patient who specialize in endocrinology
```

## Commands

| Command | Description |
|---------|-------------|
| `/help` | Show help information |
| `/status` | Display session status |
| `/clear` | Clear conversation history |
| `/export [file]` | Export generated data |
| `/quit` | Exit HealthSim |

## Data Domains

| Domain | Description |
|--------|-------------|
| **PatientSim** | Clinical/EMR patient records (FHIR, HL7v2, C-CDA) |
| **MemberSim** | Payer/claims data (X12 837/835/834) |
| **RxMemberSim** | Pharmacy/PBM records (NCPDP D.0) |
| **TrialSim** | Clinical trial data (CDISC SDTM/ADaM) |
| **PopulationSim** | Demographics and SDOH |
| **NetworkSim** | Provider network data (NPPES) |

## Architecture

HealthSim Agent uses a skills-based architecture where domain knowledge is encoded in Skills documents that guide the AI agent in generating realistic data.

```
src/healthsim_agent/
├── agent.py        # Core agent orchestration
├── ui/             # Rich terminal interface
├── state/          # Session and context management
├── db/             # DuckDB reference database
├── generation/     # Data generation framework
├── skills/         # Skill loading and routing
└── tools/          # MCP tool implementations
```

## Development

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=healthsim_agent

# Type checking
mypy src/healthsim_agent

# Linting
ruff check src/
```

## Documentation

- [UX Specification](docs/ux-specification.md)
- [Migration Plan](docs/migration/migration-plan.md)
- [Architecture Guide](docs/reference/HEALTHSIM-ARCHITECTURE-GUIDE.md)

## License

MIT License - see [LICENSE](LICENSE) for details.
