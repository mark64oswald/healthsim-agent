# Claims Generation Example

Learn to generate professional and facility claims with HealthSim.

---

## Goal

Create realistic healthcare claims with proper coding, pricing, and adjudication. You'll learn:

- Professional (837P) claims generation
- Facility (837I) claims generation
- Claim line details and modifiers
- Payment and adjudication

---

## Prerequisites

- HealthSim installed and running
- Basic familiarity with [Patient Generation](patient-generation.md)
- ~10 minutes

---

## Steps

### Step 1: Create a Member

```
healthsim › Create a member with Blue Cross PPO coverage in Dallas
```

Expected output:
```
✓ Generated member

Member: MBR-001
  Name: James Rodriguez
  DOB: 1978-03-15 (47 years)
  Location: Dallas, TX 75201
  
Coverage:
  Plan: Blue Cross Blue Shield PPO
  Member ID: BCB892745632
  Group: Large Employer Group
  Effective: 2025-01-01
  
Benefits:
  Deductible: $500 (Individual) / $1,500 (Family)
  OOP Max: $3,000 / $9,000
  Office Visit Copay: $25
  Specialist Copay: $50
```

### Step 2: Generate a Professional Claim

```
healthsim › Generate a professional claim for an office visit with the PCP for 
            back pain evaluation
```

Expected output:
```
✓ Generated professional claim

Claim: CLM-2026-000001
  Type: Professional (837P)
  Member: MBR-001 (James Rodriguez)
  Date of Service: 2026-01-10
  Provider: Dr. Michael Lee, MD (Family Medicine)
  NPI: 1234567890
  
Service Lines:
  1. 99213 - Office visit, established patient (15 min)
     ICD-10: M54.5 (Low back pain)
     Billed: $125.00
     Allowed: $95.00
     
Totals:
  Billed Amount: $125.00
  Allowed Amount: $95.00
  Deductible Applied: $70.00
  Copay: $25.00
  Plan Paid: $0.00
  Member Responsibility: $95.00
```

### Step 3: Add Follow-up with Specialist

```
healthsim › Generate a claim for orthopedic specialist visit with X-rays
```

Expected output:
```
✓ Generated professional claim

Claim: CLM-2026-000002
  Type: Professional (837P)
  Provider: Dr. Amanda Foster, DO (Orthopedics)
  NPI: 2345678901
  Date of Service: 2026-01-15
  
Service Lines:
  1. 99203 - Office visit, new patient (30 min)
     ICD-10: M54.5 (Low back pain)
     Billed: $225.00
     Allowed: $175.00

  2. 72100 - X-ray lumbar spine, 2-3 views
     ICD-10: M54.5 (Low back pain)
     Billed: $185.00
     Allowed: $125.00

Totals:
  Billed Amount: $410.00
  Allowed Amount: $300.00
  Deductible Applied: $300.00 (deductible now met)
  Copay: $0.00
  Plan Paid: $0.00
  Member Responsibility: $300.00
```

### Step 4: Generate a Facility Claim

```
healthsim › Generate a facility claim for an outpatient MRI of the lumbar spine
```

Expected output:
```
✓ Generated facility claim

Claim: CLM-2026-000003
  Type: Facility (837I)
  Facility: Dallas Regional Medical Center
  NPI: 3456789012
  Date of Service: 2026-01-20
  Bill Type: 131 (Hospital Outpatient)
  
Revenue Codes & Services:
  1. 0610 - MRI (Technical Component)
     HCPCS: 72148 - MRI lumbar spine w/o contrast
     ICD-10: M54.5 (Low back pain)
     Billed: $2,400.00
     Allowed: $850.00

Totals:
  Billed Amount: $2,400.00
  Allowed Amount: $850.00
  Deductible: $0.00 (met)
  Coinsurance (20%): $170.00
  Plan Paid: $680.00
  Member Responsibility: $170.00
```

### Step 5: View Claims Summary

```
healthsim › /status
```

```
Current Session
═══════════════════════════════════════
Members:      1
Claims:       3 (2 Professional, 1 Facility)

Financial Summary:
  Total Billed:    $2,935.00
  Total Allowed:   $1,245.00
  Plan Paid:       $680.00
  Member Paid:     $565.00
═══════════════════════════════════════
```

### Step 6: Export to X12

```
healthsim › Export claims as X12 837
```

```
✓ Exported X12 837

Professional Claims (837P): ./exports/837P-20260112.edi
Facility Claims (837I): ./exports/837I-20260112.edi
Total Transactions: 3
```

---

## What You Created

| Entity | Count | Details |
|--------|-------|---------|
| Member | 1 | PPO coverage |
| Professional Claims | 2 | Office visits, X-ray |
| Facility Claims | 1 | Outpatient MRI |
| Service Lines | 4 | Coded with ICD-10/CPT |

---

## Variations

### Emergency Room Visit

```
healthsim › Generate ER claims for chest pain workup including EKG and troponin
```

### Surgical Procedure

```
healthsim › Generate claims for an outpatient knee arthroscopy with anesthesia
```

### Preventive Care

```
healthsim › Generate claims for an annual wellness visit with routine labs
```

### Multiple Members

```
healthsim › Generate a family of 4 with various claims for a month of healthcare
```

---

## Claim Scenarios

### Pre-authorization Required

```
healthsim › Generate a claim for a procedure requiring prior auth that was approved
```

### Out-of-Network

```
healthsim › Generate an out-of-network claim with balance billing
```

### Coordination of Benefits

```
healthsim › Create a member with primary and secondary coverage, then generate 
            claims showing COB
```

### Denied Claim

```
healthsim › Generate a claim that gets denied for lack of medical necessity
```

---

## Understanding Claim Components

### Professional Claim (837P) Elements

| Field | Description | Example |
|-------|-------------|---------|
| CPT Code | Procedure performed | 99213 |
| ICD-10 | Diagnosis code | M54.5 |
| Modifier | Service modifier | 25 (separate E/M) |
| Place of Service | Where performed | 11 (Office) |
| NPI | Provider identifier | 1234567890 |

### Facility Claim (837I) Elements

| Field | Description | Example |
|-------|-------------|---------|
| Revenue Code | Type of service | 0610 (MRI) |
| HCPCS | Procedure code | 72148 |
| Bill Type | Facility type | 131 (Outpatient) |
| Admit/Discharge | Dates of service | 01/20/2026 |

---

## Troubleshooting

**Claim amounts seem off?**
- Allowed amounts vary by plan type and region
- Specify the plan type for accurate pricing

**Missing service lines?**
- Be specific about what services were performed
- Include modifiers when needed (e.g., "bilateral")

**Wrong place of service?**
- Specify location: "in the office", "at the hospital", "in the ER"

---

## Next Steps

- [Pharmacy Claims](pharmacy-claims.md) - Add prescription fills
- [Denial Scenarios](../intermediate/denial-scenarios.md) - Error handling
- [Batch Generation](../advanced/batch-generation.md) - Volume testing

---

## Related

- [MemberSim Guide](../../docs/guides/membersim-guide.md)
- [Output Formats Reference](../../docs/reference/output-formats.md)
- [Code Systems Reference](../../docs/reference/code-systems.md)
