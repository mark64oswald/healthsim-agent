# Testing Guide

HealthSim Agent uses pytest for testing. This guide covers how to write and run tests.

## Test Structure

```
tests/
├── unit/                    # Fast, isolated tests
│   ├── test_tools.py        # Tool function tests
│   ├── test_skills.py       # Skill loading/parsing tests
│   ├── test_formats.py      # Output format tests
│   └── test_database.py     # Database operation tests
├── integration/             # End-to-end tests (require API key)
│   ├── test_agent.py        # Full agent conversation tests
│   ├── test_generation.py   # Data generation tests
│   └── test_export.py       # Export pipeline tests
├── fixtures/                # Test data and mocks
│   ├── sample_cohorts.json
│   ├── sample_patients.json
│   └── conftest.py          # Shared fixtures
└── conftest.py              # Root pytest configuration
```

## Running Tests

### All Tests

```bash
# Run everything
pytest

# With verbose output
pytest -v

# Stop on first failure
pytest -x

# Run last failed
pytest --lf
```

### Specific Tests

```bash
# Single file
pytest tests/unit/test_tools.py

# Single test class
pytest tests/unit/test_tools.py::TestGenerateTool

# Single test function
pytest tests/unit/test_tools.py::TestGenerateTool::test_generate_patient

# By marker
pytest -m "unit"
pytest -m "integration"
pytest -m "slow"
```

### With Coverage

```bash
# Terminal report
pytest --cov=src/healthsim_agent --cov-report=term-missing

# HTML report
pytest --cov=src/healthsim_agent --cov-report=html
open htmlcov/index.html
```

## Writing Tests

### Unit Tests

Unit tests should be fast, isolated, and test a single unit of code.

```python
# tests/unit/test_tools.py

import pytest
from healthsim_agent.tools.generate import generate_patient

class TestGeneratePatient:
    """Tests for patient generation."""
    
    def test_generate_single_patient(self):
        """Generate a single patient with defaults."""
        result = generate_patient(count=1)
        
        assert result.success
        assert len(result.data) == 1
        assert "patient_id" in result.data[0]
        assert "name" in result.data[0]
    
    def test_generate_with_age_range(self):
        """Generate patient within age range."""
        result = generate_patient(count=1, age_range=(65, 75))
        
        assert result.success
        patient = result.data[0]
        assert 65 <= patient["age"] <= 75
    
    def test_generate_with_gender(self):
        """Generate patient with specific gender."""
        result = generate_patient(count=1, gender="female")
        
        assert result.success
        assert result.data[0]["gender"] == "female"
    
    def test_invalid_count_raises_error(self):
        """Negative count should raise ValueError."""
        with pytest.raises(ValueError, match="count must be positive"):
            generate_patient(count=-1)
```

### Integration Tests

Integration tests verify components work together.

```python
# tests/integration/test_generation.py

import pytest
from healthsim_agent import HealthSimAgent

@pytest.mark.integration
class TestPatientGeneration:
    """Integration tests for patient generation."""
    
    @pytest.fixture
    def agent(self):
        """Create agent instance."""
        return HealthSimAgent()
    
    async def test_generate_diabetic_patient(self, agent):
        """Generate a diabetic patient with labs."""
        response = await agent.chat(
            "Generate a 65-year-old diabetic patient with A1C lab"
        )
        
        # Check response contains expected elements
        assert "patient" in response.lower()
        assert "diabetes" in response.lower() or "e11" in response.lower()
        assert "a1c" in response.lower() or "4548-4" in response.lower()
    
    async def test_generate_and_export_fhir(self, agent):
        """Generate patient and export as FHIR."""
        # Generate
        await agent.chat("Generate a patient with hypertension")
        
        # Export
        response = await agent.chat("Export as FHIR")
        
        assert "bundle" in response.lower() or "fhir" in response.lower()
```

### Fixtures

Shared test fixtures go in `conftest.py`:

