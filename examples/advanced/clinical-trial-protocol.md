# Advanced Example: Clinical Trial Protocol Generation

This example demonstrates generating a complete Phase 3 clinical trial dataset including protocol design, site setup, subject enrollment, visits, adverse events, and regulatory submissions.

## Scenario

Generate data for a Phase 3 cardiovascular outcomes trial (CVOT) studying a novel GLP-1 receptor agonist for type 2 diabetes with cardiovascular disease.

## Step 1: Protocol Design

```
Create a Phase 3 cardiovascular outcomes trial protocol for a GLP-1 receptor agonist:
- Indication: Type 2 diabetes with established cardiovascular disease
- Primary endpoint: Time to first MACE (CV death, non-fatal MI, non-fatal stroke)
- Key secondary: HbA1c change from baseline at Week 52
- Design: Randomized, double-blind, placebo-controlled, event-driven
- Target enrollment: 10,000 subjects
- Planned duration: 4 years median follow-up
- Key inclusion: HbA1c 7.0-10.5%, age ≥50 with CVD history
- Key exclusion: eGFR <30, history of pancreatitis, MTC/MEN2
```

### Expected Output

```json
{
  "protocol": {
    "protocol_id": "GLP1-CVOT-001",
    "phase": "3",
    "title": "A Randomized, Double-Blind, Placebo-Controlled Trial to Evaluate Cardiovascular Outcomes with Once-Weekly GLP1-RA in Subjects with Type 2 Diabetes and Established Cardiovascular Disease",
    "sponsor": "PharmaCorp Inc.",
    "therapeutic_area": "Cardiovascular/Metabolism",
    "indication": "Type 2 Diabetes Mellitus with Cardiovascular Disease",
    "design": {
      "type": "RANDOMIZED",
      "blinding": "DOUBLE_BLIND",
      "control": "PLACEBO",
      "allocation_ratio": "1:1",
      "stratification_factors": [
        "Geographic region",
        "Baseline HbA1c (<8.5% vs ≥8.5%)",
        "Prior CV event type"
      ]
    },
    "endpoints": {
      "primary": {
        "name": "Time to first MACE",
        "definition": "Composite of cardiovascular death, non-fatal myocardial infarction, or non-fatal stroke",
        "analysis": "Cox proportional hazards model",
        "hypothesis": "Non-inferiority (margin 1.3) followed by superiority"
      },
      "key_secondary": [
        {
          "name": "HbA1c change from baseline",
          "timepoint": "Week 52",
          "analysis": "MMRM"
        },
        {
          "name": "Body weight change",
          "timepoint": "Week 52",
          "analysis": "MMRM"
        }
      ]
    },
    "population": {
      "target_enrollment": 10000,
      "target_events": 1200,
      "inclusion_criteria": [
        "Age ≥50 years",
        "Diagnosed with type 2 diabetes mellitus",
        "HbA1c 7.0-10.5% at screening",
        "Established cardiovascular disease (prior MI, stroke, PAD, or CAD)"
      ],
      "exclusion_criteria": [
        "eGFR <30 mL/min/1.73m²",
        "History of pancreatitis",
        "Personal or family history of MTC or MEN2",
        "Current use of GLP-1 receptor agonist"
      ]
    },
    "duration": {
      "screening": "4 weeks",
      "treatment": "Event-driven, minimum 2 years",
      "follow_up": "30 days post last dose"
    }
  }
}
```

## Step 2: Site Network Setup

```
Generate 150 clinical trial sites across North America, Europe, and Asia-Pacific:
- North America: 60 sites (US 50, Canada 10)
- Europe: 50 sites (UK 15, Germany 15, France 10, Spain 10)
- Asia-Pacific: 40 sites (Japan 20, South Korea 10, Australia 10)
Include site capabilities, principal investigators, and enrollment targets.
```

### Expected Output (Sample Sites)

