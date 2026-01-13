# TrialSim Guide

Generate realistic synthetic clinical trial data through natural conversation.

---

## Overview

TrialSim creates clinical trial data with:

- **Protocols** - Trial design, arms, visit schedules
- **Sites** - Investigator sites with activation status
- **Subjects** - Enrollment, randomization, demographics
- **Visits** - Scheduled and unscheduled visit records
- **Adverse Events** - AEs with MedDRA coding and CTCAE grading
- **Exposures** - Drug administration and compliance
- **Labs & Vitals** - Safety monitoring data
- **Medical History** - Prior conditions and concomitant meds

**Output Formats:** CDISC SDTM, CDISC ADaM, JSON, CSV

---

## Quick Start

Generate your first clinical trial:

```
healthsim › Generate a Phase 3 oncology trial with 50 subjects

✓ Created trial with 50 subjects

  Protocol:     ONCO-2026-001
  Phase:        Phase 3
  Indication:   Non-Small Cell Lung Cancer
  
  Design:
    Arms:       Treatment (2:1 randomization) vs Placebo
    Duration:   52 weeks
    Sites:      5 active sites
  
  Subjects:     50 enrolled
    Screening:  0
    Randomized: 48
    Completed:  2
  
  Adverse Events:  127 total
    Serious:       8
    Grade 3+:      15
```

---

## Common Scenarios

### Trial Design

Create trials by phase and therapeutic area:

```
Generate a Phase 1 dose-escalation oncology trial
Create a Phase 2 proof-of-concept diabetes trial
Generate a Phase 3 pivotal cardiovascular outcomes trial
Create a Phase 4 post-marketing safety study
```

### Subject Enrollment

Control enrollment scenarios:

```
Generate 100 subjects across 10 sites
Create subjects with 30% screen failure rate
Generate subjects with varied demographic distribution
Create subjects enrolled over 6 months
```

### Adverse Events

Generate safety data:

```
Generate adverse events for this trial
Create a serious adverse event (SAE)
Generate a SUSAR (Suspected Unexpected Serious Adverse Reaction)
Create adverse events with dose modifications
```

---

## Trial Phases

### Phase 1 - Dose Escalation

```
Generate a Phase 1 3+3 dose escalation trial
Create a Phase 1 trial with 4 dose levels
Generate first-in-human safety data
```

Features:
- Dose cohorts (3+3, accelerated titration)
- DLT (Dose Limiting Toxicity) assessment
- MTD (Maximum Tolerated Dose) determination
- PK sampling schedules

### Phase 2 - Proof of Concept

```
Generate a Phase 2a exploratory efficacy trial
Create a Phase 2b dose-ranging study
Generate a biomarker-driven Phase 2 trial
```

Features:
- Multiple dose arms
- Efficacy signal detection
- Biomarker endpoints
- Futility analysis

### Phase 3 - Pivotal

```
Generate a Phase 3 registration trial
Create a pivotal trial with interim analysis
Generate a non-inferiority trial
Create a superiority trial with co-primary endpoints
```

Features:
- Large enrollment (hundreds to thousands)
- Primary and secondary endpoints
- Subgroup analyses
- Regulatory submission quality

---

## CDISC Standards

### SDTM Domains

TrialSim generates these SDTM domains:

| Domain | Description |
|--------|-------------|
| **DM** | Demographics |
| **DS** | Disposition (enrollment, completion, withdrawal) |
| **AE** | Adverse Events |
| **CM** | Concomitant Medications |
| **EX** | Exposure |
| **LB** | Laboratory Test Results |
| **VS** | Vital Signs |
| **MH** | Medical History |
| **IE** | Inclusion/Exclusion |
| **SV** | Subject Visits |

### Generating SDTM

```
Generate this trial as SDTM
Export subjects in SDTM DM domain format
Generate SDTM AE domain for all adverse events
Create complete SDTM submission package
```

### ADaM Datasets

Analysis-ready datasets:

| Dataset | Description |
|---------|-------------|
| **ADSL** | Subject-Level Analysis |
| **ADAE** | Adverse Event Analysis |
| **ADLB** | Laboratory Analysis |
| **ADVS** | Vital Signs Analysis |
| **ADEFF** | Efficacy Analysis |
| **ADTTE** | Time-to-Event Analysis |

### Generating ADaM

```
Generate ADaM ADSL for this trial
Create ADAE with treatment-emergent flag
Generate ADTTE for survival analysis
Export complete ADaM package
```

---

## Adverse Events

### MedDRA Coding

All adverse events are coded with MedDRA:

```
Generate adverse events with MedDRA PT and SOC codes
Create AEs grouped by System Organ Class
Generate a "Nausea" AE with proper MedDRA hierarchy
```

MedDRA Hierarchy:
- SOC (System Organ Class)
- HLGT (High Level Group Term)
- HLT (High Level Term)
- PT (Preferred Term)
- LLT (Lowest Level Term)

### CTCAE Grading

Severity grading per CTCAE:

| Grade | Severity | Description |
|-------|----------|-------------|
| 1 | Mild | Asymptomatic or mild symptoms |
| 2 | Moderate | Moderate; limiting instrumental ADL |
| 3 | Severe | Severe; limiting self-care ADL |
| 4 | Life-threatening | Life-threatening consequences |
| 5 | Death | Death related to AE |

### AE Scenarios

```
Generate Grade 3 neutropenia adverse event
Create a serious adverse event requiring hospitalization
Generate treatment-related AEs with dose modifications
Create adverse events leading to study discontinuation
```

### Causality Assessment

```
Generate AEs with causality assessment
Create an AE definitely related to study drug
Generate an AE with unlikely causality
```

---

## Subject Data

### Demographics (DM)

