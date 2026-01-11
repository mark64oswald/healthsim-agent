# Troubleshooting Guide

Solutions to common issues when using HealthSim Agent.

---

## Installation Issues

### Python Version Too Old

**Symptom:**
```
ERROR: healthsim-agent requires Python 3.11+
```

**Solution:**

Install Python 3.11 or newer:

```bash
# macOS (with Homebrew)
brew install python@3.11

# Ubuntu/Debian
sudo apt update
sudo apt install python3.11

# Using pyenv (any platform)
pyenv install 3.11.0
pyenv global 3.11.0
```

Verify:
```bash
python3 --version  # Should show 3.11.x or higher
```

---

### Package Conflicts

**Symptom:**
```
ERROR: Cannot install healthsim-agent due to conflicting dependencies
```

**Solution:**

Use a virtual environment to isolate dependencies:

```bash
# Create a fresh environment
python -m venv healthsim-env
source healthsim-env/bin/activate

# Install in isolation
pip install healthsim-agent
```

If conflicts persist, try:
```bash
pip install --no-deps healthsim-agent
pip install -r requirements.txt  # Install deps separately
```

---

### Permission Denied

**Symptom:**
```
PermissionError: [Errno 13] Permission denied: '~/.healthsim/'
```

**Solution:**

Create the directory with proper permissions:

```bash
mkdir -p ~/.healthsim
chmod 755 ~/.healthsim
```

Or use a custom path:
```bash
export HEALTHSIM_DB_PATH="/path/you/own/healthsim.duckdb"
```

---

## API Key Issues

### API Key Not Found

**Symptom:**
```
Error: ANTHROPIC_API_KEY environment variable not set
```

**Solution:**

Set your API key:

```bash
# For current session
export ANTHROPIC_API_KEY="sk-ant-..."

# Permanently (add to shell profile)
echo 'export ANTHROPIC_API_KEY="sk-ant-..."' >> ~/.zshrc
source ~/.zshrc
```

Verify:
```bash
echo $ANTHROPIC_API_KEY  # Should show your key
```

---

### Invalid API Key

**Symptom:**
```
Error: Invalid API key
```

**Solution:**

