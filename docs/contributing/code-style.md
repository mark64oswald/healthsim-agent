# Code Style Guide

HealthSim Agent follows consistent coding conventions for maintainability and readability.

## Python Style

### Formatters and Linters

We use:
- **Black** - Code formatting (line length: 88)
- **Ruff** - Fast linting
- **mypy** - Type checking

```bash
# Format code
black .

# Lint
ruff check .
ruff check --fix .  # Auto-fix

# Type check
mypy src/
```

### Basic Conventions

```python
# Good: snake_case for functions and variables
def generate_patient(patient_count: int) -> list[dict]:
    patient_data = []
    ...

# Good: PascalCase for classes
class PatientGenerator:
    def __init__(self, config: GeneratorConfig):
        self.config = config

# Good: UPPER_CASE for constants
DEFAULT_AGE_RANGE = (18, 85)
MAX_BATCH_SIZE = 100
```

### Imports

```python
# Standard library
import os
from pathlib import Path
from typing import Any, Optional

# Third-party
import duckdb
import pytest
from anthropic import Anthropic

# Local
from healthsim_agent.tools import generate, query
from healthsim_agent.database import get_connection
```

Ruff automatically sorts imports. Key rules:
- Standard library first
- Third-party second
- Local imports third
- Alphabetical within groups

### Type Hints

Use type hints for all public functions:

```python
from typing import Optional

def generate_patient(
    count: int = 1,
    age_range: Optional[tuple[int, int]] = None,
    gender: Optional[str] = None,
    include_diagnoses: bool = False,
) -> ToolResult:
    """Generate synthetic patient data.
    
    Args:
        count: Number of patients to generate (1-100).
        age_range: Optional (min, max) age tuple.
        gender: Optional 'male' or 'female'.
        include_diagnoses: Whether to include conditions.
        
    Returns:
        ToolResult with success status and patient data.
        
    Raises:
        ValueError: If count is out of range.
    """
    if count < 1 or count > 100:
        raise ValueError(f"count must be 1-100, got {count}")
    ...
```

### Docstrings

Use Google-style docstrings:

```python
def transform_to_fhir(
    cohort_id: str,
    resource_types: Optional[list[str]] = None,
) -> ToolResult:
    """Transform cohort to FHIR R4 Bundle.
    
    Converts internal HealthSim entities to standard FHIR R4
    resources wrapped in a Bundle.
    
    Args:
        cohort_id: ID or name of cohort to transform.
        resource_types: Optional list to filter resources.
            If None, includes all applicable resources.
    
    Returns:
        ToolResult containing:
            - success: True if transformation succeeded
            - data: FHIR Bundle as dict
            - error: Error message if failed
    
    Raises:
        CohortNotFoundError: If cohort doesn't exist.
        TransformationError: If data cannot be converted.
    
    Example:
        >>> result = transform_to_fhir("diabetes-cohort")
        >>> result.data["resourceType"]
        'Bundle'
    """
```

### Error Handling

```python
# Use specific exceptions
class CohortNotFoundError(HealthSimError):
    """Raised when cohort doesn't exist."""
    pass

class ValidationError(HealthSimError):
    """Raised when data fails validation."""
    pass

# Provide context in errors
def load_cohort(cohort_id: str) -> dict:
    cohort = db.get_cohort(cohort_id)
    if not cohort:
        raise CohortNotFoundError(
            f"Cohort '{cohort_id}' not found. "
            f"Use 'list_cohorts()' to see available cohorts."
        )
    return cohort
```

### Naming Conventions

| Item | Convention | Example |
|------|------------|---------|
| Functions | snake_case | `generate_patient()` |
| Classes | PascalCase | `PatientGenerator` |
| Constants | UPPER_SNAKE | `MAX_BATCH_SIZE` |
| Variables | snake_case | `patient_count` |
| Private | _leading_underscore | `_internal_method()` |
| Modules | snake_case | `patient_generator.py` |

