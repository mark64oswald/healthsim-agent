# Contributing to HealthSim Agent

Thank you for your interest in contributing to HealthSim Agent! This guide will help you get started.

## Ways to Contribute

- **Bug Reports**: Found something that doesn't work right? Open an issue.
- **Feature Requests**: Have an idea for improvement? We'd love to hear it.
- **Documentation**: Help improve our guides, examples, and reference docs.
- **Code**: Submit fixes, new features, or new skills.
- **Skills**: Add domain knowledge for better data generation.

## Quick Start

```bash
# 1. Fork and clone
git clone https://github.com/YOUR_USERNAME/healthsim-agent.git
cd healthsim-agent

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# 3. Install in development mode
pip install -e ".[dev]"

# 4. Run tests
pytest

# 5. Create a branch
git checkout -b feature/your-feature-name
```

## Development Documentation

| Document | Description |
|----------|-------------|
| [Development Setup](docs/contributing/development-setup.md) | Environment setup guide |
| [Testing Guide](docs/contributing/testing-guide.md) | How to write and run tests |
| [Code Style](docs/contributing/code-style.md) | Coding conventions |

## Contribution Types

### Bug Reports

Include:
- HealthSim version (`healthsim --version`)
- Python version
- Operating system
- Steps to reproduce
- Expected vs actual behavior
- Error messages/tracebacks

### Feature Requests

Include:
- Use case description
- Proposed solution
- Alternatives considered
- Would you like to implement it?

### Pull Requests

1. **Branch naming**:
   - Features: `feature/description`
   - Bugs: `fix/description`
   - Docs: `docs/description`
   - Skills: `skill/description`

2. **Commit messages**:
   - Use conventional format: `type(scope): description`
   - Types: `feat`, `fix`, `docs`, `test`, `refactor`, `skill`
   - Examples:
     - `feat(tools): add batch export tool`
     - `fix(query): handle empty results`
     - `docs(guides): update PatientSim examples`
     - `skill(membersim): add value-based care skill`

3. **Before submitting**:
   - [ ] Tests pass: `pytest`
   - [ ] Code formatted: `black .`
   - [ ] Linting clean: `ruff check .`
   - [ ] Documentation updated if needed
   - [ ] CHANGELOG.md updated

### Adding Skills

Skills are the heart of HealthSim. To contribute a skill:

1. Choose the appropriate product directory:
   ```
   skills/{patientsim,membersim,rxmembersim,trialsim,populationsim,networksim}/
   ```

2. Follow the [skill format](docs/skills/skill-format.md):
   - YAML frontmatter with name and description
   - Overview section
   - Parameters table
   - At least 2 examples
   - Validation rules
   - Related skills links

3. Add tests for the skill behavior

4. Update the [skill catalog](docs/skills/skill-catalog.md)

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn
- Keep discussions on topic

## Getting Help

- **Questions**: Open a Discussion on GitHub
- **Bugs**: Open an Issue
- **Chat**: TBD

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.

---

Thank you for contributing to HealthSim Agent! 🏥
