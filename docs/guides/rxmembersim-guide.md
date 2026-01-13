# RxMemberSim Guide

Generate realistic synthetic pharmacy and PBM (Pharmacy Benefit Manager) data through natural conversation.

---

## Overview

RxMemberSim creates pharmacy benefit data with:

- **Prescriptions** - NCPDP SCRIPT prescriptions with full drug details
- **Pharmacy Claims** - Real-time adjudication with pricing
- **DUR Alerts** - Drug Utilization Review with clinical rules
- **Formulary** - Tier structures, prior auth requirements
- **Prior Authorization** - PA requests and determinations
- **Accumulators** - Deductible and out-of-pocket tracking
- **Specialty Programs** - Limited distribution, specialty pharmacy

**Output Formats:** NCPDP D.0, NCPDP SCRIPT, X12 835 (Pharmacy), JSON, CSV

---

## Quick Start

Generate your first pharmacy claim:

```
healthsim › Generate a pharmacy claim for metformin 1000mg

✓ Added 1 pharmacy claim

  Claim:          RX-2026-000001
  Drug:           Metformin HCl 1000mg Tablet
  NDC:            00378-0269-01
  Quantity:       60 tablets
  Days Supply:    30
  
  Pricing:
    Ingredient Cost:  $12.50
    Dispensing Fee:   $2.00
    Copay:            $10.00
    Plan Paid:        $4.50
  
  Status:         PAID
  Response Code:  00 (Approved)
```

---

## Common Scenarios

### Basic Prescription Generation

Generate prescriptions with drug details:

```
Generate a prescription for lisinopril 20mg daily
Create a 90-day supply prescription for atorvastatin
Generate a controlled substance prescription for oxycodone
Generate an antibiotic prescription for amoxicillin
```

### Pharmacy Claims Processing

Claims with different outcomes:

```
Generate a pharmacy claim that pays successfully
Create a claim that rejects for prior authorization required
Generate a claim with a DUR warning for drug interaction
Create a claim that rejects for refill too soon
```

### Formulary and Tiers

Working with benefit designs:

```
Generate a claim for a Tier 1 generic drug
Create a claim for a Tier 3 preferred brand
Generate a claim for a non-formulary drug
Create a claim requiring step therapy
```

### Prior Authorization

PA workflows:

```
Generate a prior authorization request for Humira
Create a PA approval for specialty medication
Generate a PA denial with clinical rationale
Create a PA that expires and needs renewal
```

---

## Drug Utilization Review (DUR)

### DUR Alert Types

RxMemberSim generates realistic DUR alerts:

| Alert Type | Description | Example |
|------------|-------------|---------|
| Drug-Drug Interaction | Interacting medications | Warfarin + NSAIDs |
| Therapeutic Duplication | Same drug class | Two SSRIs |
| Early Refill | Too soon to refill | < 75% of days supply used |
| High Dose | Exceeds recommended | Metformin > 2550mg/day |
| Drug-Age | Age contraindication | Diphenhydramine in elderly |
| Drug-Disease | Disease contraindication | NSAIDs in renal failure |
| Drug-Allergy | Known allergy | Penicillin allergy + amoxicillin |

### Generating DUR Scenarios

```
Generate a claim with a drug-drug interaction alert
Create a claim flagged for therapeutic duplication
Generate an early refill rejection
Create a high dose alert for opioids
```

### DUR Override Processing

```
Generate a DUR alert with pharmacist override
Create a claim where prescriber was consulted for interaction
Generate a soft stop that was overridden
```

### DUR Alert Severity

| Level | Severity | Action |
|-------|----------|--------|
| Level 1 | Major | Requires override or rejection |
| Level 2 | Moderate | Warning, may proceed |
| Level 3 | Minor | Informational only |

---

## Specialty Pharmacy

### Limited Distribution Drugs

```
Generate a specialty pharmacy claim for Humira
Create an oncology drug claim through specialty pharmacy
Generate a claim for a REMS drug
```

### Specialty Programs

```
Generate a claim with manufacturer copay assistance
Create a patient enrolled in specialty pharmacy program
Generate a claim with hub services coordination
```

### Specialty Pricing

```
Generate a specialty claim with AWP-based pricing
Create a claim with 340B pricing
Generate a specialty claim with WAC acquisition cost
```

---

## Pricing and Adjudication

### Pricing Components

| Component | Description |
|-----------|-------------|
| Ingredient Cost | Cost of the drug |
| Dispensing Fee | Pharmacy service fee |
| U&C (Usual & Customary) | Pharmacy's cash price |
| Copay | Member cost share |
| Coinsurance | Percentage cost share |
| Deductible | Amount applied to deductible |

### Pricing Scenarios

```
Generate a claim with standard copay pricing
Create a claim where member pays U&C (lower than copay)
Generate a claim with deductible applied
Create a claim in the coverage gap (donut hole)
```

