# Cross-Product Integration Guide

Build realistic multi-domain healthcare scenarios by combining HealthSim products.

---

## Overview

Real healthcare data spans multiple systems. A single person might have:

- **EMR records** (PatientSim) - Clinical encounters, diagnoses, procedures
- **Health plan enrollment** (MemberSim) - Coverage, claims, payments
- **Pharmacy benefits** (RxMemberSim) - Prescriptions, fills, DUR alerts
- **Clinical trial participation** (TrialSim) - Study visits, assessments
- **Provider relationships** (NetworkSim) - Treating physicians, facilities

HealthSim's cross-product integration links these seamlessly using **identity correlation** (SSN as universal key).

---

## Quick Start

Generate a patient with linked claims:

```
healthsim › Generate a diabetic patient with recent office visit
            and create the associated professional claim
```

Output:
```
✓ Generated linked data across products

PATIENT (PatientSim):
  ID:        PAT-001
  Name:      Maria Santos
  SSN:       ***-**-6789
  
  Encounter: Office Visit (2025-01-10)
    • Diagnosis: E11.65 Type 2 DM with hyperglycemia
    • Procedure: 99214 Office visit
    • Provider: Dr. Sarah Chen, NPI 1234567890

MEMBER (MemberSim):
  ID:        MEM-123456
  SSN:       ***-**-6789 (linked to PAT-001)
  Plan:      BlueCross PPO

  Professional Claim: CLM-2025-0001
    • Service Date: 2025-01-10
    • Diagnosis: E11.65
    • Procedure: 99214
    • Billed: $185.00
    • Allowed: $142.00
    • Member Responsibility: $30.00 (copay)
```

---

## Identity Correlation

### How Linking Works

```
                    ┌─────────────────────────────────────────┐
                    │             PERSON (Root)               │
                    │  SSN: 123-45-6789 (Universal Key)       │
                    │  Name: Maria Santos                     │
                    │  DOB: 1968-05-22                        │
                    └─────────────────────┬───────────────────┘
                                          │
        ┌─────────────────┬───────────────┼───────────────┬─────────────────┐
        │                 │               │               │                 │
        ▼                 ▼               ▼               ▼                 ▼
┌───────────────┐ ┌───────────────┐ ┌───────────────┐ ┌───────────────┐ ┌───────────────┐
│   PATIENT     │ │    MEMBER     │ │  RX_MEMBER    │ │   SUBJECT     │ │   PROVIDERS   │
│  (PatientSim) │ │  (MemberSim)  │ │(RxMemberSim)  │ │  (TrialSim)   │ │ (NetworkSim)  │
│               │ │               │ │               │ │               │ │               │
│ MRN: PAT-001  │ │ ID: MEM-12345 │ │ ID: RX-12345  │ │ ID: SUBJ-042  │ │ NPI linked to │
│ SSN: *6789    │ │ SSN: *6789    │ │ SSN: *6789    │ │ SSN: *6789    │ │ encounters    │
└───────────────┘ └───────────────┘ └───────────────┘ └───────────────┘ └───────────────┘
```

**Key Principle**: SSN links Person entities across all products. When you generate linked data, HealthSim automatically maintains this correlation.

### Correlation Rules

| Field | Behavior | Notes |
|-------|----------|-------|
| SSN | Identical across linked entities | Primary correlator |
| Name | Consistent (may have minor variations) | "Maria" vs "Maria E." |
| DOB | Identical | Must match exactly |
| Gender | Identical | Must match exactly |
| Address | May differ (home vs work vs coverage) | Realistic variation |

---

## Common Multi-Domain Scenarios

### 1. Patient with Claims

Generate clinical data with corresponding payer data:

```
Generate a 58-year-old with Type 2 diabetes including:
- Recent A1C lab result (8.2%)
- Office visit encounter
- Linked professional claim
- Metformin prescription with pharmacy claim
```

This creates:

| Product | Generated Data |
|---------|----------------|
| PatientSim | Patient, Encounter, Lab, Prescription |
| MemberSim | Member, Professional Claim |
| RxMemberSim | RxMember, Pharmacy Claim |

### 2. Clinical Trial with Medical History

Generate a trial subject with pre-existing EMR data:

```
Create a clinical trial subject for a diabetes study:
- 5-year history of Type 2 diabetes in EMR
- Prior A1C values showing progression
- Current medications
- Enrolled in Phase 3 insulin trial
- Screening visit completed
```

