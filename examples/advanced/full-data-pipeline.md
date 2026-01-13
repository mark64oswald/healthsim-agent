# Advanced Example: Full Healthcare Data Pipeline

This example demonstrates building a complete end-to-end healthcare data pipeline that spans all six HealthSim products, simulating a patient's journey from provider network discovery through clinical care, claims processing, pharmacy management, and potential clinical trial enrollment.

## Scenario

Simulate a comprehensive healthcare journey for a patient with newly diagnosed Type 2 diabetes in San Diego County, including:
- Finding an in-network endocrinologist (NetworkSim)
- Clinical encounters and lab work (PatientSim)
- Medical claims processing (MemberSim)
- Prescription management (RxMemberSim)
- Population health context (PopulationSim)
- Clinical trial screening (TrialSim)

## Pipeline Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    FULL HEALTHCARE DATA PIPELINE                        │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐              │
│  │ PopulationSim│───▶│  NetworkSim  │───▶│  PatientSim  │              │
│  │ Demographics │    │ Find Provider│    │  Clinical    │              │
│  └──────────────┘    └──────────────┘    └──────────────┘              │
│         │                   │                   │                       │
│         ▼                   ▼                   ▼                       │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐              │
│  │   Cohort     │    │  Provider    │    │   Claims     │              │
│  │ Attributes   │    │   Network    │    │  (MemberSim) │              │
│  └──────────────┘    └──────────────┘    └──────────────┘              │
│                                                 │                       │
│                      ┌──────────────┐          │                       │
│                      │  RxMemberSim │◀─────────┤                       │
│                      │   Pharmacy   │          │                       │
│                      └──────────────┘          │                       │
│                             │                  │                       │
│                             ▼                  ▼                       │
│                      ┌──────────────┐    ┌──────────────┐              │
│                      │  Formulary   │    │   TrialSim   │              │
│                      │  Processing  │    │  Screening   │              │
│                      └──────────────┘    └──────────────┘              │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## Step 1: Population Context (PopulationSim)

```
Query population health data for San Diego County to understand the diabetes 
prevalence and social determinants affecting our target area. Focus on 
census tracts in the Chula Vista area (South San Diego).
```

### Query Results

```json
{
  "population_context": {
    "geography": {
      "county": "San Diego",
      "state": "CA",
      "focus_area": "Chula Vista",
      "census_tracts_analyzed": 24
    },
    "health_indicators": {
      "diabetes_prevalence": 12.8,
      "obesity_prevalence": 32.4,
      "no_health_insurance": 8.2,
      "no_leisure_physical_activity": 24.6
    },
    "social_vulnerability": {
      "svi_overall": 0.62,
      "socioeconomic_theme": 0.58,
      "minority_language_theme": 0.78
    },
    "demographics": {
      "total_population": 185000,
      "median_age": 34.2,
      "hispanic_latino_pct": 58.4,
      "limited_english_pct": 12.8
    }
  }
}
```

## Step 2: Create Patient Profile

```
Create a patient profile for a 52-year-old Hispanic male residing in Chula Vista
who was just diagnosed with Type 2 diabetes during a routine checkup. Include:
- Complete demographics based on the population context
- Family history of diabetes
- Recent diagnosis with HbA1c of 8.2%
- BMI of 31, hypertension
- Works as a construction supervisor, has employer-sponsored insurance
```

### Patient Profile

