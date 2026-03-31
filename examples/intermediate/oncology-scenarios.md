# Oncology Scenarios Example

Generate complex oncology patient scenarios with staging, treatment protocols, and longitudinal data.

---

## Goal

Create realistic cancer patient data including:

- Cancer staging (TNM classification)
- Treatment protocols (chemo, radiation, immunotherapy)
- Lab and tumor marker trends
- Multi-disciplinary care episodes

---

## Prerequisites

- HealthSim installed and running
- Basic familiarity with [Patient Generation](../basic/patient-generation.md)
- ~20 minutes

---

## Steps

### Step 1: Generate a Breast Cancer Patient

```
healthsim › Generate a 52-year-old female newly diagnosed with Stage IIA 
            breast cancer (invasive ductal carcinoma)
```

Expected output:
```
✓ Generated oncology patient

Patient: PAT-001
  Name: Jennifer Martinez
  DOB: 1973-06-15 (52 years)
  Location: Houston, TX 77030
  
Cancer Diagnosis:
  Type: Invasive Ductal Carcinoma (IDC)
  ICD-10: C50.911 (Malignant neoplasm of right breast)
  Morphology: 8500/3 (Infiltrating duct carcinoma)
  
Staging (AJCC 8th Edition):
  Clinical Stage: IIA (T2 N0 M0)
  T: T2 (2-5cm tumor)
  N: N0 (No regional lymph node metastasis)
  M: M0 (No distant metastasis)
  
Biomarkers:
  ER: Positive (95%)
  PR: Positive (80%)
  HER2: Negative (1+ IHC)
  Ki-67: 15%
  Grade: 2 (Moderately differentiated)
```

### Step 2: Add Diagnostic Workup

```
healthsim › Generate the diagnostic workup including mammogram, ultrasound, 
            biopsy, and staging CT
```

Expected output:
```
✓ Generated diagnostic encounters

Encounters Created: 4

1. ENC-001: Diagnostic Mammogram
   Date: 2026-01-05
   CPT: 77066 (Diagnostic mammography bilateral)
   Finding: 2.8cm spiculated mass, right breast at 10 o'clock
   BIRADS: 5 (Highly suggestive of malignancy)

2. ENC-002: Breast Ultrasound
   Date: 2026-01-06
   CPT: 76642 (US breast, unilateral)
   Finding: Irregular hypoechoic mass 2.6cm, suspicious lymph node

3. ENC-003: Core Needle Biopsy
   Date: 2026-01-08
   CPT: 19083 (Biopsy breast with imaging guidance)
   Pathology: IDC, Grade 2, ER+/PR+/HER2-

4. ENC-004: Staging CT Chest/Abd/Pelvis
   Date: 2026-01-10
   CPT: 71260, 74177 (CT chest, CT abd/pelvis with contrast)
   Finding: No evidence of distant metastasis
```

### Step 3: Create Treatment Plan

```
healthsim › Generate a treatment plan: lumpectomy with sentinel node biopsy, 
            followed by AC-T chemotherapy, then radiation
```

Expected output:
```
✓ Generated treatment plan

Treatment Protocol: NCCN Breast Cancer - Operable Disease

Phase 1: Surgery
  Procedure: Lumpectomy with sentinel lymph node biopsy
  Scheduled: 2026-01-22
  
Phase 2: Adjuvant Chemotherapy
  Regimen: AC-T (Doxorubicin/Cyclophosphamide → Paclitaxel)
  Duration: 4 cycles AC q2wk, then 12 weeks T weekly
  Start Date: 2026-02-15 (3-4 weeks post-op)
  
Phase 3: Radiation Therapy
  Type: Whole breast radiation + boost
  Duration: 4-6 weeks
  Start Date: ~2026-06-01 (after chemo completion)
  
Phase 4: Endocrine Therapy
  Agent: Anastrozole 1mg daily
  Duration: 5-10 years
  Start Date: After radiation
```

### Step 4: Generate Surgical Encounter

```
healthsim › Generate the surgical encounter and claims for the lumpectomy
```

Expected output:
```
✓ Generated surgical encounter and claims

Encounter: ENC-005 (Surgical)
  Date: 2026-01-22
  Facility: MD Anderson Cancer Center
  Surgeon: Dr. Robert Kim, MD (Breast Surgical Oncology)
  
Procedures:
  1. 19301 - Mastectomy, partial (lumpectomy)
  2. 38525 - Sentinel lymph node biopsy
  3. 38900 - Intraop lymphatic mapping

Pathology Results:
  Tumor Size: 2.4cm
  Margins: Negative (>2mm)
  Sentinel Nodes: 0/3 positive
  Final Stage: pT2 pN0 M0 (Stage IIA confirmed)

Claims Generated:
  Professional (837P): CLM-2026-000001 - $4,250.00
  Facility (837I): CLM-2026-000002 - $18,500.00
```

### Step 5: Generate Chemotherapy Encounters

```
healthsim › Generate the first 4 cycles of AC chemotherapy with labs
```

