# Cohort Analytics Example

Generate and analyze cohorts of patients with HealthSim.

---

## Goal

Create patient cohorts for analysis, quality metrics, and population health. You'll learn:

- Building cohorts with criteria
- Generating cohort members
- Computing cohort metrics
- Exporting analytical data

---

## Prerequisites

- Familiarity with [Patient Generation](../basic/patient-generation.md)
- Understanding of healthcare quality measures
- ~15 minutes

---

## Scenario: Diabetes Quality Program

Build a cohort of diabetic patients to analyze HbA1c control.

### Step 1: Define Cohort Criteria

```
healthsim › Create a diabetes quality cohort with these criteria:
            - Age 18-75
            - Type 2 diabetes diagnosis (E11.x)
            - At least one HbA1c in past 12 months
            - Actively enrolled in insurance
```

Expected output:
```
✓ Created cohort definition

Cohort: diabetes-quality-2026
  Description: Type 2 diabetes quality measurement cohort
  
Inclusion Criteria:
  1. Age 18-75 years
  2. Diagnosis: E11.* (Type 2 diabetes)
  3. Lab: HbA1c within 12 months
  4. Enrollment: Active as of measurement date
  
Exclusion Criteria:
  1. Hospice or terminal diagnosis
  2. ESRD (N18.6)
  
Measurement Period: 2025-01-01 to 2025-12-31
Target Size: Not specified
```

### Step 2: Generate Cohort Members

```
healthsim › Generate 50 patients matching this cohort with realistic 
            HbA1c distribution - 60% controlled (<8%), 25% borderline 
            (8-9%), 15% uncontrolled (>9%)
```

Expected output:
```
✓ Generating cohort members...

Progress: 50/50 patients created

Cohort: diabetes-quality-2026
  Total Members: 50
  
Demographics:
  Age Range: 23-74 (mean: 56)
  Female: 54% (27)
  Male: 46% (23)
  
Geographic Distribution:
  Urban: 72%
  Suburban: 22%
  Rural: 6%
  
HbA1c Distribution (as requested):
  Controlled (<8%): 30 patients (60%)
  Borderline (8-9%): 12 patients (24%)
  Uncontrolled (>9%): 8 patients (16%)
```

### Step 3: View Cohort Summary

```
healthsim › Show cohort statistics and quality metrics
```

Expected output:
```
Cohort Analysis: diabetes-quality-2026
═══════════════════════════════════════════════

Clinical Metrics:
  HbA1c Control Rate (<8%): 60.0%
    - Target: 70%
    - Gap: 10.0 percentage points
    
  Mean HbA1c: 7.8%
  Median HbA1c: 7.4%
  
  HbA1c Distribution:
    <7%:   12 (24%) ████████
    7-8%:  18 (36%) ████████████
    8-9%:  12 (24%) ████████
    >9%:    8 (16%) █████
    
Comorbidities:
  Hypertension: 38 (76%)
  Hyperlipidemia: 32 (64%)
  Obesity: 25 (50%)
  CKD Stage 1-3: 12 (24%)
  
Medication Patterns:
  On Metformin: 45 (90%)
  On SGLT2i: 18 (36%)
  On GLP-1: 12 (24%)
  On Insulin: 8 (16%)
  Diet Only: 2 (4%)
  
Care Gaps Identified:
  No statin (should have): 8 patients
  No ACE/ARB (with HTN): 5 patients
  No retinal exam (>12 mo): 15 patients
═══════════════════════════════════════════════
```

### Step 4: Generate Claims for Cohort

```
healthsim › Generate 12 months of claims for this cohort - quarterly 
            office visits, annual labs, and appropriate prescriptions
```

Expected output:
```
✓ Generating claims for cohort...

Progress: 50/50 members complete

Claims Generated:
  Professional Claims: 287
    - Office Visits: 198 (avg 4.0 per member)
    - Lab Orders: 89
    
  Total Billed: $142,500
  Total Allowed: $89,250
  
Service Distribution:
  99213/99214 (Office): 198 claims
  83036 (HbA1c): 156 claims
  80053 (CMP): 89 claims
  
Pharmacy Claims: 856
  - Metformin fills: 225
  - Statin fills: 198
  - SGLT2i fills: 89
  - GLP-1 fills: 67
  - Insulin fills: 45
```

### Step 5: Stratify by Risk

```
healthsim › Stratify the cohort by complication risk and show 
            the high-risk patients
```

