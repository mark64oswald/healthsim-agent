# Integration Testing

Integrate HealthSim into CI/CD pipelines for automated test data generation.

---

## Goal

Learn how to use HealthSim Agent in automated testing workflows, generate consistent test fixtures, and validate data against schemas.

## Prerequisites

- HealthSim Agent installed
- Familiarity with CI/CD concepts
- Python or shell scripting knowledge

---

## Architecture Overview

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   CI Pipeline   │────▶│  HealthSim Agent │────▶│   Test Suite    │
│  (GitHub/GitLab)│     │  (Data Generator)│     │  (pytest/jest)  │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                               │
                               ▼
                        ┌──────────────────┐
                        │   DuckDB/Export  │
                        │  (Test Fixtures) │
                        └──────────────────┘
```

---

## Example 1: Generate Test Fixtures

### Create Fixture Script

```python
#!/usr/bin/env python3
"""generate_fixtures.py - Create test data for CI pipeline"""

import subprocess
import json
from pathlib import Path

FIXTURES_DIR = Path("tests/fixtures")

def run_healthsim(prompt: str) -> dict:
    """Execute HealthSim command and return JSON output."""
    result = subprocess.run(
        ["healthsim", "--json", "--prompt", prompt],
        capture_output=True,
        text=True
    )
    return json.loads(result.stdout)

def generate_patient_fixtures():
    """Generate standard patient test fixtures."""
    
    # Basic patient
    patient = run_healthsim(
        "Generate a 45-year-old male with Type 2 diabetes and hypertension"
    )
    save_fixture("basic_patient.json", patient)
    
    # Patient with encounters
    patient_journey = run_healthsim(
        "Generate a patient with 3 office visits over 6 months"
    )
    save_fixture("patient_journey.json", patient_journey)
    
    # Edge case: elderly with multiple comorbidities
    complex_patient = run_healthsim(
        "Generate an 85-year-old with CHF, CKD Stage 4, and diabetes"
    )
    save_fixture("complex_patient.json", complex_patient)

def generate_claims_fixtures():
    """Generate claims test fixtures."""
    
    # Paid claim
    paid_claim = run_healthsim(
        "Generate a paid professional claim for office visit"
    )
    save_fixture("paid_claim.json", paid_claim)
    
    # Denied claim
    denied_claim = run_healthsim(
        "Generate a denied claim for prior auth required"
    )
    save_fixture("denied_claim.json", denied_claim)

def save_fixture(filename: str, data: dict):
    """Save fixture to file."""
    filepath = FIXTURES_DIR / filename
    filepath.parent.mkdir(parents=True, exist_ok=True)
    filepath.write_text(json.dumps(data, indent=2))
    print(f"✓ Saved {filepath}")

if __name__ == "__main__":
    generate_patient_fixtures()
    generate_claims_fixtures()
    print("\n✓ All fixtures generated")
```

### Run in CI

```yaml
# .github/workflows/test.yml
name: Test Suite

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Install HealthSim
        run: pip install healthsim-agent
        
      - name: Generate Test Fixtures
        run: python scripts/generate_fixtures.py
        
      - name: Run Tests
        run: pytest tests/ -v
```

---

## Example 2: Schema Validation

### Validate Generated Data

```python
# tests/test_schema_validation.py
import pytest
import json
from jsonschema import validate, ValidationError

PATIENT_SCHEMA = {
    "type": "object",
    "required": ["mrn", "name", "birth_date", "gender"],
    "properties": {
        "mrn": {"type": "string", "pattern": "^PAT-\\d{3}$"},
        "name": {
            "type": "object",
            "required": ["given_name", "family_name"],
            "properties": {
                "given_name": {"type": "string"},
                "family_name": {"type": "string"}
            }
        },
        "birth_date": {"type": "string", "format": "date"},
        "gender": {"type": "string", "enum": ["M", "F", "O", "U"]}
    }
}

CLAIM_SCHEMA = {
    "type": "object",
    "required": ["claim_id", "claim_type", "service_date"],
    "properties": {
        "claim_id": {"type": "string"},
        "claim_type": {"enum": ["PROFESSIONAL", "INSTITUTIONAL"]},
        "service_date": {"type": "string", "format": "date"},
        "adjudication": {
            "type": "object",
            "required": ["status"],
            "properties": {
                "status": {"enum": ["paid", "denied", "pending"]}
            }
        }
    }
}

class TestPatientSchema:
    def test_basic_patient_valid(self):
        with open("tests/fixtures/basic_patient.json") as f:
            patient = json.load(f)
        validate(patient["patient"], PATIENT_SCHEMA)
    
    def test_complex_patient_valid(self):
        with open("tests/fixtures/complex_patient.json") as f:
            patient = json.load(f)
        validate(patient["patient"], PATIENT_SCHEMA)

class TestClaimSchema:
    def test_paid_claim_valid(self):
        with open("tests/fixtures/paid_claim.json") as f:
            claim = json.load(f)
        validate(claim["claim"], CLAIM_SCHEMA)
        assert claim["adjudication"]["status"] == "paid"
    
    def test_denied_claim_valid(self):
        with open("tests/fixtures/denied_claim.json") as f:
            claim = json.load(f)
        validate(claim["claim"], CLAIM_SCHEMA)
        assert claim["adjudication"]["status"] == "denied"
```

---

## Example 3: Load Testing Data

### Generate Volume Test Data

```python
# scripts/generate_load_test_data.py
"""Generate large datasets for load testing."""

import subprocess

def generate_load_test_cohort(size: int = 1000):
    """Generate a large cohort for load testing."""
    
    # Use batch generation
    subprocess.run([
        "healthsim",
        "--prompt", f"Generate {size} members with claims history",
        "--output", "load_test_data",
        "--format", "parquet"
    ])
    
    print(f"✓ Generated {size} members for load testing")

if __name__ == "__main__":
    generate_load_test_cohort(1000)
```

---

## Example 4: Deterministic Generation

### Reproducible Test Data

```python
# Use seeds for reproducible generation
result = run_healthsim(
    "Generate a diabetic patient",
    seed=12345  # Same seed = same output
)

# Verify consistency
assert result["patient"]["mrn"] == "PAT-001"
assert result["patient"]["name"]["given_name"] == "Robert"
```

---

## CI/CD Pipeline Template

```yaml
# Complete CI/CD workflow
name: HealthSim Integration Tests

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 6 * * *'  # Daily at 6 AM

jobs:
  generate-and-test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install healthsim-agent pytest jsonschema
      
      - name: Generate fixtures
        run: python scripts/generate_fixtures.py
      
      - name: Validate schemas
        run: pytest tests/test_schema_validation.py -v
      
      - name: Run integration tests
        run: pytest tests/integration/ -v
      
      - name: Upload test artifacts
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: test-fixtures
          path: tests/fixtures/
```

---

## Related

- [Batch Generation](batch-generation.md) - Generate large datasets
- [Format Transformations](../intermediate/format-transformations.md) - Export formats
- [Contributing Guide](../../docs/contributing/README.md) - Development setup

---

*Integration Testing v1.0 | HealthSim Agent*
