# Pharmacy Claims Example

Learn to generate pharmacy transactions with HealthSim RxMemberSim.

---

## Goal

Create realistic pharmacy claims with NDC codes, pricing, and DUR alerts. You'll learn:

- Prescription generation
- Pharmacy claim adjudication
- Drug utilization review (DUR)
- Formulary and pricing

---

## Prerequisites

- HealthSim installed and running
- Basic familiarity with [Patient Generation](patient-generation.md)
- ~10 minutes

---

## Steps

### Step 1: Create an RxMember

```
healthsim › Create an RxMember with Express Scripts coverage for a diabetic patient
```

Expected output:
```
✓ Generated RxMember

RxMember: RXM-001
  Name: Patricia Williams
  DOB: 1962-08-22 (63 years)
  Location: Phoenix, AZ 85004
  
Pharmacy Coverage:
  PBM: Express Scripts
  RxBIN: 003858
  RxPCN: A4
  RxGroup: RXGRP001
  Person Code: 01
  
Formulary: 3-Tier
  Tier 1 (Generic): $10 copay
  Tier 2 (Preferred Brand): $35 copay
  Tier 3 (Non-Preferred): $60 copay
  
Accumulators:
  Rx Deductible: $0 / $100
  Rx OOP: $0 / $2,500
```

### Step 2: Generate a Generic Prescription

```
healthsim › Fill a prescription for metformin 1000mg twice daily, 90 day supply
```

Expected output:
```
✓ Generated pharmacy claim

Rx Claim: RX-2026-000001
  Drug: Metformin HCl 1000mg Tablet
  NDC: 00093-7214-01
  GPI: 27200020000310
  Tier: 1 (Generic)
  
Fill Details:
  Quantity: 180 tablets
  Days Supply: 90
  Pharmacy: CVS Pharmacy #4521
  NPI: 1234567890
  DAW: 0 (No product selection)
  
Pricing:
  Ingredient Cost: $12.45
  Dispensing Fee: $2.00
  U&C Price: $45.00
  
Adjudication:
  Plan Pays: $4.45
  Patient Copay: $10.00
  Total: $14.45
```

### Step 3: Add a Brand Medication

```
healthsim › Add Jardiance 25mg daily for diabetes
```

Expected output:
```
✓ Generated pharmacy claim

Rx Claim: RX-2026-000002
  Drug: Jardiance (empagliflozin) 25mg Tablet
  NDC: 00597-0152-30
  GPI: 27850010000320
  Tier: 2 (Preferred Brand)
  
Fill Details:
  Quantity: 30 tablets
  Days Supply: 30
  Pharmacy: CVS Pharmacy #4521
  
Pricing:
  Ingredient Cost: $545.00
  Dispensing Fee: $2.00
  AWP: $598.00
  
Adjudication:
  Plan Pays: $512.00
  Patient Copay: $35.00
  Total: $547.00
```

### Step 4: Trigger a DUR Alert

```
healthsim › Now fill a prescription for glipizide 10mg twice daily
```

Expected output:
```
⚠️ DUR Alert Generated

Rx Claim: RX-2026-000003 (Pending Review)
  Drug: Glipizide 10mg Tablet
  NDC: 00378-0182-01
  
DUR Alert:
  Type: Therapeutic Duplication
  Severity: Level 2 (Significant)
  Reason: Patient already on metformin + empagliflozin for diabetes
  
Clinical Message:
  "Patient is currently receiving diabetes therapy with metformin 
   and Jardiance. Adding a sulfonylurea may increase hypoglycemia 
   risk. Consider clinical review."

Action Required: Pharmacist override or prescriber contact
```

### Step 5: Process with Override

```
healthsim › Override the DUR with pharmacist approval - prescriber confirmed
```

Expected output:
```
✓ DUR Override applied

Rx Claim: RX-2026-000003 (Adjudicated)
  Override Code: PY (Prescriber Consulted)
  Pharmacist: RPh Sarah Chen
  
Pricing:
  Ingredient Cost: $8.50
  Dispensing Fee: $2.00
  
Adjudication:
  Plan Pays: $0.50
  Patient Copay: $10.00
  Total: $10.50
```

