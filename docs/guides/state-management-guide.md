# State Management Guide

Save, load, and manage your synthetic healthcare data across sessions.

---

## Overview

State management in HealthSim lets you:

- **Save work** - Persist generated data as named cohorts
- **Resume later** - Load cohorts in future sessions
- **Query data** - Find specific entities without loading everything
- **Organize** - Tag, clone, merge, and export cohorts
- **Scale** - Generate thousands of entities without context overflow

---

## Quick Start

Save your current work:

```
healthsim › Save this as "diabetes-demo"
```

Output:
```
✓ Saved cohort "diabetes-demo"

  Entities:
    • 15 patients
    • 42 encounters
    • 156 lab results
    • 38 medications
    • 23 claims

  Total: 274 entities
  Size: 1.2 MB

Load anytime with: load diabetes-demo
```

---

## Core Concepts

### Sessions

A **session** is your current working context:

- Created when you start HealthSim
- Tracks all generated entities
- Maintains conversation history
- Lost when you exit (unless saved)

### Cohorts

A **cohort** is a saved snapshot:

- Named collection of entities
- Persisted to disk (DuckDB)
- Can be loaded in future sessions
- Supports tagging and organization

### Entities

Individual data items within a cohort:

- Patients, members, subjects
- Encounters, claims, visits
- Labs, medications, procedures
- Any generated healthcare data

---

## Saving Data

### Basic Save

Save everything in your current session:

```
Save this as "my-cohort"
Save my work as "training-data"
Persist these patients as "demo-2025"
```

### Save with Description

Add context for future reference:

```
Save as "heart-failure-cohort" with description 
"HFrEF patients for Q1 training, EF 15-40%, all on GDMT"
```

### Save with Tags

Organize with tags:

```
Save as "diabetes-cohort" tagged with "training", "validated", "2025"
```

### Selective Save

Save specific entity types:

```
Save only the patients as "patients-only"
Save patients and encounters as "clinical-data"
```

---

## Loading Data

### Load Full Cohort (Small)

For cohorts under 50 entities, load everything:

```
Load my diabetes cohort
Open the demo-2025 cohort
```

Output shows all entities:
```
✓ Loaded "diabetes-demo" with 15 patients

1. Maria Santos (58F) - Type 2 DM, A1C 7.8%
   • 4 encounters, latest: 2025-01-10
   • Medications: Metformin, Lisinopril, Atorvastatin

2. James Wilson (67M) - Type 2 DM with CKD Stage 3
   • 3 encounters, latest: 2024-12-28
   • Medications: Metformin, Jardiance, Lisinopril
   
[... all 15 patients ...]

What would you like to do with this cohort?
```

### Load Summary (Large)

For large cohorts, get a summary first:

```
Load my medicare-cohort
```

Output:
```
✓ Loaded summary for "medicare-cohort"

| Entity Type | Count |
|-------------|-------|
| Members | 500 |
| Claims | 12,450 |
| Pharmacy Claims | 8,320 |

Demographics:
  • Age range: 65-89 years
  • Gender: 245 male, 255 female
  • States: CA (120), TX (95), FL (82), ...

Too large to show all (20,770 entities).
Query for specific data or show samples.
```

### Resume Work

Continue where you left off:

```
Resume my diabetes cohort from yesterday
Continue working on medicare-cohort
```

---

## Querying Saved Data

### Basic Queries

Find specific entities without loading everything:

```
Show me patients over 70 in my cohort
Find members from California
Show claims over $1000
```

### SQL Queries

Use SQL for complex queries:

```
Query: SELECT * FROM patients WHERE age > 70 AND gender = 'F'
```

```sql
Query my cohort:
SELECT p.name, p.age, COUNT(e.id) as visit_count
FROM patients p
LEFT JOIN encounters e ON p.id = e.patient_id
GROUP BY p.id
HAVING visit_count > 5
```

### Sample Data

Get representative samples:

```
Show me 5 sample patients
Show 3 random claims
Give me sample encounters from this cohort
```

---

## Cohort Organization