```json
{
  "person": {
    "person_id": "P-2024-SD-00001",
    "ssn": "612-45-8932",
    "identifiers": {
      "mrn": "SD-MRN-00458721",
      "member_id": "BCB-CA-5589412"
    }
  },
  "demographics": {
    "name": {
      "first": "Carlos",
      "middle": "Antonio",
      "last": "Mendez"
    },
    "dob": "1972-06-18",
    "age": 52,
    "sex": "M",
    "gender_identity": "Male",
    "race": ["Other Race"],
    "ethnicity": "Hispanic or Latino",
    "preferred_language": "Spanish",
    "marital_status": "Married"
  },
  "contact": {
    "address": {
      "line1": "1245 Palomar Street",
      "city": "Chula Vista",
      "state": "CA",
      "postal_code": "91911",
      "county": "San Diego",
      "census_tract": "06073013300"
    },
    "phone": "619-555-4821",
    "email": "carlos.mendez@email.com"
  },
  "employment": {
    "status": "Full-time",
    "occupation": "Construction Supervisor",
    "employer": "Pacific Construction Corp"
  },
  "insurance": {
    "type": "Employer-Sponsored",
    "payer": "Blue Cross Blue Shield of California",
    "plan": "PPO Gold",
    "member_id": "BCB-CA-5589412",
    "group_number": "PCC-2024-001"
  },
  "clinical_summary": {
    "new_diagnoses": [
      {
        "condition": "Type 2 diabetes mellitus without complications",
        "icd10": "E11.9",
        "diagnosed_date": "2024-11-15",
        "hba1c_at_diagnosis": 8.2
      }
    ],
    "existing_conditions": [
      {
        "condition": "Essential hypertension",
        "icd10": "I10",
        "onset_date": "2019-03-22",
        "controlled": true
      },
      {
        "condition": "Overweight",
        "icd10": "E66.3",
        "onset_date": "2015-01-01",
        "bmi": 31.0
      }
    ],
    "family_history": [
      {"condition": "Type 2 Diabetes", "relative": "Father", "age_at_onset": 55},
      {"condition": "Type 2 Diabetes", "relative": "Mother", "age_at_onset": 62},
      {"condition": "Coronary Artery Disease", "relative": "Father", "age_at_onset": 68}
    ],
    "allergies": [
      {"substance": "Penicillin", "reaction": "Rash", "severity": "Moderate"}
    ],
    "current_medications": [
      {"name": "Lisinopril", "dose": "20mg", "frequency": "QD", "indication": "Hypertension"}
    ]
  }
}
```

## Step 3: Find In-Network Provider (NetworkSim)

```
Search for an in-network endocrinologist near Chula Vista, CA 91911 for 
Carlos Mendez's BCBS PPO plan. Find providers within 15 miles who:
- Accept new patients
- Are board-certified in endocrinology
- Have Spanish-speaking capability preferred
```

### Provider Search Results

```json
{
  "provider_search": {
    "search_criteria": {
      "specialty": "Endocrinology",
      "location": "91911",
      "radius_miles": 15,
      "network": "BCBS California PPO",
      "accepting_new_patients": true
    },
    "results": [
      {
        "npi": "1234567890",
        "name": "Dr. Elena Vasquez, MD",
        "credentials": "MD, FACE",
        "specialty": "Endocrinology, Diabetes & Metabolism",
        "taxonomy_code": "207RE0101X",
        "practice": {
          "name": "San Diego Diabetes & Endocrine Center",
          "address": "435 H Street, Suite 200, Chula Vista, CA 91910",
          "phone": "619-555-3200"
        },
        "network_status": "In-Network",
        "accepting_new_patients": true,
        "languages": ["English", "Spanish"],
        "distance_miles": 2.1,
        "next_available": "2024-12-02",
        "patient_rating": 4.8
      },
      {
        "npi": "2345678901",
        "name": "Dr. Michael Chen, MD, PhD",
        "credentials": "MD, PhD",
        "specialty": "Endocrinology, Diabetes & Metabolism",
        "taxonomy_code": "207RE0101X",
        "practice": {
          "name": "Sharp Rees-Stealy Medical Group",
          "address": "2001 Fourth Avenue, San Diego, CA 92101",
          "phone": "619-555-8500"
        },
        "network_status": "In-Network",
        "accepting_new_patients": true,
        "languages": ["English", "Mandarin"],
        "distance_miles": 8.4,
        "next_available": "2024-11-28",
        "patient_rating": 4.6
      }
    ],
    "selected_provider": {
      "npi": "1234567890",
      "reason": "Closest, Spanish-speaking, highly rated"
    }
  }
}
```

## Step 4: Initial Specialist Visit (PatientSim)

```
Generate the initial endocrinology visit for Carlos with Dr. Vasquez on 2024-12-02:
- New patient comprehensive visit (99205)
- Diabetes education
- Order labs: comprehensive metabolic panel, lipid panel, HbA1c, urine microalbumin
- Order retinal exam referral
- Prescribe Metformin 500mg BID
- Schedule follow-up in 3 months
```

### Clinical Encounter