```python
# tests/conftest.py

import pytest
import duckdb
from pathlib import Path

@pytest.fixture(scope="session")
def test_db():
    """Create a test database."""
    db_path = Path("tests/test_data.duckdb")
    conn = duckdb.connect(str(db_path))
    
    # Create test schema
    conn.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            patient_id VARCHAR PRIMARY KEY,
            name VARCHAR,
            age INTEGER,
            gender VARCHAR
        )
    """)
    
    yield conn
    
    # Cleanup
    conn.close()
    db_path.unlink(missing_ok=True)


@pytest.fixture
def sample_patient():
    """Sample patient data."""
    return {
        "patient_id": "PAT-001",
        "name": {"family": "Smith", "given": ["John"]},
        "age": 45,
        "gender": "male",
        "conditions": [
            {"code": "E11.9", "display": "Type 2 diabetes"}
        ]
    }


@pytest.fixture
def sample_cohort(sample_patient):
    """Sample cohort with one patient."""
    return {
        "cohort_id": "test-cohort",
        "name": "Test Cohort",
        "patients": [sample_patient]
    }
```

### Parameterized Tests

Test multiple inputs with parameterization:

```python
@pytest.mark.parametrize("age_range,expected_min,expected_max", [
    ((18, 30), 18, 30),
    ((65, 75), 65, 75),
    ((0, 5), 0, 5),
])
def test_age_range_respected(age_range, expected_min, expected_max):
    """Patient age falls within specified range."""
    result = generate_patient(count=10, age_range=age_range)
    
    for patient in result.data:
        assert expected_min <= patient["age"] <= expected_max
```

### Mocking

Mock external dependencies:

```python
from unittest.mock import patch, MagicMock

def test_query_with_mock_db():
    """Test query tool with mocked database."""
    mock_conn = MagicMock()
    mock_conn.execute.return_value.fetchall.return_value = [
        {"patient_id": "P1", "name": "Test"}
    ]
    
    with patch("healthsim_agent.database.get_connection", return_value=mock_conn):
        result = query_tool("SELECT * FROM patients LIMIT 1")
        
        assert result.success
        assert len(result.data) == 1
        mock_conn.execute.assert_called_once()
```

## Test Markers

Use markers to categorize tests:

```python
@pytest.mark.unit
def test_unit_example():
    """Fast, isolated test."""
    pass

@pytest.mark.integration
def test_integration_example():
    """Requires full system."""
    pass

@pytest.mark.slow
def test_slow_example():
    """Long-running test."""
    pass

@pytest.mark.skip(reason="Not yet implemented")
def test_future_feature():
    pass

@pytest.mark.skipif(
    not os.environ.get("ANTHROPIC_API_KEY"),
    reason="Requires API key"
)
def test_requires_api():
    pass
```

## Test Failure Policy

**Critical**: When tests fail during development:

1. **STOP and diagnose** - Understand why before changing anything

2. **Never modify test assertions just to make them pass** - If a test expectation needs to change, explain why the original was wrong

3. **Red flags requiring discussion**:
   - Changing test assertions or expected values
   - Commenting out test code
   - Adding `@pytest.skip` to passing tests
   - "Simplifying" tests that test real functionality

Tests are a specification. Changing a test to pass is like changing requirements to match a bug.

## Coverage Goals

- Unit tests: 80%+ coverage
- Integration tests: Key workflows covered
- New features: Tests required for PR approval

### Check Coverage

```bash
# Generate report
pytest --cov=src/healthsim_agent --cov-report=html

# Check specific module
pytest --cov=src/healthsim_agent/tools --cov-report=term-missing tests/unit/test_tools.py
```

## Continuous Integration

Tests run automatically on PR:

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: "3.11"
      - run: pip install -e ".[dev]"
      - run: pytest --cov --cov-report=xml
```

## Debugging Tests

```bash
# Drop into debugger on failure
pytest --pdb

# Capture print statements
pytest -s

# Verbose tracebacks
pytest --tb=long

# Run with logging
pytest --log-cli-level=DEBUG
```

## Related Documentation

- [Development Setup](development-setup.md) - Environment setup
- [Code Style](code-style.md) - Coding conventions
- [Contributing](../../CONTRIBUTING.md) - Contribution guidelines