### List Cohorts

See all saved cohorts:

```
List my cohorts
What cohorts do I have?
Show all saved data
```

Output:
```
You have 6 saved cohorts:

| Name | Entities | Updated | Tags |
|------|----------|---------|------|
| diabetes-demo | 274 | today | training |
| medicare-cohort | 20,770 | yesterday | validated |
| heart-failure-pilot | 89 | 3 days ago | demo |
| oncology-trial-2025 | 4,520 | 1 week ago | trialsim |
| test-data | 12 | 2 weeks ago | - |
| claims-sample | 1,450 | 1 month ago | demo |
```

### Tag Management

Add tags:
```
Tag medicare-cohort as "production"
Add tag "reviewed" to diabetes-demo
```

Remove tags:
```
Remove tag "test" from medicare-cohort
```

Find by tag:
```
Show cohorts tagged "validated"
List all demo cohorts
```

### Delete Cohorts

Remove unwanted cohorts:

```
Delete test-data
Remove the old claims-sample cohort
```

Always confirms before deletion:
```
Delete "test-data"? Contains 12 entities. Cannot be undone.
Type 'yes' to confirm.
```

---

## Advanced Operations

### Clone Cohorts

Create a copy for experimentation:

```
Clone diabetes-demo as diabetes-experiment
Make a copy of medicare-cohort
```

Output:
```
✓ Cloned "diabetes-demo" → "diabetes-demo-copy"

  • 15 patients copied
  • 42 encounters copied
  • All entities have new IDs
  
The clone is independent—changes won't affect original.
Would you like to rename it?
```

### Merge Cohorts

Combine multiple cohorts:

```
Merge diabetes-demo and heart-failure-pilot into chronic-disease-cohort
Combine all demo cohorts into training-master
```

Output:
```
✓ Created "chronic-disease-cohort" from 2 sources

| Source | Patients | Encounters |
|--------|----------|------------|
| diabetes-demo | 15 | 42 |
| heart-failure-pilot | 25 | 47 |
| **Total** | **40** | **89** |

Conflicts resolved: 0 (no duplicate IDs)
Source cohorts preserved unchanged.
```

### Export Cohorts

Export for external use:

**CSV:**
```
Export diabetes-demo to CSV
```

```
✓ Exported to ~/Downloads/diabetes-demo/

| File | Rows | Size |
|------|------|------|
| patients.csv | 15 | 45 KB |
| encounters.csv | 42 | 128 KB |
| lab_results.csv | 156 | 312 KB |
| medications.csv | 38 | 28 KB |
| claims.csv | 23 | 52 KB |

Total: 565 KB
```

**JSON:**
```
Export medicare-cohort as JSON
```

**Parquet:**
```
Export for analytics as Parquet files
```

**FHIR Bundle:**
```
Export diabetes-demo as FHIR Bundle
```

---

## Auto-Persist for Large Batches

### How It Works

When generating 50+ entities, HealthSim automatically:

1. Generates the data
2. Saves immediately (auto-persist)
3. Returns a summary (not full data)
4. Offers query options

### Example

```
Generate 200 Medicare members over 65
```

Output:
```
✓ Generated and saved "medicare-members-20250112"

| Metric | Value |
|--------|-------|
| Members | 200 |
| Age Range | 65-89 |
| Gender | 96 male, 104 female |
| Top States | CA (42), TX (38), FL (31) |

Data persisted. Query for specific subsets:
• "Show members from California"
• "Find members with diabetes"
• "Show 3 sample members"
```

### Why Auto-Persist?

| Without Auto-Persist | With Auto-Persist |
|---------------------|-------------------|
| 200 entities in context | Summary only (~500 tokens) |
| ~40,000 tokens consumed | Context preserved |
| Slower responses | Fast responses |
| Risk of overflow | Scalable to thousands |

### Controlling Auto-Persist

Request full data (if really needed):

```
Generate 200 members and show me all of them
```

Set threshold:

```
Set auto-persist threshold to 100 entities
```

---

## Token-Efficient Summaries

