# Batch Generation

Generate large datasets efficiently using auto-persist and batch workflows.

---

## Goal

Learn how to generate 50+ entities efficiently, manage large cohorts, and export data for analysis.

## Prerequisites

- HealthSim Agent installed and configured
- Familiarity with basic generation

---

## Overview

When generating large datasets, HealthSim uses **auto-persist** to save data to DuckDB and return compact summaries instead of flooding the conversation with JSON.

| Approach | Use Case | What You See |
|----------|----------|--------------|
| Traditional | Small scenarios (<50 entities) | Full data in conversation |
| Auto-Persist | Large batches (50+ entities) | Summary + query on demand |

---

## Example 1: Generate Large Member Cohort

### Step 1: Generate Cohort

```
healthsim › Generate 100 Medicare Advantage members over 65 in California
```

Expected output:
```
✓ Generated and saved "medicare-ca-20250113":

| Metric | Value |
|--------|-------|
| Members | 100 |
| Age Range | 65-89 |
| Gender | 48 male, 52 female |
| Plan Types | HMO (40), PPO (35), PFFS (25) |

Top counties: Los Angeles (28), San Diego (18), Orange (15)

Would you like to:
- Query specific subsets
- See sample members
- Generate claims for these members
```

### Step 2: Query Saved Data

```
healthsim › From my Medicare scenario, show female members over 75 with diabetes
```

Expected output:
```
Found 12 matching members:

| Name | Age | City | Plan | Risk Score |
|------|-----|------|------|------------|
| Margaret Wilson | 78 | San Diego | HMO | 1.85 |
| Dorothy Chen | 82 | Los Angeles | PPO | 2.12 |
| Patricia Johnson | 76 | San Francisco | HMO | 1.45 |

Showing 3 of 12. Say "show more" for the rest.
```

---

## Example 2: Clinical Trial Batch

### Generate Trial with Subjects

```
healthsim › Generate a Phase 3 oncology trial with 200 subjects
```

Expected output:
```
✓ Generated and saved "oncology-phase3-20250113":

**Study**: ONCO-2025-001 (Phase 3 NSCLC)

| Attribute | Value |
|-----------|-------|
| Sites | 8 |
| Subjects | 200 |
| Treatment Arms | Active (100), Control (100) |

**Data Generated**:
| Entity | Count |
|--------|-------|
| Subjects | 200 |
| Visits | 1,847 |
| Adverse Events | 89 |
| Lab Results | 3,200 |

Would you like to:
- Query subjects by arm or site
- View adverse event details
- Export to CDISC SDTM format
```

---

## Example 3: Resume and Extend

### Load Previous Session

```
healthsim › Load my diabetes cohort from yesterday
```

Expected output:
```
✓ Loaded "diabetes-cohort-20250112":

| Entity Type | Count |
|-------------|-------|
| Patients | 150 |
| Encounters | 425 |
| Lab Results | 890 |
| Medications | 320 |

**Clinical Characteristics**:
- Average A1C: 7.8% (range: 6.1-12.4%)
- With complications: 67 (45%)
- On insulin: 43 (29%)
```

### Add More Data

```
healthsim › Add 50 more patients with Type 1 diabetes to this cohort
```

---

## Example 4: Export for Analysis

```
healthsim › Export my training dataset to CSV for Python analysis
```

Expected output:
```
✓ Exported "combined-training-20250113" to CSV:

| File | Rows | Size |
|------|------|------|
| patients.csv | 345 | 312 KB |
| encounters.csv | 1,015 | 548 KB |
| lab_results.csv | 2,060 | 1.2 MB |
| diagnoses.csv | 892 | 124 KB |

**Location**: ~/healthsim-exports/combined-training-20250113/

Load in Python:
```python
import pandas as pd
patients = pd.read_csv('patients.csv')
print(f"Loaded {len(patients)} patients")
```
```

---

## Example 5: Merge Cohorts

```
healthsim › Merge my diabetes, heart-failure, and copd scenarios into a combined training set
```

Expected output:
```
✓ Created "combined-training-20250113" from 3 sources:

| Source | Patients | Encounters | Labs |
|--------|----------|------------|------|
| diabetes-cohort | 150 | 425 | 890 |
| heart-failure-cohort | 120 | 380 | 720 |
| copd-training | 75 | 210 | 450 |
| **Total** | **345** | **1,015** | **2,060** |

All source scenarios preserved.
```

---

## Performance Tips

### Optimal Batch Sizes

| Entity Type | Recommended Batch | Max Batch |
|-------------|-------------------|----------|
| Patients | 100-500 | 1,000 |
| Claims | 500-2,000 | 5,000 |
| Lab Results | 1,000-5,000 | 10,000 |
| Trial Subjects | 100-500 | 1,000 |

### Generation Time Estimates

| Scenario | Entities | Approx Time |
|----------|----------|-------------|
| 100 patients with encounters | ~500 | 30-60 sec |
| 500 members with claims | ~2,000 | 2-3 min |
| Clinical trial (200 subjects) | ~5,000 | 3-5 min |

---

## Variations

```
Generate 500 members with chronic conditions distributed by prevalence
Generate a year of claims history for existing patients
Generate 1000 pharmacy claims with realistic refill patterns
Clone my production cohort and randomize identifiers
```

---

## Related

- [Cohort Analytics](../intermediate/cohort-analytics.md) - Analyze generated cohorts
- [Star Schema Analytics](star-schema-analytics.md) - Dimensional analysis
- [Integration Testing](integration-testing.md) - CI/CD with batch data

---

*Batch Generation v1.0 | HealthSim Agent*