Expected output:
```
✓ Generated chemotherapy encounters

Chemotherapy Series: AC (Adriamycin + Cyclophosphamide)

Cycle 1 (2026-02-15):
  Location: Outpatient Infusion Center
  Pre-treatment Labs: CBC, CMP normal
  Drugs Administered:
    - Doxorubicin 60 mg/m² IV
    - Cyclophosphamide 600 mg/m² IV
  CPT: 96413, 96415 (Chemo admin)
  J-Codes: J9000 (Doxorubicin), J9070 (Cyclophosphamide)
  Side Effects: Nausea (Grade 1), Fatigue (Grade 2)

Cycle 2 (2026-03-01):
  Pre-treatment Labs: ANC 1.8, okay to proceed
  Drugs: Same
  Side Effects: Alopecia onset, Nausea (Grade 1)

Cycle 3 (2026-03-15):
  Pre-treatment Labs: ANC 1.5, close monitoring
  Drugs: Same
  Side Effects: Fatigue (Grade 2)

Cycle 4 (2026-03-29):
  Pre-treatment Labs: ANC 2.1, counts recovering
  Drugs: Same
  Completed AC phase ✓

Lab Trends Generated: 
  - CBC x 8 (pre/post each cycle)
  - CMP x 4 (each cycle)
```

### Step 6: Add Tumor Markers

```
healthsim › Add tumor marker tracking - CA 15-3 and CA 27.29
```

Expected output:
```
✓ Generated tumor marker series

Tumor Markers (LOINC: 6875-9 CA 15-3, 17842-6 CA 27.29):

  Baseline (2026-01-10):
    CA 15-3: 42 U/mL (elevated, ref <30)
    CA 27.29: 48 U/mL (elevated, ref <38)

  Post-Surgery (2026-02-05):
    CA 15-3: 28 U/mL (normalizing)
    CA 27.29: 32 U/mL (normalizing)

  Mid-Chemo (2026-03-15):
    CA 15-3: 18 U/mL (normal)
    CA 27.29: 22 U/mL (normal)

  Post-Chemo (2026-05-01):
    CA 15-3: 15 U/mL (normal)
    CA 27.29: 19 U/mL (normal)

Trend: ↓ Declining, consistent with response to treatment
```

### Step 7: View Summary

```
healthsim › /status
```

```
Current Session: Oncology Scenario
═══════════════════════════════════════
Patients:      1 (Breast cancer)
Encounters:    14
  Diagnostic:  4
  Surgical:    1
  Chemo:       4
  Labs:        5
Claims:        6
  Professional: 4
  Facility:     2
Lab Results:   24
═══════════════════════════════════════
```

### Step 8: Export for EHR Testing

```
healthsim › Export as FHIR R4 bundle
```

```
✓ Exported FHIR R4 Bundle

Resources:
  Patient: 1
  Condition: 3 (cancer dx, staging)
  Procedure: 8
  MedicationAdministration: 8 (chemo doses)
  Observation: 24 (labs + markers)
  DiagnosticReport: 6
  
Output: ./exports/oncology-patient-fhir.json
```

---

## What You Created

| Entity | Count | Details |
|--------|-------|---------|
| Patient | 1 | Stage IIA breast cancer |
| Encounters | 14 | Diagnostic through treatment |
| Claims | 6 | Professional + facility |
| Lab Results | 24 | CBC, CMP, tumor markers |
| Procedures | 8 | Surgery + chemo admin |

---

## Variations

### Metastatic Cancer

```
healthsim › Generate a Stage IV lung cancer patient with brain metastasis
```

### Hematologic Malignancy

```
healthsim › Generate a patient with newly diagnosed AML requiring induction chemo
```

### Immunotherapy Patient

```
healthsim › Generate a melanoma patient on pembrolizumab with immune-related AEs
```

### Clinical Trial Subject

```
healthsim › Generate a breast cancer patient enrolled in a CDK4/6 inhibitor trial
```

---

## Oncology-Specific Elements

### Staging Systems

| Cancer | System | Example |
|--------|--------|---------|
| Solid Tumors | TNM (AJCC) | T2 N0 M0 |
| Lymphoma | Ann Arbor | Stage IIIB |
| CLL | Rai/Binet | Rai Stage II |

### Common Biomarkers

| Cancer | Markers |
|--------|---------|
| Breast | ER, PR, HER2, Ki-67 |
| Lung | EGFR, ALK, PD-L1 |
| Colon | KRAS, BRAF, MSI |
| Prostate | PSA, Gleason |

### Treatment Modalities

| Type | CPT Range | J-Code |
|------|-----------|--------|
| Chemo Admin | 96401-96549 | Various |
| Radiation | 77261-77799 | - |
| Immunotherapy | 96413 | J9271 (Keytruda) |

---

## Related

- [PatientSim Guide](../../docs/guides/patientsim-guide.md)
- [Claims Generation](../basic/claims-generation.md)
- [Cross-Product Workflow](./cross-product-workflow.md)
