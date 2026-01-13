# Oncology Scenarios

Generate realistic oncology patient data including cancer diagnoses, staging, biomarkers, treatment regimens, and surveillance protocols.

---

## Goal

Demonstrate how to generate complex oncology patient scenarios with proper staging, molecular markers, and treatment plans.

## Prerequisites

- HealthSim Agent installed and configured
- Familiarity with basic patient generation

---

## Example 1: Early-Stage Breast Cancer

### Step 1: Generate Patient

```
healthsim › Generate a 55-year-old female with newly diagnosed Stage IIA ER-positive, HER2-negative breast cancer
```

Expected output:
```json
{
  "patient": {
    "mrn": "PAT-001",
    "name": { "given_name": "Margaret", "family_name": "Thompson" },
    "birth_date": "1969-08-22",
    "gender": "F"
  },
  "diagnoses": [
    {
      "code": "C50.911",
      "description": "Malignant neoplasm of right female breast",
      "diagnosed_date": "2025-01-18",
      "staging": {
        "system": "AJCC_8th_edition",
        "stage_group": "IIA",
        "clinical_stage": "cT2 N0 M0"
      }
    }
  ],
  "biomarkers": {
    "estrogen_receptor": { "status": "positive", "percentage": 95 },
    "progesterone_receptor": { "status": "positive", "percentage": 80 },
    "her2": { "ihc_score": "1+", "status": "negative" },
    "ki67": { "percentage": 15, "interpretation": "low" },
    "molecular_subtype": "luminal_a"
  }
}
```

### Step 2: Add Genomic Testing

```
healthsim › Add Oncotype DX testing results
```

Expected output:
```json
{
  "genomic_testing": {
    "test_name": "Oncotype DX",
    "recurrence_score": 18,
    "risk_category": "low",
    "chemotherapy_benefit": "unlikely_to_benefit"
  }
}
```

### Step 3: Generate Treatment Plan

```
healthsim › Create treatment plan based on biomarkers
```

Expected output:
```json
{
  "treatment_plan": {
    "intent": "curative",
    "surgery": {
      "procedure": "Lumpectomy with sentinel lymph node biopsy",
      "date": "2025-02-05",
      "status": "completed"
    },
    "radiation": {
      "regimen": "Whole breast radiation 40 Gy in 15 fractions",
      "start_date": "2025-03-10"
    },
    "hormonal_therapy": {
      "medication": "Letrozole 2.5 mg daily",
      "duration": "5-10 years"
    }
  }
}
```

## What You Created

- Patient with breast cancer diagnosis and proper staging
- Molecular biomarkers driving treatment decisions
- Genomic testing influencing chemotherapy recommendation
- Comprehensive treatment plan including surgery, radiation, and hormonal therapy

---

## Example 2: Lung Cancer with Targeted Therapy

### Step 1: Generate NSCLC Patient

```
healthsim › Generate a 68-year-old male former smoker with Stage IV NSCLC adenocarcinoma, EGFR exon 19 deletion positive, with brain metastases
```

Expected output includes:
- Primary lung cancer diagnosis (C34.91)
- Brain metastases secondary diagnosis (C79.31)
- EGFR mutation status driving therapy selection
- Osimertinib treatment (CNS-penetrant TKI)

### Key Points

- EGFR mutation status determines first-line therapy
- Osimertinib preferred for brain metastases (CNS penetration)
- SRS for oligometastatic brain disease before starting TKI

---

## Example 3: Colorectal Cancer with MSI-High Status

```
healthsim › Generate a 58-year-old male with Stage III colon cancer, MSI-high, after curative resection
```

### Key Biomarkers Generated

| Marker | Result | Clinical Significance |
|--------|--------|----------------------|
| MSI Status | MSI-High | Better prognosis, immunotherapy responsive |
| KRAS | Wild type | Anti-EGFR therapy eligible |
| BRAF | V600E positive | Suggests sporadic vs Lynch |

---

## Variations

### Different Cancer Types

```
Generate a Stage IIIA triple-negative breast cancer patient requiring neoadjuvant chemotherapy
Generate an ALK-positive NSCLC patient on alectinib
Generate a Lynch syndrome patient with colorectal cancer
Generate a patient with metastatic prostate cancer on ADT
```

### Special Populations

```
Generate a 70-year-old with colon cancer and CKD Stage 3b requiring dose adjustments
Generate a cancer patient with heart failure requiring anthracycline avoidance
Generate a frail elderly patient (ECOG 2) with reduced dose chemotherapy
```

### Oncology Emergencies

```
Generate a patient presenting with febrile neutropenia during chemotherapy
Generate a patient with tumor lysis syndrome
Generate a patient with malignant spinal cord compression
```

---

## Related

- [Patient Generation](../basic/patient-generation.md) - Basic patient creation
- [Cross-Product Workflow](cross-product-workflow.md) - Full oncology journey with claims
- [Clinical Trial Protocol](../advanced/clinical-trial-protocol.md) - Trial enrollment

---

*Oncology Scenarios v1.0 | HealthSim Agent*