```json
{
  "encounter": {
    "encounter_id": "ENC-2024-12-02-001",
    "patient_id": "P-2024-SD-00001",
    "encounter_type": "Outpatient",
    "class": "Ambulatory",
    "status": "Finished",
    "period": {
      "start": "2024-12-02T09:00:00-08:00",
      "end": "2024-12-02T10:15:00-08:00"
    },
    "location": {
      "facility": "San Diego Diabetes & Endocrine Center",
      "address": "435 H Street, Suite 200, Chula Vista, CA 91910"
    },
    "providers": [
      {
        "npi": "1234567890",
        "name": "Dr. Elena Vasquez",
        "role": "Attending"
      }
    ],
    "reason_for_visit": "New patient evaluation for Type 2 diabetes mellitus",
    "diagnoses": [
      {
        "code": "E11.9",
        "display": "Type 2 diabetes mellitus without complications",
        "type": "Principal"
      },
      {
        "code": "I10",
        "display": "Essential (primary) hypertension",
        "type": "Secondary"
      },
      {
        "code": "E66.3",
        "display": "Overweight",
        "type": "Secondary"
      }
    ],
    "procedures": [
      {
        "code": "99205",
        "display": "Office visit, new patient, high complexity",
        "cpt": true
      }
    ],
    "clinical_notes": {
      "chief_complaint": "New diagnosis of Type 2 diabetes, referred by PCP",
      "history_of_present_illness": "52-year-old Hispanic male with newly diagnosed T2DM, HbA1c 8.2% found on routine labs. Patient reports polyuria and fatigue over past 2 months. Strong family history of diabetes.",
      "physical_exam": {
        "vitals": {
          "height_cm": 175,
          "weight_kg": 95,
          "bmi": 31.0,
          "blood_pressure": "138/86",
          "heart_rate": 78,
          "temperature_c": 36.8
        },
        "general": "Well-appearing, overweight male in no acute distress",
        "cardiovascular": "Regular rate and rhythm, no murmurs",
        "extremities": "No edema, pulses intact, sensation intact to monofilament"
      },
      "assessment_and_plan": [
        "Type 2 Diabetes Mellitus - Newly diagnosed with HbA1c 8.2%. Start Metformin 500mg BID with meals, titrate to 1000mg BID as tolerated. Diabetes education today. Order baseline labs.",
        "Essential Hypertension - Well controlled on Lisinopril. Continue current regimen.",
        "Overweight - Discussed lifestyle modifications, referred to nutrition counseling.",
        "Preventive Care - Order dilated retinal exam, foot exam today showed intact sensation."
      ]
    },
    "orders": {
      "laboratory": [
        {"code": "80053", "display": "Comprehensive metabolic panel"},
        {"code": "80061", "display": "Lipid panel"},
        {"code": "83036", "display": "Hemoglobin A1c"},
        {"code": "82043", "display": "Urine microalbumin, quantitative"}
      ],
      "referrals": [
        {
          "specialty": "Ophthalmology",
          "reason": "Diabetic retinal examination",
          "urgency": "Routine"
        }
      ],
      "medications": [
        {
          "medication": "Metformin 500mg tablet",
          "sig": "Take 1 tablet by mouth twice daily with meals",
          "quantity": 60,
          "refills": 5,
          "ndc": "00378-0221-01"
        }
      ]
    },
    "follow_up": {
      "timeframe": "3 months",
      "scheduled_date": "2025-03-03",
      "instructions": "Return for follow-up, repeat HbA1c"
    }
  }
}
```

## Step 5: Process Medical Claim (MemberSim)

```
Generate the professional claim for this visit and process through adjudication:
- Rendering provider: Dr. Vasquez (NPI 1234567890)
- Billing provider: San Diego Diabetes & Endocrine Center
- Service: 99205 with E11.9 primary diagnosis
- Apply BCBS PPO contracted rates
- Calculate patient responsibility (deductible, coinsurance)
```

### Claims Processing

