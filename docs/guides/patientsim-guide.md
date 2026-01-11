# PatientSim Guide

Generate realistic synthetic clinical/EMR patient data through natural conversation.

---

## Overview

PatientSim creates clinically plausible patient records with:

- **Demographics** - Names, dates of birth, addresses, identifiers
- **Diagnoses** - ICD-10-CM coded conditions with onset dates
- **Medications** - Drugs with dosing, frequency, and duration
- **Lab Results** - Values with reference ranges and interpretation
- **Encounters** - Outpatient visits, ED visits, hospitalizations
- **Procedures** - CPT/HCPCS coded procedures
- **Vital Signs** - Blood pressure, heart rate, temperature, etc.

**Output Formats:** FHIR R4, HL7v2, C-CDA, MIMIC-III, JSON, CSV

---

## Quick Start

Generate your first patient:

```
healthsim › Generate a 45-year-old patient with Type 2 diabetes
```

Output:
```
✓ Added 1 patient

  ID:        PAT-001
  Name:      James Wilson
  Age:       45 (DOB: 1980-03-22)
  Gender:    Male
  
  Diagnoses:
    • E11.9   Type 2 diabetes mellitus
    • I10     Essential hypertension
    • E78.5   Hyperlipidemia
  
  Medications:
    • Metformin 1000mg PO BID
    • Lisinopril 20mg PO daily
    • Atorvastatin 40mg PO QHS
  
  Recent Labs:
    • HbA1c: 7.8% (elevated)
    • Glucose: 156 mg/dL (elevated)
    • Creatinine: 1.0 mg/dL (normal)
```

---

## Common Scenarios

### Basic Patient Generation

Generate patients with specific characteristics:

```
Generate a 72-year-old female with heart failure
Generate a pediatric patient (age 8) with asthma
Generate a pregnant patient in her second trimester
Generate an elderly patient with multiple chronic conditions
```

### Chronic Disease Management

Diabetes scenarios:

```
Generate a diabetic patient with poor glycemic control (A1C > 9)
Create a patient with Type 2 diabetes and diabetic nephropathy
Generate a patient newly diagnosed with diabetes
```

Heart failure scenarios:

```
Generate a patient with HFrEF (reduced ejection fraction)
Create a heart failure patient on GDMT (guideline-directed therapy)
Generate a patient with acute decompensated heart failure
```

### Acute Care

Emergency department:

```
Generate a patient presenting to the ED with chest pain
Create an ED patient with acute appendicitis
Generate a trauma patient from motor vehicle accident
```

Inpatient:

```
Generate a patient admitted for pneumonia
Create an inpatient with sepsis
Generate a surgical patient post hip replacement
```

### Oncology

Breast cancer:

```
Generate a 55-year-old with Stage IIA ER-positive breast cancer
Create a breast cancer patient post-mastectomy on hormonal therapy
Generate a metastatic breast cancer patient on chemotherapy
```

Lung cancer:

```
Generate a patient with Stage IV NSCLC, EGFR positive
Create a lung cancer patient with brain metastases
Generate a small cell lung cancer patient
```

Colorectal:

```
Generate a patient with Stage III colon cancer, MSI-high
Create a colorectal cancer patient post-colectomy
Generate a rectal cancer patient on chemoradiation
```

### Pediatric

```
Generate a 6-month-old for well-child visit
Create a pediatric patient with Type 1 diabetes
Generate a teenager with anxiety and depression
```

### Mental Health

```
Generate a patient with major depressive disorder
Create a patient with generalized anxiety disorder
Generate a patient with bipolar disorder on mood stabilizers
```

---

## Adding Clinical Details

### Encounters

Add visits to existing patients:

```
Add an office visit for this patient
Generate an ED encounter for acute chest pain
Create a 3-day hospitalization for pneumonia
```

### Procedures

```
Add a cardiac catheterization procedure
Generate a colonoscopy with biopsy
Add an appendectomy procedure
```

### Lab Results

```
Add comprehensive metabolic panel results
Generate lipid panel with abnormal values
Add tumor marker labs (CEA, CA-125)
```

### Imaging

```
Add chest X-ray showing pneumonia
Generate CT scan of abdomen/pelvis
Add cardiac echo showing reduced EF
```

---

## Output Formats

### FHIR R4

```
Generate this patient as FHIR R4
Export as FHIR Bundle
Generate FHIR conforming to US Core profile
```

Output includes:
- Patient resource
- Condition resources (diagnoses)
- MedicationRequest resources
- Observation resources (labs, vitals)
- Encounter resources

### HL7v2

```
Generate as HL7v2 ADT^A01 admission message
Create HL7v2 ORU^R01 lab results message
Export as HL7v2.5.1
```

Supported message types:
- ADT (Admit/Discharge/Transfer)
- ORU (Observation Results)
- ORM (Orders)

### C-CDA

```
Generate as C-CDA document
Export as Continuity of Care Document
Create C-CDA for Health Information Exchange
```