1. Check key format (should start with `sk-ant-`)
2. Verify key at [console.anthropic.com](https://console.anthropic.com/)
3. Ensure no extra spaces or quotes
4. Try generating a new key

```bash
# Set without quotes around the key
export ANTHROPIC_API_KEY=sk-ant-api03-xxx...
```

---

### Rate Limiting

**Symptom:**
```
Error: Rate limit exceeded. Please retry after X seconds.
```

**Solution:**

1. Wait the indicated time and retry
2. Reduce request frequency
3. For high-volume testing, contact Anthropic about rate limits

---

## Database Issues

### Database Not Found

**Symptom:**
```
Error: Database not found at ~/.healthsim/healthsim.duckdb
```

**Solution:**

The database should be created automatically. If not:

```bash
# Check the path
ls -la ~/.healthsim/

# Try running status to initialize
healthsim status
```

If using a custom path:
```bash
export HEALTHSIM_DB_PATH="/your/custom/path.duckdb"
healthsim status  # Will create if doesn't exist
```

---

### Database Locked

**Symptom:**
```
Error: Database is locked
```

**Solution:**

Another process is using the database. Close other HealthSim sessions:

```bash
# Find and kill other healthsim processes
ps aux | grep healthsim
kill <PID>

# Or force close (not recommended)
rm ~/.healthsim/*.lock  # If lock files exist
```

---

### Corrupted Database

**Symptom:**
```
Error: Database appears to be corrupted
```

**Solution:**

Back up and recreate:

```bash
# Back up existing
mv ~/.healthsim/healthsim.duckdb ~/.healthsim/healthsim.duckdb.backup

# Recreate (reference data will be restored)
healthsim status
```

Your saved cohorts will be lost. To prevent this, export important cohorts regularly:
```bash
healthsim export my-cohort --format json -o backup.json
```

---

## Generation Issues

### Generation Hangs

**Symptom:** HealthSim doesn't respond after a request.

**Solution:**

1. Wait a moment—complex generations take time
2. Press `Ctrl+C` to cancel
3. Check your network connection
4. Try a simpler request first:
   ```
   Generate a patient
   ```

---

### Unexpected Output

**Symptom:** Generated data doesn't match your request.

**Solution:**

Be more specific in your request:

```
# Vague (may not produce expected results)
Generate a patient with problems

# Specific (better results)
Generate a 55-year-old female with Type 2 diabetes (E11.9), 
hypertension (I10), and obesity (E66.9), currently on metformin, 
lisinopril, and semaglutide
```

If the issue persists, try rephrasing or breaking into steps:
```
Step 1: Generate a 55-year-old female patient
Step 2: Add Type 2 diabetes with E11.9 code
Step 3: Add medications for her conditions
```

---

### Missing Medications or Labs

**Symptom:** Patient generated without expected medications or lab results.

**Solution:**

Explicitly request them:

```
Generate a diabetic patient with:
- Appropriate medications (metformin, etc.)
- Recent lab results including A1C and glucose
- All relevant diagnoses coded
```

---

### Invalid Codes

**Symptom:** ICD-10, CPT, or other codes appear invalid.

**Solution:**

1. Verify the code in official sources:
   - ICD-10: [cms.gov ICD-10](https://www.cms.gov/medicare/coding-billing/icd-10-codes)
   - CPT: [AMA CPT](https://www.ama-assn.org/practice-management/cpt)

2. Request valid codes explicitly:
   ```
   Generate a patient with valid ICD-10-CM codes for diabetes
   ```

3. Note that codes update annually—some may be outdated

---

## Format Issues

### FHIR Validation Errors

**Symptom:** Exported FHIR doesn't validate.

**Solution:**

1. Specify the profile:
   ```
   Generate as FHIR R4 conforming to US Core
   ```

2. Check resource completeness:
   ```
   Generate a complete FHIR Patient resource with all required fields
   ```

3. Validate at [validator.fhir.org](https://validator.fhir.org/)

---

### HL7v2 Parse Errors

**Symptom:** HL7v2 messages don't parse correctly.

**Solution:**

1. Check segment delimiters (should be `|` for fields, `~` for repeating)
2. Verify MSH segment is first
3. Request specific version:
   ```
   Generate as HL7v2.5.1 ADT^A01 message
   ```

---

### X12 Format Issues

**Symptom:** X12 837/835 doesn't meet EDI standards.

**Solution:**

1. Request specific version:
   ```
   Generate as X12 837P 5010 format
   ```

2. Check delimiters (usually `~` segment, `*` element, `:` sub-element)

---

## Performance Issues

### Slow Responses

**Symptom:** HealthSim takes a long time to respond.

**Solution:**

1. Start with smaller requests:
   ```
   # Instead of
   Generate 1000 patients with full histories
   
   # Try
   Generate 10 patients first
   ```

2. Use debug mode to see what's happening:
   ```bash
   healthsim --debug
   ```

3. Check network connectivity

---

### High Memory Usage

**Symptom:** HealthSim uses excessive memory.

**Solution:**

1. Generate in smaller batches
2. Save and clear session periodically:
   ```
   save as batch-1
   # Start fresh session
   ```
3. Use queries to work with subsets:
   ```
   /sql SELECT * FROM patients WHERE condition = 'diabetes' LIMIT 100
   ```

---

## Session Issues

### Lost Session Data

**Symptom:** Session data disappeared after closing.

**Solution:**

Session data is temporary until saved:

```
save as my-work
```

Always save before closing if you want to keep your data.

---

### Can't Load Cohort

**Symptom:**
```
Error: Cohort 'my-cohort' not found
```

**Solution:**

1. List available cohorts:
   ```
   What cohorts do I have?
   ```
   Or:
   ```bash
   healthsim cohorts
   ```

2. Check for typos in the name

3. Verify database path hasn't changed:
   ```bash
   echo $HEALTHSIM_DB_PATH
   ```

---

## Getting More Help

### Enable Debug Mode

For detailed logging:

```bash
healthsim --debug
```

Or set environment variable:
```bash
export HEALTHSIM_DEBUG=true
healthsim
```

### Check Logs

Logs are stored at:
- `~/.healthsim/logs/healthsim.log`

### Report an Issue

If you can't resolve the issue:

1. Check [existing issues](https://github.com/mark64oswald/healthsim-agent/issues)
2. Open a new issue with:
   - HealthSim version (`healthsim --version`)
   - Operating system
   - Python version
   - The command/request that failed
   - Full error message
   - Steps to reproduce

---

## FAQ

### Q: Why do I need an API key?

HealthSim uses Claude (by Anthropic) as its AI engine. The API key authenticates your requests to Claude's servers.

### Q: Is my data sent to the cloud?

Your generation requests are sent to Anthropic's API. The generated data is stored locally in your DuckDB database. Saved cohorts never leave your machine.

### Q: Can I use HealthSim offline?

No, HealthSim requires internet access to communicate with the Anthropic API.

### Q: How much does it cost?

HealthSim is free and open source. You pay only for Anthropic API usage based on your Claude plan.

### Q: Where is my data stored?

- Database: `~/.healthsim/healthsim.duckdb`
- Exports: `./output/` in your current directory
- Logs: `~/.healthsim/logs/`

### Q: How do I update HealthSim?

```bash
pip install --upgrade healthsim-agent
```

### Q: How do I completely uninstall?

```bash
pip uninstall healthsim-agent
rm -rf ~/.healthsim  # Remove all data
```