### Step 6: Add a Controlled Substance

```
healthsim › Fill tramadol 50mg #60 for chronic pain
```

Expected output:
```
✓ Generated pharmacy claim

Rx Claim: RX-2026-000004
  Drug: Tramadol HCl 50mg Tablet
  NDC: 00591-5194-01
  DEA Schedule: IV
  
Fill Details:
  Quantity: 60 tablets
  Days Supply: 30
  Refills Remaining: 5
  
DUR Check: ✓ No alerts
  - No opioid PDMP conflicts
  - No quantity limits exceeded
  - No early refill
  
Adjudication:
  Plan Pays: $2.00
  Patient Copay: $10.00
  Total: $12.00
```

### Step 7: View Pharmacy Summary

```
healthsim › /status
```

```
Current Session
═══════════════════════════════════════
RxMembers:    1
Pharmacy Claims: 4
DUR Alerts:   1 (overridden)

Financial Summary:
  Total Ingredient Cost: $578.45
  Total Plan Paid:       $518.95
  Total Patient Cost:    $65.00
  
Accumulator Status:
  Rx Deductible: $0 / $100 (n/a)
  Rx OOP: $65.00 / $2,500
═══════════════════════════════════════
```

### Step 8: Export to NCPDP

```
healthsim › Export pharmacy claims as NCPDP D.0
```

```
✓ Exported NCPDP D.0

Output: ./exports/ncpdp-d0-20260112.dat
Transactions: 4 (B1 claims)
Format: NCPDP D.0 Telecommunication Standard
```

---

## What You Created

| Entity | Count | Details |
|--------|-------|---------|
| RxMember | 1 | ESI coverage |
| Pharmacy Claims | 4 | Mixed tier drugs |
| DUR Alerts | 1 | Therapeutic dup |
| Drugs | 4 | Generic + Brand |

---

## Variations

### Specialty Medication

```
healthsim › Fill Humira for rheumatoid arthritis, requiring specialty pharmacy 
            and prior authorization
```

### Mail Order

```
healthsim › Fill 90-day maintenance medications via mail order pharmacy
```

### Generic Substitution

```
healthsim › Fill a prescription for Lipitor where generic is available
```

### Multiple DUR Scenarios

```
healthsim › Create pharmacy claims that trigger drug-drug interaction, early 
            refill, and quantity limit alerts
```

---

## DUR Alert Types

| Alert Type | Description | Example |
|------------|-------------|---------|
| Drug-Drug | Interaction between drugs | Warfarin + Aspirin |
| Therapeutic Dup | Same drug class | Two SSRIs |
| Early Refill | Refill too soon | <75% of days elapsed |
| High Dose | Above recommended | Metformin >2550mg/day |
| Drug-Age | Inappropriate for age | Beers criteria |
| Drug-Disease | Contraindicated | Beta-blocker + asthma |

---

## Formulary Tiers

| Tier | Type | Typical Copay |
|------|------|---------------|
| 1 | Generic | $0-15 |
| 2 | Preferred Brand | $25-50 |
| 3 | Non-Preferred | $50-100 |
| 4 | Specialty | 20-33% coinsurance |

---

## Troubleshooting

**Wrong drug found?**
- Use NDC code: "Fill NDC 00093-7214-01"
- Or GPI: "Fill GPI 27200020000310"

**Pricing seems wrong?**
- AWP, MAC, and contract pricing vary
- Specify: "Use AWP pricing" or "Use MAC pricing"

**DUR not triggering?**
- Make sure drug history includes conflicting medications
- Be specific about the interaction you want

---

## Next Steps

- [Cross-Product Workflow](../intermediate/cross-product-workflow.md) - Link medical and Rx
- [Denial Scenarios](../intermediate/denial-scenarios.md) - PA denials
- [Batch Generation](../advanced/batch-generation.md) - Volume testing

---

## Related

- [RxMemberSim Guide](../../docs/guides/rxmembersim-guide.md)
- [Output Formats Reference](../../docs/reference/output-formats.md)
- [Code Systems Reference](../../docs/reference/code-systems.md)
