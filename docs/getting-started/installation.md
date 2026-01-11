# Installation Guide

This guide covers all installation options for HealthSim Agent.

---

## System Requirements

| Component | Requirement |
|-----------|-------------|
| Operating System | macOS, Linux, or Windows |
| Python | 3.11 or higher |
| Memory | 4GB RAM minimum (8GB recommended) |
| Disk Space | ~500MB for application + reference data |

---

## Quick Install (Recommended)

For most users, pip installation is the fastest path:

```bash
pip install healthsim-agent
```

### Verify Installation

```bash
healthsim --version
```

Expected output:
```
HealthSim Agent v1.0.0
```

---

## Install from Source

For developers or users who want the latest features:

```bash
# Clone the repository
git clone https://github.com/mark64oswald/healthsim-agent.git
cd healthsim-agent

# Create a virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install with development dependencies
pip install -e ".[dev]"
```

---

## Virtual Environment Setup

We strongly recommend using a virtual environment to avoid conflicts with other Python packages.

### Using venv (Built-in)

```bash
# Create environment
python -m venv healthsim-env

# Activate
source healthsim-env/bin/activate  # macOS/Linux
# or
healthsim-env\Scripts\activate      # Windows

# Install
pip install healthsim-agent
```

### Using conda

```bash
# Create environment
conda create -n healthsim python=3.11

# Activate
conda activate healthsim

# Install
pip install healthsim-agent
```

---

## API Key Configuration

HealthSim requires an Anthropic API key to function.

### Get an API Key

1. Go to [console.anthropic.com](https://console.anthropic.com/)
2. Sign up or log in
3. Navigate to API Keys
4. Create a new key
5. Copy the key (it won't be shown again!)

### Set the API Key

**Option 1: Environment Variable (Recommended)**

```bash
# For current session
export ANTHROPIC_API_KEY="your-key-here"

# Permanent (add to your shell profile)
echo 'export ANTHROPIC_API_KEY="your-key-here"' >> ~/.zshrc  # macOS
echo 'export ANTHROPIC_API_KEY="your-key-here"' >> ~/.bashrc # Linux
```

**Option 2: Shell Profile**

Add to `~/.zshrc` (macOS) or `~/.bashrc` (Linux):

```bash
export ANTHROPIC_API_KEY="your-key-here"
```

Then reload:
```bash
source ~/.zshrc  # or ~/.bashrc
```

**Option 3: Per-Session**

Set it each time you open a terminal:
```bash
export ANTHROPIC_API_KEY="your-key-here"
healthsim
```

### Verify API Key

```bash
healthsim status
```

If your key is valid, you'll see status information. If not, you'll see an API key error.

---

## Database Configuration

HealthSim uses DuckDB for storing reference data and your generated scenarios.

### Default Location

The database is automatically created at:
- **macOS/Linux:** `~/.healthsim/healthsim.duckdb`
- **Windows:** `%USERPROFILE%\.healthsim\healthsim.duckdb`

### Custom Database Path

To use a different location:

```bash
export HEALTHSIM_DB_PATH="/path/to/your/healthsim.duckdb"
```

### Reference Data

The database includes embedded reference data:
- **CDC PLACES:** County and tract health indicators
- **SVI:** Social Vulnerability Index data
- **NPPES:** 8.9M US healthcare providers

This data is bundled with the installation—no additional downloads required.

---

## Verifying the Installation

Run these commands to ensure everything is working:

### 1. Check Version

```bash
healthsim --version
```

### 2. Check Status

```bash
healthsim status
```

Expected output:
```
HealthSim Agent Status
══════════════════════════════════════════
Database: ~/.healthsim/healthsim.duckdb
  Status: Connected ✓
  
Reference Data:
  NPPES Providers:    8,947,123
  CDC PLACES (County): 3,222
  CDC PLACES (Tract):  85,099
  SVI Tracts:          84,768

Saved Cohorts: 0
```

### 3. Test Generation

```bash
healthsim
```

Then in the interactive session:
```
healthsim › Generate a patient with diabetes

✓ Added 1 patient
```

If you see patient output, everything is working!

---

## Troubleshooting Installation

### Python Version Too Old

```
ERROR: healthsim-agent requires Python 3.11+
```

**Solution:** Install Python 3.11 or newer:
- macOS: `brew install python@3.11`
- Linux: Use your package manager or pyenv
- Windows: Download from python.org

### API Key Not Found

```
Error: ANTHROPIC_API_KEY environment variable not set
```

**Solution:** Set your API key (see [API Key Configuration](#api-key-configuration) above)

### Permission Denied on Database

```
Error: Unable to create database at ~/.healthsim/
```

**Solution:** Ensure you have write permissions:
```bash
mkdir -p ~/.healthsim
chmod 755 ~/.healthsim
```

### Package Conflicts

```
ERROR: Cannot install healthsim-agent due to conflicting dependencies
```

**Solution:** Use a virtual environment:
```bash
python -m venv healthsim-env
source healthsim-env/bin/activate
pip install healthsim-agent
```

### Import Errors

```
ModuleNotFoundError: No module named 'healthsim_agent'
```

**Solution:** Ensure you're in the right environment:
```bash
which python  # Should point to your venv
pip list | grep healthsim  # Should show healthsim-agent
```

---

## Upgrading

### From pip

```bash
pip install --upgrade healthsim-agent
```

### From Source

```bash
cd healthsim-agent
git pull
pip install -e ".[dev]"
```

---

## Uninstalling

```bash
pip uninstall healthsim-agent
```

To also remove your data:
```bash
rm -rf ~/.healthsim
```

---

## Next Steps

- **[Your First Session](first-session.md)** - Learn the basics
- **[Quick Reference](quick-reference.md)** - Command cheat sheet
- **[User Guides](../guides/)** - Deep dives into each domain