```json
{
  "sites": [
    {
      "site_id": "US-001",
      "name": "Cleveland Clinic Cardiovascular Research",
      "country": "USA",
      "region": "North America",
      "address": {
        "street": "9500 Euclid Avenue",
        "city": "Cleveland",
        "state": "OH",
        "postal_code": "44195"
      },
      "principal_investigator": {
        "name": "Dr. Sarah Chen",
        "credentials": "MD, FACC",
        "specialty": "Cardiology"
      },
      "enrollment_target": 80,
      "capabilities": ["ECG", "Echocardiography", "Central Lab", "24/7 AE reporting"],
      "irb_approval_date": "2024-03-15",
      "site_initiation_date": "2024-04-01"
    },
    {
      "site_id": "DE-001",
      "name": "Charité Universitätsmedizin Berlin",
      "country": "Germany",
      "region": "Europe",
      "address": {
        "street": "Charitéplatz 1",
        "city": "Berlin",
        "postal_code": "10117"
      },
      "principal_investigator": {
        "name": "Prof. Dr. Marcus Weber",
        "credentials": "MD, PhD",
        "specialty": "Endocrinology"
      },
      "enrollment_target": 65,
      "capabilities": ["ECG", "MRI", "Central Lab", "Biomarker analysis"],
      "ethics_approval_date": "2024-04-01",
      "site_initiation_date": "2024-05-15"
    }
  ]
}
```

## Step 3: Subject Enrollment Cohort

```
Generate 500 enrolled subjects for the first enrollment wave:
- Match inclusion/exclusion criteria
- Realistic demographic distribution by region
- Include baseline characteristics: HbA1c, weight, BP, lipids, eGFR
- Prior CV event history with dates
- Concomitant medications (diabetes, CV)
- Randomize 1:1 to active vs placebo
```

### Expected Output (Sample Subject)

```json
{
  "subjects": [
    {
      "subject_id": "GLP1-CVOT-001-US001-0001",
      "usubjid": "GLP1CVOT001.US001.0001",
      "site_id": "US-001",
      "demographics": {
        "age": 62,
        "sex": "M",
        "race": "WHITE",
        "ethnicity": "NOT HISPANIC OR LATINO",
        "country": "USA"
      },
      "randomization": {
        "date": "2024-06-15",
        "arm": "ACTIVE",
        "stratification": {
          "region": "North America",
          "baseline_hba1c": "<8.5%",
          "cv_event_type": "Prior MI"
        }
      },
      "baseline_characteristics": {
        "hba1c": 8.2,
        "weight_kg": 98.5,
        "height_cm": 178,
        "bmi": 31.1,
        "systolic_bp": 142,
        "diastolic_bp": 86,
        "ldl_cholesterol": 95,
        "hdl_cholesterol": 38,
        "triglycerides": 185,
        "egfr": 68,
        "diabetes_duration_years": 12
      },
      "cv_history": [
        {
          "event": "Myocardial Infarction",
          "date": "2021-03-22",
          "intervention": "PCI with stent placement"
        }
      ],
      "concomitant_medications": [
        {"name": "Metformin", "dose": "1000mg", "frequency": "BID", "indication": "T2DM"},
        {"name": "Atorvastatin", "dose": "80mg", "frequency": "QD", "indication": "Dyslipidemia"},
        {"name": "Aspirin", "dose": "81mg", "frequency": "QD", "indication": "CV prevention"},
        {"name": "Lisinopril", "dose": "20mg", "frequency": "QD", "indication": "Hypertension"}
      ]
    }
  ]
}
```

## Step 4: Visit Schedule and Assessments

```
Generate visit data for 50 subjects through Week 52:
- Screening, Randomization, Week 4, 12, 26, 39, 52
- Include vital signs, labs (HbA1c, lipids, renal panel), ECGs
- Efficacy assessments (HbA1c, weight)
- Safety labs and monitoring
- Study drug accountability
```

### Expected Output (Sample Visit)

```json
{
  "visits": [
    {
      "subject_id": "GLP1-CVOT-001-US001-0001",
      "visit_name": "Week 12",
      "visit_date": "2024-09-07",
      "visit_day": 84,
      "assessments": {
        "vital_signs": {
          "weight_kg": 95.2,
          "systolic_bp": 136,
          "diastolic_bp": 82,
          "heart_rate": 72
        },
        "laboratory": {
          "hba1c": 7.4,
          "fasting_glucose": 142,
          "ldl_cholesterol": 88,
          "egfr": 70,
          "alt": 28,
          "ast": 25,
          "lipase": 45
        },
        "ecg": {
          "performed": true,
          "hr": 74,
          "pr_interval": 168,
          "qrs_duration": 92,
          "qtcf": 418,
          "interpretation": "Normal sinus rhythm"
        }
      },
      "study_drug": {
        "dose_administered": "1.0mg",
        "compliance": 98,
        "injection_site": "Abdomen",
        "adverse_events_since_last_visit": []
      }
    }
  ]
}
```

