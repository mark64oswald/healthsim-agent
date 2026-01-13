# Pharmacy Generation Example

Generate pharmacy claims with DUR alerts, pricing, and formulary data.

---

## Goal

Learn how to generate pharmacy claims with proper NDC codes, pricing components, and drug utilization review.

---

## Prerequisites

- HealthSim installed (`pip install healthsim-agent`)
- API key configured (`ANTHROPIC_API_KEY`)

---

## Steps

### Step 1: Start HealthSim

```bash
healthsim
```

### Step 2: Generate Basic Prescription Claims

```
healthsim › Generate pharmacy claims for a diabetic patient's medications
```

Expected output:
```
✓ Added 1 rx_member, 6 prescriptions

  Rx Member: RX-001
  Name:      Maria Santos
  Age:       52
  Plan:      Express Scripts Standard
  
  Prescriptions:
  
  │ Fill Date  │ Drug                │ NDC          │ Qty │ Days│ Cost    │ Copay │
  ├────────────┼─────────────────────┼──────────────┼─────┼─────┼─────────┼───────┤
  │ 2024-01-05 │ Metformin 500mg     │ 00093-7267-01│ 180 │ 90  │ $12.50  │ $10   │
  │ 2024-01-05 │ Lisinopril 10mg     │ 00093-7339-01│ 90  │ 90  │ $8.75   │ $10   │
  │ 2024-01-05 │ Atorvastatin 20mg   │ 00093-5058-01│ 90  │ 90  │ $15.20  │ $10   │
  │ 2024-04-05 │ Metformin 500mg     │ 00093-7267-01│ 180 │ 90  │ $12.50  │ $10   │
  │ 2024-04-05 │ Lisinopril 10mg     │ 00093-7339-01│ 90  │ 90  │ $8.75   │ $10   │
  │ 2024-04-05 │ Atorvastatin 20mg   │ 00093-5058-01│ 90  │ 90  │ $15.20  │ $10   │
  
  Summary:
    Total Cost:     $73.90
    Plan Paid:      $13.90
    Member Copays:  $60.00
    Tier: Generic (Tier 1)
```

### Step 3: Generate Claims with DUR Alerts

```
healthsim › Generate pharmacy claims that trigger drug interaction alerts
```

Expected output:
```
✓ Added 1 rx_member, 3 prescriptions (2 with DUR alerts)

  Rx Member: RX-002
  Name:      James Wilson
  Age:       68
  Plan:      CVS Caremark Preferred
  
  Prescriptions with DUR Alerts:
  
  1. Warfarin 5mg
     NDC: 00378-4540-01
     ⚠️ DUR Alert: Drug-Drug Interaction (Severity: HIGH)
        Interacts with: Aspirin 81mg
        Clinical Significance: Increased bleeding risk
        Action: Filled with pharmacist override
  
  2. Aspirin 81mg
     NDC: 00904-5784-51
     ⚠️ DUR Alert: Duplicate Therapy
        Existing: Plavix 75mg on profile
        Clinical Significance: Dual antiplatelet + anticoagulant
        Action: Prescriber notified
  
  3. Metoprolol 50mg
     NDC: 00378-0181-01
     ✓ No DUR alerts
```

### Step 4: Generate Specialty Pharmacy Claims

```
healthsim › Generate specialty pharmacy claims for Humira
```

Expected output:
```
✓ Added 1 rx_member, 2 prescriptions

  Rx Member: RX-003
  Name:      Sarah Johnson
  Age:       42
  Condition: Rheumatoid Arthritis
  Plan:      Accredo Specialty
  
  Specialty Rx:
  
  Drug: Humira 40mg/0.4mL Pen
  NDC:  00074-9374-02
  
  │ Fill Date  │ Qty │ AWP      │ Ingredient│ Disp Fee│ Total   │
  ├────────────┼─────┼──────────┼───────────┼─────────┼─────────┤
  │ 2024-01-10 │ 2   │ $6,845.00│ $5,476.00 │ $25.00  │$5,501.00│
  │ 2024-02-07 │ 2   │ $6,845.00│ $5,476.00 │ $25.00  │$5,501.00│
  
  Cost Breakdown:
    AWP:              $6,845.00
    Plan Discount:    -$1,369.00 (20%)
    Ingredient Cost:  $5,476.00
    Dispensing Fee:   $25.00
    Total:            $5,501.00
    Copay:            $150.00 (Specialty tier)
    Plan Paid:        $5,351.00
  
  Prior Authorization:
    PA #: PA-2024-0042
    Approved: 2023-12-15
    Expires: 2024-12-15
    
  Manufacturer Program:
    AbbVie Complete - Copay Assistance
    Max Annual Benefit: $20,000
```

