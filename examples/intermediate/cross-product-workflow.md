# Cross-Product Workflow Example

Generate linked data across multiple HealthSim domains.

---

## Goal

Create a complete patient journey spanning clinical, claims, and pharmacy domains. You'll learn:

- Identity correlation across products
- Event timing and sequencing  
- Multi-domain exports
- Realistic healthcare workflows

---

## Prerequisites

- Completed [Patient Generation](../basic/patient-generation.md)
- Completed [Claims Generation](../basic/claims-generation.md)
- Completed [Pharmacy Claims](../basic/pharmacy-claims.md)
- ~15 minutes

---

## Scenario: New Diabetes Diagnosis

A patient gets diagnosed with diabetes, sees specialists, starts medications, and has ongoing care.

### Step 1: Create the Person

```
healthsim › Create a 52-year-old man named Michael Torres in Austin, TX. 
            He should have both medical and pharmacy coverage with United Healthcare.
```

Expected output:
```
✓ Generated Person with linked identities

Person: Michael Torres
  SSN: XXX-XX-4721 (correlation key)
  DOB: 1973-06-18 (52 years)
  Location: Austin, TX 78701

Linked Identities:
  Patient: PAT-001 (clinical records)
  Member: MBR-001 (medical claims)
  RxMember: RXM-001 (pharmacy claims)
  
Medical Coverage:
  Plan: UnitedHealthcare Choice Plus
  Member ID: U87234561
  
Pharmacy Coverage:
  PBM: OptumRx
  RxBIN: 610014
```

### Step 2: Initial PCP Visit (Day 0)

```
healthsim › Michael visits his PCP for fatigue and frequent urination. 
            Generate the clinical encounter and professional claim.
```

Expected output:
```
✓ Generated linked encounter and claim

Clinical Record (PatientSim):
  Encounter: ENC-001
  Type: Office Visit
  Date: 2026-01-10
  Chief Complaint: Fatigue, polyuria
  Provider: Dr. Lisa Park, MD (Family Medicine)
  
  Assessment:
  • Suspected type 2 diabetes mellitus
  • Fatigue
  
  Plan:
  • Order fasting glucose, HbA1c, CMP
  • Return for results in 1 week

Claim (MemberSim):
  Claim: CLM-2026-000001
  CPT: 99214 (Office visit, established)
  ICD-10: R53.83 (Fatigue), R35.0 (Frequency of urination)
  Billed: $175.00 → Allowed: $135.00
  Member Pays: $25.00 (copay)
```

### Step 3: Lab Work (Day 1)

```
healthsim › Generate lab results showing elevated glucose (fasting 185) and 
            HbA1c of 8.2%. Include the lab claim.
```

Expected output:
```
✓ Generated lab results and facility claim

Lab Results (PatientSim):
  Order: LAB-001
  Collection Date: 2026-01-11
  Facility: Quest Diagnostics
  
  Results:
  • Fasting Glucose: 185 mg/dL (H) [ref: 70-100]
  • HbA1c: 8.2% (H) [ref: <5.7%]
  • Creatinine: 1.0 mg/dL [ref: 0.7-1.3]
  • eGFR: 92 mL/min [ref: >60]
  
  Interpretation: Results consistent with diabetes mellitus

Claim (MemberSim):
  Claim: CLM-2026-000002
  Type: Professional
  CPT: 82947 (Glucose), 83036 (HbA1c), 80053 (CMP)
  Billed: $245.00 → Allowed: $85.00
  Member Pays: $85.00 (deductible)
```

### Step 4: Diagnosis Visit (Day 7)

```
healthsim › Michael returns to discuss results. He's diagnosed with type 2 
            diabetes and started on metformin. Generate encounter, claim, 
            and prescription.
```

Expected output:
```
✓ Generated linked encounter, claim, and pharmacy claim

Clinical Record (PatientSim):
  Encounter: ENC-002
  Date: 2026-01-17
  
  Assessment:
  • Type 2 diabetes mellitus, newly diagnosed (E11.65)
  • HbA1c 8.2% - above target
  
  Plan:
  • Start metformin 500mg BID, titrate to 1000mg BID
  • Diabetes education referral
  • Home glucose monitoring
  • Follow-up 3 months

Claim (MemberSim):
  Claim: CLM-2026-000003
  CPT: 99214, 99490 (Chronic care management setup)
  ICD-10: E11.65 (T2DM with hyperglycemia)
  Billed: $285.00 → Allowed: $220.00
  Member Pays: $25.00 (copay)

Pharmacy Claim (RxMemberSim):
  Rx: RX-2026-000001
  Drug: Metformin HCl 500mg (titration pack)
  NDC: 00093-7212-01
  Qty: 90 tablets, 30 days supply
  Plan Pays: $2.00
  Patient Copay: $10.00
```

### Step 5: Diabetes Education (Day 14)

```
healthsim › Michael attends diabetes self-management education. 
            Generate the encounter and claim.
```

Expected output:
```
✓ Generated education encounter and claim

Clinical Record (PatientSim):
  Encounter: ENC-003
  Type: Diabetes Education (DSME)
  Date: 2026-01-24
  Duration: 60 minutes
  Educator: Sarah Chen, RD, CDCES
  
  Topics Covered:
  • Carbohydrate counting
  • Blood glucose monitoring
  • Medication adherence
  • Hypoglycemia recognition
  
  Patient Education Level: Beginner → Intermediate

Claim (MemberSim):
  Claim: CLM-2026-000004
  CPT: 98960 (DSME, individual, 30 min) x2
  ICD-10: E11.65
  Billed: $180.00 → Allowed: $140.00
  Member Pays: $0.00 (covered preventive)
```

