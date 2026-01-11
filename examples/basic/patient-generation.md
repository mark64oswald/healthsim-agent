# Patient Generation Example

Generate synthetic patients with clinical data.

---

## Goal

Learn how to generate patients with diagnoses, medications, and lab results using HealthSim.

---

## Prerequisites

- HealthSim installed (`pip install healthsim-agent`)
- API key configured (`ANTHROPIC_API_KEY`)

---

## Steps

### Step 1: Start HealthSim

```bash
healthsim
```

You should see the welcome screen and `healthsim ›` prompt.

### Step 2: Generate a Basic Patient

```
healthsim › Generate a 50-year-old male patient with hypertension
```

Expected output:
```
✓ Added 1 patient

  ID:        PAT-001
  Name:      Michael Thompson
  Age:       50 (DOB: 1975-06-12)
  Gender:    Male
  
  Diagnoses:
    • I10     Essential hypertension
  
  Medications:
    • Lisinopril 10mg PO daily
  
  Recent Labs:
    • BMP within normal limits
```

### Step 3: Generate a Patient with Multiple Conditions

```
healthsim › Generate a 65-year-old female with Type 2 diabetes and heart failure
```

Expected output:
```
✓ Added 1 patient

  ID:        PAT-002
  Name:      Barbara Wilson
  Age:       65 (DOB: 1960-03-28)
  Gender:    Female
  
  Diagnoses:
    • E11.9   Type 2 diabetes mellitus
    • I50.9   Heart failure, unspecified
    • I10     Essential hypertension
    • E78.5   Hyperlipidemia
  
  Medications:
    • Metformin 1000mg PO BID
    • Lisinopril 20mg PO daily
    • Carvedilol 12.5mg PO BID
    • Furosemide 40mg PO daily
    • Atorvastatin 40mg PO QHS
  
  Recent Labs:
    • HbA1c: 7.4% (elevated)
    • BNP: 450 pg/mL (elevated)
    • Creatinine: 1.2 mg/dL
    • eGFR: 58 mL/min
```

### Step 4: Generate a Specific Clinical Scenario

```
healthsim › Generate a 45-year-old with newly diagnosed breast cancer, 
           Stage IIA, ER-positive, HER2-negative
```

Expected output:
```
✓ Added 1 patient

  ID:        PAT-003
  Name:      Jennifer Martinez
  Age:       45 (DOB: 1980-11-05)
  Gender:    Female
  
  Diagnoses:
    • C50.911  Malignant neoplasm of breast
    • Z85.3    Personal history of malignant neoplasm of breast
  
  Cancer Details:
    Stage:     IIA (T2N0M0)
    Histology: Invasive ductal carcinoma
    Grade:     2 (moderately differentiated)
    
  Biomarkers:
    • ER: 95% (Positive)
    • PR: 80% (Positive)
    • HER2: 1+ (Negative)
    • Ki-67: 15%
    
  Treatment Plan:
    • Surgery: Lumpectomy with sentinel node biopsy
    • Radiation: Whole breast radiation planned
    • Systemic: Adjuvant hormonal therapy (tamoxifen)
```

### Step 5: Check Your Session

```
healthsim › /status
```

Expected output:
```
Current Session
═══════════════════════════════════════
Patients:     3
Encounters:   0
Claims:       0
Pharmacy:     0

Recent Activity:
  • PAT-001 (Michael Thompson) - Hypertension
  • PAT-002 (Barbara Wilson) - T2DM, Heart Failure
  • PAT-003 (Jennifer Martinez) - Breast Cancer
```

### Step 6: Save Your Work

```
healthsim › save as patient-examples

✓ Saved session 'patient-examples'
```

### Step 7: Export as FHIR

```
healthsim › Export as FHIR R4
```

Expected output:
```
✓ Generated FHIR R4 Bundle → output/patients-bundle.json

  Bundle Type: collection
  Resources:
    • 3 Patient resources
    • 8 Condition resources
    • 12 MedicationRequest resources
    • 6 Observation resources
```

---

## What You Created

| Patient | Age | Gender | Primary Conditions |
|---------|-----|--------|-------------------|
| PAT-001 | 50 | M | Hypertension |
| PAT-002 | 65 | F | Diabetes, Heart Failure |
| PAT-003 | 45 | F | Breast Cancer (Stage IIA) |

Total: 3 patients with clinically appropriate comorbidities, medications, and labs.

---

## Variations

### Generate with specific location

```
Generate a 70-year-old diabetic patient in Miami, Florida
```

### Generate multiple at once

```
Generate 5 patients with varying ages and chronic conditions
```

### Generate with specific identifiers

```
Generate a patient with MRN starting with "TEST-"
```

### Generate pediatric patient

```
Generate an 8-year-old with Type 1 diabetes
```

### Generate elderly with polypharmacy

```
Generate an 85-year-old with 5+ chronic conditions and appropriate medications
```

---

## Common Issues

### Patient lacks expected medications

Try:
```
Generate a diabetic patient with all guideline-recommended medications
```

### Labs not included

Try:
```
Generate a patient with recent lab results showing disease control
```

### Need specific codes

Try:
```
Generate a patient with ICD-10 code E11.65 (diabetes with hyperglycemia)
```

---

## Related Examples

- [Claims Generation](claims-generation.md) - Add claims for these patients
- [Pharmacy Claims](pharmacy-claims.md) - Generate prescription fills
- [Cross-Product Workflow](../intermediate/cross-product-workflow.md) - Complete patient journey

---

## Related Guides

- [PatientSim Guide](../../docs/guides/patientsim-guide.md) - Complete PatientSim reference
- [Quick Reference](../../docs/getting-started/quick-reference.md) - Command cheat sheet