## Step 5: Adverse Events and MACE Adjudication

```
Generate realistic adverse events for 200 subjects over 2 years:
- Common AEs: nausea, injection site reactions, hypoglycemia
- GI events typical for GLP-1 class
- Serious adverse events including MACE components
- Include MedDRA coding (PT, SOC)
- CTCAE grading where applicable
- Adjudicated MACE events for primary endpoint
```

### Expected Output (Sample AEs)

```json
{
  "adverse_events": [
    {
      "subject_id": "GLP1-CVOT-001-US001-0001",
      "ae_sequence": 1,
      "ae_term": "Nausea",
      "meddra_pt": "Nausea",
      "meddra_pt_code": "10028813",
      "meddra_soc": "Gastrointestinal disorders",
      "meddra_soc_code": "10017947",
      "start_date": "2024-06-18",
      "end_date": "2024-06-25",
      "severity": "MILD",
      "ctcae_grade": 1,
      "serious": false,
      "causality": "RELATED",
      "action_taken": "NONE",
      "outcome": "RECOVERED"
    },
    {
      "subject_id": "GLP1-CVOT-001-DE001-0042",
      "ae_sequence": 1,
      "ae_term": "Acute myocardial infarction",
      "meddra_pt": "Acute myocardial infarction",
      "meddra_pt_code": "10000891",
      "meddra_soc": "Cardiac disorders",
      "meddra_soc_code": "10007541",
      "start_date": "2025-08-14",
      "severity": "SEVERE",
      "ctcae_grade": 4,
      "serious": true,
      "sae_criteria": ["Life-threatening", "Hospitalization"],
      "causality": "NOT RELATED",
      "outcome": "RECOVERED WITH SEQUELAE",
      "adjudication": {
        "committee_review_date": "2025-09-01",
        "adjudicated_event": "NON-FATAL MI",
        "mace_component": true,
        "primary_endpoint_event": true
      }
    }
  ]
}
```

## Step 6: Export to CDISC SDTM

```
Export the trial data to CDISC SDTM format:
- DM (Demographics)
- DS (Disposition)
- AE (Adverse Events)
- CM (Concomitant Medications)
- EX (Exposure)
- LB (Laboratory)
- VS (Vital Signs)
- MH (Medical History)
- EG (ECG)
Include define.xml metadata
```

### Expected Output

SDTM datasets are generated as separate files:

```
sdtm/
├── dm.xpt          # Demographics
├── ds.xpt          # Disposition
├── ae.xpt          # Adverse Events
├── cm.xpt          # Concomitant Meds
├── ex.xpt          # Exposure
├── lb.xpt          # Laboratory
├── vs.xpt          # Vital Signs
├── mh.xpt          # Medical History
├── eg.xpt          # ECG
├── sv.xpt          # Subject Visits
├── define.xml      # Metadata
└── define2-0-0.xsl # Stylesheet
```

## Key Learnings

1. **Protocol-First Design**: Start with protocol to establish rules for all downstream data
2. **Regulatory Compliance**: CDISC SDTM ensures FDA/EMA submission readiness
3. **Realistic Event Rates**: AE frequencies and MACE rates match published trials
4. **Adjudication Workflow**: MACE events require independent adjudication
5. **Data Traceability**: USUBJID provides consistent subject identification

## Related Resources

- [TrialSim Guide](../docs/guides/trialsim-guide.md)
- [Phase 3 Pivotal Skill](../skills/trialsim/phase3-pivotal.md)
- [CDISC SDTM Reference](../docs/reference/output-formats.md#cdisc-sdtm)
- [MedDRA Coding Reference](../docs/reference/code-systems.md#meddra)