### Step 6: Medication Titration (Day 30)

```
healthsim › Michael tolerates metformin well. Increase to 1000mg BID 
            and fill 90-day supply.
```

Expected output:
```
✓ Generated pharmacy claim

Pharmacy Claim (RxMemberSim):
  Rx: RX-2026-000002
  Drug: Metformin HCl 1000mg Tablet
  NDC: 00093-7214-01
  Qty: 180 tablets, 90 days supply
  Refills: 3 remaining
  
  Pricing:
  Ingredient Cost: $14.50
  Plan Pays: $4.50
  Patient Copay: $10.00 (generic tier)
  
Note: Previous fill (RX-2026-000001) marked as titration
```

### Step 7: Three-Month Follow-up (Day 90)

```
healthsim › Generate Michael's 3-month diabetes follow-up with improved 
            HbA1c of 7.1%, and add statin for cardiovascular prevention.
```

Expected output:
```
✓ Generated follow-up with labs and new prescription

Clinical Record (PatientSim):
  Encounter: ENC-004
  Date: 2026-04-10
  
  Results:
  • HbA1c: 7.1% (improved from 8.2%)
  • Weight: 195 lbs (down 8 lbs)
  • BP: 128/82
  
  Assessment:
  • T2DM - improved on metformin
  • Add statin per ADA guidelines (10-year ASCVD risk)
  
  Plan:
  • Continue metformin 1000mg BID
  • Start atorvastatin 20mg daily
  • Continue quarterly follow-up

Claim (MemberSim):
  Claim: CLM-2026-000005
  CPT: 99214, 83036 (HbA1c)
  Billed: $275.00 → Allowed: $195.00
  
Pharmacy Claim (RxMemberSim):
  Rx: RX-2026-000003
  Drug: Atorvastatin 20mg Tablet
  NDC: 00378-3952-77
  Qty: 90 tablets
  Patient Copay: $10.00
```

### Step 8: View Complete Journey

```
healthsim › /status
```

```
Current Session - Michael Torres Journey
═══════════════════════════════════════════════
Person: Michael Torres (SSN: XXX-XX-4721)

Clinical (PatientSim):
  Encounters:     4
  Conditions:     1 (Type 2 Diabetes)
  Observations:   8 (Labs, Vitals)
  
Claims (MemberSim):
  Professional:   5
  Total Billed:   $1,160.00
  Total Allowed:  $775.00
  Patient Paid:   $160.00
  
Pharmacy (RxMemberSim):
  Prescriptions:  3
  Total Rx Cost:  $45.00
  Patient Copays: $30.00
  
Timeline:
  Day 0:  Initial PCP visit
  Day 1:  Lab work
  Day 7:  Diagnosis, start metformin
  Day 14: Diabetes education
  Day 30: Metformin titration
  Day 90: Follow-up, add statin
═══════════════════════════════════════════════
```

### Step 9: Export All Domains

```
healthsim › Export complete journey - FHIR for clinical, X12 for claims, NCPDP for pharmacy
```

```
✓ Exported multi-format package

Clinical (PatientSim):
  → ./exports/fhir-bundle-michael-torres.json
  Resources: 18 (Patient, Encounters, Observations, Conditions)

Claims (MemberSim):
  → ./exports/837p-michael-torres.edi
  Transactions: 5 professional claims

Pharmacy (RxMemberSim):
  → ./exports/ncpdp-michael-torres.dat
  Transactions: 3 pharmacy claims

Correlation Report:
  → ./exports/correlation-report.json
  Links all records via SSN XXX-XX-4721
```

---

## What You Created

| Domain | Entities | Key Data |
|--------|----------|----------|
| PatientSim | 4 encounters, 1 condition | Clinical documentation |
| MemberSim | 5 claims | $775 allowed |
| RxMemberSim | 3 prescriptions | 3 medications |
| **Linked Via** | SSN XXX-XX-4721 | Complete journey |

---

## Key Concepts

### Identity Correlation

All products share the same Person base:
```
Person (SSN: XXX-XX-4721)
  ├── Patient (PAT-001)  → Clinical records
  ├── Member (MBR-001)   → Medical claims  
  └── RxMember (RXM-001) → Pharmacy claims
```

### Event Timing

Events flow naturally:
```
Day 0:  Encounter → Claim
Day 1:  Lab Order → Lab Results → Lab Claim
Day 7:  Encounter → Claim → Prescription → Rx Claim
```

### Domain Linking

```
Clinical Encounter (ENC-001)
  └── ICD-10: R53.83, R35.0
        └── Claim (CLM-2026-000001)
              └── Same ICD-10 codes
                    └── Same date of service
```

---

## Variations

### Acute Care Journey

```
healthsim › Create a patient who has a heart attack, is hospitalized, 
            discharged with new medications, and has cardiac rehab
```

### Chronic Disease Progression

```
healthsim › Generate 2 years of diabetes care showing progression 
            from diet-controlled to insulin-requiring
```

### Pregnancy Journey

```
healthsim › Create a complete prenatal journey from first OB visit 
            through delivery with all visits and claims
```

---

## Troubleshooting

**Records not linking?**
- Use the same person: "Add to Michael Torres"
- Check SSN correlation in /status

**Timeline gaps?**
- Specify dates: "On January 15th..."
- Use relative: "Two weeks later..."

**Missing claims for encounter?**
- Explicitly request: "Generate the claim for this visit"

---

## Related

- [Cross-Product Guide](../../docs/guides/cross-product-guide.md)
- [State Management Guide](../../docs/guides/state-management-guide.md)
- [Patient Generation Example](../basic/patient-generation.md)
