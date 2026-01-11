# MemberSim Guide

Generate realistic synthetic health plan member and claims data through natural conversation.

---

## Overview

MemberSim creates insurance/payer data including:

- **Members** - Enrollees with demographics and identifiers
- **Enrollment** - Coverage periods, plan types, benefit structures
- **Professional Claims** - Physician services (837P)
- **Facility Claims** - Hospital services with DRG (837I)
- **Adjudication** - Payment, denials, adjustments
- **Remittance** - 835 payment details

**Output Formats:** X12 837P, 837I, 835, 834, JSON, CSV

---

## Quick Start

Generate your first claims:

```
healthsim › Generate a professional claim for an office visit
```

Output:
```
✓ Added 1 claim

  Claim:     CLM-2026-000001
  Type:      Professional (837P)
  
  Member:    John Smith (MBR-12345)
  Coverage:  Commercial PPO
  
  Service:
    Date:     2025-12-10
    Provider: Dr. Sarah Johnson, MD (NPI: 1234567890)
    CPT:      99214 - Office visit, established patient
  
  Financials:
    Charges:   $185.00
    Allowed:   $142.50
    Copay:     $25.00
    Paid:      $117.50
  
  Status:    Paid
```

---

## Common Scenarios

### Member Enrollment

Generate members with coverage:

```
Generate a member with commercial PPO coverage
Create a family of 4 with employer-sponsored HMO
Generate a Medicare Advantage member
Generate a Medicaid member in Texas
```

Enrollment variations:

```
Generate a member who changed plans mid-year
Create a member with COBRA continuation
Generate a member with dual Medicare/Medicaid eligibility
```

### Professional Claims (837P)

Office visits:

```
Generate a professional claim for an E&M visit
Create a specialist consultation claim
Generate claims for a routine preventive visit
```

Procedures:

```
Generate a professional claim for minor surgery
Create a claim for diagnostic imaging interpretation
Generate anesthesia claims for a surgical procedure
```

Telehealth:

```
Generate a telehealth visit claim
Create claims for remote patient monitoring
```

### Facility Claims (837I)

Inpatient:

```
Generate a facility claim for a 3-day hospital stay
Create an inpatient claim with DRG 470 (hip replacement)
Generate a psychiatric inpatient claim
```

Outpatient:

```
Generate an outpatient facility claim for ambulatory surgery
Create an ED facility claim
Generate claims for outpatient observation
```

Emergency:

```
Generate an emergency department claim
Create trauma center claims
```

### Adjudication Scenarios

Paid claims:

```
Generate a paid professional claim
Create a facility claim paid at 80% coinsurance
Generate claims with deductible applied
```

Denied claims:

```
Generate a denied claim for prior authorization required
Create a claim denied for non-covered service
Generate a denied claim for out-of-network provider
```

Adjusted claims:

```
Generate a claim with coordination of benefits adjustment
Create a claim with contractual adjustment
Generate a claim reduced for medical necessity
```

### Remittance (835)

```
Generate an 835 remittance for the paid claims
Create payment advice with multiple claims
Generate ERA with CARC/RARC codes
```

---

## Claims Details

### Professional Claim Components

```
Claim Header:
  - Claim ID, control number
  - Statement dates (from/to)
  - Place of service
  - Frequency/type code

Member:
  - Member ID, subscriber ID
  - Name, DOB, gender
  - Group/policy number

Provider:
  - Billing provider (NPI, taxonomy)
  - Rendering provider
  - Referring provider (if applicable)

Services:
  - Service lines with CPT/HCPCS
  - Modifiers
  - Diagnosis pointers
  - Charges, units

Diagnoses:
  - ICD-10-CM codes
  - Primary, secondary, etc.
```

### Facility Claim Components

```
Claim Header:
  - Bill type (011X inpatient, 013X outpatient)
  - Admit/discharge dates
  - Patient status code
  - Admission type/source

Services:
  - Revenue codes
  - HCPCS/CPT codes
  - Service dates
  - Units, charges

DRG (Inpatient):
  - MS-DRG code
  - Weight
  - Base payment
  - Outlier adjustments
```

### Adjudication Components

```
Payment:
  - Allowed amount
  - Paid amount
  - Member responsibility (copay, coinsurance, deductible)

Adjustments:
  - CARC (Claim Adjustment Reason Code)
  - RARC (Remittance Advice Remark Code)
  - Group codes (CO, PR, OA)

Status:
  - Paid, denied, pending
  - Denial reason (if applicable)
```

