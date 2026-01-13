# Contributing Documentation

Guides for contributing to HealthSim Agent development.

## Documentation

| Document | Description |
|----------|-------------|
| [CONTRIBUTING.md](../../CONTRIBUTING.md) | Main contribution guide (project root) |
| [Development Setup](development-setup.md) | Environment and installation |
| [Testing Guide](testing-guide.md) | Writing and running tests |
| [Code Style](code-style.md) | Coding conventions and standards |

## Quick Start

```bash
# Clone and setup
git clone https://github.com/YOUR_USERNAME/healthsim-agent.git
cd healthsim-agent
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"

# Run tests
pytest

# Check style
black .
ruff check .
```

## Contribution Types

- **Bug Reports** - Open an issue with reproduction steps
- **Feature Requests** - Describe use case and proposed solution
- **Documentation** - Improve guides, examples, reference docs
- **Code** - Submit fixes, features, improvements
- **Skills** - Add healthcare domain knowledge

## Links

- [GitHub Repository](https://github.com/mark64oswald/healthsim-agent)
- [Issue Tracker](https://github.com/mark64oswald/healthsim-agent/issues)
- [Skill Catalog](../skills/skill-catalog.md)
