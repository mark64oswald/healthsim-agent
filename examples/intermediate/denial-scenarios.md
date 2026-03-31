# Denial Scenarios Example

Generate claims denial scenarios for testing adjudication logic and appeals workflows.

---

## Goal

Create realistic claim denials with:

- Common denial reasons and CARC/RARC codes
- Prior authorization failures
- Medical necessity denials
- Out-of-network scenarios
- Appeals and corrected claims

---

## Prerequisites

- HealthSim installed and running
- Familiarity with [Claims Generation](../basic/claims-generation.md)
- ~15 minutes

---

## Steps

### Step 1: Create a Member

```
healthsim › Create a member with Aetna HMO coverage requiring referrals
```

Expected output:
```
✓ Generated member

Member: MBR-001
  Name: David Chen
  DOB: 1980-04-12 (45 years)
  
Coverage: Aetna HMO Select
  Member ID: AET774829156
  PCP Required: Yes
  Referral Required: Yes for specialists
  Prior Auth: Required for imaging, procedures
```

### Step 2: Denial - No Referral

```
healthsim › Generate a specialist visit without the required referral
```

Expected output:
```
✓ Generated denied claim

Claim: CLM-2026-000001
  Status: DENIED
  Provider: Dr. Lisa Park, MD (Dermatology)
  Service: 99203 (New patient, office visit)
  Billed: $225.00
  
Denial Details:
  CARC: 96 (Non-covered charge)
  RARC: N290 (Missing/incomplete referral)
  Remark: "Services require referral from PCP. No referral on file."
  
835 Adjustment:
  PR-96: $225.00 (Patient responsibility - non-covered)
  
Patient Impact: Full balance billing ($225.00)
```

### Step 3: Denial - Prior Auth Required

```
healthsim › Generate an MRI claim denied for missing prior authorization
```

Expected output:
```
✓ Generated denied claim

Claim: CLM-2026-000002
  Status: DENIED
  Facility: Metro Imaging Center
  Service: 72148 (MRI lumbar spine w/o contrast)
  Billed: $2,400.00
  
Denial Details:
  CARC: 197 (Precertification/authorization absent)
  RARC: N386 (Authorization number not provided)
  Remark: "Prior authorization required. No valid auth on file."
  
835 Adjustment:
  CO-197: $2,400.00 (Contractual - no auth)
  
Patient Impact: $0 (facility must obtain auth or write off)
```

### Step 4: Denial - Medical Necessity

```
healthsim › Generate a claim denied for lack of medical necessity - 
            requesting cosmetic procedure
```

Expected output:
```
✓ Generated denied claim

Claim: CLM-2026-000003
  Status: DENIED
  Provider: Dr. Robert Kim, MD (Plastic Surgery)
  Service: 15823 (Blepharoplasty, upper eyelid)
  Diagnosis: H02.839 (Dermatochalasis, unspecified)
  Billed: $3,800.00
  
Denial Details:
  CARC: 50 (Non-covered - not medically necessary)
  RARC: N115 (Service not supported by diagnosis)
  Remark: "Procedure not medically necessary based on submitted 
           diagnosis. Documentation does not support functional 
           impairment."
  
Medical Policy: Blepharoplasty requires documentation of:
  - Visual field deficit > 30%
  - Photographic evidence
  - Failed conservative treatment
  
835 Adjustment:
  CO-50: $3,800.00 (Contractual - not medically necessary)
  
Patient Impact: May appeal with additional documentation
```

### Step 5: Denial - Out of Network

```
healthsim › Generate an out-of-network ER claim with balance billing
```

Expected output:
```
✓ Generated partially denied claim

Claim: CLM-2026-000004
  Status: PARTIAL PAY (OON)
  Facility: Community Hospital (Non-participating)
  Service: 99284 (ED visit, high severity)
  Billed: $1,850.00
  
Processing (Out-of-Network):
  UCR Allowed: $650.00 (70% of in-network rate)
  OON Deductible: $500.00 (separate from in-network)
  Coinsurance: 40% = $60.00
  Plan Paid: $90.00
  
Denial Details (Balance):
  CARC: 45 (Charge exceeds UCR)
  RARC: N381 (Balance billing allowed)
  Balance Billed: $1,200.00
  
835 Payment:
  Payment: $90.00
  PR-1: $500.00 (Deductible)
  PR-2: $60.00 (Coinsurance)
  CO-45: $1,200.00 (Non-covered excess)
  
Patient Impact: 
  Plan cost share: $560.00
  Balance bill: $1,200.00
  Total: $1,760.00
```