This creates:

| Product | Generated Data |
|---------|----------------|
| PatientSim | Patient, Historical Encounters, Labs, Medications |
| TrialSim | Subject, Protocol, Screening Visit, Inclusion Criteria |

### 3. Hospitalization Episode

Generate a complete inpatient episode across systems:

```
Generate a heart failure patient with:
- ED presentation with acute decompensation
- 4-day inpatient admission
- Cardiology consult
- Echo procedure
- Facility claim (DRG-based)
- Professional claims for all providers
```

This creates:

| Product | Generated Data |
|---------|----------------|
| PatientSim | Patient, ED Encounter, Inpatient Encounter, Consult, Echo |
| MemberSim | Member, Facility Claim (DRG), Multiple Professional Claims |
| NetworkSim | Linked Providers (ED physician, hospitalist, cardiologist) |

### 4. Specialty Pharmacy Journey

Generate complex pharmacy data with clinical context:

```
Create a patient starting a specialty medication:
- Rheumatoid arthritis diagnosis
- Failed methotrexate (prior auth requirement)
- Humira prescription
- Prior authorization approval
- Specialty pharmacy fill with hub enrollment
- Medical claim for injection training
```

This creates:

| Product | Generated Data |
|---------|----------------|
| PatientSim | Patient, Diagnosis History, Failed Therapy, Prescription |
| RxMemberSim | RxMember, Prior Auth, Specialty Fill, Hub Enrollment |
| MemberSim | Member, Professional Claim (injection training) |

### 5. Population Cohort Study

Use real population data to design cohorts, then generate synthetic individuals:

```
Using PopulationSim data for San Diego County:
- Find census tracts with high diabetes prevalence (>15%)
- High social vulnerability (SVI > 0.75)
- Generate 50 patients matching this profile
- Add health plan enrollment for each
- Generate 6 months of utilization
```

This creates:

| Product | Generated Data |
|---------|----------------|
| PopulationSim | County/tract analysis (real data) |
| PatientSim | 50 Patients with appropriate demographics |
| MemberSim | 50 Members with 6 months of claims |

---

## Trigger Events

Certain clinical events automatically trigger generation in related products:

| Trigger Event | Source | Target | What Gets Generated |
|---------------|--------|--------|---------------------|
| Encounter created | PatientSim | MemberSim | Professional/Facility claim |
| Prescription written | PatientSim | RxMemberSim | Pharmacy claim |
| Procedure performed | PatientSim | MemberSim | Professional claim with CPT |
| Lab ordered | PatientSim | MemberSim | Lab claim (if outpatient) |
| Hospitalization | PatientSim | MemberSim | Facility + Professional claims |
| Trial visit | TrialSim | PatientSim | Linked encounter |
| Specialty fill | RxMemberSim | MemberSim | Pharmacy claim (integrated) |

### Requesting Linked Generation

Explicitly request cross-product data:

```
# Implicit (PatientSim only)
Generate an office visit for this patient

# Explicit (PatientSim + MemberSim)
Generate an office visit and the corresponding claim

# Full chain
Generate an encounter with all linked claims and pharmacy data
```

---

## Provider Linking (NPI)

Providers are linked using NPI rather than SSN:

```
Generate a cardiology encounter using a real San Diego cardiologist
```

HealthSim will:
1. Query NetworkSim for cardiologists in San Diego
2. Select an appropriate provider (real NPI from NPPES)
3. Link that NPI to the encounter
4. Use the same NPI on any generated claims

```
ENCOUNTER:
  Provider: Dr. Michael Torres
  NPI: 1234567890
  Specialty: Cardiology

PROFESSIONAL CLAIM:
  Rendering Provider NPI: 1234567890
  Billing Provider NPI: 9876543210 (practice)
```

---

## Cross-Product Queries

Query across linked entities:

```
Show all claims for patient PAT-001
```

```sql
SELECT c.claim_id, c.service_date, c.total_billed
FROM claims c
JOIN members m ON c.member_id = m.member_id
JOIN patients p ON m.ssn = p.ssn
WHERE p.id = 'PAT-001';
```

Find trial subjects with specific medical history:

```
Find subjects in trial ONCO-2025-001 with prior chemotherapy
```

