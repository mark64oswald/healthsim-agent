# Contributing to HealthSim Agent

Thank you for your interest in contributing to HealthSim Agent!

---

## Ways to Contribute

- **Report Bugs** - Open an issue describing the problem
- **Suggest Features** - Open an issue with your idea
- **Improve Documentation** - Submit PRs for docs
- **Write Code** - Fix bugs or add features

---

## Getting Started

### Development Setup

```bash
# Clone the repository
git clone https://github.com/mark64oswald/healthsim-agent.git
cd healthsim-agent

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install with dev dependencies
pip install -e ".[dev]"

# Run tests to verify setup
pytest
```

### Running Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=healthsim_agent

# Specific test file
pytest tests/unit/test_tools.py -v

# Watch mode (requires pytest-watch)
ptw
```

---

## Documentation Structure

| Section | Status | Notes |
|---------|--------|-------|
| [Development Setup](development-setup.md) | 📝 Coming | Dev environment setup |
| [Testing Guide](testing-guide.md) | 📝 Coming | Writing and running tests |
| [Code Style](code-style.md) | 📝 Coming | Style guidelines |
| [Release Process](release-process.md) | 📝 Coming | How releases work |

---

## Code Style

- Python code follows PEP 8
- Use `ruff` for linting
- Use `black` for formatting
- Type hints encouraged

```bash
# Format code
ruff format .

# Check linting
ruff check .

# Type checking
mypy src/healthsim_agent
```

---

## Pull Request Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Make your changes
4. Run tests (`pytest`)
5. Commit with clear message
6. Push to your fork
7. Open a Pull Request

### Commit Messages

Use clear, descriptive commit messages:

```
[Component] Brief description

- Detail 1
- Detail 2

Fixes #123
```

Examples:
```
[Tools] Add export to Parquet format

- Implement parquet writer using pyarrow
- Add tests for new format
- Update documentation

[Docs] Improve installation guide

- Add Windows-specific instructions
- Clarify Python version requirements
```

---

## Questions?

- Open an issue for questions
- Check existing issues first
- Be patient and respectful

---

*Thank you for contributing!*
