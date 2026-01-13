# Development Setup Guide

Set up your environment for HealthSim Agent development.

## Prerequisites

- Python 3.10 or higher
- Git
- 4GB+ available disk space (for reference data)
- Anthropic API key (for testing agent functionality)

## Installation

### 1. Clone the Repository

```bash
# Fork first on GitHub, then:
git clone https://github.com/YOUR_USERNAME/healthsim-agent.git
cd healthsim-agent
```

### 2. Create Virtual Environment

```bash
# Create environment
python -m venv venv

# Activate (macOS/Linux)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate
```

### 3. Install Development Dependencies

```bash
# Install in editable mode with dev dependencies
pip install -e ".[dev]"
```

This installs:
- Core HealthSim packages
- Testing: pytest, pytest-cov, pytest-asyncio
- Linting: ruff, black
- Type checking: mypy
- Documentation: mkdocs

### 4. Set Up Environment Variables

```bash
# Create .env file
cp .env.example .env

# Edit with your values
ANTHROPIC_API_KEY=your-key-here
HEALTHSIM_DB=./healthsim_data.duckdb
HEALTHSIM_SKILLS=./skills
```

Or export directly:

```bash
export ANTHROPIC_API_KEY=your-key-here
```

### 5. Initialize Database

```bash
# Run database setup
python scripts/setup_database.py
```

This creates the DuckDB database and loads reference data:
- NPPES providers (~8.9M records)
- CDC PLACES county/tract data
- SVI indices

**Note**: Initial setup takes 5-10 minutes and requires ~1.9GB disk space.

## Verify Installation

### Run Tests

```bash
# Run all tests
pytest

# With coverage
pytest --cov=src/healthsim_agent --cov-report=term-missing

# Just unit tests (fast)
pytest tests/unit/

# Integration tests (requires API key)
pytest tests/integration/
```

### Start the Agent

```bash
# Interactive mode
healthsim

# Check version
healthsim --version

# Check status
healthsim status
```

## Directory Structure

```
healthsim-agent/
├── src/healthsim_agent/          # Main package
│   ├── agent.py                  # Agent entry point
│   ├── tools/                    # Agent tools
│   │   ├── generate.py
│   │   ├── query.py
│   │   ├── export.py
│   │   ├── validate.py
│   │   └── state.py
│   ├── skills/                   # Skill loader/indexer
│   ├── formats/                  # Output transformers
│   └── database/                 # DuckDB operations
├── skills/                       # Skill markdown files
│   ├── patientsim/
│   ├── membersim/
│   ├── rxmembersim/
│   ├── trialsim/
│   ├── populationsim/
│   └── networksim/
├── tests/                        # Test suite
│   ├── unit/
│   ├── integration/
│   └── fixtures/
├── docs/                         # Documentation
│   ├── guides/
│   ├── reference/
│   ├── examples/
│   └── skills/
├── scripts/                      # Utility scripts
└── reference_data/               # Source data files
```

## Development Workflow

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Make Changes

Edit code, add tests, update docs.

### 3. Run Quality Checks

```bash
# Format code
black .

# Lint
ruff check .

# Type check
mypy src/

# Run tests
pytest
```

### 4. Commit Changes

```bash
git add .
git commit -m "feat(scope): description"
```

### 5. Push and Create PR

```bash
git push origin feature/your-feature-name
# Then create PR on GitHub
```

## IDE Setup

### VS Code

Recommended extensions:
- Python
- Pylance
- Black Formatter
- Ruff
- Even Better TOML
- Markdown All in One

Settings (`.vscode/settings.json`):
```json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.formatting.provider": "black",
    "editor.formatOnSave": true,
    "[python]": {
        "editor.defaultFormatter": "ms-python.black-formatter"
    },
    "python.linting.enabled": true
}
```

### PyCharm

1. Set project interpreter to `./venv/bin/python`
2. Enable Black as formatter
3. Enable Ruff as linter
4. Configure pytest as test runner

## Database Development

### Connect to DuckDB

```python
import duckdb

# Read-only connection
conn = duckdb.connect("healthsim_data.duckdb", read_only=True)

# Query reference data
conn.execute("SELECT COUNT(*) FROM network.nppes_providers").fetchone()
# (8934127,)

# List tables
conn.execute("SHOW TABLES").fetchall()
```

### Reset Database

```bash
# Remove and recreate
rm healthsim_data.duckdb
python scripts/setup_database.py
```

## Skills Development

### Create New Skill

1. Create file in appropriate directory:
   ```bash
   touch skills/patientsim/clinical/new-skill.md
   ```

2. Add YAML frontmatter:
   ```yaml
   ---
   name: new-skill
   description: Description with trigger phrases
   category: clinical
   product: patientsim
   version: 1.0
   ---
   ```

3. Add required sections:
   - Overview
   - Parameters table
   - Examples (at least 2)
   - Validation Rules
   - Related Skills

4. Update skill catalog:
   ```bash
   # Rebuild index
   healthsim index-skills
   ```

### Validate Skill Format

```bash
# Check skill structure
python scripts/validate_skill.py skills/patientsim/clinical/new-skill.md
```

## Troubleshooting

### Import Errors

```bash
# Ensure you're in venv
which python
# Should be: ./venv/bin/python

# Reinstall
pip install -e ".[dev]"
```

### Database Errors

```bash
# Check database exists
ls -la healthsim_data.duckdb

# Verify tables
healthsim query "SHOW TABLES"
```

### Test Failures

```bash
# Run with verbose output
pytest -v --tb=long

# Run single test file
pytest tests/unit/test_tools.py -v

# Run specific test
pytest tests/unit/test_tools.py::test_generate_patient -v
```

### API Key Issues

```bash
# Verify key is set
echo $ANTHROPIC_API_KEY

# Test connection
python -c "from anthropic import Anthropic; print(Anthropic().models.list())"
```

## Related Documentation

- [Testing Guide](testing-guide.md) - Writing and running tests
- [Code Style](code-style.md) - Coding conventions
- [Skill Format](../skills/skill-format.md) - Skill authoring