```json
{
  "claim": {
    "claim_id": "CLM-2024-12-001584",
    "claim_type": "Professional",
    "claim_status": "Paid",
    "member": {
      "member_id": "BCB-CA-5589412",
      "subscriber_id": "BCB-CA-5589412",
      "group_number": "PCC-2024-001"
    },
    "dates": {
      "service_from": "2024-12-02",
      "service_to": "2024-12-02",
      "received": "2024-12-05",
      "processed": "2024-12-08",
      "paid": "2024-12-12"
    },
    "providers": {
      "rendering": {
        "npi": "1234567890",
        "name": "Elena Vasquez MD",
        "taxonomy": "207RE0101X"
      },
      "billing": {
        "npi": "1987654321",
        "name": "San Diego Diabetes & Endocrine Center",
        "tax_id": "95-4567890"
      },
      "service_location": {
        "place_of_service": "11",
        "description": "Office"
      }
    },
    "diagnosis_codes": [
      {"sequence": 1, "code": "E11.9", "type": "Principal"},
      {"sequence": 2, "code": "I10"},
      {"sequence": 3, "code": "E66.3"}
    ],
    "service_lines": [
      {
        "line_number": 1,
        "procedure_code": "99205",
        "modifiers": [],
        "diagnosis_pointers": [1, 2, 3],
        "units": 1,
        "charges": {
          "billed": 425.00,
          "allowed": 285.00,
          "paid": 228.00,
          "coinsurance": 57.00,
          "copay": 0.00,
          "deductible": 0.00
        },
        "adjudication": {
          "status": "Paid",
          "remark_codes": ["N130"],
          "adjustment_reason": "CO-45"
        }
      }
    ],
    "totals": {
      "billed": 425.00,
      "allowed": 285.00,
      "paid": 228.00,
      "member_responsibility": 57.00,
      "plan_paid": 228.00
    },
    "benefit_period": {
      "deductible_met": 850.00,
      "deductible_remaining": 150.00,
      "oop_met": 1250.00,
      "oop_remaining": 4750.00
    }
  }
}
```

## Step 6: Pharmacy Claim (RxMemberSim)

```
Process the Metformin prescription through the pharmacy benefit:
- Filled at CVS Pharmacy in Chula Vista
- Apply PBM formulary rules
- Calculate patient cost share
- Include DUR screening
```

### Pharmacy Claim Processing

```json
{
  "pharmacy_claim": {
    "claim_id": "RX-2024-12-00892341",
    "transaction_type": "B1",
    "claim_status": "Paid",
    "member": {
      "member_id": "BCB-CA-5589412",
      "cardholder_id": "BCB-CA-5589412",
      "group_id": "PCC-RX-001",
      "person_code": "01"
    },
    "dates": {
      "date_of_service": "2024-12-02",
      "date_written": "2024-12-02",
      "date_processed": "2024-12-02"
    },
    "pharmacy": {
      "ncpdp_id": "5678901",
      "npi": "1456789012",
      "name": "CVS Pharmacy #4521",
      "address": "555 Broadway, Chula Vista, CA 91910"
    },
    "prescriber": {
      "npi": "1234567890",
      "name": "Elena Vasquez MD",
      "dea": "FV1234567"
    },
    "medication": {
      "ndc": "00378022101",
      "drug_name": "METFORMIN HCL 500MG TAB",
      "gpi": "27250010000310",
      "therapeutic_class": "Antidiabetic - Biguanide",
      "brand_generic": "G",
      "daw_code": "0",
      "quantity": 60,
      "days_supply": 30,
      "compound_code": "1"
    },
    "formulary": {
      "tier": 1,
      "status": "Preferred Generic",
      "prior_auth_required": false,
      "quantity_limit": null,
      "step_therapy": null
    },
    "dur_screening": {
      "alerts": [],
      "outcome": "Passed",
      "notes": "No drug interactions, appropriate for new T2DM"
    },
    "pricing": {
      "ingredient_cost": 8.50,
      "dispensing_fee": 2.50,
      "gross_amount_due": 11.00,
      "patient_pay": {
        "copay": 5.00,
        "coinsurance": 0.00,
        "deductible": 0.00,
        "total": 5.00
      },
      "plan_pay": 6.00,
      "u_and_c": 15.99
    },
    "refill_info": {
      "refills_authorized": 5,
      "refills_remaining": 5,
      "next_fill_date": "2024-12-27"
    }
  }
}
```

## Step 7: Clinical Trial Screening (TrialSim)

```
Screen Carlos for a Phase 3 diabetes/cardiovascular outcomes trial:
- Trial: GLP1-CVOT-001 (from our clinical-trial-protocol example)
- Evaluate against inclusion/exclusion criteria
- Generate screening assessment
```

### Trial Screening Results

