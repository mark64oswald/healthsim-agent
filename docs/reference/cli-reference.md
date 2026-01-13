# CLI Reference

The HealthSim Agent command-line interface (CLI) provides commands for interactive chat, database queries, cohort management, and data export.

## Installation

After installing HealthSim Agent, the `healthsim` command is available:

```bash
pip install healthsim-agent
healthsim --version
```

## Global Options

These options apply to all commands:

| Option | Description |
|--------|-------------|
| `--debug` | Enable debug mode with verbose output |
| `--config PATH` | Path to custom configuration file |
| `--version` | Show version and exit |
| `--help` | Show help message |

## Commands

### `healthsim` or `healthsim chat`

Start an interactive chat session.

```bash
# Start interactive session
healthsim

# With debug output
healthsim --debug

# With custom config
healthsim --config ./my-config.yaml
```

**Interactive Session Features:**
- Conversational data generation
- Natural language queries
- Auto-complete suggestions
- Session history
- Rich terminal output

**Session Commands (within chat):**
- `/help` - Show available commands
- `/status` - Show current session state
- `/clear` - Clear conversation history
- `/exit` or `/quit` - Exit the session

---

### `healthsim status`

Display database and configuration status.

```bash
healthsim status
```

**Output includes:**
- Database connection status and path
- Table counts for each schema
- NPPES provider count
- CDC PLACES data availability
- Saved cohort count

**Example output:**
```
╭────────────────────────────────────────╮
│            HealthSim Status            │
├─────────────────┬─────────┬────────────┤
│ Component       │ Status  │ Details    │
├─────────────────┼─────────┼────────────┤
│ Database        │ ✓       │ ./healthsim.duckdb │
│ Tables          │ 8       │ main schema        │
│ NPPES Providers │ 8,934,127│ network.providers  │
│ CDC PLACES      │ 3,142   │ population.places  │
│ Cohorts         │ 5       │ Saved cohorts      │
╰─────────────────┴─────────┴────────────╯
```

---

### `healthsim query`

Execute a SQL query against the database.

```bash
healthsim query "SQL_STATEMENT" [OPTIONS]
```

**Arguments:**
| Argument | Description |
|----------|-------------|
| `SQL` | SQL query to execute |

**Options:**
| Option | Default | Description |
|--------|---------|-------------|
| `--format`, `-f` | `table` | Output format: `table`, `json`, `csv` |
| `--limit`, `-n` | `100` | Maximum rows to return |

**Examples:**

```bash
# Query cohorts
healthsim query "SELECT * FROM cohorts"

# Query providers with JSON output
healthsim query "SELECT npi, name FROM network.providers WHERE state = 'CA'" -f json -n 50

# Query population data
healthsim query "SELECT county, diabetes_prevalence FROM population.places_county WHERE state = 'TX' ORDER BY diabetes_prevalence DESC" -n 10

# Export to CSV
healthsim query "SELECT * FROM cohort_entities WHERE cohort_id = 'my-cohort'" -f csv > entities.csv
```

**Schemas available:**
- `main` - HealthSim entities (cohorts, profiles, journeys)
- `network` - NPPES provider data
- `population` - CDC PLACES, SVI data

---

### `healthsim cohorts`

List all saved cohorts.

```bash
healthsim cohorts
```

**Output columns:**
| Column | Description |
|--------|-------------|
| ID | Cohort identifier (truncated) |
| Name | Cohort name |
| Description | Brief description |
| Entities | Number of entities in cohort |
| Created | Creation timestamp |

**Example output:**
```
╭─────────────┬──────────────────┬─────────────────┬──────────┬─────────────────╮
│ ID          │ Name             │ Description     │ Entities │ Created         │
├─────────────┼──────────────────┼─────────────────┼──────────┼─────────────────┤
│ abc123...   │ diabetes-study   │ T2DM patients   │ 285      │ 2024-01-15 14:30│
│ def456...   │ cardiac-demo     │ CHF cohort      │ 50       │ 2024-01-10 09:15│
│ ghi789...   │ trial-subjects   │ Phase 3 trial   │ 120      │ 2024-01-08 16:45│
╰─────────────┴──────────────────┴─────────────────┴──────────┴─────────────────╯
3 cohorts total
```

---

### `healthsim export`

Export a cohort to various formats.

```bash
healthsim export COHORT_ID [OPTIONS]
```

**Arguments:**
| Argument | Description |
|----------|-------------|
| `COHORT_ID` | Cohort ID or name to export |

**Options:**
| Option | Default | Description |
|--------|---------|-------------|
| `--format`, `-f` | `summary` | Export format: `summary`, `json`, `fhir`, `csv` |
| `--output`, `-o` | stdout | Output file path |

**Format descriptions:**
| Format | Description |
|--------|-------------|
| `summary` | Table showing entity type counts |
| `json` | Raw JSON with all entities |
| `fhir` | FHIR R4 Bundle |
| `csv` | CSV files per entity type |

**Examples:**

```bash
# Show cohort summary
healthsim export diabetes-study

# Export as JSON
healthsim export diabetes-study -f json -o patients.json

# Export as FHIR bundle
healthsim export diabetes-study -f fhir -o bundle.json

# Export as CSV (creates multiple files)
healthsim export diabetes-study -f csv -o ./export/
```

---

## Configuration

Configuration can be provided via:
1. Command-line option: `--config path/to/config.yaml`
2. Environment variable: `HEALTHSIM_CONFIG`
3. Default location: `~/.healthsim/config.yaml`

**Configuration file format:**

```yaml
# HealthSim Configuration
database:
  path: ./healthsim.duckdb
  
skills:
  directory: ./skills
  
agent:
  model: claude-sonnet-4-20250514
  
logging:
  level: INFO
```

---

## Exit Codes

| Code | Description |
|------|-------------|
| `0` | Success |
| `1` | General error |
| `2` | Invalid arguments |
| `3` | Database connection error |

---

## Environment Variables

| Variable | Description |
|----------|-------------|
| `HEALTHSIM_CONFIG` | Path to configuration file |
| `HEALTHSIM_DB` | Path to database file |
| `HEALTHSIM_SKILLS` | Path to skills directory |
| `ANTHROPIC_API_KEY` | API key for Claude (required for chat) |

---

## Related Documentation

- [Tools Reference](tools-reference.md) - Agent tool functions
- [Output Formats](output-formats.md) - Export format details
- [Getting Started](../getting-started/README.md) - Installation and setup
