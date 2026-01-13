# Patient Generation Example

Learn the fundamentals of generating patients with HealthSim.

---

## Goal

Create realistic patient records with demographics, conditions, and encounters. You'll learn:

- Basic patient generation syntax
- Adding conditions and diagnoses
- Creating encounters
- Viewing and exporting data

---

## Prerequisites

- HealthSim installed and running
- API key configured
- ~5 minutes

---

## Steps

### Step 1: Start HealthSim

```bash
healthsim
```

You'll see:
```
HealthSim Agent v0.1.0

175 skills loaded
Database: reference data ready

healthsim ›
```

### Step 2: Generate Your First Patient

```
healthsim › Create a 45-year-old female patient in Seattle with type 2 diabetes
```

Expected output:
```
✓ Generated patient

Patient: PAT-001
  Name: Maria Chen
  Age: 45 years
  Sex: Female
  Location: Seattle, WA 98101
  
Conditions:
  • Type 2 diabetes mellitus (E11.9) - Active since 2019
```

### Step 3: Add a Comorbid Condition

```
healthsim › Add hypertension to this patient
```

Expected output:
```
✓ Added condition to PAT-001

Conditions (2):
  • Type 2 diabetes mellitus (E11.9) - Active since 2019
  • Essential hypertension (I10) - Active since 2021
```

### Step 4: Create an Encounter

```
healthsim › Add an office visit for diabetes management
```

Expected output:
```
✓ Added encounter

Encounter: ENC-001
  Type: Office Visit (99214)
  Date: 2026-01-10
  Provider: Dr. Sarah Johnson, MD (Internal Medicine)
  Reason: Diabetes management
  
Diagnoses:
  • E11.9 - Type 2 diabetes mellitus
  • I10 - Essential hypertension
```

### Step 5: Add a Lab Order

```
healthsim › Add HbA1c and lipid panel lab results from this visit
```

Expected output:
```
✓ Added lab results

Lab Results (ENC-001):
  HbA1c: 7.2% (reference: <7.0%)
  Total Cholesterol: 195 mg/dL (reference: <200)
  LDL: 118 mg/dL (reference: <100)
  HDL: 48 mg/dL (reference: >40)
  Triglycerides: 145 mg/dL (reference: <150)
```

### Step 6: View Your Work

```
healthsim › /status
```

```
Current Session
═══════════════════════════════════════
Patients:     1
Encounters:   1
Observations: 5 (Lab Results)
Conditions:   2

Total Entities: 9
═══════════════════════════════════════
```

### Step 7: Export to FHIR

```
healthsim › Export as FHIR bundle
```

```
✓ Exported FHIR bundle

Output: ./exports/patient-bundle-20260112.json
Format: FHIR R4 Bundle
Resources: 9 (Patient, Conditions, Encounter, Observations)
```

---

## What You Created

| Entity | Count | Details |
|--------|-------|---------|
| Patient | 1 | 45F, Seattle |
| Conditions | 2 | Diabetes, Hypertension |
| Encounter | 1 | Office visit |
| Observations | 5 | HbA1c, Lipid panel |

---

## Variations

### Different Demographics

```
healthsim › Create a 72-year-old male veteran in Phoenix with COPD and heart failure
```

### Pediatric Patient

```
healthsim › Create an 8-year-old patient with asthma who has had 3 ER visits this year
```

### Complex History

```
healthsim › Create a patient with a complete 5-year medical history including 
            annual checkups, two hospitalizations, and chronic disease management
```

### Multiple Patients

```
healthsim › Generate 10 patients in Chicago with varying diabetes severity
```

---

## Common Patterns

### Adding Medications

```
healthsim › Add metformin 1000mg twice daily for diabetes management
```

### Adding Procedures

```
healthsim › Add an ophthalmology referral and dilated eye exam
```

### Adding Family History

```
healthsim › Add family history of coronary artery disease (father) and breast cancer (mother)
```

---

## Troubleshooting

**Patient not generating?**
- Check that you provided enough context (age, location, or condition)
- Try being more specific about demographics

**Wrong condition code?**
- HealthSim uses ICD-10-CM codes automatically
- You can specify a code: "Add diagnosis I10 (hypertension)"

**Need more realistic data?**
- Add more context about lifestyle, occupation, family history
- HealthSim will generate more detailed realistic attributes

---

## Next Steps

- [Claims Generation](claims-generation.md) - Add insurance claims
- [Pharmacy Claims](pharmacy-claims.md) - Add pharmacy transactions
- [Cross-Product Workflow](../intermediate/cross-product-workflow.md) - Full patient journey

---

## Related

- [PatientSim Guide](../../docs/guides/patientsim-guide.md)
- [Output Formats Reference](../../docs/reference/output-formats.md)
- [Code Systems Reference](../../docs/reference/code-systems.md)