```
Generate diverse subject demographics
Create subjects with specific age distribution (55-75 years)
Generate subjects with geographic diversity
```

### Disposition (DS)

```
Generate subjects with various disposition statuses
Create a screen failure scenario
Generate an early termination due to AE
Create a lost to follow-up subject
```

Subject statuses:
- SCREENING
- SCREEN_FAILED
- ENROLLED
- RANDOMIZED
- ON_TREATMENT
- COMPLETED
- WITHDRAWN
- LOST_TO_FOLLOWUP

### Medical History (MH)

```
Generate subjects with relevant medical history
Create subjects with cardiovascular comorbidities
Generate medical history matching inclusion criteria
```

---

## Safety Data

### Vital Signs (VS)

```
Generate vital sign measurements for all visits
Create abnormal vital signs triggering safety review
Generate blood pressure trends over treatment period
```

Parameters: SYSBP, DIABP, PULSE, TEMP, RESP, WEIGHT, HEIGHT, BMI

### Labs (LB)

```
Generate laboratory results for safety monitoring
Create liver function test abnormalities
Generate hematology labs showing neutropenia
Create labs with CTCAE grading
```

Categories: Hematology, Chemistry, Urinalysis, Coagulation, Immunology

### Concomitant Medications (CM)

```
Generate concomitant medication records
Create prior and concomitant medication history
Generate rescue medication usage
```

---

## Therapeutic Areas

### Oncology

```
Generate a breast cancer trial with RECIST endpoints
Create a lung cancer trial with PFS primary endpoint
Generate an immunotherapy combination trial
Create a trial with tumor marker endpoints
```

Oncology features:
- RECIST response criteria
- Tumor measurements
- Biomarker data (PD-L1, EGFR, etc.)
- Survival endpoints

### Cardiovascular

```
Generate a heart failure outcomes trial
Create a MACE endpoint cardiovascular trial
Generate a lipid-lowering trial
```

CV features:
- MACE (Major Adverse Cardiovascular Events)
- CV death, MI, stroke endpoints
- Lipid panels
- Echo/imaging data

### Diabetes/Metabolic

```
Generate a Type 2 diabetes HbA1c trial
Create a weight loss trial
Generate a NASH/NAFLD trial
```

Metabolic features:
- HbA1c change from baseline
- Weight/BMI tracking
- Metabolic panels
- Liver function monitoring

### Immunology

```
Generate a rheumatoid arthritis trial
Create an inflammatory bowel disease trial
Generate a psoriasis trial with PASI scores
```

---

## Visit Schedules

### Standard Visit Types

```
Generate a trial with screening, baseline, and weekly visits
Create an 8-week treatment period with follow-up
Generate protocol-specified visit windows
```

Visit types:
- SCREENING
- BASELINE
- RANDOMIZATION
- SCHEDULED (Week 1, Week 2, etc.)
- UNSCHEDULED
- EARLY_TERMINATION
- FOLLOW_UP
- END_OF_STUDY

### Visit Compliance

```
Generate visits with 90% compliance rate
Create subjects with missed visits
Generate unscheduled safety visits
```

---

## Output Formats

### CDISC SDTM

```
Generate as CDISC SDTM
Export SDTM domains as XPT files
Generate SDTM with define.xml
```

Compliant with CDISC SDTM IG 3.3

### CDISC ADaM

```
Generate as CDISC ADaM
Export ADaM datasets for FDA submission
Generate analysis-ready datasets
```

Compliant with CDISC ADaM IG 1.1

### JSON/CSV

```
Export trial data as JSON
Generate subjects as CSV
Export all domains as separate CSV files
```

---

## Tips & Best Practices

### Specify Trial Design Details

```
# Basic (works but generic)
Generate a clinical trial

# Better (realistic output)
Generate a Phase 3, double-blind, placebo-controlled trial
for moderate-to-severe rheumatoid arthritis, with 2:1 randomization
to active vs placebo, 300 subjects across 30 sites, 52-week treatment
period with 4-week follow-up, primary endpoint ACR20 at Week 24
```

### Use Therapeutic Context

```
Generate an oncology trial with appropriate safety monitoring
Create a cardiovascular trial with MACE adjudication
Generate an immunology trial with immunogenicity testing
```

### Request Specific SDTM Domains

```
Generate DM, AE, and EX domains for this trial
Create complete SDTM package with all required domains
Generate supplemental qualifiers for AE domain
```

---

## Related Resources

### Skills

- [phase3-pivotal.md](../../skills/trialsim/phase3-pivotal.md)
- [clinical-trials-domain.md](../../skills/trialsim/clinical-trials-domain.md)
- [recruitment-enrollment.md](../../skills/trialsim/recruitment-enrollment.md)

### Reference

- [Code Systems](../reference/code-systems.md) - MedDRA, CTCAE, CDISC CT
- [Output Formats](../reference/output-formats.md) - SDTM, ADaM specs
- [Data Models](../reference/data-models.md) - Trial data models

### Examples

- [Basic Trial Generation](../../examples/basic/trial-generation.md)
- [Oncology Trial](../../examples/intermediate/oncology-trial.md)
- [SDTM Export](../../examples/advanced/sdtm-export.md)

---

## Troubleshooting

### SDTM validation errors

Ensure complete data:
```
Generate a trial with all required SDTM domains populated
Include both DM and DS domains
```

### Missing MedDRA codes

Request coded AEs:
```
Generate adverse events with complete MedDRA coding
including PT, LLT, HLT, and SOC
```

### Inconsistent subject counts

Check enrollment flow:
```
Generate trial showing complete subject disposition
from screening through completion or withdrawal
```

See [Troubleshooting](../getting-started/troubleshooting.md) for more solutions.