Expected output:
```
Risk Stratification: diabetes-quality-2026
═══════════════════════════════════════════════

Risk Tiers:
  Low Risk: 15 patients (30%)
    • HbA1c <7%, no complications
    • Average cost/year: $2,400
    
  Moderate Risk: 22 patients (44%)
    • HbA1c 7-8% OR mild complications
    • Average cost/year: $5,800
    
  High Risk: 10 patients (20%)
    • HbA1c >8% AND complications
    • Average cost/year: $12,500
    
  Very High Risk: 3 patients (6%)
    • HbA1c >9% with multiple complications
    • Average cost/year: $28,000

High-Risk Patients Requiring Intervention:
┌──────────────┬─────┬───────┬─────────────────────┐
│ Patient      │ Age │ HbA1c │ Key Issues          │
├──────────────┼─────┼───────┼─────────────────────┤
│ PAT-012      │ 67  │ 9.8%  │ CKD3, neuropathy    │
│ PAT-023      │ 71  │ 9.2%  │ CHF, retinopathy    │
│ PAT-031      │ 58  │ 10.1% │ Non-adherent, COPD  │
│ PAT-034      │ 62  │ 9.5%  │ Recent MI, CKD2     │
│ PAT-047      │ 54  │ 9.9%  │ Morbid obesity      │
└──────────────┴─────┴───────┴─────────────────────┘

Recommended Interventions:
  • Care management enrollment: 13 patients
  • Endocrinology referral: 8 patients
  • Diabetes education: 15 patients
  • Medication optimization: 10 patients
```

### Step 6: Export Analytics Package

```
healthsim › Export cohort with star schema format for analytics
```

Expected output:
```
✓ Exported analytics package

Dimension Tables:
  → dim_patient.csv (50 rows)
  → dim_provider.csv (23 rows)
  → dim_facility.csv (12 rows)
  → dim_diagnosis.csv (89 rows)
  → dim_medication.csv (45 rows)
  → dim_date.csv (365 rows)

Fact Tables:
  → fact_encounter.csv (287 rows)
  → fact_claim.csv (287 rows)
  → fact_pharmacy.csv (856 rows)
  → fact_observation.csv (512 rows)

Quality Metrics:
  → cohort_summary.csv
  → quality_measures.csv
  → risk_stratification.csv

Package: ./exports/diabetes-quality-2026-analytics.zip
```

---

## What You Created

| Category | Count | Purpose |
|----------|-------|---------|
| Patients | 50 | Cohort members |
| Encounters | ~200 | Office visits |
| Claims | ~287 | Professional claims |
| Rx Claims | ~856 | Pharmacy claims |
| Metrics | Multiple | Quality measures |

---

## Key Concepts

### Cohort Definition

```
Cohort = {
  inclusion: [age, diagnosis, lab, enrollment],
  exclusion: [hospice, ESRD],
  measurement_period: [start, end]
}
```

### Quality Measures

HEDIS-like measures:
- HbA1c testing (did they get tested?)
- HbA1c control (is it <8%?)
- Eye exam (annual retinal)
- Nephropathy monitoring (annual uACR)

### Risk Stratification

Based on:
- Clinical values (HbA1c, eGFR)
- Comorbidity burden
- Complication history
- Utilization patterns

---

## Variations

### HEDIS Cohort

```
healthsim › Create a full HEDIS CDC (diabetes) cohort and generate 
            all required measures
```

### Heart Failure Cohort

```
healthsim › Create a heart failure quality cohort with ejection 
            fraction distribution and medication adherence metrics
```

### Care Gap Analysis

```
healthsim › Generate 100 patients and identify all care gaps 
            against clinical guidelines
```

### Cost Analysis

```
healthsim › Create a cohort for total cost of care analysis 
            with high-cost driver identification
```

---

## Troubleshooting

**Cohort too homogeneous?**
- Request specific distributions
- Add variation: "with varying socioeconomic backgrounds"

**Missing metrics?**
- Request specific measures: "Calculate HEDIS CDC measure"
- Check lab completeness

**Can't stratify?**
- Ensure cohort has necessary data elements
- Add clinical values: "Include eGFR and BP for all patients"

---

## Related

- [State Management Guide](../../docs/guides/state-management-guide.md)
- [PopulationSim Guide](../../docs/guides/populationsim-guide.md)
- [Star Schema Analytics](../advanced/star-schema-analytics.md)