### Function Length

- Aim for functions under 30 lines
- Extract helper functions for complex logic
- One function = one responsibility

```python
# Good: focused functions
def validate_patient(patient: dict) -> ValidationResult:
    """Validate a single patient."""
    errors = []
    errors.extend(_validate_demographics(patient))
    errors.extend(_validate_identifiers(patient))
    errors.extend(_validate_codes(patient))
    return ValidationResult(errors=errors)

def _validate_demographics(patient: dict) -> list[str]:
    """Validate demographic fields."""
    errors = []
    if not patient.get("name"):
        errors.append("Missing name")
    if not patient.get("gender"):
        errors.append("Missing gender")
    return errors
```

## Skill Style

### Frontmatter

Always include required YAML frontmatter:

```yaml
---
name: skill-name
description: Brief description. Triggers on "keyword1", "keyword2"
category: clinical|administrative|analytics
product: patientsim|membersim|rxmembersim|trialsim|populationsim|networksim
version: 1.0
related_skills:
  - related-skill-1
  - related-skill-2
---
```

### Skill Structure

Follow this order:

1. **Overview** - What the skill does
2. **Trigger Phrases** - When it activates
3. **Parameters** - Table of inputs
4. **Generation Patterns** - How data is created
5. **Examples** - At least 2 complete examples
6. **Validation Rules** - What makes data valid
7. **Related Skills** - Links to related skills

### Skill Example Quality

```markdown
### Example 1: Basic Diabetes Patient

**Request:**
```
Generate a 65-year-old diabetic patient
```

**Generated Data:**
```json
{
  "patient": {
    "id": "PAT-12345",
    "name": {"family": "Martinez", "given": ["Carlos"]},
    "birthDate": "1959-03-15",
    "gender": "male"
  },
  "conditions": [
    {
      "code": "E11.9",
      "display": "Type 2 diabetes mellitus without complications",
      "clinicalStatus": "active"
    }
  ]
}
```

**Notes:**
- Age calculated from birthDate
- ICD-10 code matches diagnosis
- clinicalStatus defaults to active
```

## Documentation Style

### Markdown Files

- Use ATX headers (`#`, `##`, `###`)
- One sentence per line (easier diffs)
- Code blocks with language hints
- Tables for structured data

```markdown
# Title

Brief introduction.

## Section

Explanatory text here.
Each sentence on its own line.

### Subsection

| Column 1 | Column 2 |
|----------|----------|
| Value 1  | Value 2  |

```python
# Code example
def example():
    pass
```
```

### Links

Use relative links for internal docs:

```markdown
See [Database Schema](../reference/database-schema.md)
See [PatientSim Guide](guides/patientsim-guide.md)
```

## Git Commit Style

### Conventional Commits

```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `test`: Tests
- `refactor`: Code refactoring
- `style`: Formatting
- `chore`: Maintenance
- `skill`: New or updated skill

Examples:

```bash
git commit -m "feat(tools): add batch export tool"
git commit -m "fix(query): handle empty NPPES results"
git commit -m "docs(guides): add RxMemberSim examples"
git commit -m "test(tools): add generate_claims tests"
git commit -m "skill(membersim): add value-based care skill"
```

### Branch Names

```
feature/description
fix/description
docs/description
skill/product-name
```

Examples:
- `feature/batch-export`
- `fix/query-timeout`
- `docs/trialsim-guide`
- `skill/membersim-vbc`

## Pre-commit Hooks

Install pre-commit hooks:

```bash
pip install pre-commit
pre-commit install
```

Configuration (`.pre-commit-config.yaml`):

```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 24.1.0
    hooks:
      - id: black

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.14
    hooks:
      - id: ruff
        args: [--fix]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
```

## Related Documentation

- [Development Setup](development-setup.md) - Environment setup
- [Testing Guide](testing-guide.md) - Writing tests
- [Skill Format](../skills/skill-format.md) - Skill authoring