### Step 6: Denial - Duplicate Claim

```
healthsim › Submit the same claim twice to show duplicate denial
```

Expected output:
```
✓ Generated denied claim (duplicate)

Claim: CLM-2026-000005
  Status: DENIED (Duplicate)
  Original Claim: CLM-2026-000001
  
Denial Details:
  CARC: 18 (Duplicate claim/service)
  RARC: MA130 (Duplicate of a claim processed)
  Remark: "This claim/service duplicates one already processed."
  
835 Adjustment:
  OA-18: $225.00 (Other adjustment - duplicate)
  
Action Required: None - original claim on file
```

### Step 7: Denial - Timely Filing

```
healthsim › Generate a claim denied for timely filing (submitted too late)
```

Expected output:
```
✓ Generated denied claim (timely filing)

Claim: CLM-2026-000006
  Status: DENIED
  Service Date: 2024-06-15
  Received Date: 2026-01-10
  Days from DOS: 574 days
  Filing Limit: 365 days
  
Denial Details:
  CARC: 29 (Time limit for filing expired)
  RARC: N96 (Claim not received within filing deadline)
  Remark: "Claim received 574 days from date of service. 
           Filing limit is 365 days from DOS."
  
835 Adjustment:
  CO-29: Full billed amount (Contractual write-off)
  
Patient Impact: $0 (provider must write off)
```

### Step 8: Process an Appeal

```
healthsim › Appeal the medical necessity denial with additional documentation
```

Expected output:
```
✓ Generated appeal and reconsideration

Appeal: APL-2026-000001
  Original Claim: CLM-2026-000003
  Appeal Type: Level 1 - Reconsideration
  
Additional Documentation Submitted:
  - Visual field test showing 35% deficit
  - Pre-operative photographs
  - Letter of medical necessity from ophthalmologist
  
Appeal Decision: APPROVED
  Rationale: "Additional documentation supports functional 
              impairment meeting medical policy criteria."
  
Corrected Claim: CLM-2026-000003-R1
  Status: PAID
  Allowed: $2,850.00
  Deductible: $150.00 (remaining)
  Coinsurance: $540.00 (20%)
  Plan Paid: $2,160.00
  
New 835 Generated: Payment remittance for corrected claim
```

### Step 9: View Denial Summary

```
healthsim › /status
```

```
Current Session: Denial Scenarios
═══════════════════════════════════════
Members:       1
Claims:        6
  Paid:        1 (after appeal)
  Denied:      5
  
Denial Breakdown:
  No Referral:        1
  No Prior Auth:      1
  Medical Necessity:  1 (reversed on appeal)
  Out of Network:     1 (partial)
  Duplicate:          1
  Timely Filing:      1
  
Appeals:       1 (approved)
═══════════════════════════════════════
```

---

## What You Created

| Entity | Count | Details |
|--------|-------|---------|
| Member | 1 | HMO coverage |
| Claims | 6 | Various denial scenarios |
| Denials | 5 | Different CARC codes |
| Appeals | 1 | Successful overturn |

---

## Common Denial Codes

### CARC (Claim Adjustment Reason Codes)

| Code | Description | Common Cause |
|------|-------------|--------------|
| 4 | Procedure code inconsistent with modifier | Coding error |
| 16 | Claim lacks information | Missing data |
| 18 | Duplicate claim | Resubmission |
| 29 | Timely filing | Late submission |
| 45 | Exceeds UCR | OON balance |
| 50 | Not medically necessary | No documentation |
| 96 | Non-covered charge | Plan exclusion |
| 197 | No prior auth | Missing cert |

### RARC (Remittance Advice Remark Codes)

| Code | Description |
|------|-------------|
| N115 | Diagnosis doesn't support service |
| N290 | Missing referral |
| N386 | Auth number not provided |
| N522 | Service inconsistent with diagnosis |
| MA130 | Duplicate claim |
| N96 | Filing deadline passed |

---

## Variations

### Pharmacy Denial

```
healthsim › Generate a pharmacy claim denied for prior auth on a specialty drug
```

### Coordination of Benefits

```
healthsim › Generate a COB denial where primary didn't pay first
```

### Provider Enrollment

```
healthsim › Generate a denial for provider not enrolled in plan network
```

### Bundling Edit

```
healthsim › Generate a claim denied for procedure bundling (CCI edit)
```

---

## Related

- [Claims Generation](../basic/claims-generation.md)
- [MemberSim Guide](../../docs/guides/membersim-guide.md)
- [Output Formats Reference](../../docs/reference/output-formats.md)
