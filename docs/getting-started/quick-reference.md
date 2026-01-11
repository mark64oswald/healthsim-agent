# Quick Reference

A handy cheat sheet for HealthSim Agent commands and patterns.

---

## CLI Commands

Start HealthSim from your terminal:

| Command | Description |
|---------|-------------|
| `healthsim` | Start interactive session |
| `healthsim --debug` | Start with debug output |
| `healthsim status` | Show database and reference data status |
| `healthsim query "SQL"` | Execute SQL query |
| `healthsim cohorts` | List saved cohorts |
| `healthsim export NAME` | Export a saved cohort |

### Query Options

```bash
healthsim query "SELECT * FROM patients" --format json
healthsim query "SELECT COUNT(*) FROM claims" --format table
healthsim query "SELECT * FROM members" --limit 50 --format csv
```

### Export Options

```bash
healthsim export my-cohort                           # Summary
healthsim export my-cohort --format json -o data.json
healthsim export my-cohort --format fhir -o bundle.json
healthsim export my-cohort --format csv -o patients.csv
```

---

## Session Commands

Use these within an interactive session (with `/` prefix):

| Command | Description |
|---------|-------------|
| `/help` | Show available commands |
| `/status` | Display current session status |
| `/sql QUERY` | Execute SQL query |
| `/clear` | Clear the screen |
| `/quit` | Exit HealthSim |

---

## Generation Patterns

### PatientSim (Clinical Data)

```
Generate a patient with diabetes
Generate a 65-year-old male with heart failure and COPD
Create a pediatric patient with asthma
Generate a breast cancer patient with stage IIA disease
Create an elderly patient with multiple chronic conditions
```

### MemberSim (Claims Data)

```
Generate a professional claim for an office visit
Create a facility claim for a 3-day hospital stay
Generate a denied claim requiring prior authorization
Create a claim with DRG 470 (hip replacement)
Generate an 835 remittance for recent claims
```

### RxMemberSim (Pharmacy Data)

```
Generate a pharmacy claim for metformin
Create a specialty pharmacy claim for Humira
Generate a claim with drug interaction alert
Create pharmacy claims requiring prior authorization
Generate a 30-day supply with tier 2 copay
```

### TrialSim (Clinical Trials)

```
Generate a Phase 3 oncology trial with 100 subjects
Create a Phase 1 dose escalation study
Generate adverse events for the trial
Create SDTM demographics domain
Generate efficacy data with RECIST assessments
```

### PopulationSim (Demographics/SDOH)

```
Profile Harris County, Texas
Show health indicators for Los Angeles County
Analyze social vulnerability in rural Georgia
Compare diabetes prevalence across Texas counties
Create a cohort specification for a diabetes trial
```

### NetworkSim (Providers)

```
Find cardiologists in Houston
How many primary care physicians in San Diego County?
Search for oncologists within 25 miles of Phoenix
Generate a synthetic primary care physician
Look up NPI 1234567890
```

---

## State Management

### Saving

```
save as my-cohort
save as diabetes-patients
save as test-scenario-v2
```

### Loading

```
load my-cohort
load diabetes-patients
```

### Listing

```
What cohorts do I have?
List my saved scenarios
show saved cohorts
```

### Deleting

```
delete my-cohort
remove old-test-data
```

---

## Format Transformations

Add these to any generation request:

| Request | Output Format |
|---------|---------------|
| `as FHIR` or `as FHIR R4` | FHIR R4 Bundle |
| `as HL7` or `as HL7v2` | HL7v2 message (ADT, etc.) |
| `as C-CDA` | Clinical Document Architecture |
| `as MIMIC` or `as MIMIC-III` | MIMIC-III format |
| `as 837` or `as X12 837` | X12 837P/837I EDI |
| `as 835` | X12 835 remittance |
| `as NCPDP` | NCPDP telecommunications |
| `as SDTM` | CDISC SDTM datasets |
| `as CSV` | Comma-separated values |
| `as JSON` | Raw JSON format |

### Examples

```
Generate a diabetic patient as FHIR R4
Export the claims as X12 837P
Generate SDTM domains for this trial
Show the patient as HL7v2 ADT message
```

---

## Cross-Product Patterns

Generate linked data across domains:

```
# Patient + Claims
Generate a diabetic patient with their recent office visit claims

# Patient + Pharmacy
Create a patient with heart failure and pharmacy claims for their medications

# Full Journey
Generate a member with enrollment, a hospitalization for pneumonia, 
the facility claim, and follow-up pharmacy claims for antibiotics

# Clinical Trial Context
Generate a Phase 3 trial participant with baseline assessments, 
treatment visits, and adverse event reports
```

---

## SQL Queries

Use `/sql` in session or `healthsim query` from CLI:

### Basic Queries

```sql
-- List all patients
SELECT * FROM patients

-- Count claims by type
SELECT claim_type, COUNT(*) FROM claims GROUP BY claim_type

-- Find diabetic patients
SELECT * FROM patients WHERE diagnoses LIKE '%E11%'

-- Recent encounters
SELECT * FROM encounters ORDER BY service_date DESC LIMIT 10
```

### Reference Data Queries

```sql
-- Provider search
SELECT npi, provider_name, specialty 
FROM nppes_providers 
WHERE state = 'TX' AND specialty LIKE '%Cardiol%'
LIMIT 20

-- County health data
SELECT county_name, diabetes_prevalence, obesity_prevalence
FROM cdc_places_county
WHERE state = 'TX'
ORDER BY diabetes_prevalence DESC

-- Social vulnerability
SELECT tract_fips, svi_score, svi_theme1_socioeconomic
FROM svi_tract
WHERE state = 'CA' AND county = '037'  -- Los Angeles
ORDER BY svi_score DESC
LIMIT 10
```

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ANTHROPIC_API_KEY` | Required: Your Anthropic API key | - |
| `HEALTHSIM_DB_PATH` | Custom database path | `~/.healthsim/healthsim.duckdb` |
| `HEALTHSIM_DEBUG` | Enable debug mode | `false` |

---

## Output Locations

| Content | Location |
|---------|----------|
| Database | `~/.healthsim/healthsim.duckdb` |
| Exports | `./output/` (current directory) |
| Logs | `~/.healthsim/logs/` |

---

## Common Patterns by Use Case

### Testing an EMR

```
Generate 50 patients with diverse conditions as FHIR R4
Export to output/ehr-test-data.json
```

### Claims System Testing

```
Generate 100 professional claims with varying adjudication outcomes
Include some denied claims requiring appeal
Export as X12 837P
```

### PBM Testing

```
Generate 20 members with specialty drug claims
Include DUR alerts and prior authorizations
Export as NCPDP
```

### Clinical Trial System

```
Generate a Phase 3 trial with 200 subjects
Include demographics, adverse events, and efficacy
Export as CDISC SDTM
```

### Analytics Dashboard

```
Generate 500 patients in dimensional format
Create fact and dimension tables
Export for loading into analytics tool
```

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+C` | Cancel current operation |
| `Ctrl+D` | Exit HealthSim |
| `↑` / `↓` | Navigate command history |
| `Tab` | Auto-complete (where available) |

---

## Getting Help

```
/help              # In-session help
healthsim --help   # CLI help
```

- **Documentation:** [docs/](../)
- **Examples:** [examples/](../../examples/)
- **Issues:** [GitHub Issues](https://github.com/mark64oswald/healthsim-agent/issues)