### Rejection Reasons

Common rejection codes:

| Code | Meaning |
|------|---------|
| 70 | Product not on formulary |
| 75 | Prior authorization required |
| 76 | Plan limitations exceeded |
| 79 | Refill too soon |
| 88 | DUR reject - must call prescriber |

---

## Accumulator Tracking

### Benefit Accumulators

```
Generate claims showing deductible accumulation
Create a claim that satisfies the deductible
Generate claims showing progress toward out-of-pocket max
Create a catastrophic coverage claim
```

### Medicare Part D Phases

```
Generate a claim in the initial coverage phase
Create a claim entering the coverage gap
Generate a claim in catastrophic coverage
Show transition through Part D benefit phases
```

---

## Output Formats

### NCPDP Telecommunication (D.0)

```
Generate this claim as NCPDP D.0
Export pharmacy claims in NCPDP Telecom format
```

Real-time pharmacy claims format with:
- Billing (B1), Reversal (B2), Rebill (B3) transactions
- Request and response segments
- DUR/PPS segments

### NCPDP SCRIPT

```
Generate as NCPDP SCRIPT prescription
Export prescriptions in SCRIPT 2017071 format
```

E-prescribing format for:
- NewRx (new prescriptions)
- Refill requests
- CancelRx
- RxChangeRequest

### X12 835 (Pharmacy)

```
Generate pharmacy remittance as X12 835
Export pharmacy payment data
```

Electronic remittance advice for pharmacy claims.

### JSON/CSV

```
Export pharmacy claims as JSON
Generate pharmacy data as CSV
```

---

## Integration with Other Products

### Linking to Members

```
Generate a pharmacy claim for this member
Add prescription fills to the existing member's profile
```

### Linking to Patients

```
Create pharmacy claims based on patient medications
Generate fills for all current medications
```

### Cross-Product Workflow

```
Generate a patient with diabetes, their insurance enrollment,
and pharmacy claims for their diabetes medications
```

---

## Tips & Best Practices

### Be Specific About Drug Details

```
# Basic (works but generic)
Generate a pharmacy claim

# Better (realistic output)
Generate a pharmacy claim for atorvastatin 40mg #30 with 30-day supply,
filled at CVS, for a member with a 3-tier formulary and $10/$30/$50 copays,
drug is Tier 1 generic
```

### Use NDC Codes When Needed

```
Generate a claim for NDC 00378-0269-01 (generic metformin)
Create a claim specifically for brand Lipitor
```

### Request Specific Scenarios

```
Generate a claim that triggers DUR alert DD (drug-drug interaction)
between warfarin and aspirin, requiring pharmacist override
Create a prior auth denial for medical necessity not met
```

---

## Code Systems Reference

### NDC (National Drug Code)

11-digit code: Labeler (5) + Product (4) + Package (2)

```
00378-0269-01
│     │     └── Package code
│     └── Product code
└── Labeler code (Mylan)
```

### GPI (Generic Product Identifier)

14-digit hierarchical code for drug classification.

### DAW (Dispense As Written)

| Code | Meaning |
|------|---------|
| 0 | No product selection indicated |
| 1 | Substitution not allowed by prescriber |
| 2 | Substitution allowed, patient requested brand |
| 7 | Substitution not allowed, brand mandated by law |

---

## Related Resources

### Skills

- [dur-alerts.md](../../skills/rxmembersim/dur-alerts.md)
- [formulary-management.md](../../skills/rxmembersim/formulary-management.md)
- [specialty-pharmacy.md](../../skills/rxmembersim/specialty-pharmacy.md)
- [rx-prior-auth.md](../../skills/rxmembersim/rx-prior-auth.md)

### Reference

- [Code Systems](../reference/code-systems.md) - NDC, GPI, DAW codes
- [Output Formats](../reference/output-formats.md) - NCPDP specifications
- [Data Models](../reference/data-models.md) - Canonical pharmacy claim model

### Examples

- [Basic Pharmacy Generation](../../examples/basic/pharmacy-generation.md)
- [DUR Scenarios](../../examples/intermediate/dur-scenarios.md)
- [Specialty Pharmacy Workflow](../../examples/advanced/specialty-pharmacy.md)

---

## Troubleshooting

### Claim always rejects

Check member eligibility:
```
Generate an eligible rx member with active pharmacy benefit,
then create a pharmacy claim for that member
```

### DUR alerts not appearing

Request specific alerts:
```
Generate a pharmacy claim for warfarin for a patient also on aspirin,
should trigger drug-drug interaction alert
```

### Pricing doesn't match expectations

Specify the benefit design:
```
Generate a claim for a member with $10 generic / $30 brand / $50 specialty
copay structure, Tier 2 brand drug
```

See [Troubleshooting](../getting-started/troubleshooting.md) for more solutions.