---

## Output Formats

### X12 837P (Professional)

```
Generate as X12 837P
Export in 5010 format
Create 837P for claims submission
```

### X12 837I (Institutional)

```
Generate as X12 837I
Export facility claim as EDI
```

### X12 835 (Remittance)

```
Generate 835 remittance
Create ERA for these claims
Export as X12 835
```

### X12 834 (Enrollment)

```
Generate 834 enrollment transaction
Create eligibility file as 834
```

### JSON/CSV

```
Export claims as JSON
Generate claims as CSV
Create claims spreadsheet
```

---

## Pricing & Payment

### Pricing Models

```
Generate claim with fee schedule pricing
Create claim using Medicare rates
Generate commercial contracted rates
```

### Payment Scenarios

```
Generate claim with 20% coinsurance
Create claim with $50 copay
Generate claim with deductible applied
Create claim showing out-of-pocket max reached
```

### Coordination of Benefits

```
Generate claim with primary/secondary payers
Create claim with Medicare as secondary
Generate dual-eligible member claims
```

---

## Denial Scenarios

### Common Denial Reasons

| CARC | Description | Use Case |
|------|-------------|----------|
| CO-4 | Procedure inconsistent with modifier | Modifier errors |
| CO-15 | Prior authorization required | Auth issues |
| CO-16 | Missing information | Incomplete claim |
| CO-18 | Duplicate claim | Resubmission |
| CO-27 | Expenses incurred after coverage ended | Eligibility |
| CO-29 | Time limit for filing expired | Late submission |
| CO-50 | Non-covered service | Benefit exclusion |
| CO-96 | Non-covered charges | Various |
| PR-1 | Deductible | Member responsibility |
| PR-2 | Coinsurance | Member responsibility |
| PR-3 | Copay | Member responsibility |

Generate specific denials:

```
Generate a claim denied with CO-15 (prior auth required)
Create a claim denied for duplicate submission (CO-18)
Generate a claim denied as non-covered (CO-50)
```

---

## Tips & Best Practices

### Complete Claims

Request full claim details:

```
Generate a complete professional claim with all standard elements
including member, provider, service lines, and adjudication
```

### Realistic Scenarios

Ask for clinically appropriate services:

```
Generate claims for a diabetic patient's quarterly follow-up
including office visit, A1C lab, and medication refills
```

### Testing Specific Scenarios

Be explicit about test cases:

```
Generate a claim that will be denied for prior authorization
Create a claim with multiple service lines totaling over $1000
Generate a facility claim with 5-day length of stay
```

### Linked Data

Connect claims to patients:

```
Generate a professional claim for this patient's encounter
Create facility claims for their hospitalization
```

---

## Integration with Other Domains

### With PatientSim

```
Generate a diabetic patient with their recent office visit claims
Create a patient and facility claims for their surgery
```

### With RxMemberSim

```
Generate a member with both medical and pharmacy claims
Create claims for the office visit and prescription fills
```

### With NetworkSim

```
Generate a claim with a real Texas cardiologist as provider
Create facility claims at Houston Methodist Hospital
```

---

## Related Resources

### Skills

- [professional-claims.md](../../skills/membersim/professional-claims.md)
- [facility-claims.md](../../skills/membersim/facility-claims.md)
- [enrollment-eligibility.md](../../skills/membersim/enrollment-eligibility.md)
- [plan-benefits.md](../../skills/membersim/plan-benefits.md)

### Reference

- [X12 Format Reference](../reference/output-formats.md#x12)
- [CARC/RARC Codes](../reference/code-systems.md#adjustment-codes)
- [DRG Reference](../reference/code-systems.md#drg)

### Examples

- [Basic Claims Generation](../../examples/basic/claims-generation.md)
- [Denial Scenarios](../../examples/intermediate/denial-scenarios.md)
- [EDI Testing](../../examples/advanced/edi-testing.md)

---

## Troubleshooting

### Claims lack proper coding

Request specific codes:
```
Generate a professional claim with proper CPT and ICD-10 codes
```

### X12 format issues

Request specific version:
```
Generate as valid X12 837P 5010 format with proper delimiters
```

### Missing adjudication

Request complete adjudication:
```
Generate a claim with full adjudication including CARC/RARC codes
```

See [Troubleshooting](../getting-started/troubleshooting.md) for more solutions.