### Get Summary

View cohort contents without loading:

```
What's in my diabetes cohort?
Summarize medicare-cohort
Get stats for heart-failure-pilot
```

Output:
```
"diabetes-demo" summary:

| Entity Type | Count |
|-------------|-------|
| Patients | 15 |
| Encounters | 42 |
| Lab Results | 156 |
| Medications | 38 |
| Claims | 23 |

Demographics:
  • Age range: 45-72 years
  • Gender: 8 male, 7 female
  • Avg conditions per patient: 3.2

Clinical:
  • Primary: Type 2 Diabetes (15)
  • Common comorbidities: HTN (12), HLD (10), Obesity (8)
  • Average A1C: 7.6%

Token cost: ~400 tokens
Full load would be: ~12,000 tokens
```

### Summary vs Full Load

| Cohort Size | Summary Tokens | Full Load Tokens | Recommendation |
|-------------|----------------|------------------|----------------|
| 10 entities | ~200 | ~2,000 | Full load OK |
| 50 entities | ~400 | ~10,000 | Consider summary |
| 200 entities | ~600 | ~40,000 | Use summary |
| 1000 entities | ~800 | ~200,000 | Summary only |

---

## Workflow Patterns

### Demo Preparation

1. Generate demo data
2. Review and refine
3. Save with descriptive name
4. Tag as "demo" and "validated"
5. Clone for each presentation

```
Generate 20 diverse patients for demo
[review and adjust]
Save as "quarterly-demo-2025Q1" tagged "demo", "validated"
Clone for sales team as "sales-demo-q1"
Clone for training as "training-demo-q1"
```

### Research Cohort Building

1. Query population data (PopulationSim)
2. Design cohort criteria
3. Generate patients in batches
4. Add clinical data progressively
5. Export for analysis

```
Step 1: Analyze high-diabetes areas in California
Step 2: Generate 500 diabetic patients matching demographics
Step 3: Add 12 months of encounters for each
Step 4: Add corresponding claims
Step 5: Export as Parquet for statistical analysis
```

### Training Data Pipeline

1. Define requirements
2. Generate labeled data
3. Validate with SMEs
4. Tag as "validated"
5. Export for ML training

```
Generate 1000 heart failure patients with:
- Balanced outcomes (500 readmitted, 500 not)
- All clinical features populated
- 6 months history each

[SME review]
Tag as "validated", "ml-training"
Export as CSV with outcome labels
```

---

## Related Resources

### Skills

- [State Management Skill](../../skills/common/state-management.md) - Detailed skill reference
- [DuckDB Skill](../../skills/common/duckdb-skill.md) - SQL query patterns

### Product Guides

- [PatientSim Guide](patientsim-guide.md) - Patient generation
- [MemberSim Guide](membersim-guide.md) - Claims generation
- [Cross-Product Guide](cross-product-guide.md) - Multi-domain workflows

### Reference

- [Database Schema](../reference/database-schema.md) - Entity storage structure
- [CLI Reference](../reference/cli-reference.md) - Command line options

---

## Troubleshooting

### Cohort won't load

Check if it exists:
```
List my cohorts
```

Verify the name:
```
Load "diabetes-demo"  # with quotes if special characters
```

### Can't find saved data

Data persists in the DuckDB database. Check:
```
Show database status
List all cohorts including archived
```

### Out of memory during load

Use summary instead of full load:
```
Summarize my large cohort
Query for just what I need
```

### Lost work after crash

If session wasn't saved, data may be lost. Always:
```
Save frequently during long sessions
Use auto-persist for large batches
```

### Merge conflicts

If cohorts have duplicate IDs:
```
Merge with conflict strategy: rename
```

Options:
- `skip` - Keep first, ignore duplicates
- `rename` - Keep both with modified IDs
- `overwrite` - Keep latest version

### Export fails

Check disk space:
```
Export to ~/Downloads (ensure space available)
```

Try different format:
```
Export as JSON instead of Parquet
```

See [Troubleshooting](../getting-started/troubleshooting.md) for more solutions.