### Step 5: Generate Claims with Formulary Issues

```
healthsim › Generate pharmacy claims with non-formulary and step therapy requirements
```

Expected output:
```
✓ Generated 4 prescription scenarios

  1. Covered Generic
     Drug:   Omeprazole 20mg
     Status: Formulary (Tier 1)
     Copay:  $10
     ✓ Filled
  
  2. Preferred Brand
     Drug:   Eliquis 5mg
     Status: Formulary (Tier 3)
     Copay:  $75
     ✓ Filled
  
  3. Non-Formulary Brand
     Drug:   Nexium 40mg
     Status: Non-Formulary
     ✗ Rejected - Drug not covered
     Alternative: Omeprazole (generic) or Prilosec OTC
  
  4. Step Therapy Required
     Drug:   Ozempic 0.5mg
     Status: Prior Auth / Step Therapy
     ✗ Rejected - Step therapy not met
     Required: Trial of Metformin, then Jardiance
     Appeal Option: Medical necessity override
```

### Step 6: View Claim Pricing Details

```
healthsim › Show pricing breakdown for RX-001 prescriptions
```

Expected output:
```
Pricing Analysis - Metformin 500mg #180
═══════════════════════════════════════

AWP (Average Wholesale Price):
  Unit AWP:     $0.08
  Extended AWP: $14.40
  
Ingredient Cost Calculation:
  MAC (Maximum Allowable Cost): $0.07/unit
  Extended MAC: $12.60
  
Dispensing Fee: $2.00

Pricing Basis: MAC + Fee
  Ingredient: $12.60
  + Disp Fee: $2.00
  = Total:    $14.60
  
U&C (Usual & Customary): $18.50
  Lower of calculated vs U&C applied
  
Final Pricing:
  Total Cost:      $14.60
  Plan Pays:       $4.60
  Member Copay:    $10.00 (Tier 1 copay)
```

### Step 7: Export as NCPDP

```
healthsim › Export pharmacy claims as NCPDP D.0
```

Expected output:
```
✓ Generated NCPDP D.0 → output/pharmacy-claims.ncpdp

  Transaction Type: B1 (Billing Request)
  Claims: 11
  
  Sample Transaction:
  AM01 Header: 51=D0, 103=1.2, 109=RX-001
  AM04 Insurance: 301=ABC123, 302=01
  AM07 Claim: 401=B1, 402=01, 403=20240105
  AM11 Pricing: 409=$12.50, 426=$10.00
  ...
```

---

## What You Created

| Rx Member | Claims | Type | Total Cost |
|-----------|--------|------|------------|
| RX-001 | 6 | Maintenance meds | $73.90 |
| RX-002 | 3 | With DUR alerts | $245.00 |
| RX-003 | 2 | Specialty | $11,002.00 |

---

## Variations

### Generate mail order claims

```
Generate 90-day mail order pharmacy claims
```

### Generate controlled substance claims

```
Generate opioid prescriptions with appropriate PDMP checks
```

### Generate compound claims

```
Generate compound pharmacy claims with multiple ingredients
```

### Generate claims with manufacturer rebates

```
Generate brand claims showing estimated rebate values
```

---

## Common Issues

### NDC not found

```
Generate claims using standard retail NDC format
```

### DUR not triggering

```
Generate claims with explicit drug interactions to show DUR
```

### Need specific pharmacy

```
Generate claims filled at Walgreens pharmacy NPI 1234567890
```

---

## Related Examples

- [Patient Generation](patient-generation.md) - Clinical data
- [Claims Generation](claims-generation.md) - Medical claims
- [Cross-Product](../intermediate/patient-journey.md) - Full workflow

---

## Related Guides

- [RxMemberSim Guide](../../docs/guides/rxmembersim-guide.md) - Complete pharmacy reference
- [Code Systems](../../docs/reference/code-systems.md) - NDC format details