```json
{
  "trial_screening": {
    "trial_id": "GLP1-CVOT-001",
    "trial_title": "Cardiovascular Outcomes with GLP-1 RA in T2DM",
    "candidate": {
      "patient_id": "P-2024-SD-00001",
      "name": "Carlos Mendez"
    },
    "screening_date": "2024-12-15",
    "screening_site": {
      "site_id": "US-CA-042",
      "name": "San Diego Clinical Research Center"
    },
    "eligibility_assessment": {
      "overall_status": "SCREEN_FAILURE",
      "inclusion_criteria": [
        {"criterion": "Age ≥50 years", "met": true, "value": "52 years"},
        {"criterion": "T2DM diagnosis", "met": true, "value": "Diagnosed 2024-11-15"},
        {"criterion": "HbA1c 7.0-10.5%", "met": true, "value": "8.2%"},
        {"criterion": "Established CVD", "met": false, "value": "No prior CV events", "reason": "SCREEN_FAILURE"}
      ],
      "exclusion_criteria": [
        {"criterion": "eGFR <30", "met": false, "value": "eGFR 85"},
        {"criterion": "History of pancreatitis", "met": false},
        {"criterion": "MTC/MEN2 history", "met": false},
        {"criterion": "Current GLP-1 RA use", "met": false}
      ],
      "failure_reason": "Does not meet inclusion criterion: established cardiovascular disease",
      "recommendation": "Patient may be eligible for trials targeting newly diagnosed T2DM without CVD requirement"
    },
    "alternative_trials": [
      {
        "trial_id": "MET-FIRST-002",
        "title": "Metformin First-Line Therapy Optimization",
        "inclusion_match": "High",
        "status": "Recruiting"
      },
      {
        "trial_id": "DPP4-LIFESTYLE-001",
        "title": "DPP4 Inhibitor with Lifestyle Intervention",
        "inclusion_match": "Medium",
        "status": "Recruiting"
      }
    ]
  }
}
```

## Step 8: Generate Complete Data Package

```
Export the complete integrated dataset for Carlos Mendez:
1. FHIR Bundle (Patient, Encounters, Claims, MedicationRequests)
2. X12 837P (Professional claim)
3. NCPDP D.0 (Pharmacy claim)
4. CSV flat files for analytics
```

### Export Summary

```json
{
  "data_package": {
    "patient_id": "P-2024-SD-00001",
    "generated_date": "2024-12-15T14:30:00-08:00",
    "exports": {
      "fhir": {
        "format": "FHIR R4 Bundle",
        "file": "carlos_mendez_fhir_bundle.json",
        "resources": {
          "Patient": 1,
          "Encounter": 1,
          "Condition": 3,
          "MedicationRequest": 2,
          "Observation": 8,
          "DiagnosticReport": 1,
          "Claim": 1,
          "ExplanationOfBenefit": 1,
          "Coverage": 1
        }
      },
      "x12": {
        "format": "X12 837P",
        "file": "CLM-2024-12-001584.edi",
        "transaction_set": "837",
        "version": "005010X222A1"
      },
      "ncpdp": {
        "format": "NCPDP D.0",
        "file": "RX-2024-12-00892341.ncpdp",
        "transaction_type": "B1",
        "version": "D.0"
      },
      "analytics": {
        "format": "CSV",
        "files": [
          "patient_demographics.csv",
          "clinical_encounters.csv",
          "diagnoses.csv",
          "procedures.csv",
          "medications.csv",
          "medical_claims.csv",
          "pharmacy_claims.csv"
        ]
      }
    },
    "data_quality": {
      "completeness": 100,
      "cross_product_linkage": "Verified",
      "code_validation": "Passed",
      "format_compliance": "Passed"
    }
  }
}
```

## Pipeline Summary

| Step | Product | Input | Output |
|------|---------|-------|--------|
| 1 | PopulationSim | Geography query | Population health context |
| 2 | PatientSim | Cohort criteria | Patient profile |
| 3 | NetworkSim | Insurance + specialty | Provider selection |
| 4 | PatientSim | Provider + patient | Clinical encounter |
| 5 | MemberSim | Encounter data | Processed claim |
| 6 | RxMemberSim | Prescription | Pharmacy claim |
| 7 | TrialSim | Patient profile | Screening assessment |
| 8 | All | Complete data | Multi-format export |

## Key Integration Points

1. **Person → Patient → Member**: SSN-based correlation (612-45-8932)
2. **Provider Consistency**: NPI 1234567890 used across clinical and claims
3. **Diagnosis Flow**: E11.9 from encounter to claims to DUR
4. **Medication Continuity**: Prescription from encounter to pharmacy claim
5. **Geographic Context**: Census tract informs population health patterns

## Related Resources

- [Cross-Product Guide](../docs/guides/cross-product-guide.md)
- [State Management Guide](../docs/guides/state-management-guide.md)
- [Output Formats Reference](../docs/reference/output-formats.md)
- [All Product Guides](../docs/guides/)