```sql
SELECT s.usubjid, p.mrn, m.medication_name
FROM subjects s
JOIN patients p ON s.ssn = p.ssn
JOIN medications m ON p.id = m.patient_id
WHERE s.study_id = 'ONCO-2025-001'
  AND m.medication_class = 'Antineoplastic';
```

---

## Building Complex Cohorts

### Step-by-Step Approach

Build multi-domain cohorts incrementally:

```
Step 1: Generate base population
Generate 100 Medicare members over 65 in California

Step 2: Add clinical data
For each member, create a patient record with appropriate 
chronic conditions based on their age and risk score

Step 3: Add utilization
Generate 12 months of encounters and claims for each patient
matching their condition profile

Step 4: Add pharmacy
Generate pharmacy fills for all medications prescribed

Step 5: Select for trial
Identify 20 patients with HFrEF who might qualify for 
a heart failure clinical trial
```

### Maintaining Consistency

When building across products:

| Aspect | Ensure Consistency |
|--------|-------------------|
| Demographics | Same DOB, gender, name across all records |
| Dates | Claim dates match encounter dates |
| Codes | ICD-10 on claim matches diagnosis on encounter |
| Providers | NPI on claim matches encounter provider |
| Medications | Prescribed meds generate pharmacy claims |
| Dosing | Fill quantity matches prescription |

---

## Output Format Combinations

Export linked data in matching formats:

```
Export this patient's data as:
- FHIR Bundle (clinical data)
- X12 837P (professional claims)
- NCPDP D.0 (pharmacy claims)
```

Or unified exports:

```
Export the complete cohort as CSV files with:
- patients.csv
- encounters.csv
- claims.csv
- pharmacy_claims.csv
- All linked by patient_id/member_id correlation
```

---

## Tips & Best Practices

### Be Explicit About Linking

Tell HealthSim what you want linked:

```
# May not generate claims
Generate an office visit

# Will generate linked claims
Generate an office visit with professional claim

# Full linkage
Generate an office visit with professional claim,
any ordered labs with lab claims, and prescriptions
with pharmacy claims
```

### Use Real Provider Data

For realistic claims, use real NPIs:

```
Generate using a real endocrinologist from San Diego
```

### Validate Consistency

After generating linked data:

```
Validate that all claims match their source encounters
Check that pharmacy claims match prescriptions
Verify SSN correlation across all entities
```

### Build Incrementally

Don't try to generate everything at once:

```
1. Create the patient with conditions
2. Verify the clinical data looks correct
3. Add the health plan enrollment
4. Generate encounters over time
5. Add corresponding claims
6. Review the complete picture
```

---

## Related Resources

### Skills

- [Identity Correlation](../../skills/common/identity-correlation.md) - SSN linking patterns
- [State Management](../../skills/common/state-management.md) - Cohort persistence
- [Cross-Domain Sync](../../skills/generation/executors/cross-domain-sync.md) - Trigger automation

### Product Guides

- [PatientSim Guide](patientsim-guide.md) - Clinical data generation
- [MemberSim Guide](membersim-guide.md) - Claims data generation
- [RxMemberSim Guide](rxmembersim-guide.md) - Pharmacy data generation
- [TrialSim Guide](trialsim-guide.md) - Clinical trial data
- [PopulationSim Guide](populationsim-guide.md) - Population health queries
- [NetworkSim Guide](networksim-guide.md) - Provider data

### Reference

- [Data Models](../reference/data-models.md) - Entity relationships
- [Code Systems](../reference/code-systems.md) - Standard codes

---

## Troubleshooting

### Claims don't match encounters

Ensure you requested linked generation:
```
Generate the encounter AND the corresponding claim
```

Check date consistency:
```
Verify the claim service date matches the encounter date
```

### SSN mismatch across products

All linked entities must share SSN:
```
Show the SSN for patient PAT-001 and member MEM-123456
```

If mismatched, regenerate with explicit linking:
```
Generate a member record for patient PAT-001
```

### Provider NPI not on claim

Specify provider linking:
```
Generate the claim using the same provider from the encounter
```

### Pharmacy claims missing

Prescriptions need explicit pharmacy claim generation:
```
Generate the prescription AND the pharmacy claim for the fill
```

### Can't find linked records

Query using SSN correlation:
```
Find all records for SSN ending in 6789 across all products
```

See [Troubleshooting](../getting-started/troubleshooting.md) for more solutions.