Document types:
- CCD (Continuity of Care Document)
- Progress Note
- Discharge Summary

### MIMIC-III

```
Generate in MIMIC-III format
Export as MIMIC tables
Create MIMIC-compatible patient data
```

Tables:
- PATIENTS
- ADMISSIONS
- DIAGNOSES_ICD
- PRESCRIPTIONS
- LABEVENTS

### CSV/JSON

```
Export as CSV
Generate as JSON
Export patient data as spreadsheet
```

---

## Clinical Patterns

### Appropriate Comorbidities

HealthSim generates clinically plausible comorbidity patterns:

| Primary Condition | Common Comorbidities |
|-------------------|---------------------|
| Type 2 Diabetes | Hypertension, hyperlipidemia, obesity, CKD |
| Heart Failure | CAD, hypertension, atrial fibrillation, CKD |
| COPD | CAD, lung cancer, anxiety, osteoporosis |
| CKD | Diabetes, hypertension, anemia, bone disease |

### Medication Matching

Medications match conditions:

| Condition | Expected Medications |
|-----------|---------------------|
| Type 2 Diabetes | Metformin, SGLT2i, GLP-1 RA, insulin |
| Heart Failure | ACEi/ARB, beta-blocker, diuretic, MRA |
| Hypertension | ACEi/ARB, CCB, thiazide |
| Hyperlipidemia | Statin, ezetimibe |

### Lab Correlation

Labs reflect disease state:

| Condition | Lab Findings |
|-----------|-------------|
| Diabetes | Elevated A1C, glucose, possible microalbuminuria |
| Heart Failure | Elevated BNP, possible anemia, renal changes |
| CKD | Elevated creatinine, low eGFR, electrolyte changes |

---

## Tips & Best Practices

### Be Specific

More detail produces better results:

```
# Basic (works but generic)
Generate a diabetic patient

# Better (more realistic output)
Generate a 58-year-old Hispanic male with Type 2 diabetes for 10 years,
currently on metformin and semaglutide, A1C around 7.5%, with mild 
diabetic retinopathy and stage 2 CKD, seen regularly by endocrinology
```

### Use Clinical Language

HealthSim understands medical terminology:

```
Generate a patient with HFrEF, EF 30%, on GDMT
Create a patient with DKA requiring ICU admission
Generate ESRD patient on hemodialysis
```

### Build Progressively

Start simple, add complexity:

```
1. Generate a 65-year-old with COPD
2. Add a recent exacerbation requiring hospitalization
3. Add post-discharge follow-up encounter
4. Generate the discharge medications
```

### Request Specific Codes

When code accuracy matters:

```
Generate a patient with E11.65 (diabetes with hyperglycemia)
Use ICD-10 code I50.22 for chronic systolic heart failure
Include CPT 99214 for the office visit
```

---

## Oncology Deep Dive

PatientSim includes comprehensive oncology support.

### Staging

Request specific TNM staging:

```
Generate a patient with T2N1M0 breast cancer
Create Stage IIIB lung cancer (T3N2M0)
```

### Biomarkers

Include molecular testing:

```
Generate breast cancer with ER+, PR+, HER2-
Create lung cancer patient EGFR exon 19 deletion positive
Generate colorectal cancer MSI-high, BRAF wild-type
```

### Treatment Plans

```
Generate a breast cancer patient post-lumpectomy on adjuvant therapy
Create a lung cancer patient on osimertinib
Generate a patient receiving FOLFOX chemotherapy
```

### Surveillance

```
Generate oncology follow-up with imaging and labs
Create a cancer survivorship visit
Add tumor marker surveillance labs
```

---

## Related Resources

### Skills

- [diabetes-management.md](../../skills/patientsim/diabetes-management.md)
- [heart-failure.md](../../skills/patientsim/heart-failure.md)
- [oncology/](../../skills/patientsim/oncology/)
- [behavioral-health.md](../../skills/patientsim/behavioral-health.md)

### Reference

- [Code Systems](../reference/code-systems.md) - ICD-10, CPT, LOINC
- [Output Formats](../reference/output-formats.md) - Format specifications
- [Data Models](../reference/data-models.md) - Canonical patient model

### Examples

- [Basic Patient Generation](../../examples/basic/patient-generation.md)
- [Oncology Scenarios](../../examples/intermediate/oncology-scenarios.md)
- [Format Transformations](../../examples/intermediate/format-transformations.md)

---

## Troubleshooting

### Patient lacks expected medications

Be explicit:
```
Generate a diabetic patient with all appropriate medications including
metformin, blood pressure medication, and statin
```

### Diagnoses don't have proper codes

Request coded output:
```
Generate a patient with properly coded ICD-10-CM diagnoses
```

### Output doesn't match format specification

Specify the format clearly:
```
Generate as valid FHIR R4 conforming to US Core 5.0.1
```

See [Troubleshooting](../getting-started/troubleshooting.md) for more solutions.
